from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone

# Restaurant configuration
class RestaurantConfig(models.Model):
    """Restaurant configuration for capacity and booking rules"""
    max_daily_capacity = models.IntegerField(default=50, help_text="Maximum number of guests per day")
    max_time_slot_capacity = models.IntegerField(default=20, help_text="Maximum guests per 2-hour time slot")
    booking_advance_days = models.IntegerField(default=30, help_text="How many days in advance bookings are allowed")
    
    class Meta:
        verbose_name = "Restaurant Configuration"
        
    def __str__(self):
        return f"Max Capacity: {self.max_daily_capacity} guests/day"

# Create your models here.
class Booking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings', null=True, blank=True)
    name = models.CharField(max_length=255)
    no_of_guests = models.IntegerField() 
    booking_date = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    
    # Status tracking
    STATUS_CHOICES = [
        ('confirmed', 'Confirmed'),
        ('pending', 'Pending'),
        ('cancelled', 'Cancelled'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='confirmed')

    def __str__(self):
        return f"{self.name} - {self.booking_date} ({self.no_of_guests} guests)"

    class Meta:
        ordering = ['-booking_date']
        # Prevent duplicate bookings for same user at same time
        unique_together = ['user', 'booking_date']
    
    def clean(self):
        """Validate booking constraints"""
        if self.booking_date and self.booking_date <= timezone.now():
            raise ValidationError("Cannot book for past dates")
            
        if self.no_of_guests <= 0:
            raise ValidationError("Number of guests must be at least 1")
            
        if self.no_of_guests > 10:
            raise ValidationError("Maximum 10 guests per booking")
    
    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
    
    @staticmethod
    def get_time_slot_capacity(booking_datetime):
        """Get current capacity for a 2-hour time slot"""
        from datetime import timedelta
        
        # Define 2-hour time slot window
        slot_start = booking_datetime.replace(minute=0, second=0, microsecond=0)
        slot_end = slot_start + timedelta(hours=2)
        
        # Count existing confirmed bookings in this time slot
        existing_bookings = Booking.objects.filter(
            booking_date__gte=slot_start,
            booking_date__lt=slot_end,
            status='confirmed'
        ).aggregate(
            total_guests=models.Sum('no_of_guests')
        )
        
        return existing_bookings['total_guests'] or 0
    
    @staticmethod
    def get_daily_capacity(booking_date):
        """Get current capacity for entire day"""
        from datetime import datetime, time
        
        # Get start and end of the day
        day_start = datetime.combine(booking_date.date(), time.min)
        day_end = datetime.combine(booking_date.date(), time.max)
        
        # Count existing confirmed bookings for the day
        existing_bookings = Booking.objects.filter(
            booking_date__range=(day_start, day_end),
            status='confirmed'
        ).aggregate(
            total_guests=models.Sum('no_of_guests')
        )
        
        return existing_bookings['total_guests'] or 0


class Menu(models.Model):
 
    title = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2) 
    inventory = models.IntegerField()  

    def __str__(self):
        return f"{self.title} - ${self.price}"