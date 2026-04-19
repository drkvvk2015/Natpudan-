import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.mark.integration
def test_metrics_endpoint_responds_or_gracefully_unavailable():
    client = TestClient(app)
    response = client.get("/metrics")
    assert response.status_code in {200, 503}
