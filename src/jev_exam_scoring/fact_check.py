from .util import *

# Factual answers — short or long — are graded on facts alone: no syntax,
# algorithm, or structure to check. The old single 0-2 score prompt (historical
# 0-2 scale) is decomposed into one noul question per score dimension, joined with
# coefficients (same pattern as essay/code/pseudocode).
FACT_NOUL_QUESTIONS = {
    "factually_correct": {
        "type": "noul",
        "instructions": "Is everything stated in `student_answer` factually correct when checked against `correct_answer`? Extra incorrect claims count as errors. Judge correctness only; do not penalize omissions here unless an omission makes a stated claim misleading.",
        "criteria": {
            "true": "All factual claims in `student_answer` are true when checked against `correct_answer`",
            "false": "`student_answer` contains a factual error when checked against `correct_answer` (even a single false claim, including an incorrect extra claim, fails)",
        },
    },
    "complete": {
        "type": "noul",
        "instructions": "Does `student_answer` cover everything in `correct_answer` needed to answer `question_description`, with no major omission that makes it wrong or misleading? Length is irrelevant.",
        "criteria": {
            "true": "`student_answer` is complete, covers the key points of `correct_answer`",
            "false": "`student_answer` has a major omission, is incomplete or misleading vs `correct_answer`",
        },
    },
    "answers_question": {
        "type": "noul",
        "instructions": "Does `student_answer` directly answer `question_description` (on-topic), rather than answering a different question or missing the point?",
        "criteria": {
            "true": "`student_answer` directly answers `question_description`",
            "false": "`student_answer` is off-topic, answers a different question, or does not answer `question_description`",
        },
    },
}


FACT_SCORE_KEYS = ("factually_correct", "complete", "answers_question")

# Weights for deriving the 0-1 fact score from the three noul markers.
# Factual correctness dominates; completeness and on-topic answer share the rest.
FACT_CORRECTNESS_WEIGHT = 0.5
FACT_COMPLETENESS_WEIGHT = 0.3
FACT_RELEVANCE_WEIGHT = 0.2


def build_fact_state(
    question_description: str, correct_answer: str, student_answer: str
) -> str:
    """Build the state JSON string sent to jev for fact grading.

    Keys: `question_description`, `correct_answer`, `student_answer`.
    """
    return build_state(
        {
            "question_description": question_description,
            "correct_answer": correct_answer,
            "student_answer": student_answer,
        }
    )


def fact_score_from_checks(
    factually_correct: float,
    complete: float,
    answers_question: float,
) -> float:
    """Derive the 0-1 fact score from the three noul markers (no extra jev call).

    Weighted average of the markers, plus a +0.1 bonus capped at 1.0,
    remapped to the 0-1 range through the dense_power curve (dense in the
    lower part of the range):
    dense_score(min(factually_correct * 0.5 + complete * 0.3
    + answers_question * 0.2 + 0.1, 1)).
    """
    weighted = min((
        factually_correct * FACT_CORRECTNESS_WEIGHT
        + complete * FACT_COMPLETENESS_WEIGHT
        + answers_question * FACT_RELEVANCE_WEIGHT
    )+0.1, 1)
    return dense_score(weighted)


def check_fact(
    student_answer: str,
    correct_answer: str,
    question_description: str,
    max_points: float,
) -> dict[str, float]:
    """Grade a factual answer against the correct answer using the jev model.

    Args:
        student_answer: The student's answer (short or long).
        correct_answer: The reference answer.
        question_description: The question asked.
        max_points: Maximum points achievable for the task.

    Returns a dict with probabilities (0 to 1) for factually_correct,
    complete and answers_question, plus the derived fact_score on the 0-1
    scale and points_given (fact_score * max_points).
    """
    answers = ask_jev(
        build_fact_state(question_description, correct_answer, student_answer),
        FACT_NOUL_QUESTIONS,
    )
    # noul is a probability from 0 (no) to 1 (yes).
    checks = {key: answers[key]["noul"] for key in FACT_SCORE_KEYS}
    fact_score = fact_score_from_checks(
        checks["factually_correct"],
        checks["complete"],
        checks["answers_question"],
    )
    return {
        **checks,
        "fact_score": fact_score,
        "points_given": fact_score * max_points,
    }
