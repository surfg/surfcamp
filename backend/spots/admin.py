from django.contrib import admin
from django.utils.html import format_html
from .models import SurfSpot, SpotImage


class SpotImageInline(admin.TabularInline):
    model = SpotImage
    extra = 1
    fields = ['image', 'alt_text', 'is_main', 'order', 'image_preview']
    readonly_fields = ['image_preview']

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-height: 60px;"/>', obj.image.url)
        return '-'
    image_preview.short_description = 'Превью'


@admin.register(SurfSpot)
class SurfSpotAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'region', 'wave_type', 'wave_direction',
        'crowd_level', 'rating', 'is_active', 'image_preview'
    ]
    list_filter = [
        'is_active', 'region__country', 'wave_type',
        'wave_direction', 'crowd_level'
    ]
    search_fields = ['name', 'description']
    list_editable = ['is_active']
    prepopulated_fields = {'slug': ('name',)}
    filter_horizontal = ['camps']

    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'slug', 'region', 'camps', 'description', 'short_description')
        }),
        ('Геолокация', {
            'fields': (('latitude', 'longitude'),)
        }),
        ('Характеристики волны', {
            'fields': (
                ('wave_direction', 'wave_type'),
                ('wave_height_min', 'wave_height_max')
            )
        }),
        ('Условия', {
            'fields': (
                'skill_levels',
                ('best_tide', 'best_swell'),
                ('best_wind', 'best_season'),
                'crowd_level'
            )
        }),
        ('Опасности', {
            'fields': (
                'hazards',
                ('has_rocks', 'has_reef', 'has_currents', 'has_sharks')
            )
        }),
        ('Инфраструктура', {
            'fields': (
                ('has_parking', 'has_showers', 'has_rentals'),
                ('has_cafe', 'has_lifeguard')
            )
        }),
        ('Рейтинг и статус', {
            'fields': ('rating', 'is_active')
        }),
    )

    inlines = [SpotImageInline]

    def image_preview(self, obj):
        main_image = obj.main_image
        if main_image:
            return format_html('<img src="{}" style="max-height: 40px; border-radius: 4px;"/>', main_image.image.url)
        return '-'
    image_preview.short_description = 'Фото'


@admin.register(SpotImage)
class SpotImageAdmin(admin.ModelAdmin):
    list_display = ['spot', 'image_preview', 'alt_text', 'is_main', 'order']
    list_filter = ['spot', 'is_main']
    list_editable = ['is_main', 'order']

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-height: 60px;"/>', obj.image.url)
        return '-'
    image_preview.short_description = 'Превью'
