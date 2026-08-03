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

Return your response in EXACTLY this format:

Score:
<number only>

Strengths:
- point 1
- point 2

Areas for Improvement:
- point 1
- point 2

Suggestions:
- point 1
- point 2

Rules:
- Be encouraging.
- Be concise.
- Maximum 2 points per section.
- Do NOT ask follow-up questions.
- Do NOT add introductions.
- Do NOT add conclusions.
- Do NOT say "Would you like..."
- End your response after the Suggestions section.
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