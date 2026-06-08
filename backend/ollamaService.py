import requests


def generate_question(role):

    prompt = f"""
    You are a technical interviewer.

    Generate exactly ONE interview question for a {role}.

    Rules:
    - Return only the question
    - No explanation
    - No reasoning
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