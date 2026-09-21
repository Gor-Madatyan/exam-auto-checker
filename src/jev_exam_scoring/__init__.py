from .code_check import check_code, check_code_full, check_code_score
from .essay_check import check_essay, check_essay_full, check_essay_score
from .fact_check import check_fact_score
from .grading import (
    GradedScore,
    SnapMode,
    discrete_levels,
    grade_code_full,
    grade_code_score,
    grade_essay_full,
    grade_essay_score,
    grade_fact_score,
    grade_pseudocode_full,
    grade_pseudocode_score,
    grade_score,
    score_to_points,
    snap_to_discrete,
)
from .pseudocode_check import (
    check_pseudocode,
    check_pseudocode_full,
    check_pseudocode_score,
)

__all__ = [
    "GradedScore",
    "SnapMode",
    "check_code",
    "check_code_full",
    "check_code_score",
    "check_essay",
    "check_essay_full",
    "check_essay_score",
    "check_fact_score",
    "check_pseudocode",
    "check_pseudocode_full",
    "check_pseudocode_score",
    "discrete_levels",
    "grade_code_full",
    "grade_code_score",
    "grade_essay_full",
    "grade_essay_score",
    "grade_fact_score",
    "grade_pseudocode_full",
    "grade_pseudocode_score",
    "grade_score",
    "score_to_points",
    "snap_to_discrete",
]


def main() -> None:

    score = check_fact_score(
        # user answer
        "A DoS attack comes from a single source, while a DDoS attack uses many compromised machines to overwhelm the target.",
        # reference answer
        "A DoS (Denial of Service) attack is launched from a single system, whereas a DDoS (Distributed Denial of Service) attack is launched from many distributed systems, often a botnet, making it harder to block.",
        # question
        "What is the difference between DDoS and DoS?",
    )

    print(score)
