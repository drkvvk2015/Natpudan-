#!/usr/bin/env python3
"""
Create admin user via API: admin / admin123
"""
import requests
import sys
import time

BASE_URL = "http://localhost:8000"

print("\n" + "="*50)
print(" Creating Admin User")
print("="*50)

# First check if backend is running
try:
    response = requests.get(f"{BASE_URL}/health", timeout=5)
    if response.status_code != 200:
        print("✗ Backend not responding properly")
        sys.exit(1)
    print("✓ Backend is running")
except Exception as e:
    print(f"✗ Backend not available: {e}")
    print("  Please start the backend first with: start-dev.ps1")
    sys.exit(1)

# Try to register admin user
try:
    register_data = {
        "email": "admin@admin.com",
        "password": "admin123",
        "full_name": "Administrator",
        "role": "admin"
    }
    
    response = requests.post(
        f"{BASE_URL}/api/auth/register",
        json=register_data,
        timeout=10
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"✓ Admin user created successfully")
        print(f"\n  Email: admin@admin.com")
        print(f"  Password: admin123")
        print(f"  Role: admin")
    elif response.status_code == 400:
        # User might already exist, try to login
        print("! User already exists, verifying with login...")
        login_data = {
            "email": "admin@admin.com",
            "password": "admin123"
        }
        
        login_response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json=login_data,
            timeout=10
        )
        
        if login_response.status_code == 200:
            print(f"✓ Admin user verified")
            print(f"\n  Email: admin@admin.com")
            print(f"  Password: admin123")
            print(f"  Role: admin")
        else:
            print(f"✗ Error: {response.text}")
            sys.exit(1)
    else:
        print(f"✗ Error: {response.status_code}")
        print(f"  Response: {response.text}")
        sys.exit(1)
    
    print("\n" + "="*50)
    print(" Admin user ready to use!")
    print("="*50)
    print(f"\nLogin at: http://localhost:5173")
    print(f"Email: admin@admin.com")
    print(f"Password: admin123\n")
    
except Exception as e:
    print(f"✗ Error: {e}")
    sys.exit(1)
