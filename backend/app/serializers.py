from datetime import datetime
from decimal import Decimal
from typing import Any

from app.core.config import settings
from app.models import AdminUser, MediaAsset, Project, PromptQuestion, ResumeFile, SiteProfile


def isoformat(value: datetime | None) -> str | None:
    return value.isoformat() if value else None


def json_value(value: Any, default: Any) -> Any:
    return default if value is None else value


def public_api_url(path: str) -> str:
    base = settings.public_api_base_url.rstrip("/") or "/api"
    normalized_path = path if path.startswith("/") else f"/{path}"
    return f"{base}{normalized_path}"


def public_asset_url(url: str | None) -> str | None:
    if not url:
        return url

    upload_base = settings.public_upload_base_url.rstrip("/") or "/uploads"
    if upload_base != "/uploads" and url.startswith("/uploads/"):
        return f"{upload_base}{url.removeprefix('/uploads')}"
    return url


def serialize_media(asset: MediaAsset | None) -> dict[str, Any] | None:
    if asset is None:
        return None

    return {
        "id": asset.id,
        "project_id": asset.project_id,
        "media_type": asset.media_type,
        "purpose": asset.purpose,
        "original_filename": asset.original_filename,
        "stored_filename": asset.stored_filename,
        "url": public_asset_url(asset.public_url),
        "public_url": public_asset_url(asset.public_url),
        "mime_type": asset.mime_type,
        "file_ext": asset.file_ext,
        "file_size": asset.file_size,
        "width": asset.width,
        "height": asset.height,
        "duration_seconds": float(asset.duration_seconds) if isinstance(asset.duration_seconds, Decimal) else asset.duration_seconds,
        "alt_text": asset.alt_text,
        "sort_order": asset.sort_order,
        "metadata": json_value(asset.metadata_, {}),
        "created_at": isoformat(asset.created_at),
    }


def serialize_project_list_item(project: Project, cover_media: MediaAsset | None) -> dict[str, Any]:
    return {
        "id": project.id,
        "slug": project.slug,
        "title": project.title,
        "subtitle": project.subtitle,
        "summary": project.summary,
        "project_type": project.project_type,
        "role": project.role,
        "tech_stack": json_value(project.tech_stack, []),
        "cover_media": serialize_cover_media(cover_media),
        "is_featured": project.is_featured,
        "sort_order": project.sort_order,
    }


def serialize_project_detail(project: Project, media: list[MediaAsset]) -> dict[str, Any]:
    return {
        "id": project.id,
        "slug": project.slug,
        "title": project.title,
        "subtitle": project.subtitle,
        "summary": project.summary,
        "project_type": project.project_type,
        "background": project.background,
        "goals": project.goals,
        "features": json_value(project.features, []),
        "role": project.role,
        "challenges": json_value(project.challenges, []),
        "solutions": json_value(project.solutions, []),
        "tech_stack": json_value(project.tech_stack, []),
        "links": json_value(project.links, []),
        "cover_media": serialize_cover_media(next((item for item in media if item.id == project.cover_media_id), None)),
        "media": [serialize_media(item) for item in media],
    }


def serialize_cover_media(asset: MediaAsset | None) -> dict[str, Any] | None:
    if asset is None:
        return None
    return {
        "id": asset.id,
        "url": public_asset_url(asset.public_url),
        "media_type": asset.media_type,
    }


def serialize_resume(resume: ResumeFile) -> dict[str, Any]:
    return {
        "id": resume.id,
        "title": resume.title,
        "media_id": resume.media_id,
        "version_label": resume.version_label,
        "download_url": public_api_url("/resume/download"),
        "updated_at": isoformat(resume.updated_at),
    }


def serialize_admin_resume(resume: ResumeFile) -> dict[str, Any]:
    return {
        "id": resume.id,
        "title": resume.title,
        "media_id": resume.media_id,
        "version_label": resume.version_label,
        "is_current": resume.is_current,
        "status": resume.status,
        "media": serialize_media(resume.media),
        "download_url": public_api_url("/resume/download") if resume.is_current else None,
        "created_at": isoformat(resume.created_at),
        "updated_at": isoformat(resume.updated_at),
    }


def serialize_site_profile(profile: SiteProfile) -> dict[str, Any]:
    return {
        "owner_name": profile.owner_name,
        "headline": profile.headline,
        "summary": profile.summary,
        "email": profile.email,
        "phone": profile.phone,
        "wechat": profile.wechat,
        "github_url": profile.github_url,
        "portfolio_url": profile.portfolio_url,
        "extra_links": json_value(profile.extra_links, []),
    }


def serialize_admin_site_profile(profile: SiteProfile) -> dict[str, Any]:
    data = serialize_site_profile(profile)
    data.update(
        {
            "id": profile.id,
            "status": profile.status,
            "created_at": isoformat(profile.created_at),
            "updated_at": isoformat(profile.updated_at),
        }
    )
    return data


def serialize_prompt_question(question: PromptQuestion) -> dict[str, Any]:
    return {
        "id": question.id,
        "question": question.question,
        "category": question.category,
        "sort_order": question.sort_order,
    }


def serialize_admin_prompt_question(question: PromptQuestion) -> dict[str, Any]:
    return {
        "id": question.id,
        "question": question.question,
        "category": question.category,
        "sort_order": question.sort_order,
        "status": question.status,
        "created_at": isoformat(question.created_at),
        "updated_at": isoformat(question.updated_at),
    }


def serialize_admin_user(admin: AdminUser) -> dict[str, Any]:
    return {
        "id": admin.id,
        "username": admin.username,
        "display_name": admin.display_name,
        "email": admin.email,
        "status": admin.status,
        "last_login_at": isoformat(admin.last_login_at),
    }
