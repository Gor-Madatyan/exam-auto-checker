# Student Scoring Ruleset — jev-exam-scoring

> Derived from: (a) internal benchmarks in `results.md` (code / pseudocode, v2 prompt fix, v3 recalibration),
> (b) the current implementation in `src/jev_exam_scoring/` (`util.py`, `code_check.py`,
> `pseudocode_check.py`, `fact_check.py`, `essay_check.py`), which is the source of truth, and
> (c) external assessment research (analytic vs. holistic rubrics, partial-credit autograding,
> Bloom's taxonomy, essay validity, LLM-as-judge calibration).
>
> Status: **normative** for all four scoring domains. If a prompt, weight, or gate changes,
> re-run the matching benchmark script and update `results.md` + `openapi.yaml` (per `AGENTS.md`).
> The `Scoring Rules` block in `build_state()` (`util.py`) SHOULD be populated from §2–§6 of this file.
>
> Scale: `noul` criteria live in `[0, 1]`; every derived `*_score` lives in **`[0, 1]`**
> (`dense_score = dense_power(...) / 100`); `points_given = score * max_points`.
> (`results.md` tables record historical runs on a 0–2 calibration — divide those values by 2
> to compare with current output. `noul` values, weights, and `< 0.5` gates are unaffected.)

---

## 1. General assessment principles

These are the research-backed invariants. Everything below implements them.

1. **Analytic, not holistic, by default.** Each domain decomposes quality into 2–3 independent
   `noul` criteria in `[0, 1]` plus one derived 0–1 score. Analytic rubrics give diagnostic,
   formative feedback (which criterion failed and why); a single holistic number hides the cause
   (cf. `syntax_error`: algorithm `0.87` but compiles `0.03` — one number cannot explain that).
   Use the derived score for ranking/leaderboards; use the per-criterion `noul` values for
   pass/fail and for student feedback.
2. **Validity: criteria must be independent and aligned to the learning goal.**
   Each `noul` question measures exactly one construct (syntax ≠ algorithm ≠ edge cases;
   facts ≠ completeness ≠ relevance; content ≠ grammar). Never let one criterion smuggle in
   another (e.g. do not punish grammar inside a "meets requirements" judgment, or style inside
   an algorithm judgment). Qualitative differentiation ("wrong algorithm" vs. "minor logic bug"),
   not intensifiers ("good" vs. "very good").
3. **Reliability: fixed thresholds, fixed weights, fixed wording.**
   Prompt wording measurably moves scores (v2 fix: `missing_return` compiles `0.50 → 0.19`;
   v3 recalibration halved `missing_return`'s score `0.84 → 0.37` on the old 0–2 scale,
   i.e. `~0.42 → ~0.19` today). Treat every instruction string as
   versioned config: change → benchmark → document.
4. **Partial credit is explicit, not emergent.** The 0–1 band semantics (§2.3) define exactly
   what earns 0 / ~0.5 / ~1. The weighted average (+0.1 bonus, capped at 1.0) + `dense_score`
   curve implements partial credit; fail-gates (§2.4) prevent a middling average from passing
   a fundamentally broken submission.
5. **Fairness / Bloom alignment.** Grade the cognitive level actually asked.
   Recall (`define`, `list`) ≠ application (`implement`, `code`, `debug`) ≠ creation
   (`design`, `construct`). A correct solution in a different style, language feature set, or
   variable naming is fully correct if the requested algorithm/behavior is present.
   Never require matching the reference answer's wording, structure, or style (proven by
   `correct_different_style`: algorithm `0.99` despite uppercase keywords, `LENGTH`/`FLOOR`,
   renamed variables).
6. **LLM-as-judge discipline.** The judge (`upstage/solar-decide` via OpenRouter Decisions API)
   is conservative at the top (correct submissions peak ≈ `0.82–0.85`, never a clean `1.0`)
   and lenient on "almost right" logic unless the criteria force severity. Countermeasures,
   all mandatory:
   - narrow, typed `noul` questions over open-ended scoring;
   - severity explicitly written into the 0-band ("missing return", "wrong algorithm",
     "key steps missing" ∈ 0, not 1);
   - fail-gates on `noul` values, never on the holistic score alone;
   - prompt changes validated empirically per model (prompt sensitivity is model-specific).

---

## 2. Global scoring mechanics (all domains)

### 2.1 Scale and types

| Artifact | Range | Meaning |
|---|---|---|
| Each `noul` criterion | `[0, 1]` | Probability of "yes". `0` = no, `1` = yes. |
| Derived `*_score` | `[0, 1]` | `dense_score(min(weighted_avg + 0.1, 1))` — see §2.2. Quality signal, not a gate. |
| `points_given` | `[0, max_points]` | `score * max_points` (as implemented in all `check_*`). |
| Gate threshold | `0.5` | Any gated criterion `< 0.5` = fail that criterion (§2.4). |

### 2.2 Aggregation: weighted average + bonus + dense curve

1. Compute `weighted = Σ (criterion × weight)` using the domain weights (§3–§6).
2. Add the **correctness bonus `+0.1`, capped at `1.0`**: `weighted = min(weighted + 0.1, 1)`.
   Rationale: lifts borderline-correct submissions without moving clear failures
   (all `*_score_from_checks` implement this; keep it).
3. Remap with `dense_score` = `dense_power(x, gamma=0.38) / 100`, i.e.
   `weighted^0.38`. Reference points: `0 → 0.0`, `0.5 → ~0.77`, `1 → 1.0`.
   The curve is dense at the bottom: small gains from zero matter, and middling averages
   land high — which is exactly why fail-gates (§2.4) are non-optional.
4. Keep `gamma = 0.38`. (`dense_log` / `dense_ease_out` in `util.py` are unused alternatives;
   do not swap curves without a full re-benchmark.)

### 2.3 Universal band semantics (v3 wording, all domains)

| Score (0–1) | Label | Meaning |
|---|---|---|
| `< 0.25` | Incorrect | Fundamentally wrong: wrong algorithm/approach, missing result on some path, crash-level errors, off-topic/empty, or factually false core claim. |
| `0.25–0.75` | Partially correct | Right approach with minor bugs: off-by-one, incomplete edge handling, partial omission, minor factual gap. |
| `≥ 0.75` | Correct | Correct and complete for all inputs. Style, syntax details, naming, and formatting **may differ freely** from the reference. |

Calibrated expectations from benchmarks (halved to current scale): wrong-approach submissions
score `~0.03–0.18`; off-by-one scores `~0.5–0.6`; correct submissions score `~0.82–0.85`
(conservative ceiling — do **not** expect a clean `1.0` from the judge; map `≥ 0.75` to full
marks if a clean ceiling matters).

### 2.4 Fail-gates override the score (mandatory)

**A single failing criterion fails the submission even when the weighted score looks middling.**
This is the single most important rule in this file — it is confirmed by every benchmark:

- Code: fail if `compiles_and_runs < 0.5` **or** `correct_algorithm < 0.5`.
- Pseudocode: fail if `clear_and_complete < 0.5` **or** `correct_algorithm < 0.5`.
- Fact: fail if `factually_correct < 0.5` **or** `answers_question < 0.5`
  (completeness alone never passes a factually wrong or off-topic answer).
- Essay: fail if `meets_requirements < 0.5` (grammar alone never passes an off-topic essay).

`handles_edge_cases` / `complete` / `grammatically_correct` and the holistic score are
**quality signals**, not hard gates — except as stated above.

### 2.5 Empty, off-topic, and non-attempts

- Empty string / no attempt → all criteria `≈ 0`, score `≈ 0`. Never award the `+0.1` bonus
  any semantic weight here (it still applies arithmetically; the result stays failing).
- Off-topic but well-formed (e.g. linear scan for binary search, unrelated essay) →
  relevance/requirements criterion `≈ 0`, overall fail regardless of other criteria.
- Syntax-broken but logically sound code → `compiles_and_runs ≈ 0.03`, algorithm may stay
  high (`0.87` observed) **by design** (logic judged independently of syntax). The gate on
  `compiles_and_runs` is what fails it. Same logic for fact: a fluent, complete, but false
  answer fails on `factually_correct`.

### 2.6 Reference answer discipline

- The reference is ground truth for *behavior*, not a style template. In code/pseudocode/fact,
  any submission producing the right result for all inputs (or stating the reference's key
  points correctly) is correct.
- For essays the "reference" is the topic + requirements string; there is no model essay to match.

---

## 3. Code (`check_code`) — weights 0.2 / 0.5 / 0.3

**Criteria (`NOUL_QUESTIONS`):**

1. `compiles_and_runs` (weight `0.2`) — "Is the syntax valid and does every code path return
   a value (no missing or implicit returns)?" True = valid syntax; false = syntax/structure error.
2. `correct_algorithm` (weight `0.5`, dominant) — "Does it implement the requested algorithm's
   logic correctly?" True = correct design; false = wrong algorithm/logic.
3. `handles_edge_cases` (weight `0.3`) — "Does it correctly handle boundary conditions
   (empty input, single element, **target not present**, extreme values)?" True = handles;
   false = fails on edges.

Score: `code_score = dense_score(min(compiles*0.2 + algorithm*0.5 + edges*0.3 + 0.1, 1))`,
`points_given = code_score * max_points`.

**Rules:**

- R3.1 Gate: fail if `compiles_and_runs < 0.5` or `correct_algorithm < 0.5`.
- R3.2 Missing return / implicit `None` on any path (e.g. no `return -1`) counts as
  `compiles_and_runs` failure (v2 wording — keep the "every code path returns a value" clause).
  Benchmark: this moved `missing_return` from `0.50` to `0.16–0.19`. Edge cases will also
  dip (`~0.43–0.49`); algorithm may stay high (`~0.88`) — the gate still fails it.
- R3.3 Wrong algorithm (e.g. linear scan for binary search) → `correct_algorithm ≈ 0.01`,
  score `~0.03–0.18`. Pass even if `compiles_and_runs ≈ 0.97` and edge cases look
  okay (`0.71–0.72` observed — edge handling of the *wrong* algorithm does not redeem it).
- R3.4 Off-by-one (`while low < high`, missing `low == high`) → partial credit:
  algorithm `~0.36–0.37`, edges `~0.47–0.51`, score `~0.55–0.6`. Gate fails it
  (algorithm `< 0.5`) but the score correctly signals "close".
- R3.5 Syntax error (missing colon, etc.) → `compiles_and_runs ≈ 0.03`, score `~0.07–0.17`.
  Algorithm is judged on logic alone and may read high — ignore it; the gate decides.
  Never use the holistic score as a syntax detector.
- R3.6 Correct recursive and iterative variants are equally correct (both `≥ 0.91` on every
  check, score `~0.83–0.85`). No penalty for recursion vs. iteration, naming, or formatting.
- R3.7 `handles_edge_cases` is advisory. Use it to order partial credit and to write feedback,
  not to pass/fail.

---

## 4. Pseudocode (`check_pseudocode`) — weights 0.2 / 0.5 / 0.3

**Criteria (`PSEUDOCODE_NOUL_QUESTIONS`):** same shape as code, except criterion 1:

1. `clear_and_complete` (weight `0.2`) — "Is the pseudocode clear, complete, and does it
   describe a full algorithm with no missing steps?" (There is **no syntax to compile**;
   style/keywords/casing are free.)
2. `correct_algorithm` (weight `0.5`, dominant) — same as code.
3. `handles_edge_cases` (weight `0.3`) — same as code.

Score: `pseudocode_score = dense_score(min(clarity*0.2 + algorithm*0.5 + edges*0.3 + 0.1, 1))`,
`points_given = pseudocode_score * max_points`.

**Rules:**

- R4.1 Gate: fail if `clear_and_complete < 0.5` or `correct_algorithm < 0.5`.
- R4.2 **No strict-syntax matching.** Uppercase keywords, `LENGTH`/`FLOOR` vs. `length`/`//`,
  different variable names — all acceptable if the algorithm is right
  (`correct_different_style`: clear `0.98`, algorithm `0.99`, score `~0.82`). Instruct the
  judge to evaluate the algorithm itself, never wording/structure similarity.
- R4.3 Missing "not found" result (no `-1`/equivalent) is the softest failure mode:
  algorithm stays high (`0.95–0.97`), clarity hovers at the gate (`0.48–0.52`), score `~0.31–0.33`
  on the current scale. It fails **only** via the `clear_and_complete` gate —
  keep that gate strict. Recommended hardening (open item from benchmarks): add a dedicated
  `noul` question "does every path produce a result?" if missing-result handling is graded.
- R4.4 Wrong algorithm → `correct_algorithm ≈ 0.02`, score `~0.11`.
  Vague/descriptive non-algorithms (`vague_incomplete`) → clear `~0.06`, algorithm `~0.09–0.10`,
  score `~0.01`: decisive fail.
- R4.5 Off-by-one → same partial-credit band as code (algorithm `~0.36–0.38`,
  score `~0.5–0.55`).

---

## 5. Factual answers (`check_fact`) — weights 0.5 / 0.3 / 0.2

**Criteria (`FACT_NOUL_QUESTIONS`):**

1. `factually_correct` (weight `0.5`, dominant) — "Is everything stated factually correct
   against the reference? **Extra incorrect claims count as errors.**"
2. `complete` (weight `0.3`) — "Covers everything needed; no major omission that makes it
   wrong or misleading?" True = covers reference key points.
3. `answers_question` (weight `0.2`) — "Directly answers the question asked (on-topic)?"

Score: `fact_score = dense_score(min(correctness*0.5 + complete*0.3 + relevance*0.2 + 0.1, 1))`,
`points_given = fact_score * max_points`.

**Rules:**

- R5.1 Gate: fail if `factually_correct < 0.5` or `answers_question < 0.5`.
  A fluent, complete, on-topic answer with one false core claim fails. An accurate answer to
  a *different* question fails.
- R5.2 Extra claims are graded: a correct core plus an incorrect addition lowers
  `factually_correct` (per the "including incorrect extra claims" criterion). No credit for
  padding.
- R5.3 Omissions are graded on `complete`, not `factually_correct`: a true-but-incomplete
  answer keeps correctness high and loses on completeness → partial-credit band
  (`0.25–0.75`). A omission that makes the answer *misleading* also lowers correctness.
- R5.4 Length is irrelevant. Short exact answers and long thorough answers are judged only
  on the three criteria. Buried errors (correct text with one false sentence) fail correctness.
- R5.5 Bands for `fact_score` (as implemented in `fact_benchmark.py`):
  correct `∈ [0.75, 1.0]`, partial `∈ [0.25, 0.75)`, incorrect `∈ [0.0, 0.25)`.
  Scores are conservative at the top; treat `≥ 0.75` as full correctness.

---

## 6. Essays (`check_essay`) — weights 0.6 / 0.4

**Criteria (`ESSAY_NOUL_QUESTIONS`):**

1. `meets_requirements` (weight `0.6`, dominant) — "Does the essay fulfil the requirements
   (topic match, length, structure)?" True = meets topic + length; false = off-topic/wrong length.
2. `grammatically_correct` (weight `0.4`) — "Grammatically correct with correct spelling and
   basic sentence punctuation?" False = frequent errors **relative to length**.

Score: `essay_score = dense_score(min(meets*0.6 + grammar*0.4 + 0.1, 1))`,
`points_given = essay_score * max_points`.

**Rules:**

- R6.1 Gate: fail if `meets_requirements < 0.5`. Grammar never rescues an off-topic,
  too-short, or structureless essay; content never rescues an unreadable one either —
  but the hard gate is on requirements (research consensus: content/organization dominate
  holistic judgments; separating the traits preserves validity).
- R6.2 Content and mechanics are judged independently (validity rule). Do not let
  grammatical errors leak into `meets_requirements`, nor eloquence mask missing structure.
  Expected benchmark bands: good essay `(0.7–1.0 / 0.7–1.0)`; off-topic `(0.0–0.5 / 0.7–1.0)`;
  too short `(0.0–0.5 / 0.7–1.0)`; bad grammar `(0.5–1.0 / 0.0–0.5)`; no structure
  `(0.0–0.5 / 0.0–0.5)`; empty `(0.0–0.5 / 0.0–0.5)` (per `essay_benchmark.py`).
- R6.3 Length/structure requirements come from the `requirements` string
  (e.g. "≥ 150 words, introduction + body + conclusion") and are part of the state
  (`build_essay_state`). An essay that is on-topic but half the required length fails
  `meets_requirements`. Always pass explicit requirements; never grade against an
  unstated length.
- R6.4 Grammar is error-density relative to length, not an absolute count. A long essay
  with a few slips stays `≥ 0.7`; a short essay riddled with errors drops below `0.5`.
- R6.5 Empty submission → fail both criteria, score `~0`.

---

## 7. Feedback and student-facing rules

1. Every graded submission returns **all** of: per-criterion `noul` values, derived score,
   and `points_given` — plus a one-line reason per failed criterion (which gate fired and why).
   A bare number is not feedback.
2. Student-facing grade bands (0–1 scale): `≥ 0.75` correct/full marks · `0.25–0.75` partial
   credit (resubmit-eligible; feedback must name the fix: "off-by-one: handle `low == high`",
   "missing `return -1` path", "omits botnet/distributed key point") · `< 0.25` incorrect.
3. Gates map to messages: `compiles < 0.5` → "does not run / missing return";
   `algorithm < 0.5` → "wrong approach or logic"; `edge < 0.5` → "fails boundary cases
   (list them)"; `factually_correct < 0.5` → "factually wrong (quote the claim)";
   `complete < 0.5` → "missing key point (name it)"; `answers_question < 0.5` → "off-topic";
   `meets_requirements < 0.5` → "off-topic / length / structure (name which)";
   `grammar < 0.5` → "language errors (density, not style)".
4. Partial credit is additive through the weights — never subtract ad-hoc penalties on top.
   If a new error class matters, add a criterion or tighten wording (§8), don't hand-adjust.

---

## 8. Calibration, maintenance, and API rules

1. **One router per domain, one `/check` endpoint each** (`code`, `essay`, `fact`, `pseudocode`).
   Routers validate/shape I/O only; all `NOUL_QUESTIONS`, weights, and `*_score_from_checks`
   math live in the library modules. Never duplicate the math in routers.
2. **Thresholds and weights are frozen** unless a benchmark justifies the change:
   code `0.2/0.5/0.3`, pseudocode `0.2/0.5/0.3`, fact `0.5/0.3/0.2`, essay `0.6/0.4`
   (requirements/grammar), gate `0.5`, bonus `+0.1` capped at `1.0`, `gamma 0.38`,
   `ask_jev timeout=60`.
3. **Change protocol:** edit wording/weights → run `benchmark.py` / `essay_benchmark.py` /
   `fact_benchmark.py` (live backend, costs money) → update `results.md` → update
   `openapi.yaml` if routes/schemas change. `results.md` v2/v3 entries are the template
   (note: their score tables are on the historical 0–2 calibration — divide by 2).
4. **Transport/error mapping** (`ask_jev` via `api/_helpers.py::call_jev`): transport errors
   → 502 upstream; missing `OPENROUTER_API_KEY` → 500. Keep `timeout=60` (prevents hung
   threadpool workers). Auth: `X-API-Key` header required on every endpoint
   (`api/security.py`, `api/config.py`).
5. **Known open items** (do not silently work around; benchmark before adopting):
   - Conservative `1.0` ceiling (best observed `~0.84`): needs an explicit "Award top marks
     when…" directive or acceptance that `≥ 0.75` = full marks; may be inherent model calibration.
   - Proposed pseudocode `produces_result_on_all_paths` `noul` question for missing-result cases.
   - The v3 `syntax_error` score (`0.17` current-scale) reads softer than its v2 wording
     ("errors that would crash" vs. "severe syntax errors") — the score alone is not a syntax
     detector; the gate decides.
6. **Style:** `from __future__ import annotations` in API files, `from .util import *` in
   scoring modules, type hints, docstrings noting weights, bonus, and gates (per `AGENTS.md`).

---

## Appendix A — Quick reference card

| Domain | Criteria (weights) | Fail if | Partial-credit anchor (0–1) |
|---|---|---|---|
| Code | compiles 0.2 · algorithm 0.5 · edges 0.3 | compiles `< 0.5` or algorithm `< 0.5` | off-by-one → `~0.55–0.6` |
| Pseudocode | clarity 0.2 · algorithm 0.5 · edges 0.3 | clarity `< 0.5` or algorithm `< 0.5` | off-by-one → `~0.5–0.55` |
| Fact | correctness 0.5 · completeness 0.3 · relevance 0.2 | correctness `< 0.5` or relevance `< 0.5` | omission → `0.25–0.75` |
| Essay | requirements 0.6 · grammar 0.4 | requirements `< 0.5` | bad grammar, good content → still partial |

Global: `score = dense_score(min(Σw·c + 0.1, 1))`, `gamma=0.38`
(`0 → 0.0`, `0.5 → ~0.77`, `1 → 1.0`);
`points_given = score × max_points`; gate `0.5`;
`≥ 0.75` correct · `0.25–0.75` partial · `< 0.25` incorrect.

## Appendix B — Sources

- Internal: `results.md` (code/pseudocode benchmarks, v2 prompt fix, v3 recalibration;
  score tables on historical 0–2 calibration — halve for current scale),
  `benchmark.py`, `essay_benchmark.py`, `fact_benchmark.py`, `src/jev_exam_scoring/*.py`.
- Analytic-vs-holistic rubrics (formative feedback needs analytic criteria; holistic for
  summative impression; many practitioners combine both — analytic for feedback, holistic
  for the final mark): Stanford TeachingWriting Rubric Design; WMU Rubrics 101;
  ANU Types of Rubrics; Brown (JALT TEVAL) "Analytic or holistic?"; Frontiers in Education
  "Modeling Holistic Marks With Analytic Rubrics".
- Partial-credit autograding (rubric/equivalence checking, concept-graph matching,
  edit-distance partial marks, LLM-repair + test execution): AutoRubric (Berkeley EECS-2020-34);
  ISSTA'23 concept-based grading; ICDE'19 SQL partial marking; arXiv:2204.04196 proof
  partial credit; MDPI Informatics 16(8) LLM Python grading; SimGrade; FlexiGrader.
- Validity/reliability (align criteria to goals, criterion independence, qualitative
  differentiation, assessor calibration, positive language, stakeholder feedback):
  Glasgow "What Makes a Good Rubric?"; HEQCO Guide to Valid and Reliable Rubrics;
  Panadero et al. rubric co-creation; MDPI Educ. Sci. 11(8)441 Assessment Evaluation Rubric.
- Bloom's for Computing (56 CS-specific verbs; one verb per outcome; level depends on
  prior exposure): ACM CCECC "Bloom's for Computing" + SIGITE'24 competencies guide.
- Essay validity (grammar/content conflation, rater bias to mechanics, content+organization
  dominate holistic judgments, separate traits + rater training): Chula Pasaa revision study;
  "Reliability and validity of rubrics for assessment through writing"; TOEFL iBT holistic
  vs. analytic study; Wiley "Validity of Examination Essays".
- LLM-as-judge (capability-dependent leniency → multi-judge calibrated voting; Bayesian /
  Neural-ODE post-hoc calibration with anchors; prompt effects are model-specific):
  arXiv:2609.12002; arXiv:2605.09227; EDM'26 prompt-sensitivity poster; CalibraEval
  (ACL 2025); AIMEcon-WIP 2025 AES fairness study.
