"""
API Tests for Little Lemon Restaurant

Tests for all REST API endpoints including authentication, permissions, serialization, and CRUD operations.
"""
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
import json

from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from rest_framework.authtoken.models import Token

from restaurant.models import Menu, Booking, RestaurantConfig
from restaurant.serializers import MenuSerializer, BookingSerializer, UserSerializer


class APIAuthenticationTest(APITestCase):
    """Test API authentication mechanisms"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='apiuser',
            email='api@example.com',
            password='apipass123'
        )
        self.token = Token.objects.create(user=self.user)
        self.client = APIClient()
    
    def test_token_authentication_required(self):
        """Test that API endpoints require authentication"""
        # Try accessing protected endpoint without token
        response = self.client.get('/api/bookings/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_valid_token_authentication(self):
        """Test API access with valid token"""
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        response = self.client.get('/api/bookings/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_invalid_token_authentication(self):
        """Test API access with invalid token"""
        self.client.credentials(HTTP_AUTHORIZATION='Token invalid_token')
        response = self.client.get('/api/bookings/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_token_creation_endpoint(self):
        """Test token creation via API"""
        response = self.client.post('/api-token-auth/', {
            'username': 'apiuser',
            'password': 'apipass123'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)
        
        # Test with invalid credentials
        response = self.client.post('/api-token-auth/', {
            'username': 'apiuser',
            'password': 'wrongpass'
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class MenuAPITest(APITestCase):
    """Test Menu API endpoints"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user('testuser', 'test@example.com', 'pass123')
        self.staff_user = User.objects.create_user('staff', 'staff@example.com', 'pass123', is_staff=True)
        
        self.token = Token.objects.create(user=self.user)
        self.staff_token = Token.objects.create(user=self.staff_user)
        
        self.menu_items = [
            Menu.objects.create(title="Greek Salad", price=Decimal('12.99'), inventory=20),
            Menu.objects.create(title="Bruschetta", price=Decimal('8.99'), inventory=15),
            Menu.objects.create(title="Grilled Salmon", price=Decimal('18.99'), inventory=0)  # Out of stock
        ]
        
        self.client = APIClient()
    
    def test_get_menu_items_list(self):
        """Test GET /api/menu-items/ endpoint"""
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        response = self.client.get('/api/menu-items/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)
        
        # Check item structure
        item = response.data[0]
        self.assertIn('id', item)
        self.assertIn('title', item)
        self.assertIn('price', item)
        self.assertIn('inventory', item)
    
    def test_get_single_menu_item(self):
        """Test GET /api/menu-items/{id}/ endpoint"""
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        item_id = self.menu_items[0].id
        
        response = self.client.get(f'/api/menu-items/{item_id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Greek Salad')
        self.assertEqual(response.data['price'], '12.99')
    
    def test_create_menu_item_staff_only(self):
        """Test POST /api/menu-items/ - staff only"""
        # Regular user should not be able to create
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        response = self.client.post('/api/menu-items/', {
            'title': 'New Dish',
            'price': '15.99',
            'inventory': 10
        })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        # Staff user should be able to create
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.staff_token.key)
        response = self.client.post('/api/menu-items/', {
            'title': 'New Dish',
            'price': '15.99',
            'inventory': 10
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], 'New Dish')
    
    def test_update_menu_item_staff_only(self):
        """Test PUT /api/menu-items/{id}/ - staff only"""
        item_id = self.menu_items[0].id
        
        # Regular user should not be able to update
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        response = self.client.put(f'/api/menu-items/{item_id}/', {
            'title': 'Updated Greek Salad',
            'price': '13.99',
            'inventory': 25
        })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        # Staff user should be able to update
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.staff_token.key)
        response = self.client.put(f'/api/menu-items/{item_id}/', {
            'title': 'Updated Greek Salad',
            'price': '13.99',
            'inventory': 25
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Updated Greek Salad')
    
    def test_delete_menu_item_staff_only(self):
        """Test DELETE /api/menu-items/{id}/ - staff only"""
        item_id = self.menu_items[2].id
        
        # Regular user should not be able to delete
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        response = self.client.delete(f'/api/menu-items/{item_id}/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        # Staff user should be able to delete
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.staff_token.key)
        response = self.client.delete(f'/api/menu-items/{item_id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        # Verify item is deleted
        self.assertFalse(Menu.objects.filter(id=item_id).exists())


class BookingAPITest(APITestCase):
    """Test Booking API endpoints"""
    
    def setUp(self):
        """Set up test data"""
        self.user1 = User.objects.create_user('user1', 'user1@example.com', 'pass123')
        self.user2 = User.objects.create_user('user2', 'user2@example.com', 'pass123')
        self.staff_user = User.objects.create_user('staff', 'staff@example.com', 'pass123', is_staff=True)
        
        self.token1 = Token.objects.create(user=self.user1)
        self.token2 = Token.objects.create(user=self.user2)
        self.staff_token = Token.objects.create(user=self.staff_user)
        
        # Create restaurant config
        self.config = RestaurantConfig.objects.create(
            max_daily_capacity=50,
            max_time_slot_capacity=20,
            booking_advance_days=30
        )
        
        # Create test bookings
        future_date = timezone.now() + timedelta(days=7)
        self.booking1 = Booking.objects.create(
            user=self.user1,
            name="John Doe",
            no_of_guests=4,
            booking_date=future_date
        )
        
        self.booking2 = Booking.objects.create(
            user=self.user2,
            name="Jane Smith",
            no_of_guests=2,
            booking_date=future_date + timedelta(hours=2)
        )
        
        self.client = APIClient()
    
    def test_get_user_bookings(self):
        """Test GET /api/bookings/ - user sees only their bookings"""
        # User1 should see only their booking
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token1.key)
        response = self.client.get('/api/bookings/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'John Doe')
        
        # User2 should see only their booking
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token2.key)
        response = self.client.get('/api/bookings/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'Jane Smith')
    
    def test_staff_sees_all_bookings(self):
        """Test staff user sees all bookings"""
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.staff_token.key)
        response = self.client.get('/api/bookings/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
    
    def test_create_booking(self):
        """Test POST /api/bookings/ - create new booking"""
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token1.key)
        
        future_date = timezone.now() + timedelta(days=10)
        booking_data = {
            'name': 'Alice Johnson',
            'no_of_guests': 3,
            'booking_date': future_date.isoformat()
        }
        
        response = self.client.post('/api/bookings/', booking_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'Alice Johnson')
        self.assertEqual(response.data['no_of_guests'], 3)
        
        # Verify booking was created in database
        booking = Booking.objects.get(name='Alice Johnson')
        self.assertEqual(booking.user, self.user1)
    
    def test_create_booking_validation(self):
        """Test booking creation validation"""
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token1.key)
        
        # Test past date
        past_date = timezone.now() - timedelta(days=1)
        booking_data = {
            'name': 'Past Booking',
            'no_of_guests': 2,
            'booking_date': past_date.isoformat()
        }
        
        response = self.client.post('/api/bookings/', booking_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # Test invalid guest count
        future_date = timezone.now() + timedelta(days=5)
        booking_data = {
            'name': 'Invalid Guests',
            'no_of_guests': 0,
            'booking_date': future_date.isoformat()
        }
        
        response = self.client.post('/api/bookings/', booking_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_update_own_booking(self):
        """Test PUT /api/bookings/{id}/ - update own booking"""
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token1.key)
        booking_id = self.booking1.id
        
        future_date = timezone.now() + timedelta(days=8)
        update_data = {
            'name': 'John Updated',
            'no_of_guests': 5,
            'booking_date': future_date.isoformat()
        }
        
        response = self.client.put(f'/api/bookings/{booking_id}/', update_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'John Updated')
        self.assertEqual(response.data['no_of_guests'], 5)
    
    def test_cannot_update_others_booking(self):
        """Test user cannot update another user's booking"""
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token1.key)
        booking_id = self.booking2.id  # User2's booking
        
        update_data = {
            'name': 'Hacked Booking',
            'no_of_guests': 10,
            'booking_date': timezone.now() + timedelta(days=5)
        }
        
        response = self.client.put(f'/api/bookings/{booking_id}/', update_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_delete_own_booking(self):
        """Test DELETE /api/bookings/{id}/ - delete own booking"""
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token1.key)
        booking_id = self.booking1.id
        
        response = self.client.delete(f'/api/bookings/{booking_id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        # Verify booking is deleted
        self.assertFalse(Booking.objects.filter(id=booking_id).exists())
    
    def test_cannot_delete_others_booking(self):
        """Test user cannot delete another user's booking"""
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token1.key)
        booking_id = self.booking2.id  # User2's booking
        
        response = self.client.delete(f'/api/bookings/{booking_id}/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        
        # Verify booking still exists
        self.assertTrue(Booking.objects.filter(id=booking_id).exists())


class UserAPITest(APITestCase):
    """Test User API endpoints"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='pass123',
            first_name='Test',
            last_name='User'
        )
        
        self.staff_user = User.objects.create_user(
            username='staff',
            email='staff@example.com',
            password='pass123',
            is_staff=True
        )
        
        self.token = Token.objects.create(user=self.user)
        self.staff_token = Token.objects.create(user=self.staff_user)
        
        self.client = APIClient()
    
    def test_regular_user_profile_access(self):
        """Test regular user can access only their profile"""
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        response = self.client.get('/api/users/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Regular user should see only their own profile
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['username'], 'testuser')
    
    def test_staff_user_access_all_users(self):
        """Test staff user can access all user profiles"""
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.staff_token.key)
        response = self.client.get('/api/users/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Staff should see all users
        self.assertGreaterEqual(len(response.data), 2)
    
    def test_get_user_profile_action(self):
        """Test /api/users/profile/ action"""
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        response = self.client.get('/api/users/profile/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'testuser')
        self.assertEqual(response.data['email'], 'test@example.com')
        self.assertEqual(response.data['first_name'], 'Test')
    
    def test_update_user_profile(self):
        """Test PATCH /api/users/update_profile/"""
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        update_data = {
            'first_name': 'Updated',
            'last_name': 'Name'
        }
        
        response = self.client.patch('/api/users/update_profile/', update_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['first_name'], 'Updated')
        self.assertEqual(response.data['last_name'], 'Name')
        
        # Verify database was updated
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, 'Updated')
        self.assertEqual(self.user.last_name, 'Name')


class SerializerTest(TestCase):
    """Test API serializers"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user('testuser', 'test@example.com', 'pass123')
        self.config = RestaurantConfig.objects.create(
            max_daily_capacity=50,
            max_time_slot_capacity=20,
            booking_advance_days=30
        )
    
    def test_menu_serializer(self):
        """Test MenuSerializer"""
        menu_item = Menu.objects.create(
            title="Test Dish",
            price=Decimal('15.99'),
            inventory=10
        )
        
        serializer = MenuSerializer(menu_item)
        data = serializer.data
        
        self.assertEqual(data['title'], 'Test Dish')
        self.assertEqual(data['price'], '15.99')
        self.assertEqual(data['inventory'], 10)
    
    def test_booking_serializer_validation(self):
        """Test BookingSerializer validation"""
        # Valid data
        future_date = timezone.now() + timedelta(days=5)
        valid_data = {
            'name': 'Test Booking',
            'no_of_guests': 4,
            'booking_date': future_date,
            'user': self.user
        }
        
        serializer = BookingSerializer(data=valid_data)
        self.assertTrue(serializer.is_valid())
        
        # Invalid guest count
        invalid_data = valid_data.copy()
        invalid_data['no_of_guests'] = 0
        
        serializer = BookingSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('no_of_guests', serializer.errors)
    
    def test_user_serializer(self):
        """Test UserSerializer"""
        # Create a mock request for context
        from rest_framework.test import APIRequestFactory
        factory = APIRequestFactory()
        request = factory.get('/')
        request.user = self.user
        
        serializer = UserSerializer(self.user, context={'request': request})
        data = serializer.data
        
        self.assertEqual(data['username'], 'testuser')
        self.assertEqual(data['email'], 'test@example.com')
        self.assertIn('id', data)
        self.assertNotIn('password', data)  # Password should not be serialized


class APIErrorHandlingTest(APITestCase):
    """Test API error handling"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user('testuser', 'test@example.com', 'pass123')
        self.token = Token.objects.create(user=self.user)
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
    
    def test_404_not_found(self):
        """Test 404 error for non-existent resources"""
        response = self.client.get('/api/bookings/99999/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        
        response = self.client.get('/api/menu-items/99999/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_method_not_allowed(self):
        """Test 405 error for unsupported methods"""
        response = self.client.patch('/api/menu-items/')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
    
    def test_validation_errors(self):
        """Test 400 error for validation failures"""
        # Missing required fields
        response = self.client.post('/api/bookings/', {})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('name', response.data)
        self.assertIn('no_of_guests', response.data)
        self.assertIn('booking_date', response.data)
    
    def test_permission_denied(self):
        """Test 403 error for permission issues"""
        # Try to create menu item as regular user (not staff)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)  # Regular user token
        response = self.client.post('/api/menu-items/', {
            'title': 'New Dish',
            'price': '10.99',
            'inventory': 5
        })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class APIPerformanceTest(APITestCase):
    """Test API performance characteristics"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user('testuser', 'test@example.com', 'pass123')
        self.token = Token.objects.create(user=self.user)
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        
        # Create multiple menu items for performance testing
        self.menu_items = []
        for i in range(100):
            item = Menu.objects.create(
                title=f"Menu Item {i}",
                price=Decimal('10.99'),
                inventory=10
            )
            self.menu_items.append(item)
    
    def test_menu_list_performance(self):
        """Test menu list endpoint with many items"""
        response = self.client.get('/api/menu-items/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 100)
        
        # Basic performance check - should complete quickly
        import time
        start_time = time.time()
        response = self.client.get('/api/menu-items/')
        end_time = time.time()
        
        # Should complete within 1 second for 100 items
        self.assertLess(end_time - start_time, 1.0)
    
    def test_pagination_support(self):
        """Test API pagination (if implemented)"""
        response = self.client.get('/api/menu-items/?limit=10')
        
        # This test depends on pagination implementation
        # For now, just check that the endpoint accepts the parameter
        self.assertIn(response.status_code, [200, 400])  # Either works or parameter ignored