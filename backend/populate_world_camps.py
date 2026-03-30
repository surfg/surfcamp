"""
Comprehensive script to populate 100+ realistic surf camps from around the world.
Run with: python manage.py shell < populate_world_camps.py
"""
import os
import sys
import django
import random

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from camps.models import Country, Region, SurfCamp, BoardType, Amenity, Instructor, Activity, Review
from decimal import Decimal

# Clear existing data
print("Clearing existing camps...")
SurfCamp.objects.all().delete()
Region.objects.all().delete()
Country.objects.all().delete()
BoardType.objects.all().delete()
Amenity.objects.all().delete()

# Create Board Types
print("Creating board types...")
board_types_data = [
    {'name': 'Софттопы', 'name_en': 'Soft tops', 'icon': 'softtop', 'description': 'Perfect for beginners'},
    {'name': 'Лонгборды', 'name_en': 'Longboards', 'icon': 'longboard', 'description': '9ft+ classic longboards'},
    {'name': 'Мидлы', 'name_en': 'Funboards', 'icon': 'funboard', 'description': 'Mid-length versatile boards'},
    {'name': 'Шортборды', 'name_en': 'Shortboards', 'icon': 'shortboard', 'description': 'High performance boards'},
    {'name': 'Фишборды', 'name_en': 'Fish', 'icon': 'fish', 'description': 'Retro fish boards'},
]
board_types = []
for bt in board_types_data:
    obj = BoardType.objects.create(**bt)
    board_types.append(obj)
    print(f"  Created board type: {bt['name_en']}")

# Create Amenities
print("Creating amenities...")
amenities_data = [
    {'name': 'Бассейн', 'name_en': 'Pool', 'icon': 'pool', 'category': 'accommodation'},
    {'name': 'Wi-Fi', 'name_en': 'Wi-Fi', 'icon': 'wifi', 'category': 'services'},
    {'name': 'Кондиционер', 'name_en': 'Air Conditioning', 'icon': 'ac', 'category': 'accommodation'},
    {'name': 'Ресторан', 'name_en': 'Restaurant', 'icon': 'restaurant', 'category': 'food'},
    {'name': 'Бар', 'name_en': 'Bar', 'icon': 'bar', 'category': 'food'},
    {'name': 'Йога', 'name_en': 'Yoga', 'icon': 'yoga', 'category': 'activities'},
    {'name': 'Массаж', 'name_en': 'Massage', 'icon': 'massage', 'category': 'services'},
    {'name': 'Прокат велосипедов', 'name_en': 'Bike Rental', 'icon': 'bike', 'category': 'activities'},
    {'name': 'Трансфер', 'name_en': 'Airport Transfer', 'icon': 'transfer', 'category': 'services'},
    {'name': 'Прачечная', 'name_en': 'Laundry', 'icon': 'laundry', 'category': 'services'},
]
amenities = []
for am in amenities_data:
    obj = Amenity.objects.create(**am)
    amenities.append(obj)

# Countries and Regions data
print("Creating countries and regions...")
countries_data = {
    'IDN': {
        'name': 'Индонезия',
        'name_en': 'Indonesia',
        'description': 'Tropical paradise with world-class waves from Bali to Mentawai',
        'regions': [
            {'name': 'Бали', 'name_en': 'Bali', 'lat': -8.3405, 'lng': 115.0920},
            {'name': 'Ломбок', 'name_en': 'Lombok', 'lat': -8.6512, 'lng': 116.3249},
            {'name': 'Сумбава', 'name_en': 'Sumbawa', 'lat': -8.5000, 'lng': 117.5000},
            {'name': 'Ментаваи', 'name_en': 'Mentawai', 'lat': -1.4500, 'lng': 98.9000},
            {'name': 'Ява', 'name_en': 'Java', 'lat': -7.6145, 'lng': 110.7128},
            {'name': 'Сумба', 'name_en': 'Sumba', 'lat': -9.6500, 'lng': 120.2500},
        ]
    },
    'LKA': {
        'name': 'Шри-Ланка',
        'name_en': 'Sri Lanka',
        'description': 'Year-round surfing on the tropical island of Sri Lanka',
        'regions': [
            {'name': 'Велигама', 'name_en': 'Weligama', 'lat': 5.9720, 'lng': 80.4290},
            {'name': 'Мирисса', 'name_en': 'Mirissa', 'lat': 5.9449, 'lng': 80.4586},
            {'name': 'Хиккадува', 'name_en': 'Hikkaduwa', 'lat': 6.1395, 'lng': 80.0986},
            {'name': 'Аругам Бэй', 'name_en': 'Arugam Bay', 'lat': 6.8407, 'lng': 81.8365},
        ]
    },
    'PRT': {
        'name': 'Португалия',
        'name_en': 'Portugal',
        'description': 'Europe\'s premier surf destination with consistent Atlantic swells',
        'regions': [
            {'name': 'Пениш', 'name_en': 'Peniche', 'lat': 39.3558, 'lng': -9.3819},
            {'name': 'Эрисейра', 'name_en': 'Ericeira', 'lat': 38.9631, 'lng': -9.4166},
            {'name': 'Назаре', 'name_en': 'Nazare', 'lat': 39.6020, 'lng': -9.0692},
            {'name': 'Лагош', 'name_en': 'Lagos', 'lat': 37.1029, 'lng': -8.6730},
            {'name': 'Сагреш', 'name_en': 'Sagres', 'lat': 37.0086, 'lng': -8.9369},
            {'name': 'Кашкайш', 'name_en': 'Cascais', 'lat': 38.6979, 'lng': -9.4215},
        ]
    },
    'MAR': {
        'name': 'Марокко',
        'name_en': 'Morocco',
        'description': 'Consistent pointbreaks and rich culture on Africa\'s northwest coast',
        'regions': [
            {'name': 'Тагазут', 'name_en': 'Taghazout', 'lat': 30.5445, 'lng': -9.7088},
            {'name': 'Тамрахт', 'name_en': 'Tamraght', 'lat': 30.5200, 'lng': -9.6800},
            {'name': 'Иммессуан', 'name_en': 'Imsouane', 'lat': 30.8417, 'lng': -9.8250},
            {'name': 'Эссауэйра', 'name_en': 'Essaouira', 'lat': 31.5085, 'lng': -9.7595},
            {'name': 'Агадир', 'name_en': 'Agadir', 'lat': 30.4278, 'lng': -9.5981},
        ]
    },
    'CRI': {
        'name': 'Коста-Рика',
        'name_en': 'Costa Rica',
        'description': 'Pura Vida lifestyle with incredible biodiversity and warm water waves',
        'regions': [
            {'name': 'Тамариндо', 'name_en': 'Tamarindo', 'lat': 10.2995, 'lng': -85.8374},
            {'name': 'Санта Тереза', 'name_en': 'Santa Teresa', 'lat': 9.6421, 'lng': -85.1676},
            {'name': 'Носара', 'name_en': 'Nosara', 'lat': 9.9739, 'lng': -85.6538},
            {'name': 'Хако', 'name_en': 'Jaco', 'lat': 9.6168, 'lng': -84.6286},
            {'name': 'Доминикал', 'name_en': 'Dominical', 'lat': 9.2531, 'lng': -83.8580},
        ]
    },
    'ESP': {
        'name': 'Испания',
        'name_en': 'Spain',
        'description': 'Diverse coastline from the Basque Country to the Canary Islands',
        'regions': [
            {'name': 'Канарские острова', 'name_en': 'Canary Islands', 'lat': 28.2916, 'lng': -16.6291},
            {'name': 'Страна Басков', 'name_en': 'Basque Country', 'lat': 43.2630, 'lng': -2.9350},
            {'name': 'Галисия', 'name_en': 'Galicia', 'lat': 42.5751, 'lng': -8.1339},
            {'name': 'Андалусия', 'name_en': 'Andalusia', 'lat': 36.7213, 'lng': -4.4216},
        ]
    },
    'FRA': {
        'name': 'Франция',
        'name_en': 'France',
        'description': 'The birthplace of European surfing with legendary beaches',
        'regions': [
            {'name': 'Биарриц', 'name_en': 'Biarritz', 'lat': 43.4832, 'lng': -1.5586},
            {'name': 'Оссегор', 'name_en': 'Hossegor', 'lat': 43.6647, 'lng': -1.3988},
            {'name': 'Капбретон', 'name_en': 'Capbreton', 'lat': 43.6426, 'lng': -1.4286},
            {'name': 'Ла Грав', 'name_en': 'La Grave', 'lat': 43.5697, 'lng': -1.4689},
        ]
    },
    'AUS': {
        'name': 'Австралия',
        'name_en': 'Australia',
        'description': 'Iconic surf culture with world-class breaks along endless coastline',
        'regions': [
            {'name': 'Голд Кост', 'name_en': 'Gold Coast', 'lat': -28.0167, 'lng': 153.4000},
            {'name': 'Байрон Бэй', 'name_en': 'Byron Bay', 'lat': -28.6428, 'lng': 153.6119},
            {'name': 'Маргарет Ривер', 'name_en': 'Margaret River', 'lat': -33.9533, 'lng': 115.0778},
            {'name': 'Сидней', 'name_en': 'Sydney', 'lat': -33.8688, 'lng': 151.2093},
            {'name': 'Торки', 'name_en': 'Torquay', 'lat': -38.3316, 'lng': 144.3262},
        ]
    },
    'MEX': {
        'name': 'Мексика',
        'name_en': 'Mexico',
        'description': 'Pacific coast perfection from Baja to Puerto Escondido',
        'regions': [
            {'name': 'Пуэрто Эскондидо', 'name_en': 'Puerto Escondido', 'lat': 15.8720, 'lng': -97.0767},
            {'name': 'Саюлита', 'name_en': 'Sayulita', 'lat': 20.8697, 'lng': -105.4400},
            {'name': 'Баха Калифорния', 'name_en': 'Baja California', 'lat': 23.6345, 'lng': -109.6976},
            {'name': 'Тодос Сантос', 'name_en': 'Todos Santos', 'lat': 23.4500, 'lng': -110.2230},
        ]
    },
    'ZAF': {
        'name': 'Южная Африка',
        'name_en': 'South Africa',
        'description': 'Incredible variety from J-Bay to Cape Town\'s big waves',
        'regions': [
            {'name': 'Джей Бэй', 'name_en': "J-Bay", 'lat': -34.0343, 'lng': 24.9218},
            {'name': 'Кейптаун', 'name_en': 'Cape Town', 'lat': -33.9249, 'lng': 18.4241},
            {'name': 'Дурбан', 'name_en': 'Durban', 'lat': -29.8587, 'lng': 31.0218},
            {'name': 'Муссел Бэй', 'name_en': 'Mossel Bay', 'lat': -34.1833, 'lng': 22.1333},
        ]
    },
    'NIC': {
        'name': 'Никарагуа',
        'name_en': 'Nicaragua',
        'description': 'Uncrowded waves and affordable living in Central America',
        'regions': [
            {'name': 'Сан Хуан дель Сур', 'name_en': 'San Juan del Sur', 'lat': 11.2539, 'lng': -85.8662},
            {'name': 'Поповаки', 'name_en': 'Popoyo', 'lat': 11.4181, 'lng': -86.0139},
        ]
    },
    'PAN': {
        'name': 'Панама',
        'name_en': 'Panama',
        'description': 'Caribbean and Pacific waves in a tropical paradise',
        'regions': [
            {'name': 'Санта Каталина', 'name_en': 'Santa Catalina', 'lat': 7.6372, 'lng': -81.2586},
            {'name': 'Бокас дель Торо', 'name_en': 'Bocas del Toro', 'lat': 9.3403, 'lng': -82.2419},
        ]
    },
    'ECU': {
        'name': 'Эквадор',
        'name_en': 'Ecuador',
        'description': 'Year-round surf on the South American Pacific coast',
        'regions': [
            {'name': 'Монтаньита', 'name_en': 'Montanita', 'lat': -1.8283, 'lng': -80.7553},
            {'name': 'Канао', 'name_en': 'Canoa', 'lat': -0.4667, 'lng': -80.4500},
        ]
    },
    'PER': {
        'name': 'Перу',
        'name_en': 'Peru',
        'description': 'Legendary left pointbreaks along the Pacific coast',
        'regions': [
            {'name': 'Манкора', 'name_en': 'Mancora', 'lat': -4.1036, 'lng': -81.0458},
            {'name': 'Чикама', 'name_en': 'Chicama', 'lat': -7.7000, 'lng': -79.4500},
            {'name': 'Лима', 'name_en': 'Lima', 'lat': -12.0464, 'lng': -77.0428},
        ]
    },
    'PHL': {
        'name': 'Филиппины',
        'name_en': 'Philippines',
        'description': 'Tropical island surfing with warm water and friendly locals',
        'regions': [
            {'name': 'Сиаргао', 'name_en': 'Siargao', 'lat': 9.8550, 'lng': 126.0442},
            {'name': 'Ла Юнион', 'name_en': 'La Union', 'lat': 16.6181, 'lng': 120.3169},
            {'name': 'Багалонг', 'name_en': 'Baler', 'lat': 15.7594, 'lng': 121.5616},
        ]
    },
}

# Camp name templates by region
camp_names = {
    'Bali': ['Padang Padang Surf Camp', 'Uluwatu Wave Riders', 'Canggu Surf House', 'Kuta Beach Surf School', 'Seminyak Surf Lodge',
             'Medewi Surf Camp', 'Balangan Surf House', 'Echo Beach Camp', 'Green Bowl Surf', 'Bingin Waves'],
    'Lombok': ['Kuta Lombok Surf', 'Desert Point Camp', 'Gerupuk Bay Surf', 'Mawi Surf House', 'Ekas Bay Camp'],
    'Sumbawa': ['Lakey Peak Surf', 'Scar Reef Camp', 'Super Suck Surf Lodge', 'Yo-Yo\'s Surf House'],
    'Mentawai': ['Hollow Trees Camp', 'Macaronis Surf Lodge', 'Lance\'s Right Camp', 'Rifles Surf House'],
    'Weligama': ['Weligama Bay Surf', 'Stilt Fisherman Camp', 'Lanka Surf House', 'Coconut Beach Surf'],
    'Mirissa': ['Mirissa Waves Camp', 'Secret Point Lodge', 'Whale Beach Surf'],
    'Arugam Bay': ['Main Point Surf Camp', 'Whisky Point Lodge', 'Baby Point House', 'Elephant Rock Surf'],
    'Peniche': ['Supertubos Surf Camp', 'Baleal Surf House', 'Peniche Waves', 'Medao Grande Camp', 'Lagido Surf Lodge'],
    'Ericeira': ['Ribeira d\'Ilhas Camp', 'Coxos Surf House', 'Cave Surf Lodge', 'Pedra Branca Camp'],
    'Nazare': ['Big Wave Camp', 'North Canyon Lodge', 'Nazare Surf House'],
    'Taghazout': ['Anchor Point Camp', 'Hash Point Surf', 'Killer Point Lodge', 'Panoramas Surf House', 'Devil\'s Rock Camp'],
    'Tamraght': ['Banana Point Surf', 'Crocodile Surf House', 'Tamraght Waves'],
    'Imsouane': ['Magic Bay Camp', 'Cathedral Surf House', 'Long Wave Lodge'],
    'Tamarindo': ['Tamarindo Surf Camp', 'Playa Grande Lodge', 'Langosta Surf House', 'Avellanas Wave Camp'],
    'Santa Teresa': ['Playa Carmen Surf', 'Santa Teresa Wave House', 'Mal Pais Camp', 'Hermosa Surf Lodge'],
    'Nosara': ['Playa Guiones Surf', 'Garza Surf Camp', 'Nosara Wave House'],
    'Canary Islands': ['Fuerteventura Surf', 'Lanzarote Wave Camp', 'Tenerife Surf House', 'Gran Canaria Lodge'],
    'Basque Country': ['Mundaka Surf Camp', 'Sopelana Wave House', 'Zarautz Surf Lodge', 'San Sebastian Camp'],
    'Biarritz': ['Grande Plage Surf', 'Côte des Basques Camp', 'Marbella Surf House'],
    'Hossegor': ['La Gravière Camp', 'Les Estagnots Surf', 'La Nord Surf House', 'Capbreton Lodge'],
    'Gold Coast': ['Snapper Rocks Surf', 'Kirra Point Camp', 'Coolangatta Wave House', 'Burleigh Heads Lodge'],
    'Byron Bay': ['The Pass Surf Camp', 'Wategos Waves', 'Broken Head Lodge', 'Suffolk Park Surf'],
    'Puerto Escondido': ['Zicatela Surf Camp', 'La Punta Lodge', 'Carrizalillo Wave House', 'Mexican Pipeline Camp'],
    'Sayulita': ['Sayulita Surf School', 'Punta Mita Lodge', 'San Pancho Camp'],
    'J-Bay': ['Supertubes Surf Lodge', 'J-Bay Wave Camp', 'Jeffreys Bay Surf House'],
    'Cape Town': ['Muizenberg Surf', 'Dungeons Big Wave Camp', 'Long Beach Lodge', 'Kommetjie Surf House'],
    'Siargao': ['Cloud 9 Surf Camp', 'General Luna Lodge', 'Tuason Point House', 'Quicksilver Surf'],
    'Montanita': ['La Punta Surf', 'Montanita Wave House', 'Olón Surf Camp'],
    'Mancora': ['Mancora Surf Camp', 'Las Pocitas Lodge', 'Pan American Surf House'],
    'San Juan del Sur': ['Maderas Surf Camp', 'Remanso Wave Lodge', 'Playa Hermosa House'],
}

# Create all countries and regions
regions_map = {}
for code, data in countries_data.items():
    country = Country.objects.create(
        name=data['name'],
        name_en=data['name_en'],
        code=code,
        description=data['description'],
        is_active=True
    )
    print(f"Created country: {data['name_en']}")

    for region_data in data['regions']:
        region = Region.objects.create(
            country=country,
            name=region_data['name'],
            name_en=region_data['name_en'],
            latitude=region_data['lat'],
            longitude=region_data['lng']
        )
        regions_map[region_data['name_en']] = region
        print(f"  Created region: {region_data['name_en']}")

# Sample descriptions
descriptions_en = [
    "Experience the ultimate surf adventure at our beachfront camp. With daily surf lessons, yoga sessions, and comfortable accommodation, we offer the perfect blend of adventure and relaxation.",
    "Our surf camp is nestled in paradise, offering world-class waves just steps from your door. Whether you're a beginner or advanced surfer, our experienced instructors will help you catch the perfect wave.",
    "Join our surf community and discover why surfers from around the world come back year after year. Crystal clear waters, consistent waves, and an unforgettable atmosphere await you.",
    "Wake up to the sound of waves and enjoy daily surf sessions with our certified instructors. Our camp offers everything you need for an epic surf trip.",
    "Located at one of the best surf spots in the region, our camp provides the ideal base for your surfing adventure. Enjoy quality boards, expert coaching, and a vibrant surf community.",
]

histories = [
    "Founded by professional surfers in 2010, our camp started as a small beach shack and has grown into one of the most respected surf schools in the region.",
    "What began as a passion project between two traveling surfers has evolved into a world-renowned surf destination, welcoming thousands of surf enthusiasts each year.",
    "Our founders discovered this magical spot in 2008 while on a surf trip. Unable to leave, they built a small camp that has grown with the same spirit of adventure.",
    "Started by a local surf family, our camp represents generations of wave knowledge passed down through the years. We share not just surfing, but our way of life.",
    "After years of competitive surfing, our founders wanted to share their passion with others. What started as informal lessons became this beloved surf camp.",
]

instructor_names = [
    "Carlos", "Maria", "João", "Ana", "Pedro", "Sofia", "Marco", "Laura", "Diego", "Isabella",
    "Kai", "Luna", "Mateo", "Valentina", "Lucas", "Elena", "Gabriel", "Mia", "Sebastian", "Camila",
    "Made", "Wayan", "Ketut", "Nyoman", "Komang", "Putu", "Kadek", "Gede", "Agung", "Surya"
]

reviewer_names = [
    ("John S.", "USA"), ("Emma W.", "UK"), ("Thomas M.", "Germany"), ("Sophie L.", "France"),
    ("Andreas K.", "Sweden"), ("Marta P.", "Spain"), ("Dmitri V.", "Russia"), ("Yuki T.", "Japan"),
    ("Michael B.", "Australia"), ("Lisa H.", "Canada"), ("Pierre D.", "Belgium"), ("Hans M.", "Netherlands"),
    ("Marco R.", "Italy"), ("Katarina N.", "Norway"), ("David C.", "Ireland"), ("Sarah J.", "New Zealand"),
    ("Alex P.", "Brazil"), ("Maria G.", "Argentina"), ("Chen W.", "China"), ("Kim L.", "South Korea"),
]

review_texts = [
    "Amazing experience! The waves were perfect and the instructors were incredibly patient and knowledgeable.",
    "Best surf camp I've ever been to. The vibe, the waves, the people - everything was perfect!",
    "Went from never surfing to catching real waves in just a week. The coaching here is top-notch.",
    "Beautiful location, friendly staff, and great facilities. Will definitely come back next year!",
    "The instructors really know what they're doing. I improved so much during my stay.",
    "Perfect combination of surfing, yoga, and relaxation. This place has it all!",
    "Great atmosphere and excellent value for money. The food was delicious too!",
    "Couldn't have asked for a better introduction to surfing. Thank you for an unforgettable experience!",
    "The waves here are incredible and the camp is perfectly located. Highly recommended!",
    "Outstanding instruction and wonderful community. Already planning my return trip!",
]

# Create camps
print("\nCreating surf camps...")
camp_count = 0

for region_name, region in regions_map.items():
    # Get camp names for this region or use generic names
    names = camp_names.get(region_name, [f"{region_name} Surf Camp {i+1}" for i in range(5)])

    for name in names:
        # Randomize camp attributes
        base_price = random.randint(35, 200)
        has_pool = random.random() > 0.6
        has_yoga = random.random() > 0.5
        has_restaurant = random.random() > 0.4
        has_parties = random.random() > 0.7
        board_rental = random.random() > 0.3
        bed_breakfast = random.random() > 0.5

        skill_levels = random.sample(['beginner', 'intermediate', 'advanced'], k=random.randint(1, 3))

        # Create camp
        camp = SurfCamp.objects.create(
            name=name,
            slug=name.lower().replace(' ', '-').replace("'", '').replace('/', '-'),
            region=region,
            short_description=f"Premier surf camp in {region_name} offering world-class waves and expert coaching.",
            description=random.choice(descriptions_en),
            history=random.choice(histories) if random.random() > 0.3 else '',
            address=f"{random.randint(1, 999)} Beach Road, {region_name}",
            latitude=region.latitude + random.uniform(-0.05, 0.05),
            longitude=region.longitude + random.uniform(-0.05, 0.05),
            price_per_night=Decimal(str(base_price)),
            price_per_lesson=Decimal(str(random.randint(25, 80))) if random.random() > 0.3 else None,
            has_bed_breakfast=bed_breakfast,
            bed_breakfast_price=Decimal(str(random.randint(10, 25))) if bed_breakfast else None,
            skill_levels=skill_levels,
            has_pool=has_pool,
            has_restaurant=has_restaurant,
            has_yoga=has_yoga,
            has_parties=has_parties,
            board_rental_available=board_rental,
            board_rental_price=Decimal(str(random.randint(10, 35))) if board_rental else None,
            website=f"https://www.{name.lower().replace(' ', '')}.com",
            email=f"info@{name.lower().replace(' ', '')}.com",
            phone=f"+{random.randint(1, 99)}{random.randint(100000000, 999999999)}",
            instagram=f"@{name.lower().replace(' ', '_')}",
            rating=Decimal(str(round(random.uniform(4.0, 5.0), 1))),
            reviews_count=random.randint(10, 200),
            is_featured=random.random() > 0.85,
            is_active=True,
        )

        # Add board types
        camp.board_types.set(random.sample(board_types, k=random.randint(2, len(board_types))))

        # Add amenities
        camp.amenities.set(random.sample(amenities, k=random.randint(3, len(amenities))))

        # Create instructors
        num_instructors = random.randint(2, 5)
        for i in range(num_instructors):
            Instructor.objects.create(
                camp=camp,
                name=random.choice(instructor_names),
                bio=f"Professional surfer with {random.randint(5, 20)} years of experience.",
                experience_years=random.randint(5, 20),
                certifications="ISA Level " + str(random.randint(1, 3)) + " Certified",
                languages=random.choice(["English, Spanish", "English, Portuguese", "English, French", "English, Indonesian"]),
                is_head_coach=i == 0
            )

        # Create activities
        activities_data = [
            ('Серф-урок', 'Surf Lesson', 'Professional coaching session', True),
            ('Йога', 'Yoga', 'Morning yoga session', random.random() > 0.5),
            ('Экскурсия', 'Excursion', 'Local sightseeing trip', False),
            ('Массаж', 'Massage', 'Relaxing massage treatment', False),
            ('Аренда скутера', 'Scooter Rental', 'Explore the area', False),
        ]
        for act in activities_data:
            if random.random() > 0.3:
                Activity.objects.create(
                    camp=camp,
                    name=act[0],
                    name_en=act[1],
                    description=act[2],
                    price=None if act[3] else Decimal(str(random.randint(15, 50))),
                    is_included=act[3]
                )

        # Create reviews
        num_reviews = random.randint(3, 8)
        for _ in range(num_reviews):
            reviewer = random.choice(reviewer_names)
            Review.objects.create(
                camp=camp,
                author_name=reviewer[0],
                author_country=reviewer[1],
                rating=random.randint(4, 5),
                title=random.choice(["Great experience!", "Amazing!", "Highly recommend!", "Perfect vacation", "Will return!"]),
                text=random.choice(review_texts),
                surf_level=random.choice(['beginner', 'intermediate', 'advanced']),
                is_verified=random.random() > 0.3,
                is_published=True
            )

        camp_count += 1
        if camp_count % 10 == 0:
            print(f"  Created {camp_count} camps...")

print(f"\nDone! Created {camp_count} surf camps across {len(regions_map)} regions in {len(countries_data)} countries.")
print(f"Total countries: {Country.objects.count()}")
print(f"Total regions: {Region.objects.count()}")
print(f"Total camps: {SurfCamp.objects.count()}")
