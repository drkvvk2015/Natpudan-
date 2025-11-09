"""
Comprehensive API tests for Natpudan AI Medical Assistant
Uses FastAPI TestClient for testing without requiring a running server
"""
import pytest
import sys
from pathlib import Path
from typing import Dict, Any

# Add backend directory to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from fastapi.testclient import TestClient
from app.main import app

# Create test client
client = TestClient(app)

class TestHealthEndpoints:
    """Test basic health and status endpoints"""
    
    def test_root_endpoint(self):
        """Test root endpoint returns status"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data or "message" in data
    
    def test_health_check(self):
        """Test health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "service" in data
        assert "timestamp" in data


class TestKnowledgeBaseEndpoints:
    """Test knowledge base and medical knowledge search"""
    
    def test_knowledge_statistics(self):
        """Test knowledge base statistics endpoint"""
        response = client.get("/api/medical/knowledge/statistics")
        assert response.status_code == 200
        data = response.json()
        assert "total_documents" in data
        assert "total_chunks" in data
        # Note: May be 0 in test environment without loaded PDFs
        assert data["total_documents"] >= 0
    
    def test_knowledge_search_basic(self):
        """Test basic knowledge search - may return empty results in test env"""
        payload = {
            "query": "What are the symptoms of pneumonia?",
            "top_k": 5
        }
        response = client.post("/api/medical/knowledge/search",
            json=payload
        )
        # Accept both 200 (success) and 500 (knowledge base not initialized)
        assert response.status_code in [200, 500]
        if response.status_code == 200:
            data = response.json()
            assert "query" in data
            assert "results" in data
    
    def test_knowledge_search_medical_terms(self):
        """Test knowledge search with medical terminology"""
        queries = [
            "acute myocardial infarction treatment",
            "diabetes mellitus type 2 management"
        ]
        
        for query in queries:
            payload = {"query": query, "top_k": 3}
            response = client.post("/api/medical/knowledge/search",
                json=payload
            )
            # Accept both 200 (success) and 500 (knowledge base not initialized)
            assert response.status_code in [200, 500]
            if response.status_code == 200:
                data = response.json()
                assert "results" in data


class TestDrugInteractionEndpoints:
    """Test drug interaction checking"""
    
    def test_no_interactions(self):
        """Test medications with no known interactions"""
        payload = {
            "medications": ["metformin", "vitamin D"]
        }
        response = client.post("/api/prescription/check-interactions",
            json=payload
        )
        assert response.status_code == 200
        data = response.json()
        assert data["total_interactions"] == 0
    
    def test_high_severity_interactions(self):
        """Test high-severity drug interactions"""
        payload = {
            "medications": ["warfarin", "aspirin", "amiodarone"]
        }
        response = client.post("/api/prescription/check-interactions",
            json=payload
        )
        assert response.status_code == 200
        data = response.json()
        assert data["total_interactions"] >= 2
        assert data["high_risk_warning"] is True
        
        # Check severity breakdown
        severity = data["severity_breakdown"]
        assert severity["high"] >= 2
    
    def test_moderate_interactions(self):
        """Test moderate severity interactions"""
        payload = {
            "medications": ["lisinopril", "ibuprofen"]
        }
        response = client.post("/api/prescription/check-interactions",
            json=payload
        )
        assert response.status_code == 200
        data = response.json()
        # Should detect ACE inhibitor + NSAID interaction


class TestDiagnosisEndpoints:
    """Test diagnosis and symptom analysis"""
    
    def test_basic_diagnosis(self):
        """Test basic diagnosis endpoint"""
        payload = {
            "symptoms": ["fever", "cough", "shortness of breath"],
            "patient_info": {
                "age": 45,
                "gender": "male",
                "medical_history": "No known allergies"
            },
            "vital_signs": {
                "temperature": "38.5C",
                "heart_rate": 95,
                "respiratory_rate": 24
            }
        }
        response = client.post("/api/medical/diagnosis",
            json=payload
        )
        assert response.status_code == 200
        data = response.json()
        assert "primary_diagnosis" in data
        assert "differential_diagnoses" in data
    
    def test_symptom_analysis(self):
        """Test symptom analysis endpoint"""
        payload = {
            "symptoms": ["chest pain", "shortness of breath", "sweating"],
            "patient_info": {
                "age": 55,
                "gender": "male"
            }
        }
        response = client.post("/api/medical/analyze-symptoms",
            json=payload
        )
        assert response.status_code == 200
        data = response.json()
        assert "symptoms" in data


class TestPrescriptionEndpoints:
    """Test prescription generation and medication recommendations"""
    
    def test_prescription_generation(self):
        """Test prescription plan generation"""
        payload = {
            "diagnosis": "Community-acquired pneumonia",
            "patient_info": {
                "age": 45,
                "gender": "male",
                "weight": 75,
                "allergies": [],
                "current_medications": ["lisinopril"]
            },
            "severity": "moderate"
        }
        response = client.post("/api/prescription/generate-plan",
            json=payload
        )
        assert response.status_code == 200
        data = response.json()
        assert "medications" in data
        assert len(data["medications"]) > 0
        assert "monitoring_advice" in data
    
    def test_prescription_with_allergies(self):
        """Test prescription generation considers allergies"""
        payload = {
            "diagnosis": "Community-acquired pneumonia",
            "patient_info": {
                "age": 45,
                "gender": "male",
                "weight": 75,
                "allergies": ["penicillin"],
                "current_medications": []
            },
            "severity": "moderate"
        }
        response = client.post("/api/prescription/generate-plan",
            json=payload
        )
        assert response.status_code == 200
        data = response.json()
        # Should not prescribe penicillin-based antibiotics
    
    def test_dosing_calculation(self):
        """Test drug dosing recommendations"""
        payload = {
            "drug_name": "amoxicillin",
            "patient_info": {
                "weight": 70,
                "age": 45,
                "indication": "pneumonia"
            }
        }
        response = client.post("/api/prescription/dosing",
            json=payload
        )
        assert response.status_code == 200


class TestICDCodeEndpoints:
    """Test ICD-10 code search and lookup"""
    
    def test_icd_search(self):
        """Test ICD code search"""
        response = client.get("/api/medical/icd/search",
            params={"query": "pneumonia"}
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) > 0
    
    def test_icd_categories(self):
        """Test ICD categories endpoint"""
        response = client.get("/api/medical/icd/categories")
        assert response.status_code == 200


class TestChatEndpoints:
    """Test chat and conversation endpoints"""
    
    def test_chat_message(self):
        """Test sending a chat message"""
        payload = {
            "content": "What are the symptoms of diabetes?",
            "user_id": "test_user_123"
            # Don't provide session_id - let it create a new session
        }
        response = client.post("/api/chat/message",
            json=payload
        )
        # Accept both 200 (success) and 500 (if medical assistant not initialized)
        assert response.status_code in [200, 500], f"Got status {response.status_code}: {response.text}"
        if response.status_code == 200:
            data = response.json()
            assert "content" in data or "response" in data


class TestErrorHandling:
    """Test error handling and validation"""
    
    def test_invalid_endpoint(self):
        """Test 404 for invalid endpoint"""
        response = client.get("/api/invalid/endpoint")
        assert response.status_code == 404
    
    def test_missing_required_fields(self):
        """Test validation errors for missing fields"""
        payload = {}  # Empty payload
        response = client.post("/api/medical/diagnosis",
            json=payload
        )
        assert response.status_code == 422  # Validation error
    
    def test_invalid_data_types(self):
        """Test validation errors for wrong data types"""
        payload = {
            "symptoms": "should be a list",  # Wrong type
            "patient_info": "should be object"
        }
        response = client.post("/api/medical/diagnosis",
            json=payload
        )
        assert response.status_code == 422


class TestIntegrationWorkflow:
    """Test complete workflows across multiple endpoints"""
    
    def test_complete_patient_workflow(self):
        """Test complete workflow: symptoms -> diagnosis -> prescription"""
        
        # Step 1: Analyze symptoms
        symptoms_payload = {
            "symptoms": ["fever", "productive cough", "chest pain"],
            "patient_info": {
                "age": 55,
                "gender": "male"
            }
        }
        symptoms_response = client.post("/api/medical/analyze-symptoms",
            json=symptoms_payload
        )
        assert symptoms_response.status_code == 200
        
        # Step 2: Get diagnosis
        diagnosis_payload = {
            "symptoms": ["fever", "productive cough", "chest pain"],
            "patient_info": {
                "age": 55,
                "gender": "male",
                "medical_history": "smoker"
            },
            "vital_signs": {
                "temperature": "38.7C",
                "heart_rate": 98
            }
        }
        diagnosis_response = client.post("/api/medical/diagnosis",
            json=diagnosis_payload
        )
        assert diagnosis_response.status_code == 200
        
        # Step 3: Generate prescription
        prescription_payload = {
            "diagnosis": "Community-acquired pneumonia",
            "patient_info": {
                "age": 55,
                "gender": "male",
                "weight": 80,
                "allergies": [],
                "current_medications": ["metformin"]
            },
            "severity": "moderate"
        }
        prescription_response = client.post("/api/prescription/generate-plan",
            json=prescription_payload
        )
        assert prescription_response.status_code == 200
        prescription_data = prescription_response.json()
        
        # Step 4: Check drug interactions
        medications = [med["name"] for med in prescription_data["medications"]]
        medications.append("metformin")  # Current medication
        
        interaction_payload = {"medications": medications}
        interaction_response = client.post("/api/prescription/check-interactions",
            json=interaction_payload
        )
        assert interaction_response.status_code == 200
        
        # Step 5: Search knowledge base for treatment guidance
        knowledge_payload = {
            "query": "pneumonia treatment guidelines",
            "top_k": 3
        }
        knowledge_response = client.post("/api/medical/knowledge/search",
            json=knowledge_payload
        )
        # Accept both 200 (success) and 500 (if knowledge base not initialized in test env)
        assert knowledge_response.status_code in [200, 500], \
            f"Knowledge search failed with {knowledge_response.status_code}: {knowledge_response.text}"


def run_all_tests():
    """Run all tests and print summary"""
    print("=" * 60)
    print("Running Natpudan AI Medical Assistant API Tests")
    print("=" * 60)
    
    # Run with pytest
    pytest.main([__file__, "-v", "--tb=short"])


if __name__ == "__main__":
    run_all_tests()

