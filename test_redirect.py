#!/usr/bin/env python3
import requests

# Test the menu redirect
try:
    response = requests.get('http://127.0.0.1:8000/menu/', allow_redirects=False)
    print(f"Menu redirect status: {response.status_code}")
    if 'Location' in response.headers:
        redirect_url = response.headers['Location']
        print(f"Redirects to: {redirect_url}")
        
        if '/login/' in redirect_url:
            print("✅ SUCCESS: Redirects to custom login page!")
        elif '/auth/token/login' in redirect_url:
            print("❌ PROBLEM: Still redirecting to Djoser API login")
        else:
            print(f"❓ UNKNOWN: Redirects to unexpected URL: {redirect_url}")
    else:
        print("No redirect found")
        
except Exception as e:
    print(f"Error: {e}")