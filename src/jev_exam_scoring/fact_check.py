from .util import *

FACT_CHECK_SCORE_CRITERIA = [
    "0: Incorrect — Contains a significant factual error, a major omission that makes the answer wrong or misleading, or does not answer the question asked.",
    "1: Partially Correct — Mostly accurate but with a minor factual error, an important omission, or imprecise terminology.",
    "2: Correct — Factually accurate, complete, and directly answers the question. Wording and structure may differ from the reference.",
]

# Factual answers — short or long — are graded on facts alone: no syntax, algorithm, or
# structure to check, so only the score prompt is used (no noul or full variants).
FACT_CHECK_SCORE_QUESTION = {
    "fact_check_score": {
        "type": "score",
        "instructions": """
        Compare the Student Answer against the Correct Reference Answer and rate its factual accuracy.
        Judge only the facts: is everything stated true, and is the answer complete enough to answer the question?
        Check every factual claim in the Student Answer, not just the main point — a long answer that adds
        incorrect information must not score higher than a short answer that is simply correct.
        Extra correct information beyond the reference is fine; incorrect extra claims are errors.
        Ignore style, wording, phrasing, and length differences — a short answer can be fully correct,
        and a long answer is not penalized for being thorough.
        """,
        "criteria": FACT_CHECK_SCORE_CRITERIA,
    }
}


def check_fact_score(
    student_answer: str, correct_answer: str, question_description: str
) -> float:
    """Single-score variant: rate a short factual answer on a 0-2 scale.

    Returns one score: 0 (incorrect), 1 (partially correct), 2 (fully correct).
    """
    answers = ask_jev(
        build_state(question_description, correct_answer, student_answer),
        FACT_CHECK_SCORE_QUESTION,
    )
    # noul is a probability from 0 (no) to 1 (yes); choice and score carry the full distribution.
    return answers["fact_check_score"]["score"]