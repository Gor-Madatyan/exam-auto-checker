"""Benchmark jev's essay-checking prompt.

Runs check_essay across edge cases: good essay, off-topic, too short,
bad grammar/spelling, missing structure, and empty submission.

Each case is evaluated against expected bands for the two noul values:
  - meets_requirements  (topic match, word count, essay structure)
  - grammatically_correct (grammar, spelling, punctuation)
"""

from jev_exam_scoring.essay_check import check_essay

TOPIC = "Should social media be banned for children under 14?"

REQUIREMENTS = "At least 150 words, with an introduction, body paragraphs, and a conclusion."

GOOD_ESSAY = """Social media should be restricted for children under fourteen because the risks currently outweigh the benefits. While these platforms offer connection and entertainment, young teenagers are especially vulnerable to their negative effects on mental health, safety, and school performance.

First, endless scrolling and comparison with influencers can damage self-esteem and increase anxiety. Second, children are easy targets for cyberbullying, scams, and strangers who hide their real identity. Third, notifications and short videos are designed to be addictive, stealing time from homework, sleep, and real friendships. In addition, late-night use harms sleep, which teenagers need for healthy development. Schools already report shorter attention spans and more conflicts caused by online drama.

For these reasons, parents and lawmakers should limit access until fourteen and teach digital literacy instead of leaving children alone online. A clear age limit, combined with education and safer platform design, would protect children while still letting them benefit from technology later."""

BAD_GRAMMAR_ESSAY = """Social media should be restrict for childrens under fourteen beacuse the risks currently outweighs the benefits. While these platforms offers connection and entertainment, young teenagers is especially vulnerable to there negative effects on mental healht, safety, and scool performance.

First, endless scrolling and comparison with influencers can damages self-esteem and increase anxiaty. Second, childrens are easy targets for cyberbullying, scams, and strangers whom hides their real identity. Third, notification and short videos is designed to be addictive, stealing time from homework, sleep, and real friendship. In addition, late-night use harm sleep, which teenagers needs for healthy developement. Schools already reports shorter attention spans and more conflicts caused by online drama.

For these reasons, parents and lawmakers should limit acces until fourteen and teach digital literacy instead of leave children alone online. A clear age limit, combined with education and more safer platform design, would protects children while still letting them benefit from technology later."""

OFF_TOPIC_ESSAY = """Football is the most popular sport in the world because it is simple, exciting, and brings people together. All you need is a ball and some open space, and children in every country play it in streets, parks, and schoolyards with great enthusiasm and joy.

First, football teaches teamwork and discipline, since every player must cooperate and follow tactics to win matches. Second, it keeps people healthy by providing excellent exercise for the heart, muscles, and coordination. Professional leagues also create jobs and entertainment for millions of fans who fill stadiums and watch games on television every weekend with passion.

For these reasons, football deserves its place as the king of sports. Governments should build more pitches and support youth academies so that every child has the chance to play, stay healthy, and dream of becoming a professional player one day."""

TOO_SHORT_ESSAY = """Social media is bad for kids under fourteen. It causes anxiety and cyberbullying. I think parents should limit it until they are older."""

NO_STRUCTURE_ESSAY = """social media anxiety cyberbullying scams addiction self-esteem sleep homework attention span online drama notifications short videos influencers comparison mental health safety school performance parents lawmakers age limit digital literacy platform design children teenagers fourteen restriction protection technology education later access limit teach learn harm steal damage increase report cause effect problem solution bad good important because and also with for"""

# (name, expected_meets_band, expected_grammar_band, submission)
CASES = [
    ("good_essay", (0.7, 1.0), (0.7, 1.0), GOOD_ESSAY),
    ("off_topic", (0.0, 0.5), (0.7, 1.0), OFF_TOPIC_ESSAY),
    ("too_short", (0.0, 0.5), (0.7, 1.0), TOO_SHORT_ESSAY),
    ("bad_grammar", (0.5, 1.0), (0.0, 0.5), BAD_GRAMMAR_ESSAY),
    ("no_structure", (0.0, 0.5), (0.0, 0.5), NO_STRUCTURE_ESSAY),
    ("empty", (0.0, 0.5), (0.0, 0.5), ""),
]


def in_band(value: float, band: tuple[float, float]) -> bool:
    lo, hi = band
    return lo <= value <= hi


def main() -> None:
    print(f"Topic: {TOPIC}")
    print(f"Requirements: {REQUIREMENTS}\n")
    print(f"{'case':<14} {'meets':<7} {'grammar':<8} {'score':<6} verdict")
    print("-" * 60)
    for name, meets_band, grammar_band, submission in CASES:
        try:
            result = check_essay(submission, TOPIC, 2.0, REQUIREMENTS)
        except Exception as exc:
            print(f"{name:<14} {'ERR':<7} {'ERR':<8} {'ERR':<6} {exc}")
            continue
        meets = result["meets_requirements"]
        grammar = result["grammatically_correct"]
        score = result["essay_score"]
        ok = in_band(meets, meets_band) and in_band(grammar, grammar_band)
        verdict = "OK" if ok else "MISMATCH"
        print(
            f"{name:<14} {meets:<7.2f} {grammar:<8.2f} {score:<6.2f} {verdict} "
            f"(expected meets{list(meets_band)} grammar{list(grammar_band)})"
        )


if __name__ == "__main__":
    main()
