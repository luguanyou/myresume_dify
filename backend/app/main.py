from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse

from app.api.admin_auth import router as admin_auth_router
from app.api.admin_media import router as admin_media_router
from app.api.admin_prompt_questions import router as admin_prompt_questions_router
from app.api.admin_projects import router as admin_projects_router
from app.api.admin_resumes import router as admin_resumes_router
from app.api.admin_site import router as admin_site_router
from app.api.chat import router as chat_router
from app.api.health import router as health_router
from app.api.public import router as public_router
from app.core.config import settings


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.api_title,
        version=settings.api_version,
        root_path=settings.app_root_path.rstrip("/"),
    )

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        if isinstance(exc.detail, dict) and exc.detail.get("success") is False:
            return JSONResponse(status_code=exc.status_code, content=exc.detail)
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})

    app.add_middleware(
        CORSMiddleware,
        allow_origins=[origin.strip() for origin in settings.cors_origins.split(",") if origin.strip()],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    upload_base_url = settings.public_upload_base_url.rstrip("/") or "/uploads"

    @app.get(f"{upload_base_url}/{{file_path:path}}", include_in_schema=False)
    async def uploaded_file(file_path: str):
        upload_root = Path(settings.upload_dir).resolve()
        requested_path = (upload_root / file_path).resolve()
        if upload_root not in requested_path.parents and requested_path != upload_root:
            raise HTTPException(status_code=404, detail="File not found")
        if not requested_path.is_file():
            raise HTTPException(status_code=404, detail="File not found")
        return FileResponse(requested_path)

    app.include_router(health_router)
    app.include_router(public_router)
    app.include_router(chat_router)
    app.include_router(admin_auth_router)
    app.include_router(admin_projects_router)
    app.include_router(admin_media_router)
    app.include_router(admin_resumes_router)
    app.include_router(admin_site_router)
    app.include_router(admin_prompt_questions_router)
    return app


app = create_app()
