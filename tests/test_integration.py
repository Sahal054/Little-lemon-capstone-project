"""
Integration Tests for Little Lemon Restaurant

End-to-end tests covering complete user workflows and system integration.
"""
from django.test import TestCase, Client, TransactionTestCase
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.messages import get_messages
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
import time

from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token

from restaurant.models import Menu, Booking, RestaurantConfig


class CompleteUserWorkflowTest(TestCase):
    """Test complete user workflows from registration to booking"""
    
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        
        # Create restaurant configuration
        self.config = RestaurantConfig.objects.create(
            max_daily_capacity=50,
            max_time_slot_capacity=20,
            booking_advance_days=30
        )
        
        # Create sample menu items
        self.menu_items = [
            Menu.objects.create(title="Greek Salad", price=Decimal('12.99'), inventory=20),
            Menu.objects.create(title="Bruschetta", price=Decimal('8.99'), inventory=15),
            Menu.objects.create(title="Grilled Salmon", price=Decimal('18.99'), inventory=10),
            Menu.objects.create(title="Pasta Primavera", price=Decimal('16.99'), inventory=12),
            Menu.objects.create(title="Lamb Chops", price=Decimal('22.99'), inventory=8)
        ]
    
    def test_new_user_complete_journey(self):
        """Test complete journey of a new user from registration to booking"""
        
        # 1. User visits homepage
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Little Lemon")
        
        # 2. User tries to access menu without login - should redirect
        response = self.client.get(reverse('menu'))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/login/'))
        
        # 3. User goes to registration page
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'register.html')
        
        # 4. User registers new account
        registration_data = {
            'username': 'journeyuser',
            'email': 'journey@example.com',
            'password': 'journey123',
            'first_name': 'Journey',
            'last_name': 'Test'
        }
        
        response = self.client.post(reverse('register'), registration_data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('login'))
        
        # Verify user was created
        user = User.objects.get(username='journeyuser')
        self.assertEqual(user.email, 'journey@example.com')
        
        # 5. User logs in
        response = self.client.post(reverse('login'), {
            'username': 'journeyuser',
            'password': 'journey123'
        })
        self.assertEqual(response.status_code, 302)
        
        # 6. User visits about page
        response = self.client.get(reverse('about'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "About")
        
        # 7. User views menu
        response = self.client.get(reverse('menu'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'menu.html')
        
        # Verify all menu items are displayed
        for item in self.menu_items:
            self.assertContains(response, item.title)
            self.assertContains(response, str(item.price))
        
        # 8. User goes to booking page
        response = self.client.get(reverse('book'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'book.html')
        
        # 9. User makes a booking
        future_date = timezone.now() + timedelta(days=7)
        booking_data = {
            'name': 'Journey Family Dinner',
            'no_of_guests': '4',
            'booking_date': future_date.strftime('%Y-%m-%d'),
            'booking_time': future_date.strftime('%H:%M')
        }
        
        response = self.client.post(reverse('book'), booking_data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('book'))
        
        # Verify booking was created
        booking = Booking.objects.get(user=user)
        self.assertEqual(booking.name, 'Journey Family Dinner')
        self.assertEqual(booking.no_of_guests, 4)
        
        # Check success message
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('reservation has been confirmed' in str(msg) for msg in messages))
        
        # 10. User views their bookings
        response = self.client.get(reverse('my-bookings'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'my_bookings.html')
        self.assertContains(response, 'Journey Family Dinner')
        self.assertContains(response, '4 guests')
        
        # 11. User makes another booking
        future_date2 = timezone.now() + timedelta(days=14)
        booking_data2 = {
            'name': 'Anniversary Dinner',
            'no_of_guests': '2',
            'booking_date': future_date2.strftime('%Y-%m-%d'),
            'booking_time': future_date2.strftime('%H:%M')
        }
        
        response = self.client.post(reverse('book'), booking_data2)
        self.assertEqual(response.status_code, 302)
        
        # 12. User checks updated bookings list
        response = self.client.get(reverse('my-bookings'))
        self.assertEqual(response.status_code, 200)
        
        # Should show both bookings
        self.assertContains(response, 'Journey Family Dinner')
        self.assertContains(response, 'Anniversary Dinner')
        self.assertEqual(response.context['total_bookings'], 2)
        
        # 13. User logs out
        response = self.client.post(reverse('logout'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('home'))
        
        # 14. Verify user can't access protected pages after logout
        response = self.client.get(reverse('menu'))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/login/'))
    
    def test_returning_user_workflow(self):
        """Test workflow of returning user"""
        
        # Create existing user
        user = User.objects.create_user(
            username='returninguser',
            email='returning@example.com',
            password='return123',
            first_name='Returning',
            last_name='Customer'
        )
        
        # Create existing booking (bypass validation for test data)
        past_booking = Booking(
            user=user,
            name='Previous Visit',
            no_of_guests=2,
            booking_date=timezone.now() - timedelta(days=30),  # Past booking
            status='confirmed'
        )
        # Save without calling clean() to allow past date for test
        super(Booking, past_booking).save()
        
        # 1. User visits homepage
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        
        # 2. User logs in directly
        response = self.client.post(reverse('login'), {
            'username': 'returninguser',
            'password': 'return123'
        })
        self.assertEqual(response.status_code, 302)
        
        # 3. User checks their booking history
        response = self.client.get(reverse('my-bookings'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Previous Visit')
        
        # 4. User makes new booking
        future_date = timezone.now() + timedelta(days=10)
        response = self.client.post(reverse('book'), {
            'name': 'Return Visit',
            'no_of_guests': '3',
            'booking_date': future_date.strftime('%Y-%m-%d'),
            'booking_time': future_date.strftime('%H:%M')
        })
        
        self.assertEqual(response.status_code, 302)
        
        # 5. Verify both bookings appear in history
        response = self.client.get(reverse('my-bookings'))
        self.assertContains(response, 'Previous Visit')
        self.assertContains(response, 'Return Visit')
        self.assertEqual(response.context['total_bookings'], 2)


class APIIntegrationTest(TestCase):
    """Test API integration workflows"""
    
    def setUp(self):
        """Set up test data"""
        self.api_client = APIClient()
        
        # Create users
        self.user = User.objects.create_user('apiuser', 'api@example.com', 'api123')
        self.staff_user = User.objects.create_user('staff', 'staff@example.com', 'staff123', is_staff=True)
        
        # Create tokens
        self.token = Token.objects.create(user=self.user)
        self.staff_token = Token.objects.create(user=self.staff_user)
        
        # Create restaurant config
        self.config = RestaurantConfig.objects.create(
            max_daily_capacity=50,
            max_time_slot_capacity=20,
            booking_advance_days=30
        )
        
        # Create menu items
        self.menu_items = [
            Menu.objects.create(title="API Salad", price=Decimal('10.99'), inventory=15),
            Menu.objects.create(title="API Pizza", price=Decimal('14.99'), inventory=20)
        ]
    
    def test_complete_api_workflow(self):
        """Test complete API workflow from authentication to booking management"""
        
        # 1. Get authentication token
        response = self.api_client.post('/api-token-auth/', {
            'username': 'apiuser',
            'password': 'api123'
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn('token', response.data)
        token = response.data['token']
        
        # 2. Set authentication header
        self.api_client.credentials(HTTP_AUTHORIZATION=f'Token {token}')
        
        # 3. Get menu items
        response = self.api_client.get('/api/menu-items/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)
        
        # 4. Create booking via API
        future_date = timezone.now() + timedelta(days=5)
        booking_data = {
            'name': 'API Test Booking',
            'no_of_guests': 3,
            'booking_date': future_date.isoformat()
        }
        
        response = self.api_client.post('/api/bookings/', booking_data, format='json')
        self.assertEqual(response.status_code, 201)
        booking_id = response.data['id']
        
        # 5. Get user's bookings
        response = self.api_client.get('/api/bookings/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'API Test Booking')
        
        # 6. Update booking
        update_data = {
            'name': 'Updated API Booking',
            'no_of_guests': 4,
            'booking_date': future_date.isoformat()
        }
        
        response = self.api_client.put(f'/api/bookings/{booking_id}/', update_data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['name'], 'Updated API Booking')
        self.assertEqual(response.data['no_of_guests'], 4)
        
        # 7. Get user profile
        response = self.api_client.get('/api/users/profile/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['username'], 'apiuser')
        
        # 8. Update user profile
        profile_data = {
            'first_name': 'API',
            'last_name': 'User'
        }
        
        response = self.api_client.patch('/api/users/update_profile/', profile_data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['first_name'], 'API')
        
        # 9. Delete booking
        response = self.api_client.delete(f'/api/bookings/{booking_id}/')
        self.assertEqual(response.status_code, 204)
        
        # 10. Verify booking is deleted
        response = self.api_client.get('/api/bookings/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 0)
    
    def test_staff_api_workflow(self):
        """Test staff-specific API workflows"""
        
        # Set staff authentication
        self.api_client.credentials(HTTP_AUTHORIZATION=f'Token {self.staff_token.key}')
        
        # 1. Staff can see all bookings (if any exist)
        # Create booking for regular user first
        booking = Booking.objects.create(
            user=self.user,
            name='Regular User Booking',
            no_of_guests=2,
            booking_date=timezone.now() + timedelta(days=3)
        )
        
        response = self.api_client.get('/api/bookings/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        
        # 2. Staff can create menu items
        menu_data = {
            'title': 'Staff Created Dish',
            'price': '19.99',
            'inventory': 12
        }
        
        response = self.api_client.post('/api/menu-items/', menu_data, format='json')
        self.assertEqual(response.status_code, 201)
        menu_id = response.data['id']
        
        # 3. Staff can update menu items
        update_data = {
            'title': 'Updated Staff Dish',
            'price': '21.99',
            'inventory': 15
        }
        
        response = self.api_client.put(f'/api/menu-items/{menu_id}/', update_data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['title'], 'Updated Staff Dish')
        
        # 4. Staff can delete menu items
        response = self.api_client.delete(f'/api/menu-items/{menu_id}/')
        self.assertEqual(response.status_code, 204)
        
        # 5. Staff can see all users
        response = self.api_client.get('/api/users/')
        self.assertEqual(response.status_code, 200)
        self.assertGreaterEqual(len(response.data), 2)  # At least staff and regular user


class SystemIntegrationTest(TransactionTestCase):
    """Test system-wide integration scenarios"""
    
    def setUp(self):
        """Set up test data"""
        self.web_client = Client()
        self.api_client = APIClient()
        
        # Create users
        self.web_user = User.objects.create_user('webuser', 'web@example.com', 'web123')
        self.api_user = User.objects.create_user('apiuser', 'api@example.com', 'api123')
        
        # Create API token
        self.token = Token.objects.create(user=self.api_user)
        
        # Create restaurant config
        self.config = RestaurantConfig.objects.create(
            max_daily_capacity=20,
            max_time_slot_capacity=10,
            booking_advance_days=30
        )
        
        # Create menu items
        Menu.objects.create(title="Integration Dish", price=Decimal('15.99'), inventory=10)
    
    def test_web_and_api_consistency(self):
        """Test consistency between web interface and API"""
        
        # 1. Create booking via web interface
        self.web_client.login(username='webuser', password='web123')
        
        future_date = timezone.now() + timedelta(days=6)
        web_booking_data = {
            'name': 'Web Interface Booking',
            'no_of_guests': '3',
            'booking_date': future_date.strftime('%Y-%m-%d'),
            'booking_time': future_date.strftime('%H:%M')
        }
        
        response = self.web_client.post(reverse('book'), web_booking_data)
        self.assertEqual(response.status_code, 302)
        
        # 2. Create booking via API
        self.api_client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        
        api_future_date = timezone.now() + timedelta(days=7)
        api_booking_data = {
            'name': 'API Interface Booking',
            'no_of_guests': 4,
            'booking_date': api_future_date.isoformat()
        }
        
        response = self.api_client.post('/api/bookings/', api_booking_data, format='json')
        self.assertEqual(response.status_code, 201)
        
        # 3. Verify both bookings exist in database
        web_booking = Booking.objects.get(user=self.web_user)
        api_booking = Booking.objects.get(user=self.api_user)
        
        self.assertEqual(web_booking.name, 'Web Interface Booking')
        self.assertEqual(api_booking.name, 'API Interface Booking')
        
        # 4. Verify capacity calculations include both bookings
        test_date = future_date.date()
        daily_capacity = Booking.get_daily_capacity(test_date)
        
        # Should include web booking guests
        self.assertGreaterEqual(daily_capacity, 3)
        
        api_test_date = api_future_date.date()
        api_daily_capacity = Booking.get_daily_capacity(api_test_date)
        
        # Should include API booking guests
        self.assertGreaterEqual(api_daily_capacity, 4)
        
        # 5. Test that web user can see their booking in my-bookings
        response = self.web_client.get(reverse('my-bookings'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Web Interface Booking')
        self.assertNotContains(response, 'API Interface Booking')  # Should not see other user's booking
        
        # 6. Test that API user can see their booking via API
        response = self.api_client.get('/api/bookings/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'API Interface Booking')
    
    def test_concurrent_web_api_bookings(self):
        """Test concurrent bookings from web and API interfaces"""
        
        import threading
        import time
        
        results = {'web': None, 'api': None, 'errors': []}
        
        def web_booking():
            """Create booking via web interface"""
            try:
                client = Client()
                client.login(username='webuser', password='web123')
                
                future_date = timezone.now() + timedelta(days=8, hours=19)
                booking_data = {
                    'name': 'Concurrent Web Booking',
                    'no_of_guests': '5',
                    'booking_date': future_date.strftime('%Y-%m-%d'),
                    'booking_time': future_date.strftime('%H:%M')
                }
                
                response = client.post(reverse('book'), booking_data)
                results['web'] = response.status_code
                
            except Exception as e:
                results['errors'].append(f'Web error: {str(e)}')
        
        def api_booking():
            """Create booking via API"""
            try:
                client = APIClient()
                client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
                
                future_date = timezone.now() + timedelta(days=8, hours=19)  # Same time as web booking
                booking_data = {
                    'name': 'Concurrent API Booking',
                    'no_of_guests': 6,
                    'booking_date': future_date.isoformat()
                }
                
                response = client.post('/api/bookings/', booking_data, format='json')
                results['api'] = response.status_code
                
            except Exception as e:
                results['errors'].append(f'API error: {str(e)}')
        
        # Start both bookings concurrently
        web_thread = threading.Thread(target=web_booking)
        api_thread = threading.Thread(target=api_booking)
        
        web_thread.start()
        time.sleep(0.01)  # Small delay to increase concurrency chance
        api_thread.start()
        
        web_thread.join()
        api_thread.join()
        
        # Check results
        print(f"Concurrent booking results: {results}")
        
        # At least one booking should succeed or fail gracefully
        self.assertIsNotNone(results['web'])
        self.assertIsNotNone(results['api'])
        
        # Check total capacity doesn't exceed limits
        future_date = timezone.now() + timedelta(days=8, hours=19)
        time_slot_capacity = Booking.get_time_slot_capacity(future_date)
        self.assertLessEqual(time_slot_capacity, self.config.max_time_slot_capacity)
        
        # If both succeeded, total guests should not exceed capacity
        total_bookings = Booking.objects.filter(booking_date__date=future_date.date()).count()
        if total_bookings == 2:
            self.assertLessEqual(time_slot_capacity, self.config.max_time_slot_capacity)


class PerformanceIntegrationTest(TestCase):
    """Test performance under realistic usage scenarios"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test data once for the entire test class"""
        super().setUpClass()
        # Create multiple users (reduced from 50 to 10 for faster execution)
        cls.users = []
        for i in range(10):
            user = User.objects.create_user(f'perfuser{i}', f'perf{i}@example.com', 'perf123')
            cls.users.append(user)
        
        # Create many menu items
        for i in range(10):  # Reduced from 20 to 10
            Menu.objects.create(
                title=f"Performance Dish {i}",
                price=Decimal('10.99') + Decimal(str(i)),
                inventory=20
            )
    
    def setUp(self):
        """Set up test data"""
        # Create restaurant config
        self.config = RestaurantConfig.objects.create(
            max_daily_capacity=200,
            max_time_slot_capacity=50,
            booking_advance_days=30
        )
    
    def test_high_load_scenario(self):
        """Test system under high load"""
        
        start_time = time.time()
        
        # Simulate multiple users accessing the system
        clients = []
        for i in range(10):  # 10 concurrent users
            client = Client()
            client.login(username=f'perfuser{i}', password='perf123')
            clients.append(client)
        
        # Each user accesses multiple pages
        for client in clients:
            # Homepage
            response = client.get(reverse('home'))
            self.assertEqual(response.status_code, 200)
            
            # Menu page
            response = client.get(reverse('menu'))
            self.assertEqual(response.status_code, 200)
            
            # Booking page
            response = client.get(reverse('book'))
            self.assertEqual(response.status_code, 200)
            
            # My bookings page
            response = client.get(reverse('my-bookings'))
            self.assertEqual(response.status_code, 200)
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Performance assertion - should handle 40 page views (10 users * 4 pages) quickly
        self.assertLess(total_time, 10.0)  # Should complete within 10 seconds
        
        print(f"High load test completed in {total_time:.2f} seconds")
        print(f"Average time per page view: {total_time/40:.3f} seconds")


class ErrorHandlingIntegrationTest(TestCase):
    """Test error handling across the entire system"""
    
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        self.user = User.objects.create_user('erroruser', 'error@example.com', 'error123')
        
        self.config = RestaurantConfig.objects.create(
            max_daily_capacity=50,
            max_time_slot_capacity=20,
            booking_advance_days=30
        )
    
    def test_graceful_error_handling(self):
        """Test that errors are handled gracefully throughout the system"""
        
        # 1. Test invalid login
        response = self.client.post(reverse('login'), {
            'username': 'nonexistent',
            'password': 'wrongpass'
        })
        self.assertEqual(response.status_code, 200)  # Should stay on login page
        self.assertTemplateUsed(response, 'login.html')
        
        # 2. Test booking with invalid data after login
        self.client.login(username='erroruser', password='error123')
        
        response = self.client.post(reverse('book'), {
            'name': '',  # Invalid empty name
            'no_of_guests': 'invalid',  # Invalid guest count
            'booking_date': 'invalid-date',
            'booking_time': 'invalid-time'
        })
        
        # Should handle errors gracefully
        self.assertEqual(response.status_code, 302)  # Redirects back
        
        # Check for error messages
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(len(messages) > 0)
        
        # 3. Test accessing non-existent pages
        response = self.client.get('/non-existent-page/')
        self.assertEqual(response.status_code, 404)
        
        # 4. Test method not allowed
        response = self.client.delete(reverse('home'))
        self.assertEqual(response.status_code, 405)
    
    def test_capacity_limit_errors(self):
        """Test error handling when capacity limits are reached"""
        
        # Set very low capacity for testing
        self.config.max_time_slot_capacity = 2
        self.config.save()
        
        self.client.login(username='erroruser', password='error123')
        
        # Create booking that fills capacity
        future_date = timezone.now() + timedelta(days=5)
        
        # First booking - should succeed
        response = self.client.post(reverse('book'), {
            'name': 'First Booking',
            'no_of_guests': '2',
            'booking_date': future_date.strftime('%Y-%m-%d'),
            'booking_time': future_date.strftime('%H:%M')
        })
        self.assertEqual(response.status_code, 302)
        
        # Create another user for second booking
        user2 = User.objects.create_user('erroruser2', 'error2@example.com', 'error123')
        client2 = Client()
        client2.login(username='erroruser2', password='error123')
        
        # Second booking - should fail due to capacity
        response = client2.post(reverse('book'), {
            'name': 'Second Booking',
            'no_of_guests': '2',
            'booking_date': future_date.strftime('%Y-%m-%d'),
            'booking_time': future_date.strftime('%H:%M')
        })
        
        # Should redirect with error message
        self.assertEqual(response.status_code, 302)
        
        # Check that capacity was not exceeded
        time_slot_capacity = Booking.get_time_slot_capacity(future_date)
        self.assertLessEqual(time_slot_capacity, self.config.max_time_slot_capacity)


class DataConsistencyTest(TransactionTestCase):
    """Test data consistency across different interfaces"""
    
    def setUp(self):
        """Set up test data"""
        self.web_client = Client()
        self.api_client = APIClient()
        
        self.user = User.objects.create_user('consistencyuser', 'consistency@example.com', 'cons123')
        self.token = Token.objects.create(user=self.user)
        
        self.config = RestaurantConfig.objects.create(
            max_daily_capacity=100,
            max_time_slot_capacity=30,
            booking_advance_days=30
        )
    
    def test_data_consistency_across_interfaces(self):
        """Test that data remains consistent across web and API interfaces"""
        
        # 1. Create booking via web interface
        self.web_client.login(username='consistencyuser', password='cons123')
        
        future_date = timezone.now() + timedelta(days=9)
        web_booking = {
            'name': 'Consistency Test Web',
            'no_of_guests': '5',
            'booking_date': future_date.strftime('%Y-%m-%d'),
            'booking_time': future_date.strftime('%H:%M')
        }
        
        response = self.web_client.post(reverse('book'), web_booking)
        self.assertEqual(response.status_code, 302)
        
        # 2. Verify booking via API
        self.api_client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        response = self.api_client.get('/api/bookings/')
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'Consistency Test Web')
        self.assertEqual(response.data[0]['no_of_guests'], 5)
        
        api_booking_id = response.data[0]['id']
        
        # 3. Update booking via API
        update_data = {
            'name': 'Updated via API',
            'no_of_guests': 6,
            'booking_date': future_date.isoformat()
        }
        
        response = self.api_client.put(f'/api/bookings/{api_booking_id}/', update_data, format='json')
        self.assertEqual(response.status_code, 200)
        
        # 4. Verify update via web interface
        response = self.web_client.get(reverse('my-bookings'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Updated via API')
        self.assertContains(response, '6 guests')
        self.assertNotContains(response, 'Consistency Test Web')
        
        # 5. Verify capacity calculations are consistent
        calculated_capacity = Booking.get_time_slot_capacity(future_date)
        db_booking = Booking.objects.get(id=api_booking_id)
        
        self.assertEqual(calculated_capacity, db_booking.no_of_guests)
        self.assertEqual(calculated_capacity, 6)
        
        print(f"Data consistency verified - Capacity: {calculated_capacity}, DB guests: {db_booking.no_of_guests}")