from rest_framework import serializers
from .models import LessonProvider, SurfLesson, LessonImage, LessonReview


class LessonProviderSerializer(serializers.ModelSerializer):
    region_name = serializers.CharField(source='region.name', read_only=True)
    country_name = serializers.CharField(source='region.country.name', read_only=True)
    country_code = serializers.CharField(source='region.country.code', read_only=True)

    class Meta:
        model = LessonProvider
        fields = [
            'id', 'name', 'slug', 'description', 'description_ru',
            'region_name', 'country_name', 'country_code',
            'address', 'latitude', 'longitude',
            'phone', 'email', 'website', 'instagram', 'whatsapp',
            'logo', 'main_image', 'rating', 'reviews_count',
            'is_featured'
        ]


class LessonImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = LessonImage
        fields = ['id', 'image', 'alt_text', 'is_main', 'order']


class LessonReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = LessonReview
        fields = [
            'id', 'author_name', 'author_country', 'author_photo',
            'rating', 'title', 'text', 'surf_level', 'visit_date',
            'is_verified', 'created_at'
        ]


class SurfLessonListSerializer(serializers.ModelSerializer):
    """Serializer for lesson list view"""
    region_name = serializers.CharField(read_only=True)
    country_name = serializers.CharField(read_only=True)
    country_code = serializers.CharField(read_only=True)
    provider_name = serializers.CharField(source='provider.name', read_only=True)
    provider_slug = serializers.CharField(source='provider.slug', read_only=True)
    duration_hours = serializers.FloatField(read_only=True)

    class Meta:
        model = SurfLesson
        fields = [
            'id', 'name', 'name_ru', 'slug', 'short_description', 'short_description_ru',
            'provider_name', 'provider_slug',
            'region_name', 'country_name', 'country_code',
            'lesson_type', 'skill_level',
            'duration_minutes', 'duration_hours', 'max_participants', 'min_age',
            'price', 'currency', 'price_per_person',
            'is_package', 'lessons_in_package',
            'includes_equipment', 'includes_transport',
            'main_image', 'rating', 'reviews_count',
            'is_featured'
        ]


class SurfLessonDetailSerializer(serializers.ModelSerializer):
    """Serializer for lesson detail view"""
    provider = LessonProviderSerializer(read_only=True)
    images = LessonImageSerializer(many=True, read_only=True)
    reviews = LessonReviewSerializer(many=True, read_only=True)
    region_name = serializers.CharField(read_only=True)
    country_name = serializers.CharField(read_only=True)
    country_code = serializers.CharField(read_only=True)
    duration_hours = serializers.FloatField(read_only=True)

    class Meta:
        model = SurfLesson
        fields = [
            'id', 'name', 'name_ru', 'slug',
            'short_description', 'short_description_ru',
            'description', 'description_ru',
            'provider',
            'region_name', 'country_name', 'country_code',
            'lesson_type', 'skill_level',
            'duration_minutes', 'duration_hours', 'max_participants', 'min_age',
            'price', 'currency', 'price_per_person',
            'is_package', 'lessons_in_package', 'package_discount_percent',
            'includes_equipment', 'includes_wetsuit', 'includes_transport',
            'includes_photos', 'includes_video', 'includes_theory', 'includes_insurance',
            'main_image', 'images', 'reviews',
            'rating', 'reviews_count', 'bookings_count',
            'is_featured', 'created_at'
        ]
