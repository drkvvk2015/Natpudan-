"""
Test knowledge base upload and search functionality
"""
import os
import requests
import json
from pathlib import Path

# API base URL
BASE_URL = "http://127.0.0.1:8000"

def test_health():
    """Test health endpoint"""
    print("\n=== Testing Health Endpoint ===")
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_statistics():
    """Test knowledge base statistics endpoint"""
    print("\n=== Testing Statistics Endpoint ===")
    try:
        response = requests.get(f"{BASE_URL}/api/medical/knowledge/statistics")
        print(f"Status Code: {response.status_code}")
        data = response.json()
        print(f"Response: {json.dumps(data, indent=2)}")
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False

def upload_pdf(pdf_path):
    """Upload a PDF to the knowledge base"""
    print(f"\n=== Uploading {Path(pdf_path).name} ===")
    try:
        with open(pdf_path, 'rb') as f:
            files = {'file': (Path(pdf_path).name, f, 'application/pdf')}
            response = requests.post(
                f"{BASE_URL}/api/upload/document",
                files=files
            )
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_search(query):
    """Test knowledge base search"""
    print(f"\n=== Searching for '{query}' ===")
    try:
        response = requests.post(
            f"{BASE_URL}/api/medical/knowledge/search",
            json={"query": query, "top_k": 5}
        )
        print(f"Status Code: {response.status_code}")
        data = response.json()
        print(f"Found {len(data.get('results', []))} results")
        for i, result in enumerate(data.get('results', []), 1):
            print(f"\nResult {i}:")
            print(f"  Source: {result.get('metadata', {}).get('source', 'Unknown')}")
            print(f"  Score: {result.get('score', 0):.4f}")
            print(f"  Content preview: {result.get('content', '')[:200]}...")
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False

def main():
    print("=== Knowledge Base Test Script ===")
    
    # Test health
    if not test_health():
        print("\nHealth check failed! Is the backend running?")
        return
    
    # Test statistics before upload
    test_statistics()
    
    # Find and upload first PDF from medical_books
    medical_books_dir = Path(__file__).parent / "backend" / "data" / "medical_books"
    pdf_files = list(medical_books_dir.glob("*.pdf"))
    
    if pdf_files:
        print(f"\nFound {len(pdf_files)} PDF files in {medical_books_dir}")
        # Upload first PDF
        first_pdf = pdf_files[0]
        print(f"Uploading first PDF: {first_pdf.name}")
        upload_pdf(str(first_pdf))
        
        # Test statistics after upload
        test_statistics()
        
        # Test search
        test_search("fever")
    else:
        print(f"\nNo PDF files found in {medical_books_dir}")
    
    print("\n=== Test Complete ===")

if __name__ == "__main__":
    main()
