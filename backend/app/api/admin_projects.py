from typing import Annotated, Any, Literal

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, Field
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.api.admin_auth import get_current_admin
from app.api.responses import api_error, ok
from app.db.session import get_db
from app.models import AdminUser, Project
from app.models.portfolio import utc_now

router = APIRouter(prefix="/api/admin", tags=["admin-projects"])


class ProjectCreateRequest(BaseModel):
    slug: str = Field(min_length=1, max_length=100)
    title: str = Field(min_length=1, max_length=120)
    subtitle: str | None = Field(default=None, max_length=200)
    summary: str = Field(min_length=1, max_length=500)
    project_type: str = Field(min_length=1, max_length=60)
    background: str | None = None
    goals: str | None = None
    role: str | None = None
    features: list[str] | None = None
    challenges: list[str] | None = None
    solutions: list[str] | None = None
    tech_stack: list[str] = Field(default_factory=list)
    links: list[dict[str, Any]] | None = None
    cover_media_id: int | None = None
    is_featured: bool = False
    sort_order: int = 0
    status: Literal["draft", "published", "hidden"] = "published"


class ProjectUpdateRequest(BaseModel):
    slug: str | None = Field(default=None, min_length=1, max_length=100)
    title: str | None = Field(default=None, min_length=1, max_length=120)
    subtitle: str | None = Field(default=None, max_length=200)
    summary: str | None = Field(default=None, min_length=1, max_length=500)
    project_type: str | None = Field(default=None, min_length=1, max_length=60)
    background: str | None = None
    goals: str | None = None
    role: str | None = None
    features: list[str] | None = None
    challenges: list[str] | None = None
    solutions: list[str] | None = None
    tech_stack: list[str] | None = None
    links: list[dict[str, Any]] | None = None
    cover_media_id: int | None = None
    is_featured: bool | None = None
    sort_order: int | None = None
    status: Literal["draft", "published", "hidden"] | None = None


def serialize_admin_project(project: Project) -> dict:
    return {
        "id": project.id,
        "slug": project.slug,
        "title": project.title,
        "subtitle": project.subtitle,
        "summary": project.summary,
        "project_type": project.project_type,
        "background": project.background,
        "goals": project.goals,
        "role": project.role,
        "features": project.features or [],
        "challenges": project.challenges or [],
        "solutions": project.solutions or [],
        "tech_stack": project.tech_stack or [],
        "links": project.links or [],
        "cover_media_id": project.cover_media_id,
        "status": project.status,
        "is_featured": project.is_featured,
        "sort_order": project.sort_order,
        "created_at": project.created_at.isoformat() if project.created_at else None,
        "updated_at": project.updated_at.isoformat() if project.updated_at else None,
    }


def get_admin_project_or_404(project_id: int, db: Session) -> Project:
    project = db.scalar(
        select(Project).where(
            Project.id == project_id,
            Project.deleted_at.is_(None),
        )
    )
    if project is None:
        raise api_error(404, "NOT_FOUND", "Project not found")
    return project


@router.get("/projects")
def list_admin_projects(
    admin: Annotated[AdminUser, Depends(get_current_admin)],
    status: Literal["draft", "published", "hidden"] | None = Query(default=None),
    keyword: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    query = select(Project).where(Project.deleted_at.is_(None))
    if status is not None:
        query = query.where(Project.status == status)
    if keyword:
        pattern = f"%{keyword}%"
        query = query.where(or_(Project.title.ilike(pattern), Project.summary.ilike(pattern)))

    projects = db.scalars(
        query.order_by(Project.sort_order.desc(), Project.id.desc()).offset((page - 1) * page_size).limit(page_size)
    ).all()
    return ok([serialize_admin_project(project) for project in projects])


@router.get("/projects/{project_id}")
def get_admin_project(
    project_id: int,
    admin: Annotated[AdminUser, Depends(get_current_admin)],
    db: Session = Depends(get_db),
):
    project = get_admin_project_or_404(project_id, db)
    return ok(serialize_admin_project(project))


@router.post("/projects")
def create_admin_project(
    payload: ProjectCreateRequest,
    admin: Annotated[AdminUser, Depends(get_current_admin)],
    db: Session = Depends(get_db),
):
    existing = db.scalar(select(Project).where(Project.slug == payload.slug, Project.deleted_at.is_(None)))
    if existing is not None:
        raise api_error(400, "BAD_REQUEST", "Project slug already exists")

    project = Project(**payload.model_dump())
    db.add(project)
    db.commit()
    db.refresh(project)
    return ok(serialize_admin_project(project), message="created")


@router.put("/projects/{project_id}")
def update_admin_project(
    project_id: int,
    payload: ProjectUpdateRequest,
    admin: Annotated[AdminUser, Depends(get_current_admin)],
    db: Session = Depends(get_db),
):
    project = get_admin_project_or_404(project_id, db)
    update_data = payload.model_dump(exclude_unset=True)

    if "slug" in update_data and update_data["slug"] != project.slug:
        existing = db.scalar(
            select(Project).where(
                Project.slug == update_data["slug"],
                Project.id != project.id,
                Project.deleted_at.is_(None),
            )
        )
        if existing is not None:
            raise api_error(400, "BAD_REQUEST", "Project slug already exists")

    for key, value in update_data.items():
        setattr(project, key, value)
    db.add(project)
    db.commit()
    db.refresh(project)
    return ok(serialize_admin_project(project))


@router.delete("/projects/{project_id}")
def delete_admin_project(
    project_id: int,
    admin: Annotated[AdminUser, Depends(get_current_admin)],
    db: Session = Depends(get_db),
):
    project = get_admin_project_or_404(project_id, db)
    project.deleted_at = utc_now()
    db.add(project)
    db.commit()
    return ok({"id": project_id, "deleted": True}, message="deleted")
