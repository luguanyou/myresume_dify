from typing import Annotated, Literal

from fastapi import APIRouter, Depends, File, Form, Query, UploadFile
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.admin_auth import get_current_admin
from app.api.responses import api_error, ok
from app.db.session import get_db
from app.models import AdminUser, MediaAsset, Project
from app.models.portfolio import utc_now
from app.serializers import serialize_media
from app.services.uploads import save_upload_file

router = APIRouter(prefix="/api/admin", tags=["admin-media"])


class MediaUpdateRequest(BaseModel):
    project_id: int | None = None
    purpose: str | None = Field(default=None, max_length=50)
    alt_text: str | None = Field(default=None, max_length=255)
    sort_order: int | None = None
    status: Literal["draft", "published", "hidden"] | None = None


def get_project(project_id: int | None, db: Session) -> Project | None:
    if project_id is None:
        return None
    project = db.scalar(select(Project).where(Project.id == project_id, Project.deleted_at.is_(None)))
    if project is None:
        raise api_error(404, "NOT_FOUND", "Project not found")
    return project


def ensure_project_exists(project_id: int | None, db: Session) -> None:
    get_project(project_id, db)


def set_project_cover_if_empty(project: Project | None, asset: MediaAsset) -> None:
    if project is None or project.cover_media_id is not None:
        return
    if asset.media_type != "image":
        return
    project.cover_media_id = asset.id


def get_media_or_404(media_id: int, db: Session) -> MediaAsset:
    asset = db.scalar(
        select(MediaAsset).where(
            MediaAsset.id == media_id,
            MediaAsset.deleted_at.is_(None),
        )
    )
    if asset is None:
        raise api_error(404, "NOT_FOUND", "Media asset not found")
    return asset


@router.get("/media")
def list_admin_media(
    admin: Annotated[AdminUser, Depends(get_current_admin)],
    media_type: Literal["image", "video", "document"] | None = Query(default=None),
    project_id: int | None = Query(default=None),
    purpose: str | None = Query(default=None),
    db: Session = Depends(get_db),
):
    query = select(MediaAsset).where(MediaAsset.deleted_at.is_(None))
    if media_type is not None:
        query = query.where(MediaAsset.media_type == media_type)
    if project_id is not None:
        query = query.where(MediaAsset.project_id == project_id)
    if purpose is not None:
        query = query.where(MediaAsset.purpose == purpose)

    assets = db.scalars(query.order_by(MediaAsset.sort_order.desc(), MediaAsset.id.desc())).all()
    return ok([serialize_media(asset) for asset in assets])


@router.get("/media/{media_id}")
def get_admin_media(
    media_id: int,
    admin: Annotated[AdminUser, Depends(get_current_admin)],
    db: Session = Depends(get_db),
):
    asset = get_media_or_404(media_id, db)
    return ok(serialize_media(asset))


@router.post("/media")
async def upload_admin_media(
    admin: Annotated[AdminUser, Depends(get_current_admin)],
    file: UploadFile = File(...),
    media_type: Literal["image", "video", "document"] = Form(...),
    purpose: str = Form(default="general"),
    project_id: int | None = Form(default=None),
    alt_text: str | None = Form(default=None),
    sort_order: int = Form(default=0),
    db: Session = Depends(get_db),
):
    project = get_project(project_id, db)
    stored = await save_upload_file(file, media_type, purpose)
    asset = MediaAsset(
        project_id=project_id,
        media_type=media_type,
        purpose=purpose,
        original_filename=stored.original_filename,
        stored_filename=stored.stored_filename,
        storage_path=stored.storage_path,
        public_url=stored.public_url,
        mime_type=stored.mime_type,
        file_ext=stored.file_ext,
        file_size=stored.file_size,
        alt_text=alt_text,
        sort_order=sort_order,
        status="published",
    )
    db.add(asset)
    db.flush()
    set_project_cover_if_empty(project, asset)
    if project is not None:
        db.add(project)
    db.commit()
    db.refresh(asset)
    return ok(serialize_media(asset), message="uploaded")


@router.put("/media/{media_id}")
def update_admin_media(
    media_id: int,
    payload: MediaUpdateRequest,
    admin: Annotated[AdminUser, Depends(get_current_admin)],
    db: Session = Depends(get_db),
):
    asset = get_media_or_404(media_id, db)
    update_data = payload.model_dump(exclude_unset=True)
    if "project_id" in update_data:
        ensure_project_exists(update_data["project_id"], db)

    for key, value in update_data.items():
        setattr(asset, key, value)
    db.add(asset)
    db.commit()
    db.refresh(asset)
    return ok(serialize_media(asset))


@router.delete("/media/{media_id}")
def delete_admin_media(
    media_id: int,
    admin: Annotated[AdminUser, Depends(get_current_admin)],
    db: Session = Depends(get_db),
):
    asset = get_media_or_404(media_id, db)
    asset.deleted_at = utc_now()
    db.add(asset)
    db.commit()
    return ok({"id": media_id, "deleted": True}, message="deleted")
