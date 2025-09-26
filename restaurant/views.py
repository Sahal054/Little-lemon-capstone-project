from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.models import User
from rest_framework.views import APIView 
from rest_framework import generics, viewsets, permissions
from rest_framework.response import Response
from restaurant.models import Booking, Menu
from restaurant.serializers import BookingSerializer, MenuSerializer, UserSerializer 
from rest_framework.permissions import IsAuthenticated

def index(request):
     return render(request, 'index.html', {})

class MenuItemsView(generics.ListCreateAPIView):
     permission_classes = [IsAuthenticated]
     queryset = Menu.objects.all()
     serializer_class = MenuSerializer  

class SingleMenuItemView(generics.RetrieveUpdateAPIView, generics.DestroyAPIView):
     queryset = Menu.objects.all()
     serializer_class = MenuSerializer 

class BookingViewSet(viewsets.ModelViewSet):
     permission_classes = [IsAuthenticated]
     queryset = Booking.objects.all()
     serializer_class = BookingSerializer  

class UserViewSet(viewsets.ModelViewSet):
   queryset = User.objects.all()
   serializer_class = UserSerializer
   permission_classes = [permissions.IsAuthenticated]

