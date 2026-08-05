"""HTTP API for question generation, interview evaluation, and review history."""

from collections.abc import Generator
from datetime import datetime
import logging
from typing import Annotated

from fastapi import Depends, FastAPI, Header, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from auth import router as auth_router
from database import Base, SessionLocal, engine
from models import InterviewAttempt, User
from ollama_service import evaluate_answer, generate_question, select_topic

app = FastAPI()
logger = logging.getLogger(__name__)

# SQLite has no migration runner in this project. create_all safely creates the
# new interview_attempts table without changing existing tables or records.
Base.metadata.create_all(bind=engine)

app.include_router(auth_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_db() -> Generator[Session, None, None]:
    """Provide one SQLAlchemy session per request and always close it."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(
    x_user_id: Annotated[int | None, Header()] = None,
    db: Session = Depends(get_db),
) -> User:
    """Resolve the user from the ID retained by the existing frontend login flow."""
    if x_user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication is required.",
        )

    user = db.get(User, x_user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authenticated user.",
        )
    return user


class AnswerRequest(BaseModel):
    question: str = Field(min_length=1)
    answer: str
    role: str = Field(default="General", min_length=1, max_length=120)
    topic: str = Field(default="General", min_length=1, max_length=120)
    difficulty: str = Field(default="Medium", min_length=1, max_length=32)


class HistoryItem(BaseModel):
    id: int
    role: str
    topic: str
    difficulty: str
    score: int
    created_at: datetime


class InterviewDetail(HistoryItem):
    question: str
    answer: str
    strengths: list[str]
    improvements: list[str]
    ideal_answer: str
    confidence: str


def serialize_history_item(attempt: InterviewAttempt) -> dict:
    """Keep history payloads intentionally small; answers belong to the detail API."""
    return {
        "id": attempt.id,
        "role": attempt.role,
        "topic": attempt.topic,
        "difficulty": attempt.difficulty,
        "score": attempt.score,
        "created_at": attempt.created_at,
    }


@app.get("/")
def home():
    return {"message": "AI Interview Coach Running"}


@app.get("/question")
def question(
    role: str,
    topic: str | None = None,
    difficulty: str = "Medium",
):
    """Generate a question without creating a history item until it is evaluated."""
    selected_topic = topic or select_topic(role)
    generated_question = generate_question(role, selected_topic, difficulty)
    return {
        "role": role,
        "topic": selected_topic,
        "difficulty": difficulty,
        "question": generated_question,
    }


@app.get("/history", response_model=list[HistoryItem])
def history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Return a user's evaluated attempts, excluding answer content."""
    records = (
        db.query(InterviewAttempt)
        .filter(InterviewAttempt.user_id == current_user.id)
        .order_by(InterviewAttempt.created_at.desc(), InterviewAttempt.id.desc())
        .all()
    )
    return [serialize_history_item(record) for record in records]


@app.get("/history/{interview_id}", response_model=InterviewDetail)
def interview_detail(
    interview_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Return a complete attempt only when it belongs to the logged-in user."""
    attempt = (
        db.query(InterviewAttempt)
        .filter(
            InterviewAttempt.id == interview_id,
            InterviewAttempt.user_id == current_user.id,
        )
        .first()
    )
    if attempt is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Interview not found.")

    return {
        **serialize_history_item(attempt),
        "question": attempt.question,
        "answer": attempt.answer,
        "strengths": attempt.strengths,
        "improvements": attempt.improvements,
        "ideal_answer": attempt.ideal_answer,
        "confidence": attempt.confidence,
    }


@app.post("/evaluate-answer")
def evaluate(
    data: AnswerRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Evaluate an answer with Ollama and atomically persist the complete attempt."""
    try:
        result = evaluate_answer(data.question, data.answer)
    except ValueError as exc:
        logger.exception("Ollama returned an unusable evaluation response: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="The AI returned invalid evaluation data. Please try again.",
        ) from exc

    attempt = InterviewAttempt(
        user_id=current_user.id,
        role=data.role,
        topic=data.topic,
        difficulty=data.difficulty,
        question=data.question,
        answer=data.answer,
        score=result.score,
        strengths=result.strengths,
        improvements=result.improvements,
        ideal_answer=result.ideal_answer,
        confidence=result.confidence,
    )
    try:
        db.add(attempt)
        db.commit()
        db.refresh(attempt)
    except Exception:
        db.rollback()
        logger.exception("Unable to save interview attempt for user %s", current_user.id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="The evaluation was generated but could not be saved. Please try again.",
        )

    # Preserve the existing evaluation response shape; the ID is additive for
    # clients that want to open the detail view directly.
    return {"evaluation": result.model_dump(), "interview_id": attempt.id}
