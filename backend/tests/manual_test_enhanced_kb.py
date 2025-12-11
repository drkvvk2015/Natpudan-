"""Test script for enhanced knowledge base"""

import sys
sys.path.insert(0, 'app')

from services.enhanced_knowledge_base import get_knowledge_base

# Initialize knowledge base
print("[TOOL] Initializing Enhanced Knowledge Base...")
kb = get_knowledge_base()

# Get statistics
stats = kb.get_statistics()
print(f"\n[STATS] Knowledge Base Statistics:")
print(f"   Sources: {stats['sources']}")
print(f"   Capabilities: {stats['capabilities']}")
print(f"   Source Details: {stats['source_details']}")

# Test searches
test_queries = [
    "high blood pressure symptoms",
    "diabetes treatment",
    "asthma emergency",
    "headache",
    "chest pain"
]

print(f"\n[SEARCH] Testing Knowledge Base Searches:\n")
for query in test_queries:
    print(f"Query: '{query}'")
    results = kb.search(query, top_k=2)
    print(f"Found {len(results)} results\n")
    
    for i, result in enumerate(results, 1):
        print(f"  {i}. Source: {result['source']}")
        print(f"     Score: {result['score']:.2f}")
        print(f"     ICD-10: {result.get('icd10', 'N/A')}")
        print(f"     Preview: {result['text'][:150]}...")
        print()
    print("-" * 80 + "\n")

print("[OK] Knowledge Base Test Complete!")
