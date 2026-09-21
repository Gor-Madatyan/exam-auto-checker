from .util import *

PSEUDOCODE_SCORE_CRITERIA = [
    "0: Incorrect — Wrong algorithm (a fundamentally different approach than requested), a code path that produces no result (e.g., no specified result when the target is absent), or key steps missing.",
    "1: Partially Correct — The right algorithm with minor logic bugs (e.g., off-by-one) or incomplete edge case handling.",
    "2: Correct — The algorithm is correct and complete and produces the right result for all inputs. Pseudocode style, formatting, and syntax may differ freely.",
]

# Unlike check_code, there is no syntax to compile: pseudocode has no strict
# syntax, so the grader must judge the algorithm itself and not require the
# submission to match the Reference Answer's wording or structure.
PSEUDOCODE_NOUL_QUESTIONS = {
    "clear_and_complete": {
        "type": "noul",
        "instructions": "Is the pseudocode clear, complete, and does it describe a full algorithm with no missing steps? No strict syntax is required — pseudocode style may vary.",
        "criteria": {
            "true": "Clear and complete",
            "false": "Vague, incomplete, or missing steps",
        },
    },
    "correct_algorithm": {
        "type": "noul",
        "instructions": "Does it implement the requested algorithm's logic correctly? Judge the algorithm itself, not the pseudocode style or syntax, and do not require exact wording from the Reference Answer.",
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


PSEUDOCODE_SCORE_QUESTION = {
    "pseudocode_score": {
        "type": "score",
        "instructions": """
        Compare the Student Answer against the Correct Answer and rate the algorithmic correctness of the pseudocode.
        Pseudocode has no strict syntax: ignore style, formatting, and wording differences, and do not require the submission to match the Reference Answer structurally.
        Focus only on whether the algorithm logic is correct, complete, and handles edge cases.
        """,
        "criteria": PSEUDOCODE_SCORE_CRITERIA,
    }
}


PSEUDOCODE_SCORE_KEYS = ("clear_and_complete", "correct_algorithm", "handles_edge_cases")


def check_pseudocode(
    student_pseudocode: str, correct_pseudocode: str, question_description: str
) -> dict[str, float]:
    """Compare a student's pseudocode against a correct solution using the jev model.

    Unlike check_code, no strict syntax matching with the Reference Answer is
    required — pseudocode style may vary freely.

    Returns a dict of probabilities (0 to 1) for each check:
    clear_and_complete, correct_algorithm, handles_edge_cases.
    """
    answers = ask_jev(
        build_state(question_description, correct_pseudocode, student_pseudocode),
        PSEUDOCODE_NOUL_QUESTIONS,
    )
    # noul is a probability from 0 (no) to 1 (yes); choice and score carry the full distribution.
    return {key: answers[key]["noul"] for key in PSEUDOCODE_SCORE_KEYS}


def check_pseudocode_score(
    student_pseudocode: str, correct_pseudocode: str, question_description: str
) -> float:
    """Single-score variant: rate the pseudocode on a 0-2 scale.

    Returns one score: 0 (incorrect), 1 (partially correct), 2 (fully correct).
    """
    answers = ask_jev(
        build_state(question_description, correct_pseudocode, student_pseudocode),
        PSEUDOCODE_SCORE_QUESTION,
    )
    # noul is a probability from 0 (no) to 1 (yes); choice and score carry the full distribution.
    return answers["pseudocode_score"]["score"]


def check_pseudocode_full(
    student_pseudocode: str, correct_pseudocode: str, question_description: str
) -> dict[str, dict[str, float] | float]:
    """Combined variant: three noul checks and the 0-2 score in a single request.

    Returns {"checks": {clear_and_complete, correct_algorithm, handles_edge_cases},
    "score": 0 (incorrect) to 2 (fully correct)}.
    """
    answers = ask_jev(
        build_state(question_description, correct_pseudocode, student_pseudocode),
        {**PSEUDOCODE_NOUL_QUESTIONS, **PSEUDOCODE_SCORE_QUESTION},
    )
    # noul is a probability from 0 (no) to 1 (yes); choice and score carry the full distribution.
    return {
        "checks": {key: answers[key]["noul"] for key in PSEUDOCODE_SCORE_KEYS},
        "score": answers["pseudocode_score"]["score"],
    }