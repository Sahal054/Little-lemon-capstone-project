from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.contrib.auth.models import User
from restaurant.models import RestaurantConfig

class Command(BaseCommand):
    help = 'Automatically set up production environment with users and data'

    def handle(self, *args, **options):
        self.stdout.write('🚀 Auto-setting up production environment...')
        
        # Create restaurant config
        config, created = RestaurantConfig.objects.get_or_create(
            id=1,
            defaults={
                'max_daily_capacity': 50,
                'max_time_slot_capacity': 10, 
                'booking_advance_days': 30
            }
        )
        if created:
            self.stdout.write('✅ Restaurant configuration created')
        
        # Load menu items
        try:
            call_command('loaddata', 'menu_items')
            self.stdout.write('✅ Menu items loaded')
        except:
            self.stdout.write('⚠️ Menu items may already exist')
            
        # Create admin user
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser(
                username='admin',
                email='admin@littlelemon.com',
                password='admin123'
            )
            self.stdout.write('✅ Admin user created: admin/admin123')
            
        # Create demo user
        if not User.objects.filter(username='demo').exists():
            User.objects.create_user(
                username='demo',
                email='demo@littlelemon.com',
                password='demo123',
                first_name='Demo',
                last_name='User'
            )
            self.stdout.write('✅ Demo user created: demo/demo123')
            
        self.stdout.write('🎉 Production setup complete!')
        self.stdout.write('🌐 Visit your admin at: /admin/')
        self.stdout.write('👨‍💼 Login: admin/admin123')
        self.stdout.write('👤 Demo: demo/demo123')