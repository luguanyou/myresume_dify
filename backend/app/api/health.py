from fastapi import APIRouter

from app.core.config import settings

router = APIRouter(prefix="/api", tags=["health"])


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
