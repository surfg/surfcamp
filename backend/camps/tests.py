import pytest
from rest_framework import status

from camps.models import SurfCamp, Review


@pytest.mark.django_db
class TestCountryAPI:
    def test_list_countries(self, api_client, country):
        url = '/api/countries/'
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]['name_en'] == 'Indonesia'
        assert response.data[0]['code'] == 'IDN'


@pytest.mark.django_db
class TestRegionAPI:
    def test_list_regions(self, api_client, region):
        url = '/api/regions/'
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]['name_en'] == 'Canggu'


@pytest.mark.django_db
class TestSurfCampAPI:
    def test_list_camps(self, api_client, surf_camp):
        url = '/api/camps/'
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 1
        assert response.data['results'][0]['name'] == 'Test Surf Camp'

    def test_retrieve_camp(self, api_client, surf_camp):
        url = f'/api/camps/{surf_camp.slug}/'
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data['name'] == 'Test Surf Camp'
        assert response.data['price_per_night'] == '89.00'
        assert 'beginner' in response.data['skill_levels']
        assert response.data['has_pool'] is True

    def test_featured_camps(self, api_client, surf_camp):
        url = '/api/camps/featured/'
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]['is_featured'] is True

    def test_map_data(self, api_client, surf_camp):
        url = '/api/camps/map_data/'
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert 'latitude' in response.data[0]
        assert 'longitude' in response.data[0]

    def test_filter_by_skill_level(self, api_client, surf_camp):
        url = '/api/camps/?skill_level=beginner'
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 1

        url = '/api/camps/?skill_level=advanced'
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 0

    def test_filter_by_price(self, api_client, surf_camp):
        url = '/api/camps/?min_price=50&max_price=100'
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 1

        url = '/api/camps/?min_price=100'
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 0

    def test_filter_by_amenities(self, api_client, surf_camp):
        url = '/api/camps/?has_pool=true'
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 1

        url = '/api/camps/?has_pool=false'
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 0

    def test_search_camps(self, api_client, surf_camp):
        url = '/api/camps/?search=Test'
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 1

        url = '/api/camps/?search=NonExistent'
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 0


@pytest.mark.django_db
class TestReviewAPI:
    def test_list_reviews(self, api_client, review):
        url = '/api/reviews/'
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 1
        assert response.data['results'][0]['author_name'] == 'Test User'

    def test_camp_reviews(self, api_client, surf_camp, review):
        url = f'/api/camps/{surf_camp.slug}/reviews/'
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
class TestModels:
    def test_country_str(self, country):
        assert str(country) == 'Индонезия'

    def test_region_str(self, region, country):
        assert str(region) == 'Чангу, Индонезия'

    def test_camp_str(self, surf_camp):
        assert str(surf_camp) == 'Test Surf Camp'

    def test_camp_country_property(self, surf_camp, country):
        assert surf_camp.country == country

    def test_review_updates_camp_rating(self, surf_camp):
        # Create a new review
        review = Review.objects.create(
            camp=surf_camp,
            author_name='New Reviewer',
            rating=5,
            text='Great!',
            is_published=True
        )

        # Verify the review was created
        assert review.id is not None
        assert review.rating == 5

        # The camp rating should be updated
        surf_camp.refresh_from_db()
        assert surf_camp.rating > 0
