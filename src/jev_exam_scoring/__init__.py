from .code_check import check_code, check_code_full, check_code_score
from .essay_check import check_essay
from .fact_check import check_fact_score
from .pseudocode_check import (
    check_pseudocode,
    check_pseudocode_full,
    check_pseudocode_score,
)

__all__ = [
    "check_code",
    "check_code_full",
    "check_code_score",
    "check_essay",
    "check_fact_score",
    "check_pseudocode",
    "check_pseudocode_full",
    "check_pseudocode_score",
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
