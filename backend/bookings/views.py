from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from .models import Booking, Guest, Payment
from .serializers import (
    BookingCreateSerializer, BookingDetailSerializer, BookingListSerializer,
    AddGuestSerializer, ProcessPaymentSerializer, GuestSerializer
)
import uuid


class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.select_related('camp').prefetch_related('guests', 'payments')
    lookup_field = 'booking_number'

    def get_serializer_class(self):
        if self.action == 'create':
            return BookingCreateSerializer
        if self.action == 'list':
            return BookingListSerializer
        return BookingDetailSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        # В реальном приложении здесь была бы фильтрация по пользователю
        return queryset

    def create(self, request, *args, **kwargs):
        """Override create to return detailed booking data"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        booking = serializer.save()
        # Return detailed booking data
        response_serializer = BookingDetailSerializer(booking)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def add_guest(self, request, booking_number=None):
        """Добавить гостя к бронированию"""
        booking = self.get_object()
        serializer = AddGuestSerializer(data=request.data)
        if serializer.is_valid():
            is_primary = not booking.guests.exists()
            guest = Guest.objects.create(
                booking=booking,
                is_primary=is_primary,
                **serializer.validated_data
            )
            return Response(GuestSerializer(guest).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['put'])
    def update_guests(self, request, booking_number=None):
        """Обновить всех гостей"""
        booking = self.get_object()
        guests_data = request.data.get('guests', [])

        # Удаляем старых гостей
        booking.guests.all().delete()

        # Создаём новых
        for i, guest_data in enumerate(guests_data):
            # Remove is_primary from guest_data as we set it based on index
            guest_data_copy = {k: v for k, v in guest_data.items() if k != 'is_primary'}
            Guest.objects.create(
                booking=booking,
                is_primary=(i == 0),
                **guest_data_copy
            )

        return Response(BookingDetailSerializer(booking).data)

    @action(detail=True, methods=['post'])
    def process_payment(self, request, booking_number=None):
        """Обработать платёж (мок)"""
        booking = self.get_object()
        serializer = ProcessPaymentSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data

        # Создаём платёж (мок - всегда успешный)
        payment = Payment.objects.create(
            booking=booking,
            amount=booking.total_price,
            currency=booking.currency,
            method=data['method'],
            transaction_id=f'TXN{uuid.uuid4().hex[:12].upper()}',
            status='completed',
            card_last_four=data.get('card_number', '')[-4:] if data.get('card_number') else '',
            card_brand=self._detect_card_brand(data.get('card_number', '')),
            completed_at=timezone.now()
        )

        # Обновляем статус бронирования
        booking.payment_status = 'paid'
        booking.status = 'confirmed'
        booking.paid_at = timezone.now()
        booking.confirmed_at = timezone.now()
        booking.save()

        return Response({
            'success': True,
            'payment_id': str(payment.id),
            'transaction_id': payment.transaction_id,
            'booking': BookingDetailSerializer(booking).data
        })

    @action(detail=True, methods=['post'])
    def cancel(self, request, booking_number=None):
        """Отменить бронирование"""
        booking = self.get_object()
        reason = request.data.get('reason', '')

        if booking.status in ['cancelled', 'completed']:
            return Response(
                {'error': 'Cannot cancel this booking'},
                status=status.HTTP_400_BAD_REQUEST
            )

        booking.status = 'cancelled'
        booking.cancelled_at = timezone.now()
        booking.cancellation_reason = reason
        booking.save()

        return Response(BookingDetailSerializer(booking).data)

    @action(detail=True, methods=['get'])
    def price_breakdown(self, request, booking_number=None):
        """Получить детализацию цены"""
        booking = self.get_object()
        return Response({
            'nights': booking.nights,
            'price_per_night': float(booking.price_per_night),
            'accommodation_total': float(booking.price_per_night * booking.nights),
            'breakfast_total': float(booking.breakfast_total),
            'lessons_total': float(booking.lessons_total),
            'board_rental_total': float(booking.board_rental_total),
            'subtotal': float(booking.subtotal),
            'service_fee': float(booking.service_fee),
            'total_price': float(booking.total_price),
            'currency': booking.currency
        })

    def _detect_card_brand(self, card_number):
        """Определить тип карты по номеру"""
        if not card_number:
            return ''
        number = card_number.replace(' ', '').replace('-', '')
        if number.startswith('4'):
            return 'Visa'
        if number.startswith(('51', '52', '53', '54', '55')):
            return 'Mastercard'
        if number.startswith(('34', '37')):
            return 'Amex'
        return 'Card'
