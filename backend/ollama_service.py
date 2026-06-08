import requests


def generate_question(role):

    prompt = prompt = f"""
You are a senior technical interviewer.

Generate ONE unique interview question for a {role}.

Rules:
- Do not repeat common questions.
- Cover different topics each time.
- Return only the question.
- No numbering.
- No explanation.

Question:
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