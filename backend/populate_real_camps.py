#!/usr/bin/env python
"""
Populate database with real surf camp data.
Run with: python manage.py shell < populate_real_camps.py
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from camps.models import Country, Region, SurfCamp, BoardType, Amenity
from decimal import Decimal

print("=" * 80)
print("CLEANING UP FAKE DATA AND POPULATING WITH REAL DATA")
print("=" * 80)

# Clear existing data
print("\n[1/5] Clearing existing camps and regions...")
# First delete bookings and reviews that reference camps
from bookings.models import Booking
print("  Clearing bookings...")
Booking.objects.all().delete()
print("  Clearing camps...")
SurfCamp.objects.all().delete()
print("  Clearing regions...")
Region.objects.all().delete()
print("  Clearing countries...")
Country.objects.all().delete()
print("✓ Cleared camps, regions, and countries")

# Create Board Types
print("\n[2/5] Creating board types...")
board_types_data = [
    {'name': 'Софттопы', 'name_en': 'Soft tops', 'icon': 'softtop', 'description': 'Perfect for beginners'},
    {'name': 'Лонгборды', 'name_en': 'Longboards', 'icon': 'longboard', 'description': '9ft+ classic longboards'},
    {'name': 'Мидлы', 'name_en': 'Funboards', 'icon': 'funboard', 'description': 'Mid-length versatile boards'},
    {'name': 'Шортборды', 'name_en': 'Shortboards', 'icon': 'shortboard', 'description': 'High performance boards'},
]
board_types = {}
for bt in board_types_data:
    obj = BoardType.objects.create(**bt)
    board_types[bt['name_en']] = obj
print(f"✓ Created {len(board_types)} board types")

# Create Amenities
print("\n[3/5] Creating amenities...")
amenities_data = [
    {'name': 'Бассейн', 'name_en': 'Pool', 'icon': 'pool', 'category': 'accommodation'},
    {'name': 'Wi-Fi', 'name_en': 'Wi-Fi', 'icon': 'wifi', 'category': 'services'},
    {'name': 'Кондиционер', 'name_en': 'Air Conditioning', 'icon': 'ac', 'category': 'accommodation'},
    {'name': 'Ресторан', 'name_en': 'Restaurant', 'icon': 'restaurant', 'category': 'food'},
    {'name': 'Бар', 'name_en': 'Bar', 'icon': 'bar', 'category': 'food'},
    {'name': 'Йога', 'name_en': 'Yoga', 'icon': 'yoga', 'category': 'activities'},
    {'name': 'Массаж', 'name_en': 'Massage', 'icon': 'massage', 'category': 'services'},
    {'name': 'Трансфер', 'name_en': 'Airport Transfer', 'icon': 'transfer', 'category': 'services'},
]
amenities = {}
for am in amenities_data:
    obj = Amenity.objects.create(**am)
    amenities[am['name_en']] = obj
print(f"✓ Created {len(amenities)} amenities")

# Create Countries and Regions
print("\n[4/5] Creating countries and regions...")
countries_data = {
    'Portugal': {'code': 'PT', 'name_en': 'Portugal', 'regions': [
        'Peniche', 'Ericeira', 'Cascais', 'Algarve', 'Lagos', 'Porto', 'Madeira', 'Costa Caparica'
    ]},
    'Spain': {'code': 'ES', 'name_en': 'Spain', 'regions': ['Cantabria', 'Canary Islands']},
    'Indonesia': {'code': 'ID', 'name_en': 'Indonesia', 'regions': ['Bali', 'Lombok']},
    'Costa Rica': {'code': 'CR', 'name_en': 'Costa Rica', 'regions': ['Guanacaste']},
    'Morocco': {'code': 'MA', 'name_en': 'Morocco', 'regions': ['Souss-Massa', 'Taghazout']},
    'Sri Lanka': {'code': 'LK', 'name_en': 'Sri Lanka', 'regions': ['Southern Province']},
    'Russia': {'code': 'RU', 'name_en': 'Russia', 'regions': ['Kaliningrad', 'Kamchatka']},
}

countries = {}
regions = {}

for country_name, data in countries_data.items():
    country = Country.objects.create(
        name=country_name,
        name_en=data['name_en'],
        code=data['code'],
        is_active=True
    )
    countries[country_name] = country
    print(f"  ✓ Created country: {country_name}")

    for region_name in data['regions']:
        region = Region.objects.create(
            country=country,
            name=region_name,
            name_en=region_name,
            description=f"{region_name}, {country_name}"
        )
        regions[f"{country_name}_{region_name}"] = region

print(f"✓ Created {len(countries)} countries and {len(regions)} regions")

# Real camp data
print("\n[5/5] Creating camps with real data...")

camps_data = [
    # PORTUGAL
    {
        'name': 'Baleal Surf Camp',
        'slug': 'baleal-surf-camp-peniche',
        'region': regions['Portugal_Peniche'],
        'short_description': 'Portugal\'s first surf camp, beachfront in Peniche',
        'description': 'Founded in 1993, located directly on the beach in one of Europe\'s most consistent and surfer-friendly surf spots. 89km north of Lisbon.',
        'address': 'Rua Ferreira de Castro N.º 16 R/C A ESQ., 2520-158 Ferrel – Peniche, Portugal',
        'latitude': Decimal('39.3583'),
        'longitude': Decimal('-9.2633'),
        'price_per_night': Decimal('45.00'),
        'price_per_lesson': Decimal('50.00'),
        'skill_levels': ['beginner', 'intermediate', 'advanced'],
        'website': 'https://www.balealsurfcamp.com/',
        'email': 'info@balealsurfcamp.com',
        'phone': '+351 961 316 204',
        'instagram': '@balealsurfcamp',
        'whatsapp': '+351 961 316 204',
        'has_pool': False,
        'has_restaurant': True,
        'has_yoga': False,
        'has_parties': False,
    },
    {
        'name': 'Rapture Surf Camp - Ericeira',
        'slug': 'rapture-surf-camp-ericeira',
        'region': regions['Portugal_Ericeira'],
        'short_description': 'Network of 8 unique surf camps in 5 countries',
        'description': 'Part of a global network serving 85,000+ guests since 2003. Multiple locations in Portugal and worldwide.',
        'address': 'Ericeira, Portugal',
        'latitude': Decimal('38.9452'),
        'longitude': Decimal('-9.3550'),
        'price_per_night': Decimal('55.00'),
        'price_per_lesson': Decimal('60.00'),
        'skill_levels': ['beginner', 'intermediate', 'advanced'],
        'website': 'https://www.rapturecamps.com',
        'phone': '+447700177360',
        'instagram': '@rapturecamps',
        'has_pool': False,
        'has_restaurant': False,
        'has_yoga': True,
        'has_parties': True,
    },
    {
        'name': 'Gota Dagua - Costa Caparica',
        'slug': 'gota-dagua-costa-caparica',
        'region': regions['Portugal_Costa Caparica'],
        'short_description': 'Family-oriented surf and yoga camp near Lisbon',
        'description': 'Weekly packages combining surfing with yoga sessions. Pool, bikes, and skateboards available. Free board and wetsuit rental included.',
        'address': 'Costa da Caparica, Lisbon, Portugal',
        'latitude': Decimal('38.3500'),
        'longitude': Decimal('-9.2000'),
        'price_per_night': Decimal('61.29'),  # €429 for 7 nights
        'price_per_lesson': Decimal('22.50'),
        'bed_breakfast_price': Decimal('61.29'),
        'has_bed_breakfast': True,
        'skill_levels': ['beginner', 'intermediate', 'advanced'],
        'website': 'https://gotadaguasurf.com/surfcamp/portugal-lisbon/',
        'email': 'info@wordpress-762907-2632641.cloudwaysapps.com',
        'phone': '+351 939 591 707',
        'instagram': '@gotadagua_surf',
        'has_pool': True,
        'has_restaurant': True,
        'has_yoga': True,
        'has_parties': False,
    },
    {
        'name': 'The Salty - Peniche',
        'slug': 'the-salty-peniche',
        'region': regions['Portugal_Peniche'],
        'short_description': 'Social wellness experience by the ocean with yoga and community',
        'description': 'Surf, yoga, community and calm spaces in Portugal. Package includes daily breakfast, unlimited yoga with breathwork, surf lessons, and board rental.',
        'address': 'Peniche, Portugal',
        'latitude': Decimal('39.3583'),
        'longitude': Decimal('-9.2633'),
        'price_per_night': Decimal('114.14'),  # €799 for 7 nights / 7
        'bed_breakfast_price': Decimal('114.14'),
        'has_bed_breakfast': True,
        'skill_levels': ['beginner', 'intermediate'],
        'website': 'https://www.thesalty.co/home-peniche/',
        'phone': '+351 923083334',
        'instagram': '@thesalty__',
        'has_pool': True,
        'has_restaurant': True,
        'has_yoga': True,
        'has_parties': True,
    },
    {
        'name': 'Laneez Ericeira',
        'slug': 'laneez-ericeira',
        'region': regions['Portugal_Ericeira'],
        'short_description': 'Your home over the ocean - comprehensive surf accommodation',
        'description': 'Surf House, Surf Vilas, and Sea View Apartments. Daily yoga sessions (2x), surf school, and canoe surfing. UNESCO World Surfing Reserve area.',
        'address': 'Rua Dr. Eduardo Burnay 5, 2655-368 Ericeira, Portugal',
        'latitude': Decimal('38.9452'),
        'longitude': Decimal('-9.3550'),
        'price_per_night': Decimal('60.00'),
        'price_per_lesson': Decimal('45.00'),
        'skill_levels': ['beginner', 'intermediate', 'advanced'],
        'website': 'https://laneezericeira.com/',
        'email': 'laneezericeira@gmail.com',
        'phone': '+351 968 555 744',
        'instagram': '@laneezericeira',
        'has_pool': False,
        'has_restaurant': False,
        'has_yoga': True,
        'has_parties': False,
    },
    {
        'name': 'Russo Surf Camp',
        'slug': 'russo-surf-camp-algarve',
        'region': regions['Portugal_Algarve'],
        'short_description': 'One of the first Algarve surf camps, founded in 2003',
        'description': 'Founded by Portuguese surf pioneer Rui Russo. Located in Costa Vicentina Natural Park. Offers surf instruction, yoga retreats, and combined packages.',
        'address': 'Vale Figueiras, Aljezur, Algarve, Portugal',
        'latitude': Decimal('37.3053'),
        'longitude': Decimal('-8.8789'),
        'price_per_night': Decimal('85.57'),  # €599 for 7 nights
        'price_per_lesson': Decimal('60.00'),
        'skill_levels': ['beginner', 'intermediate'],
        'website': 'https://russosurf.com/',
        'email': 'info@russosurf.com',
        'phone': '+351 964 342 391',
        'instagram': '@russo_surfcamp_vale_figueiras',
        'has_pool': False,
        'has_restaurant': True,
        'has_yoga': True,
        'has_parties': False,
    },
    {
        'name': 'Tiny Whale Surf Lodge',
        'slug': 'tiny-whale-surf-lodge-lagos',
        'region': regions['Portugal_Lagos'],
        'short_description': 'Boutique surf camp with personalized coaching for beginners and intermediates',
        'description': 'High-quality surf coaching in small groups with fully catered experience. In-house chef, video coaching, airport pickup included. Yoga packages available.',
        'address': 'Lote 276 & 279 Colinas Verdes, 8600-074 Bensafrim, Lagos',
        'latitude': Decimal('37.0997'),
        'longitude': Decimal('-8.6708'),
        'price_per_night': Decimal('150.00'),
        'price_per_lesson': Decimal('70.00'),
        'skill_levels': ['beginner', 'intermediate'],
        'website': 'https://www.tinywhalesurflodge.com/',
        'email': '[email protected]',
        'phone': '+351 913665446',
        'instagram': '@tinywhalesurflodge',
        'has_pool': True,
        'has_restaurant': True,
        'has_yoga': True,
        'has_parties': False,
    },
    {
        'name': 'Ericeira Surf Camp',
        'slug': 'ericeira-surf-camp',
        'region': regions['Portugal_Ericeira'],
        'short_description': 'Cozy accommodation and surf lessons in UNESCO World Surfing Reserve',
        'description': 'Founded in 2005. Certified surf instruction for all levels. Equipment rental (boards, wetsuits, bikes), yoga, SUP, bike tours, massage. Walking distance to beaches.',
        'address': 'Rua Doutor Eduardo Burnay, 28, 2655-370 Ericeira, Portugal',
        'latitude': Decimal('38.9452'),
        'longitude': Decimal('-9.3550'),
        'price_per_night': Decimal('40.00'),
        'price_per_lesson': Decimal('40.00'),
        'skill_levels': ['beginner', 'intermediate', 'advanced'],
        'website': 'https://ericeirasurfcamp.com/',
        'email': 'info@ericeirasurfcamp.com',
        'phone': '+351 912 148 306',
        'instagram': '@ericeirasurfcamp',
        'has_pool': False,
        'has_restaurant': False,
        'has_yoga': True,
        'has_parties': False,
    },
    {
        'name': 'Peniche Surf Camp',
        'slug': 'peniche-surf-camp',
        'region': regions['Portugal_Peniche'],
        'short_description': 'Ocean-front camp with 200+ board rentals, established 1994',
        'description': 'Instructed 50,000+ students since 1994. Surf school, 200+ surfboard rentals (soft, epoxy, PU), board repair, Rip Curl wetsuits, yoga classes, transfers.',
        'address': 'Avenida do Mar, 162 - Casais do Baleal, 2520-101 Peniche, Portugal',
        'latitude': Decimal('39.3583'),
        'longitude': Decimal('-9.2633'),
        'price_per_night': Decimal('45.00'),
        'price_per_lesson': Decimal('45.00'),
        'skill_levels': ['beginner', 'intermediate', 'advanced'],
        'website': 'https://www.penichesurfcamp.com/',
        'email': 'bookings@penichesurfcamp.com',
        'phone': '+351 962 336 295',
        'instagram': '@penichesurfcamp',
        'has_pool': False,
        'has_restaurant': False,
        'has_yoga': True,
        'has_parties': False,
    },
    {
        'name': 'Pure Surf Camp Peniche',
        'slug': 'pure-surf-camp-peniche',
        'region': regions['Portugal_Peniche'],
        'short_description': 'Newly renovated accommodations on Baleal Beach with pool and gym',
        'description': 'Located in Ferrel on Baleal Beach. Renovated accommodations with private bathrooms, pool, garden, indoor gym. Includes daily breakfast, yoga, cross-training, and wine/cheese tasting.',
        'address': 'R. Casal dos Ninhos 12, Ferrel, 2520-053 Peniche, Portugal',
        'latitude': Decimal('39.3583'),
        'longitude': Decimal('-9.2633'),
        'price_per_night': Decimal('54.14'),  # €379 for 7 nights
        'price_per_lesson': Decimal('30.00'),  # avg of course prices
        'skill_levels': ['beginner', 'intermediate', 'advanced'],
        'website': 'https://www.puresurfcamps.com/en/surf-camps/surf-camps-portugal/surf-camp-peniche/',
        'phone': '+49 89 59988365',
        'instagram': '@puresurfcamps',
        'has_pool': True,
        'has_restaurant': True,
        'has_yoga': True,
        'has_parties': False,
    },
    {
        'name': 'Ferrel Surf House',
        'slug': 'ferrel-surf-house',
        'region': regions['Portugal_Peniche'],
        'short_description': 'Ocean-front surf school with individualized training and video analysis',
        'description': 'Located 50m from Baleal Beach. Familiar vibe, not commercial. Individualized surf training with video analysis. TripAdvisor Travellers\' Choice 2020.',
        'address': 'Avenida da Praia, nº 25, Ferrel - Baleal, 2520-051 Peniche, Portugal',
        'latitude': Decimal('39.3583'),
        'longitude': Decimal('-9.2633'),
        'price_per_night': Decimal('50.00'),
        'price_per_lesson': Decimal('50.00'),
        'skill_levels': ['beginner', 'intermediate'],
        'website': 'https://www.ferrelsurfhouse.com/',
        'email': 'contact@ferrelsurfhouse.com',
        'phone': '+351 925 013 006',
        'instagram': '@ferrelsurfhouse',
        'whatsapp': '+351 910896687',
        'has_pool': False,
        'has_restaurant': False,
        'has_yoga': False,
        'has_parties': False,
    },
    {
        'name': 'Peniche Surf Lodge',
        'slug': 'peniche-surf-lodge',
        'region': regions['Portugal_Peniche'],
        'short_description': 'Luxury affordable accommodation with family-style surf packages',
        'description': 'Located within ancient castle walls. Walking distance to shops/cafes. 3+ day packages year-round. Beach camps with parasols, windbreaks, volleyball.',
        'address': 'Peniche, Portugal',
        'latitude': Decimal('39.3583'),
        'longitude': Decimal('-9.2633'),
        'price_per_night': Decimal('62.86'),  # €350 for dorm avg
        'price_per_lesson': Decimal('45.00'),
        'skill_levels': ['beginner', 'intermediate'],
        'website': 'https://www.penichesurflodge.com/',
        'email': 'surfpeniche@gmail.com',
        'phone': '+351 912 590 574',
        'instagram': '@penichesurflodge',
        'has_pool': False,
        'has_restaurant': True,
        'has_yoga': False,
        'has_parties': True,
    },

    # INDONESIA
    {
        'name': 'Surfmakers - Bali',
        'slug': 'surfmakers-bali-kuta',
        'region': regions['Indonesia_Bali'],
        'short_description': '2-week comprehensive surf camp in Kuta, Bali',
        'description': '5 minutes walk from ocean. 2-week camp includes accommodation, breakfasts, 6 surf lessons, theory, equipment, transfers, video/photo, excursions.',
        'address': 'Kuta, Bali, Indonesia',
        'latitude': Decimal('-8.7245'),
        'longitude': Decimal('115.1689'),
        'price_per_night': Decimal('145.38'),  # $1890 for 13 nights
        'price_per_lesson': Decimal('50.00'),
        'skill_levels': ['beginner', 'intermediate'],
        'website': 'https://surfmakerscamp.com/surfcampbali',
        'phone': '+62 813 3751 7799',
        'instagram': '@surfmakers',
        'whatsapp': '+62 813 3751 7799',
        'has_pool': False,
        'has_restaurant': True,
        'has_yoga': False,
        'has_parties': False,
    },
    {
        'name': 'Surf Discovery',
        'slug': 'surf-discovery-bali',
        'region': regions['Indonesia_Bali'],
        'short_description': 'Russian surfing school in Kuta with professional coaching',
        'description': 'Professional sportsmen united to create a Russian surfing school. 2 minutes from Kuta Beach. Group/individual lessons, surf trips, yoga, photography services.',
        'address': 'Jalan Pantai Kuta, Kuta, Bali 80361, Indonesia',
        'latitude': Decimal('-8.7245'),
        'longitude': Decimal('115.1689'),
        'price_per_night': Decimal('50.00'),
        'price_per_lesson': Decimal('60.00'),
        'skill_levels': ['beginner', 'intermediate', 'advanced'],
        'website': 'https://surfdiscovery.org/',
        'email': 'info@surfdiscovery.ru',
        'phone': '+62-8170-399-9959',
        'instagram': '@surfdiscoverybali',
        'has_pool': False,
        'has_restaurant': True,
        'has_yoga': True,
        'has_parties': False,
    },
    {
        'name': 'Kinetika Surf Camp',
        'slug': 'kinetika-surf-camp-bali',
        'region': regions['Indonesia_Bali'],
        'short_description': 'Fully planned author programs focused on good waves',
        'description': 'Fully planned and organized author programs on specific dates. Includes trips to Mentawai, G-Land, and Sumba. Prioritizes good waves and quality instruction.',
        'address': 'Bali, Indonesia',
        'latitude': Decimal('-8.6500'),
        'longitude': Decimal('115.2500'),
        'price_per_night': Decimal('100.00'),
        'price_per_lesson': Decimal('50.00'),
        'skill_levels': ['beginner', 'intermediate', 'advanced'],
        'website': 'https://kinetika.surf/camps',
        'email': '[email protected]',
        'phone': '+628113909055',
        'instagram': '@kinetika.surf',
        'has_pool': False,
        'has_restaurant': True,
        'has_yoga': True,
        'has_parties': False,
    },
    {
        'name': 'Wave House - Canggu',
        'slug': 'wave-house-canggu',
        'region': regions['Indonesia_Bali'],
        'short_description': 'More than just a surf camp - operating since 2011, 20,000+ surfers',
        'description': 'Comprehensive surf, yoga, meals, and community activities. Located near Berawa Beach. Surf + Stay packages, Day Pass, individual lessons available.',
        'address': 'Jl. Subak Sari, Canggu, Bali, Indonesia',
        'latitude': Decimal('-8.6500'),
        'longitude': Decimal('115.1700'),
        'price_per_night': Decimal('75.00'),
        'price_per_lesson': Decimal('50.00'),
        'skill_levels': ['beginner', 'intermediate'],
        'website': 'https://wavehouse.ru/',
        'phone': '+62 81246902423',
        'instagram': '@wavehousebali',
        'whatsapp': '+62 81246902423',
        'has_pool': True,
        'has_restaurant': True,
        'has_yoga': True,
        'has_parties': True,
    },
    {
        'name': 'Padang Padang Surf Camp',
        'slug': 'padang-padang-surf-camp',
        'region': regions['Indonesia_Bali'],
        'short_description': 'Bali\'s Premier Surf Camp with year-round operation and wellness focus',
        'description': 'Year-round operation with organic meals and serene ambience. Surf instruction, yoga, wellness retreats. Located in Uluwatu.',
        'address': 'Jl Labuan Sait, Pecatu, Bali 80361, Indonesia',
        'latitude': Decimal('-8.8098'),
        'longitude': Decimal('115.1398'),
        'price_per_night': Decimal('100.00'),
        'price_per_lesson': Decimal('60.00'),
        'skill_levels': ['beginner', 'intermediate', 'advanced'],
        'website': 'https://www.balisurfingcamp.com/',
        'phone': '+62 811 3894 440',
        'instagram': '@padangpadangsurfcampbali',
        'has_pool': True,
        'has_restaurant': True,
        'has_yoga': True,
        'has_parties': False,
    },

    # LOMBOK
    {
        'name': 'KuraSurf',
        'slug': 'kurasurf-lombok',
        'region': regions['Indonesia_Lombok'],
        'short_description': 'Resort-style wellness-integrated surf camp',
        'description': '11 weekly sessions, yoga, ice baths, sauna recovery. Located in Kuta, Lombok. High-quality instruction with wellness focus.',
        'address': 'Kuta, Lombok, Indonesia',
        'latitude': Decimal('-8.7417'),
        'longitude': Decimal('116.3417'),
        'price_per_night': Decimal('105.57'),  # €739 for 7 nights
        'price_per_lesson': Decimal('50.00'),
        'skill_levels': ['beginner', 'intermediate'],
        'website': 'https://www.kurasurf.com/',
        'email': 'info@kurasurf.com',
        'phone': '+1 424 231-4509',
        'instagram': '@kura.surf',
        'has_pool': True,
        'has_restaurant': True,
        'has_yoga': True,
        'has_parties': False,
    },
    {
        'name': 'LMBK Surf House',
        'slug': 'lmbk-surf-house-lombok',
        'region': regions['Indonesia_Lombok'],
        'short_description': 'Top-rated adults-only surf camp with 2:1 coaching ratio',
        'description': '18+ adults-only property. 2:1 coaching ratio (max 2 students per instructor). Video analysis, guided instruction. Private rooms & luxury dorm.',
        'address': 'Kuta, Lombok, Indonesia',
        'latitude': Decimal('-8.7417'),
        'longitude': Decimal('116.3417'),
        'price_per_night': Decimal('80.00'),
        'price_per_lesson': Decimal('50.00'),
        'skill_levels': ['beginner', 'intermediate'],
        'website': 'https://lmbksurfhouse.com/',
        'email': 'lmbksurfhouse@gmail.com',
        'phone': '+62 821-4591-3335',
        'instagram': '@lmbksurfhouse',
        'has_pool': True,
        'has_restaurant': True,
        'has_yoga': True,
        'has_parties': False,
    },
    {
        'name': 'Surf Camp Lombok',
        'slug': 'surf-camp-lombok',
        'region': regions['Indonesia_Lombok'],
        'short_description': 'Two-week journey with 2 daily sessions and theory instruction',
        'description': 'Beachfront with direct boat access to 7 diverse breaks. 2 surf sessions/day, theory & practical. Beginner and intermediate/advanced programs.',
        'address': 'Gerupuk, Lombok, Indonesia',
        'latitude': Decimal('-8.5000'),
        'longitude': Decimal('116.2500'),
        'price_per_night': Decimal('100.00'),
        'price_per_lesson': Decimal('50.00'),
        'skill_levels': ['beginner', 'intermediate', 'advanced'],
        'website': 'https://www.surfcampindonesia.com/',
        'email': 'bookings@surfcampindo.com',
        'phone': '006281338897423',
        'instagram': '@surfcamplombok',
        'has_pool': False,
        'has_restaurant': True,
        'has_yoga': True,
        'has_parties': False,
    },

    # COSTA RICA
    {
        'name': 'Iguana Surf Camp',
        'slug': 'iguana-surf-camp-tamarindo',
        'region': regions['Costa Rica_Guanacaste'],
        'short_description': '#1 Tamarindo Surf Shop, Camp & Tour Agency since 1989',
        'description': 'Beachfront location in center of Tamarindo. Mission to share wave knowledge and ocean respect. Surf lessons, accommodations, and adventure tours.',
        'address': 'Tamarindo, Costa Rica',
        'latitude': Decimal('10.3010'),
        'longitude': Decimal('-85.8386'),
        'price_per_night': Decimal('92.71'),  # $649-849 for 5-7 nights avg
        'price_per_lesson': Decimal('65.00'),
        'skill_levels': ['beginner', 'intermediate'],
        'website': 'https://iguanasurf.net/',
        'email': 'reservations@iguanasurf.net',
        'phone': '+1 (813) 321-5532',
        'instagram': '@iguanasurf_tamarindo',
        'whatsapp': '+506 8800-7873',
        'has_pool': False,
        'has_restaurant': True,
        'has_yoga': False,
        'has_parties': False,
    },

    # MOROCCO
    {
        'name': 'Gota Dagua - Tamraght',
        'slug': 'gota-dagua-tamraght',
        'region': regions['Morocco_Taghazout'],
        'short_description': 'High-quality surf coaching with family atmosphere',
        'description': '7-night package €379. Weekly packages combining surf and yoga. Beginner-to-intermediate progression. World-class point breaks. Local cuisine and evening activities.',
        'address': 'Tamraght, Morocco',
        'latitude': Decimal('30.4583'),
        'longitude': Decimal('-9.8167'),
        'price_per_night': Decimal('54.14'),  # €379 for 7 nights
        'price_per_lesson': Decimal('40.00'),
        'skill_levels': ['beginner', 'intermediate'],
        'website': 'https://gotadaguasurf.com/surfcamp/tamraght-morocco/',
        'email': 'info@wordpress-762907-2632641.cloudwaysapps.com',
        'phone': '+351 939 591 707',
        'instagram': '@gotadagua_surf',
        'has_pool': True,
        'has_restaurant': True,
        'has_yoga': True,
        'has_parties': False,
    },
    {
        'name': 'Moroc Surf Camp',
        'slug': 'moroc-surf-camp',
        'region': regions['Morocco_Taghazout'],
        'short_description': 'Your yoga and surf adventure in Tamraght',
        'description': 'Yoga and surf adventure combining instruction, accommodation, dining, and recreational activities. Team experiences available.',
        'address': 'Hay Tissaluine, Tamraght, Aourir 80750, Morocco',
        'latitude': Decimal('30.4583'),
        'longitude': Decimal('-9.8167'),
        'price_per_night': Decimal('70.00'),
        'price_per_lesson': Decimal('45.00'),
        'skill_levels': ['beginner', 'intermediate'],
        'website': 'https://www.marocsurfcamp.com/',
        'email': 'contact@marocsurfcamp.com',
        'phone': '+212 657156219',
        'instagram': '@marocsurfcamp',
        'has_pool': True,
        'has_restaurant': True,
        'has_yoga': True,
        'has_parties': False,
    },
    {
        'name': 'Zen Surf Morocco',
        'slug': 'zen-surf-morocco',
        'region': regions['Morocco_Taghazout'],
        'short_description': 'Immersive surf & yoga vacations in Taghazout Bay',
        'description': 'Beachfront location with traditional Moroccan dining. Instruction, yoga, accommodations. Immersive wellness and water sports experience.',
        'address': 'Hay Tihaouarine - Banana Beach, Aourir, Morocco',
        'latitude': Decimal('30.4583'),
        'longitude': Decimal('-9.8167'),
        'price_per_night': Decimal('80.00'),
        'price_per_lesson': Decimal('50.00'),
        'skill_levels': ['beginner', 'intermediate'],
        'website': 'https://www.zensurfmorocco.com',
        'email': 'contact@zensurfmorocco.com',
        'phone': '+33 6 17 41 23 78',
        'instagram': '@zensurfmorocco',
        'has_pool': False,
        'has_restaurant': True,
        'has_yoga': True,
        'has_parties': False,
    },
    {
        'name': 'Blue Waves Surf House',
        'slug': 'blue-waves-surf-house-anza',
        'region': regions['Morocco_Souss-Massa'],
        'short_description': 'Charming fishing village with healthy local cuisine',
        'description': '6 rooms for up to 17 guests. The Jungle Beach Bar serves healthy local cuisine. Located 13km north of Taghazout, 45min from Agadir airport.',
        'address': 'Anza, Agadir 80000, Morocco',
        'latitude': Decimal('30.3000'),
        'longitude': Decimal('-9.9000'),
        'price_per_night': Decimal('65.00'),
        'price_per_lesson': Decimal('45.00'),
        'skill_levels': ['beginner', 'intermediate'],
        'website': 'https://www.bluewavesurfhouse.com/anza',
        'email': 'reservations@bluewavesurfhouse.com',
        'phone': '+212 666 121 252',
        'instagram': '@bluewavesurfhouse',
        'has_pool': False,
        'has_restaurant': True,
        'has_yoga': False,
        'has_parties': False,
    },

    # SRI LANKA
    {
        'name': 'Lucky\'s Surf Camp',
        'slug': 'luckys-surf-camp-weligama',
        'region': regions['Sri Lanka_Southern Province'],
        'short_description': 'Founded by Sri Lanka\'s National Surfing Champion',
        'description': 'Lifestyle-focused beachfront camp. Expert coaching, wellness activities, yoga. 30m from ocean in Weligama fishing village. Rooftop café with ocean views.',
        'address': 'New by Pass road, Pelana, Weligama 81700, Sri Lanka',
        'latitude': Decimal('5.9497'),
        'longitude': Decimal('80.7891'),
        'price_per_night': Decimal('70.00'),
        'price_per_lesson': Decimal('50.00'),
        'skill_levels': ['beginner', 'intermediate', 'advanced'],
        'website': 'https://luckyssurfcamp.com/',
        'email': 'hello@luckyssurfcamp.com',
        'phone': '+94 77 106 3202',
        'instagram': '@luckyssurfcamp',
        'has_pool': True,
        'has_restaurant': True,
        'has_yoga': True,
        'has_parties': False,
    },
    {
        'name': 'Surf\'s Up Sri Lanka',
        'slug': 'surfs-up-sri-lanka',
        'region': regions['Sri Lanka_Southern Province'],
        'short_description': 'Comprehensive hotel and surf camp with rooftop bar',
        'description': 'Hotel, surf instruction, restaurant, rooftop bar. 10,000+ trained surfers since 2018. Year-round operation, peak October-May.',
        'address': 'New Galle Road 429, Weligama, Matara 81700, Sri Lanka',
        'latitude': Decimal('5.9497'),
        'longitude': Decimal('80.7891'),
        'price_per_night': Decimal('87.14'),  # $875 for 10 nights
        'price_per_lesson': Decimal('50.00'),
        'skill_levels': ['beginner', 'intermediate'],
        'website': 'https://surfs-up.ru/surfcamp',
        'email': 'info@surfs-up.ru',
        'phone': '+79690390719',
        'instagram': '@surfsuphotel',
        'whatsapp': '+79690390719',
        'has_pool': True,
        'has_restaurant': True,
        'has_yoga': False,
        'has_parties': True,
    },

    # RUSSIA
    {
        'name': 'König Surf Club',
        'slug': 'konig-surf-club-kaliningrad',
        'region': regions['Russia_Kaliningrad'],
        'short_description': 'First surfing school on the Baltic Sea',
        'description': 'Year-round lessons, summer camps, international tours. Modern center on Baltic Sea coast with experienced instructors. Available 09:00-19:00 daily.',
        'address': 'ул. Приморская 21, г. Зеленоградск, Калининградская область, Russia',
        'latitude': Decimal('54.9500'),
        'longitude': Decimal('21.8333'),
        'price_per_night': Decimal('50.00'),
        'price_per_lesson': Decimal('40.00'),
        'skill_levels': ['beginner', 'intermediate'],
        'website': 'https://konigsurf.club/',
        'email': 'info@konigsurf.club',
        'phone': '+7-906-217-5550',
        'instagram': '@konigsurf.club',
        'has_pool': False,
        'has_restaurant': False,
        'has_yoga': False,
        'has_parties': False,
    },
    {
        'name': 'Snowave Kamchatka',
        'slug': 'snowave-kamchatka',
        'region': regions['Russia_Kamchatka'],
        'short_description': 'Russia\'s first surf school with 19,000+ students trained',
        'description': 'Established 2009. Summer & winter programs on Pacific Ocean. 19,000+ students taught. Modern instruction with experienced team.',
        'address': 'Халактырский пляж, Камчатка, Russia',
        'latitude': Decimal('56.5500'),
        'longitude': Decimal('161.0000'),
        'price_per_night': Decimal('60.00'),
        'price_per_lesson': Decimal('45.00'),
        'skill_levels': ['beginner', 'intermediate'],
        'website': 'https://snowave-kamchatka.com/',
        'phone': '+79960356533',
        'instagram': '@snowave_kamchatka',
        'whatsapp': '+79960356533',
        'has_pool': False,
        'has_restaurant': False,
        'has_yoga': False,
        'has_parties': False,
    },
]

# Create camps
created_count = 0
for camp_data in camps_data:
    try:
        camp = SurfCamp.objects.create(**camp_data)
        created_count += 1
        print(f"  ✓ Created: {camp.name}")
    except Exception as e:
        print(f"  ✗ Error creating {camp_data.get('name', 'Unknown')}: {str(e)}")

print(f"\n{'='*80}")
print(f"✓ COMPLETE: Created {created_count} surf camps with real data")
print(f"✓ Database successfully cleaned and populated")
print(f"{'='*80}")
