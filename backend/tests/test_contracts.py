from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_root_contract_and_request_id_header():
    response = client.get('/')
    assert response.status_code == 200
    data = response.json()
    assert set(data.keys()) == {'status', 'timestamp'}
    assert response.headers['X-Request-ID']


def test_health_contract():
    response = client.get('/health')
    assert response.status_code == 200
    data = response.json()
    assert {'status', 'service', 'services', 'timestamp'} <= set(data.keys())
    assert isinstance(data['services'], dict)


def test_detailed_health_contract():
    response = client.get('/health/detailed')
    assert response.status_code == 200
    data = response.json()
    assert {'status', 'uptime', 'cpu_usage', 'memory_usage', 'disk_usage', 'database_status'} <= set(data.keys())
