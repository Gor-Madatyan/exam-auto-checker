from .util import *

# Unlike check_code, there is no syntax to compile: pseudocode has no strict
# syntax, so the grader must judge the algorithm itself and not require the
# submission to match the Reference Answer's wording or structure.
PSEUDOCODE_NOUL_QUESTIONS = {
    "clear_and_complete": {
        "type": "noul",
        "instructions": "Is `student_pseudocode` clear, complete, and does it describe a full algorithm for `question_description` with no missing steps? Different wording, keywords, casing, or variable names are acceptable.",
        "criteria": {
            "true": "`student_pseudocode` is clear and complete",
            "false": "`student_pseudocode` is vague, incomplete, has key steps missing, or produces no result on some path (including a missing not-found result)",
        },
    },
    "correct_algorithm": {
        "type": "noul",
        "instructions": "Does `student_pseudocode` implement the algorithm requested in `question_description` correctly, when compared against `correct_pseudocode`? Judge the algorithm itself, not wording or structure.",
        "criteria": {
            "true": "`student_pseudocode` implements the correct algorithm design from `correct_pseudocode`",
            "false": "`student_pseudocode` uses the wrong algorithm or logic vs `correct_pseudocode`",
        },
    },
    "handles_edge_cases": {
        "type": "noul",
        "instructions": "Does `student_pseudocode` correctly handle boundary conditions and edge cases for `question_description` (e.g., empty input, single element, target not present, extreme values)?",
        "criteria": {
            "true": "`student_pseudocode` handles edge cases",
            "false": "`student_pseudocode` fails on edge cases",
        },
    },
}


PSEUDOCODE_SCORE_KEYS = ("clear_and_complete", "correct_algorithm", "handles_edge_cases")

# Weights for deriving the 0-1 pseudocode score from the three noul markers.
# The algorithm itself dominates; clarity/completeness and edge cases share the rest.
PSEUDOCODE_CLARITY_WEIGHT = 0.2
PSEUDOCODE_ALGORITHM_WEIGHT = 0.5
PSEUDOCODE_EDGE_WEIGHT = 0.3


def build_pseudocode_state(
    question_description: str, correct_pseudocode: str, student_pseudocode: str
) -> str:
    """Build the state JSON string sent to jev for pseudocode grading.

    Keys: `question_description`, `correct_pseudocode`, `student_pseudocode`.
    """
    return build_state(
        {
            "question_description": question_description,
            "correct_pseudocode": correct_pseudocode,
            "student_pseudocode": student_pseudocode,
        }
    )


def pseudocode_score_from_checks(
    clear_and_complete: float,
    correct_algorithm: float,
    handles_edge_cases: float,
) -> float:
    """Derive the 0-1 pseudocode score from the three noul markers (no extra jev call).

    Weighted average of the markers, plus a +0.1 bonus capped at 1.0,
    remapped to the 0-1 range through the dense_power curve (dense in the
    lower part of the range):
    dense_score(min(clear_and_complete * 0.2 + correct_algorithm * 0.5
    + handles_edge_cases * 0.3 + 0.1, 1)).

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
    pseudocode_score on the 0-1 scale and points_given
    (pseudocode_score * max_points).
    """
    answers = ask_jev(
        build_pseudocode_state(
            question_description, correct_pseudocode, student_pseudocode
        ),
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
