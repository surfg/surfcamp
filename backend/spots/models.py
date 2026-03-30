from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from camps.models import Region, SurfCamp


class SurfSpot(models.Model):
    """Серф-спот"""
    WAVE_DIRECTION_CHOICES = [
        ('left', 'Left'),
        ('right', 'Right'),
        ('both', 'A-Frame (Both)'),
    ]

    WAVE_TYPE_CHOICES = [
        ('beach', 'Beach Break'),
        ('reef', 'Reef Break'),
        ('point', 'Point Break'),
    ]

    CROWD_LEVEL_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('very_high', 'Very High'),
    ]

    # Основная информация
    name = models.CharField(max_length=200, verbose_name="Название")
    slug = models.SlugField(max_length=200, unique=True, verbose_name="URL")
    region = models.ForeignKey(Region, on_delete=models.CASCADE, related_name='spots', verbose_name="Регион")
    camps = models.ManyToManyField(SurfCamp, blank=True, related_name='spots', verbose_name="Кемпы рядом")

    # Описание
    description = models.TextField(verbose_name="Описание")
    short_description = models.CharField(max_length=300, blank=True, verbose_name="Краткое описание")

    # Геолокация
    latitude = models.DecimalField(max_digits=10, decimal_places=7, verbose_name="Широта")
    longitude = models.DecimalField(max_digits=10, decimal_places=7, verbose_name="Долгота")

    # Характеристики волны
    wave_direction = models.CharField(max_length=10, choices=WAVE_DIRECTION_CHOICES, verbose_name="Направление волны")
    wave_type = models.CharField(max_length=10, choices=WAVE_TYPE_CHOICES, verbose_name="Тип волны")
    wave_height_min = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True, verbose_name="Мин. высота волны (м)")
    wave_height_max = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True, verbose_name="Макс. высота волны (м)")

    # Условия
    skill_levels = models.JSONField(default=list, verbose_name="Подходящие уровни")  # ['beginner', 'intermediate', 'advanced']
    best_tide = models.CharField(max_length=50, blank=True, verbose_name="Лучший прилив")
    best_swell = models.CharField(max_length=100, blank=True, verbose_name="Лучший свелл")
    best_wind = models.CharField(max_length=100, blank=True, verbose_name="Лучший ветер")
    best_season = models.CharField(max_length=100, blank=True, verbose_name="Лучший сезон")

    # Загруженность
    crowd_level = models.CharField(max_length=20, choices=CROWD_LEVEL_CHOICES, default='medium', verbose_name="Загруженность")

    # Опасности
    hazards = models.TextField(blank=True, verbose_name="Опасности")
    has_rocks = models.BooleanField(default=False, verbose_name="Камни")
    has_reef = models.BooleanField(default=False, verbose_name="Риф")
    has_currents = models.BooleanField(default=False, verbose_name="Течения")
    has_sharks = models.BooleanField(default=False, verbose_name="Акулы")

    # Инфраструктура
    has_parking = models.BooleanField(default=False, verbose_name="Парковка")
    has_showers = models.BooleanField(default=False, verbose_name="Душ")
    has_rentals = models.BooleanField(default=False, verbose_name="Прокат")
    has_cafe = models.BooleanField(default=False, verbose_name="Кафе")
    has_lifeguard = models.BooleanField(default=False, verbose_name="Спасатели")

    # Рейтинг
    rating = models.DecimalField(
        max_digits=3, decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(5)],
        default=0, verbose_name="Рейтинг"
    )

    # Мета
    is_active = models.BooleanField(default=True, verbose_name="Активен")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Серф-спот"
        verbose_name_plural = "Серф-споты"
        ordering = ['name']

    def __str__(self):
        return f"{self.name}, {self.region.name}"

    @property
    def main_image(self):
        img = self.images.filter(is_main=True).first()
        if not img:
            img = self.images.first()
        return img


class SpotImage(models.Model):
    """Изображение спота"""
    spot = models.ForeignKey(SurfSpot, on_delete=models.CASCADE, related_name='images', verbose_name="Спот")
    image = models.ImageField(upload_to='spots/', verbose_name="Изображение")
    alt_text = models.CharField(max_length=200, blank=True, verbose_name="Alt текст")
    is_main = models.BooleanField(default=False, verbose_name="Главное изображение")
    order = models.PositiveIntegerField(default=0, verbose_name="Порядок")

    class Meta:
        verbose_name = "Изображение спота"
        verbose_name_plural = "Изображения спотов"
        ordering = ['order', '-is_main']

    def save(self, *args, **kwargs):
        if self.is_main:
            SpotImage.objects.filter(spot=self.spot, is_main=True).update(is_main=False)
        super().save(*args, **kwargs)
