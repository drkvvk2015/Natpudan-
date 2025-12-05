"""Test KB upload endpoint directly"""
import requests
import os
from pathlib import Path

# Test files
test_files = [
    r"D:\Users\CNSHO\Documents\GitHub\Natpudan-\backend\data\medical_books\a-guide-to-the-mrcp-part-2-written-paper.pdf",
]

# Check if file exists
for f in test_files:
    if os.path.exists(f):
        print(f"[OK] Found: {Path(f).name} ({os.path.getsize(f) / 1024 / 1024:.2f} MB)")
    else:
        print(f"[X] Not found: {f}")
        exit(1)

# First, login to get token
print("\n1. Logging in...")
login_response = requests.post(
    "http://127.0.0.1:8000/api/auth/login",
    data={
        "username": "admin",
        "password": "admin123"
    }
)

if login_response.status_code != 200:
    print(f"[X] Login failed: {login_response.status_code}")
    print(login_response.text)
    exit(1)

token = login_response.json()["access_token"]
print(f"[OK] Login successful, token: {token[:20]}...")

# Now upload
print("\n2. Uploading PDF...")
headers = {
    "Authorization": f"Bearer {token}"
}

files_to_upload = []
for filepath in test_files:
    files_to_upload.append(
        ('files', (Path(filepath).name, open(filepath, 'rb'), 'application/pdf'))
    )

data = {
    'use_full_content': 'false',
    'chunk_size': '1000'
}

try:
    upload_response = requests.post(
        "http://127.0.0.1:8000/api/medical/knowledge/upload",
        headers=headers,
        files=files_to_upload,
        data=data,
        timeout=300  # 5 minutes
    )
    
    print(f"Status: {upload_response.status_code}")
    print(f"Response: {upload_response.json()}")
    
except Exception as e:
    print(f"[X] Upload failed: {e}")
finally:
    # Close files
    for _, (_, file_obj, _) in files_to_upload:
        file_obj.close()
