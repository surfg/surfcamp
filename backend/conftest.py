import pytest
from django.contrib.auth.models import User
from rest_framework.test import APIClient

from camps.models import Country, Region, BoardType, Amenity, SurfCamp, Review
from spots.models import SurfSpot


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def admin_user(db):
    return User.objects.create_superuser(
        username='testadmin',
        email='admin@test.com',
        password='testpass123'
    )


@pytest.fixture
def country(db):
    return Country.objects.create(
        name='Индонезия',
        name_en='Indonesia',
        code='IDN',
        description='Surf paradise',
        is_active=True
    )


@pytest.fixture
def region(db, country):
    return Region.objects.create(
        country=country,
        name='Чангу',
        name_en='Canggu',
        latitude=-8.6478,
        longitude=115.1385
    )


@pytest.fixture
def board_types(db):
    return [
        BoardType.objects.create(name='Софттоп', name_en='Soft Top'),
        BoardType.objects.create(name='Лонгборд', name_en='Longboard'),
        BoardType.objects.create(name='Шортборд', name_en='Shortboard'),
    ]


@pytest.fixture
def amenities(db):
    return [
        Amenity.objects.create(name='Wi-Fi', name_en='Free WiFi', category='accommodation'),
        Amenity.objects.create(name='Завтрак', name_en='Breakfast', category='food'),
    ]


@pytest.fixture
def surf_camp(db, region, board_types, amenities):
    camp = SurfCamp.objects.create(
        name='Test Surf Camp',
        slug='test-surf-camp',
        region=region,
        short_description='A great surf camp for testing',
        description='Full description of the test surf camp',
        address='123 Beach Road, Canggu',
        latitude=-8.6512,
        longitude=115.1324,
        price_per_night=89.00,
        price_per_lesson=45.00,
        skill_levels=['beginner', 'intermediate'],
        board_rental_available=True,
        board_rental_price=15.00,
        has_pool=True,
        has_yoga=True,
        rating=4.5,
        reviews_count=10,
        is_featured=True,
        is_active=True
    )
    camp.board_types.set(board_types)
    camp.amenities.set(amenities)
    return camp


@pytest.fixture
def surf_spot(db, region):
    return SurfSpot.objects.create(
        name='Test Beach',
        slug='test-beach',
        region=region,
        description='A great beginner spot',
        short_description='Beginner friendly',
        latitude=-8.6556,
        longitude=115.1328,
        wave_direction='both',
        wave_type='beach',
        skill_levels=['beginner'],
        crowd_level='medium',
        rating=4.2,
        is_active=True
    )


@pytest.fixture
def review(db, surf_camp):
    return Review.objects.create(
        camp=surf_camp,
        author_name='Test User',
        author_country='USA',
        rating=5,
        title='Amazing experience!',
        text='I had a wonderful time at this surf camp.',
        surf_level='beginner',
        is_verified=True,
        is_published=True
    )
