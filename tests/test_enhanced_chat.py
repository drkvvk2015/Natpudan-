"""
Test Enhanced Chat with Detailed Responses
This script tests the new detailed chat functionality with KB sources
"""
import requests
import json

BASE_URL = "http://localhost:8001"
API_URL = f"{BASE_URL}/api"

# Test credentials
EMAIL = "test@example.com"
PASSWORD = "test123"

print("🧪 Testing Enhanced Chat with Knowledge Base Integration...")
print()

# Step 1: Authentication
print("[INFO] Step 1: Authentication...")
try:
    login_response = requests.post(
        f"{API_URL}/auth/login",
        json={"username": EMAIL, "password": PASSWORD}
    )
    login_response.raise_for_status()
    token = login_response.json()["access_token"]
    print("[OK] Authenticated successfully")
    print()
except Exception as e:
    print(f"[ERROR] Authentication failed: {e}")
    print("Please ensure backend is running and test user exists")
    exit(1)

# Step 2: Send test medical query
print("[INFO] Step 2: Sending Test Medical Query...")
test_query = "What are the first-line treatments for type 2 diabetes?"
print(f"💬 Query: {test_query}")
print("[WAIT] Waiting for response...")
print()

headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

try:
    response = requests.post(
        f"{API_URL}/chat/message",
        json={"message": test_query, "conversation_id": None},
        headers=headers
    )
    response.raise_for_status()
    data = response.json()
    
    print("[OK] Response Received!")
    print()
    print("="*70)
    print("[STATS] CHAT RESPONSE")
    print("="*70)
    print()
    print(data["message"])
    print()
    print("="*70)
    print()
    
    # Check response characteristics
    message = data["message"]
    length = len(message)
    print(f"[RULER] Response Length: {length} characters")
    
    # Check for citations
    if "[1]" in message or "[2]" in message or "[3]" in message:
        print("[OK] Citations Found: Response includes numbered references")
    else:
        print("[WARNING]  No Citations: Response doesn't include numbered references")
    
    # Check for KB sources
    if "MEDICAL KNOWLEDGE BASE" in message or "🏥" in message:
        print("[OK] KB Sources Found: Response includes Knowledge Base section")
    else:
        print("[WARNING]  No KB Headers: Knowledge Base section not visible")
    
    # Check for structured sections
    if any(term in message for term in ["EXECUTIVE SUMMARY", "DETAILED ANALYSIS", "CLINICAL GUIDANCE"]):
        print("[OK] Structured Format: Response includes organized sections")
    else:
        print("[WARNING]  Basic Format: Structured sections not detected")
    
    print()
    print("[OK] TEST COMPLETED SUCCESSFULLY!")
    print()
    
    # Summary
    if length > 1000:
        print("[READY] Response is detailed (>1000 chars) - Enhancement working!")
    elif length > 500:
        print("[WARNING]  Response is moderate length (500-1000 chars) - May need tuning")
    else:
        print("[WARNING]  Response is short (<500 chars) - Enhancement may not be active")
    
except Exception as e:
    print(f"[ERROR] Chat request failed: {e}")
    if hasattr(e, 'response'):
        print(f"Response: {e.response.text}")
    exit(1)

print()
print("[TIP] TIP: Check the response above for:")
print("   - Numbered citations like [1], [2], [3]")
print("   - Knowledge Base source headers (🏥)")
print("   - Structured sections (Executive Summary, etc.)")
print("   - Detailed clinical information")
print()
