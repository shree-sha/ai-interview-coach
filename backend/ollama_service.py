import random
import json
from typing import Literal

import requests
from pydantic import BaseModel, Field, ValidationError, field_validator


class EvaluationResult(BaseModel):
    """The validated feedback contract returned by the evaluation endpoint."""

    score: int = Field(ge=0, le=100)
    strengths: list[str] = Field(min_length=1, max_length=2)
    improvements: list[str] = Field(min_length=1, max_length=2)
    ideal_answer: str = Field(min_length=1)
    confidence: Literal["Low", "Medium", "High"]

    @field_validator("strengths", "improvements")
    @classmethod
    def clean_feedback_items(cls, items: list[str]) -> list[str]:
        cleaned_items = [item.strip() for item in items if isinstance(item, str) and item.strip()]
        if not cleaned_items:
            raise ValueError("must contain at least one non-empty item")
        return cleaned_items

    @field_validator("ideal_answer")
    @classmethod
    def clean_ideal_answer(cls, answer: str) -> str:
        answer = answer.strip()
        if not answer:
            raise ValueError("must not be blank")
        return answer

TOPICS = {
    "Python Developer": [
        "Python Basics",
        "OOP",
        "Data Structures",
        "Algorithms",
        "Generators",
        "Decorators",
        "Multithreading",
        "APIs"
    ],

    "Data Analyst": [
        "SQL",
        "Pandas",
        "NumPy",
        "Data Cleaning",
        "Statistics",
        "Visualization"
    ],

    "QA Engineer": [
        "Manual Testing",
        "API Testing",
        "Automation",
        "Selenium",
        "Test Cases"
    ],

    "React Developer": [
        "React Hooks",
        "State Management",
        "Performance",
        "Redux",
        "Routing"
    ]
}


def generate_question(role):

    topic = random.choice(
        TOPICS.get(role, ["General"])
    )

    print(f"Role: {role}")
    print(f"Topic Selected: {topic}")

    prompt = f"""
You are a senior technical interviewer.

Generate ONE interview question for a {role}
on the topic: {topic}.

Rules:
- Return only the question.
- No numbering.
- No explanation.
- Make it practical and interview-focused.
"""

    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "gemma3:4b",
            "prompt": prompt,
            "stream": False
        }
    )

    return response.json()["response"].strip()

def _parse_evaluation_response(response_text: str) -> EvaluationResult:
    """Parse JSON only, tolerating an accidental Markdown code fence from the model."""
    content = response_text.strip()

    if content.startswith("```"):
        lines = content.splitlines()
        content = "\n".join(lines[1:-1]).strip() if len(lines) >= 3 else content

    try:
        payload = json.loads(content)
    except json.JSONDecodeError as exc:
        raise ValueError("Ollama returned invalid evaluation JSON") from exc

    try:
        return EvaluationResult.model_validate(payload)
    except ValidationError as exc:
        raise ValueError("Ollama returned an invalid evaluation schema") from exc


def evaluate_answer(question, answer):

    prompt = f"""
You are an AI Interview Coach.

Evaluate the candidate's answer.

Question:
{question}

Candidate Answer:
{answer}

Scoring Guidelines:
- 0-20 : No understanding or "I don't know"
- 21-40 : Very basic understanding
- 41-60 : Partial understanding
- 61-80 : Good understanding
- 81-100 : Excellent understanding

Return ONLY a valid JSON object. Do not use Markdown code fences or include any text before or after the JSON.

Use exactly this schema:
{{
  "score": 82,
  "strengths": ["Explained the algorithm clearly", "Used appropriate terminology"],
  "improvements": ["Discuss time complexity", "Handle edge cases"],
  "ideal_answer": "A concise, technically correct answer that covers the key points.",
  "confidence": "Medium"
}}

Rules:
- Be encouraging.
- Be concise.
- score must be an integer from 0 to 100.
- strengths and improvements must each contain 1 or 2 short strings.
- ideal_answer must be a short, direct model answer, not a critique.
- confidence must be exactly one of: Low, Medium, High.
- Do NOT ask follow-up questions.
"""

    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "gemma3:4b",
            "prompt": prompt,
            "format": "json",
            "stream": False
        }
    )

    response.raise_for_status()
    return _parse_evaluation_response(response.json()["response"])
