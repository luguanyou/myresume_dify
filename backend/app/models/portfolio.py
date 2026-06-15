from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import BigInteger, Boolean, DateTime, ForeignKey, Index, Integer, JSON, Numeric, String, Text
from sqlalchemy.dialects import mysql
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


def unsigned_bigint():
    return BigInteger().with_variant(mysql.BIGINT(unsigned=True), "mysql").with_variant(Integer, "sqlite")


def primary_key_column():
    return mapped_column(unsigned_bigint(), primary_key=True, autoincrement=True)


def utc_now() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


class Project(Base):
    __tablename__ = "projects"
    __table_args__ = (
        Index("idx_projects_status_sort", "status", "sort_order", "id"),
        Index("idx_projects_featured_sort", "is_featured", "sort_order", "id"),
        Index("idx_projects_cover_media_id", "cover_media_id"),
    )

    id: Mapped[int] = primary_key_column()
    slug: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    title: Mapped[str] = mapped_column(String(120), nullable=False)
    subtitle: Mapped[str | None] = mapped_column(String(200), nullable=True)
    summary: Mapped[str] = mapped_column(String(500), nullable=False)
    project_type: Mapped[str] = mapped_column(String(60), nullable=False)
    background: Mapped[str | None] = mapped_column(Text, nullable=True)
    goals: Mapped[str | None] = mapped_column(Text, nullable=True)
    role: Mapped[str | None] = mapped_column(Text, nullable=True)
    features: Mapped[list[str] | None] = mapped_column(JSON, nullable=True)
    challenges: Mapped[list[str] | None] = mapped_column(JSON, nullable=True)
    solutions: Mapped[list[str] | None] = mapped_column(JSON, nullable=True)
    tech_stack: Mapped[list[str]] = mapped_column(JSON, nullable=False)
    links: Mapped[list[dict] | None] = mapped_column(JSON, nullable=True)
    cover_media_id: Mapped[int | None] = mapped_column(unsigned_bigint(), nullable=True)
    is_featured: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="published")
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=utc_now, onupdate=utc_now)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    media_assets: Mapped[list["MediaAsset"]] = relationship(back_populates="project")


class MediaAsset(Base):
    __tablename__ = "media_assets"
    __table_args__ = (
        Index("idx_media_project", "project_id", "sort_order", "id"),
        Index("idx_media_type_purpose", "media_type", "purpose"),
        Index("idx_media_status", "status"),
    )

    id: Mapped[int] = primary_key_column()
    project_id: Mapped[int | None] = mapped_column(
        unsigned_bigint(),
        ForeignKey("projects.id", ondelete="SET NULL"),
        nullable=True,
    )
    media_type: Mapped[str] = mapped_column(String(30), nullable=False)
    purpose: Mapped[str] = mapped_column(String(50), nullable=False, default="general")
    original_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    stored_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    storage_path: Mapped[str] = mapped_column(String(500), nullable=False)
    public_url: Mapped[str] = mapped_column(String(500), nullable=False)
    mime_type: Mapped[str] = mapped_column(String(120), nullable=False)
    file_ext: Mapped[str] = mapped_column(String(20), nullable=False)
    file_size: Mapped[int] = mapped_column(unsigned_bigint(), nullable=False)
    width: Mapped[int | None] = mapped_column(Integer, nullable=True)
    height: Mapped[int | None] = mapped_column(Integer, nullable=True)
    duration_seconds: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)
    alt_text: Mapped[str | None] = mapped_column(String(255), nullable=True)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="published")
    metadata_: Mapped[dict | None] = mapped_column("metadata", JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=utc_now, onupdate=utc_now)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    project: Mapped[Project | None] = relationship(back_populates="media_assets")
    resume_files: Mapped[list["ResumeFile"]] = relationship(back_populates="media")


class ResumeFile(Base):
    __tablename__ = "resume_files"
    __table_args__ = (
        Index("idx_resume_current_status", "is_current", "status"),
        Index("idx_resume_media_id", "media_id"),
    )

    id: Mapped[int] = primary_key_column()
    title: Mapped[str] = mapped_column(String(160), nullable=False)
    media_id: Mapped[int] = mapped_column(
        unsigned_bigint(),
        ForeignKey("media_assets.id", ondelete="RESTRICT"),
        nullable=False,
    )
    version_label: Mapped[str | None] = mapped_column(String(60), nullable=True)
    is_current: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="published")
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=utc_now, onupdate=utc_now)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    media: Mapped[MediaAsset] = relationship(back_populates="resume_files")


class AdminUser(Base):
    __tablename__ = "admin_users"
    __table_args__ = (Index("idx_admin_status", "status"),)

    id: Mapped[int] = primary_key_column()
    username: Mapped[str] = mapped_column(String(80), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    display_name: Mapped[str | None] = mapped_column(String(120), nullable=True)
    email: Mapped[str | None] = mapped_column(String(160), nullable=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="active")
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=utc_now, onupdate=utc_now)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)


class SiteProfile(Base):
    __tablename__ = "site_profile"
    __table_args__ = (Index("idx_site_profile_status", "status"),)

    id: Mapped[int] = primary_key_column()
    owner_name: Mapped[str] = mapped_column(String(80), nullable=False)
    headline: Mapped[str] = mapped_column(String(160), nullable=False)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    email: Mapped[str | None] = mapped_column(String(160), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(80), nullable=True)
    wechat: Mapped[str | None] = mapped_column(String(120), nullable=True)
    github_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    portfolio_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    extra_links: Mapped[list[dict] | None] = mapped_column(JSON, nullable=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="published")
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=utc_now, onupdate=utc_now)


class PromptQuestion(Base):
    __tablename__ = "prompt_questions"
    __table_args__ = (
        Index("idx_prompt_status_sort", "status", "sort_order", "id"),
        Index("idx_prompt_category", "category"),
    )

    id: Mapped[int] = primary_key_column()
    question: Mapped[str] = mapped_column(String(300), nullable=False)
    category: Mapped[str | None] = mapped_column(String(80), nullable=True)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="published")
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=utc_now, onupdate=utc_now)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
