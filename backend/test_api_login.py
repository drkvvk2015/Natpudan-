import sys
sys.path.insert(0, '.')

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

print("=" * 60)
print("API LOGIN TEST")
print("=" * 60)

payload = {
    "email": "admin@admin.com",
    "password": "Admin@123"
}

print(f"\nTesting POST /api/auth/login")
print(f"Payload: {payload}")

response = client.post("/api/auth/login", json=payload)

print(f"\nStatus Code: {response.status_code}")
print(f"Response Headers: {dict(response.headers)}")

if response.status_code == 200:
    data = response.json()
    print(f"\n✅ LOGIN SUCCESSFUL!")
    print(f"Email: {data['user']['email']}")
    print(f"Role: {data['user']['role']}")
    print(f"Token exists: {bool(data.get('access_token'))}")
else:
    print(f"\n❌ LOGIN FAILED!")
    print(f"Response: {response.json()}")
