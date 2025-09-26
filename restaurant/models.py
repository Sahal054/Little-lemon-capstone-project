from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Booking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings', null=True, blank=True)
    name = models.CharField(max_length=255)
    no_of_guests = models.IntegerField() 
    booking_date = models.DateTimeField()

    def __str__(self):
        return f"{self.name} - {self.booking_date}"

    class Meta:
        ordering = ['-booking_date']


class Menu(models.Model):
 
    title = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2) 
    inventory = models.IntegerField()  

    def __str__(self):
        return f"{self.title} - ${self.price}"