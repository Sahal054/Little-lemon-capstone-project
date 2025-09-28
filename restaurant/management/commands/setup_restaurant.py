from django.core.management.base import BaseCommand
from restaurant.models import RestaurantConfig

class Command(BaseCommand):
    help = 'Initialize restaurant configuration with default capacity settings'

    def add_arguments(self, parser):
        parser.add_argument(
            '--max-daily-capacity',
            type=int,
            default=50,
            help='Maximum number of guests per day (default: 50)'
        )
        parser.add_argument(
            '--max-time-slot-capacity',
            type=int,
            default=20,
            help='Maximum guests per 2-hour time slot (default: 20)'
        )
        parser.add_argument(
            '--booking-advance-days',
            type=int,
            default=30,
            help='How many days in advance bookings are allowed (default: 30)'
        )

    def handle(self, *args, **options):
        # Create or update restaurant configuration
        config, created = RestaurantConfig.objects.get_or_create(
            pk=1,  # Ensure only one configuration record
            defaults={
                'max_daily_capacity': options['max_daily_capacity'],
                'max_time_slot_capacity': options['max_time_slot_capacity'],
                'booking_advance_days': options['booking_advance_days'],
            }
        )
        
        if not created:
            # Update existing configuration
            config.max_daily_capacity = options['max_daily_capacity']
            config.max_time_slot_capacity = options['max_time_slot_capacity']
            config.booking_advance_days = options['booking_advance_days']
            config.save()
            action = 'Updated'
        else:
            action = 'Created'
        
        self.stdout.write(
            self.style.SUCCESS(
                f'{action} restaurant configuration:\n'
                f'  - Max daily capacity: {config.max_daily_capacity} guests\n'
                f'  - Max time slot capacity: {config.max_time_slot_capacity} guests\n'
                f'  - Booking advance window: {config.booking_advance_days} days'
            )
        )