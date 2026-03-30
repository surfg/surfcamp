#!/usr/bin/env python
"""
Populate Thailand (Phuket) surf camps data
Run: python populate_thailand.py
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from camps.models import Country, Region, BoardType, Amenity, SurfCamp, Instructor, Activity, Review
from spots.models import SurfSpot


def create_thailand_phuket():
    """Create Thailand and Phuket regions"""
    thailand, _ = Country.objects.get_or_create(
        code='THA',
        defaults={
            'name': 'Таиланд',
            'name_en': 'Thailand',
            'description': 'Thailand offers excellent beginner-friendly surf conditions with warm waters year-round. Phuket and Khao Lak are the main surf destinations with consistent waves during monsoon season (May-October).'
        }
    )

    regions_data = [
        {'name': 'Ката Бич', 'name_en': 'Kata Beach', 'latitude': 7.8167, 'longitude': 98.2917,
         'description': 'The surfing mecca of Phuket with consistent waves for all skill levels'},
        {'name': 'Банг Тао', 'name_en': 'Bang Tao', 'latitude': 7.9750, 'longitude': 98.2833,
         'description': 'Long stretch of beach perfect for beginners with gentle waves'},
        {'name': 'Сурин', 'name_en': 'Surin', 'latitude': 7.9750, 'longitude': 98.2750,
         'description': 'Powerful waves and barrel opportunities for experienced surfers'},
        {'name': 'Патонг', 'name_en': 'Patong', 'latitude': 7.8889, 'longitude': 98.2961,
         'description': 'Popular tourist beach with beginner-friendly waves'},
        {'name': 'Камала', 'name_en': 'Kamala', 'latitude': 7.9533, 'longitude': 98.2817,
         'description': 'Quieter alternative with good waves for intermediate surfers'},
        {'name': 'Као Лак', 'name_en': 'Khao Lak', 'latitude': 8.6500, 'longitude': 98.2500,
         'description': 'Uncrowded beaches north of Phuket with consistent surf'},
    ]

    regions = []
    for r in regions_data:
        region, _ = Region.objects.get_or_create(
            country=thailand, name_en=r['name_en'],
            defaults=r
        )
        regions.append(region)

    print(f"Created Thailand with {len(regions)} regions")
    return thailand, regions


def create_surf_camps(regions):
    """Create Thailand surf camps with real data"""
    board_types = list(BoardType.objects.all())
    amenities = list(Amenity.objects.all())

    camps_data = [
        {
            'name': 'Talay Surf Camp',
            'slug': 'talay-surf-camp-phuket',
            'region': 'Kata Beach',
            'short_description': 'Premier surf school in Phuket offering comprehensive lessons for beginners',
            'description': '''Talay Surf Camp is widely recognized as the best surf camp in Thailand. Located at Kata Beach, we harness the beginner-friendly nature of Phuket's beach breaks and help novices get their feet wet in surfing.

Our 6-Day "Learn to Surf" Camp includes five days of professional instruction with all equipment provided. For those unsure about committing to a full week, we offer a 3-Day option featuring three hours of tuition plus a relaxing Thai massage to help you recover.

Choose from private beach hotel rooms for added comfort or budget-friendly hostel stays. All packages include equipment rental, theory sessions, and practical ocean time.''',
            'history': 'Established as one of Phuket\'s first dedicated surf schools, Talay has trained thousands of surfers.',
            'address': 'Kata Beach, Karon, Mueang Phuket District, Phuket 83100',
            'latitude': 7.8178,
            'longitude': 98.2985,
            'price_per_night': 65,
            'price_per_lesson': 40,
            'has_bed_breakfast': True,
            'bed_breakfast_price': 45,
            'skill_levels': ['beginner', 'intermediate'],
            'board_rental_available': True,
            'board_rental_price': 12,
            'has_pool': False,
            'has_restaurant': True,
            'has_yoga': True,
            'has_parties': False,
            'website': 'https://talaysurfschool.com',
            'email': 'info@talaysurfschool.com',
            'instagram': '@talaysurfschool',
            'rating': 4.9,
            'reviews_count': 245,
            'is_featured': True,
        },
        {
            'name': 'Saltwater Dreaming Surf School',
            'slug': 'saltwater-dreaming-phuket',
            'region': 'Bang Tao',
            'short_description': 'Established surf school since 2002 with expert instruction on Bang Tao Beach',
            'description': '''Saltwater Dreaming has been providing surf lessons and camps on Phuket's west coast since 2002. Located at Bang Tao Beach, considered the best beach in Phuket for learning to surf, we offer lessons in waist-deep water with gentle, easy-to-ride waves.

Our experienced instructors focus on building confidence and proper technique from day one. Small group sizes ensure personalized attention, while our beach location provides the perfect learning environment.

All equipment is included, and we offer photo/video packages to capture your surfing journey.''',
            'address': 'Bang Tao Beach, Thalang District, Phuket 83110',
            'latitude': 7.9756,
            'longitude': 98.2845,
            'price_per_night': 55,
            'price_per_lesson': 35,
            'has_bed_breakfast': True,
            'bed_breakfast_price': 40,
            'skill_levels': ['beginner'],
            'board_rental_available': True,
            'board_rental_price': 10,
            'has_pool': False,
            'has_restaurant': False,
            'has_yoga': False,
            'has_parties': False,
            'website': 'https://saltwater-dreaming.com',
            'email': 'info@saltwater-dreaming.com',
            'instagram': '@saltwaterdreaming',
            'rating': 4.7,
            'reviews_count': 312,
            'is_featured': False,
        },
        {
            'name': 'Phuket Surf House',
            'slug': 'phuket-surf-house',
            'region': 'Kata Beach',
            'short_description': 'Boutique surf lodge with pool and modern amenities near Kata Beach',
            'description': '''Phuket Surf House combines comfortable accommodation with quality surf instruction. Our boutique lodge features a refreshing pool, modern rooms with air conditioning, and a short walk to Kata Beach's best breaks.

We cater to surfers of all levels, from complete beginners to intermediates looking to progress. Daily surf sessions are complemented by yoga classes and video analysis to accelerate your learning.

The common area and rooftop terrace are perfect for socializing with fellow surf enthusiasts and watching stunning Andaman Sea sunsets.''',
            'address': 'Kata Beach Road, Karon, Phuket 83100',
            'latitude': 7.8195,
            'longitude': 98.2968,
            'price_per_night': 75,
            'price_per_lesson': 45,
            'has_bed_breakfast': True,
            'bed_breakfast_price': 55,
            'skill_levels': ['beginner', 'intermediate'],
            'board_rental_available': True,
            'board_rental_price': 15,
            'has_pool': True,
            'has_restaurant': True,
            'has_yoga': True,
            'has_parties': True,
            'instagram': '@phuketsurfhouse',
            'rating': 4.6,
            'reviews_count': 89,
            'is_featured': True,
        },
        {
            'name': 'Surin Beach Surf Academy',
            'slug': 'surin-beach-surf-academy',
            'region': 'Surin',
            'short_description': 'Advanced coaching for intermediate surfers seeking barrel waves',
            'description': '''Surin Beach Surf Academy is designed for surfers who want to take their skills to the next level. Located at one of Phuket's most powerful beach breaks, we specialize in intermediate to advanced coaching.

Our certified instructors focus on reading waves, positioning, and maneuvers in more challenging conditions. The rocky headlands at Surin create excellent barrel opportunities during the peak season.

We provide high-performance equipment and offer private coaching sessions for accelerated progression.''',
            'address': 'Surin Beach, Choeng Thale, Phuket 83110',
            'latitude': 7.9765,
            'longitude': 98.2742,
            'price_per_night': 85,
            'price_per_lesson': 60,
            'skill_levels': ['intermediate', 'advanced'],
            'board_rental_available': True,
            'board_rental_price': 20,
            'has_pool': True,
            'has_restaurant': True,
            'has_yoga': False,
            'has_parties': False,
            'website': 'https://surinbeachsurf.com',
            'rating': 4.8,
            'reviews_count': 56,
            'is_featured': False,
        },
        {
            'name': 'Khao Lak Surf Discovery',
            'slug': 'khao-lak-surf-discovery',
            'region': 'Khao Lak',
            'short_description': 'Escape the crowds at pristine Khao Lak beaches north of Phuket',
            'description': '''Khao Lak Surf Discovery offers a quieter alternative to busy Phuket beaches. Located 80km north, our camp provides uncrowded waves on pristine sandy beaches.

The area is perfect for those seeking a more relaxed atmosphere while learning to surf. Long sandy beaches and consistent waves make it ideal for beginners and intermediate surfers alike.

Combine your surf trip with visits to stunning national parks and waterfalls. We offer transportation from Phuket airport and all-inclusive packages with accommodation, lessons, and equipment.''',
            'address': 'Khao Lak Beach, Takua Pa, Phang Nga 82190',
            'latitude': 8.6512,
            'longitude': 98.2456,
            'price_per_night': 50,
            'price_per_lesson': 35,
            'has_bed_breakfast': True,
            'bed_breakfast_price': 35,
            'skill_levels': ['beginner', 'intermediate'],
            'board_rental_available': True,
            'board_rental_price': 10,
            'has_pool': False,
            'has_restaurant': True,
            'has_yoga': True,
            'has_parties': False,
            'instagram': '@khaolaksurf',
            'rating': 4.5,
            'reviews_count': 78,
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

    print(f"Created {len(created_camps)} surf camps in Thailand")
    return created_camps


def create_surf_spots(regions):
    """Create Thailand surf spots"""
    spots_data = [
        {
            'name': 'Kata Beach Main',
            'slug': 'kata-beach-main',
            'region': 'Kata Beach',
            'description': 'The main surf spot at Kata Beach with consistent swell during monsoon season. Sandy bottom and multiple peaks make it perfect for all levels.',
            'short_description': 'Consistent beach break perfect for learning',
            'latitude': 7.8172,
            'longitude': 98.2982,
            'wave_direction': 'both',
            'wave_type': 'beach',
            'wave_height_min': 0.5,
            'wave_height_max': 2.0,
            'skill_levels': ['beginner', 'intermediate'],
            'best_tide': 'Mid to High',
            'best_swell': 'SW 3-6 ft',
            'best_wind': 'E offshore',
            'best_season': 'May - October',
            'crowd_level': 'medium',
            'has_parking': True,
            'has_showers': True,
            'has_rentals': True,
            'has_cafe': True,
            'rating': 4.3,
        },
        {
            'name': 'Kata Noi',
            'slug': 'kata-noi',
            'region': 'Kata Beach',
            'description': 'Smaller bay south of Kata Beach with more powerful waves. Better for intermediate surfers looking for more challenge.',
            'short_description': 'More powerful waves in a scenic cove',
            'latitude': 7.8089,
            'longitude': 98.2981,
            'wave_direction': 'right',
            'wave_type': 'beach',
            'wave_height_min': 0.8,
            'wave_height_max': 2.5,
            'skill_levels': ['intermediate', 'advanced'],
            'best_tide': 'Mid',
            'best_swell': 'SW 4-8 ft',
            'best_wind': 'E',
            'best_season': 'May - September',
            'crowd_level': 'low',
            'has_rocks': True,
            'has_parking': True,
            'has_cafe': True,
            'rating': 4.5,
        },
        {
            'name': 'Bang Tao Beach',
            'slug': 'bang-tao-beach',
            'region': 'Bang Tao',
            'description': '6km long beach with gentle waves perfect for beginners. The southern end is protected by a headland creating ideal learning conditions.',
            'short_description': 'Long beach ideal for beginners',
            'latitude': 7.9756,
            'longitude': 98.2845,
            'wave_direction': 'both',
            'wave_type': 'beach',
            'wave_height_min': 0.3,
            'wave_height_max': 1.5,
            'skill_levels': ['beginner'],
            'best_tide': 'All tides',
            'best_swell': 'SW 2-4 ft',
            'best_wind': 'E',
            'best_season': 'May - October',
            'crowd_level': 'low',
            'has_parking': True,
            'has_rentals': True,
            'has_cafe': True,
            'rating': 4.0,
        },
        {
            'name': 'Surin Beach',
            'slug': 'surin-beach-spot',
            'region': 'Surin',
            'description': 'Powerful beach break with waves up to 2m during peak season. Rocky headlands create barrel opportunities. For experienced surfers only.',
            'short_description': 'Powerful waves for experienced surfers',
            'latitude': 7.9765,
            'longitude': 98.2742,
            'wave_direction': 'left',
            'wave_type': 'beach',
            'wave_height_min': 1.0,
            'wave_height_max': 2.5,
            'skill_levels': ['intermediate', 'advanced'],
            'best_tide': 'Mid to High',
            'best_swell': 'SW 5-8 ft',
            'best_wind': 'E-NE',
            'best_season': 'June - September',
            'crowd_level': 'medium',
            'has_rocks': True,
            'has_currents': True,
            'has_parking': True,
            'has_cafe': True,
            'rating': 4.4,
        },
        {
            'name': 'Kamala Beach',
            'slug': 'kamala-beach',
            'region': 'Kamala',
            'description': 'Quieter beach between Patong and Surin with consistent waves for intermediates. Less crowded than other Phuket spots.',
            'short_description': 'Uncrowded intermediate spot',
            'latitude': 7.9533,
            'longitude': 98.2817,
            'wave_direction': 'both',
            'wave_type': 'beach',
            'wave_height_min': 0.5,
            'wave_height_max': 2.0,
            'skill_levels': ['intermediate'],
            'best_tide': 'Mid',
            'best_swell': 'SW 4-6 ft',
            'best_wind': 'E',
            'best_season': 'May - October',
            'crowd_level': 'low',
            'has_parking': True,
            'has_cafe': True,
            'rating': 4.2,
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

    print(f"Created {len(created_spots)} surf spots in Thailand")
    return created_spots


def create_instructors(camps):
    """Create instructors for Thailand camps"""
    instructors_data = [
        ('Talay Surf Camp', [
            {'name': 'Chai Sombat', 'experience_years': 12, 'languages': 'English, Thai, German', 'is_head_coach': True, 'certifications': 'ISA Level 2, Lifeguard'},
            {'name': 'Anna Schmidt', 'experience_years': 8, 'languages': 'English, German, Thai', 'certifications': 'ISA Level 1'},
            {'name': 'Mike Thompson', 'experience_years': 6, 'languages': 'English, Thai', 'certifications': 'ISA Level 1'},
        ]),
        ('Phuket Surf House', [
            {'name': 'Somchai Prasert', 'experience_years': 15, 'languages': 'English, Thai, Russian', 'is_head_coach': True, 'certifications': 'ISA Level 2'},
            {'name': 'Lisa Chen', 'experience_years': 5, 'languages': 'English, Mandarin', 'certifications': 'ISA Level 1'},
        ]),
        ('Surin Beach Surf Academy', [
            {'name': 'Tom Briggs', 'experience_years': 18, 'languages': 'English, Thai', 'is_head_coach': True, 'certifications': 'Former Pro Surfer, ISA Level 3'},
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
                    'bio': f"Professional surf instructor with {instr.get('experience_years', 5)} years of experience in Thailand."
                }
            )
            count += 1

    print(f"Created {count} instructors for Thailand camps")


def create_reviews(camps):
    """Create reviews for Thailand camps"""
    import random

    reviews_templates = [
        {'author_name': 'James K.', 'author_country': 'UK', 'rating': 5, 'title': 'Perfect for beginners!', 'text': 'Amazing experience learning to surf in Phuket! The instructors were patient and professional. Caught my first waves on day one. The warm water made learning so much easier than back home. Highly recommend!', 'surf_level': 'beginner'},
        {'author_name': 'Sarah M.', 'author_country': 'Australia', 'rating': 5, 'title': 'Great value in Thailand', 'text': 'You can\'t beat the value for money here. Quality instruction, beautiful beaches, and delicious Thai food after surfing. The instructors knew exactly when and where to find the best waves.', 'surf_level': 'beginner'},
        {'author_name': 'Hans B.', 'author_country': 'Germany', 'rating': 4, 'title': 'Good progression camp', 'text': 'Came to improve my intermediate skills and made great progress. Video analysis was particularly helpful. Only minor issue was the crowds at peak times, but instructors knew quieter spots.', 'surf_level': 'intermediate'},
        {'author_name': 'Maria L.', 'author_country': 'Spain', 'rating': 5, 'title': 'Best holiday ever', 'text': 'Combined surf camp with Thai culture and food - perfect! The staff was so friendly and helpful. Beach location was stunning. Will definitely be back next year.', 'surf_level': 'beginner'},
        {'author_name': 'Alex P.', 'author_country': 'Russia', 'rating': 4, 'title': 'Solid surf experience', 'text': 'Professional setup with good equipment. Learned proper technique and ocean safety. Accommodation was comfortable and close to the beach. Would recommend for anyone wanting to learn.', 'surf_level': 'beginner'},
        {'author_name': 'Yuki T.', 'author_country': 'Japan', 'rating': 5, 'title': 'Excellent instructors', 'text': 'The patience and skill of the instructors made all the difference. As a complete beginner, I was nervous, but they made me feel confident in the water. Great photos and videos to remember the trip!', 'surf_level': 'beginner'},
    ]

    count = 0
    for camp in camps:
        num_reviews = random.randint(3, 5)
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

    print(f"Created {count} reviews for Thailand camps")


def main():
    print("Starting Thailand (Phuket) data population...")
    print("-" * 50)

    thailand, regions = create_thailand_phuket()
    camps = create_surf_camps(regions)
    spots = create_surf_spots(regions)
    create_instructors(camps)
    create_reviews(camps)

    # Link spots to nearby camps
    for spot in spots:
        nearby_camps = SurfCamp.objects.filter(
            region=spot.region,
            is_active=True
        )
        spot.camps.set(nearby_camps)

    print("-" * 50)
    print("Done! Thailand data populated successfully.")
    print(f"Total Thailand camps: {SurfCamp.objects.filter(region__country__code='THA').count()}")


if __name__ == '__main__':
    main()
