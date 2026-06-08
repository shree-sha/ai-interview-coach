from fastapi import FastAPI
from ollamaService import generate_question

app = FastAPI()


@app.get("/")
def home():
    return {"message": "AI Interview Coach Running"}


@app.get("/question")
def question():

    generated_question = generate_question(
        "Python Developer"
    )

    return {
        "question": generated_question
    }