from .util import *

# Factual answers — short or long — are graded on facts alone: no syntax,
# algorithm, or structure to check. The old single 0-2 score prompt is
# decomposed into one noul question per score dimension, joined with
# coefficients (same pattern as essay/code/pseudocode).
FACT_NOUL_QUESTIONS = {
    "factually_correct": {
        "type": "noul",
        "instructions": """
        Is everything stated in the Student Answer factually correct?
        """,
        "criteria": {
            "true": "All factual claims are true when checked against reference answer.",
            "false": "Contains a factual error (including incorrect extra claims) when checked against reference answer.",
        },
    },
    "complete": {
        "type": "noul",
        "instructions": "Does the Student Answer cover everything needed to answer the question, with no major omission that makes it wrong or misleading?",
        "criteria": {
            "true": "Complete, covers the reference's key points",
            "false": "Major omission, incomplete or misleading",
        },
    },
    "answers_question": {
        "type": "noul",
        "instructions": "Does the Student Answer directly answer the question asked (on-topic), rather than answering a different question or missing the point?",
        "criteria": {
            "true": "Directly answers the question asked",
            "false": "Off-topic or does not answer the question",
        },
    },
}


FACT_SCORE_KEYS = ("factually_correct", "complete", "answers_question")

# Weights for deriving the 0-2 fact score from the three noul markers.
# Factual correctness dominates; completeness and on-topic answer share the rest.
FACT_CORRECTNESS_WEIGHT = 0.5
FACT_COMPLETENESS_WEIGHT = 0.3
FACT_RELEVANCE_WEIGHT = 0.2


def fact_score_from_checks(
    factually_correct: float,
    complete: float,
    answers_question: float,
) -> float:
    """Derive the 0-2 fact score from the three noul markers (no extra jev call).

    Weighted average of the markers remapped to the 0-2 range through the
    dense_power curve (dense in the lower part of the range):
    dense_score(factually_correct * 0.5 + complete * 0.3
    + answers_question * 0.2).
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
    complete and answers_question, plus the derived fact_score on the 0-2
    scale and points_given (fact_score / 2 * max_points).
    """
    answers = ask_jev(
        build_state(question_description, correct_answer, student_answer),
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
