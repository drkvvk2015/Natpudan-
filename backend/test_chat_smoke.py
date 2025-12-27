#!/usr/bin/env python
"""Smoke test suite for Medical AI Chat functionality."""

import asyncio
import sys
import time
import httpx
import json
from typing import Dict, Any
from pathlib import Path

# Configuration
BACKEND_URL = "http://127.0.0.1:8000"
TEST_TIMEOUT = 30.0

class ChatSmokeTest:
    """Test suite for medical chat functionality."""
    
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=TEST_TIMEOUT)
        self.auth_token = None
        self.conversation_id = None
        self.test_results = {
            "PASSED": [],
            "FAILED": [],
            "SKIPPED": []
        }
    
    def log_test(self, name: str, status: str, message: str = ""):
        """Log test result."""
        timestamp = time.strftime("%H:%M:%S")
        status_emoji = "✅" if status == "PASSED" else "❌" if status == "FAILED" else "⏭️"
        print(f"[{timestamp}] {status_emoji} {name}")
        if message:
            print(f"           {message}")
        self.test_results[status].append(name)
    
    async def test_backend_health(self):
        """Test backend is running."""
        try:
            response = await self.client.get(f"{BACKEND_URL}/health")
            if response.status_code == 200:
                data = response.json()
                self.log_test("Backend Health Check", "PASSED", 
                             f"Status: {data.get('status')}")
                return True
            else:
                self.log_test("Backend Health Check", "FAILED", 
                             f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Backend Health Check", "FAILED", 
                         f"Connection error: {str(e)}")
            return False
    
    async def test_detailed_health(self):
        """Test detailed health metrics."""
        try:
            response = await self.client.get(f"{BACKEND_URL}/health/detailed")
            if response.status_code == 200:
                data = response.json()
                cpu = data.get("cpu_usage", 0)
                memory = data.get("memory_usage", {}).get("percent", 0)
                self.log_test("Detailed Health Metrics", "PASSED",
                             f"CPU: {cpu}%, Memory: {memory}%")
                return True
            else:
                self.log_test("Detailed Health Metrics", "FAILED",
                             f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Detailed Health Metrics", "FAILED", str(e))
            return False
    
    async def test_user_registration(self):
        """Test user registration."""
        try:
            test_email = f"test_user_{int(time.time())}@example.com"
            response = await self.client.post(
                f"{BACKEND_URL}/api/auth/register",
                json={
                    "email": test_email,
                    "password": "TestPassword123!",
                    "full_name": "Test User"
                }
            )
            
            if response.status_code in [200, 201]:
                self.log_test("User Registration", "PASSED",
                             f"User: {test_email}")
                return True, test_email
            else:
                self.log_test("User Registration", "FAILED",
                             f"Status code: {response.status_code}")
                return False, None
        except Exception as e:
            self.log_test("User Registration", "FAILED", str(e))
            return False, None
    
    async def test_user_login(self, email: str, password: str = "TestPassword123!"):
        """Test user login."""
        try:
            response = await self.client.post(
                f"{BACKEND_URL}/api/auth/login",
                json={
                    "email": email,
                    "password": password
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                self.auth_token = data.get("access_token")
                self.log_test("User Login", "PASSED", f"Token received: {self.auth_token[:20]}...")
                return True
            else:
                self.log_test("User Login", "FAILED",
                             f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("User Login", "FAILED", str(e))
            return False
    
    async def test_chat_send_message(self, message: str):
        """Test sending a chat message."""
        try:
            if not self.auth_token:
                self.log_test("Send Chat Message", "SKIPPED", "No auth token")
                return False
            
            response = await self.client.post(
                f"{BACKEND_URL}/api/chat/message",
                json={"message": message},
                headers={"Authorization": f"Bearer {self.auth_token}"}
            )
            
            if response.status_code == 200:
                data = response.json()
                self.conversation_id = data.get("conversation_id")
                assistant_msg = data.get("message", {}).get("content", "")
                
                self.log_test("Send Chat Message", "PASSED",
                             f"Conv ID: {self.conversation_id}, "
                             f"Response len: {len(assistant_msg)} chars")
                return True
            else:
                self.log_test("Send Chat Message", "FAILED",
                             f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Send Chat Message", "FAILED", str(e))
            return False
    
    async def test_chat_history(self):
        """Test retrieving chat history."""
        try:
            if not self.auth_token:
                self.log_test("Chat History", "SKIPPED", "No auth token")
                return False
            
            response = await self.client.get(
                f"{BACKEND_URL}/api/chat/history",
                headers={"Authorization": f"Bearer {self.auth_token}"}
            )
            
            if response.status_code == 200:
                data = response.json()
                self.log_test("Chat History", "PASSED",
                             f"Conversations: {len(data)}")
                return True
            else:
                self.log_test("Chat History", "FAILED",
                             f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Chat History", "FAILED", str(e))
            return False
    
    async def test_drug_interaction_check(self):
        """Test drug interaction checking."""
        try:
            if not self.auth_token:
                self.log_test("Drug Interaction Check", "SKIPPED", "No auth token")
                return False
            
            response = await self.client.post(
                f"{BACKEND_URL}/api/prescription/check-interactions",
                json={"medications": ["warfarin", "aspirin"]},
                headers={"Authorization": f"Bearer {self.auth_token}"}
            )
            
            if response.status_code == 200:
                data = response.json()
                interactions = data.get("total_interactions", 0)
                self.log_test("Drug Interaction Check", "PASSED",
                             f"Interactions found: {interactions}")
                return True
            else:
                self.log_test("Drug Interaction Check", "FAILED",
                             f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Drug Interaction Check", "FAILED", str(e))
            return False
    
    async def test_icd_search(self):
        """Test ICD-10 code search."""
        try:
            response = await self.client.get(
                f"{BACKEND_URL}/api/medical/icd/search?query=fever&max_results=5"
            )
            
            if response.status_code == 200:
                data = response.json()
                self.log_test("ICD-10 Search", "PASSED",
                             f"Results: {len(data) if isinstance(data, list) else 'N/A'}")
                return True
            else:
                self.log_test("ICD-10 Search", "FAILED",
                             f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("ICD-10 Search", "FAILED", str(e))
            return False
    
    async def test_knowledge_base_stats(self):
        """Test knowledge base statistics."""
        try:
            response = await self.client.get(
                f"{BACKEND_URL}/api/medical/knowledge/statistics"
            )
            
            if response.status_code == 200:
                data = response.json()
                doc_count = data.get("document_count", 0)
                chunk_count = data.get("chunk_count", 0)
                self.log_test("Knowledge Base Stats", "PASSED",
                             f"Docs: {doc_count}, Chunks: {chunk_count}")
                return True
            else:
                self.log_test("Knowledge Base Stats", "FAILED",
                             f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Knowledge Base Stats", "FAILED", str(e))
            return False
    
    async def run_all_tests(self):
        """Run all smoke tests."""
        print("\n" + "=" * 70)
        print("NATPUDAN MEDICAL AI CHAT - SMOKE TEST SUITE")
        print("=" * 70 + "\n")
        print(f"Backend URL: {BACKEND_URL}")
        print()
        
        # Basic health checks
        print("📋 INFRASTRUCTURE TESTS:")
        print("-" * 70)
        await self.test_backend_health()
        await self.test_detailed_health()
        
        # Knowledge base
        print("\n📚 KNOWLEDGE BASE TESTS:")
        print("-" * 70)
        await self.test_knowledge_base_stats()
        await self.test_icd_search()
        
        # Authentication & Chat
        print("\n🔐 AUTHENTICATION & CHAT TESTS:")
        print("-" * 70)
        registered, email = await self.test_user_registration()
        
        if registered:
            logged_in = await self.test_user_login(email)
            
            if logged_in:
                # Medical AI chat tests
                print("\n💬 MEDICAL AI CHAT TESTS:")
                print("-" * 70)
                
                # Test 1: Define a medical condition
                await self.test_chat_send_message("Define fever in adults")
                
                # Test 2: Drug interaction
                print("\n🔬 ADVANCED FEATURES:")
                print("-" * 70)
                await self.test_drug_interaction_check()
                
                # Test 3: Chat history
                print("\n📖 HISTORY & STATE TESTS:")
                print("-" * 70)
                await self.test_chat_history()
        
        # Print results
        print("\n" + "=" * 70)
        print("TEST RESULTS SUMMARY")
        print("=" * 70)
        
        passed = len(self.test_results["PASSED"])
        failed = len(self.test_results["FAILED"])
        skipped = len(self.test_results["SKIPPED"])
        total = passed + failed + skipped
        
        print(f"\n✅ PASSED:  {passed}/{total}")
        for test in self.test_results["PASSED"]:
            print(f"   - {test}")
        
        if failed > 0:
            print(f"\n❌ FAILED:  {failed}/{total}")
            for test in self.test_results["FAILED"]:
                print(f"   - {test}")
        
        if skipped > 0:
            print(f"\n⏭️  SKIPPED: {skipped}/{total}")
            for test in self.test_results["SKIPPED"]:
                print(f"   - {test}")
        
        print("\n" + "=" * 70)
        
        if failed == 0:
            print("✅ ALL TESTS PASSED - CHAT IS READY!")
            return 0
        else:
            print(f"❌ {failed} TESTS FAILED - PLEASE FIX ISSUES")
            return 1
    
    async def close(self):
        """Clean up."""
        await self.client.aclose()


async def main():
    """Main entry point."""
    test_suite = ChatSmokeTest()
    try:
        exit_code = await test_suite.run_all_tests()
        return exit_code
    finally:
        await test_suite.close()


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
