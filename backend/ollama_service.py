import random
import json
from typing import Literal

import requests
from pydantic import BaseModel, Field, ValidationError, field_validator
from config import OLLAMA_GENERATE_URL, OLLAMA_MODEL, OLLAMA_STREAM


class EvaluationResult(BaseModel):
    """The validated feedback contract returned by the evaluation endpoint."""

    score: int = Field(ge=0, le=100)
    strengths: list[str] = Field(default_factory=list, max_length=2)
    improvements: list[str] = Field(min_length=1, max_length=2)
    ideal_answer: str = Field(min_length=1)
    confidence: Literal["Low", "Medium", "High"]

    @field_validator("strengths")
    @classmethod
    def clean_strengths(cls, items: list[str]) -> list[str]:
        return [item.strip() for item in items if isinstance(item, str) and item.strip()]

    @field_validator("improvements")
    @classmethod
    def clean_improvements(cls, items: list[str]) -> list[str]:
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


def select_topic(role: str) -> str:
    """Choose a supported topic for a role when the caller did not specify one."""
    return random.choice(TOPICS.get(role, ["General"]))


def generate_question(role: str, topic: str | None = None, difficulty: str = "Medium") -> str:
    """Generate one focused question using the supplied interview metadata."""
    topic = topic or select_topic(role)

    print(f"Role: {role}")
    print(f"Topic Selected: {topic}")

    prompt = f"""
You are a senior technical interviewer.

Generate ONE interview question for a {role}
on the topic: {topic}.
Difficulty: {difficulty}.

Rules:
- Return only the question.
- No numbering.
- No explanation.
- Make it practical and interview-focused.
"""

    response = requests.post(
        OLLAMA_GENERATE_URL,
        json={
            "model": OLLAMA_MODEL,
            "prompt": prompt,
            "stream": OLLAMA_STREAM
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


def _request_evaluation(prompt: str) -> EvaluationResult:
    """Ask Ollama for feedback constrained by the Pydantic JSON schema."""
    response = requests.post(
        OLLAMA_GENERATE_URL,
        json={
            "model": OLLAMA_MODEL,
            "prompt": prompt,
            "format": EvaluationResult.model_json_schema(),
            "stream": OLLAMA_STREAM
        }
    )
    response.raise_for_status()
    return _parse_evaluation_response(response.json()["response"])


def _validate_feedback_completeness(result: EvaluationResult) -> EvaluationResult:
    """Keep the feedback contract complete without inventing technical claims."""
    return result


def _ensure_meaningful_strength(
    result: EvaluationResult, *, is_non_attempt: bool
) -> EvaluationResult:
    """Provide a truthful baseline strength when a non-empty answer has none."""
    if not is_non_attempt and not result.strengths:
        return result.model_copy(
            update={"strengths": ["You provided a response to the question."]}
        )
    return result


def evaluate_answer(question, answer):
    answer_text = answer.strip().lower()

    invalid_answers = {
        "",
        "na",
        "n/a",
        "i don't know",
        "dont know",
        "idk",
        "...",
        "-"
    }

    is_non_attempt = answer_text in invalid_answers
    non_attempt_instructions = """
The candidate did not attempt the question. You must return:

- a score from 0 to 20;
- an empty strengths array: [];
- one or two improvements, including \"Attempt the question even if you are unsure.\";
- a detailed ideal answer for this specific question; and
- High confidence.
""" if is_non_attempt else ""

    prompt = f"""
You are a Senior Technical Interviewer and AI Interview Coach.

Your job is to evaluate the candidate's answer to a technical interview question.

Question:
{question}

Candidate Answer:
{answer}

Evaluate ONLY what the candidate actually wrote.

Scoring Rubric

0-20
No meaningful attempt or no technical content.

21-40
Very limited understanding with major misconceptions.

41-60
Partial understanding but missing important concepts.

61-80
Good understanding with minor mistakes or missing details.

81-100
Excellent, technically accurate, well-explained answer.

Evaluation Rules

- Evaluate only the candidate's answer.
- Never invent knowledge or strengths.
- Every strength must be directly supported by the candidate's answer.
- Do not praise concepts that are not mentioned.
- Be objective and fair.
- For every meaningful attempt, provide one or two specific strengths. Use an empty
  strengths array only when the candidate made no meaningful attempt.

If the answer is empty, "NA", "N/A", "I don't know", "IDK", "...", or contains no meaningful technical content:

- Score must be between 0 and 20.
- Confidence must be High.
- Explain that no meaningful answer was provided.
- Do not fabricate strengths.
- Encourage the candidate to attempt the question.

{non_attempt_instructions}

For the ideal_answer:

- Write the answer that an excellent interview candidate would give.
- Keep it between 120 and 250 words.
- Explain the solution clearly.
- Mention important concepts.
- Do not include code blocks or code snippets; explain any code-related details in plain prose.
- Explain why the solution works.
- Independently verify every technical claim before returning it. Do not repeat an incorrect claim from the candidate's answer.
- State the exact time and space complexity for each algorithm discussed; do not give two approaches the same complexity unless that is correct.
- Clearly distinguish average/expected performance from worst-case performance and explain relevant trade-offs.
- Recommend one approach when the question asks for a choice, and justify that recommendation.
- Do not describe an algorithm as in-place unless it genuinely uses O(1) auxiliary space in its standard implementation.
- Do not criticize the candidate in this section.
- The ideal answer should teach the concept, not just summarize it.

Return ONLY valid JSON.

The JSON schema is:

{{
  "score": 82,
  "strengths": [],
  "improvements": [
    "..."
  ],
  "ideal_answer": "...",
  "confidence": "Medium"
}}

Rules for JSON:

- score must be an integer between 0 and 100.
- strengths must contain 0-2 short bullet points. Use an empty array when there are no supported strengths.
- improvements must contain 1-2 short bullet points.
- ideal_answer must be a detailed model answer.
- confidence must be exactly one of:
  "Low"
  "Medium"
  "High"

Do not return Markdown.
Do not wrap JSON in code fences.
Return only the JSON object.
"""

    try:
        result = _request_evaluation(prompt)
        result = _validate_feedback_completeness(result)
        if not is_non_attempt and not result.strengths:
            raise ValueError("Ollama returned no strengths for a submitted answer")
        return _ensure_meaningful_strength(result, is_non_attempt=is_non_attempt)
    except ValueError:
        retry_prompt = f"""{prompt}

Your previous response was incomplete or could not be parsed. Generate the evaluation again.
For a meaningful candidate answer, strengths must include one or two concrete points
that are explicitly supported by the answer. Do not use an empty strengths array
unless the candidate made no meaningful attempt.
Return one JSON object that exactly matches the supplied schema. Ensure all text values are valid JSON strings.
"""
        result = _request_evaluation(retry_prompt)
    result = _validate_feedback_completeness(result)
    return _ensure_meaningful_strength(result, is_non_attempt=is_non_attempt)
