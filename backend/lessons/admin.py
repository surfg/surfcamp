from django.contrib import admin
from .models import LessonProvider, SurfLesson, LessonImage, LessonReview


class LessonImageInline(admin.TabularInline):
    model = LessonImage
    extra = 1


class LessonReviewInline(admin.TabularInline):
    model = LessonReview
    extra = 0
    readonly_fields = ['created_at']


class SurfLessonInline(admin.TabularInline):
    model = SurfLesson
    extra = 0
    fields = ['name', 'lesson_type', 'skill_level', 'price', 'is_active']
    show_change_link = True


@admin.register(LessonProvider)
class LessonProviderAdmin(admin.ModelAdmin):
    list_display = ['name', 'region', 'rating', 'reviews_count', 'is_active', 'is_featured']
    list_filter = ['is_active', 'is_featured', 'region__country']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    inlines = [SurfLessonInline]


@admin.register(SurfLesson)
class SurfLessonAdmin(admin.ModelAdmin):
    list_display = ['name', 'provider', 'lesson_type', 'skill_level', 'price', 'duration_minutes', 'is_active', 'is_featured']
    list_filter = ['is_active', 'is_featured', 'lesson_type', 'skill_level', 'provider__region__country']
    search_fields = ['name', 'description', 'provider__name']
    prepopulated_fields = {'slug': ('name',)}
    inlines = [LessonImageInline, LessonReviewInline]
    fieldsets = (
        (None, {
            'fields': ('provider', 'name', 'name_ru', 'slug', 'short_description', 'short_description_ru', 'description', 'description_ru')
        }),
        ('Lesson Details', {
            'fields': ('lesson_type', 'skill_level', 'duration_minutes', 'max_participants', 'min_age')
        }),
        ('Pricing', {
            'fields': ('price', 'currency', 'price_per_person', 'is_package', 'lessons_in_package', 'package_discount_percent')
        }),
        ('Includes', {
            'fields': ('includes_equipment', 'includes_wetsuit', 'includes_transport', 'includes_photos', 'includes_video', 'includes_theory', 'includes_insurance')
        }),
        ('Media & Status', {
            'fields': ('main_image', 'rating', 'reviews_count', 'bookings_count', 'is_active', 'is_featured')
        }),
    )


@admin.register(LessonImage)
class LessonImageAdmin(admin.ModelAdmin):
    list_display = ['lesson', 'alt_text', 'is_main', 'order']
    list_filter = ['is_main']


@admin.register(LessonReview)
class LessonReviewAdmin(admin.ModelAdmin):
    list_display = ['lesson', 'author_name', 'rating', 'is_verified', 'created_at']
    list_filter = ['is_verified', 'rating']
    search_fields = ['author_name', 'text']
