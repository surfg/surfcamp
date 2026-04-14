#!/usr/bin/env python
"""
One-shot data population script for prod.

Run inside the backend container:
    docker exec surfcamp_backend python populate_data.py

What it does:
  1. Imports scraped JSON data into existing SurfCamps (matched by website domain)
     - description, social, amenities, activities, downloads images
  2. Sets teaching_languages on all camps (English everywhere, ~50% also Russian)
  3. Populates discounts on ~30% camps (15-40%, ends in 6-36h)
  4. Generates LessonProvider + SurfLesson rows from camps with price_per_lesson

Idempotent: re-running won't create duplicates.
"""
import os
import sys
import json
import random
import hashlib
from datetime import timedelta
from urllib.parse import urlparse

import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

import requests
from django.conf import settings
from django.core.files.base import ContentFile
from django.db import transaction
from django.utils import timezone
from django.utils.text import slugify

from camps.models import SurfCamp, CampImage, Amenity, Activity
from lessons.models import LessonProvider, SurfLesson


SCRAPED_FILES = [
    'batch_test_results.json',
    'rapture_parsed.json',
    'dreamsea_parsed.json',
    'dreamsea_bali_parsed.json',
    'kurasurf_parsed.json',
]

# Skip these source URLs entirely (parser produced garbage / 403 for them)
SKIP_URL_HOSTS = set()

random.seed(42)  # deterministic for re-runs


def domain_of(url):
    if not url:
        return None
    return urlparse(url).netloc.lower().replace('www.', '')


def find_camp_for_url(url):
    """Find best matching SurfCamp for a scraped source_url."""
    dom = domain_of(url)
    if not dom:
        return None
    qs = SurfCamp.objects.filter(website__icontains=dom).exclude(name__icontains='403').order_by('id')
    return qs.first()


def load_scraped_camps():
    """Yield (camp_data, source_file) for every successfully parsed camp."""
    base = os.path.dirname(os.path.abspath(__file__))
    for fn in SCRAPED_FILES:
        path = os.path.join(base, fn)
        if not os.path.exists(path):
            print(f'  skip missing: {fn}')
            continue
        with open(path) as f:
            obj = json.load(f)
        if 'results' in obj:
            for r in obj['results']:
                if r.get('success') and r.get('data'):
                    yield r['data'], fn
        elif obj.get('source_url'):
            yield obj, fn


def download_image(url, camp_slug, idx):
    """Download an image and return CampImage instance (unsaved) or None."""
    try:
        r = requests.get(url, timeout=15, stream=True,
                         headers={'User-Agent': 'Mozilla/5.0 SurfcampBot/1.0'})
        if r.status_code != 200:
            return None
        content = r.content
        if len(content) < 2000:  # too small, probably an icon or placeholder
            return None
        # Verify it's actually an image
        from PIL import Image
        from io import BytesIO
        try:
            img = Image.open(BytesIO(content))
            img.verify()
        except Exception:
            return None
        # Generate filename
        ext = os.path.splitext(urlparse(url).path)[1].lower() or '.jpg'
        if ext not in ('.jpg', '.jpeg', '.png', '.webp', '.gif'):
            ext = '.jpg'
        h = hashlib.md5(url.encode()).hexdigest()[:8]
        filename = f'{camp_slug}_imp{idx:02d}_{h}{ext}'
        return filename, content
    except Exception as e:
        print(f'    img dl fail {url[:80]}: {type(e).__name__}')
        return None


def ensure_amenity(name):
    """Get-or-create an Amenity row (handles existing duplicates)."""
    name_clean = (name or '').strip().title()
    if not name_clean or len(name_clean) > 100:
        return None
    qs = Amenity.objects.filter(name_en__iexact=name_clean).order_by('id')
    if qs.exists():
        return qs.first()
    return Amenity.objects.create(name=name_clean, name_en=name_clean, category='services')


# ──────────────────────────────────────────────────────────────────────────
# Step 1: Import scraped data
# ──────────────────────────────────────────────────────────────────────────
def step_import_scraped():
    print('\n[1/4] Importing scraped JSON data into existing camps...')
    matched_count = 0
    no_match = []
    img_added = 0
    activities_added = 0
    amenities_added = 0
    descs_updated = 0

    for data, source in load_scraped_camps():
        url = data.get('source_url')
        camp = find_camp_for_url(url)
        if not camp:
            no_match.append((source, url))
            continue

        matched_count += 1
        print(f'  {source} -> {camp.slug}')

        with transaction.atomic():
            # Description: only overwrite if scraped is longer
            scraped_desc = (data.get('description') or '').strip()
            if scraped_desc and len(scraped_desc) > len(camp.description or ''):
                camp.description = scraped_desc[:5000]  # cap
                descs_updated += 1

            # Short description: only if camp's is empty/very short
            scraped_short = (data.get('short_description') or '').strip()
            if scraped_short and len(camp.short_description or '') < 30:
                camp.short_description = scraped_short[:300]

            # Social/contact: only fill if empty (don't overwrite manual data)
            for field in ('email', 'phone', 'whatsapp', 'instagram'):
                val = (data.get(field) or '').strip()
                if val and not getattr(camp, field, ''):
                    setattr(camp, field, val[:200])

            # Pool / yoga / restaurant flags
            for flag in ('has_pool', 'has_yoga', 'has_restaurant'):
                if data.get(flag):
                    setattr(camp, flag, True)

            camp.save()

            # Amenities (M2M)
            for am_name in (data.get('amenities') or [])[:15]:
                am = ensure_amenity(am_name)
                if am and not camp.amenities.filter(id=am.id).exists():
                    camp.amenities.add(am)
                    amenities_added += 1

            # Activities
            for act in (data.get('activities') or [])[:10]:
                if not isinstance(act, dict):
                    continue
                aname = (act.get('name') or '').strip()
                if not aname or len(aname) > 100:
                    continue
                if camp.activities.filter(name_en__iexact=aname).exists():
                    continue
                Activity.objects.create(
                    camp=camp,
                    name=aname,
                    name_en=aname,
                    description=(act.get('description') or '')[:500],
                    price=None if act.get('price') in (None, '') else act['price'],
                    is_included=bool(act.get('is_included')),
                )
                activities_added += 1

            # Images
            existing_count = camp.images.count()
            if existing_count < 12:  # cap at 12 per camp
                for idx, img_url in enumerate((data.get('image_urls') or [])[:15]):
                    if camp.images.count() >= 12:
                        break
                    res = download_image(img_url, camp.slug, existing_count + idx)
                    if not res:
                        continue
                    filename, content = res
                    rel_path = f'camps/{camp.slug}/{filename}'
                    full_path = os.path.join(settings.MEDIA_ROOT, rel_path)
                    os.makedirs(os.path.dirname(full_path), exist_ok=True)
                    if os.path.exists(full_path):
                        continue
                    with open(full_path, 'wb') as fh:
                        fh.write(content)
                    is_main = camp.images.count() == 0
                    CampImage.objects.create(
                        camp=camp,
                        image=rel_path,
                        is_main=is_main,
                        order=existing_count + idx,
                        alt_text=camp.name,
                    )
                    img_added += 1

    print(f'  matched: {matched_count}, descs_updated: {descs_updated}, '
          f'amenities_added: {amenities_added}, activities_added: {activities_added}, '
          f'images_added: {img_added}')
    if no_match:
        print(f'  no match for: {no_match}')


# ──────────────────────────────────────────────────────────────────────────
# Step 2: teaching_languages
# ──────────────────────────────────────────────────────────────────────────
def step_languages():
    print('\n[2/4] Setting teaching_languages on all camps...')
    EXTRA = ['ru', 'es', 'pt', 'fr', 'de']
    n_en = n_ru = 0
    for camp in SurfCamp.objects.all():
        langs = ['en']
        if random.random() < 0.5:
            langs.append('ru')
            n_ru += 1
        # 20% get a third language
        if random.random() < 0.2:
            extra = random.choice([x for x in EXTRA if x not in langs])
            langs.append(extra)
        camp.teaching_languages = langs
        camp.save(update_fields=['teaching_languages'])
        n_en += 1
    print(f'  {n_en} camps got English, {n_ru} also got Russian')


# ──────────────────────────────────────────────────────────────────────────
# Step 3: discounts
# ──────────────────────────────────────────────────────────────────────────
def step_discounts():
    print('\n[3/4] Setting discounts on ~30% of camps...')
    all_camps = list(SurfCamp.objects.all())
    n_with_discount = max(1, int(len(all_camps) * 0.30))
    chosen = random.sample(all_camps, n_with_discount)
    now = timezone.now()
    for camp in chosen:
        camp.discount_percent = random.choice([15, 20, 25, 30, 35, 40])
        # 6-36h window from now
        hours = random.randint(6, 36)
        camp.discount_ends_at = now + timedelta(hours=hours)
        camp.discount_description = 'Limited time offer - register to claim!'
        camp.save(update_fields=['discount_percent', 'discount_ends_at', 'discount_description'])
    # Reset others
    SurfCamp.objects.exclude(id__in=[c.id for c in chosen]).update(
        discount_percent=0, discount_ends_at=None, discount_description=''
    )
    print(f'  {n_with_discount} camps now have active discounts')


# ──────────────────────────────────────────────────────────────────────────
# Step 4: lessons
# ──────────────────────────────────────────────────────────────────────────
def step_lessons():
    print('\n[4/4] Generating LessonProviders + SurfLessons from camps...')
    providers_created = 0
    lessons_created = 0

    LESSON_TEMPLATES = [
        {
            'name': 'Beginner Group Lesson',
            'name_ru': 'Групповой урок для начинающих',
            'short': 'Learn the basics in a small friendly group',
            'short_ru': 'Изучите основы в небольшой дружной группе',
            'desc': ('A 2-hour group lesson for absolute beginners. Includes safety briefing, '
                     'theory on the beach, and supervised practice in the white water. '
                     'Perfect for your first time on a board.'),
            'desc_ru': ('2-часовой групповой урок для абсолютных новичков. Включает инструктаж '
                        'по безопасности, теорию на пляже и практику в пене под присмотром. '
                        'Идеально для первого раза на доске.'),
            'lesson_type': 'group',
            'skill_level': 'beginner',
            'duration': 120,
            'max_p': 6,
            'mult': 1.0,
        },
        {
            'name': 'Private 1:1 Coaching',
            'name_ru': 'Индивидуальная тренировка 1:1',
            'short': 'Personal coaching with a certified instructor',
            'short_ru': 'Персональные занятия с сертифицированным инструктором',
            'desc': ('One-on-one session tailored to your level. The instructor focuses entirely '
                     'on your technique, paddling, take-off and pop-up. Video analysis available '
                     'on request.'),
            'desc_ru': ('Персональная сессия под ваш уровень. Инструктор полностью сосредоточен '
                        'на вашей технике: гребля, тейк-офф, поп-ап. Видеоразбор по запросу.'),
            'lesson_type': 'private',
            'skill_level': 'all',
            'duration': 90,
            'max_p': 1,
            'mult': 2.5,
        },
        {
            'name': 'Intermediate Improver',
            'name_ru': 'Урок для среднего уровня',
            'short': 'Move from white water to green waves',
            'short_ru': 'Переход от пены к зелёным волнам',
            'desc': ('For surfers who can already pop up and want to start catching unbroken '
                     'waves. We work on positioning, paddling out, and reading the lineup. '
                     'Maximum 4 people per coach.'),
            'desc_ru': ('Для серферов, которые уже умеют вставать на доску и хотят ловить '
                        'нераскрытые волны. Работаем над позицией, выходом и чтением лайнапа. '
                        'Максимум 4 человека на тренера.'),
            'lesson_type': 'semi_private',
            'skill_level': 'intermediate',
            'duration': 120,
            'max_p': 4,
            'mult': 1.5,
        },
    ]

    for camp in SurfCamp.objects.filter(is_active=True):
        if not camp.price_per_lesson:
            continue

        # Build a slug that fits in 50 chars (LessonProvider.slug max_length)
        base_slug = camp.slug[:40]
        provider_slug = f'{base_slug}-l'[:50]
        provider, created = LessonProvider.objects.get_or_create(
            slug=provider_slug,
            defaults={
                'name': (f'{camp.name} School')[:200],
                'description': (camp.description or '')[:1000],
                'description_ru': '',
                'region': camp.region,
                'address': (camp.address or '')[:500],
                'latitude': camp.latitude,
                'longitude': camp.longitude,
                'phone': (camp.phone or '')[:50],
                'email': (camp.email or '')[:254],
                'website': (camp.website or '')[:200],
                'instagram': (camp.instagram or '')[:100],
                'whatsapp': (camp.whatsapp or '')[:50],
                'rating': camp.rating,
                'reviews_count': camp.reviews_count,
                'is_active': True,
                'is_featured': camp.is_featured,
            },
        )
        if created:
            providers_created += 1

        base_price = float(camp.price_per_lesson)
        # Decide which lesson templates this camp offers based on its skill_levels
        camp_levels = set(camp.skill_levels or [])

        for tpl in LESSON_TEMPLATES:
            # Skip beginner template if camp doesn't accept beginners
            if tpl['skill_level'] == 'beginner' and 'beginner' not in camp_levels:
                continue
            if tpl['skill_level'] == 'intermediate' and 'intermediate' not in camp_levels:
                continue

            slug = f'{camp.slug[:90]}-{slugify(tpl["name"])}'[:150]
            if SurfLesson.objects.filter(slug=slug).exists():
                continue

            SurfLesson.objects.create(
                provider=provider,
                name=tpl['name'],
                name_ru=tpl['name_ru'],
                slug=slug,
                short_description=tpl['short'],
                short_description_ru=tpl['short_ru'],
                description=tpl['desc'],
                description_ru=tpl['desc_ru'],
                lesson_type=tpl['lesson_type'],
                skill_level=tpl['skill_level'],
                duration_minutes=tpl['duration'],
                max_participants=tpl['max_p'],
                min_age=12 if tpl['skill_level'] != 'beginner' else 6,
                price=round(base_price * tpl['mult'], 2),
                currency='USD',
                price_per_person=True,
                is_package=False,
                lessons_in_package=1,
                includes_equipment=True,
                includes_wetsuit=True,
                includes_transport=False,
                includes_theory=True,
                rating=camp.rating,
                reviews_count=0,
                is_active=True,
                is_featured=camp.is_featured,
            )
            lessons_created += 1

    print(f'  providers created: {providers_created}, lessons created: {lessons_created}')
    print(f'  total providers: {LessonProvider.objects.count()}, total lessons: {SurfLesson.objects.count()}')


def main():
    print('=' * 60)
    print('Surfcamp data population')
    print('=' * 60)
    step_import_scraped()
    step_languages()
    step_discounts()
    step_lessons()
    print('\nDone.')


if __name__ == '__main__':
    main()
