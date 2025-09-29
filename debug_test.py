#!/usr/bin/env python
import os
import sys
import django

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'littlelemon.settings')
django.setup()

from datetime import timedelta
from django.utils import timezone
from django.contrib.auth.models import User
from restaurant.models import Booking, RestaurantConfig
from restaurant.serializers import BookingSerializer

# Test booking creation
print("Testing booking creation...")

# Create test user
try:
    user = User.objects.create_user('debuguser', 'debug@example.com', 'debug123')
    print(f"Created user: {user}")
except Exception as e:
    user = User.objects.get(username='debuguser')
    print(f"Using existing user: {user}")

# Create config
try:
    config = RestaurantConfig.objects.create(
        max_daily_capacity=50,
        max_time_slot_capacity=20,
        booking_advance_days=30
    )
    print(f"Created config: {config}")
except Exception as e:
    config = RestaurantConfig.objects.first()
    print(f"Using existing config: {config}")

# Test datetime
test_datetime = timezone.now() + timedelta(days=7, hours=19)
print(f"Test datetime: {test_datetime}")
print(f"Is timezone aware: {timezone.is_aware(test_datetime)}")

# Test booking data
booking_data = {
    'name': 'Debug Booking',
    'no_of_guests': 2,
    'booking_date': test_datetime,
    'user': user
}

print(f"Booking data: {booking_data}")

# Try to create booking using serializer
serializer = BookingSerializer(data=booking_data)
print(f"Serializer is valid: {serializer.is_valid()}")
if not serializer.is_valid():
    print(f"Validation errors: {serializer.errors}")
else:
    booking = serializer.save(user=user)
    print(f"Created booking: {booking}")