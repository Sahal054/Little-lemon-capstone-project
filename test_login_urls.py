#!/usr/bin/env python3
import requests

print("Testing login URLs...")

# Test custom login page
try:
    response = requests.get('http://127.0.0.1:8000/login/')
    print(f"Custom login (/login/): Status {response.status_code}")
    if response.status_code == 200:
        if 'Welcome Back' in response.text:
            print("✅ Custom login template working!")
        elif 'Django REST framework' in response.text:
            print("❌ Showing DRF interface instead of custom template")
        else:
            print("❓ Unknown template content")
    else:
        print(f"❌ Error: {response.status_code}")
except Exception as e:
    print(f"Error testing custom login: {e}")

# Test Djoser API login
try:
    response = requests.get('http://127.0.0.1:8000/auth/token/login/')
    print(f"Djoser API login (/auth/token/login/): Status {response.status_code}")
    if response.status_code == 405:
        print("✅ Correctly returns Method Not Allowed (GET not supported)")
    else:
        print(f"❓ Unexpected status: {response.status_code}")
except Exception as e:
    print(f"Error testing Djoser login: {e}")

print("\nTo see the custom login page, use: http://127.0.0.1:8000/login/")
print("Avoid using: http://127.0.0.1:8000/auth/token/login/")