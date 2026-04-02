from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from camps.models import Region, Country


class LessonProvider(models.Model):
    """Провайдер уроков серфинга (школа/инструктор)"""
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    description_ru = models.TextField(blank=True)

    # Location
    region = models.ForeignKey(Region, on_delete=models.CASCADE, related_name='lesson_providers')
    address = models.CharField(max_length=500, blank=True)
    latitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    longitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)

    # Contact
    phone = models.CharField(max_length=50, blank=True)
    email = models.EmailField(blank=True)
    website = models.URLField(blank=True)
    instagram = models.CharField(max_length=100, blank=True)
    whatsapp = models.CharField(max_length=50, blank=True)

    # Media
    logo = models.ImageField(upload_to='providers/logos/', null=True, blank=True)
    main_image = models.ImageField(upload_to='providers/images/', null=True, blank=True)

    # Rating
    rating = models.DecimalField(max_digits=2, decimal_places=1, default=0,
                                  validators=[MinValueValidator(0), MaxValueValidator(5)])
    reviews_count = models.PositiveIntegerField(default=0)

    # Status
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-is_featured', '-rating']

    def __str__(self):
        return self.name


class SurfLesson(models.Model):
    """Урок серфинга"""
    LESSON_TYPE_CHOICES = [
        ('private', 'Private'),
        ('group', 'Group'),
        ('semi_private', 'Semi-Private'),
    ]

    SKILL_LEVEL_CHOICES = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
        ('all', 'All Levels'),
    ]

    provider = models.ForeignKey(LessonProvider, on_delete=models.CASCADE, related_name='lessons')

    # Basic info
    name = models.CharField(max_length=200)
    name_ru = models.CharField(max_length=200, blank=True)
    slug = models.SlugField(max_length=150, unique=True)
    short_description = models.CharField(max_length=300)
    short_description_ru = models.CharField(max_length=300, blank=True)
    description = models.TextField()
    description_ru = models.TextField(blank=True)

    # Lesson details
    lesson_type = models.CharField(max_length=20, choices=LESSON_TYPE_CHOICES, default='group')
    skill_level = models.CharField(max_length=20, choices=SKILL_LEVEL_CHOICES, default='beginner')
    duration_minutes = models.PositiveIntegerField(default=120)  # Duration in minutes
    max_participants = models.PositiveIntegerField(default=6)
    min_age = models.PositiveIntegerField(default=6)

    # Pricing
    price = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='USD')
    price_per_person = models.BooleanField(default=True)  # False = price per lesson

    # Package options
    is_package = models.BooleanField(default=False)
    lessons_in_package = models.PositiveIntegerField(default=1)
    package_discount_percent = models.PositiveIntegerField(default=0)

    # What's included
    includes_equipment = models.BooleanField(default=True)
    includes_wetsuit = models.BooleanField(default=True)
    includes_transport = models.BooleanField(default=False)
    includes_photos = models.BooleanField(default=False)
    includes_video = models.BooleanField(default=False)
    includes_theory = models.BooleanField(default=True)
    includes_insurance = models.BooleanField(default=False)

    # Media
    main_image = models.ImageField(upload_to='lessons/', null=True, blank=True)

    # Rating
    rating = models.DecimalField(max_digits=2, decimal_places=1, default=0,
                                  validators=[MinValueValidator(0), MaxValueValidator(5)])
    reviews_count = models.PositiveIntegerField(default=0)
    bookings_count = models.PositiveIntegerField(default=0)

    # Status
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-is_featured', '-rating', 'price']

    def __str__(self):
        return f"{self.name} - {self.provider.name}"

    @property
    def region_name(self):
        return self.provider.region.name

    @property
    def country_name(self):
        return self.provider.region.country.name

    @property
    def country_code(self):
        return self.provider.region.country.code

    @property
    def duration_hours(self):
        return self.duration_minutes / 60


class LessonImage(models.Model):
    """Изображения урока"""
    lesson = models.ForeignKey(SurfLesson, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='lessons/')
    alt_text = models.CharField(max_length=200, blank=True)
    is_main = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['-is_main', 'order']

    def __str__(self):
        return f"Image for {self.lesson.name}"


class LessonReview(models.Model):
    """Отзывы об уроках"""
    lesson = models.ForeignKey(SurfLesson, on_delete=models.CASCADE, related_name='reviews')
    author_name = models.CharField(max_length=100)
    author_country = models.CharField(max_length=100, blank=True)
    author_photo = models.ImageField(upload_to='reviews/', null=True, blank=True)
    rating = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    title = models.CharField(max_length=200, blank=True)
    text = models.TextField()
    surf_level = models.CharField(max_length=20, blank=True)
    visit_date = models.DateField(null=True, blank=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Review by {self.author_name} for {self.lesson.name}"
