"""Benchmark jev's fact-checking prompt on short and long answers.

Runs check_fact across edge cases: correct/incorrect, short/long,
buried errors, extra incorrect claims, omissions, off-topic, and empty answers.

check_fact returns one noul float in [0, 1] per criterion
(factually_correct, complete, answers_question) plus the derived fact_score
on the 0-2 scale (weighted average joined with coefficients). Each case is
evaluated against a score band rather than an exact value:
  - correct    -> [1.5, 2.0]
  - partial    -> [0.5, 1.5)
  - incorrect  -> [0.0, 0.5)
"""

from jev_exam_scoring.fact_check import check_fact

QUESTION = "What is the difference between DDoS and DoS?"

REFERENCE = (
    "A DoS (Denial of Service) attack is launched from a single system, whereas a "
    "DDoS (Distributed Denial of Service) attack is launched from many distributed "
    "systems, often a botnet, making it harder to block."
)

# (name, expected_band, submission)
CASES = [
    (
        "correct_short",
        (1.5, 2.0),
        "DoS comes from one source; DDoS comes from many sources, often a botnet.",
    ),
    (
        "correct_long",
        (1.5, 2.0),
        "A Denial of Service (DoS) attack is an attempt to make a service unavailable "
        "by overwhelming it with traffic or requests. The key characteristic is that it "
        "originates from a single source system. A Distributed Denial of Service (DDoS) "
        "attack does the same thing but coordinates many compromised machines, often "
        "organized into a botnet, to flood the target simultaneously. Because the traffic "
        "comes from many distributed sources, a DDoS attack is much harder to defend "
        "against and to block by simply blacklisting a single IP address.",
    ),
    (
        "incorrect_short",
        (0.0, 0.5),
        "DoS and DDoS are the same thing; both come from a single computer.",
    ),
    (
        "incorrect_long_buried",
        (0.0, 0.5),
        "A Denial of Service attack aims to make a service unavailable. A DoS attack "
        "originates from a single source, while a DDoS attack uses many distributed "
        "machines, often a botnet. One additional difference is that DoS attacks are "
        "always illegal, whereas DDoS attacks are perfectly legal.",
    ),
    (
        "partial_minor",
        (0.5, 1.5),
        "DoS comes from one source. DDoS is similar but uses a few more computers.",
    ),
    (
        "extra_incorrect",
        (0.0, 0.5),
        "DoS is single-source and DDoS is distributed. DDoS attacks are always carried "
        "out by governments.",
    ),
    (
        "off_topic",
        (0.0, 0.5),
        "The difference between TCP and UDP is that TCP is connection-oriented while "
        "UDP is connectionless.",
    ),
    (
        "empty",
        (0.0, 0.5),
        "",
    ),
    (
        "important_omission",
        (0.0, 0.5),
        "DoS is a denial of service attack.",
    ),
    (
        "correct_long_thorough",
        (1.5, 2.0),
        "DoS and DDoS are both denial-of-service attacks that aim to disrupt a target "
        "service. The fundamental difference is the number of attacking sources. A DoS "
        "attack is launched from a single machine, so the defender can often mitigate it "
        "by blocking that one source address. A DDoS attack is launched from many "
        "distributed machines, frequently a botnet of compromised devices, which makes "
        "it far more difficult to stop because there is no single source to block. This "
        "distributed nature is why DDoS attacks tend to be more damaging and harder to "
        "defend against than simple DoS attacks.",
    ),
]


def main() -> None:
    print(f"Question: {QUESTION}\n")
    print(f"{'case':<26} {'band':<14} {'actual':<7} verdict")
    print("-" * 60)
    for name, (lo, hi), submission in CASES:
        try:
            result = check_fact(submission, REFERENCE, QUESTION, 2.0)
            actual = result["fact_score"]
        except Exception as exc:
            print(f"{name:<26} {'ERR':<14} {'ERR':<7} {exc}")
            continue
        verdict = "OK" if lo <= actual <= hi else "MISMATCH"
        print(f"{name:<26} {f'[{lo}, {hi}]':<14} {actual:<7.2f} {verdict}")


if __name__ == "__main__":
    main()
