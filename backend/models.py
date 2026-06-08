from sqlalchemy import Column, Integer, String
from database import Base


class InterviewHistory(Base):
    __tablename__ = "interview_history"

    id = Column(Integer, primary_key=True, index=True)
    role = Column(String)
    question = Column(String)
    created_at = Column(String)