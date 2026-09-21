import json
import os

import requests

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass

API_URL = "https://openrouter.ai/api/alpha/decisions"
MODEL = "~typesafe/jev-latest"
API_KEY = os.getenv("OPENROUTER_API_KEY")
if not API_KEY:
    raise RuntimeError(
        "OPENROUTER_API_KEY is not set. "
        "Copy .env.example to .env and fill in your key."
    )


def build_state(question_description: str, correct_code: str, student_code: str) -> str:
    """Build the state prompt sent to jev."""
    return f"""
Question / Problem Statement:
{question_description}

Correct Reference Answer:
{correct_code}

Student Submission:
{student_code}
"""


def ask_jev(state: str, questions: dict) -> dict:
    """POST a state and questions to jev and return the answers."""
    response = requests.post(
        url=API_URL,
        headers={
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json",
        },
        data=json.dumps(
            {
                "model": MODEL,
                "state": state,
                "questions": questions,
            }
        ),
    )
    return response.json()["answers"]
