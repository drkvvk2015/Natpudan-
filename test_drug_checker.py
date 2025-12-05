#!/usr/bin/env python3
"""
Test script for Drug Interaction Checker
Tests both backend service and API endpoint
"""

import requests
import json
from typing import Dict, List, Any

# Configuration
BACKEND_URL = "http://127.0.0.1:8000"
API_ENDPOINT = f"{BACKEND_URL}/api/prescription/check-interactions"

def test_no_interactions() -> bool:
    """Test medications with no known interactions"""
    print("[TEST] Checking medications with NO interactions...")
    payload = {
        "medications": ["Metformin", "Vitamin D"]
    }
    
    try:
        response = requests.post(API_ENDPOINT, json=payload)
        if response.status_code != 200:
            print(f"  [ERROR] Status {response.status_code}")
            return False
        
        data = response.json()
        assert data["total_interactions"] == 0, "Expected 0 interactions"
        assert data["high_risk_warning"] == False, "Expected no high risk"
        print("  [OK] PASSED - No interactions detected")
        return True
    except Exception as e:
        print(f"  [ERROR] {e}")
        return False

def test_high_risk_interactions() -> bool:
    """Test high-severity drug interactions"""
    print("[TEST] Checking HIGH RISK medications...")
    payload = {
        "medications": ["Warfarin", "Aspirin", "Amiodarone"]
    }
    
    try:
        response = requests.post(API_ENDPOINT, json=payload)
        if response.status_code != 200:
            print(f"  [ERROR] Status {response.status_code}")
            return False
        
        data = response.json()
        print(f"  Total interactions: {data['total_interactions']}")
        print(f"  High risk: {data['high_risk_warning']}")
        print(f"  Severity breakdown: {data['severity_breakdown']}")
        
        assert data["high_risk_warning"] == True, "Expected high risk warning"
        assert data["severity_breakdown"]["high"] >= 2, "Expected at least 2 high severity"
        
        if data.get("interactions"):
            print("\n  Interactions found:")
            for interaction in data["interactions"]:
                print(f"    - {interaction['drug1']} + {interaction['drug2']}")
                print(f"      Severity: {interaction['severity'].upper()}")
                print(f"      Description: {interaction['description']}")
                if interaction.get("recommendation"):
                    print(f"      Recommendation: {interaction['recommendation']}")
        
        print("  [OK] PASSED - High risk interactions detected")
        return True
    except Exception as e:
        print(f"  [ERROR] {e}")
        return False

def test_moderate_interactions() -> bool:
    """Test moderate severity interactions"""
    print("[TEST] Checking MODERATE RISK medications...")
    payload = {
        "medications": ["Lisinopril", "Ibuprofen"]
    }
    
    try:
        response = requests.post(API_ENDPOINT, json=payload)
        if response.status_code != 200:
            print(f"  [ERROR] Status {response.status_code}")
            return False
        
        data = response.json()
        print(f"  Total interactions: {data['total_interactions']}")
        print(f"  High risk: {data['high_risk_warning']}")
        print(f"  Severity breakdown: {data['severity_breakdown']}")
        
        print("  [OK] PASSED - Moderate interactions checked")
        return True
    except Exception as e:
        print(f"  [ERROR] {e}")
        return False

def test_severity_filtering() -> bool:
    """Test severity-based filtering"""
    print("[TEST] Checking severity filtering...")
    payload = {
        "medications": ["Warfarin", "Aspirin", "Amiodarone"],
        "include_severity": ["high"]
    }
    
    try:
        response = requests.post(API_ENDPOINT, json=payload)
        if response.status_code != 200:
            print(f"  [ERROR] Status {response.status_code}")
            return False
        
        data = response.json()
        
        # Check that only high severity returned
        if data.get("interactions"):
            for interaction in data["interactions"]:
                assert interaction["severity"] == "high", f"Unexpected severity: {interaction['severity']}"
        
        print(f"  Total HIGH severity interactions: {data['severity_breakdown']['high']}")
        print("  [OK] PASSED - Severity filtering works")
        return True
    except Exception as e:
        print(f"  [ERROR] {e}")
        return False

def test_insufficient_medications() -> bool:
    """Test error handling for insufficient medications"""
    print("[TEST] Checking insufficient medications handling...")
    payload = {
        "medications": ["Metformin"]
    }
    
    try:
        response = requests.post(API_ENDPOINT, json=payload)
        if response.status_code != 200:
            print(f"  [ERROR] Status {response.status_code}")
            return False
        
        data = response.json()
        assert data["total_interactions"] == 0, "Expected 0 interactions for single drug"
        
        print("  [OK] PASSED - Gracefully handles insufficient drugs")
        return True
    except Exception as e:
        print(f"  [ERROR] {e}")
        return False

def print_header(text: str) -> None:
    """Print formatted header"""
    print("\n" + "="*70)
    print(f"  {text}")
    print("="*70 + "\n")

def main():
    """Run all tests"""
    print_header("DRUG INTERACTION CHECKER - TEST SUITE")
    
    # Check backend connectivity
    print("[INIT] Checking backend connectivity...")
    try:
        response = requests.get(f"{BACKEND_URL}/health")
        if response.status_code == 200:
            print("  [OK] Backend is running\n")
        else:
            print(f"  [ERROR] Backend health check failed: {response.status_code}")
            return
    except Exception as e:
        print(f"  [ERROR] Cannot connect to backend: {e}")
        print("  Make sure backend is running on http://127.0.0.1:8000")
        return
    
    # Run tests
    tests = [
        test_no_interactions,
        test_high_risk_interactions,
        test_moderate_interactions,
        test_severity_filtering,
        test_insufficient_medications,
    ]
    
    results = []
    for test_func in tests:
        try:
            result = test_func()
            results.append(result)
        except Exception as e:
            print(f"  [ERROR] Test exception: {e}")
            results.append(False)
        print()
    
    # Summary
    print_header("TEST SUMMARY")
    passed = sum(results)
    total = len(results)
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        print("\n[EMOJI] ALL TESTS PASSED - Drug Interaction Checker is working correctly!\n")
    else:
        print(f"\n[WARNING] {total - passed} test(s) failed\n")

if __name__ == "__main__":
    main()
