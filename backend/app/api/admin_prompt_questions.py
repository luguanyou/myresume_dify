from typing import Annotated, Literal

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.admin_auth import get_current_admin
from app.api.responses import api_error, ok
from app.db.session import get_db
from app.models import AdminUser, PromptQuestion
from app.models.portfolio import utc_now
from app.serializers import serialize_admin_prompt_question

router = APIRouter(prefix="/api/admin", tags=["admin-prompt-questions"])


class PromptQuestionCreateRequest(BaseModel):
    question: str = Field(min_length=1, max_length=300)
    category: str | None = Field(default=None, max_length=80)
    sort_order: int = 0
    status: Literal["draft", "published", "hidden"] = "published"


class PromptQuestionUpdateRequest(BaseModel):
    question: str | None = Field(default=None, min_length=1, max_length=300)
    category: str | None = Field(default=None, max_length=80)
    sort_order: int | None = None
    status: Literal["draft", "published", "hidden"] | None = None


def get_question_or_404(question_id: int, db: Session) -> PromptQuestion:
    question = db.scalar(
        select(PromptQuestion).where(
            PromptQuestion.id == question_id,
            PromptQuestion.deleted_at.is_(None),
        )
    )
    if question is None:
        raise api_error(404, "NOT_FOUND", "Prompt question not found")
    return question


@router.get("/prompt-questions")
def list_admin_prompt_questions(
    admin: Annotated[AdminUser, Depends(get_current_admin)],
    db: Session = Depends(get_db),
):
    questions = db.scalars(
        select(PromptQuestion)
        .where(PromptQuestion.deleted_at.is_(None))
        .order_by(PromptQuestion.sort_order.desc(), PromptQuestion.id.asc())
    ).all()
    return ok([serialize_admin_prompt_question(question) for question in questions])


@router.get("/prompt-questions/{question_id}")
def get_admin_prompt_question(
    question_id: int,
    admin: Annotated[AdminUser, Depends(get_current_admin)],
    db: Session = Depends(get_db),
):
    question = get_question_or_404(question_id, db)
    return ok(serialize_admin_prompt_question(question))


@router.post("/prompt-questions")
def create_admin_prompt_question(
    payload: PromptQuestionCreateRequest,
    admin: Annotated[AdminUser, Depends(get_current_admin)],
    db: Session = Depends(get_db),
):
    question = PromptQuestion(**payload.model_dump())
    db.add(question)
    db.commit()
    db.refresh(question)
    return ok(serialize_admin_prompt_question(question), message="created")


@router.put("/prompt-questions/{question_id}")
def update_admin_prompt_question(
    question_id: int,
    payload: PromptQuestionUpdateRequest,
    admin: Annotated[AdminUser, Depends(get_current_admin)],
    db: Session = Depends(get_db),
):
    question = get_question_or_404(question_id, db)
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(question, key, value)
    db.add(question)
    db.commit()
    db.refresh(question)
    return ok(serialize_admin_prompt_question(question))


@router.delete("/prompt-questions/{question_id}")
def delete_admin_prompt_question(
    question_id: int,
    admin: Annotated[AdminUser, Depends(get_current_admin)],
    db: Session = Depends(get_db),
):
    question = get_question_or_404(question_id, db)
    question.deleted_at = utc_now()
    db.add(question)
    db.commit()
    return ok({"id": question_id, "deleted": True}, message="deleted")
