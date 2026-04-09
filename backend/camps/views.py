from rest_framework import viewsets, filters
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend, FilterSet, CharFilter, NumberFilter, BooleanFilter
from django.db.models import Q, Value, CharField, Min, Max, Avg
from django.db.models.functions import Concat
from .models import Country, Region, BoardType, Amenity, SurfCamp, Review
from .serializers import (
    CountrySerializer, RegionSerializer, BoardTypeSerializer,
    AmenitySerializer, SurfCampListSerializer, SurfCampDetailSerializer,
    ReviewSerializer
)


class SurfCampFilter(FilterSet):
    country = CharFilter(field_name='region__country__code', lookup_expr='iexact')
    region = NumberFilter(field_name='region__id')
    min_price = NumberFilter(field_name='price_per_night', lookup_expr='gte')
    max_price = NumberFilter(field_name='price_per_night', lookup_expr='lte')
    skill_level = CharFilter(method='filter_skill_level')
    language = CharFilter(method='filter_language')
    has_pool = BooleanFilter(field_name='has_pool')
    has_yoga = BooleanFilter(field_name='has_yoga')
    has_parties = BooleanFilter(field_name='has_parties')
    has_bed_breakfast = BooleanFilter(field_name='has_bed_breakfast')
    board_rental = BooleanFilter(field_name='board_rental_available')
    min_rating = NumberFilter(field_name='rating', lookup_expr='gte')
    is_featured = BooleanFilter(field_name='is_featured')
    board_types = CharFilter(method='filter_board_types')

    class Meta:
        model = SurfCamp
        fields = [
            'country', 'region', 'min_price', 'max_price',
            'skill_level', 'language', 'has_pool', 'has_yoga', 'has_parties',
            'has_bed_breakfast', 'board_rental', 'min_rating', 'is_featured',
            'board_types'
        ]

    def filter_skill_level(self, queryset, name, value):
        # Filter JSONField array for containing the value
        return queryset.filter(skill_levels__icontains=value)

    def filter_language(self, queryset, name, value):
        # Filter JSONField array for containing the language code
        return queryset.filter(teaching_languages__icontains=value)

    def filter_board_types(self, queryset, name, value):
        # Filter by board types (comma-separated IDs)
        if value:
            board_type_ids = [int(x) for x in value.split(',') if x.isdigit()]
            if board_type_ids:
                return queryset.filter(board_types__id__in=board_type_ids).distinct()
        return queryset


class CountryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Country.objects.filter(is_active=True)
    serializer_class = CountrySerializer
    pagination_class = None


class RegionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Region.objects.all()
    serializer_class = RegionSerializer
    filterset_fields = ['country']
    pagination_class = None


class BoardTypeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = BoardType.objects.all()
    serializer_class = BoardTypeSerializer
    pagination_class = None


class AmenityViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Amenity.objects.all()
    serializer_class = AmenitySerializer
    pagination_class = None


class SurfCampViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = SurfCamp.objects.filter(is_active=True).select_related(
        'region', 'region__country'
    ).prefetch_related('images', 'board_types', 'amenities')
    filterset_class = SurfCampFilter
    search_fields = ['name', 'short_description', 'address', 'region__name']
    ordering_fields = ['price_per_night', 'rating', 'reviews_count', 'created_at']
    ordering = ['-is_featured', '-rating']
    lookup_field = 'slug'

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return SurfCampDetailSerializer
        return SurfCampListSerializer

    @action(detail=False, methods=['get'])
    def featured(self, request):
        """Рекомендуемые кемпы"""
        featured = self.queryset.filter(is_featured=True)[:6]
        serializer = SurfCampListSerializer(featured, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def map_data(self, request):
        """Данные для карты (минимум полей)"""
        camps = self.filter_queryset(self.get_queryset())
        data = camps.values(
            'id', 'name', 'slug', 'latitude', 'longitude',
            'price_per_night', 'rating', 'skill_levels'
        )
        return Response(list(data))

    @action(detail=True, methods=['get'])
    def reviews(self, request, slug=None):
        """Отзывы кемпа с пагинацией"""
        camp = self.get_object()
        reviews = camp.reviews.filter(is_published=True)
        page = self.paginate_queryset(reviews)
        if page is not None:
            serializer = ReviewSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = ReviewSerializer(reviews, many=True)
        return Response(serializer.data)


class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.filter(is_published=True)
    serializer_class = ReviewSerializer
    filterset_fields = ['camp', 'rating', 'surf_level']
    ordering = ['-created_at']

    def get_queryset(self):
        queryset = super().get_queryset()
        camp_slug = self.request.query_params.get('camp_slug')
        if camp_slug:
            queryset = queryset.filter(camp__slug=camp_slug)
        return queryset


@api_view(['GET'])
def search_autocomplete(request):
    """
    Поиск с автодополнением по странам, регионам и кемпам
    Поддерживает русский и английский языки
    """
    from django.db.models import Count

    query = request.query_params.get('q', '').strip()
    lang = request.query_params.get('lang', 'en')  # 'en' или 'ru'

    if len(query) < 2:
        return Response({'results': []})

    # Для кириллицы делаем поиск и с заглавной и с маленькой буквы
    query_lower = query.lower()
    query_title = query.title()
    query_upper = query.upper()

    results = []

    def get_localized(name_ru, name_en):
        """Возвращает локализованное название"""
        if lang == 'ru':
            return name_ru or name_en
        return name_en or name_ru

    # Поиск по странам (ищем и в русских и в английских названиях)
    countries = Country.objects.filter(
        Q(name__icontains=query) | Q(name_en__icontains=query) |
        Q(name__icontains=query_lower) | Q(name__icontains=query_title) |
        Q(name__icontains=query_upper),
        is_active=True
    ).annotate(
        camps_count=Count('regions__camps', filter=Q(regions__camps__is_active=True))
    ).distinct()[:3]
    for country in countries:
        results.append({
            'type': 'country',
            'id': country.id,
            'name': get_localized(country.name, country.name_en),
            'name_ru': country.name,
            'name_en': country.name_en,
            'code': country.code,
            'camps_count': country.camps_count,
            'image': country.image.url if country.image else None
        })

    # Поиск по регионам
    regions = Region.objects.filter(
        Q(name__icontains=query) | Q(name_en__icontains=query) |
        Q(name__icontains=query_lower) | Q(name__icontains=query_title) |
        Q(name__icontains=query_upper)
    ).select_related('country').annotate(
        camps_count=Count('camps', filter=Q(camps__is_active=True))
    ).distinct()[:3]
    for region in regions:
        results.append({
            'type': 'region',
            'id': region.id,
            'name': get_localized(region.name, region.name_en),
            'name_ru': region.name,
            'name_en': region.name_en,
            'country_name': get_localized(region.country.name, region.country.name_en),
            'country_code': region.country.code,
            'camps_count': region.camps_count
        })

    # Поиск по кемпам (также ищем по русскому названию региона)
    camps = SurfCamp.objects.filter(
        Q(name__icontains=query) |
        Q(short_description__icontains=query) |
        Q(region__name__icontains=query) |
        Q(region__name_en__icontains=query) |
        Q(region__country__name__icontains=query) |
        Q(region__country__name_en__icontains=query) |
        Q(region__name__icontains=query_lower) |
        Q(region__name__icontains=query_title) |
        Q(region__country__name__icontains=query_lower) |
        Q(region__country__name__icontains=query_title),
        is_active=True
    ).select_related('region', 'region__country').distinct()[:5]
    for camp in camps:
        results.append({
            'type': 'camp',
            'id': camp.id,
            'slug': camp.slug,
            'name': camp.name,
            'region_name': get_localized(camp.region.name, camp.region.name_en),
            'country_name': get_localized(camp.region.country.name, camp.region.country.name_en),
            'price_per_night': float(camp.price_per_night),
            'rating': float(camp.rating),
            'image': camp.main_image.url if camp.main_image else None
        })

    return Response({'results': results})


@api_view(['GET'])
def filter_options(request):
    """
    Получить все доступные опции для фильтров
    """
    from django.db.models import Count

    # Страны с кемпами (используем annotate для camps_count)
    countries = Country.objects.filter(
        is_active=True
    ).annotate(
        camps_count=Count('regions__camps', filter=Q(regions__camps__is_active=True))
    ).filter(
        camps_count__gt=0
    ).values('id', 'name', 'name_en', 'code', 'camps_count')

    # Регионы с кемпами
    regions = Region.objects.annotate(
        camps_count=Count('camps', filter=Q(camps__is_active=True))
    ).filter(
        camps_count__gt=0
    ).select_related('country').values(
        'id', 'name', 'name_en', 'country__code', 'country__name_en', 'camps_count'
    )

    # Ценовые диапазоны
    price_stats = SurfCamp.objects.filter(is_active=True).aggregate(
        min_price=Min('price_per_night'),
        max_price=Max('price_per_night'),
        avg_price=Avg('price_per_night')
    )

    # Удобства
    amenities = Amenity.objects.all().values('id', 'name', 'name_en', 'icon', 'category')

    # Типы досок
    board_types = BoardType.objects.all().values('id', 'name', 'name_en', 'icon')

    return Response({
        'countries': list(countries),
        'regions': list(regions),
        'price_range': {
            'min': float(price_stats['min_price'] or 0),
            'max': float(price_stats['max_price'] or 500),
            'avg': float(price_stats['avg_price'] or 100)
        },
        'skill_levels': [
            {'value': 'beginner', 'label': 'Beginner'},
            {'value': 'intermediate', 'label': 'Intermediate'},
            {'value': 'advanced', 'label': 'Advanced'}
        ],
        'languages': [
            {'value': 'en', 'label': 'English', 'label_ru': 'Английский'},
            {'value': 'ru', 'label': 'Russian', 'label_ru': 'Русский'},
            {'value': 'es', 'label': 'Spanish', 'label_ru': 'Испанский'},
            {'value': 'pt', 'label': 'Portuguese', 'label_ru': 'Португальский'},
            {'value': 'fr', 'label': 'French', 'label_ru': 'Французский'},
            {'value': 'de', 'label': 'German', 'label_ru': 'Немецкий'},
        ],
        'amenities': list(amenities),
        'board_types': list(board_types),
        'features': [
            {'key': 'has_pool', 'label': 'Pool'},
            {'key': 'has_yoga', 'label': 'Yoga'},
            {'key': 'has_parties', 'label': 'Parties'},
            {'key': 'has_bed_breakfast', 'label': 'Breakfast included'},
            {'key': 'board_rental_available', 'label': 'Board rental'}
        ]
    })
