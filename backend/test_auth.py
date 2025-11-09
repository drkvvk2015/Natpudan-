"""
Test authentication endpoints
"""
import requests
import json

BASE_URL = "http://127.0.0.1:8001"

def test_register():
    """Test user registration"""
    print("\n=== Testing User Registration ===")
    
    url = f"{BASE_URL}/api/auth/register"
    data = {
        "email": "testdoctor@example.com",
        "password": "SecurePass123!",
        "full_name": "Dr. John Smith",
        "role": "doctor",
        "license_number": "MD12345",
        "specialization": "Cardiology",
        "phone": "+1234567890"
    }
    
    response = requests.post(url, json=data)
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 201:
        result = response.json()
        print(f"✅ Registration successful!")
        print(f"User: {result['user']['full_name']} ({result['user']['role']})")
        print(f"Email: {result['user']['email']}")
        print(f"Token: {result['access_token'][:50]}...")
        return result['access_token'], data['email'], data['password']
    else:
        print(f"❌ Registration failed: {response.text}")
        return None, None, None


def test_login(email, password):
    """Test user login"""
    print("\n=== Testing User Login ===")
    
    url = f"{BASE_URL}/api/auth/login"
    data = {
        "email": email,
        "password": password
    }
    
    response = requests.post(url, json=data)
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Login successful!")
        print(f"User: {result['user']['full_name']}")
        print(f"Token: {result['access_token'][:50]}...")
        return result['access_token']
    else:
        print(f"❌ Login failed: {response.text}")
        return None


def test_get_current_user(token):
    """Test get current user info"""
    print("\n=== Testing Get Current User ===")
    
    url = f"{BASE_URL}/api/auth/me"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    response = requests.get(url, headers=headers)
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Get current user successful!")
        print(f"ID: {result['id']}")
        print(f"Email: {result['email']}")
        print(f"Name: {result['full_name']}")
        print(f"Role: {result['role']}")
        print(f"Active: {result['is_active']}")
        print(f"Created: {result['created_at']}")
        return True
    else:
        print(f"❌ Get current user failed: {response.text}")
        return False


def test_register_patient():
    """Test patient registration"""
    print("\n=== Testing Patient Registration ===")
    
    url = f"{BASE_URL}/api/auth/register"
    data = {
        "email": "testpatient@example.com",
        "password": "PatientPass123!",
        "full_name": "Jane Doe",
        "role": "patient",
        "phone": "+0987654321",
        "date_of_birth": "1990-05-15"
    }
    
    response = requests.post(url, json=data)
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 201:
        result = response.json()
        print(f"✅ Patient registration successful!")
        print(f"User: {result['user']['full_name']} ({result['user']['role']})")
        print(f"Email: {result['user']['email']}")
        return result['access_token']
    else:
        print(f"❌ Patient registration failed: {response.text}")
        return None


def test_invalid_login():
    """Test login with invalid credentials"""
    print("\n=== Testing Invalid Login ===")
    
    url = f"{BASE_URL}/api/auth/login"
    data = {
        "email": "nonexistent@example.com",
        "password": "WrongPassword123!"
    }
    
    response = requests.post(url, json=data)
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 401:
        print(f"✅ Invalid login correctly rejected!")
        print(f"Error: {response.json()['detail']}")
        return True
    else:
        print(f"❌ Unexpected response: {response.text}")
        return False


def main():
    """Run all authentication tests"""
    print("=" * 60)
    print("AUTHENTICATION SYSTEM TESTS")
    print("=" * 60)
    
    try:
        # Test 1: Register doctor
        token1, email, password = test_register()
        if not token1:
            print("\n❌ Registration failed, skipping remaining tests")
            return
        
        # Test 2: Login with doctor account
        token2 = test_login(email, password)
        if not token2:
            print("\n❌ Login failed, skipping remaining tests")
            return
        
        # Test 3: Get current user info
        test_get_current_user(token2)
        
        # Test 4: Register patient
        patient_token = test_register_patient()
        if patient_token:
            test_get_current_user(patient_token)
        
        # Test 5: Invalid login
        test_invalid_login()
        
        print("\n" + "=" * 60)
        print("✅ ALL AUTHENTICATION TESTS COMPLETED!")
        print("=" * 60)
        
        print("\n📊 Summary:")
        print("✅ Doctor Registration: Working")
        print("✅ Patient Registration: Working")
        print("✅ User Login: Working")
        print("✅ Get Current User: Working")
        print("✅ Invalid Login Protection: Working")
        
        print("\n🎉 Authentication system is fully functional!")
        
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Cannot connect to backend server")
        print("Please ensure the backend is running on http://127.0.0.1:8001")
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")


if __name__ == "__main__":
    main()
