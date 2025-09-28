from rest_framework import serializers
from restaurant.models import Menu, Booking, RestaurantConfig
from django.contrib.auth.models import User
from django.utils import timezone
from django.db import transaction
from datetime import datetime, timedelta


class MenuSerializer(serializers.ModelSerializer):
    class Meta:
        model = Menu
        fields = '__all__'


class BookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = ['user', 'name', 'no_of_guests', 'booking_date', 'status']
        read_only_fields = ['user', 'status']
    
    def validate_booking_date(self, value):
        """Validate booking date constraints"""
        now = timezone.now()
        
        # Check if booking is for future date
        if value <= now:
            raise serializers.ValidationError("Booking must be for a future date and time.")
        
        # Check if booking is within allowed advance booking window
        config = RestaurantConfig.objects.first()
        if config:
            max_advance = now + timedelta(days=config.booking_advance_days)
            if value > max_advance:
                raise serializers.ValidationError(
                    f"Bookings can only be made up to {config.booking_advance_days} days in advance."
                )
        
        return value
    
    def validate_no_of_guests(self, value):
        """Validate number of guests"""
        if value <= 0:
            raise serializers.ValidationError("Number of guests must be at least 1.")
        
        if value > 10:
            raise serializers.ValidationError("Maximum 10 guests per booking.")
        
        return value
    
    def validate(self, data):
        """Cross-field validation with concurrency handling"""
        booking_date = data.get('booking_date')
        no_of_guests = data.get('no_of_guests')
        
        if booking_date and no_of_guests:
            # Use atomic transaction to prevent race conditions
            with transaction.atomic():
                # Get restaurant configuration
                config = RestaurantConfig.objects.select_for_update().first()
                if not config:
                    # Create default config if none exists
                    config = RestaurantConfig.objects.create()
                
                # Check daily capacity
                daily_capacity = Booking.get_daily_capacity(booking_date)
                if daily_capacity + no_of_guests > config.max_daily_capacity:
                    available = config.max_daily_capacity - daily_capacity
                    raise serializers.ValidationError({
                        'non_field_errors': [
                            f"Not enough capacity available for {booking_date.strftime('%B %d, %Y')}. "
                            f"Only {max(0, available)} spots remaining."
                        ]
                    })
                
                # Check time slot capacity (2-hour window)
                slot_capacity = Booking.get_time_slot_capacity(booking_date)
                if slot_capacity + no_of_guests > config.max_time_slot_capacity:
                    available = config.max_time_slot_capacity - slot_capacity
                    raise serializers.ValidationError({
                        'non_field_errors': [
                            f"Not enough capacity available for the {booking_date.strftime('%I:%M %p')} time slot. "
                            f"Only {max(0, available)} spots remaining."
                        ]
                    })
        
        return data
    
    def create(self, validated_data):
        """Create booking with atomic transaction"""
        with transaction.atomic():
            # Double-check capacity just before creating (prevents race conditions)
            booking_date = validated_data['booking_date']
            no_of_guests = validated_data['no_of_guests']
            
            config = RestaurantConfig.objects.select_for_update().first()
            if not config:
                config = RestaurantConfig.objects.create()
            
            # Final capacity check with database lock
            daily_capacity = Booking.get_daily_capacity(booking_date)
            slot_capacity = Booking.get_time_slot_capacity(booking_date)
            
            if daily_capacity + no_of_guests > config.max_daily_capacity:
                available = config.max_daily_capacity - daily_capacity
                raise serializers.ValidationError({
                    'non_field_errors': [
                        f"Booking failed due to concurrent reservation. "
                        f"Only {max(0, available)} spots remaining for this date."
                    ]
                })
            
            if slot_capacity + no_of_guests > config.max_time_slot_capacity:
                available = config.max_time_slot_capacity - slot_capacity
                raise serializers.ValidationError({
                    'non_field_errors': [
                        f"Booking failed due to concurrent reservation. "
                        f"Only {max(0, available)} spots remaining for this time slot."
                    ]
                })
            
            # Create the booking
            booking = Booking.objects.create(**validated_data)
            return booking


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['url', 'username', 'email', 'groups']