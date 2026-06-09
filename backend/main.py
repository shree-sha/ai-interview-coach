from fastapi import FastAPI
from datetime import datetime
from pydantic import BaseModel
from ollama_service import generate_question, evaluate_answer
from database import engine, SessionLocal
from models import InterviewHistory, Base
from fastapi.middleware.cors import CORSMiddleware
from auth import router as auth_router

app = FastAPI()

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

    result = evaluate_answer(
        data.question,
        data.answer
    )

    return {
        "evaluation": result
    }  