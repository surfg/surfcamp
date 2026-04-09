import os
from rest_framework import serializers
from .models import (
    Country, Region, BoardType, Amenity, SurfCamp,
    CampImage, Instructor, Activity, Review
)


def get_optimized_image_url(original_path, size='thumb'):
    """
    Convert original image path to optimized WebP path
    Example: camps/foo/img_00_abc.jpg -> optimized/camps/foo/img_00_abc_thumb.webp
    """
    if not original_path:
        return None

    # Parse path
    path_str = str(original_path)
    dir_name = os.path.dirname(path_str)  # camps/camp-slug
    base_name = os.path.basename(path_str)  # img_00_hash.jpg
    name_without_ext = os.path.splitext(base_name)[0]  # img_00_hash

    # Build optimized path
    optimized_path = f"optimized/{dir_name}/{name_without_ext}_{size}.webp"
    return optimized_path


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
    """Serializer with optimized image sizes"""
    thumb = serializers.SerializerMethodField()
    medium = serializers.SerializerMethodField()
    large = serializers.SerializerMethodField()

    class Meta:
        model = CampImage
        fields = ['id', 'image', 'thumb', 'medium', 'large', 'alt_text', 'is_main', 'order']

    def _get_optimized_url(self, obj, size):
        """Get optimized image URL for given size"""
        if not obj.image:
            return None
        request = self.context.get('request')
        optimized_path = get_optimized_image_url(obj.image.name, size)
        if request:
            return request.build_absolute_uri(f'/media/{optimized_path}')
        return f'/media/{optimized_path}'

    def get_thumb(self, obj):
        return self._get_optimized_url(obj, 'thumb')

    def get_medium(self, obj):
        return self._get_optimized_url(obj, 'medium')

    def get_large(self, obj):
        return self._get_optimized_url(obj, 'large')


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
    discount_active = serializers.SerializerMethodField()

    class Meta:
        model = SurfCamp
        fields = [
            'id', 'name', 'slug', 'short_description',
            'region_name', 'country_name', 'country_code',
            'latitude', 'longitude',
            'price_per_night', 'has_bed_breakfast', 'bed_breakfast_price',
            'skill_levels', 'teaching_languages',
            'rating', 'reviews_count',
            'has_pool', 'has_yoga', 'is_featured', 'main_image',
            'discount_percent', 'discount_ends_at', 'discount_description', 'discount_active'
        ]

    def get_discount_active(self, obj):
        """Check if discount is currently active"""
        from django.utils import timezone
        if obj.discount_percent and obj.discount_percent > 0:
            if obj.discount_ends_at:
                return obj.discount_ends_at > timezone.now()
            return True  # No end date = always active
        return False

    def get_main_image(self, obj):
        """Return optimized thumb version for list cards"""
        main_img = obj.main_image
        if main_img and main_img.image:
            request = self.context.get('request')
            # Use optimized thumb for list view (faster loading)
            optimized_path = get_optimized_image_url(main_img.image.name, 'thumb')
            if request:
                return request.build_absolute_uri(f'/media/{optimized_path}')
            return f'/media/{optimized_path}'
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
            'skill_levels', 'teaching_languages',
            'board_types', 'board_rental_available', 'board_rental_price',
            'amenities', 'has_pool', 'has_restaurant', 'has_yoga', 'has_parties',
            'website', 'email', 'phone', 'instagram', 'whatsapp',
            'rating', 'reviews_count', 'is_featured',
            'discount_percent', 'discount_ends_at', 'discount_description',
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
