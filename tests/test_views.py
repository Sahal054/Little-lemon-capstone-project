"""
View Tests for Little Lemon Restaurant

Tests for all Django views including templates, forms, authentication, and user interactions.
"""
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.messages import get_messages
from django.utils import timezone
from datetime import timedelta

from restaurant.models import Menu, Booking, RestaurantConfig


class PublicViewsTest(TestCase):
    """Test public views accessible to all users"""
    
    def setUp(self):
        """Set up test data"""
        self.client = Client()
    
    def test_home_page_view(self):
        """Test homepage view"""
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Little Lemon")
        self.assertTemplateUsed(response, 'index.html')
    
    def test_about_page_view(self):
        """Test about page view"""
        response = self.client.get(reverse('about'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "About")
        self.assertTemplateUsed(response, 'about.html')
    
    def test_login_page_view(self):
        """Test login page view"""
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Login")
        self.assertTemplateUsed(response, 'login.html')
    
    def test_register_page_view(self):
        """Test register page view"""
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Register")
        self.assertTemplateUsed(response, 'register.html')


class AuthenticatedViewsTest(TestCase):
    """Test views that require authentication"""
    
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        
        # Create some menu items
        self.menu_items = [
            Menu.objects.create(title="Greek Salad", price=12.99, inventory=20),
            Menu.objects.create(title="Bruschetta", price=8.99, inventory=15),
            Menu.objects.create(title="Grilled Salmon", price=18.99, inventory=10)
        ]
        
        # Create restaurant config
        self.config = RestaurantConfig.objects.create(
            max_daily_capacity=50,
            max_time_slot_capacity=20,
            booking_advance_days=30
        )
    
    def test_menu_view_requires_login(self):
        """Test menu view redirects unauthenticated users"""
        response = self.client.get(reverse('menu'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/login/?next=/menu/')
    
    def test_menu_view_authenticated(self):
        """Test menu view for authenticated users"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('menu'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'menu.html')
        self.assertContains(response, "Greek Salad")
        self.assertContains(response, "Bruschetta")
        self.assertContains(response, "Grilled Salmon")
    
    def test_booking_view_requires_login(self):
        """Test booking view redirects unauthenticated users"""
        response = self.client.get(reverse('book'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/login/?next=/book/')
    
    def test_booking_view_authenticated(self):
        """Test booking view for authenticated users"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('book'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'book.html')
        self.assertContains(response, "Make a Reservation")
    
    def test_my_bookings_view_requires_login(self):
        """Test my bookings view redirects unauthenticated users"""
        response = self.client.get(reverse('my-bookings'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/login/?next=/my-bookings/')
    
    def test_my_bookings_view_authenticated(self):
        """Test my bookings view for authenticated users"""
        self.client.login(username='testuser', password='testpass123')
        
        # Create a booking for the user
        future_date = timezone.now() + timedelta(days=7)
        booking = Booking.objects.create(
            user=self.user,
            name="Test Booking",
            no_of_guests=4,
            booking_date=future_date
        )
        
        response = self.client.get(reverse('my-bookings'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'my_bookings.html')
        self.assertContains(response, "Test Booking")
        self.assertContains(response, "4 guests")


class LoginViewTest(TestCase):
    """Test login functionality"""
    
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            first_name='Test'
        )
    
    def test_login_get_request(self):
        """Test GET request to login page"""
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'login.html')
    
    def test_valid_login(self):
        """Test login with valid credentials"""
        response = self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'testpass123'
        })
        
        # Should redirect after successful login
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('home'))
        
        # Check user is logged in
        user = response.wsgi_request.user
        self.assertTrue(user.is_authenticated)
        
        # Check success message
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('Welcome back' in str(msg) for msg in messages))
    
    def test_invalid_login(self):
        """Test login with invalid credentials"""
        response = self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'wrongpassword'
        })
        
        # Should stay on login page
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'login.html')
        
        # Check error message
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('Invalid username or password' in str(msg) for msg in messages))
    
    def test_login_redirect_next(self):
        """Test login redirects to next parameter"""
        next_url = reverse('menu')
        response = self.client.post(f"{reverse('login')}?next={next_url}", {
            'username': 'testuser',
            'password': 'testpass123'
        })
        
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, next_url)


class RegisterViewTest(TestCase):
    """Test registration functionality"""
    
    def setUp(self):
        """Set up test data"""
        self.client = Client()
    
    def test_register_get_request(self):
        """Test GET request to register page"""
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'register.html')
    
    def test_valid_registration(self):
        """Test registration with valid data"""
        response = self.client.post(reverse('register'), {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'newpass123',
            'first_name': 'New',
            'last_name': 'User'
        })
        
        # Should redirect to login page
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('login'))
        
        # Check user was created
        user = User.objects.get(username='newuser')
        self.assertEqual(user.email, 'newuser@example.com')
        self.assertEqual(user.first_name, 'New')
        self.assertEqual(user.last_name, 'User')
        
        # Check success message
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('Account created successfully' in str(msg) for msg in messages))
    
    def test_duplicate_username_registration(self):
        """Test registration with existing username"""
        # Create existing user
        User.objects.create_user('existinguser', 'existing@example.com', 'pass123')
        
        response = self.client.post(reverse('register'), {
            'username': 'existinguser',
            'email': 'different@example.com',
            'password': 'newpass123'
        })
        
        # Should stay on register page with error
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'register.html')
        
        # Check error message
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('Registration failed' in str(msg) for msg in messages))


class BookingViewTest(TestCase):
    """Test booking form functionality"""
    
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Create restaurant config
        self.config = RestaurantConfig.objects.create(
            max_daily_capacity=50,
            max_time_slot_capacity=20,
            booking_advance_days=30
        )
        
        self.client.login(username='testuser', password='testpass123')
    
    def test_valid_booking_submission(self):
        """Test booking with valid data"""
        future_date = timezone.now() + timedelta(days=7)
        booking_date = future_date.strftime('%Y-%m-%d')
        booking_time = future_date.strftime('%H:%M')
        
        response = self.client.post(reverse('book'), {
            'name': 'John Doe',
            'no_of_guests': '4',
            'booking_date': booking_date,
            'booking_time': booking_time
        })
        
        # Should redirect back to booking page
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('book'))
        
        # Check booking was created
        booking = Booking.objects.get(user=self.user)
        self.assertEqual(booking.name, 'John Doe')
        self.assertEqual(booking.no_of_guests, 4)
        
        # Check success message
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('reservation has been confirmed' in str(msg) for msg in messages))
    
    def test_invalid_booking_date_format(self):
        """Test booking with invalid date format"""
        response = self.client.post(reverse('book'), {
            'name': 'John Doe',
            'no_of_guests': '4',
            'booking_date': 'invalid-date',
            'booking_time': '19:00'
        })
        
        # Should redirect back with error
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('book'))
        
        # Check error message
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('Invalid date or time format' in str(msg) for msg in messages))
    
    def test_booking_past_date(self):
        """Test booking with past date"""
        past_date = timezone.now() - timedelta(days=1)
        booking_date = past_date.strftime('%Y-%m-%d')
        booking_time = past_date.strftime('%H:%M')
        
        response = self.client.post(reverse('book'), {
            'name': 'John Doe',
            'no_of_guests': '4',
            'booking_date': booking_date,
            'booking_time': booking_time
        })
        
        # Should redirect back with error
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('book'))
        
        # Should not create booking
        self.assertEqual(Booking.objects.filter(user=self.user).count(), 0)


class LogoutViewTest(TestCase):
    """Test logout functionality"""
    
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_logout_authenticated_user(self):
        """Test logout for authenticated user"""
        # Login first
        self.client.login(username='testuser', password='testpass123')
        
        # GET request should show logout confirmation
        response = self.client.get(reverse('logout'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'logout.html')
    
    def test_logout_post_request(self):
        """Test logout POST request"""
        # Login first
        self.client.login(username='testuser', password='testpass123')
        
        # POST request should logout and redirect
        response = self.client.post(reverse('logout'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('home'))
        
        # Check success message
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('logged out successfully' in str(msg) for msg in messages))
    
    def test_logout_unauthenticated_user(self):
        """Test logout for unauthenticated user"""
        response = self.client.get(reverse('logout'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('login'))


class TemplateContextTest(TestCase):
    """Test template context data"""
    
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.login(username='testuser', password='testpass123')
    
    def test_menu_context_data(self):
        """Test menu view context data"""
        # Create menu items
        menu_items = [
            Menu.objects.create(title="Item 1", price=10.99, inventory=5),
            Menu.objects.create(title="Item 2", price=15.99, inventory=0),  # Out of stock
            Menu.objects.create(title="Item 3", price=12.99, inventory=10)
        ]
        
        response = self.client.get(reverse('menu'))
        self.assertEqual(response.status_code, 200)
        
        context_menu_items = response.context['menu_items']
        self.assertEqual(len(context_menu_items), 3)
        
        # Check all items are present
        titles = [item.title for item in context_menu_items]
        self.assertIn("Item 1", titles)
        self.assertIn("Item 2", titles)
        self.assertIn("Item 3", titles)
    
    def test_my_bookings_context_data(self):
        """Test my bookings view context data"""
        # Create bookings
        future_date1 = timezone.now() + timedelta(days=5)
        future_date2 = timezone.now() + timedelta(days=10)
        
        booking1 = Booking.objects.create(
            user=self.user,
            name="Booking 1",
            no_of_guests=2,
            booking_date=future_date1
        )
        
        booking2 = Booking.objects.create(
            user=self.user,
            name="Booking 2", 
            no_of_guests=4,
            booking_date=future_date2
        )
        
        response = self.client.get(reverse('my-bookings'))
        self.assertEqual(response.status_code, 200)
        
        # Check context data
        self.assertEqual(response.context['total_bookings'], 2)
        self.assertIn('my_bookings', response.context)
        self.assertIn('now', response.context)
        
        # Check bookings are ordered by date (newest first)
        bookings = response.context['my_bookings']
        self.assertEqual(bookings[0], booking2)  # Later date should be first
        self.assertEqual(bookings[1], booking1)


class ViewPermissionsTest(TestCase):
    """Test view permissions and access control"""
    
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        self.regular_user = User.objects.create_user(
            username='regular',
            email='regular@example.com',
            password='pass123'
        )
        
        self.staff_user = User.objects.create_user(
            username='staff',
            email='staff@example.com',
            password='pass123',
            is_staff=True
        )
    
    def test_regular_user_access(self):
        """Test regular user access to views"""
        self.client.login(username='regular', password='pass123')
        
        # Should have access to these views
        accessible_views = ['home', 'about', 'menu', 'book', 'my-bookings', 'logout']
        
        for view_name in accessible_views:
            response = self.client.get(reverse(view_name))
            self.assertIn(response.status_code, [200, 302], f"Failed for {view_name}")
    
    def test_anonymous_user_restrictions(self):
        """Test anonymous user restrictions"""
        # Should redirect to login for protected views
        protected_views = ['menu', 'book', 'my-bookings']
        
        for view_name in protected_views:
            response = self.client.get(reverse(view_name))
            self.assertEqual(response.status_code, 302, f"Failed for {view_name}")
            self.assertTrue(response.url.startswith('/login/'), f"Failed redirect for {view_name}")


class ResponseTest(TestCase):
    """Test HTTP responses and status codes"""
    
    def setUp(self):
        """Set up test data"""
        self.client = Client()
    
    def test_404_handling(self):
        """Test 404 error handling"""
        response = self.client.get('/nonexistent-page/')
        self.assertEqual(response.status_code, 404)
    
    def test_method_not_allowed(self):
        """Test method not allowed responses"""
        # Try DELETE on a view that doesn't support it
        response = self.client.delete(reverse('home'))
        self.assertEqual(response.status_code, 405)  # Method Not Allowed