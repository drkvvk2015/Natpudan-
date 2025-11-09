"""Debug script to test chat endpoint"""
import sys
from pathlib import Path

backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

# Print all registered routes
print("Registered routes:")
for route in app.routes:
    if hasattr(route, 'path') and hasattr(route, 'methods'):
        print(f"  {route.methods} {route.path}")

print("\n" + "="*50)
print("Testing chat endpoint...")
print("="*50 + "\n")

# Test the chat endpoint
payload = {
    "content": "What are the symptoms of diabetes?",
    "user_id": "test_user_123",
    "session_id": "test_session_456"
}

response = client.post("/api/chat/message", json=payload)
print(f"Status Code: {response.status_code}")
print(f"Response: {response.json()}")
