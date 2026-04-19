import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.mark.integration
def test_health_endpoint_available():
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    payload = response.json()
    assert payload.get("status") in {"healthy", "ok"}
