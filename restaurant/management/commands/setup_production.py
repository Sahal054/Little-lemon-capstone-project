from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.contrib.auth.models import User
from restaurant.models import RestaurantConfig

class Command(BaseCommand):
    help = 'Set up production environment with demo data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--demo-user',
            action='store_true',
            help='Create demo user for portfolio showcase',
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('Setting up Little Lemon production environment...')
        )
        
        # Load menu items
        self.stdout.write('Loading menu items...')
        try:
            call_command('loaddata', 'menu_items')
            self.stdout.write(
                self.style.SUCCESS('Menu items loaded successfully!')
            )
        except Exception as e:
            self.stdout.write(
                self.style.WARNING(f'Menu items may already exist: {e}')
            )
        
        # Create demo user if requested
        if options['demo_user']:
            if not User.objects.filter(username='demo').exists():
                self.stdout.write('Creating demo user...')
                demo_user = User.objects.create_user(
                    username='demo',
                    email='demo@littlelemon.com',
                    password='demo123',
                    first_name='Demo',
                    last_name='User'
                )
                self.stdout.write(
                    self.style.SUCCESS('Demo user created: demo/demo123')
                )
            else:
                self.stdout.write(
                    self.style.WARNING('Demo user already exists')
                )
        
        # Ensure restaurant config exists
        config, created = RestaurantConfig.objects.get_or_create(
            id=1,
            defaults={
                'max_daily_capacity': 50,
                'max_time_slot_capacity': 10,
                'booking_advance_days': 30
            }
        )
        if created:
            self.stdout.write(
                self.style.SUCCESS('Restaurant configuration created')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS('Restaurant configuration already exists')
            )
        
        self.stdout.write('')
        self.stdout.write(
            self.style.SUCCESS('Production setup completed!')
        )
        self.stdout.write(
            self.style.SUCCESS('Your Little Lemon restaurant is ready!')
        )
        self.stdout.write('')
        self.stdout.write('Next steps:')
        self.stdout.write('1. Visit your admin panel: /admin/')
        self.stdout.write('2. Upload images for menu items')
        self.stdout.write('3. Test the booking system')
        self.stdout.write('4. Share your portfolio: https://little-lemon-restaurant-c912.onrender.com')