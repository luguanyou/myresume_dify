from starlette.testclient import TestClient

from app.main import app


def test_health_endpoint_returns_service_status():
    client = TestClient(app)

    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json() == {
        "success": True,
        "data": {
            "status": "ok",
            "service": "portfolio-api",
            "version": "1.0",
        },
        "message": "ok",
    }
