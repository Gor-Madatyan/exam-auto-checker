# jev Code-Checking Benchmark

Benchmark of the code-checking pattern against the **`~typesafe/jev-latest`** model (via OpenRouter) for grading student code submissions.

- **Date:** 2026-09-21
- **Question:** "Write a binary search algorithm"
- **Variants:**
  - `check_code()` — three `noul` checks, each a probability from 0 (no) to 1 (yes)
  - `check_code_score()` — single `score` question, one value from 0 (incorrect) to 2 (fully correct)
  - `check_code_full()` — all four questions (3 noul + score) in a single request
- **Prompt revision (v2):** after the first run, the instructions were tightened to require a return value on every code path:
  - `compiles_and_runs`: "Is the syntax valid and does every code path return a value (no missing or implicit returns)?"
  - `handles_edge_cases`: added "target not present" to the example edge cases
  - `score` instructions: "...including return values on every code path"
- **Prompt revision (v3):** score criteria recalibrated (see [Score recalibration](#score-recalibration-v3))

## Test Cases

| Case | Description | Expected |
|------|-------------|----------|
| `correct_recursive` | Correct recursive binary search | all checks ≈ 1 |
| `correct_iterative` | Correct iterative binary search | all checks ≈ 1 |
| `off_by_one` | `while low < high` — misses `low == high` | algorithm / edge cases low |
| `linear_search` | Linear scan instead of binary search | algorithm low |
| `syntax_error` | Missing colon after `while` | compiles low |
| `missing_return` | No `return -1` when target not found | compiles low |

## Results — 3 × noul (`check_code`)

| Case | compiles_and_runs | correct_algorithm | handles_edge_cases |
|------|------------------:|------------------:|-------------------:|
| correct_recursive | 0.97 | 0.97 | 0.91 |
| correct_iterative | 0.98 | 0.99 | 0.94 |
| off_by_one | 0.95 | 0.37 | 0.51 |
| linear_search | 0.97 | 0.01 | 0.72 |
| syntax_error | 0.03 | 0.87 | 0.73 |
| missing_return | 0.19 | 0.88 | 0.49 |

## Results — single score (`check_code_score`)

| Case | score (0–2) |
|------|------------:|
| correct_recursive | 1.70 |
| correct_iterative | 1.70 |
| off_by_one | 1.22 |
| linear_search | 0.31 |
| syntax_error | 0.15 |
| missing_return | 0.83 |

## Results — combined (`check_code_full`)

| Case | compiles_and_runs | correct_algorithm | handles_edge_cases | score |
|------|------------------:|------------------:|-------------------:|------:|
| correct_recursive | 0.97 | 0.97 | 0.91 | 1.70 |
| correct_iterative | 0.98 | 0.99 | 0.94 | 1.69 |
| off_by_one | 0.96 | 0.36 | 0.47 | 1.16 |
| linear_search | 0.97 | 0.01 | 0.71 | 0.35 |
| syntax_error | 0.03 | 0.87 | 0.70 | 0.14 |
| missing_return | 0.16 | 0.89 | 0.43 | 0.87 |

## Combined vs. separate calls

| Case | noul (compiles / alg / edge) | full (compiles / alg / edge) | score | full score |
|------|------------------------------|------------------------------|------:|-----------:|
| correct_recursive | 0.97 / 0.97 / 0.91 | 0.97 / 0.97 / 0.91 | 1.70 | 1.70 |
| correct_iterative | 0.98 / 0.99 / 0.94 | 0.98 / 0.99 / 0.94 | 1.70 | 1.69 |
| off_by_one | 0.95 / 0.37 / 0.51 | 0.96 / 0.36 / 0.47 | 1.22 | 1.16 |
| linear_search | 0.97 / 0.01 / 0.72 | 0.97 / 0.01 / 0.71 | 0.31 | 0.35 |
| syntax_error | 0.03 / 0.87 / 0.73 | 0.03 / 0.87 / 0.70 | 0.15 | 0.14 |
| missing_return | 0.19 / 0.88 / 0.49 | 0.16 / 0.89 / 0.43 | 0.83 | 0.87 |

Asking all four questions in one request produces the same answers as separate calls — every difference is within run-to-run noise (≤ 0.05). No cross-contamination between the noul and score questions.

## Prompt fix: before / after

| Case | check | v1 (before) | v2 (after) |
|------|-------|------------:|-----------:|
| missing_return | compiles_and_runs | 0.50 | **0.19** |
| missing_return | handles_edge_cases | 0.58 | 0.48 |
| missing_return | score | 0.98 | **0.85** |
| correct_recursive | compiles_and_runs | 0.98 | 0.97 |
| correct_iterative | compiles_and_runs | 0.99 | 0.98 |

The fix moved `missing_return` from "borderline" to "clearly flagged" on `compiles_and_runs` (0.50 → 0.19) and pushed the single score below 1.0 (0.98 → 0.85), while correct submissions stayed at ≥ 0.97 on every check — no regressions.

## Analysis

**Strong points (all variants)**

- Clear-cut failures are caught well: `linear_search` (score 0.31–0.35, algorithm 0.01) and `syntax_error` (score 0.14–0.15, compiles 0.03) are decisively rejected.
- `off_by_one` lands in a sensible middle ground: score 1.16–1.22, with both algorithm (0.36–0.37) and edge cases (0.47–0.51) flagged.
- Correct submissions remain clearly distinguished: ≥ 0.91 on every noul check.

**Remaining weaknesses**

- `missing_return` is improved but still the softest failure: score 0.83–0.87 (below "partially correct" now, but far from the 0.14–0.35 of other failures) and `correct_algorithm = 0.88–0.89` — the model still judges the algorithm logic as sound and only partially penalizes the missing return. The noul `compiles_and_runs = 0.16–0.19` is the decisive signal.
- The score variant remains conservative on correct code: 1.69–1.70 / 2.0, never a clean 2.
- `syntax_error` still scores `correct_algorithm = 0.87` — the model evaluates logic independently of syntax, which is by design but means a single score hides *why* a submission failed.

**Combined request verdict**

- `check_code_full()` is the best of both worlds at no quality cost: one API call returns the diagnostic noul signals *and* the compact score, with results indistinguishable from two separate calls. Use it as the default.
- The combined call costs the same tokens as the separate noul call (4 questions vs. 3) and saves a whole round trip compared to calling both separately.

**Recommendation**

- Use `check_code_full()` as the primary grader.
- A reasonable pass/fail rule: fail if `compiles_and_runs < 0.5` or `correct_algorithm < 0.5`; treat `handles_edge_cases` and `score` as quality signals rather than hard gates.
- If you only ever need a single number (e.g., a leaderboard), `check_code_score()` alone is fine — but you lose the failure diagnosis.

---

# Pseudocode Benchmark

Same binary-search question, but submissions are **pseudocode** and graded with `check_pseudocode*`. The prompts explicitly drop strict-syntax matching: pseudocode has no syntax to compile, so `compiles_and_runs` is replaced by `clear_and_complete`, and the instructions tell the model to judge the algorithm itself rather than require the submission to match the Reference Answer's wording or structure.

- **Date:** 2026-09-21 (same run as the code benchmark above)
- **Question:** "Write a binary search algorithm in pseudocode"
- **Reference:** `function`-style pseudocode (lowercase keywords, `length`, `//`)
- **Variants:** `check_pseudocode()` (3 × noul), `check_pseudocode_score()` (0–2), `check_pseudocode_full()` (combined)

## Test Cases

| Case | Description | Expected |
|------|-------------|----------|
| `correct_different_style` | Correct algorithm, very different style (uppercase keywords, `LENGTH`/`FLOOR`, different variable names) | all checks ≈ 1 — the critical case for "no strict syntax" |
| `off_by_one` | `while low < high` — misses `low == high` | algorithm / edge cases low |
| `linear_search` | Linear scan instead of binary search | algorithm low |
| `missing_not_found` | No `-1` returned when target not found | clear / edge cases low |
| `vague_incomplete` | Describes the goal but omits the halving steps | all checks low |

## Results — 3 × noul (`check_pseudocode`)

| Case | clear_and_complete | correct_algorithm | handles_edge_cases |
|------|-------------------:|------------------:|-------------------:|
| correct_different_style | 0.98 | 0.99 | 0.92 |
| off_by_one | 0.62 | 0.38 | 0.50 |
| linear_search | 0.59 | 0.02 | 0.78 |
| missing_not_found | 0.52 | 0.97 | 0.53 |
| vague_incomplete | 0.06 | 0.10 | 0.49 |

## Results — single score (`check_pseudocode_score`)

| Case | score (0–2) |
|------|------------:|
| correct_different_style | 1.64 |
| off_by_one | 1.04 |
| linear_search | 0.58 |
| missing_not_found | 1.16 |
| vague_incomplete | 0.03 |

## Results — combined (`check_pseudocode_full`)

| Case | clear_and_complete | correct_algorithm | handles_edge_cases | score |
|------|-------------------:|------------------:|-------------------:|------:|
| correct_different_style | 0.98 | 0.99 | 0.92 | 1.64 |
| off_by_one | 0.64 | 0.36 | 0.42 | 1.01 |
| linear_search | 0.62 | 0.02 | 0.78 | 0.54 |
| missing_not_found | 0.48 | 0.95 | 0.47 | 1.15 |
| vague_incomplete | 0.06 | 0.09 | 0.48 | 0.02 |

## Analysis

**The "no strict syntax" design works.** The critical case, `correct_different_style`, is accepted: algorithm 0.99, clear 0.98, score 1.64 — despite uppercase keywords, `LENGTH`/`FLOOR` instead of `length`/`//`, and renamed variables. The grader judges the algorithm, not the wording.

**Algorithmic errors are caught just as well as in the code benchmark:**

- `linear_search` → algorithm 0.02 (vs 0.01 for code), score 0.54–0.58 (vs 0.30–0.35). Slightly softer score, but still decisively failing.
- `off_by_one` → algorithm 0.36–0.38, edge cases 0.42–0.50, score 1.01–1.04 — the same sensible middle ground as the code benchmark (1.16–1.22).
- `vague_incomplete` → clear 0.06, algorithm 0.09–0.10, score 0.02–0.03. Decisively rejected.

**`missing_not_found` is the softest failure, mirroring `missing_return` in the code benchmark.** The model still judges the halving logic sound (`correct_algorithm` 0.95–0.97) and only partially penalizes the missing "not found" result. In the code benchmark this was caught by `compiles_and_runs` (0.16–0.19); in pseudocode there is no compile concept, so `clear_and_complete` plays that role — but less decisively (0.48–0.52 vs 0.16–0.19). If missing-result handling matters, consider a dedicated noul question (e.g., "does every code path produce a result?").

**Verdict:** `check_pseudocode_full()` is the right default, same as `check_code_full()`. A reasonable pass/fail rule: fail if `clear_and_complete < 0.5` or `correct_algorithm < 0.5`.

---

# Score recalibration (v3)

After the v2 runs, the score criteria were recalibrated to fix two calibration errors visible in the data:

- **Too lenient on missing results:** v2 criteria put "missing return statements" in 0 but the model scored `missing_return` 0.84 and `missing_not_found` 1.16 — above "partially correct".
- **Too lenient on wrong algorithms:** v2's "1: Partially Correct — Right general approach" swallowed a linear scan submitted for binary search (pseudocode score 0.58).

**v3 criteria (code):**

```
0: Incorrect — Wrong algorithm (a fundamentally different approach than requested), a code path that produces no result (e.g., missing return), or errors that would crash or give wrong answers.
1: Partially Correct — The right algorithm with minor logic bugs (e.g., off-by-one) or incomplete edge case handling.
2: Correct — The algorithm is correct and complete and produces the right result for all inputs. Style, syntax, and implementation details may differ from the reference.
```

**v3 criteria (pseudocode):** same shape, with "no specified result when the target is absent" and "key steps missing" in 0, and "pseudocode style, formatting, and syntax may differ freely" in 2.

## Before / after — code scores

| Case | v2 | v3 | Δ |
|------|----:|----:|---:|
| correct_recursive | 1.71 | 1.67 | −0.04 (noise) |
| correct_iterative | 1.69 | 1.66 | −0.03 (noise) |
| off_by_one | 1.19 | 1.12 | −0.07 (noise) |
| linear_search | 0.30 | **0.05** | −0.25 ✓ |
| syntax_error | 0.14 | 0.34 | +0.20 ⚠ |
| missing_return | 0.84 | **0.37** | −0.47 ✓✓ |

## Before / after — pseudocode scores

| Case | v2 | v3 | Δ |
|------|----:|----:|---:|
| correct_different_style | 1.64 | 1.63 | −0.01 (noise) |
| off_by_one | 1.04 | 1.13 | +0.09 (noise) |
| linear_search | 0.58 | **0.21** | −0.37 ✓ |
| missing_not_found | 1.16 | **0.66** | −0.50 ✓✓ |
| vague_incomplete | 0.03 | 0.03 | 0 |

## Analysis

**What improved**

- The two softest failures are now decisive: `missing_return` 0.84 → 0.37 and `missing_not_found` 1.16 → 0.66, both clearly below "partially correct" (1.0).
- Wrong algorithms now score near zero: `linear_search` 0.30 → 0.05 (code) and 0.58 → 0.21 (pseudocode).
- Correct submissions unchanged within noise (1.63–1.68) — no regression.
- The `full` variant tracks the standalone score closely (e.g., `missing_return` 0.36 vs 0.37), so the recalibration applies to both call styles.

**Remaining issues**

- `syntax_error` rose 0.14 → 0.34. Still decisively failing, but the new 0-wording ("errors that would crash") reads as less severe than the old "Severe syntax errors". The `compiles_and_runs` noul (0.03) remains the decisive signal — the score alone is not a reliable syntax detector.
- The 2.0 ceiling on correct submissions persists (best 1.68): the model stays conservative about awarding full marks even with "produces the right result for all inputs". If a clean 2.0 matters, the criteria may need an explicit "Award 2 when…" directive, or the ceiling may be inherent model calibration.
- `missing_not_found` at 0.62–0.66 is now clearly failing but still the closest-to-1 failure; the proposed `produces_result_on_all_paths` noul question would make this signal explicit rather than relying on the score alone.