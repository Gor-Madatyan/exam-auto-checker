from .util import *

NOUL_QUESTIONS = {
    "compiles_and_runs": {
        "type": "noul",
        "instructions": "Is the syntax of `student_code` valid and does every code path in `student_code` return a value (no missing or implicit returns)?",
        "criteria": {
            "true": "Syntax of `student_code` is valid and every code path returns a value",
            "false": "Syntax or structure error in `student_code` (including missing returns)",
        },
    },
    "correct_algorithm": {
        "type": "noul",
        "instructions": "Does `student_code` implement the algorithm requested in `question_description` correctly, when compared against `correct_code` for behavior? Judge logic alone, independently of syntax errors in `student_code`; different naming, formatting, or language features are acceptable.",
        "criteria": {
            "true": "`student_code` implements the correct algorithm design from `correct_code` (style, naming, and formatting may differ freely)",
            "false": "`student_code` uses the wrong algorithm or logic vs `correct_code`",
        },
    },
    "handles_edge_cases": {
        "type": "noul",
        "instructions": "Does `student_code` correctly handle boundary conditions and edge cases for `question_description` (e.g., empty input, single element, target not present, extreme values)?",
        "criteria": {
            "true": "`student_code` handles edge cases",
            "false": "`student_code` fails on edge cases",
        },
    },
}


SCORE_KEYS = ("compiles_and_runs", "correct_algorithm", "handles_edge_cases")

# Weights for deriving the 0-1 code score from the three noul markers.
# The algorithm itself dominates; syntax/returns and edge cases share the rest.
CODE_COMPILES_WEIGHT = 0.2
CODE_ALGORITHM_WEIGHT = 0.5
CODE_EDGE_WEIGHT = 0.3


def build_code_state(
    question_description: str, correct_code: str, student_code: str
) -> str:
    """Build the state JSON string sent to jev for code grading.

    Keys: `question_description`, `correct_code`, `student_code`.
    """
    return build_state(
        {
            "question_description": question_description,
            "correct_code": correct_code,
            "student_code": student_code,
        }
    )


def code_score_from_checks(
    compiles_and_runs: float,
    correct_algorithm: float,
    handles_edge_cases: float,
) -> float:
    """Derive the 0-1 code score from the three noul markers (no extra jev call).

    Weighted average of the markers, plus a +0.1 bonus capped at 1.0,
    remapped to the 0-1 range through the dense_power curve (dense in the
    lower part of the range):
    dense_score(min(compiles_and_runs * 0.2 + correct_algorithm * 0.5
    + handles_edge_cases * 0.3 + 0.1, 1)).

    Note the score is a quality signal, not a sole gate: a single failing
    criterion should fail the submission even when the weighted score looks
    middling (e.g. broken syntax with sound logic, or a wrong algorithm that
    still handles edges). A reasonable rule: fail if ``compiles_and_runs < 0.5``
    or ``correct_algorithm < 0.5``.
    """
    weighted = min((
        compiles_and_runs * CODE_COMPILES_WEIGHT
        + correct_algorithm * CODE_ALGORITHM_WEIGHT
        + handles_edge_cases * CODE_EDGE_WEIGHT
    ) + 0.1, 1)
    return dense_score(weighted)


def check_code(
    student_code: str,
    correct_code: str,
    question_description: str,
    max_points: float,
) -> dict[str, float]:
    """Compare a student's code against a correct solution using the jev model.

    Args:
        student_code: The student's source code.
        correct_code: The reference solution.
        question_description: The task / problem statement.
        max_points: Maximum points achievable for the task.

    Returns a dict with probabilities (0 to 1) for compiles_and_runs,
    correct_algorithm and handles_edge_cases, plus the derived code_score
    on the 0-1 scale and points_given (code_score * max_points).
    """
    answers = ask_jev(
        build_code_state(question_description, correct_code, student_code),
        NOUL_QUESTIONS,
    )
    # noul is a probability from 0 (no) to 1 (yes).
    checks = {key: answers[key]["noul"] for key in SCORE_KEYS}
    code_score = code_score_from_checks(
        checks["compiles_and_runs"],
        checks["correct_algorithm"],
        checks["handles_edge_cases"],
    )
    return {
        **checks,
        "code_score": code_score,
        "points_given": code_score * max_points,
    }
