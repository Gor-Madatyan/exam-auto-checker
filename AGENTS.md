# AGENTS.md — jev-exam-scoring

Automated exam scoring backed by the **jev scoring backend** (via OpenRouter Decisions API).
Each scoring domain exposes one `POST /api/v1/<domain>/check` endpoint returning
per-criterion `noul` floats in `[0, 1]`, a derived 0–1 score, and `points_given`
(`score * max_points`).

## Setup

- Python `>=3.12` (see `.python-version`), managed with `uv`. Venv lives in `.venv/`.
- Install deps: `uv sync`
- Env: `cp .env.example .env`, then fill in:
  - `OPENROUTER_API_KEY` — required, used by `src/jev_exam_scoring/util.py` (`ask_jev`, model `upstage/solar-decide`, 60s timeout).
  - `API_KEY` — required, clients must send it as the `X-API-Key` header (see `api/security.py`, `api/config.py`).
- Never commit `.env` (gitignored). Only `.env.example` with placeholders.

## Commands

- Run server: `uv run serve` (defaults `127.0.0.1:8000`; flags `--host/--port/--reload`, or `HOST`/`PORT`/`RELOAD` env) — entrypoint `jev_exam_scoring.api.serve:main`.
- Dev mode: `uv run serve --reload`
- Run library example: check `src/jev_exam_scoring/example.py`
- Benchmarks (hit the live OpenRouter backend, cost money / need keys):
  - `uv run python benchmark.py` (code + pseudocode, binary search cases)
  - `uv run python essay_benchmark.py`
  - `uv run python fact_benchmark.py`
- No test suite or linter configured. If adding one, declare it in `pyproject.toml`.

## Repo layout

- `src/jev_exam_scoring/` — scoring library (importable as `jev_exam_scoring`):
  - `util.py` — `build_state()`, `ask_jev()`, `dense_power()` / `dense_score()` (maps 0–1 weighted average plus +0.1 bonus capped at 1.0 → 0–1 via gamma=0.38 curve). All scoring modules build on this.
  - `code_check.py` — `check_code()`, `code_score_from_checks()`; weights 0.2 compiles / 0.5 algorithm / 0.3 edge cases. Fail if `compiles_and_runs < 0.5` or `correct_algorithm < 0.5`.
  - `essay_check.py` / `fact_check.py` / `pseudocode_check.py` — same pattern: `check_<domain>()` + `<domain>_score_from_checks()` + `*_WEIGHT` constants.
  - `__init__.py` — re-exports all `check_*` functions and weight constants.
  - `example.py` — usage example.
- `src/jev_exam_scoring/api/` — FastAPI app:
  - `app.py` — `create_app()` factory; `routers/` — one router per domain (`code.py`, `essay.py`, `fact.py`, `pseudocode.py`), each a single `/check` endpoint.
  - `schemas.py`, `security.py` (X-API-Key), `config.py` (settings), `_helpers.py`, `serve.py`.
- Root: `benchmark.py`, `essay_benchmark.py`, `fact_benchmark.py` (live-backend benchmarks); `results.md` (published benchmark results — update if prompts/weights change); `openapi.yaml` (committed API snapshot — regenerate/update when routes or schemas change); `pyproject.toml`; `uv.lock`.

## Conventions for agents

- Implementation is the source of truth. When any doc (`results.md`, `openapi.yaml`, `rules.md`,
  docstrings, router descriptions, benchmark bands) disagrees with the code in
  `src/jev_exam_scoring/`, the code wins: fix the doc, never silently "correct" the code.
  An intentional behavior change requires a benchmark run plus updates to `results.md`
  and `openapi.yaml` (see below).
- Scoring logic lives in the library modules, API routers only validate/shape I/O. Keep `NOUL_QUESTIONS`, weights, and `*_score_from_checks()` derivation together per domain; don't duplicate the math in routers.
- Scores: criteria are `noul` floats `[0, 1]`; derived score is 0–1 via `dense_score(min(weighted_avg + 0.1, 1))`; `points_given = score * max_points`. Preserve the documented weight constants and the fail-gate comments (e.g. code fail if compiles/algorithm `< 0.5`).
- `ask_jev()` maps transport errors to 502 upstream and missing keys to 500 — keep the `timeout=60` (prevents hung threadpool workers).
- Prompt wording matters (see `results.md` v2/v3 revisions). If you retune instructions, re-run the matching benchmark script and update `results.md`.
- Keep `openapi.yaml` in sync with `api/` changes.
- Follow existing style: `from __future__ import annotations` in API files, `from .util import *` in scoring modules, type hints, docstrings noting weights and gates.
