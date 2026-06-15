from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, UploadFile
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.admin_auth import get_current_admin
from app.api.responses import api_error, ok
from app.db.session import get_db
from app.models import AdminUser, MediaAsset, ResumeFile
from app.serializers import serialize_admin_resume
from app.services.uploads import save_upload_file

router = APIRouter(prefix="/api/admin", tags=["admin-resumes"])


def get_resume_or_404(resume_id: int, db: Session) -> ResumeFile:
    resume = db.scalar(
        select(ResumeFile).where(
            ResumeFile.id == resume_id,
            ResumeFile.deleted_at.is_(None),
        )
    )
    if resume is None:
        raise api_error(404, "NOT_FOUND", "Resume not found")
    return resume


def set_current_resume(resume: ResumeFile, db: Session) -> None:
    resumes = db.scalars(select(ResumeFile).where(ResumeFile.deleted_at.is_(None))).all()
    for item in resumes:
        item.is_current = item.id == resume.id
        db.add(item)
    resume.status = "published"
    resume.is_current = True
    db.add(resume)


@router.get("/resumes")
def list_admin_resumes(
    admin: Annotated[AdminUser, Depends(get_current_admin)],
    db: Session = Depends(get_db),
):
    resumes = db.scalars(
        select(ResumeFile).where(ResumeFile.deleted_at.is_(None)).order_by(ResumeFile.id.desc())
    ).all()
    return ok([serialize_admin_resume(resume) for resume in resumes])


@router.post("/resumes")
async def upload_admin_resume(
    admin: Annotated[AdminUser, Depends(get_current_admin)],
    file: UploadFile = File(...),
    title: str = Form(...),
    version_label: str | None = Form(default=None),
    set_current: bool = Form(default=False),
    db: Session = Depends(get_db),
):
    stored = await save_upload_file(file, "document", "resume")
    media = MediaAsset(
        media_type="document",
        purpose="resume",
        original_filename=stored.original_filename,
        stored_filename=stored.stored_filename,
        storage_path=stored.storage_path,
        public_url=stored.public_url,
        mime_type=stored.mime_type,
        file_ext=stored.file_ext,
        file_size=stored.file_size,
        alt_text=title,
        status="published",
    )
    db.add(media)
    db.flush()

    resume = ResumeFile(
        title=title,
        media_id=media.id,
        version_label=version_label,
        is_current=False,
        status="published",
    )
    db.add(resume)
    db.flush()

    if set_current:
        set_current_resume(resume, db)

    db.commit()
    db.refresh(resume)
    return ok(serialize_admin_resume(resume), message="uploaded")


@router.put("/resumes/{resume_id}/current")
def set_admin_resume_current(
    resume_id: int,
    admin: Annotated[AdminUser, Depends(get_current_admin)],
    db: Session = Depends(get_db),
):
    resume = get_resume_or_404(resume_id, db)
    set_current_resume(resume, db)
    db.commit()
    db.refresh(resume)
    return ok(serialize_admin_resume(resume))
