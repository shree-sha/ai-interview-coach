from fastapi import FastAPI, HTTPException
from datetime import datetime
import logging
from pydantic import BaseModel
from ollama_service import generate_question, evaluate_answer
from database import engine, SessionLocal
from models import InterviewHistory, Base
from fastapi.middleware.cors import CORSMiddleware
from auth import router as auth_router

app = FastAPI()
logger = logging.getLogger(__name__)

Base.metadata.create_all(bind=engine)

app.include_router(auth_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class AnswerRequest(BaseModel):
    question: str
    answer: str

@app.get("/")
def home():
    return {"message": "AI Interview Coach Running"}


@app.get("/question")
def question(role: str):

    generated_question = generate_question(role)

    db = SessionLocal()

    record = InterviewHistory(
        role=role,
        question=generated_question,
        created_at=str(datetime.now())
    )

    db.add(record)
    db.commit()

    db.close()

    return {
        "role": role,
        "question": generated_question
    }

@app.get("/history")
def history():

    db = SessionLocal()

    records = db.query(
        InterviewHistory
    ).all()

    db.close()

    return records

@app.post("/evaluate-answer")
def evaluate(data: AnswerRequest):
    try:
        result = evaluate_answer(
            data.question,
            data.answer
        )
    except ValueError as exc:
        logger.exception("Ollama returned an unusable evaluation response: %s", exc)
        raise HTTPException(status_code=502, detail="The AI returned invalid evaluation data. Please try again.") from exc

    return {
        "evaluation": result.model_dump()
    }
