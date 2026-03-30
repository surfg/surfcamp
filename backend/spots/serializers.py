from rest_framework import serializers
from .models import SurfSpot, SpotImage


class SpotImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = SpotImage
        fields = ['id', 'image', 'alt_text', 'is_main', 'order']


class SurfSpotListSerializer(serializers.ModelSerializer):
    """Сериализатор для списка спотов"""
    region_name = serializers.CharField(source='region.name_en', read_only=True)
    country_name = serializers.CharField(source='region.country.name_en', read_only=True)
    main_image = serializers.SerializerMethodField()

    class Meta:
        model = SurfSpot
        fields = [
            'id', 'name', 'slug', 'short_description',
            'region_name', 'country_name',
            'latitude', 'longitude',
            'wave_type', 'wave_direction', 'skill_levels',
            'crowd_level', 'rating', 'main_image'
        ]

    def get_main_image(self, obj):
        main_img = obj.main_image
        if main_img:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(main_img.image.url)
            return main_img.image.url
        return None


class SurfSpotDetailSerializer(serializers.ModelSerializer):
    """Полный сериализатор для детальной страницы"""
    region_name = serializers.CharField(source='region.name_en', read_only=True)
    country_name = serializers.CharField(source='region.country.name_en', read_only=True)
    images = SpotImageSerializer(many=True, read_only=True)
    nearby_camps = serializers.SerializerMethodField()

    class Meta:
        model = SurfSpot
        fields = [
            'id', 'name', 'slug', 'region_name', 'country_name',
            'description', 'short_description',
            'latitude', 'longitude',
            'wave_direction', 'wave_type', 'wave_height_min', 'wave_height_max',
            'skill_levels', 'best_tide', 'best_swell', 'best_wind', 'best_season',
            'crowd_level', 'hazards',
            'has_rocks', 'has_reef', 'has_currents', 'has_sharks',
            'has_parking', 'has_showers', 'has_rentals', 'has_cafe', 'has_lifeguard',
            'rating', 'images', 'nearby_camps'
        ]

    def get_nearby_camps(self, obj):
        from camps.serializers import SurfCampListSerializer
        return SurfCampListSerializer(
            obj.camps.filter(is_active=True)[:5],
            many=True,
            context=self.context
        ).data
