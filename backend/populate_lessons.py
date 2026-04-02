#!/usr/bin/env python
"""
Script to populate surf lessons data
Run: python populate_lessons.py
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from camps.models import Country, Region
from lessons.models import LessonProvider, SurfLesson, LessonReview


def create_lesson_providers():
    """Create lesson providers (surf schools)"""

    # Get regions
    try:
        bali = Region.objects.get(name_en='Bali')
    except Region.DoesNotExist:
        print("Bali region not found.")
        bali = None

    try:
        portugal_ericeira = Region.objects.filter(name_en__icontains='Ericeira').first()
    except:
        portugal_ericeira = None

    try:
        portugal_peniche = Region.objects.filter(name_en__icontains='Peniche').first()
    except:
        portugal_peniche = None

    try:
        sri_lanka_weligama = Region.objects.filter(name_en__icontains='Weligama').first()
    except:
        sri_lanka_weligama = None

    try:
        byron_bay = Region.objects.get(name_en='Byron Bay')
    except Region.DoesNotExist:
        byron_bay = None

    try:
        santa_teresa = Region.objects.get(name_en='Santa Teresa')
    except Region.DoesNotExist:
        santa_teresa = None

    try:
        lombok = Region.objects.get(name_en='Lombok')
    except Region.DoesNotExist:
        lombok = None

    providers_data = []

    if bali:
        providers_data.extend([
            {
                'name': 'Odysseys Surf School',
                'slug': 'odysseys-surf-school',
                'region': bali,
                'description': 'Premier surf school in Canggu offering lessons for all levels. Our ISA certified instructors provide personalized coaching with small group sizes.',
                'description_ru': 'Премиум серф-школа в Чангу для всех уровней. Наши сертифицированные инструкторы ISA предоставляют персональный коучинг в маленьких группах.',
                'address': 'Jl. Pantai Batu Bolong No.58, Canggu, Bali',
                'latitude': -8.6550,
                'longitude': 115.1328,
                'phone': '+62 812 3456 7890',
                'email': 'info@odysseyssurf.com',
                'website': 'https://odysseyssurf.com',
                'instagram': '@odysseyssurf',
                'whatsapp': '+62 812 3456 7890',
                'rating': 4.9,
                'reviews_count': 156,
                'is_featured': True,
            },
            {
                'name': 'Bali Wave Riders',
                'slug': 'bali-wave-riders',
                'region': bali,
                'description': 'Family-friendly surf school on Kuta Beach. Perfect for beginners with gentle waves and patient instructors.',
                'description_ru': 'Семейная серф-школа на пляже Кута. Идеально для начинающих с мягкими волнами и терпеливыми инструкторами.',
                'address': 'Jl. Pantai Kuta, Kuta, Bali',
                'latitude': -8.7215,
                'longitude': 115.1686,
                'phone': '+62 813 9876 5432',
                'email': 'book@baliwaveriderscom',
                'website': 'https://baliwaveriderscom',
                'instagram': '@baliwaveriderscom',
                'whatsapp': '+62 813 9876 5432',
                'rating': 4.7,
                'reviews_count': 234,
                'is_featured': True,
            },
            {
                'name': 'Pro Surf Uluwatu',
                'slug': 'pro-surf-uluwatu',
                'region': bali,
                'description': 'Advanced surf coaching in world-class Uluwatu breaks. For intermediate to advanced surfers looking to progress.',
                'description_ru': 'Продвинутый серф-коучинг на мировых спотах Улувату. Для серферов среднего и продвинутого уровня.',
                'address': 'Jl. Labuan Sait, Uluwatu, Bali',
                'latitude': -8.8145,
                'longitude': 115.0890,
                'phone': '+62 817 1234 5678',
                'email': 'coach@prosurfulu.com',
                'website': 'https://prosurfulu.com',
                'instagram': '@prosurfulu',
                'whatsapp': '+62 817 1234 5678',
                'rating': 4.8,
                'reviews_count': 89,
                'is_featured': False,
            },
        ])

    if lombok:
        providers_data.append({
            'name': 'Lombok Surf Academy',
            'slug': 'lombok-surf-academy',
            'region': lombok,
            'description': 'Premier surf school in Kuta Lombok. Perfect waves for all levels with experienced local instructors.',
            'description_ru': 'Премиум серф-школа в Куте, Ломбок. Идеальные волны для всех уровней с опытными местными инструкторами.',
            'address': 'Kuta Beach, Lombok',
            'latitude': -8.8990,
            'longitude': 116.2890,
            'phone': '+62 819 1234 5678',
            'email': 'info@lomboksurf.com',
            'website': 'https://lomboksurf.com',
            'instagram': '@lomboksurf',
            'whatsapp': '+62 819 1234 5678',
            'rating': 4.7,
            'reviews_count': 145,
            'is_featured': True,
        })

    if portugal_ericeira:
        providers_data.append({
            'name': 'Ericeira Surf Academy',
            'slug': 'ericeira-surf-academy',
            'region': portugal_ericeira,
            'description': 'Professional surf academy in Europe\'s only World Surfing Reserve. Learn with certified coaches in perfect conditions.',
            'description_ru': 'Профессиональная серф-академия в единственном Всемирном серфинг-резерве Европы.',
            'address': 'Rua da Ribeira, Ericeira, Portugal',
            'latitude': 38.9626,
            'longitude': -9.4189,
            'phone': '+351 912 345 678',
            'email': 'info@ericeirasurf.pt',
            'website': 'https://ericeirasurf.pt',
            'instagram': '@ericeirasurf',
            'whatsapp': '+351 912 345 678',
            'rating': 4.9,
            'reviews_count': 312,
            'is_featured': True,
        })

    if portugal_peniche:
        providers_data.append({
            'name': 'Peniche Surf Center',
            'slug': 'peniche-surf-center',
            'region': portugal_peniche,
            'description': 'Centrally located surf school with access to multiple breaks. Lessons adapted to daily conditions.',
            'description_ru': 'Серф-школа с удобным расположением и доступом к разным спотам. Уроки адаптируются под условия.',
            'address': 'Av. do Mar, Peniche, Portugal',
            'latitude': 39.3558,
            'longitude': -9.3814,
            'phone': '+351 918 765 432',
            'email': 'hello@penichesurfcenter.com',
            'website': 'https://penichesurfcenter.com',
            'instagram': '@penichesurfcenter',
            'whatsapp': '+351 918 765 432',
            'rating': 4.6,
            'reviews_count': 178,
            'is_featured': False,
        })

    if sri_lanka_weligama:
        providers_data.append({
            'name': 'Weligama Bay Surf School',
            'slug': 'weligama-bay-surf-school',
            'region': sri_lanka_weligama,
            'description': 'The original surf school in Weligama Bay. Perfect beginner waves and warm tropical waters.',
            'description_ru': 'Оригинальная серф-школа в заливе Велигама. Идеальные волны для начинающих и тёплые тропические воды.',
            'address': 'Weligama Bay Beach, Weligama, Sri Lanka',
            'latitude': 5.9720,
            'longitude': 80.4270,
            'phone': '+94 77 123 4567',
            'email': 'surf@weligamabay.lk',
            'website': 'https://weligamabaysurf.lk',
            'instagram': '@weligamabaysurf',
            'whatsapp': '+94 77 123 4567',
            'rating': 4.8,
            'reviews_count': 267,
            'is_featured': True,
        })

    if byron_bay:
        providers_data.append({
            'name': 'Byron Bay Surf School',
            'slug': 'byron-bay-surf-school',
            'region': byron_bay,
            'description': 'Australia\'s longest running surf school. Learn in the beautiful waters of Byron Bay with experienced instructors.',
            'description_ru': 'Старейшая серф-школа Австралии. Учитесь в прекрасных водах Байрон Бэй с опытными инструкторами.',
            'address': 'Lawson Street, Byron Bay, NSW',
            'latitude': -28.6474,
            'longitude': 153.6020,
            'phone': '+61 2 6685 7536',
            'email': 'info@byronbaysurf.com.au',
            'website': 'https://byronbaysurf.com.au',
            'instagram': '@byronbaysurf',
            'whatsapp': '+61 412 345 678',
            'rating': 4.8,
            'reviews_count': 423,
            'is_featured': True,
        })

    if santa_teresa:
        providers_data.append({
            'name': 'Santa Teresa Surf Camp',
            'slug': 'santa-teresa-surf-camp',
            'region': santa_teresa,
            'description': 'Learn to surf in paradise. Our instructors will have you riding waves in no time on Costa Rica\'s beautiful Pacific coast.',
            'description_ru': 'Научитесь серфингу в раю. Наши инструкторы научат вас кататься на волнах на прекрасном тихоокеанском побережье Коста-Рики.',
            'address': 'Playa Santa Teresa, Costa Rica',
            'latitude': 9.6420,
            'longitude': -85.1695,
            'phone': '+506 8888 1234',
            'email': 'surf@santateresacamp.com',
            'website': 'https://santateresacamp.com',
            'instagram': '@santateresasurf',
            'whatsapp': '+506 8888 1234',
            'rating': 4.9,
            'reviews_count': 198,
            'is_featured': True,
        })

    if not providers_data:
        print("No valid regions found for providers.")
        return []

    providers = []
    for data in providers_data:
        provider, created = LessonProvider.objects.get_or_create(
            slug=data['slug'],
            defaults=data
        )
        providers.append(provider)
        status = "Created" if created else "Exists"
        print(f"  {status}: {provider.name}")

    print(f"\nTotal providers: {len(providers)}")
    return providers


def create_lessons(providers):
    """Create surf lessons for each provider"""

    lessons_templates = [
        # Beginner lessons
        {
            'name': 'Beginner Surf Lesson',
            'name_ru': 'Урок серфинга для начинающих',
            'short_description': '2-hour lesson perfect for first-timers',
            'short_description_ru': '2-часовой урок, идеальный для новичков',
            'description': 'Our beginner surf lesson is designed for those who have never surfed before. Learn the fundamentals of surfing including paddling, popping up, and catching white water waves. All equipment provided.',
            'description_ru': 'Урок для тех, кто никогда не серфил. Изучите основы: гребля, вставание на доску и катание по пене. Всё оборудование включено.',
            'lesson_type': 'group',
            'skill_level': 'beginner',
            'duration_minutes': 120,
            'max_participants': 6,
            'min_age': 8,
            'price': 45,
            'currency': 'EUR',
            'price_per_person': True,
            'includes_equipment': True,
            'includes_wetsuit': True,
            'includes_photos': True,
            'includes_theory': True,
            'is_featured': True,
        },
        {
            'name': 'Private Beginner Lesson',
            'name_ru': 'Индивидуальный урок для начинающих',
            'short_description': '1-on-1 coaching for rapid progress',
            'short_description_ru': 'Персональное обучение для быстрого прогресса',
            'description': 'One-on-one instruction tailored to your learning pace. Perfect for those who want personalized attention and faster progression.',
            'description_ru': 'Индивидуальное обучение в вашем темпе. Идеально для тех, кто хочет персонального внимания и быстрого прогресса.',
            'lesson_type': 'private',
            'skill_level': 'beginner',
            'duration_minutes': 90,
            'max_participants': 1,
            'min_age': 6,
            'price': 85,
            'currency': 'EUR',
            'price_per_person': True,
            'includes_equipment': True,
            'includes_wetsuit': True,
            'includes_photos': True,
            'includes_video': True,
            'includes_theory': True,
            'is_featured': True,
        },
        # Intermediate lessons
        {
            'name': 'Intermediate Surf Coaching',
            'name_ru': 'Коучинг для среднего уровня',
            'short_description': 'Improve your technique with video analysis',
            'short_description_ru': 'Улучшите технику с видеоанализом',
            'description': 'For surfers who can catch green waves. Focus on bottom turns, top turns, and wave selection. Includes video analysis.',
            'description_ru': 'Для серферов, катающихся по зелёным волнам. Фокус на нижнем повороте, топ-тёрне и выборе волн. Включает видеоанализ.',
            'lesson_type': 'semi_private',
            'skill_level': 'intermediate',
            'duration_minutes': 150,
            'max_participants': 3,
            'min_age': 12,
            'price': 95,
            'currency': 'EUR',
            'price_per_person': True,
            'includes_equipment': True,
            'includes_wetsuit': True,
            'includes_video': True,
            'includes_theory': True,
            'is_featured': False,
        },
        # Advanced lessons
        {
            'name': 'Advanced Surf Coaching',
            'name_ru': 'Продвинутый серф-коучинг',
            'short_description': 'Master advanced maneuvers with pro coaches',
            'short_description_ru': 'Освойте продвинутые манёвры с про-коучами',
            'description': 'For experienced surfers looking to perfect their technique. Work on aerials, barrels, and competition strategy.',
            'description_ru': 'Для опытных серферов, желающих совершенствовать технику. Работа над эйрами, трубами и соревновательной стратегией.',
            'lesson_type': 'private',
            'skill_level': 'advanced',
            'duration_minutes': 180,
            'max_participants': 2,
            'min_age': 16,
            'price': 150,
            'currency': 'EUR',
            'price_per_person': True,
            'includes_equipment': False,
            'includes_video': True,
            'includes_theory': True,
            'is_featured': False,
        },
        # Packages
        {
            'name': '5-Day Surf Course',
            'name_ru': '5-дневный курс серфинга',
            'short_description': 'Complete beginner course over 5 days',
            'short_description_ru': 'Полный курс для начинающих за 5 дней',
            'description': 'Our most popular package! 5 consecutive days of surf lessons with progressive skill building. Go from zero to catching your own waves.',
            'description_ru': 'Наш самый популярный пакет! 5 дней уроков с постепенным развитием навыков. От нуля до самостоятельного катания.',
            'lesson_type': 'group',
            'skill_level': 'beginner',
            'duration_minutes': 120,
            'max_participants': 6,
            'min_age': 8,
            'price': 180,
            'currency': 'EUR',
            'price_per_person': True,
            'is_package': True,
            'lessons_in_package': 5,
            'package_discount_percent': 20,
            'includes_equipment': True,
            'includes_wetsuit': True,
            'includes_photos': True,
            'includes_theory': True,
            'is_featured': True,
        },
        {
            'name': 'Kids Surf Camp',
            'name_ru': 'Детский серф-лагерь',
            'short_description': 'Fun surf lessons for kids aged 6-14',
            'short_description_ru': 'Весёлые уроки серфинга для детей 6-14 лет',
            'description': 'Safe and fun introduction to surfing for children. Small groups, patient instructors, and lots of games.',
            'description_ru': 'Безопасное и весёлое знакомство с серфингом для детей. Маленькие группы, терпеливые инструкторы, много игр.',
            'lesson_type': 'group',
            'skill_level': 'beginner',
            'duration_minutes': 90,
            'max_participants': 4,
            'min_age': 6,
            'price': 35,
            'currency': 'EUR',
            'price_per_person': True,
            'includes_equipment': True,
            'includes_wetsuit': True,
            'includes_photos': True,
            'includes_insurance': True,
            'is_featured': False,
        },
    ]

    all_lessons = []

    for provider in providers:
        for i, template in enumerate(lessons_templates):
            # Create unique slug
            slug = f"{provider.slug}-{template['name'].lower().replace(' ', '-').replace("'", '')}"

            # Adjust prices based on location
            price = template['price']
            currency = template['currency']

            # Indonesia tends to be cheaper
            if provider.region.country.code == 'IDN':
                price = int(price * 0.6)  # 40% cheaper
                currency = 'USD'
            # Sri Lanka also cheaper
            elif provider.region.country.code == 'LKA':
                price = int(price * 0.5)
                currency = 'USD'
            # Australia more expensive
            elif provider.region.country.code == 'AUS':
                price = int(price * 1.3)
                currency = 'AUD'
            # Costa Rica in USD
            elif provider.region.country.code == 'CRI':
                currency = 'USD'

            lesson_data = {
                **template,
                'provider': provider,
                'slug': slug,
                'price': price,
                'currency': currency,
            }

            # Remove non-model fields
            is_featured = lesson_data.pop('is_featured', False)

            lesson, created = SurfLesson.objects.get_or_create(
                slug=slug,
                defaults=lesson_data
            )

            # Set is_featured separately
            lesson.is_featured = is_featured
            lesson.save()

            all_lessons.append(lesson)

            if created:
                print(f"  Created: {lesson.name} ({provider.name})")

    print(f"\nTotal lessons: {len(all_lessons)}")
    return all_lessons


def create_reviews(lessons):
    """Create some sample reviews"""

    review_templates = [
        {
            'author_name': 'Sarah M.',
            'author_country': 'United States',
            'rating': 5,
            'title': 'Amazing experience!',
            'text': 'Best surf lesson I\'ve ever had. The instructor was patient and made learning so fun. Stood up on my first day!',
            'surf_level': 'beginner',
            'is_verified': True,
        },
        {
            'author_name': 'Marcus K.',
            'author_country': 'Germany',
            'rating': 5,
            'title': 'Professional coaching',
            'text': 'Excellent video analysis helped me improve my technique significantly. Highly recommend for intermediate surfers.',
            'surf_level': 'intermediate',
            'is_verified': True,
        },
        {
            'author_name': 'Anna L.',
            'author_country': 'Australia',
            'rating': 4,
            'title': 'Great for beginners',
            'text': 'Very well organized lesson. Equipment was in good condition and the instructor was friendly and helpful.',
            'surf_level': 'beginner',
            'is_verified': True,
        },
        {
            'author_name': 'Dmitry P.',
            'author_country': 'Russia',
            'rating': 5,
            'title': 'Exceeded expectations',
            'text': 'The 5-day course was perfect. By the end I was catching green waves on my own. Great value for money.',
            'surf_level': 'beginner',
            'is_verified': True,
        },
        {
            'author_name': 'Emma W.',
            'author_country': 'United Kingdom',
            'rating': 4,
            'title': 'Fun and safe',
            'text': 'Brought my kids here and they loved it! Instructors were patient and safety-conscious. Will come back.',
            'surf_level': 'beginner',
            'is_verified': True,
        },
    ]

    reviews_created = 0

    # Add reviews to featured lessons
    featured_lessons = [l for l in lessons if l.is_featured]

    for lesson in featured_lessons[:10]:
        for template in review_templates[:3]:  # 3 reviews per lesson
            review_data = {
                **template,
                'lesson': lesson,
            }
            review, created = LessonReview.objects.get_or_create(
                lesson=lesson,
                author_name=template['author_name'],
                defaults=review_data
            )
            if created:
                reviews_created += 1

    print(f"Created {reviews_created} reviews")


def main():
    print("=" * 50)
    print("Populating Surf Lessons Data")
    print("=" * 50)

    print("\n1. Creating lesson providers...")
    providers = create_lesson_providers()

    if not providers:
        print("No providers created. Exiting.")
        return

    print("\n2. Creating surf lessons...")
    lessons = create_lessons(providers)

    print("\n3. Creating reviews...")
    create_reviews(lessons)

    print("\n" + "=" * 50)
    print("Done! Surf lessons data populated successfully.")
    print("=" * 50)


if __name__ == '__main__':
    main()
