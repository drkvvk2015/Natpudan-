"""Simple KB test - upload and search"""
import requests
import os
from pathlib import Path

BASE_URL = "http://127.0.0.1:8000"

print("=== Knowledge Base Test ===\n")

# 1. Health check
print("1. Health Check...")
r = requests.get(f"{BASE_URL}/health")
print(f"   Status: {r.json()}\n")

# 2. Statistics before
print("2. Statistics (before upload)...")
r = requests.get(f"{BASE_URL}/api/medical/knowledge/statistics")
stats = r.json()
print(f"   Documents: {stats.get('total_documents', 0)}")
print(f"   Chunks: {stats.get('total_chunks', 0)}")
print(f"   Level: {stats.get('knowledge_level', 'UNKNOWN')}\n")

# 3. Upload PDF
print("3. Uploading PDF...")
medical_books = Path(__file__).parent / "backend" / "data" / "medical_books"
pdfs = list(medical_books.glob("*.pdf"))
if pdfs:
    pdf = pdfs[0]
    print(f"   File: {pdf.name}")
    with open(pdf, 'rb') as f:
        files = {'file': (pdf.name, f, 'application/pdf')}
        r = requests.post(f"{BASE_URL}/api/upload/document", files=files)
    print(f"   Result: {r.status_code}")
    if r.status_code == 200:
        print(f"   {r.json()}\n")

# 4. Statistics after
print("4. Statistics (after upload)...")
r = requests.get(f"{BASE_URL}/api/medical/knowledge/statistics")
stats = r.json()
print(f"   Documents: {stats.get('total_documents', 0)}")
print(f"   Chunks: {stats.get('total_chunks', 0)}")
print(f"   Level: {stats.get('knowledge_level', 'UNKNOWN')}")
if stats.get('pdf_sources'):
    print(f"   PDFs:")
    for pdf in stats['pdf_sources']:
        print(f"     - {pdf['name']}\n")

# 5. Search
print("5. Search for 'fever'...")
r = requests.post(f"{BASE_URL}/api/medical/knowledge/search", 
                  json={"query": "fever", "top_k": 3})
results = r.json()
print(f"   Found: {len(results.get('results', []))} results")
for i, res in enumerate(results.get('results', [])[:2], 1):
    print(f"\n   Result {i}:")
    print(f"   Source: {res['metadata'].get('source', 'Unknown')}")
    print(f"   Score: {res.get('score', 0):.4f}")
    print(f"   Text: {res['content'][:150]}...")

print("\n=== Complete ===")
