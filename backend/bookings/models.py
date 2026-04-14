from django.db import models
from django.core.validators import MinValueValidator, EmailValidator
from django.utils import timezone
import uuid


class Booking(models.Model):
    """Модель бронирования"""

    STATUS_CHOICES = [
        ('pending', 'Ожидает подтверждения'),
        ('confirmed', 'Подтверждено'),
        ('paid', 'Оплачено'),
        ('cancelled', 'Отменено'),
        ('completed', 'Завершено'),
    ]

    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Ожидает оплаты'),
        ('processing', 'В обработке'),
        ('paid', 'Оплачено'),
        ('failed', 'Ошибка оплаты'),
        ('refunded', 'Возвращено'),
    ]

    PACKAGE_CHOICES = [
        ('full', 'С уроками'),
        ('bnb', 'Только проживание (B&B)'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    booking_number = models.CharField(max_length=20, unique=True, editable=False)

    # Связь с кемпом
    camp = models.ForeignKey(
        'camps.SurfCamp',
        on_delete=models.PROTECT,
        related_name='bookings'
    )

    # Даты
    check_in = models.DateField()
    check_out = models.DateField()
    nights = models.PositiveIntegerField(editable=False)

    # Гости
    adults = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])
    children = models.PositiveIntegerField(default=0)

    # Тип пакета
    package_type = models.CharField(max_length=10, choices=PACKAGE_CHOICES, default='full')

    # Опции
    include_breakfast = models.BooleanField(default=False)
    include_lessons = models.BooleanField(default=False)
    lessons_count = models.PositiveIntegerField(default=0)
    include_board_rental = models.BooleanField(default=False)

    # Цены
    price_per_night = models.DecimalField(max_digits=10, decimal_places=2)
    breakfast_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    lessons_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    board_rental_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    service_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='USD')

    # Статусы
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')

    # Особые запросы
    special_requests = models.TextField(blank=True)
    arrival_time = models.TimeField(null=True, blank=True)

    # Метаданные
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    confirmed_at = models.DateTimeField(null=True, blank=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)
    cancellation_reason = models.TextField(blank=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['booking_number']),
            models.Index(fields=['status']),
            models.Index(fields=['check_in', 'check_out']),
        ]

    def save(self, *args, **kwargs):
        if not self.booking_number:
            self.booking_number = self.generate_booking_number()
        if self.check_in and self.check_out:
            self.nights = (self.check_out - self.check_in).days
        super().save(*args, **kwargs)

    def generate_booking_number(self):
        """Генерация номера бронирования"""
        import random
        import string
        prefix = 'SC'
        date_part = timezone.now().strftime('%y%m%d')
        random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
        return f'{prefix}{date_part}{random_part}'

    def __str__(self):
        return f'{self.booking_number} - {self.camp.name}'


class Guest(models.Model):
    """Данные гостя"""

    booking = models.ForeignKey(
        Booking,
        on_delete=models.CASCADE,
        related_name='guests'
    )

    is_primary = models.BooleanField(default=False)

    # Личные данные
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(validators=[EmailValidator()])
    phone = models.CharField(max_length=30)

    # Дополнительно для основного гостя
    country = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=100, blank=True)

    # Уровень сёрфинга
    SKILL_CHOICES = [
        ('beginner', 'Начинающий'),
        ('intermediate', 'Средний'),
        ('advanced', 'Продвинутый'),
    ]
    surf_level = models.CharField(max_length=20, choices=SKILL_CHOICES, default='beginner')

    # Экстренный контакт
    emergency_name = models.CharField(max_length=200, blank=True)
    emergency_phone = models.CharField(max_length=30, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-is_primary', 'id']

    def __str__(self):
        return f'{self.first_name} {self.last_name}'


class Payment(models.Model):
    """Платеж"""

    METHOD_CHOICES = [
        ('card', 'Банковская карта'),
        ('paypal', 'PayPal'),
        ('bank_transfer', 'Банковский перевод'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    booking = models.ForeignKey(
        Booking,
        on_delete=models.CASCADE,
        related_name='payments'
    )

    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='USD')
    method = models.CharField(max_length=20, choices=METHOD_CHOICES)

    # Данные транзакции
    transaction_id = models.CharField(max_length=100, blank=True)
    status = models.CharField(max_length=20, default='pending')

    # Данные карты (маскированные)
    card_last_four = models.CharField(max_length=4, blank=True)
    card_brand = models.CharField(max_length=20, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'Payment {self.id} - {self.amount} {self.currency}'
