#!/usr/bin/env python3
"""Test KB upload endpoint"""

import requests
import json
from pathlib import Path

# Test PDFs directory (files you're trying to upload)
TEST_FILES = [
    "Oxford Handbook of Clinical Medicine 10th 2017 Edition_SamanSarKo - Copy.pdf",
    "Harrisons Endocrinology, 3rd.pdf",
    "macleods_clinical_examination_14_ed.pdf"
]

# First, get auth token
print("[INFO] Getting auth token...")
auth_response = requests.post(
    "http://127.0.0.1:8000/api/auth/login",
    json={"email": "admin@natpudan.com", "password": "admin123"}
)

if auth_response.status_code != 200:
    print(f"[ERROR] Auth failed: {auth_response.text}")
    exit(1)

token = auth_response.json()["access_token"]
print(f"[OK] Got token: {token[:20]}...")

headers = {"Authorization": f"Bearer {token}"}

# Try uploading
print("\n[INFO] Testing upload endpoint...")
try:
    response = requests.post(
        "http://127.0.0.1:8000/api/medical/knowledge/upload",
        headers=headers,
        json={"test": "data"}
    )
    print(f"[TEST] Response status: {response.status_code}")
    print(f"[TEST] Response: {response.text}")
except Exception as e:
    print(f"[ERROR] {e}")

print("\n[INFO] KB upload test complete")
