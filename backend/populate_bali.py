#!/usr/bin/env python
"""
Скрипт для заполнения данных по Бали
Запуск: python populate_bali.py
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from camps.models import Country, Region, BoardType, Amenity, SurfCamp, Instructor, Activity, Review
from spots.models import SurfSpot


def create_board_types():
    """Создаём типы досок"""
    board_types = [
        {'name': 'Софттоп', 'name_en': 'Soft Top', 'description': 'Мягкая доска для начинающих'},
        {'name': 'Лонгборд', 'name_en': 'Longboard', 'description': 'Длинная доска 9+ футов'},
        {'name': 'Мидленгс', 'name_en': 'Mid Length', 'description': 'Средняя доска 7-8 футов'},
        {'name': 'Шортборд', 'name_en': 'Shortboard', 'description': 'Короткая доска для продвинутых'},
        {'name': 'Фанборд', 'name_en': 'Funboard', 'description': 'Универсальная доска'},
    ]
    created = []
    for bt in board_types:
        obj, _ = BoardType.objects.get_or_create(name_en=bt['name_en'], defaults=bt)
        created.append(obj)
    print(f"Created {len(created)} board types")
    return created


def create_amenities():
    """Создаём удобства"""
    amenities_data = [
        # Проживание
        {'name': 'Кондиционер', 'name_en': 'Air Conditioning', 'category': 'accommodation', 'icon': 'snowflake'},
        {'name': 'Wi-Fi', 'name_en': 'Free WiFi', 'category': 'accommodation', 'icon': 'wifi'},
        {'name': 'Приватная комната', 'name_en': 'Private Room', 'category': 'accommodation', 'icon': 'bed'},
        {'name': 'Общая комната', 'name_en': 'Shared Room', 'category': 'accommodation', 'icon': 'users'},
        {'name': 'Горячая вода', 'name_en': 'Hot Water', 'category': 'accommodation', 'icon': 'droplet'},
        # Питание
        {'name': 'Завтрак включён', 'name_en': 'Breakfast Included', 'category': 'food', 'icon': 'coffee'},
        {'name': 'Полный пансион', 'name_en': 'Full Board', 'category': 'food', 'icon': 'utensils'},
        {'name': 'Веган меню', 'name_en': 'Vegan Options', 'category': 'food', 'icon': 'leaf'},
        # Серфинг
        {'name': 'Доски включены', 'name_en': 'Boards Included', 'category': 'surf', 'icon': 'board'},
        {'name': 'Видеоанализ', 'name_en': 'Video Analysis', 'category': 'surf', 'icon': 'video'},
        {'name': 'Фото с сессий', 'name_en': 'Photo Package', 'category': 'surf', 'icon': 'camera'},
        # Активности
        {'name': 'Йога', 'name_en': 'Yoga Classes', 'category': 'activities', 'icon': 'yoga'},
        {'name': 'Фитнес', 'name_en': 'Fitness Center', 'category': 'activities', 'icon': 'dumbbell'},
        {'name': 'Скейтпарк', 'name_en': 'Skate Park', 'category': 'activities', 'icon': 'skateboard'},
        {'name': 'Экскурсии', 'name_en': 'Excursions', 'category': 'activities', 'icon': 'map'},
        # Сервисы
        {'name': 'Трансфер', 'name_en': 'Airport Transfer', 'category': 'services', 'icon': 'car'},
        {'name': 'Прачечная', 'name_en': 'Laundry Service', 'category': 'services', 'icon': 'washing'},
        {'name': 'Прокат байков', 'name_en': 'Motorbike Rental', 'category': 'services', 'icon': 'motorcycle'},
    ]
    created = []
    for a in amenities_data:
        obj, _ = Amenity.objects.get_or_create(name_en=a['name_en'], defaults=a)
        created.append(obj)
    print(f"Created {len(created)} amenities")
    return created


def create_indonesia_bali():
    """Создаём Индонезию и регионы Бали"""
    indonesia, _ = Country.objects.get_or_create(
        code='IDN',
        defaults={
            'name': 'Индонезия',
            'name_en': 'Indonesia',
            'description': 'Индонезия — рай для серферов с тысячами островов и идеальными волнами круглый год.'
        }
    )

    regions_data = [
        {'name': 'Кута', 'name_en': 'Kuta', 'latitude': -8.7180, 'longitude': 115.1686,
         'description': 'Популярное место для начинающих с пологими волнами'},
        {'name': 'Семиньяк', 'name_en': 'Seminyak', 'latitude': -8.6913, 'longitude': 115.1571,
         'description': 'Стильный район с хорошими волнами и ресторанами'},
        {'name': 'Чангу', 'name_en': 'Canggu', 'latitude': -8.6478, 'longitude': 115.1385,
         'description': 'Хипстерский район с разнообразными споами для всех уровней'},
        {'name': 'Улувату', 'name_en': 'Uluwatu', 'latitude': -8.8291, 'longitude': 115.0849,
         'description': 'Легендарные рифовые волны для продвинутых серферов'},
        {'name': 'Паданг Паданг', 'name_en': 'Padang Padang', 'latitude': -8.8149, 'longitude': 115.1009,
         'description': 'Известный спот с мощными трубами'},
        {'name': 'Медеви', 'name_en': 'Medewi', 'latitude': -8.4044, 'longitude': 114.8258,
         'description': 'Длинные левые волны на западе Бали'},
    ]

    regions = []
    for r in regions_data:
        region, _ = Region.objects.get_or_create(
            country=indonesia, name_en=r['name_en'],
            defaults=r
        )
        regions.append(region)

    print(f"Created Indonesia with {len(regions)} regions")
    return indonesia, regions


def create_surf_camps(regions):
    """Создаём серф-кемпы"""
    board_types = list(BoardType.objects.all())
    amenities = list(Amenity.objects.all())

    camps_data = [
        {
            'name': 'Endless Summer Surf Camp',
            'slug': 'endless-summer-bali',
            'region': 'Canggu',
            'short_description': 'Premium surf camp с бассейном и йогой в сердце Чангу',
            'description': '''Endless Summer Surf Camp — это премиальный серф-кемп, расположенный в самом сердце Чангу. Мы предлагаем комплексный опыт серфинга, включающий ежедневные уроки с профессиональными инструкторами, видеоанализ, йога-сессии и комфортное проживание.

Наш кемп идеально подходит как для начинающих, так и для прогрессирующих серферов. Мы работаем на лучших спотах региона, подбирая условия под ваш уровень.

Территория кемпа включает бассейн, ресторан с здоровой кухней, зону отдыха и скейт-рампу.''',
            'history': 'Основан в 2015 году группой австралийских серферов, влюбившихся в Бали.',
            'address': 'Jl. Pantai Batu Bolong No. 88, Canggu, Bali',
            'latitude': -8.6512,
            'longitude': 115.1324,
            'price_per_night': 89,
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
            'website': 'https://endlesssummerbali.com',
            'email': 'info@endlesssummerbali.com',
            'instagram': '@endlesssummerbali',
            'rating': 4.8,
            'reviews_count': 127,
            'is_featured': True,
        },
        {
            'name': 'Wave House Bali',
            'slug': 'wave-house-bali',
            'region': 'Canggu',
            'short_description': 'Уютный серф-хаус для прогрессирующих серферов',
            'description': '''Wave House Bali — это уютный бутик-кемп для тех, кто хочет серьёзно прогрессировать в серфинге. Маленькие группы (max 4 человека), индивидуальный подход и фокус на технике.

Мы специализируемся на intermediate и advanced серферах, помогая преодолеть плато и выйти на новый уровень. Видеоанализ каждой сессии входит в стоимость.''',
            'address': 'Jl. Pantai Berawa No. 42, Canggu, Bali',
            'latitude': -8.6578,
            'longitude': 115.1402,
            'price_per_night': 75,
            'price_per_lesson': 55,
            'skill_levels': ['intermediate', 'advanced'],
            'board_rental_available': True,
            'board_rental_price': 20,
            'has_pool': False,
            'has_restaurant': True,
            'has_yoga': True,
            'has_parties': False,
            'instagram': '@wavehousebali',
            'rating': 4.9,
            'reviews_count': 68,
            'is_featured': True,
        },
        {
            'name': 'Kuta Beach Surf School',
            'slug': 'kuta-beach-surf-school',
            'region': 'Kuta',
            'short_description': 'Идеальное место для первых шагов в серфинге',
            'description': '''Kuta Beach Surf School — лучший выбор для тех, кто только начинает свой путь в серфинге. Расположены прямо на пляже Кута с идеальными волнами для обучения.

Опытные русскоговорящие инструкторы, софтборды для безопасного обучения, и гарантия — вы встанете на доску на первом же уроке!''',
            'address': 'Jl. Pantai Kuta, Kuta, Bali',
            'latitude': -8.7185,
            'longitude': 115.1690,
            'price_per_night': 45,
            'price_per_lesson': 35,
            'has_bed_breakfast': True,
            'bed_breakfast_price': 30,
            'skill_levels': ['beginner'],
            'board_rental_available': True,
            'board_rental_price': 10,
            'has_pool': False,
            'has_restaurant': False,
            'has_yoga': False,
            'has_parties': True,
            'rating': 4.5,
            'reviews_count': 234,
            'is_featured': False,
        },
        {
            'name': 'Uluwatu Surf Villas',
            'slug': 'uluwatu-surf-villas',
            'region': 'Uluwatu',
            'short_description': 'Люксовые виллы с видом на легендарные волны Улувату',
            'description': '''Uluwatu Surf Villas — это премиум-опыт для серферов, которые хотят кататься на лучших волнах Бали в комфорте. Частные виллы с бассейнами, вид на океан, личный серф-гид.

Мы организуем сессии на всех спотах полуострова Букит: Улувату, Паданг Паданг, Бингин, Дримлэнд. Подходит для advanced серферов.''',
            'address': 'Jl. Labuan Sait, Pecatu, Uluwatu, Bali',
            'latitude': -8.8156,
            'longitude': 115.0892,
            'price_per_night': 180,
            'price_per_lesson': 80,
            'skill_levels': ['intermediate', 'advanced'],
            'board_rental_available': True,
            'board_rental_price': 25,
            'has_pool': True,
            'has_restaurant': True,
            'has_yoga': True,
            'has_parties': False,
            'website': 'https://uluwatusurfvillas.com',
            'rating': 4.95,
            'reviews_count': 45,
            'is_featured': True,
        },
        {
            'name': 'Seminyak Surf Lodge',
            'slug': 'seminyak-surf-lodge',
            'region': 'Seminyak',
            'short_description': 'Стильный лодж в центре Семиньяка с серф-программой',
            'description': '''Seminyak Surf Lodge сочетает городской комфорт и серф-лайфстайл. Расположены в 5 минутах от пляжа, в окружении лучших ресторанов и баров Семиньяка.

Утром — серфинг на Double Six Beach, вечером — закаты в beach club. Идеально для тех, кто хочет совместить серфинг с nightlife.''',
            'address': 'Jl. Double Six No. 66, Seminyak, Bali',
            'latitude': -8.6920,
            'longitude': 115.1578,
            'price_per_night': 95,
            'price_per_lesson': 50,
            'has_bed_breakfast': True,
            'bed_breakfast_price': 65,
            'skill_levels': ['beginner', 'intermediate'],
            'board_rental_available': True,
            'board_rental_price': 15,
            'has_pool': True,
            'has_restaurant': True,
            'has_yoga': False,
            'has_parties': True,
            'instagram': '@seminyaksurflodge',
            'rating': 4.6,
            'reviews_count': 89,
            'is_featured': False,
        },
        {
            'name': 'Medewi Longboard Paradise',
            'slug': 'medewi-longboard-paradise',
            'region': 'Medewi',
            'short_description': 'Тихий рай для лонгбордистов на западе Бали',
            'description': '''Medewi Longboard Paradise — это escape от туристического Бали. Расположены в тихой деревне у знаменитого левого поинт-брейка Медеви.

Идеальное место для лонгбординга и ностальжик-серфинга. Длинные волны, мало народу, аутентичная атмосфера старого Бали. Подходит для intermediate+ лонгбордистов.''',
            'address': 'Medewi Beach, Pekutatan, West Bali',
            'latitude': -8.4048,
            'longitude': 114.8262,
            'price_per_night': 55,
            'price_per_lesson': 40,
            'has_bed_breakfast': True,
            'bed_breakfast_price': 40,
            'skill_levels': ['intermediate', 'advanced'],
            'board_rental_available': True,
            'board_rental_price': 12,
            'has_pool': False,
            'has_restaurant': True,
            'has_yoga': True,
            'has_parties': False,
            'rating': 4.7,
            'reviews_count': 52,
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
        camp.amenities.add(*amenities[:8])  # Add first 8 amenities

        created_camps.append(camp)

    print(f"Created {len(created_camps)} surf camps")
    return created_camps


def create_surf_spots(regions):
    """Создаём серф-споты"""
    spots_data = [
        {
            'name': 'Batu Bolong',
            'slug': 'batu-bolong',
            'region': 'Canggu',
            'description': 'Самый популярный спот Чангу. Мягкие волны, песчаное дно, идеально для обучения и лонгбординга.',
            'short_description': 'Идеальный спот для начинающих и лонгбордистов',
            'latitude': -8.6556,
            'longitude': 115.1328,
            'wave_direction': 'both',
            'wave_type': 'beach',
            'wave_height_min': 0.5,
            'wave_height_max': 2.0,
            'skill_levels': ['beginner', 'intermediate'],
            'best_tide': 'Mid to High',
            'best_swell': 'SW 3-6 ft',
            'best_wind': 'SE offshore',
            'best_season': 'April - October',
            'crowd_level': 'high',
            'has_rocks': False,
            'has_parking': True,
            'has_showers': True,
            'has_rentals': True,
            'has_cafe': True,
            'rating': 4.2,
        },
        {
            'name': 'Echo Beach',
            'slug': 'echo-beach',
            'region': 'Canggu',
            'description': 'Мощный бич-брейк с быстрыми волнами. Популярен среди локалов и прогрессирующих серферов.',
            'short_description': 'Мощные волны для intermediate серферов',
            'latitude': -8.6532,
            'longitude': 115.1254,
            'wave_direction': 'left',
            'wave_type': 'beach',
            'wave_height_min': 1.0,
            'wave_height_max': 3.0,
            'skill_levels': ['intermediate', 'advanced'],
            'best_tide': 'Mid',
            'best_swell': 'SW 4-8 ft',
            'best_wind': 'SE',
            'best_season': 'May - September',
            'crowd_level': 'high',
            'has_currents': True,
            'has_parking': True,
            'has_cafe': True,
            'rating': 4.5,
        },
        {
            'name': 'Uluwatu',
            'slug': 'uluwatu-main',
            'region': 'Uluwatu',
            'description': 'Легендарный рифовый спот. Длинные левые волны до 300 метров. Только для опытных серферов.',
            'short_description': 'Легендарный спот — длинные левые волны',
            'latitude': -8.8294,
            'longitude': 115.0847,
            'wave_direction': 'left',
            'wave_type': 'reef',
            'wave_height_min': 2.0,
            'wave_height_max': 5.0,
            'skill_levels': ['advanced'],
            'best_tide': 'Mid',
            'best_swell': 'S-SW 6-12 ft',
            'best_wind': 'E-SE',
            'best_season': 'May - October',
            'crowd_level': 'very_high',
            'has_reef': True,
            'has_currents': True,
            'has_parking': True,
            'has_cafe': True,
            'rating': 4.9,
        },
        {
            'name': 'Padang Padang',
            'slug': 'padang-padang',
            'region': 'Padang Padang',
            'description': 'Знаменитый баррел-спот, где проходят соревнования WSL. Короткие мощные левые трубы.',
            'short_description': 'Мировой класс баррелов',
            'latitude': -8.8146,
            'longitude': 115.1012,
            'wave_direction': 'left',
            'wave_type': 'reef',
            'wave_height_min': 1.5,
            'wave_height_max': 4.0,
            'skill_levels': ['advanced'],
            'best_tide': 'Low to Mid',
            'best_swell': 'SW 5-10 ft',
            'best_wind': 'E',
            'best_season': 'June - September',
            'crowd_level': 'very_high',
            'has_reef': True,
            'has_rocks': True,
            'has_parking': True,
            'has_cafe': True,
            'has_lifeguard': True,
            'rating': 4.8,
        },
        {
            'name': 'Kuta Beach',
            'slug': 'kuta-beach',
            'region': 'Kuta',
            'description': 'Классический бич-брейк для начинающих. Мягкие волны, песчаное дно, множество школ.',
            'short_description': 'Лучшее место для первого урока',
            'latitude': -8.7188,
            'longitude': 115.1687,
            'wave_direction': 'both',
            'wave_type': 'beach',
            'wave_height_min': 0.3,
            'wave_height_max': 1.5,
            'skill_levels': ['beginner'],
            'best_tide': 'Mid to High',
            'best_swell': 'SW 2-5 ft',
            'best_wind': 'E',
            'best_season': 'Year round',
            'crowd_level': 'very_high',
            'has_parking': True,
            'has_showers': True,
            'has_rentals': True,
            'has_cafe': True,
            'has_lifeguard': True,
            'rating': 3.8,
        },
        {
            'name': 'Medewi Point',
            'slug': 'medewi-point',
            'region': 'Medewi',
            'description': 'Длинный левый поинт-брейк. Волны до 200 метров, идеально для лонгбординга.',
            'short_description': 'Длинные левые волны для лонгбордистов',
            'latitude': -8.4046,
            'longitude': 114.8260,
            'wave_direction': 'left',
            'wave_type': 'point',
            'wave_height_min': 0.5,
            'wave_height_max': 2.5,
            'skill_levels': ['intermediate', 'advanced'],
            'best_tide': 'Mid to High',
            'best_swell': 'SW 3-6 ft',
            'best_wind': 'E',
            'best_season': 'April - October',
            'crowd_level': 'low',
            'has_rocks': True,
            'has_parking': True,
            'has_cafe': True,
            'rating': 4.6,
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

    print(f"Created {len(created_spots)} surf spots")
    return created_spots


def create_instructors(camps):
    """Создаём инструкторов"""
    instructors_data = [
        ('Endless Summer Surf Camp', [
            {'name': 'Made Surya', 'experience_years': 15, 'languages': 'English, Indonesian, Russian', 'is_head_coach': True, 'certifications': 'ISA Level 2, Lifeguard'},
            {'name': 'Ketut Wira', 'experience_years': 10, 'languages': 'English, Indonesian', 'certifications': 'ISA Level 1'},
            {'name': 'Alex Johnson', 'experience_years': 8, 'languages': 'English, Spanish', 'certifications': 'ISA Level 2'},
        ]),
        ('Wave House Bali', [
            {'name': 'Putu Dharma', 'experience_years': 20, 'languages': 'English, Indonesian, Japanese', 'is_head_coach': True, 'certifications': 'ISA Level 3, Former Pro'},
            {'name': 'Sarah Miller', 'experience_years': 7, 'languages': 'English, French', 'certifications': 'ISA Level 2'},
        ]),
        ('Uluwatu Surf Villas', [
            {'name': 'Wayan Sukma', 'experience_years': 25, 'languages': 'English, Indonesian', 'is_head_coach': True, 'certifications': 'Pro Surfer, ISA Level 3'},
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
                    'bio': f"Professional surf instructor with {instr.get('experience_years', 5)} years of experience."
                }
            )
            count += 1

    print(f"Created {count} instructors")


def create_activities(camps):
    """Создаём активности"""
    activities_data = [
        ('Endless Summer Surf Camp', [
            {'name': 'Йога', 'name_en': 'Morning Yoga', 'price': None, 'is_included': True},
            {'name': 'Видеоанализ', 'name_en': 'Video Analysis', 'price': None, 'is_included': True},
            {'name': 'Снорклинг тур', 'name_en': 'Snorkeling Trip', 'price': 45},
            {'name': 'Водопады тур', 'name_en': 'Waterfall Tour', 'price': 55},
        ]),
        ('Uluwatu Surf Villas', [
            {'name': 'Массаж', 'name_en': 'Balinese Massage', 'price': 35},
            {'name': 'Кулинарный класс', 'name_en': 'Cooking Class', 'price': 40},
            {'name': 'Храмы тур', 'name_en': 'Temple Tour', 'price': 60},
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

    print(f"Created {count} activities")


def create_reviews(camps):
    """Создаём отзывы"""
    import random

    reviews_templates = [
        {'author_name': 'Mike S.', 'author_country': 'USA', 'rating': 5, 'title': 'Best surf camp ever!', 'text': 'Amazing experience! The instructors were super professional and patient. I went from zero to catching green waves in just 5 days. The accommodation was comfortable and the food was delicious. Highly recommend!', 'surf_level': 'beginner'},
        {'author_name': 'Emma L.', 'author_country': 'UK', 'rating': 5, 'title': 'Perfect for progression', 'text': 'Came here as an intermediate surfer looking to improve. The video analysis sessions were incredibly helpful. Made huge progress in my technique. Will definitely come back!', 'surf_level': 'intermediate'},
        {'author_name': 'Lars H.', 'author_country': 'Germany', 'rating': 4, 'title': 'Great vibes, good waves', 'text': 'Really enjoyed my stay. The staff was friendly, the location perfect. Only minor issue was the crowded lineup on weekends. Otherwise excellent!', 'surf_level': 'intermediate'},
        {'author_name': 'Sophie M.', 'author_country': 'France', 'rating': 5, 'title': 'Dream vacation!', 'text': 'This place exceeded all my expectations. Beautiful villa, amazing food, and perfect waves every day. The surf guides knew exactly where to take us based on conditions.', 'surf_level': 'advanced'},
        {'author_name': 'Dmitry K.', 'author_country': 'Russia', 'rating': 5, 'title': 'Отличный кемп!', 'text': 'Провёл здесь 2 недели и это были лучшие каникулы в моей жизни. Научился серфить с нуля, обзавёлся новыми друзьями. Организация на высшем уровне.', 'surf_level': 'beginner'},
        {'author_name': 'Anna P.', 'author_country': 'Australia', 'rating': 4, 'title': 'Good value for money', 'text': 'Solid surf camp with knowledgeable instructors. The equipment was in good condition. Would have liked more variety in the food menu, but overall a great experience.', 'surf_level': 'intermediate'},
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

    print(f"Created {count} reviews")


def main():
    print("Starting Bali data population...")
    print("-" * 50)

    create_board_types()
    create_amenities()
    indonesia, regions = create_indonesia_bali()
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
    print("Done! Data populated successfully.")
    print(f"Total camps: {SurfCamp.objects.count()}")
    print(f"Total spots: {SurfSpot.objects.count()}")


if __name__ == '__main__':
    main()
