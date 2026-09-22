from .util import *

# Unlike check_code, there is no syntax to compile: pseudocode has no strict
# syntax, so the grader must judge the algorithm itself and not require the
# submission to match the Reference Answer's wording or structure.
PSEUDOCODE_NOUL_QUESTIONS = {
    "clear_and_complete": {
        "type": "noul",
        "instructions": "Is the pseudocode clear, complete, and does it describe a full algorithm with no missing steps?",
        "criteria": {
            "true": "Clear and complete",
            "false": "Vague, incomplete, or missing steps",
        },
    },
    "correct_algorithm": {
        "type": "noul",
        "instructions": "Does it implement the requested algorithm's logic correctly?",
        "criteria": {
            "true": "Correct algorithm design",
            "false": "Wrong algorithm or logic",
        },
    },
    "handles_edge_cases": {
        "type": "noul",
        "instructions": "Does it correctly handle boundary conditions and edge cases (e.g., empty input, single element, target not present, extreme values)?",
        "criteria": {
            "true": "Handles edge cases",
            "false": "Fails on edge cases",
        },
    },
}


PSEUDOCODE_SCORE_KEYS = ("clear_and_complete", "correct_algorithm", "handles_edge_cases")

# Weights for deriving the 0-2 pseudocode score from the three noul markers.
# The algorithm itself dominates; clarity/completeness and edge cases share the rest.
PSEUDOCODE_CLARITY_WEIGHT = 0.2
PSEUDOCODE_ALGORITHM_WEIGHT = 0.5
PSEUDOCODE_EDGE_WEIGHT = 0.3


def pseudocode_score_from_checks(
    clear_and_complete: float,
    correct_algorithm: float,
    handles_edge_cases: float,
) -> float:
    """Derive the 0-2 pseudocode score from the three noul markers (no extra jev call).

    Weighted average of the markers remapped to the 0-2 range through the
    dense_power curve (dense in the lower part of the range):
    dense_score(clear_and_complete * 0.2 + correct_algorithm * 0.5
    + handles_edge_cases * 0.3).

    Note the score is a quality signal, not a sole gate: a single failing
    criterion should fail the submission even when the weighted score looks
    middling (e.g. sound halving logic with no "not found" result). A
    reasonable rule: fail if ``clear_and_complete < 0.5`` or
    ``correct_algorithm < 0.5``.
    """
    weighted = min((
        clear_and_complete * PSEUDOCODE_CLARITY_WEIGHT
        + correct_algorithm * PSEUDOCODE_ALGORITHM_WEIGHT
        + handles_edge_cases * PSEUDOCODE_EDGE_WEIGHT
    )+0.1, 1)
    return dense_score(weighted)


def check_pseudocode(
    student_pseudocode: str,
    correct_pseudocode: str,
    question_description: str,
    max_points: float,
) -> dict[str, float]:
    """Compare a student's pseudocode against a correct solution using the jev model.

    Unlike check_code, no strict syntax matching with the Reference Answer is
    required — pseudocode style may vary freely.

    Args:
        student_pseudocode: The student's pseudocode submission.
        correct_pseudocode: The reference pseudocode.
        question_description: The task / problem statement.
        max_points: Maximum points achievable for the task.

    Returns a dict with probabilities (0 to 1) for clear_and_complete,
    correct_algorithm and handles_edge_cases, plus the derived
    pseudocode_score on the 0-2 scale and points_given
    (pseudocode_score / 2 * max_points).
    """
    answers = ask_jev(
        build_state(question_description, correct_pseudocode, student_pseudocode),
        PSEUDOCODE_NOUL_QUESTIONS,
    )
    # noul is a probability from 0 (no) to 1 (yes).
    checks = {key: answers[key]["noul"] for key in PSEUDOCODE_SCORE_KEYS}
    pseudocode_score = pseudocode_score_from_checks(
        checks["clear_and_complete"],
        checks["correct_algorithm"],
        checks["handles_edge_cases"],
    )
    return {
        **checks,
        "pseudocode_score": pseudocode_score,
        "points_given": pseudocode_score * max_points,
    }
