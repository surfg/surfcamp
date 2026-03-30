#!/usr/bin/env python
"""
Populate Sri Lanka surf camps data
Run: python populate_sri_lanka.py
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from camps.models import Country, Region, BoardType, Amenity, SurfCamp, Instructor, Activity, Review
from spots.models import SurfSpot


def create_sri_lanka():
    """Create Sri Lanka and surf regions"""
    sri_lanka, _ = Country.objects.get_or_create(
        code='LKA',
        defaults={
            'name': 'Шри-Ланка',
            'name_en': 'Sri Lanka',
            'description': 'Sri Lanka offers year-round surfing with two distinct seasons. The south coast (Weligama, Hikkaduwa) is best November-April, while the east coast (Arugam Bay) fires May-October. Perfect warm water waves for all levels.'
        }
    )

    regions_data = [
        {'name': 'Велигама', 'name_en': 'Weligama', 'latitude': 5.9750, 'longitude': 80.4297,
         'description': 'Sri Lanka\'s ultimate beginner beach with consistent, gentle waves year-round'},
        {'name': 'Аругам Бэй', 'name_en': 'Arugam Bay', 'latitude': 6.8404, 'longitude': 81.8368,
         'description': 'International surf destination and only WSL competition venue in Sri Lanka'},
        {'name': 'Мирисса', 'name_en': 'Mirissa', 'latitude': 5.9466, 'longitude': 80.4583,
         'description': 'Popular surf spot on the south coast, great for intermediates'},
        {'name': 'Хиккадува', 'name_en': 'Hikkaduwa', 'latitude': 6.1407, 'longitude': 80.1012,
         'description': 'Sri Lanka\'s surf mecca with mix of shore breaks and reefs'},
        {'name': 'Ахангама', 'name_en': 'Ahangama', 'latitude': 5.9744, 'longitude': 80.3647,
         'description': 'Home to famous reef breaks for intermediate to advanced surfers'},
        {'name': 'Хирикетия', 'name_en': 'Hiriketiya', 'latitude': 5.9500, 'longitude': 80.7167,
         'description': 'Scenic horseshoe bay with consistent waves and laid-back vibe'},
    ]

    regions = []
    for r in regions_data:
        region, _ = Region.objects.get_or_create(
            country=sri_lanka, name_en=r['name_en'],
            defaults=r
        )
        regions.append(region)

    print(f"Created Sri Lanka with {len(regions)} regions")
    return sri_lanka, regions


def create_surf_camps(regions):
    """Create Sri Lanka surf camps with real data"""
    board_types = list(BoardType.objects.all())
    amenities = list(Amenity.objects.all())

    camps_data = [
        {
            'name': 'The Surfer Weligama',
            'slug': 'the-surfer-weligama',
            'region': 'Weligama',
            'short_description': 'Premier beginner surf camp in Sri Lanka\'s best learning destination',
            'description': '''The Surfer Weligama is one of the most mentioned surf camps in Sri Lanka, renowned for exceptional beginner instruction. Located at Weligama Bay, we offer the perfect learning environment with consistent, gentle waves.

Our comprehensive packages include 6-7 surf lessons, matching yoga sessions, board rental, and breakfast/dinner. The rooftop kitchen and communal areas make it easy to connect with fellow surfers.

We focus on building confidence and proper technique, ensuring you leave with skills that will serve you for life. Our instructors speak multiple languages and have years of experience with nervous beginners.''',
            'history': 'Founded to share the magic of Sri Lankan waves with beginners from around the world.',
            'address': 'Weligama Bay, Southern Province, Sri Lanka',
            'latitude': 5.9720,
            'longitude': 80.4285,
            'price_per_night': 55,
            'price_per_lesson': 30,
            'has_bed_breakfast': True,
            'bed_breakfast_price': 40,
            'skill_levels': ['beginner'],
            'board_rental_available': True,
            'board_rental_price': 8,
            'has_pool': False,
            'has_restaurant': True,
            'has_yoga': True,
            'has_parties': False,
            'website': 'https://thesurferweligama.com',
            'email': 'info@thesurferweligama.com',
            'instagram': '@thesurferweligama',
            'rating': 4.8,
            'reviews_count': 287,
            'is_featured': True,
        },
        {
            'name': 'Solid Surf & Yoga House',
            'slug': 'solid-surf-yoga-house',
            'region': 'Weligama',
            'short_description': 'All-inclusive surf and yoga retreat with pool and palm garden',
            'description': '''Solid Surf & Yoga House is the best surf camp in Sri Lanka for beginner to intermediate surfers. Our all-inclusive "One Package Fits All" program includes accommodation, meals, structured surf lessons, surf guiding, yoga, and access to multiple surf spots along Sri Lanka's south coast.

Our property features a stunning dark-tiled pool set in a palm-fringed garden - perfect for relaxing after surf sessions. We offer up to 6 hours of daily surfing with video analysis to accelerate your progression.

Whether you're standing on a board for the first time or looking to refine your technique, our ISA-certified instructors will help you achieve your goals.''',
            'address': 'Weligama Beach Road, Weligama, Sri Lanka',
            'latitude': 5.9735,
            'longitude': 80.4312,
            'price_per_night': 95,
            'price_per_lesson': 45,
            'has_bed_breakfast': True,
            'bed_breakfast_price': 65,
            'skill_levels': ['beginner', 'intermediate'],
            'board_rental_available': True,
            'board_rental_price': 12,
            'has_pool': True,
            'has_restaurant': True,
            'has_yoga': True,
            'has_parties': False,
            'website': 'https://solidsurfhouse.com',
            'email': 'info@solidsurfhouse.com',
            'instagram': '@solidsurfhouse',
            'rating': 4.9,
            'reviews_count': 156,
            'is_featured': True,
        },
        {
            'name': 'Arugam Bay Surf Camp',
            'slug': 'arugam-bay-surf-camp',
            'region': 'Arugam Bay',
            'short_description': 'Authentic surf camp at Sri Lanka\'s world-class right-hand point break',
            'description': '''Arugam Bay Surf Camp is located at Sri Lanka's premier surf destination - an international surf spot and the only WSL competition venue in the country. Our whitewash cabanas and hammock-filled garden create a relaxed atmosphere perfect for surf-focused holidays.

Our 15-day packages include 13 surf classes with theory and video analysis, plus 13 yoga classes to keep you limber. We cater to all levels, from beginners learning on the inside section to advanced surfers tackling the famous Main Point.

The east coast season runs May-October, offering consistent swells and offshore winds. Book in-season for the best conditions.''',
            'address': 'Main Road, Arugam Bay, Eastern Province, Sri Lanka',
            'latitude': 6.8412,
            'longitude': 81.8356,
            'price_per_night': 65,
            'price_per_lesson': 35,
            'has_bed_breakfast': True,
            'bed_breakfast_price': 45,
            'skill_levels': ['beginner', 'intermediate', 'advanced'],
            'board_rental_available': True,
            'board_rental_price': 10,
            'has_pool': False,
            'has_restaurant': True,
            'has_yoga': True,
            'has_parties': True,
            'website': 'https://arugambaysurfcamp.com',
            'email': 'info@arugambaysurfcamp.com',
            'instagram': '@arugambaysurfcamp',
            'rating': 4.7,
            'reviews_count': 203,
            'is_featured': True,
        },
        {
            'name': 'Safa Surf Camp',
            'slug': 'safa-surf-camp-arugam',
            'region': 'Arugam Bay',
            'short_description': 'Personalized surf coaching with beachside accommodation in Arugam Bay',
            'description': '''Safa Surf Camp offers personalized surf coaching from beginner to experienced levels. Located in the heart of Arugam Bay, we're just steps away from the eastern coast's main surf spots.

Our programs include surf coaching sessions, theory lessons, yoga, and comfortable beachside accommodation. We keep groups small to ensure personalized attention and faster progression.

The laid-back Arugam Bay vibe, combined with world-class waves, makes this the perfect destination for a serious surf trip.''',
            'address': 'Beach Road, Arugam Bay, Sri Lanka',
            'latitude': 6.8395,
            'longitude': 81.8378,
            'price_per_night': 50,
            'price_per_lesson': 30,
            'has_bed_breakfast': True,
            'bed_breakfast_price': 35,
            'skill_levels': ['beginner', 'intermediate'],
            'board_rental_available': True,
            'board_rental_price': 8,
            'has_pool': False,
            'has_restaurant': True,
            'has_yoga': True,
            'has_parties': False,
            'website': 'https://safaarugambay.com',
            'email': 'info@safaarugambay.com',
            'instagram': '@safasurfcamp',
            'rating': 4.6,
            'reviews_count': 134,
            'is_featured': False,
        },
        {
            'name': 'The Salty Pelican',
            'slug': 'salty-pelican-hiriketiya',
            'region': 'Hiriketiya',
            'short_description': 'Boutique surf villa with pool overlooking scenic Hiriketiya Bay',
            'description': '''The Salty Pelican is a boutique surf camp set above beautiful Hiriketiya Bay - a scenic horseshoe-shaped cove on Sri Lanka's south coast. Our modern villa features a pool, yoga deck, lounge, and bar with ocean views.

We offer 4, 8, and 11-day surf packages for all levels, with new surfboard rental included. The bay's consistent waves are perfect for progression, while nearby breaks offer more challenge for experienced surfers.

The relaxed Hiriketiya vibe, combined with our comfortable amenities, makes this perfect for surfers seeking both waves and wellness.''',
            'address': 'Hiriketiya Bay, Dikwella, Sri Lanka',
            'latitude': 5.9485,
            'longitude': 80.7142,
            'price_per_night': 85,
            'price_per_lesson': 40,
            'has_bed_breakfast': True,
            'bed_breakfast_price': 60,
            'skill_levels': ['beginner', 'intermediate'],
            'board_rental_available': True,
            'board_rental_price': 15,
            'has_pool': True,
            'has_restaurant': True,
            'has_yoga': True,
            'has_parties': True,
            'instagram': '@thesaltypelican',
            'rating': 4.8,
            'reviews_count': 98,
            'is_featured': False,
        },
        {
            'name': 'Dreamsea Sri Lanka',
            'slug': 'dreamsea-sri-lanka',
            'region': 'Ahangama',
            'short_description': 'Boho-chic surf resort with pool and walkable reef breaks',
            'description': '''Dreamsea Sri Lanka is a stylish surf retreat in Ahangama featuring boho-chic interiors, a refreshing pool, and a lively bar. The property is walkable to several reef breaks, making it ideal for surfers of all levels.

Our surf programs combine daily lessons with yoga and wellness activities. The international atmosphere attracts surfers from around the world, creating a vibrant community vibe.

Ahangama is famous for its reef breaks including Kabalana and The Rock - perfect for intermediate surfers looking to take their skills to the next level.''',
            'address': 'Ahangama, Southern Province, Sri Lanka',
            'latitude': 5.9756,
            'longitude': 80.3658,
            'price_per_night': 90,
            'price_per_lesson': 45,
            'has_bed_breakfast': True,
            'bed_breakfast_price': 65,
            'skill_levels': ['beginner', 'intermediate', 'advanced'],
            'board_rental_available': True,
            'board_rental_price': 15,
            'has_pool': True,
            'has_restaurant': True,
            'has_yoga': True,
            'has_parties': True,
            'website': 'https://dreamsea.world/sri-lanka',
            'instagram': '@dreamseaworldwide',
            'rating': 4.5,
            'reviews_count': 167,
            'is_featured': False,
        },
        {
            'name': 'Surf & Yoga Mirissa',
            'slug': 'surf-yoga-mirissa',
            'region': 'Mirissa',
            'short_description': 'Intimate surf retreat with pool and co-work space in Mirissa',
            'description': '''Surf & Yoga Mirissa offers an intimate surf experience with just 4 rooms plus a dorm. Our 15-day packages include 12 surf sessions, 12 yoga sessions, and 3 massages.

The property features a pool, co-work space for digital nomads, and is minutes from Mirissa's popular breaks. We focus on quality over quantity, ensuring personalized attention for every guest.

Mirissa is also famous for whale watching, adding an extra dimension to your surf trip. The south coast season runs November-April with consistent swells and warm water.''',
            'address': 'Mirissa Beach Road, Mirissa, Sri Lanka',
            'latitude': 5.9478,
            'longitude': 80.4592,
            'price_per_night': 70,
            'price_per_lesson': 35,
            'has_bed_breakfast': True,
            'bed_breakfast_price': 50,
            'skill_levels': ['beginner', 'intermediate'],
            'board_rental_available': True,
            'board_rental_price': 10,
            'has_pool': True,
            'has_restaurant': True,
            'has_yoga': True,
            'has_parties': False,
            'website': 'https://surfnyogamirissa.com',
            'email': 'info@surfnyogamirissa.com',
            'instagram': '@surfyogamirissa',
            'rating': 4.7,
            'reviews_count': 89,
            'is_featured': False,
        },
        {
            'name': 'Hikkaduwa Surf School',
            'slug': 'hikkaduwa-surf-school',
            'region': 'Hikkaduwa',
            'short_description': 'Classic Sri Lankan surf school in the original surf town',
            'description': '''Hikkaduwa Surf School is located in Sri Lanka's original surf destination - the town that started it all. During the south coast season (November-March), Hikkaduwa attracts thousands of surfers with its mix of shore breaks and reefs.

We offer lessons for all levels, from gentle beach breaks for beginners to the famous Main Reef for advanced surfers. Our local instructors know these waves inside out, having surfed them their entire lives.

Affordable rates, warm hospitality, and quality waves make Hikkaduwa a must-visit on any Sri Lanka surf trip.''',
            'address': 'Galle Road, Hikkaduwa, Sri Lanka',
            'latitude': 6.1395,
            'longitude': 80.0998,
            'price_per_night': 40,
            'price_per_lesson': 25,
            'has_bed_breakfast': True,
            'bed_breakfast_price': 30,
            'skill_levels': ['beginner', 'intermediate', 'advanced'],
            'board_rental_available': True,
            'board_rental_price': 8,
            'has_pool': False,
            'has_restaurant': True,
            'has_yoga': False,
            'has_parties': True,
            'instagram': '@hikkaduwasurfschool',
            'rating': 4.4,
            'reviews_count': 245,
            'is_featured': False,
        },
        {
            'name': 'TS2 Surf Camp',
            'slug': 'ts2-surf-camp-weligama',
            'region': 'Weligama',
            'short_description': 'Budget-friendly surf camp with quality instruction in Weligama',
            'description': '''TS2 Surf Camp is a solid choice for budget-conscious surfers looking to learn at one of the best beginner spots in the world - Weligama Beach.

We offer affordable packages with 10 surf lessons over 7 days for under $300. Simple, clean rooms and a friendly atmosphere make it easy to focus on what matters - surfing!

Our local instructors provide patient, encouraging coaching to get you standing and riding waves quickly. Equipment is included in all packages.''',
            'address': 'Weligama Beach, Weligama, Sri Lanka',
            'latitude': 5.9715,
            'longitude': 80.4265,
            'price_per_night': 35,
            'price_per_lesson': 20,
            'has_bed_breakfast': True,
            'bed_breakfast_price': 25,
            'skill_levels': ['beginner'],
            'board_rental_available': True,
            'board_rental_price': 6,
            'has_pool': False,
            'has_restaurant': True,
            'has_yoga': False,
            'has_parties': False,
            'instagram': '@ts2surfcamp',
            'rating': 4.3,
            'reviews_count': 176,
            'is_featured': False,
        },
    ]

    region_map = {r.name_en: r for r in regions}
    created_camps = []

    for camp_data in camps_data:
        region_name = camp_data.pop('region')
        region = region_map.get(region_name)
        if not region:
            print(f"Region {region_name} not found, skipping {camp_data['name']}")
            continue

        camp, created = SurfCamp.objects.get_or_create(
            slug=camp_data['slug'],
            defaults={**camp_data, 'region': region}
        )

        # Add board types based on skill levels
        if 'beginner' in camp.skill_levels:
            camp.board_types.add(*[bt for bt in board_types if bt.name_en in ['Soft Top', 'Funboard', 'Longboard']])
        if 'intermediate' in camp.skill_levels:
            camp.board_types.add(*[bt for bt in board_types if bt.name_en in ['Funboard', 'Mid Length', 'Longboard']])
        if 'advanced' in camp.skill_levels:
            camp.board_types.add(*board_types)

        # Add amenities
        camp.amenities.add(*amenities[:8])

        created_camps.append(camp)

    print(f"Created {len(created_camps)} surf camps in Sri Lanka")
    return created_camps


def create_surf_spots(regions):
    """Create Sri Lanka surf spots"""
    spots_data = [
        {
            'name': 'Weligama Bay',
            'slug': 'weligama-bay',
            'region': 'Weligama',
            'description': 'The ultimate beginner beach in Sri Lanka with consistent, gentle waves. Sandy bottom and wide bay provide safe learning conditions year-round.',
            'short_description': 'Sri Lanka\'s best beginner beach',
            'latitude': 5.9725,
            'longitude': 80.4298,
            'wave_direction': 'both',
            'wave_type': 'beach',
            'wave_height_min': 0.3,
            'wave_height_max': 1.5,
            'skill_levels': ['beginner', 'intermediate'],
            'best_tide': 'All tides',
            'best_swell': 'SW 2-4 ft',
            'best_wind': 'NE offshore',
            'best_season': 'November - April',
            'crowd_level': 'high',
            'has_parking': True,
            'has_showers': True,
            'has_rentals': True,
            'has_cafe': True,
            'rating': 4.5,
        },
        {
            'name': 'Arugam Bay Main Point',
            'slug': 'arugam-bay-main-point',
            'region': 'Arugam Bay',
            'description': 'World-famous right-hand point break and only WSL competition venue in Sri Lanka. Long, peeling waves up to 300m rides on good days.',
            'short_description': 'World-class right-hand point break',
            'latitude': 6.8415,
            'longitude': 81.8345,
            'wave_direction': 'right',
            'wave_type': 'point',
            'wave_height_min': 1.0,
            'wave_height_max': 3.0,
            'skill_levels': ['intermediate', 'advanced'],
            'best_tide': 'Mid to High',
            'best_swell': 'S-SW 4-8 ft',
            'best_wind': 'NW offshore',
            'best_season': 'May - October',
            'crowd_level': 'very_high',
            'has_rocks': True,
            'has_parking': True,
            'has_cafe': True,
            'has_rentals': True,
            'rating': 4.9,
        },
        {
            'name': 'Whiskey Point',
            'slug': 'whiskey-point',
            'region': 'Arugam Bay',
            'description': 'Fast right-hander located north of Main Point. Shorter rides but more powerful waves. Named after the nearby beach bar.',
            'short_description': 'Fast and powerful right-hander',
            'latitude': 6.8650,
            'longitude': 81.8420,
            'wave_direction': 'right',
            'wave_type': 'reef',
            'wave_height_min': 1.0,
            'wave_height_max': 2.5,
            'skill_levels': ['intermediate', 'advanced'],
            'best_tide': 'Mid',
            'best_swell': 'S 4-6 ft',
            'best_wind': 'NW',
            'best_season': 'June - September',
            'crowd_level': 'medium',
            'has_reef': True,
            'has_parking': True,
            'has_cafe': True,
            'rating': 4.6,
        },
        {
            'name': 'Mirissa Beach',
            'slug': 'mirissa-beach',
            'region': 'Mirissa',
            'description': 'Popular south coast spot with peaks along the beach. Can get crowded but offers fun waves for all levels.',
            'short_description': 'Popular beach break for all levels',
            'latitude': 5.9470,
            'longitude': 80.4590,
            'wave_direction': 'both',
            'wave_type': 'beach',
            'wave_height_min': 0.5,
            'wave_height_max': 2.0,
            'skill_levels': ['beginner', 'intermediate'],
            'best_tide': 'Mid to High',
            'best_swell': 'SW 3-5 ft',
            'best_wind': 'NE',
            'best_season': 'November - April',
            'crowd_level': 'high',
            'has_parking': True,
            'has_showers': True,
            'has_rentals': True,
            'has_cafe': True,
            'rating': 4.2,
        },
        {
            'name': 'Hikkaduwa Main Reef',
            'slug': 'hikkaduwa-main-reef',
            'region': 'Hikkaduwa',
            'description': 'Classic reef break in front of Hikkaduwa town. Consistent waves during season with multiple takeoff zones.',
            'short_description': 'Classic Sri Lankan reef break',
            'latitude': 6.1412,
            'longitude': 80.0985,
            'wave_direction': 'left',
            'wave_type': 'reef',
            'wave_height_min': 0.8,
            'wave_height_max': 2.5,
            'skill_levels': ['intermediate', 'advanced'],
            'best_tide': 'Mid',
            'best_swell': 'SW 4-6 ft',
            'best_wind': 'NE',
            'best_season': 'November - March',
            'crowd_level': 'high',
            'has_reef': True,
            'has_parking': True,
            'has_rentals': True,
            'has_cafe': True,
            'rating': 4.4,
        },
        {
            'name': 'Hikkaduwa Beach Break',
            'slug': 'hikkaduwa-beach-break',
            'region': 'Hikkaduwa',
            'description': 'Sandy beach break south of the main reef, perfect for beginners and longboarders.',
            'short_description': 'Beginner-friendly beach break',
            'latitude': 6.1380,
            'longitude': 80.1005,
            'wave_direction': 'both',
            'wave_type': 'beach',
            'wave_height_min': 0.3,
            'wave_height_max': 1.5,
            'skill_levels': ['beginner'],
            'best_tide': 'All tides',
            'best_swell': 'SW 2-4 ft',
            'best_wind': 'NE',
            'best_season': 'November - April',
            'crowd_level': 'medium',
            'has_parking': True,
            'has_rentals': True,
            'has_cafe': True,
            'rating': 4.0,
        },
        {
            'name': 'Kabalana',
            'slug': 'kabalana',
            'region': 'Ahangama',
            'description': 'Famous A-frame reef break producing both lefts and rights. One of Sri Lanka\'s best waves for intermediate to advanced surfers.',
            'short_description': 'A-frame reef with lefts and rights',
            'latitude': 5.9680,
            'longitude': 80.3615,
            'wave_direction': 'both',
            'wave_type': 'reef',
            'wave_height_min': 1.0,
            'wave_height_max': 2.5,
            'skill_levels': ['intermediate', 'advanced'],
            'best_tide': 'Mid to High',
            'best_swell': 'SW 4-6 ft',
            'best_wind': 'NE',
            'best_season': 'November - April',
            'crowd_level': 'medium',
            'has_reef': True,
            'has_parking': True,
            'has_cafe': True,
            'rating': 4.7,
        },
        {
            'name': 'Hiriketiya Bay',
            'slug': 'hiriketiya-bay-spot',
            'region': 'Hiriketiya',
            'description': 'Beautiful horseshoe bay with consistent waves. Protected from wind, making it reliable when other spots are blown out.',
            'short_description': 'Scenic bay with consistent waves',
            'latitude': 5.9490,
            'longitude': 80.7155,
            'wave_direction': 'right',
            'wave_type': 'beach',
            'wave_height_min': 0.5,
            'wave_height_max': 2.0,
            'skill_levels': ['beginner', 'intermediate'],
            'best_tide': 'Mid',
            'best_swell': 'SW 3-5 ft',
            'best_wind': 'Any - protected bay',
            'best_season': 'November - April',
            'crowd_level': 'medium',
            'has_parking': True,
            'has_cafe': True,
            'has_rentals': True,
            'rating': 4.5,
        },
    ]

    region_map = {r.name_en: r for r in regions}
    created_spots = []

    for spot_data in spots_data:
        region_name = spot_data.pop('region')
        region = region_map.get(region_name)
        if not region:
            continue

        spot, _ = SurfSpot.objects.get_or_create(
            slug=spot_data['slug'],
            defaults={**spot_data, 'region': region}
        )
        created_spots.append(spot)

    print(f"Created {len(created_spots)} surf spots in Sri Lanka")
    return created_spots


def create_instructors(camps):
    """Create instructors for Sri Lanka camps"""
    instructors_data = [
        ('The Surfer Weligama', [
            {'name': 'Kasun Silva', 'experience_years': 12, 'languages': 'English, Sinhala, German', 'is_head_coach': True, 'certifications': 'ISA Level 2, Lifeguard'},
            {'name': 'Nuwan Fernando', 'experience_years': 8, 'languages': 'English, Sinhala', 'certifications': 'ISA Level 1'},
        ]),
        ('Solid Surf & Yoga House', [
            {'name': 'Chamara Perera', 'experience_years': 15, 'languages': 'English, Sinhala, French', 'is_head_coach': True, 'certifications': 'ISA Level 2'},
            {'name': 'Emma Wilson', 'experience_years': 6, 'languages': 'English, Spanish', 'certifications': 'ISA Level 1, Yoga RYT-200'},
        ]),
        ('Arugam Bay Surf Camp', [
            {'name': 'Lakmal Jayawardena', 'experience_years': 20, 'languages': 'English, Sinhala, Tamil', 'is_head_coach': True, 'certifications': 'ISA Level 3, Former National Champion'},
            {'name': 'Ravi Kumar', 'experience_years': 10, 'languages': 'English, Tamil', 'certifications': 'ISA Level 2'},
            {'name': 'Sarah Mitchell', 'experience_years': 7, 'languages': 'English, German', 'certifications': 'ISA Level 1'},
        ]),
        ('Dreamsea Sri Lanka', [
            {'name': 'Priya Mendis', 'experience_years': 9, 'languages': 'English, Sinhala, Russian', 'is_head_coach': True, 'certifications': 'ISA Level 2'},
        ]),
    ]

    camp_map = {c.name: c for c in camps}
    count = 0
    for camp_name, instructors in instructors_data:
        camp = camp_map.get(camp_name)
        if not camp:
            continue
        for instr in instructors:
            Instructor.objects.get_or_create(
                camp=camp, name=instr['name'],
                defaults={
                    'experience_years': instr.get('experience_years', 5),
                    'languages': instr.get('languages', 'English'),
                    'certifications': instr.get('certifications', ''),
                    'is_head_coach': instr.get('is_head_coach', False),
                    'bio': f"Professional surf instructor with {instr.get('experience_years', 5)} years of experience in Sri Lanka."
                }
            )
            count += 1

    print(f"Created {count} instructors for Sri Lanka camps")


def create_activities(camps):
    """Create activities for Sri Lanka camps"""
    activities_data = [
        ('Arugam Bay Surf Camp', [
            {'name': 'Йога', 'name_en': 'Sunrise Yoga', 'price': None, 'is_included': True},
            {'name': 'Сафари', 'name_en': 'Kumana Safari', 'price': 55},
            {'name': 'Китовое сафари', 'name_en': 'Whale Watching', 'price': 45},
        ]),
        ('Solid Surf & Yoga House', [
            {'name': 'Йога', 'name_en': 'Daily Yoga', 'price': None, 'is_included': True},
            {'name': 'Массаж', 'name_en': 'Ayurvedic Massage', 'price': 35},
            {'name': 'Храмы', 'name_en': 'Temple Tour Galle', 'price': 40},
        ]),
        ('The Salty Pelican', [
            {'name': 'Йога', 'name_en': 'Sunset Yoga', 'price': None, 'is_included': True},
            {'name': 'Снорклинг', 'name_en': 'Snorkeling Trip', 'price': 35},
        ]),
    ]

    camp_map = {c.name: c for c in camps}
    count = 0
    for camp_name, activities in activities_data:
        camp = camp_map.get(camp_name)
        if not camp:
            continue
        for act in activities:
            Activity.objects.get_or_create(
                camp=camp, name_en=act['name_en'],
                defaults={
                    'name': act['name'],
                    'price': act.get('price'),
                    'is_included': act.get('is_included', False),
                    'description': f"{act['name_en']} experience at {camp_name}"
                }
            )
            count += 1

    print(f"Created {count} activities for Sri Lanka camps")


def create_reviews(camps):
    """Create reviews for Sri Lanka camps"""
    import random

    reviews_templates = [
        {'author_name': 'Tom H.', 'author_country': 'UK', 'rating': 5, 'title': 'Life-changing experience!', 'text': 'Sri Lanka exceeded all my expectations. The waves, the food, the people - everything was perfect. Learned to surf in warm water with patient instructors. Already planning my return trip!', 'surf_level': 'beginner'},
        {'author_name': 'Julia S.', 'author_country': 'Germany', 'rating': 5, 'title': 'Best beginner waves ever', 'text': 'Weligama is THE place to learn surfing. Soft waves, sandy bottom, warm water - couldn\'t ask for better conditions. The instructors were incredibly patient and encouraging.', 'surf_level': 'beginner'},
        {'author_name': 'Marco B.', 'author_country': 'Italy', 'rating': 4, 'title': 'Great progression', 'text': 'Came as an intermediate and improved so much. Video analysis was really helpful. The food was amazing and the vibe was super relaxed. Would definitely recommend.', 'surf_level': 'intermediate'},
        {'author_name': 'Sophie L.', 'author_country': 'France', 'rating': 5, 'title': 'Paradise found', 'text': 'The combination of surfing and yoga was exactly what I needed. Beautiful accommodation, delicious Sri Lankan curries, and perfect waves every day. Pure magic!', 'surf_level': 'beginner'},
        {'author_name': 'David K.', 'author_country': 'Australia', 'rating': 5, 'title': 'World class waves', 'text': 'Arugam Bay lives up to the hype! Main Point is incredible - long, peeling right-handers with warm water. The surf camp was basic but comfortable, and the atmosphere was great.', 'surf_level': 'advanced'},
        {'author_name': 'Elena M.', 'author_country': 'Russia', 'rating': 4, 'title': 'Great value for money', 'text': 'Amazing surf trip for a budget-friendly price. Accommodation was simple but clean, instructors were experienced, and the waves were consistent. Sri Lanka is a must-visit for surfers!', 'surf_level': 'intermediate'},
        {'author_name': 'Jack W.', 'author_country': 'USA', 'rating': 5, 'title': 'Unforgettable surf trip', 'text': 'From complete beginner to catching green waves in one week. The warm Sri Lankan hospitality made the experience even better. Can\'t wait to come back!', 'surf_level': 'beginner'},
    ]

    count = 0
    for camp in camps:
        num_reviews = random.randint(3, 6)
        selected_reviews = random.sample(reviews_templates, min(num_reviews, len(reviews_templates)))

        for review in selected_reviews:
            Review.objects.get_or_create(
                camp=camp,
                author_name=review['author_name'],
                defaults={
                    'author_country': review['author_country'],
                    'rating': review['rating'],
                    'title': review['title'],
                    'text': review['text'],
                    'surf_level': review['surf_level'],
                    'is_verified': True,
                    'is_published': True,
                }
            )
            count += 1

    print(f"Created {count} reviews for Sri Lanka camps")


def main():
    print("Starting Sri Lanka data population...")
    print("-" * 50)

    sri_lanka, regions = create_sri_lanka()
    camps = create_surf_camps(regions)
    spots = create_surf_spots(regions)
    create_instructors(camps)
    create_activities(camps)
    create_reviews(camps)

    # Link spots to nearby camps
    for spot in spots:
        nearby_camps = SurfCamp.objects.filter(
            region=spot.region,
            is_active=True
        )
        spot.camps.set(nearby_camps)

    print("-" * 50)
    print("Done! Sri Lanka data populated successfully.")
    print(f"Total Sri Lanka camps: {SurfCamp.objects.filter(region__country__code='LKA').count()}")


if __name__ == '__main__':
    main()
