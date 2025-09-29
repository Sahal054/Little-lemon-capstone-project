"""
Concurrency Tests for Little Lemon Restaurant

Tests for concurrent booking scenarios, race condition prevention, and database integrity.
"""
import threading
import time
from django.test import TestCase, TransactionTestCase
from django.contrib.auth.models import User
from django.utils import timezone
from django.db import transaction, IntegrityError
from datetime import timedelta
from unittest.mock import patch
import concurrent.futures

from restaurant.models import Booking, RestaurantConfig
from restaurant.serializers import BookingSerializer


class ConcurrencyTestCase(TransactionTestCase):
    """
    Test concurrent operations using TransactionTestCase
    This allows testing actual database transactions and rollbacks
    """
    
    def setUp(self):
        """Set up test data"""
        # Create multiple users for concurrent testing
        self.users = []
        for i in range(10):
            user = User.objects.create_user(
                username=f'user{i}',
                email=f'user{i}@example.com',
                password='pass123'
            )
            self.users.append(user)
        
        # Create restaurant configuration
        self.config = RestaurantConfig.objects.create(
            max_daily_capacity=50,
            max_time_slot_capacity=10,  # Small capacity to test limits
            booking_advance_days=30
        )
        
        # Common booking datetime for concurrent tests
        self.test_datetime = timezone.now() + timedelta(days=7, hours=19)  # 7 PM next week
    
    def test_concurrent_booking_creation(self):
        """Test multiple users creating bookings simultaneously"""
        results = []
        exceptions = []
        
        def create_booking(user_index):
            """Function to create booking in thread"""
            try:
                user = self.users[user_index]
                booking_data = {
                    'name': f'User {user_index} Booking',
                    'no_of_guests': 2,
                    'booking_date': self.test_datetime,
                    'user': user
                }
                
                # Use atomic transaction with concurrency protection
                with transaction.atomic():
                    serializer = BookingSerializer(data=booking_data)
                    if serializer.is_valid():
                        booking = serializer.save(user=user)
                        results.append(f'Success: {booking.id}')
                        return booking
                    else:
                        results.append(f'Validation Error: {serializer.errors}')
                        return None
                        
            except Exception as e:
                exceptions.append(f'User {user_index}: {str(e)}')
                return None
        
        # Create 5 concurrent booking attempts
        num_threads = 5
        with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = [executor.submit(create_booking, i) for i in range(num_threads)]
            concurrent.futures.wait(futures)
        
        # Check results
        successful_bookings = Booking.objects.filter(booking_date=self.test_datetime).count()
        
        # All 5 bookings should succeed (5 * 2 guests = 10, which equals our capacity)
        self.assertEqual(successful_bookings, num_threads)
        self.assertEqual(len(results), num_threads)
        
        print(f"Concurrent booking results: {results}")
        if exceptions:
            print(f"Exceptions occurred: {exceptions}")
    
    def test_capacity_limit_enforcement(self):
        """Test that capacity limits are enforced under concurrency"""
        results = []
        exceptions = []
        
        def create_large_booking(user_index):
            """Function to create booking that might exceed capacity"""
            try:
                user = self.users[user_index]
                booking_data = {
                    'name': f'Large Booking {user_index}',
                    'no_of_guests': 4,  # 3 bookings * 4 guests = 12 > 10 capacity
                    'booking_date': self.test_datetime,
                    'user': user
                }
                
                with transaction.atomic():
                    serializer = BookingSerializer(data=booking_data)
                    if serializer.is_valid():
                        booking = serializer.save(user=user)
                        results.append(f'Success: {booking.id} - {booking.no_of_guests} guests')
                        return True
                    else:
                        results.append(f'Validation Failed: {serializer.errors}')
                        return False
                        
            except Exception as e:
                exceptions.append(f'User {user_index}: {str(e)}')
                return False
        
        # Try to create 3 concurrent bookings of 4 guests each (12 total > 10 capacity)
        num_threads = 3
        with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = [executor.submit(create_large_booking, i) for i in range(num_threads)]
            concurrent.futures.wait(futures)
        
        # Check total guests doesn't exceed capacity
        bookings = Booking.objects.filter(booking_date=self.test_datetime)
        total_guests = sum(booking.no_of_guests for booking in bookings)
        
        self.assertLessEqual(total_guests, self.config.max_time_slot_capacity)
        
        print(f"Capacity limit test results: {results}")
        print(f"Total guests booked: {total_guests}/{self.config.max_time_slot_capacity}")
        if exceptions:
            print(f"Exceptions: {exceptions}")
    
    def test_race_condition_prevention(self):
        """Test prevention of race conditions in booking creation"""
        race_results = []
        
        def race_booking_attempt(user_index):
            """Simulate race condition scenario"""
            try:
                user = self.users[user_index]
                
                # Simulate checking availability first (potential race condition point)
                current_capacity = Booking.get_time_slot_capacity(self.test_datetime)
                available_spots = self.config.max_time_slot_capacity - current_capacity
                
                # Small delay to increase chance of race condition
                time.sleep(0.01)
                
                if available_spots >= 3:  # Need 3 spots
                    booking_data = {
                        'name': f'Race Test {user_index}',
                        'no_of_guests': 3,
                        'booking_date': self.test_datetime,
                        'user': user
                    }
                    
                    # This should use atomic transaction with select_for_update
                    with transaction.atomic():
                        serializer = BookingSerializer(data=booking_data)
                        if serializer.is_valid():
                            booking = serializer.save(user=user)
                            race_results.append(f'Race Success: {user_index}')
                            return True
                        else:
                            race_results.append(f'Race Validation Failed: {user_index}')
                            return False
                else:
                    race_results.append(f'Race No Capacity: {user_index}')
                    return False
                    
            except Exception as e:
                race_results.append(f'Race Exception {user_index}: {str(e)}')
                return False
        
        # Create 4 concurrent attempts for 3 guests each (12 > 10 capacity)
        num_threads = 4
        with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = [executor.submit(race_booking_attempt, i) for i in range(num_threads)]
            concurrent.futures.wait(futures)
        
        # Verify data integrity
        bookings = Booking.objects.filter(booking_date=self.test_datetime)
        total_guests = sum(booking.no_of_guests for booking in bookings)
        
        # Should not exceed capacity even with race condition attempts
        self.assertLessEqual(total_guests, self.config.max_time_slot_capacity)
        
        print(f"Race condition test results: {race_results}")
        print(f"Final capacity: {total_guests}/{self.config.max_time_slot_capacity}")
    
    def test_unique_constraint_enforcement(self):
        """Test that unique constraints are enforced under concurrency"""
        user = self.users[0]
        constraint_results = []
        
        def attempt_duplicate_booking(attempt_id):
            """Try to create duplicate booking for same user/datetime"""
            try:
                booking_data = {
                    'name': f'Duplicate Attempt {attempt_id}',
                    'no_of_guests': 2,
                    'booking_date': self.test_datetime,
                    'user': user
                }
                
                booking = Booking.objects.create(**booking_data)
                constraint_results.append(f'Created: {attempt_id}')
                return booking
                
            except IntegrityError as e:
                constraint_results.append(f'Integrity Error: {attempt_id}')
                return None
            except Exception as e:
                constraint_results.append(f'Other Error {attempt_id}: {str(e)}')
                return None
        
        # Try to create 3 bookings for same user/datetime concurrently
        num_threads = 3
        with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = [executor.submit(attempt_duplicate_booking, i) for i in range(num_threads)]
            concurrent.futures.wait(futures)
        
        # Should only have 1 booking for this user/datetime
        bookings_count = Booking.objects.filter(
            user=user, 
            booking_date=self.test_datetime
        ).count()
        
        self.assertEqual(bookings_count, 1)
        
        print(f"Unique constraint test results: {constraint_results}")
    
    def test_daily_capacity_enforcement(self):
        """Test daily capacity limits with concurrent bookings"""
        # Set low daily capacity for testing
        self.config.max_daily_capacity = 15
        self.config.save()
        
        daily_results = []
        test_date = self.test_datetime.date()
        
        # Create bookings at different times on same day
        time_slots = [
            self.test_datetime.replace(hour=12, minute=0),  # Lunch
            self.test_datetime.replace(hour=19, minute=0),  # Dinner
            self.test_datetime.replace(hour=21, minute=0),  # Late dinner
        ]
        
        def create_daily_booking(user_index):
            """Create booking for daily capacity test"""
            try:
                user = self.users[user_index]
                time_slot = time_slots[user_index % len(time_slots)]
                
                booking_data = {
                    'name': f'Daily Test {user_index}',
                    'no_of_guests': 4,  # 4 users * 4 guests = 16 > 15 daily limit
                    'booking_date': time_slot,
                    'user': user
                }
                
                with transaction.atomic():
                    serializer = BookingSerializer(data=booking_data)
                    if serializer.is_valid():
                        booking = serializer.save(user=user)
                        daily_results.append(f'Daily Success: {user_index}')
                        return True
                    else:
                        daily_results.append(f'Daily Validation Failed: {user_index} - {serializer.errors}')
                        return False
                        
            except Exception as e:
                daily_results.append(f'Daily Exception {user_index}: {str(e)}')
                return False
        
        # Try 4 concurrent bookings of 4 guests each across different times
        num_threads = 4
        with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = [executor.submit(create_daily_booking, i) for i in range(num_threads)]
            concurrent.futures.wait(futures)
        
        # Check daily capacity not exceeded
        daily_bookings = Booking.objects.filter(booking_date__date=test_date)
        total_daily_guests = sum(booking.no_of_guests for booking in daily_bookings)
        
        self.assertLessEqual(total_daily_guests, self.config.max_daily_capacity)
        
        print(f"Daily capacity test results: {daily_results}")
        print(f"Daily total: {total_daily_guests}/{self.config.max_daily_capacity}")


class AtomicTransactionTest(TestCase):
    """Test atomic transaction behavior"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user('atomicuser', 'atomic@example.com', 'pass123')
        self.config = RestaurantConfig.objects.create(
            max_daily_capacity=50,
            max_time_slot_capacity=20,
            booking_advance_days=30
        )
    
    def test_transaction_rollback_on_error(self):
        """Test that transactions roll back properly on errors"""
        future_date = timezone.now() + timedelta(days=5)
        
        # Mock an error during booking save
        with patch.object(Booking, 'save', side_effect=Exception('Simulated error')):
            with self.assertRaises(Exception):
                with transaction.atomic():
                    booking = Booking(
                        user=self.user,
                        name="Should Rollback",
                        no_of_guests=2,
                        booking_date=future_date
                    )
                    booking.save()  # This will raise the mocked exception
        
        # Verify no booking was created
        bookings_count = Booking.objects.filter(user=self.user).count()
        self.assertEqual(bookings_count, 0)
    
    def test_select_for_update_locking(self):
        """Test select_for_update database locking"""
        # This test verifies the locking mechanism exists
        # In real concurrency scenarios, this prevents race conditions
        
        with transaction.atomic():
            config = RestaurantConfig.objects.select_for_update().first()
            self.assertIsNotNone(config)
            
            # During this transaction, other threads would be blocked
            # from updating the config until transaction commits
            config.max_daily_capacity = 100
            config.save()
        
        # Verify the update was applied
        updated_config = RestaurantConfig.objects.first()
        self.assertEqual(updated_config.max_daily_capacity, 100)


class PerformanceTest(TestCase):
    """Test performance under concurrent load"""
    
    def setUp(self):
        """Set up test data"""
        self.users = []
        for i in range(20):  # More users for performance testing
            user = User.objects.create_user(f'perfuser{i}', f'perf{i}@example.com', 'pass123')
            self.users.append(user)
        
        self.config = RestaurantConfig.objects.create(
            max_daily_capacity=100,
            max_time_slot_capacity=50,
            booking_advance_days=30
        )
    
    def test_booking_creation_performance(self):
        """Test booking creation performance with many concurrent users"""
        import time
        
        start_time = time.time()
        performance_results = []
        
        def timed_booking_creation(user_index):
            """Create booking and measure time"""
            user_start = time.time()
            try:
                user = self.users[user_index]
                future_date = timezone.now() + timedelta(days=5, hours=18)
                
                booking_data = {
                    'name': f'Performance Test {user_index}',
                    'no_of_guests': 2,
                    'booking_date': future_date + timedelta(minutes=user_index * 5),  # Spread times
                    'user': user
                }
                
                with transaction.atomic():
                    serializer = BookingSerializer(data=booking_data)
                    if serializer.is_valid():
                        booking = serializer.save(user=user)
                        user_end = time.time()
                        performance_results.append(user_end - user_start)
                        return True
                    else:
                        user_end = time.time()
                        performance_results.append(user_end - user_start)
                        return False
                        
            except Exception as e:
                user_end = time.time()
                performance_results.append(user_end - user_start)
                return False
        
        # Create 10 concurrent bookings
        num_threads = 10
        with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = [executor.submit(timed_booking_creation, i) for i in range(num_threads)]
            concurrent.futures.wait(futures)
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Performance assertions
        self.assertLess(total_time, 5.0)  # Should complete within 5 seconds
        
        if performance_results:
            avg_time = sum(performance_results) / len(performance_results)
            max_time = max(performance_results)
            print(f"Performance results - Total: {total_time:.2f}s, Avg: {avg_time:.3f}s, Max: {max_time:.3f}s")
            
            # Individual booking should complete quickly
            self.assertLess(avg_time, 1.0)  # Average under 1 second
            self.assertLess(max_time, 2.0)   # No single booking over 2 seconds
    
    def test_capacity_calculation_performance(self):
        """Test performance of capacity calculation methods"""
        # Create multiple bookings first
        test_date = timezone.now() + timedelta(days=3)
        
        for i in range(10):
            Booking.objects.create(
                user=self.users[i],
                name=f'Capacity Test {i}',
                no_of_guests=2,
                booking_date=test_date + timedelta(minutes=i * 10)
            )
        
        # Test time slot capacity calculation performance
        start_time = time.time()
        for _ in range(100):  # Run 100 times to measure performance
            capacity = Booking.get_time_slot_capacity(test_date)
        end_time = time.time()
        
        time_slot_time = end_time - start_time
        self.assertLess(time_slot_time, 1.0)  # Should complete 100 calls in under 1 second
        
        # Test daily capacity calculation performance
        start_time = time.time()
        for _ in range(100):
            daily_capacity = Booking.get_daily_capacity(test_date.date())
        end_time = time.time()
        
        daily_time = end_time - start_time
        self.assertLess(daily_time, 1.0)  # Should complete 100 calls in under 1 second
        
        print(f"Capacity calculation performance - Time slot: {time_slot_time:.3f}s, Daily: {daily_time:.3f}s")


class DatabaseIntegrityTest(TransactionTestCase):
    """Test database integrity under concurrent operations"""
    
    def setUp(self):
        """Set up test data"""
        self.users = []
        for i in range(5):
            user = User.objects.create_user(f'integrityuser{i}', f'int{i}@example.com', 'pass123')
            self.users.append(user)
        
        self.config = RestaurantConfig.objects.create(
            max_daily_capacity=20,
            max_time_slot_capacity=8,
            booking_advance_days=30
        )
    
    def test_database_consistency(self):
        """Test that database remains consistent under concurrent operations"""
        test_datetime = timezone.now() + timedelta(days=4, hours=20)
        integrity_results = []
        
        def integrity_test_booking(user_index):
            """Create booking while testing database consistency"""
            try:
                user = self.users[user_index]
                booking_data = {
                    'name': f'Integrity Test {user_index}',
                    'no_of_guests': 3,
                    'booking_date': test_datetime,
                    'user': user
                }
                
                with transaction.atomic():
                    # Check consistency before creating
                    pre_capacity = Booking.get_time_slot_capacity(test_datetime)
                    
                    serializer = BookingSerializer(data=booking_data)
                    if serializer.is_valid():
                        booking = serializer.save(user=user)
                        
                        # Check consistency after creating
                        post_capacity = Booking.get_time_slot_capacity(test_datetime)
                        expected_capacity = pre_capacity + booking.no_of_guests
                        
                        if post_capacity == expected_capacity:
                            integrity_results.append(f'Consistent: {user_index}')
                        else:
                            integrity_results.append(f'Inconsistent: {user_index} - {post_capacity} != {expected_capacity}')
                        
                        return True
                    else:
                        integrity_results.append(f'Validation Failed: {user_index}')
                        return False
                        
            except Exception as e:
                integrity_results.append(f'Error: {user_index} - {str(e)}')
                return False
        
        # Run concurrent integrity tests
        num_threads = 3  # 3 * 3 guests = 9 > 8 capacity
        with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = [executor.submit(integrity_test_booking, i) for i in range(num_threads)]
            concurrent.futures.wait(futures)
        
        # Final integrity check
        final_bookings = Booking.objects.filter(booking_date=test_datetime)
        calculated_capacity = Booking.get_time_slot_capacity(test_datetime)
        actual_capacity = sum(booking.no_of_guests for booking in final_bookings)
        
        self.assertEqual(calculated_capacity, actual_capacity, "Capacity calculation inconsistent with actual bookings")
        self.assertLessEqual(actual_capacity, self.config.max_time_slot_capacity, "Capacity limit exceeded")
        
        print(f"Database integrity test results: {integrity_results}")
        print(f"Final integrity check - Calculated: {calculated_capacity}, Actual: {actual_capacity}")
        
        # Check for consistency messages
        consistent_results = [r for r in integrity_results if 'Consistent' in r]
        self.assertGreater(len(consistent_results), 0, "No consistent results found")