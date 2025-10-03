from django.contrib import admin
from restaurant.models import Booking, Menu, RestaurantConfig

# Register your models here.
@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'booking_date', 'no_of_guests', 'status', 'created_at']
    list_filter = ['status', 'booking_date', 'created_at']
    search_fields = ['name', 'user__username']
    ordering = ['-booking_date']
    date_hierarchy = 'booking_date'

@admin.register(Menu)
class MenuAdmin(admin.ModelAdmin):
    list_display = ['title', 'price', 'inventory', 'image_preview']
    search_fields = ['title']
    ordering = ['title']
    readonly_fields = ['image_preview']
    
    def image_preview(self, obj):
        if obj.image:
            return f'<img src="{obj.image.url}" style="max-height: 50px; max-width: 100px;" />'
        return "No image"
    image_preview.short_description = 'Image Preview'
    image_preview.allow_tags = True

@admin.register(RestaurantConfig)
class RestaurantConfigAdmin(admin.ModelAdmin):
    list_display = ['max_daily_capacity', 'max_time_slot_capacity', 'booking_advance_days']
    
    def has_add_permission(self, request):
        # Only allow one configuration record
        return not RestaurantConfig.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        # Don't allow deletion of the configuration
        return False
