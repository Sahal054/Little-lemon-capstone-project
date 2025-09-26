#!/usr/bin/env python
import os
import sys
import django

# Setup Django
sys.path.append('/home/sahal/Django_meta/capestone_project')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'littlelemon.settings')
django.setup()

from restaurant.models import Menu, Booking
from django.contrib.auth.models import User
from datetime import datetime, timedelta

# Create sample menu items
menu_items = [
    {'title': 'Greek Salad', 'price': 12.99, 'inventory': 20},
    {'title': 'Bruschetta', 'price': 8.99, 'inventory': 15},
    {'title': 'Grilled Salmon', 'price': 18.99, 'inventory': 10},
    {'title': 'Lemon Pasta', 'price': 16.99, 'inventory': 12},
    {'title': 'Mediterranean Bowl', 'price': 14.99, 'inventory': 8}
]

for item in menu_items:
    menu_obj, created = Menu.objects.get_or_create(
        title=item['title'],
        defaults={
            'price': item['price'],
            'inventory': item['inventory']
        }
    )
    if created:
        print(f"Created menu item: {menu_obj.title}")
    else:
        print(f"Menu item already exists: {menu_obj.title}")

print("Sample menu items setup complete!")