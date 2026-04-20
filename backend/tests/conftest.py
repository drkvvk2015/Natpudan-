"""
Test configuration and fixtures
"""
import pytest
import os
import sys
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

# Configure pytest-asyncio
pytest_plugins = ('pytest_asyncio',)

# Test configuration
TEST_BASE_URL = os.getenv("TEST_BASE_URL", "http://127.0.0.1:8000")

@pytest.fixture
def base_url():
    """Provide base URL for tests"""
    return TEST_BASE_URL

@pytest.fixture
def sample_patient_info():
    """Sample patient information for testing"""
    return {
        "age": 45,
        "gender": "male",
        "weight": 75,
        "allergies": [],
        "current_medications": [],
        "medical_history": "No known allergies, non-smoker"
    }

@pytest.fixture
def sample_symptoms():
    """Sample symptoms for testing"""
    return ["fever", "cough", "shortness of breath", "chest pain"]

@pytest.fixture
def sample_vital_signs():
    """Sample vital signs for testing"""
    return {
        "temperature": "38.5C",
        "heart_rate": 95,
        "blood_pressure": "130/80",
        "respiratory_rate": 24,
        "oxygen_saturation": "94%"
    }
