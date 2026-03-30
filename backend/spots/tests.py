import pytest
from rest_framework import status

from spots.models import SurfSpot


@pytest.mark.django_db
class TestSurfSpotAPI:
    def test_list_spots(self, api_client, surf_spot):
        url = '/api/spots/'
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 1
        assert response.data['results'][0]['name'] == 'Test Beach'

    def test_retrieve_spot(self, api_client, surf_spot):
        url = f'/api/spots/{surf_spot.slug}/'
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data['name'] == 'Test Beach'
        assert response.data['wave_type'] == 'beach'
        assert response.data['wave_direction'] == 'both'

    def test_retrieve_spot_detail_fields(self, api_client, surf_spot):
        """Test that detail endpoint includes all expected fields"""
        url = f'/api/spots/{surf_spot.slug}/'
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        # Check detail-specific fields exist
        assert 'description' in response.data
        assert 'best_tide' in response.data
        assert 'best_swell' in response.data
        assert 'best_wind' in response.data
        assert 'hazards' in response.data
        assert 'has_parking' in response.data
        assert 'has_showers' in response.data
        assert 'nearby_camps' in response.data
        assert 'images' in response.data

    def test_retrieve_spot_not_found(self, api_client):
        """Test 404 for non-existent spot"""
        url = '/api/spots/nonexistent-spot/'
        response = api_client.get(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_nearby_camps_in_spot_detail(self, api_client, surf_spot, surf_camp):
        """Test that nearby camps are included in spot detail"""
        # Associate the camp with the spot
        surf_camp.spots.add(surf_spot)

        url = f'/api/spots/{surf_spot.slug}/'
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert 'nearby_camps' in response.data
        assert len(response.data['nearby_camps']) == 1
        assert response.data['nearby_camps'][0]['name'] == surf_camp.name

    def test_map_data(self, api_client, surf_spot):
        url = '/api/spots/map_data/'
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert 'latitude' in response.data[0]
        assert 'longitude' in response.data[0]

    def test_filter_by_skill_level(self, api_client, surf_spot):
        url = '/api/spots/?skill_level=beginner'
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 1

        url = '/api/spots/?skill_level=advanced'
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 0

    def test_filter_by_wave_type(self, api_client, surf_spot):
        url = '/api/spots/?wave_type=beach'
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 1

        url = '/api/spots/?wave_type=reef'
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 0


@pytest.mark.django_db
class TestSurfSpotModel:
    def test_spot_str(self, surf_spot, region):
        assert str(surf_spot) == f'Test Beach, {region.name}'

    def test_spot_main_image_none(self, surf_spot):
        assert surf_spot.main_image is None
