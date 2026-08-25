from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import relationship
from database import Base


class InterviewHistory(Base):
    __tablename__ = "interview_history"

    id = Column(Integer, primary_key=True, index=True)
    role = Column(String)
    question = Column(String)
    created_at = Column(String)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    email = Column(String, unique=True, index=True)
    password_hash = Column(String, nullable=False)

    interview_attempts = relationship(
        "InterviewAttempt",
        back_populates="user",
        cascade="all, delete-orphan",
    )


class InterviewAttempt(Base):
    """A complete, evaluated interview response submitted by a user."""

    __tablename__ = "interview_attempts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    role = Column(String(120), nullable=False)
    topic = Column(String(120), nullable=False)
    difficulty = Column(String(32), nullable=False)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    score = Column(Integer, nullable=False)
    strengths = Column(JSON, nullable=False, default=list)
    improvements = Column(JSON, nullable=False, default=list)
    ideal_answer = Column(Text, nullable=False)
    confidence = Column(String(16), nullable=False)
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        index=True,
    )

    user = relationship("User", back_populates="interview_attempts")
