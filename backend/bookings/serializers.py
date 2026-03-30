from rest_framework import serializers
from decimal import Decimal
from .models import Booking, Guest, Payment


class GuestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Guest
        fields = [
            'id', 'is_primary', 'first_name', 'last_name', 'email', 'phone',
            'country', 'city', 'surf_level', 'emergency_name', 'emergency_phone'
        ]


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = [
            'id', 'amount', 'currency', 'method', 'status',
            'card_last_four', 'card_brand', 'created_at', 'completed_at'
        ]
        read_only_fields = ['id', 'status', 'created_at', 'completed_at']


class BookingCreateSerializer(serializers.ModelSerializer):
    guests = GuestSerializer(many=True, required=False)

    class Meta:
        model = Booking
        fields = [
            'camp', 'check_in', 'check_out', 'adults', 'children',
            'include_breakfast', 'include_lessons', 'lessons_count',
            'include_board_rental', 'special_requests', 'arrival_time', 'guests'
        ]

    def validate(self, data):
        if data['check_in'] >= data['check_out']:
            raise serializers.ValidationError(
                {'check_out': 'Check-out date must be after check-in date'}
            )
        return data

    def create(self, validated_data):
        guests_data = validated_data.pop('guests', [])
        camp = validated_data['camp']

        # Calculate prices
        nights = (validated_data['check_out'] - validated_data['check_in']).days
        price_per_night = camp.price_per_night
        subtotal = price_per_night * nights

        breakfast_total = 0
        if validated_data.get('include_breakfast') and camp.has_bed_breakfast:
            breakfast_total = (camp.bed_breakfast_price or 0) * nights * (
                validated_data['adults'] + validated_data.get('children', 0)
            )

        lessons_total = 0
        if validated_data.get('include_lessons') and camp.price_per_lesson:
            lessons_total = camp.price_per_lesson * validated_data.get('lessons_count', 0)

        board_rental_total = 0
        if validated_data.get('include_board_rental') and camp.board_rental_available:
            board_rental_total = (camp.board_rental_price or 0) * nights

        subtotal = subtotal + breakfast_total + lessons_total + board_rental_total
        service_fee = round(subtotal * Decimal('0.1'), 2)  # 10% service fee
        total_price = subtotal + service_fee

        booking = Booking.objects.create(
            **validated_data,
            price_per_night=price_per_night,
            breakfast_total=breakfast_total,
            lessons_total=lessons_total,
            board_rental_total=board_rental_total,
            subtotal=subtotal,
            service_fee=service_fee,
            total_price=total_price
        )

        for i, guest_data in enumerate(guests_data):
            # Remove is_primary from guest_data as we set it based on index
            guest_data_copy = {k: v for k, v in guest_data.items() if k != 'is_primary'}
            Guest.objects.create(booking=booking, is_primary=(i == 0), **guest_data_copy)

        return booking


class BookingDetailSerializer(serializers.ModelSerializer):
    guests = GuestSerializer(many=True, read_only=True)
    payments = PaymentSerializer(many=True, read_only=True)
    camp_name = serializers.CharField(source='camp.name', read_only=True)
    camp_slug = serializers.CharField(source='camp.slug', read_only=True)
    camp_image = serializers.SerializerMethodField()
    camp_address = serializers.CharField(source='camp.address', read_only=True)

    class Meta:
        model = Booking
        fields = [
            'id', 'booking_number', 'camp', 'camp_name', 'camp_slug', 'camp_image',
            'camp_address', 'check_in', 'check_out', 'nights', 'adults', 'children',
            'include_breakfast', 'include_lessons', 'lessons_count', 'include_board_rental',
            'price_per_night', 'breakfast_total', 'lessons_total', 'board_rental_total',
            'subtotal', 'service_fee', 'total_price', 'currency',
            'status', 'payment_status', 'special_requests', 'arrival_time',
            'created_at', 'guests', 'payments'
        ]

    def get_camp_image(self, obj):
        return obj.camp.main_image.url if obj.camp.main_image else None


class BookingListSerializer(serializers.ModelSerializer):
    camp_name = serializers.CharField(source='camp.name', read_only=True)
    camp_slug = serializers.CharField(source='camp.slug', read_only=True)

    class Meta:
        model = Booking
        fields = [
            'id', 'booking_number', 'camp_name', 'camp_slug',
            'check_in', 'check_out', 'nights', 'total_price', 'currency',
            'status', 'payment_status', 'created_at'
        ]


class AddGuestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Guest
        fields = [
            'first_name', 'last_name', 'email', 'phone',
            'country', 'city', 'surf_level', 'emergency_name', 'emergency_phone'
        ]


class ProcessPaymentSerializer(serializers.Serializer):
    method = serializers.ChoiceField(choices=['card', 'paypal', 'bank_transfer'])
    card_number = serializers.CharField(max_length=19, required=False)
    card_expiry = serializers.CharField(max_length=7, required=False)
    card_cvc = serializers.CharField(max_length=4, required=False)
    card_holder = serializers.CharField(max_length=100, required=False)

    def validate(self, data):
        if data['method'] == 'card':
            required_fields = ['card_number', 'card_expiry', 'card_cvc', 'card_holder']
            for field in required_fields:
                if not data.get(field):
                    raise serializers.ValidationError({field: 'This field is required for card payment'})
        return data
