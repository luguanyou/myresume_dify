from typing import Annotated, Literal

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.admin_auth import get_current_admin
from app.api.responses import ok
from app.db.session import get_db
from app.models import AdminUser, SiteProfile
from app.serializers import serialize_admin_site_profile

router = APIRouter(prefix="/api/admin", tags=["admin-site"])


class SiteProfileRequest(BaseModel):
    owner_name: str = Field(min_length=1, max_length=80)
    headline: str = Field(min_length=1, max_length=160)
    summary: str | None = None
    email: str | None = Field(default=None, max_length=160)
    phone: str | None = Field(default=None, max_length=80)
    wechat: str | None = Field(default=None, max_length=120)
    github_url: str | None = Field(default=None, max_length=500)
    portfolio_url: str | None = Field(default=None, max_length=500)
    extra_links: list[dict] | None = None
    status: Literal["published", "hidden"] = "published"


def get_or_create_profile(db: Session) -> SiteProfile:
    profile = db.scalar(select(SiteProfile).order_by(SiteProfile.id.asc()).limit(1))
    if profile is None:
        profile = SiteProfile(owner_name="", headline="", status="published", extra_links=[])
        db.add(profile)
        db.flush()
    return profile


@router.get("/site/profile")
def get_admin_site_profile(
    admin: Annotated[AdminUser, Depends(get_current_admin)],
    db: Session = Depends(get_db),
):
    profile = get_or_create_profile(db)
    db.commit()
    db.refresh(profile)
    return ok(serialize_admin_site_profile(profile))


@router.put("/site/profile")
def update_admin_site_profile(
    payload: SiteProfileRequest,
    admin: Annotated[AdminUser, Depends(get_current_admin)],
    db: Session = Depends(get_db),
):
    profile = get_or_create_profile(db)
    for key, value in payload.model_dump().items():
        setattr(profile, key, value)
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return ok(serialize_admin_site_profile(profile))
