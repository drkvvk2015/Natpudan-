"""
Simple test script to verify backend API functionality.
Run this after starting the backend server to test all endpoints.
"""
import requests
import sys

API_URL = "http://localhost:8000"

def test_health():
    """Test health check endpoint."""
    print("\n1. Testing health check endpoint...")
    try:
        response = requests.get(f"{API_URL}/health")
        if response.status_code == 200:
            print("✓ Health check passed:", response.json())
            return True
        else:
            print("✗ Health check failed:", response.status_code)
            return False
    except Exception as e:
        print("✗ Health check error:", str(e))
        return False

def test_root():
    """Test root endpoint."""
    print("\n2. Testing root endpoint...")
    try:
        response = requests.get(f"{API_URL}/")
        if response.status_code == 200:
            print("✓ Root endpoint passed:", response.json())
            return True
        else:
            print("✗ Root endpoint failed:", response.status_code)
            return False
    except Exception as e:
        print("✗ Root endpoint error:", str(e))
        return False

def test_symptom_analysis():
    """Test symptom analysis endpoint."""
    print("\n3. Testing symptom analysis...")
    try:
        data = {
            "symptoms": "fever, cough, shortness of breath",
            "age": 45,
            "gender": "male"
        }
        response = requests.post(f"{API_URL}/api/analyze-symptoms", json=data)
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                print("✓ Symptom analysis passed")
                print("  Analysis preview:", result.get("analysis", "")[:100] + "...")
                return True
        print("✗ Symptom analysis failed:", response.status_code)
        return False
    except Exception as e:
        print("✗ Symptom analysis error:", str(e))
        return False

def test_drug_interactions():
    """Test drug interaction endpoint."""
    print("\n4. Testing drug interaction check...")
    try:
        data = {
            "medications": ["warfarin", "aspirin"]
        }
        response = requests.post(f"{API_URL}/api/check-interactions", json=data)
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                print("✓ Drug interaction check passed")
                print("  Analysis preview:", result.get("analysis", "")[:100] + "...")
                return True
        print("✗ Drug interaction check failed:", response.status_code)
        return False
    except Exception as e:
        print("✗ Drug interaction check error:", str(e))
        return False

def test_medical_search():
    """Test medical information search."""
    print("\n5. Testing medical information search...")
    try:
        data = {
            "query": "hypertension"
        }
        response = requests.post(f"{API_URL}/api/search-medical-info", json=data)
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                print("✓ Medical search passed")
                print("  Information preview:", result.get("information", "")[:100] + "...")
                return True
        print("✗ Medical search failed:", response.status_code)
        return False
    except Exception as e:
        print("✗ Medical search error:", str(e))
        return False

def test_knowledge_base_stats():
    """Test knowledge base statistics."""
    print("\n6. Testing knowledge base stats...")
    try:
        response = requests.get(f"{API_URL}/api/knowledge-base/stats")
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                print("✓ Knowledge base stats passed")
                print("  Stats:", result.get("stats"))
                return True
        print("✗ Knowledge base stats failed:", response.status_code)
        return False
    except Exception as e:
        print("✗ Knowledge base stats error:", str(e))
        return False

def main():
    """Run all tests."""
    print("=" * 60)
    print("Natpudan AI Medical Assistant - Backend API Tests")
    print("=" * 60)
    print(f"\nTesting backend at: {API_URL}")
    print("\nMake sure:")
    print("1. Backend server is running (python main.py)")
    print("2. OpenAI API key is configured in .env")
    print("3. All dependencies are installed")
    
    # Run tests
    tests = [
        test_health,
        test_root,
        test_symptom_analysis,
        test_drug_interactions,
        test_medical_search,
        test_knowledge_base_stats,
    ]
    
    results = []
    for test in tests:
        results.append(test())
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    passed = sum(results)
    total = len(results)
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        print("\n✓ All tests passed! Backend is working correctly.")
        return 0
    else:
        print(f"\n✗ {total - passed} test(s) failed. Check errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
