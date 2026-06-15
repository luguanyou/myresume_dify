from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.responses import api_error, ok
from app.core.config import settings
from app.db.session import get_db
from app.models import AdminUser
from app.security import create_access_token, decode_access_token, verify_password
from app.serializers import serialize_admin_user
from app.models.portfolio import utc_now

router = APIRouter(prefix="/api/admin/auth", tags=["admin-auth"])
bearer_scheme = HTTPBearer(auto_error=False)


class AdminLoginRequest(BaseModel):
    username: str = Field(min_length=1, max_length=80)
    password: str = Field(min_length=1, max_length=255)


def get_current_admin(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
    db: Session = Depends(get_db),
) -> AdminUser:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise api_error(401, "UNAUTHORIZED", "Missing bearer token")

    payload = decode_access_token(credentials.credentials)
    if payload is None or not payload.get("sub"):
        raise api_error(401, "UNAUTHORIZED", "Invalid or expired token")

    try:
        admin_id = int(payload["sub"])
    except (TypeError, ValueError):
        raise api_error(401, "UNAUTHORIZED", "Invalid or expired token")

    admin = db.scalar(
        select(AdminUser).where(
            AdminUser.id == admin_id,
            AdminUser.status == "active",
            AdminUser.deleted_at.is_(None),
        )
    )
    if admin is None:
        raise api_error(401, "UNAUTHORIZED", "Invalid or expired token")
    return admin


@router.post("/login")
def login(payload: AdminLoginRequest, db: Session = Depends(get_db)):
    admin = db.scalar(
        select(AdminUser).where(
            AdminUser.username == payload.username,
            AdminUser.status == "active",
            AdminUser.deleted_at.is_(None),
        )
    )

    if admin is None or not verify_password(payload.password, admin.password_hash):
        raise api_error(401, "UNAUTHORIZED", "Invalid username or password")

    admin.last_login_at = utc_now()
    db.add(admin)
    db.commit()
    db.refresh(admin)

    token = create_access_token(admin.id, timedelta(seconds=settings.admin_token_expire_seconds))
    return ok(
        {
            "access_token": token,
            "token_type": "bearer",
            "expires_in": settings.admin_token_expire_seconds,
            "admin": serialize_admin_user(admin),
        }
    )


@router.get("/me")
def me(admin: Annotated[AdminUser, Depends(get_current_admin)]):
    return ok(serialize_admin_user(admin))


@router.post("/logout")
def logout(admin: Annotated[AdminUser, Depends(get_current_admin)]):
    return ok({"logged_out": True})
