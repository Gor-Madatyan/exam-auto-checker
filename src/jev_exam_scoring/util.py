import json
import math
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
        "OPENROUTER_API_KEY is not set. Copy .env.example to .env and fill in your key."
    )


def build_state(
    question_description: str,
    correct_code: str,
    student_code: str,
    rules: str = "",
) -> str:
    """Build the state prompt sent to jev."""
    state = f"""
Question / Problem Statement:
{question_description}

Correct Reference Answer:
{correct_code}

Student Submission:
{student_code}
"""
    if rules:
        state += f"""
Scoring Rules:
{rules}
"""
    return state


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
        # Never block forever: without this, a stalled backend hangs the
        # request (and its threadpool worker) indefinitely. requests.Timeout
        # is a RequestException, so call_jev maps it to HTTP 502.
        timeout=60,
    )
    return response.json()["answers"]


def dense_power(x: float, gamma: float = 0.38) -> float:
    """Power/Gamma curve remapping (gamma < 1 expands lower range)."""
    norm_x = max(0.0, min(100.0, float(x))) / 100.0
    return 100.0 * (norm_x**gamma)


def dense_score(weighted: float) -> float:
    """Map a 0-1 weighted noul average to the 0-2 score scale.

    Remaps through the dense_power curve, which is dense in the lower part
    of the range (gamma < 1 lifts middling averages while keeping the
    endpoints exact): 0 -> 0.0, 0.5 -> ~1.58, 1 -> 2.0.
    """
    return dense_power(weighted * 100.0) / 100


def dense_log(x: float, a: float = 20.0) -> float:
    """Logarithmic remapping (higher 'a' compresses the upper bound more)."""
    norm_x = max(0.0, min(100.0, float(x))) / 100.0
    return 100.0 * (math.log(1.0 + a * norm_x) / math.log(1.0 + a))


def dense_ease_out(x:  float, k: float = 2.25) -> float:
    """Ease-Out power curve remapping."""
    norm_x = max(0.0, min(100.0, float(x))) / 100.0
    return 100.0 * (1.0 - (1.0 - norm_x) ** k)
