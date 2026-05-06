from django import forms
from django.contrib import admin
from django.utils.html import format_html
from .models import (
    Country, Region, BoardType, Amenity, SurfCamp,
    CampImage, Instructor, Activity, Review
)


TEACHING_LANGUAGE_CHOICES = [
    ('en', 'English / Английский'),
    ('ru', 'Russian / Русский'),
    ('es', 'Spanish / Испанский'),
    ('pt', 'Portuguese / Португальский'),
    ('fr', 'French / Французский'),
    ('de', 'German / Немецкий'),
    ('it', 'Italian / Итальянский'),
]

SKILL_LEVEL_CHOICES = [
    ('beginner', 'Beginner / Начинающий'),
    ('intermediate', 'Intermediate / Средний'),
    ('advanced', 'Advanced / Продвинутый'),
]


class SurfCampAdminForm(forms.ModelForm):
    teaching_languages = forms.MultipleChoiceField(
        choices=TEACHING_LANGUAGE_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label='Языки обучения',
        help_text='Языки, на которых проводятся занятия в кемпе'
    )
    skill_levels = forms.MultipleChoiceField(
        choices=SKILL_LEVEL_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label='Уровни серфинга',
    )

    class Meta:
        model = SurfCamp
        fields = '__all__'

    def clean_teaching_languages(self):
        return list(self.cleaned_data.get('teaching_languages') or [])

    def clean_skill_levels(self):
        return list(self.cleaned_data.get('skill_levels') or [])


@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ['name', 'name_en', 'code', 'slug', 'is_active', 'camps_count']
    list_filter = ['is_active']
    search_fields = ['name', 'name_en', 'code', 'slug']
    list_editable = ['is_active']
    prepopulated_fields = {'slug': ('name_en',)}

    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'name_en', 'code', 'slug', 'image', 'description', 'is_active')
        }),
        ('SEO / Лендинг', {
            'fields': ('landing_h1', 'landing_intro', 'landing_faq', 'seo_title', 'seo_description'),
            'classes': ('collapse',),
            'description': 'Заполните для гео-лендинга по /<slug>. landing_faq — JSON вида [{"q":"...","a":"..."}].'
        }),
    )

    def camps_count(self, obj):
        return SurfCamp.objects.filter(region__country=obj).count()
    camps_count.short_description = 'Кемпов'


@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    list_display = ['name', 'country', 'camps_count']
    list_filter = ['country']
    search_fields = ['name', 'name_en']

    def camps_count(self, obj):
        return obj.camps.count()
    camps_count.short_description = 'Кемпов'


@admin.register(BoardType)
class BoardTypeAdmin(admin.ModelAdmin):
    list_display = ['name_en', 'name', 'icon']
    search_fields = ['name', 'name_en']


@admin.register(Amenity)
class AmenityAdmin(admin.ModelAdmin):
    list_display = ['name_en', 'name', 'category', 'icon']
    list_filter = ['category']
    search_fields = ['name', 'name_en']


class CampImageInline(admin.TabularInline):
    model = CampImage
    extra = 1
    fields = ['image', 'alt_text', 'is_main', 'order', 'image_preview']
    readonly_fields = ['image_preview']

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-height: 60px;"/>', obj.image.url)
        return '-'
    image_preview.short_description = 'Превью'


class InstructorInline(admin.TabularInline):
    model = Instructor
    extra = 0
    fields = ['name', 'photo', 'experience_years', 'languages', 'is_head_coach']


class ActivityInline(admin.TabularInline):
    model = Activity
    extra = 0
    fields = ['name_en', 'name', 'price', 'is_included']


class ReviewInline(admin.TabularInline):
    model = Review
    extra = 0
    fields = ['author_name', 'rating', 'title', 'is_verified', 'is_published', 'created_at']
    readonly_fields = ['created_at']


@admin.register(SurfCamp)
class SurfCampAdmin(admin.ModelAdmin):
    form = SurfCampAdminForm
    list_display = [
        'name', 'region', 'price_per_night', 'teaching_languages_badge', 'discount_badge',
        'rating', 'reviews_count', 'is_featured', 'is_active', 'image_preview'
    ]
    list_filter = ['is_active', 'is_featured', 'region__country', 'has_pool', 'has_yoga', 'has_parties', 'discount_percent']
    search_fields = ['name', 'slug', 'short_description', 'address', 'region__name', 'region__country__name']
    list_editable = ['is_featured', 'is_active']
    prepopulated_fields = {'slug': ('name',)}
    filter_horizontal = ['board_types', 'amenities']
    actions = ['set_24h_discount', 'clear_discount']

    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'slug', 'region', 'short_description', 'description', 'history')
        }),
        ('Геолокация', {
            'fields': ('address', ('latitude', 'longitude'))
        }),
        ('Цены', {
            'fields': (
                'price_per_night', 'price_per_lesson',
                ('has_bed_breakfast', 'bed_breakfast_price')
            )
        }),
        ('Скидки', {
            'fields': (
                ('discount_percent', 'discount_ends_at'),
                'discount_description'
            ),
            'classes': ('collapse',),
            'description': 'Настройте скидку с таймером. Скидка автоматически истечёт в указанное время.'
        }),
        ('Серфинг', {
            'fields': (
                'skill_levels', 'teaching_languages', 'board_types',
                ('board_rental_available', 'board_rental_price')
            ),
            'description': 'Уровни серфинга и языки преподавания используются в фильтрах на сайте.'
        }),
        ('Удобства', {
            'fields': (
                'amenities',
                ('has_pool', 'has_restaurant', 'has_yoga', 'has_parties')
            )
        }),
        ('Контакты', {
            'fields': ('website', 'email', 'phone', 'instagram', 'whatsapp')
        }),
        ('Рейтинг и статус', {
            'fields': (('rating', 'reviews_count'), ('is_featured', 'is_active'))
        }),
    )

    def teaching_languages_badge(self, obj):
        langs = obj.teaching_languages or []
        if not langs:
            return format_html('<span style="color: #dc2626; font-weight: 600;">— не задано</span>')
        return ', '.join(str(l).upper() for l in langs)
    teaching_languages_badge.short_description = 'Языки'

    def discount_badge(self, obj):
        if obj.discount_percent and obj.discount_percent > 0:
            from django.utils import timezone
            if obj.discount_ends_at and obj.discount_ends_at > timezone.now():
                time_left = obj.discount_ends_at - timezone.now()
                hours = int(time_left.total_seconds() // 3600)
                return format_html(
                    '<span style="background: #dc2626; color: white; padding: 2px 8px; border-radius: 10px; font-size: 11px;">'
                    '-{}% ({}h left)</span>',
                    obj.discount_percent, hours
                )
            elif not obj.discount_ends_at:
                return format_html(
                    '<span style="background: #f59e0b; color: white; padding: 2px 8px; border-radius: 10px; font-size: 11px;">'
                    '-{}%</span>',
                    obj.discount_percent
                )
        return '-'
    discount_badge.short_description = 'Скидка'

    @admin.action(description='Установить скидку 15%% на 24 часа')
    def set_24h_discount(self, request, queryset):
        from django.utils import timezone
        from datetime import timedelta
        count = queryset.update(
            discount_percent=15,
            discount_ends_at=timezone.now() + timedelta(hours=24),
            discount_description='Flash Sale - 24 hours only!'
        )
        self.message_user(request, f'Скидка 15% установлена для {count} кемпов на 24 часа.')

    @admin.action(description='Убрать скидку')
    def clear_discount(self, request, queryset):
        count = queryset.update(
            discount_percent=0,
            discount_ends_at=None,
            discount_description=''
        )
        self.message_user(request, f'Скидка убрана для {count} кемпов.')

    inlines = [CampImageInline, InstructorInline, ActivityInline, ReviewInline]

    def image_preview(self, obj):
        main_image = obj.main_image
        if main_image:
            return format_html('<img src="{}" style="max-height: 40px; border-radius: 4px;"/>', main_image.image.url)
        return '-'
    image_preview.short_description = 'Фото'


@admin.register(CampImage)
class CampImageAdmin(admin.ModelAdmin):
    list_display = ['camp', 'image_preview', 'alt_text', 'is_main', 'order']
    list_filter = ['camp', 'is_main']
    list_editable = ['is_main', 'order']

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-height: 60px;"/>', obj.image.url)
        return '-'
    image_preview.short_description = 'Превью'


@admin.register(Instructor)
class InstructorAdmin(admin.ModelAdmin):
    list_display = ['name', 'camp', 'experience_years', 'languages', 'is_head_coach']
    list_filter = ['camp', 'is_head_coach']
    search_fields = ['name', 'bio']


@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = ['name_en', 'camp', 'price', 'is_included']
    list_filter = ['camp', 'is_included']
    search_fields = ['name', 'name_en']


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['author_name', 'camp', 'rating', 'is_verified', 'is_published', 'created_at']
    list_filter = ['is_verified', 'is_published', 'rating', 'camp']
    search_fields = ['author_name', 'title', 'text']
    list_editable = ['is_verified', 'is_published']
    date_hierarchy = 'created_at'


# Настройка админ-сайта
admin.site.site_header = 'SurfCamp Admin'
admin.site.site_title = 'SurfCamp'
admin.site.index_title = 'Управление серф-кемпами'
