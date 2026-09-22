from .code_check import (
    CODE_ALGORITHM_WEIGHT,
    CODE_COMPILES_WEIGHT,
    CODE_EDGE_WEIGHT,
    check_code,
    code_score_from_checks,
)
from .essay_check import (
    ESSAY_GRAMMAR_WEIGHT,
    ESSAY_REQUIREMENTS_WEIGHT,
    check_essay,
    essay_score_from_checks,
)
from .fact_check import (
    FACT_COMPLETENESS_WEIGHT,
    FACT_CORRECTNESS_WEIGHT,
    FACT_RELEVANCE_WEIGHT,
    check_fact,
    fact_score_from_checks,
)
from .pseudocode_check import (
    PSEUDOCODE_ALGORITHM_WEIGHT,
    PSEUDOCODE_CLARITY_WEIGHT,
    PSEUDOCODE_EDGE_WEIGHT,
    check_pseudocode,
    pseudocode_score_from_checks,
)

__all__ = [
    "CODE_ALGORITHM_WEIGHT",
    "CODE_COMPILES_WEIGHT",
    "CODE_EDGE_WEIGHT",
    "check_code",
    "code_score_from_checks",
    "ESSAY_GRAMMAR_WEIGHT",
    "ESSAY_REQUIREMENTS_WEIGHT",
    "check_essay",
    "essay_score_from_checks",
    "FACT_COMPLETENESS_WEIGHT",
    "FACT_CORRECTNESS_WEIGHT",
    "FACT_RELEVANCE_WEIGHT",
    "check_fact",
    "fact_score_from_checks",
    "PSEUDOCODE_ALGORITHM_WEIGHT",
    "PSEUDOCODE_CLARITY_WEIGHT",
    "PSEUDOCODE_EDGE_WEIGHT",
    "check_pseudocode",
    "pseudocode_score_from_checks",
]


def main() -> None:

    score = check_fact(
        # user answer
        "A DoS attack comes from a single source, while a DDoS attack uses many compromised machines to overwhelm the target.",
        # reference answer
        "A DoS (Denial of Service) attack is launched from a single system, whereas a DDoS (Distributed Denial of Service) attack is launched from many distributed systems, often a botnet, making it harder to block.",
        # question
        "What is the difference between DDoS and DoS?",
        # max points
        2.0,
    )

    print(score)
