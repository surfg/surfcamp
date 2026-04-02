from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q

from .models import SurfLesson, LessonProvider
from .serializers import (
    SurfLessonListSerializer, SurfLessonDetailSerializer,
    LessonProviderSerializer
)


class SurfLessonViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for surf lessons"""
    queryset = SurfLesson.objects.filter(is_active=True).select_related(
        'provider', 'provider__region', 'provider__region__country'
    )
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = {
        'lesson_type': ['exact'],
        'skill_level': ['exact'],
        'provider__region__country__code': ['exact'],
        'provider__region': ['exact'],
        'price': ['gte', 'lte'],
        'duration_minutes': ['gte', 'lte'],
        'includes_equipment': ['exact'],
        'includes_transport': ['exact'],
        'is_package': ['exact'],
        'is_featured': ['exact'],
    }
    search_fields = ['name', 'name_ru', 'description', 'provider__name']
    ordering_fields = ['price', 'rating', 'duration_minutes', 'created_at']
    ordering = ['-is_featured', '-rating']
    lookup_field = 'slug'

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return SurfLessonDetailSerializer
        return SurfLessonListSerializer

    def get_queryset(self):
        queryset = super().get_queryset()

        # Filter by country code (shortcut)
        country = self.request.query_params.get('country')
        if country:
            queryset = queryset.filter(provider__region__country__code=country)

        # Filter by region
        region = self.request.query_params.get('region')
        if region:
            queryset = queryset.filter(provider__region_id=region)

        # Filter by max price
        max_price = self.request.query_params.get('max_price')
        if max_price:
            queryset = queryset.filter(price__lte=max_price)

        # Filter by min price
        min_price = self.request.query_params.get('min_price')
        if min_price:
            queryset = queryset.filter(price__gte=min_price)

        # Filter by skill level
        skill_level = self.request.query_params.get('skill_level')
        if skill_level:
            queryset = queryset.filter(
                Q(skill_level=skill_level) | Q(skill_level='all')
            )

        # Filter by lesson type
        lesson_type = self.request.query_params.get('lesson_type')
        if lesson_type:
            queryset = queryset.filter(lesson_type=lesson_type)

        # Filter by duration (max)
        max_duration = self.request.query_params.get('max_duration')
        if max_duration:
            queryset = queryset.filter(duration_minutes__lte=max_duration)

        return queryset

    @action(detail=False, methods=['get'])
    def featured(self, request):
        """Get featured lessons"""
        featured = self.get_queryset().filter(is_featured=True)[:8]
        serializer = SurfLessonListSerializer(featured, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def filters(self, request):
        """Get filter options for lessons"""
        lessons = SurfLesson.objects.filter(is_active=True)

        # Get countries with lesson count
        from django.db.models import Count
        from camps.models import Country

        countries_with_lessons = Country.objects.filter(
            regions__lesson_providers__lessons__is_active=True
        ).annotate(
            lessons_count=Count('regions__lesson_providers__lessons', distinct=True)
        ).filter(lessons_count__gt=0).order_by('name')

        # Price range
        from django.db.models import Min, Max, Avg
        price_stats = lessons.aggregate(
            min=Min('price'),
            max=Max('price'),
            avg=Avg('price')
        )

        return Response({
            'countries': [
                {
                    'id': c.id,
                    'name': c.name,
                    'name_en': c.name_en,
                    'code': c.code,
                    'lessons_count': c.lessons_count
                }
                for c in countries_with_lessons
            ],
            'lesson_types': [
                {'value': 'private', 'label': 'Private', 'label_ru': 'Индивидуальный'},
                {'value': 'group', 'label': 'Group', 'label_ru': 'Групповой'},
                {'value': 'semi_private', 'label': 'Semi-Private', 'label_ru': 'Полуиндивидуальный'},
            ],
            'skill_levels': [
                {'value': 'beginner', 'label': 'Beginner', 'label_ru': 'Начинающий'},
                {'value': 'intermediate', 'label': 'Intermediate', 'label_ru': 'Средний'},
                {'value': 'advanced', 'label': 'Advanced', 'label_ru': 'Продвинутый'},
                {'value': 'all', 'label': 'All Levels', 'label_ru': 'Все уровни'},
            ],
            'price_range': {
                'min': float(price_stats['min'] or 0),
                'max': float(price_stats['max'] or 500),
                'avg': float(price_stats['avg'] or 100),
            },
            'durations': [
                {'value': 60, 'label': '1 hour', 'label_ru': '1 час'},
                {'value': 90, 'label': '1.5 hours', 'label_ru': '1.5 часа'},
                {'value': 120, 'label': '2 hours', 'label_ru': '2 часа'},
                {'value': 180, 'label': '3 hours', 'label_ru': '3 часа'},
                {'value': 240, 'label': '4+ hours', 'label_ru': '4+ часа'},
            ],
        })


class LessonProviderViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for lesson providers"""
    queryset = LessonProvider.objects.filter(is_active=True).select_related(
        'region', 'region__country'
    ).prefetch_related('lessons')
    serializer_class = LessonProviderSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['region__country__code', 'region', 'is_featured']
    search_fields = ['name', 'description']
    ordering_fields = ['rating', 'reviews_count', 'name']
    ordering = ['-is_featured', '-rating']
    lookup_field = 'slug'
