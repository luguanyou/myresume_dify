from pathlib import Path

from fastapi import APIRouter, Depends, Query
from fastapi.responses import FileResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.responses import api_error, ok
from app.db.session import get_db
from app.models import MediaAsset, Project, PromptQuestion, ResumeFile, SiteProfile
from app.serializers import (
    serialize_project_detail,
    serialize_project_list_item,
    serialize_prompt_question,
    serialize_resume,
    serialize_site_profile,
)

router = APIRouter(prefix="/api", tags=["public"])


@router.get("/projects")
def list_projects(
    featured: bool | None = Query(default=None),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    query = select(Project).where(Project.status == "published", Project.deleted_at.is_(None))
    if featured is True:
        query = query.where(Project.is_featured.is_(True))
    projects = db.scalars(query.order_by(Project.sort_order.desc(), Project.id.desc()).limit(limit)).all()

    cover_ids = [project.cover_media_id for project in projects if project.cover_media_id is not None]
    media_by_id = {}
    if cover_ids:
        cover_media = db.scalars(
            select(MediaAsset).where(
                MediaAsset.id.in_(cover_ids),
                MediaAsset.status == "published",
                MediaAsset.deleted_at.is_(None),
            )
        ).all()
        media_by_id = {asset.id: asset for asset in cover_media}

    return ok([serialize_project_list_item(project, media_by_id.get(project.cover_media_id)) for project in projects])


@router.get("/projects/{project_id}")
def get_project(project_id: int, db: Session = Depends(get_db)):
    project = db.scalar(
        select(Project).where(
            Project.id == project_id,
            Project.status == "published",
            Project.deleted_at.is_(None),
        )
    )
    if project is None:
        raise api_error(404, "NOT_FOUND", "Project not found")

    media = db.scalars(
        select(MediaAsset)
        .where(
            MediaAsset.project_id == project.id,
            MediaAsset.status == "published",
            MediaAsset.deleted_at.is_(None),
        )
        .order_by(MediaAsset.sort_order.desc(), MediaAsset.id.asc())
    ).all()
    return ok(serialize_project_detail(project, list(media)))


@router.get("/resume/current")
def get_current_resume(db: Session = Depends(get_db)):
    resume = db.scalar(
        select(ResumeFile)
        .where(
            ResumeFile.is_current.is_(True),
            ResumeFile.status == "published",
            ResumeFile.deleted_at.is_(None),
        )
        .order_by(ResumeFile.id.desc())
        .limit(1)
    )
    if resume is None:
        raise api_error(404, "NOT_FOUND", "Current resume not found")
    return ok(serialize_resume(resume))


@router.get("/resume/download")
def download_current_resume(db: Session = Depends(get_db)):
    resume = db.scalar(
        select(ResumeFile)
        .where(
            ResumeFile.is_current.is_(True),
            ResumeFile.status == "published",
            ResumeFile.deleted_at.is_(None),
        )
        .order_by(ResumeFile.id.desc())
        .limit(1)
    )
    if resume is None or resume.media is None:
        raise api_error(404, "NOT_FOUND", "Current resume not found")

    file_path = Path(resume.media.storage_path)
    if not file_path.exists():
        raise api_error(404, "NOT_FOUND", "Resume file not found")

    return FileResponse(
        path=file_path,
        media_type=resume.media.mime_type or "application/pdf",
        filename=resume.media.original_filename or "resume.pdf",
    )


@router.get("/site/profile")
def get_site_profile(db: Session = Depends(get_db)):
    profile = db.scalar(
        select(SiteProfile)
        .where(SiteProfile.status == "published")
        .order_by(SiteProfile.id.asc())
        .limit(1)
    )
    if profile is None:
        raise api_error(404, "NOT_FOUND", "Site profile not found")
    return ok(serialize_site_profile(profile))


@router.get("/prompt-questions")
def list_prompt_questions(db: Session = Depends(get_db)):
    questions = db.scalars(
        select(PromptQuestion)
        .where(PromptQuestion.status == "published", PromptQuestion.deleted_at.is_(None))
        .order_by(PromptQuestion.sort_order.desc(), PromptQuestion.id.asc())
    ).all()
    return ok([serialize_prompt_question(question) for question in questions])
