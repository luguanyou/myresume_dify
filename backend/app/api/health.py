from fastapi import APIRouter
from fastapi import Response, status
from sqlalchemy import inspect, text
from sqlalchemy.exc import SQLAlchemyError

from app.core.config import settings
from app.db.session import engine

router = APIRouter(prefix="/api", tags=["health"])

REQUIRED_TABLES = {
    "admin_users",
    "media_assets",
    "projects",
    "prompt_questions",
    "resume_files",
    "site_profile",
}


@router.get("/health")
def get_health():
    return {
        "success": True,
        "data": {
            "status": "ok",
            "service": settings.service_name,
            "version": settings.api_version,
        },
        "message": "ok",
    }


@router.get("/health/db")
def get_database_health(response: Response):
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
            existing_tables = set(inspect(connection).get_table_names())
    except SQLAlchemyError as exc:
        original = getattr(exc, "orig", exc)
        error_code = original.args[0] if getattr(original, "args", None) else None
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return {
            "success": False,
            "data": {
                "status": "error",
                "database": {
                    "connected": False,
                    "required_tables_ok": False,
                    "error_type": type(original).__name__,
                    "error_code": error_code,
                },
            },
            "message": "database unavailable",
        }

    missing_tables = sorted(REQUIRED_TABLES - existing_tables)
    if missing_tables:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return {
            "success": False,
            "data": {
                "status": "error",
                "database": {
                    "connected": True,
                    "required_tables_ok": False,
                    "missing_tables": missing_tables,
                },
            },
            "message": "database schema is not initialized",
        }

    return {
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
