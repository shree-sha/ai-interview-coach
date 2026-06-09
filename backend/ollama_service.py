import requests
import random

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

def evaluate_answer(question, answer):

    prompt = f"""
You are a technical interviewer.

Question:
{question}

Candidate Answer:
{answer}

Evaluate the answer.

Return exactly:

Score: <0-100>

Feedback: <short feedback>
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