"""Test Phase 4 API with better timing"""
import requests
import time

print("Waiting for server to fully start...")
time.sleep(3)

try:
    print("Testing /api/phase-4/health endpoint...")
    response = requests.get('http://localhost:8000/api/phase-4/health', timeout=10)
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print("\n✅ Phase 4 API Health Check:")
        print(f"   Status: {data.get('status')}")
        print(f"   Phase: {data.get('phase')}")
        print(f"   Services: {data.get('services')}")
        print(f"   Cache Stats: {data.get('cache_statistics')}")
        print("\n🎉 Phase 4 Sprint 1 is LIVE and working!")
    else:
        print(f"❌ Unexpected status code: {response.status_code}")
        print(f"Response: {response.text}")
        
except requests.exceptions.ConnectionError:
    print("❌ Cannot connect to server at http://localhost:8000")
    print("   Make sure the server is running:")
    print("   cd backend && python -m uvicorn app.main:app --reload --port 8000")
except Exception as e:
    print(f"❌ Error: {type(e).__name__}: {e}")
