from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import FilterSet, CharFilter, NumberFilter
from .models import SurfSpot
from .serializers import SurfSpotListSerializer, SurfSpotDetailSerializer


class SurfSpotFilter(FilterSet):
    country = CharFilter(field_name='region__country__code', lookup_expr='iexact')
    region = NumberFilter(field_name='region__id')
    wave_type = CharFilter(field_name='wave_type')
    wave_direction = CharFilter(field_name='wave_direction')
    skill_level = CharFilter(method='filter_skill_level')
    crowd_level = CharFilter(field_name='crowd_level')

    class Meta:
        model = SurfSpot
        fields = ['country', 'region', 'wave_type', 'wave_direction', 'skill_level', 'crowd_level']

    def filter_skill_level(self, queryset, name, value):
        # Filter JSONField array for containing the value
        return queryset.filter(skill_levels__icontains=value)


class SurfSpotViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = SurfSpot.objects.filter(is_active=True).select_related(
        'region', 'region__country'
    ).prefetch_related('images')
    filterset_class = SurfSpotFilter
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'rating', 'crowd_level']
    ordering = ['name']
    lookup_field = 'slug'

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return SurfSpotDetailSerializer
        return SurfSpotListSerializer

    @action(detail=False, methods=['get'])
    def map_data(self, request):
        """Данные для карты"""
        spots = self.filter_queryset(self.get_queryset())
        data = spots.values(
            'id', 'name', 'slug', 'latitude', 'longitude',
            'wave_type', 'wave_direction', 'skill_levels', 'crowd_level'
        )
        return Response(list(data))
