"""Quick test to verify Phase 4 API is working"""
import requests
import time

# Wait a moment for server to fully start
time.sleep(2)

try:
    response = requests.get('http://localhost:8000/api/phase-4/health', timeout=5)
    
    if response.status_code == 200:
        data = response.json()
        print("✅ Phase 4 API Health Check:")
        print(f"   Status: {data.get('status')}")
        print(f"   Service: {data.get('service')}")
        print(f"   Database Tables: {data.get('database_tables')}")
        print("\n🎉 Phase 4 Sprint 1 is LIVE and working!")
    else:
        print(f"❌ Unexpected status code: {response.status_code}")
        print(f"Response: {response.text}")
        
except requests.exceptions.ConnectionError:
    print("❌ Cannot connect to server at http://localhost:8000")
    print("   Make sure the server is running:")
    print("   cd backend && python -m uvicorn app.main:app --reload --port 8000")
except Exception as e:
    print(f"❌ Error: {e}")
