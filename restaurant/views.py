from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.views import View
from rest_framework.views import APIView 
from rest_framework import generics, viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from restaurant.models import Booking, Menu
from restaurant.serializers import BookingSerializer, MenuSerializer, UserSerializer 
from rest_framework.permissions import IsAuthenticated

class IndexView(View):
    """
    Homepage view - accessible to all users
    """
    def get(self, request):
        return render(request, 'index.html', {})

class AboutView(View):
    """
    About page view - accessible to all users
    """
    def get(self, request):
        return render(request, 'about.html', {})


class MenuView(LoginRequiredMixin, View):
    """
    Menu view for authenticated users only
    """
    login_url = '/login/'  # Explicit path to our custom login page
    
    def get(self, request, *args, **kwargs):        
        # Get menu items and render template
        menu_items = Menu.objects.all()
        return render(request, 'menu.html', {'menu_items': menu_items})

class BookView(LoginRequiredMixin, View):
    """
    Booking view for authenticated users only with concurrency protection
    """
    login_url = '/login/'  # Explicit path to our custom login page
    
    def get(self, request, *args, **kwargs):
        """Handle GET requests for template rendering"""        
        return render(request, 'book.html', {})
    
    def post(self, request, *args, **kwargs):
        """Handle POST requests for booking form submission with concurrency handling"""
        from django.db import transaction
        from datetime import datetime
        
        try:
            # Parse the booking data
            booking_date_str = f"{request.POST.get('booking_date')} {request.POST.get('booking_time')}"
            booking_datetime = datetime.strptime(booking_date_str, '%Y-%m-%d %H:%M')
            
            # Make timezone aware
            from django.utils import timezone
            booking_datetime = timezone.make_aware(booking_datetime)
            
            booking_data = {
                'name': request.POST.get('name'),
                'no_of_guests': int(request.POST.get('no_of_guests', 0)),
                'booking_date': booking_datetime,
                'user': request.user
            }
            
            # Use atomic transaction to prevent race conditions
            with transaction.atomic():
                serializer = BookingSerializer(data=booking_data)
                if serializer.is_valid():
                    # Save with the current user
                    booking = serializer.save(user=request.user)
                    messages.success(
                        request, 
                        f'Your reservation has been confirmed! '
                        f'Booking for {booking.no_of_guests} guests on '
                        f'{booking.booking_date.strftime("%B %d, %Y at %I:%M %p")}.'
                    )
                    return redirect('book')
                else:
                    # Handle validation errors
                    error_msgs = []
                    for field, errors in serializer.errors.items():
                        if field == 'non_field_errors':
                            error_msgs.extend(errors)
                        else:
                            for error in errors:
                                error_msgs.append(f"{field.replace('_', ' ').title()}: {error}")
                    
                    for error in error_msgs:
                        messages.error(request, error)
                    
        except ValueError as e:
            messages.error(request, 'Invalid date or time format. Please check your input.')
        except Exception as e:
            messages.error(request, f'Booking failed: {str(e)}')
        
        return redirect('book')

class MyBookingsView(LoginRequiredMixin, View):
    """
    View for displaying current user's bookings
    """
    login_url = '/login/'  # Explicit path to our custom login page
    
    def get(self, request, *args, **kwargs):
        """Handle template requests for user's bookings"""            
        # Get user's bookings and render template
        my_bookings = Booking.objects.filter(user=request.user).order_by('-booking_date')
        
        from django.utils import timezone
        context = {
            'my_bookings': my_bookings,
            'total_bookings': my_bookings.count(),
            'now': timezone.now(),
        }
        return render(request, 'my_bookings.html', context)

class RegisterView(View):
    """
    User registration view
    """
    def get(self, request, *args, **kwargs):
        """Handle GET requests for template rendering"""
        return render(request, 'register.html', {})
    
    def post(self, request, *args, **kwargs):
        # Handle form submission for template
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        first_name = request.POST.get('first_name', '')
        last_name = request.POST.get('last_name', '')
        
        try:
            # Create user
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name
            )
            messages.success(request, 'Account created successfully! You can now login.')
            return redirect('login')
        except Exception as e:
            messages.error(request, f'Registration failed: {str(e)}')
        
        return render(request, 'register.html', {})

class LoginView(View):
    """
    User login view
    """
    def get(self, request, *args, **kwargs):
        """Handle GET requests for template rendering"""
        # Always render template for GET requests
        return render(request, 'login.html', {})
    
    def post(self, request, *args, **kwargs):
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {user.first_name or user.username}!')
            
            # Always redirect for web requests (no API response)
            next_url = request.GET.get('next', 'home')
            return redirect(next_url)
        else:
            error_msg = 'Invalid username or password.'
            messages.error(request, error_msg)
        
        return render(request, 'login.html', {})

class LogoutView(View):
    """
    User logout view that handles both template rendering and logout
    """
    def get(self, request, *args, **kwargs):
        """Show logout confirmation for GET requests"""
        if request.user.is_authenticated:
            # User is logged in, perform logout and show success page
            logout(request)
            return render(request, 'logout.html', {})
        else:
            # User is not logged in, redirect to login page
            return redirect('login')
    
    def post(self, request, *args, **kwargs):
        """Handle POST logout requests"""
        logout(request)
        success_msg = 'You have been logged out successfully.'
        messages.success(request, success_msg)
        
        return redirect('home')

# Enhanced API Views with additional functionality
class MenuItemsView(generics.ListCreateAPIView):
    """
    API view for listing and creating menu items
    GET: List all menu items
    POST: Create a new menu item (admin functionality)
    """
    permission_classes = [IsAuthenticated]
    queryset = Menu.objects.all()
    serializer_class = MenuSerializer
    
    @action(detail=False, methods=['get'])
    def available_items(self, request):
        """Get only menu items that are in stock"""
        available_items = self.queryset.filter(inventory__gt=0)
        serializer = self.get_serializer(available_items, many=True)
        return Response(serializer.data)

class SingleMenuItemView(generics.RetrieveUpdateDestroyAPIView):
    """
    API view for retrieving, updating, and deleting individual menu items
    GET: Retrieve a specific menu item
    PUT/PATCH: Update a menu item (admin functionality)
    DELETE: Delete a menu item (admin functionality)
    """
    permission_classes = [IsAuthenticated]
    queryset = Menu.objects.all()
    serializer_class = MenuSerializer

class BookingViewSet(viewsets.ModelViewSet):
    """
    ViewSet for booking management with full CRUD operations
    Includes additional actions for booking management
    """
    permission_classes = [IsAuthenticated]
    serializer_class = BookingSerializer
    
    def get_queryset(self):
        """Filter bookings by authenticated user"""
        if self.request.user.is_staff:
            return Booking.objects.all()
        return Booking.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        """Automatically associate booking with current user"""
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def my_bookings(self, request):
        """Get current user's bookings"""
        user_bookings = Booking.objects.filter(user=request.user).order_by('-booking_date')
        serializer = self.get_serializer(user_bookings, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def upcoming_bookings(self, request):
        """Get upcoming bookings for current user"""
        from django.utils import timezone
        upcoming = Booking.objects.filter(
            user=request.user, 
            booking_date__gte=timezone.now()
        ).order_by('booking_date')
        serializer = self.get_serializer(upcoming, many=True)
        return Response(serializer.data)

class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet for user management
    Restricted to staff users for security
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Limit access based on user permissions"""
        if self.request.user.is_staff:
            return User.objects.all()
        # Regular users can only see their own profile
        return User.objects.filter(id=self.request.user.id)
    
    @action(detail=False, methods=['get'])
    def profile(self, request):
        """Get current user's profile"""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)
    
    @action(detail=False, methods=['patch'])
    def update_profile(self, request):
        """Update current user's profile"""
        serializer = self.get_serializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Pure API Views (separate from web interface)
class MenuAPIView(generics.ListCreateAPIView):
    """
    Pure API view for menu items - only for API consumers
    """
    permission_classes = [IsAuthenticated]
    queryset = Menu.objects.all()
    serializer_class = MenuSerializer

class MenuItemAPIView(generics.RetrieveUpdateDestroyAPIView):
    """
    Pure API view for individual menu items - only for API consumers
    """
    permission_classes = [IsAuthenticated]
    queryset = Menu.objects.all()
    serializer_class = MenuSerializer

class BookingAPIViewSet(viewsets.ModelViewSet):
    """
    Pure API ViewSet for bookings - only for API consumers
    """
    permission_classes = [IsAuthenticated]
    serializer_class = BookingSerializer
    
    def get_queryset(self):
        """Filter bookings by authenticated user"""
        if self.request.user.is_staff:
            return Booking.objects.all()
        return Booking.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        """Automatically associate booking with current user"""
        serializer.save(user=self.request.user)

