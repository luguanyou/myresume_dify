from starlette.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool

from app.api import health
from app.db.base import Base
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


def test_database_health_endpoint_returns_ok_when_required_tables_exist(monkeypatch):
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    monkeypatch.setattr(health, "engine", engine)
    client = TestClient(app)

    response = client.get("/api/health/db")

    assert response.status_code == 200
    assert response.json() == {
        "success": True,
        "data": {
            "status": "ok",
            "database": {
                "connected": True,
                "required_tables_ok": True,
            },
        },
        "message": "ok",
    }


def test_database_health_endpoint_reports_missing_schema(monkeypatch):
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    monkeypatch.setattr(health, "engine", engine)
    client = TestClient(app)

    response = client.get("/api/health/db")

    assert response.status_code == 503
    body = response.json()
    assert body["success"] is False
    assert body["message"] == "database schema is not initialized"
    assert body["data"]["database"]["connected"] is True
    assert body["data"]["database"]["required_tables_ok"] is False
    assert "projects" in body["data"]["database"]["missing_tables"]
