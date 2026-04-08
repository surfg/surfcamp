from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class Country(models.Model):
    """Страна с серф-кемпами"""
    name = models.CharField(max_length=100, verbose_name="Название")
    name_en = models.CharField(max_length=100, verbose_name="Название (EN)")
    code = models.CharField(max_length=3, unique=True, verbose_name="Код страны")
    image = models.ImageField(upload_to='countries/', blank=True, null=True, verbose_name="Изображение")
    description = models.TextField(blank=True, verbose_name="Описание")
    is_active = models.BooleanField(default=True, verbose_name="Активна")

    class Meta:
        verbose_name = "Страна"
        verbose_name_plural = "Страны"
        ordering = ['name']

    def __str__(self):
        return self.name


class Region(models.Model):
    """Регион внутри страны"""
    country = models.ForeignKey(Country, on_delete=models.CASCADE, related_name='regions', verbose_name="Страна")
    name = models.CharField(max_length=100, verbose_name="Название")
    name_en = models.CharField(max_length=100, verbose_name="Название (EN)")
    description = models.TextField(blank=True, verbose_name="Описание")
    latitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True, verbose_name="Широта")
    longitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True, verbose_name="Долгота")

    class Meta:
        verbose_name = "Регион"
        verbose_name_plural = "Регионы"
        ordering = ['country', 'name']

    def __str__(self):
        return f"{self.name}, {self.country.name}"


class SurfLevel(models.TextChoices):
    BEGINNER = 'beginner', 'Beginner'
    INTERMEDIATE = 'intermediate', 'Intermediate'
    ADVANCED = 'advanced', 'Advanced'


class BoardType(models.Model):
    """Тип серф-доски"""
    name = models.CharField(max_length=50, verbose_name="Название")
    name_en = models.CharField(max_length=50, verbose_name="Название (EN)")
    icon = models.CharField(max_length=50, blank=True, verbose_name="Иконка (CSS класс)")
    description = models.TextField(blank=True, verbose_name="Описание")

    class Meta:
        verbose_name = "Тип доски"
        verbose_name_plural = "Типы досок"

    def __str__(self):
        return self.name_en


class Amenity(models.Model):
    """Удобства кемпа"""
    name = models.CharField(max_length=100, verbose_name="Название")
    name_en = models.CharField(max_length=100, verbose_name="Название (EN)")
    icon = models.CharField(max_length=50, blank=True, verbose_name="Иконка (CSS класс)")
    category = models.CharField(max_length=50, choices=[
        ('accommodation', 'Проживание'),
        ('food', 'Питание'),
        ('surf', 'Серфинг'),
        ('activities', 'Активности'),
        ('services', 'Сервисы'),
    ], default='services', verbose_name="Категория")

    class Meta:
        verbose_name = "Удобство"
        verbose_name_plural = "Удобства"
        ordering = ['category', 'name']

    def __str__(self):
        return self.name_en


class SurfCamp(models.Model):
    """Серф-кемп"""
    # Основная информация
    name = models.CharField(max_length=200, verbose_name="Название")
    slug = models.SlugField(max_length=200, unique=True, verbose_name="URL")
    region = models.ForeignKey(Region, on_delete=models.CASCADE, related_name='camps', verbose_name="Регион")

    # Описание
    short_description = models.CharField(max_length=300, verbose_name="Краткое описание")
    description = models.TextField(verbose_name="Полное описание")
    history = models.TextField(blank=True, verbose_name="История школы")

    # Геолокация
    address = models.CharField(max_length=300, verbose_name="Адрес")
    latitude = models.DecimalField(max_digits=10, decimal_places=7, verbose_name="Широта")
    longitude = models.DecimalField(max_digits=10, decimal_places=7, verbose_name="Долгота")

    # Цены
    price_per_night = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена за ночь (USD)")
    price_per_lesson = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Цена за урок (USD)")
    has_bed_breakfast = models.BooleanField(default=False, verbose_name="Bed & Breakfast (без уроков)")
    bed_breakfast_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Цена B&B за ночь (USD)")

    # Уровни серфинга
    skill_levels = models.JSONField(default=list, verbose_name="Уровни серфинга")  # ['beginner', 'intermediate', 'advanced']

    # Доски
    board_types = models.ManyToManyField(BoardType, blank=True, related_name='camps', verbose_name="Типы досок")
    board_rental_available = models.BooleanField(default=True, verbose_name="Аренда досок")
    board_rental_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Цена аренды доски/день (USD)")

    # Удобства
    amenities = models.ManyToManyField(Amenity, blank=True, related_name='camps', verbose_name="Удобства")
    has_pool = models.BooleanField(default=False, verbose_name="Бассейн")
    has_restaurant = models.BooleanField(default=False, verbose_name="Ресторан")
    has_yoga = models.BooleanField(default=False, verbose_name="Йога")
    has_parties = models.BooleanField(default=False, verbose_name="Вечеринки")

    # Контакты
    website = models.URLField(blank=True, verbose_name="Сайт")
    email = models.EmailField(blank=True, verbose_name="Email")
    phone = models.CharField(max_length=30, blank=True, verbose_name="Телефон")
    instagram = models.CharField(max_length=100, blank=True, verbose_name="Instagram")
    whatsapp = models.CharField(max_length=30, blank=True, verbose_name="WhatsApp")

    # Рейтинг
    rating = models.DecimalField(
        max_digits=3, decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(5)],
        default=0, verbose_name="Рейтинг"
    )
    reviews_count = models.PositiveIntegerField(default=0, verbose_name="Количество отзывов")

    # Скидки
    discount_percent = models.PositiveIntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(90)],
        verbose_name="Скидка (%)"
    )
    discount_ends_at = models.DateTimeField(
        null=True, blank=True,
        verbose_name="Скидка действует до"
    )
    discount_description = models.CharField(
        max_length=200, blank=True,
        verbose_name="Описание скидки"
    )

    # Мета
    is_featured = models.BooleanField(default=False, verbose_name="Рекомендуемый")
    is_active = models.BooleanField(default=True, verbose_name="Активен")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Серф-кемп"
        verbose_name_plural = "Серф-кемпы"
        ordering = ['-is_featured', '-rating']

    def __str__(self):
        return self.name

    @property
    def country(self):
        return self.region.country

    @property
    def main_image(self):
        img = self.images.filter(is_main=True).first()
        if not img:
            img = self.images.first()
        return img


class CampImage(models.Model):
    """Изображение кемпа"""
    camp = models.ForeignKey(SurfCamp, on_delete=models.CASCADE, related_name='images', verbose_name="Кемп")
    image = models.ImageField(upload_to='camps/', verbose_name="Изображение")
    alt_text = models.CharField(max_length=200, blank=True, verbose_name="Alt текст")
    is_main = models.BooleanField(default=False, verbose_name="Главное изображение")
    order = models.PositiveIntegerField(default=0, verbose_name="Порядок")

    class Meta:
        verbose_name = "Изображение кемпа"
        verbose_name_plural = "Изображения кемпов"
        ordering = ['order', '-is_main']

    def save(self, *args, **kwargs):
        if self.is_main:
            CampImage.objects.filter(camp=self.camp, is_main=True).update(is_main=False)
        super().save(*args, **kwargs)


class Instructor(models.Model):
    """Инструктор"""
    camp = models.ForeignKey(SurfCamp, on_delete=models.CASCADE, related_name='instructors', verbose_name="Кемп")
    name = models.CharField(max_length=100, verbose_name="Имя")
    photo = models.ImageField(upload_to='instructors/', blank=True, null=True, verbose_name="Фото")
    bio = models.TextField(blank=True, verbose_name="Биография")
    experience_years = models.PositiveIntegerField(default=0, verbose_name="Опыт (лет)")
    certifications = models.CharField(max_length=300, blank=True, verbose_name="Сертификаты")
    languages = models.CharField(max_length=200, blank=True, verbose_name="Языки")
    is_head_coach = models.BooleanField(default=False, verbose_name="Главный тренер")

    class Meta:
        verbose_name = "Инструктор"
        verbose_name_plural = "Инструкторы"
        ordering = ['-is_head_coach', 'name']

    def __str__(self):
        return f"{self.name} ({self.camp.name})"


class Activity(models.Model):
    """Дополнительная активность"""
    camp = models.ForeignKey(SurfCamp, on_delete=models.CASCADE, related_name='activities', verbose_name="Кемп")
    name = models.CharField(max_length=100, verbose_name="Название")
    name_en = models.CharField(max_length=100, verbose_name="Название (EN)")
    description = models.TextField(blank=True, verbose_name="Описание")
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Цена (USD)")
    is_included = models.BooleanField(default=False, verbose_name="Включено в стоимость")
    image = models.ImageField(upload_to='activities/', blank=True, null=True, verbose_name="Изображение")

    class Meta:
        verbose_name = "Активность"
        verbose_name_plural = "Активности"

    def __str__(self):
        return f"{self.name_en} - {self.camp.name}"


class Review(models.Model):
    """Отзыв о кемпе"""
    camp = models.ForeignKey(SurfCamp, on_delete=models.CASCADE, related_name='reviews', verbose_name="Кемп")
    author_name = models.CharField(max_length=100, verbose_name="Имя автора")
    author_country = models.CharField(max_length=100, blank=True, verbose_name="Страна автора")
    author_photo = models.ImageField(upload_to='reviews/', blank=True, null=True, verbose_name="Фото автора")

    rating = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name="Оценка"
    )
    title = models.CharField(max_length=200, blank=True, verbose_name="Заголовок")
    text = models.TextField(verbose_name="Текст отзыва")

    surf_level = models.CharField(max_length=20, choices=SurfLevel.choices, blank=True, verbose_name="Уровень серфинга")
    visit_date = models.DateField(null=True, blank=True, verbose_name="Дата визита")

    is_verified = models.BooleanField(default=False, verbose_name="Проверен")
    is_published = models.BooleanField(default=True, verbose_name="Опубликован")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Отзыв"
        verbose_name_plural = "Отзывы"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.author_name} - {self.camp.name} ({self.rating})"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Обновляем рейтинг кемпа
        camp = self.camp
        reviews = camp.reviews.filter(is_published=True)
        if reviews.exists():
            avg_rating = reviews.aggregate(models.Avg('rating'))['rating__avg']
            camp.rating = round(avg_rating, 2)
            camp.reviews_count = reviews.count()
            camp.save(update_fields=['rating', 'reviews_count'])
