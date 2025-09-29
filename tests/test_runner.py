"""
Test Runner and Test Documentation for Little Lemon Restaurant

This file provides utilities and documentation for running the comprehensive test suite.
"""

# Test Categories and Commands
TEST_COMMANDS = {
    'all': 'python manage.py test',
    'models': 'python manage.py test tests.test_models',
    'views': 'python manage.py test tests.test_views', 
    'api': 'python manage.py test tests.test_api',
    'auth': 'python manage.py test tests.test_auth',
    'concurrency': 'python manage.py test tests.test_concurrency',
    'integration': 'python manage.py test tests.test_integration',
}

# Specific Test Classes
SPECIFIC_TESTS = {
    'menu_models': 'python manage.py test tests.test_models.MenuModelTest',
    'booking_models': 'python manage.py test tests.test_models.BookingModelTest',
    'login_views': 'python manage.py test tests.test_views.LoginViewTest',
    'api_auth': 'python manage.py test tests.test_api.APIAuthenticationTest',
    'concurrency_booking': 'python manage.py test tests.test_concurrency.ConcurrencyTestCase',
    'user_workflow': 'python manage.py test tests.test_integration.CompleteUserWorkflowTest',
}

# Performance and Load Tests
PERFORMANCE_TESTS = {
    'concurrency_performance': 'python manage.py test tests.test_concurrency.PerformanceTest',
    'integration_performance': 'python manage.py test tests.test_integration.PerformanceIntegrationTest',
    'high_load': 'python manage.py test tests.test_integration.PerformanceIntegrationTest.test_high_load_scenario',
}

def print_test_commands():
    """Print available test commands"""
    print("🧪 Little Lemon Test Suite")
    print("=" * 50)
    
    print("\n📋 Test Categories:")
    for name, command in TEST_COMMANDS.items():
        print(f"  {name:12} : {command}")
    
    print("\n🎯 Specific Test Classes:")
    for name, command in SPECIFIC_TESTS.items():
        print(f"  {name:18} : {command}")
    
    print("\n⚡ Performance Tests:")
    for name, command in PERFORMANCE_TESTS.items():
        print(f"  {name:20} : {command}")

if __name__ == "__main__":
    print_test_commands()