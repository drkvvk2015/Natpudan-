"""Test Phase 4 Medical Image Analysis API"""
import requests
import base64
from io import BytesIO
from PIL import Image

# Create a minimal test image (1x1 pixel)
def create_test_image():
    """Create a minimal valid test image"""
    img = Image.new('RGB', (1, 1), color='red')
    img_bytes = BytesIO()
    img.save(img_bytes, format='PNG')
    img_bytes.seek(0)
    return img_bytes.getvalue()

print("🚀 Phase 4 Medical Image Analysis Test")
print("=" * 50)

# Test 1: Health Check
print("\n1️⃣ Testing Health Endpoint...")
try:
    r = requests.get('http://localhost:8000/api/phase-4/health', timeout=5)
    if r.status_code == 200:
        data = r.json()
        print(f"✅ Health Status: {data['status']}")
        print(f"   Services: {data['services']}")
        print(f"   Cache: {data['cache_statistics']}")
    else:
        print(f"❌ Status {r.status_code}: {r.text}")
except Exception as e:
    print(f"❌ Error: {e}")

# Test 2: Image Analysis
print("\n2️⃣ Testing Image Analysis Endpoint...")
try:
    test_image_data = create_test_image()
    
    files = {
        'image': ('test_image.png', test_image_data, 'image/png')
    }
    params = {
        'image_type': 'xray',
        'clinical_context': 'Test chest X-ray for demonstration'
    }
    
    r = requests.post(
        'http://localhost:8000/api/phase-4/image/analyze',
        files=files,
        params=params,
        timeout=15
    )
    
    print(f"Status Code: {r.status_code}")
    
    if r.status_code == 200:
        data = r.json()
        print(f"✅ Image Analysis Successful!")
        print(f"   Image ID: {data.get('image_id')}")
        print(f"   Type: {data.get('image_type')}")
        print(f"   Severity: {data.get('severity')}")
        print(f"   Confidence: {data.get('confidence'):.2%}")
        print(f"   Findings: {data.get('findings', [])[:2]}")  # First 2 findings
        print(f"\n🎉 Phase 4 Medical Image Analysis is WORKING!")
    else:
        print(f"❌ Error {r.status_code}:")
        print(r.text)
        
except requests.exceptions.ConnectionError:
    print("❌ Cannot connect to server at http://localhost:8000")
    print("   Ensure server is running: python -m uvicorn app.main:app --port 8000")
except Exception as e:
    print(f"❌ Error: {type(e).__name__}: {e}")

print("\n" + "=" * 50)
print("Test Complete!")
