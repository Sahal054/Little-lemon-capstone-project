from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from rest_framework.views import APIView 
from rest_framework import generics, viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from restaurant.models import Booking, Menu
from restaurant.serializers import BookingSerializer, MenuSerializer, UserSerializer 
from rest_framework.permissions import IsAuthenticated

class IndexView(APIView):
    """
    Homepage view - accessible to all users
    """
    def get(self, request):
        return render(request, 'index.html', {})

class AboutView(APIView):
    """
    About page view - accessible to all users
    """
    def get(self, request):
        return render(request, 'about.html', {})


class MenuView(generics.ListAPIView):
    """
    Enhanced menu view that handles both template rendering and API responses
    Inherits from ListAPIView for consistency with other API views
    """
    permission_classes = [IsAuthenticated]
    queryset = Menu.objects.all()
    serializer_class = MenuSerializer
    
    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, 'Please log in to view the menu.')
            return redirect('login')
            
        # Check if this is an API request (Accept: application/json)
        if request.accepted_renderer.format == 'json':
            return super().get(request, *args, **kwargs)
        
        # Template rendering for web interface
        menu_items = self.get_queryset()
        return render(request, 'menu.html', {'menu_items': menu_items})

class BookView(generics.CreateAPIView):
    """
    Enhanced booking view that handles both template rendering and API responses
    Uses CreateAPIView for consistent validation and creation logic
    """
    permission_classes = [IsAuthenticated]
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    
    def get(self, request, *args, **kwargs):
        """Handle GET requests for template rendering"""
        if not request.user.is_authenticated:
            messages.error(request, 'Please log in to make a booking.')
            return redirect('login')
        return render(request, 'book.html', {})
    
    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, 'Please log in to make a booking.')
            return redirect('login')
            
        # Check if this is an API request
        if request.accepted_renderer.format == 'json':
            return super().post(request, *args, **kwargs)
        
        # Handle form submission for template
        booking_data = {
            'name': request.POST.get('name'),
            'no_of_guests': request.POST.get('no_of_guests'),
            'booking_date': f"{request.POST.get('booking_date')} {request.POST.get('booking_time')}"
        }
        
        serializer = self.get_serializer(data=booking_data)
        if serializer.is_valid():
            # Save with the current user
            booking = serializer.save(user=request.user)
            messages.success(request, 'Your reservation has been confirmed successfully!')
        else:
            error_msgs = []
            for field, errors in serializer.errors.items():
                error_msgs.extend(errors)
            messages.error(request, f'Booking failed: {", ".join(error_msgs)}')
        
        return redirect('book')
    
    def perform_create(self, serializer):
        """Override to automatically set the user when creating via API"""
        serializer.save(user=self.request.user)

class MyBookingsView(generics.ListAPIView):
    """
    View for displaying current user's bookings
    Shows both template and API responses for user's personal bookings
    """
    permission_classes = [IsAuthenticated]
    serializer_class = BookingSerializer
    
    def get_queryset(self):
        """Return only the current user's bookings"""
        return Booking.objects.filter(user=self.request.user).order_by('-booking_date')
    
    def get(self, request, *args, **kwargs):
        """Handle both template and API requests"""
        if not request.user.is_authenticated:
            messages.error(request, 'Please log in to view your bookings.')
            return redirect('login')
            
        # Check if this is an API request
        if request.accepted_renderer.format == 'json':
            return super().get(request, *args, **kwargs)
        
        # Template rendering for web interface
        my_bookings = self.get_queryset()
        from django.utils import timezone
        context = {
            'my_bookings': my_bookings,
            'total_bookings': my_bookings.count(),
            'now': timezone.now(),
        }
        return render(request, 'my_bookings.html', context)

class RegisterView(generics.CreateAPIView):
    """
    User registration view that handles both template rendering and API responses
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = []  # Allow unauthenticated access for registration
    
    def get(self, request, *args, **kwargs):
        """Handle GET requests for template rendering"""
        return render(request, 'register.html', {})
    
    def post(self, request, *args, **kwargs):
        # Check if this is an API request
        if request.accepted_renderer.format == 'json':
            return super().post(request, *args, **kwargs)
        
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

class LoginView(APIView):
    """
    User login view that handles both template rendering and API responses
    """
    permission_classes = []  # Allow unauthenticated access for login
    
    def get(self, request, *args, **kwargs):
        """Handle GET requests for template rendering"""
        return render(request, 'login.html', {})
    
    def post(self, request, *args, **kwargs):
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {user.first_name or user.username}!')
            
            # Handle API response
            if request.accepted_renderer.format == 'json':
                return Response({
                    'message': 'Login successful',
                    'user': UserSerializer(user).data
                }, status=status.HTTP_200_OK)
            
            # Redirect for template
            next_url = request.GET.get('next', 'home')
            return redirect(next_url)
        else:
            error_msg = 'Invalid username or password.'
            messages.error(request, error_msg)
            
            # Handle API error response
            if request.accepted_renderer.format == 'json':
                return Response({
                    'error': error_msg
                }, status=status.HTTP_401_UNAUTHORIZED)
        
        return render(request, 'login.html', {})

class LogoutView(APIView):
    """
    User logout view that handles both template rendering and API responses
    """
    def post(self, request, *args, **kwargs):
        logout(request)
        success_msg = 'You have been logged out successfully.'
        messages.success(request, success_msg)
        
        # Handle API response
        if request.accepted_renderer.format == 'json':
            return Response({
                'message': success_msg
            }, status=status.HTTP_200_OK)
        
        return redirect('home')
    
    def get(self, request, *args, **kwargs):
        """Allow GET requests for logout as well"""
        return self.post(request, *args, **kwargs)

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

