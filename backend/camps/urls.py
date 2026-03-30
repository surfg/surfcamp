from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CountryViewSet, RegionViewSet, BoardTypeViewSet,
    AmenityViewSet, SurfCampViewSet, ReviewViewSet,
    search_autocomplete, filter_options
)

router = DefaultRouter()
router.register('countries', CountryViewSet)
router.register('regions', RegionViewSet)
router.register('board-types', BoardTypeViewSet)
router.register('amenities', AmenityViewSet)
router.register('camps', SurfCampViewSet)
router.register('reviews', ReviewViewSet)

urlpatterns = [
    path('search/', search_autocomplete, name='search-autocomplete'),
    path('filters/', filter_options, name='filter-options'),
    path('', include(router.urls)),
]
