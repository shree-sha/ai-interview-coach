from fastapi import FastAPI
from datetime import datetime

from ollama_service import generate_question
from database import engine, SessionLocal
from models import InterviewHistory, Base
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

Base.metadata.create_all(bind=engine)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {"message": "AI Interview Coach Running"}


@app.get("/question")
def question():

    role = "Python Developer"

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