from rest_framework import serializers
from .models import (
    Country, Region, BoardType, Amenity, SurfCamp,
    CampImage, Instructor, Activity, Review
)


class CountrySerializer(serializers.ModelSerializer):
    camps_count = serializers.SerializerMethodField()

    class Meta:
        model = Country
        fields = ['id', 'name', 'name_en', 'code', 'image', 'description', 'camps_count']

    def get_camps_count(self, obj):
        return SurfCamp.objects.filter(region__country=obj, is_active=True).count()


class RegionSerializer(serializers.ModelSerializer):
    country_name = serializers.CharField(source='country.name_en', read_only=True)
    camps_count = serializers.SerializerMethodField()

    class Meta:
        model = Region
        fields = ['id', 'name', 'name_en', 'country', 'country_name', 'latitude', 'longitude', 'camps_count']

    def get_camps_count(self, obj):
        return obj.camps.filter(is_active=True).count()


class BoardTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = BoardType
        fields = ['id', 'name', 'name_en', 'icon', 'description']


class AmenitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Amenity
        fields = ['id', 'name', 'name_en', 'icon', 'category']


class CampImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = CampImage
        fields = ['id', 'image', 'alt_text', 'is_main', 'order']


class InstructorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Instructor
        fields = [
            'id', 'name', 'photo', 'bio', 'experience_years',
            'certifications', 'languages', 'is_head_coach'
        ]


class ActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Activity
        fields = ['id', 'name', 'name_en', 'description', 'price', 'is_included', 'image']


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = [
            'id', 'author_name', 'author_country', 'author_photo',
            'rating', 'title', 'text', 'surf_level', 'visit_date',
            'is_verified', 'created_at'
        ]


class SurfCampListSerializer(serializers.ModelSerializer):
    """Сериализатор для списка кемпов (карточки)"""
    region_name = serializers.CharField(source='region.name_en', read_only=True)
    country_name = serializers.CharField(source='region.country.name_en', read_only=True)
    country_code = serializers.CharField(source='region.country.code', read_only=True)
    main_image = serializers.SerializerMethodField()

    class Meta:
        model = SurfCamp
        fields = [
            'id', 'name', 'slug', 'short_description',
            'region_name', 'country_name', 'country_code',
            'latitude', 'longitude',
            'price_per_night', 'has_bed_breakfast', 'bed_breakfast_price',
            'skill_levels', 'rating', 'reviews_count',
            'has_pool', 'has_yoga', 'is_featured', 'main_image'
        ]

    def get_main_image(self, obj):
        main_img = obj.main_image
        if main_img:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(main_img.image.url)
            return main_img.image.url
        return None


class SurfCampDetailSerializer(serializers.ModelSerializer):
    """Полный сериализатор для детальной страницы"""
    region = RegionSerializer(read_only=True)
    country = serializers.SerializerMethodField()
    board_types = BoardTypeSerializer(many=True, read_only=True)
    amenities = AmenitySerializer(many=True, read_only=True)
    images = CampImageSerializer(many=True, read_only=True)
    instructors = InstructorSerializer(many=True, read_only=True)
    activities = ActivitySerializer(many=True, read_only=True)
    reviews = serializers.SerializerMethodField()
    spots = serializers.SerializerMethodField()

    class Meta:
        model = SurfCamp
        fields = [
            'id', 'name', 'slug', 'region', 'country',
            'short_description', 'description', 'history',
            'address', 'latitude', 'longitude',
            'price_per_night', 'price_per_lesson',
            'has_bed_breakfast', 'bed_breakfast_price',
            'skill_levels', 'board_types', 'board_rental_available', 'board_rental_price',
            'amenities', 'has_pool', 'has_restaurant', 'has_yoga', 'has_parties',
            'website', 'email', 'phone', 'instagram', 'whatsapp',
            'rating', 'reviews_count', 'is_featured',
            'images', 'instructors', 'activities', 'reviews', 'spots',
            'created_at', 'updated_at'
        ]

    def get_country(self, obj):
        return {
            'id': obj.region.country.id,
            'name': obj.region.country.name,
            'name_en': obj.region.country.name_en,
            'code': obj.region.country.code
        }

    def get_reviews(self, obj):
        reviews = obj.reviews.filter(is_published=True)[:10]
        return ReviewSerializer(reviews, many=True).data

    def get_spots(self, obj):
        from spots.serializers import SurfSpotListSerializer
        return SurfSpotListSerializer(obj.spots.filter(is_active=True), many=True, context=self.context).data
