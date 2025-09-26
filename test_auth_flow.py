#!/usr/bin/env python
"""
Test script to verify authentication and booking flow
"""
import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def test_authentication_flow():
    print("Testing Little Lemon Authentication Flow")
    print("=" * 50)
    
    # Test 1: Access public pages
    print("\n1. Testing public pages...")
    response = requests.get(f"{BASE_URL}/")
    print(f"Home page: {response.status_code} {'✓' if response.status_code == 200 else '✗'}")
    
    response = requests.get(f"{BASE_URL}/about/")
    print(f"About page: {response.status_code} {'✓' if response.status_code == 200 else '✗'}")
    
    # Test 2: Access protected pages without authentication
    print("\n2. Testing protected pages without authentication...")
    response = requests.get(f"{BASE_URL}/menu/", allow_redirects=False)
    print(f"Menu redirect: {response.status_code} {'✓' if response.status_code == 302 else '✗'}")
    
    response = requests.get(f"{BASE_URL}/book/", allow_redirects=False)
    print(f"Booking redirect: {response.status_code} {'✓' if response.status_code == 302 else '✗'}")
    
    # Test 3: Check API endpoints
    print("\n3. Testing API endpoints...")
    try:
        # Try to access API without authentication
        headers = {'Accept': 'application/json'}
        response = requests.get(f"{BASE_URL}/api/bookings/", headers=headers)
        print(f"API bookings without auth: {response.status_code} {'✓' if response.status_code == 401 else '✗'}")
    except Exception as e:
        print(f"API test failed: {e}")
    
    print("\n" + "=" * 50)
    print("Authentication flow test complete!")
    print("\nTo fully test:")
    print("1. Visit http://127.0.0.1:8000/ (should work)")
    print("2. Click 'Book now' (should redirect to login)")
    print("3. Register/Login and try again (should work)")

if __name__ == "__main__":
    test_authentication_flow()