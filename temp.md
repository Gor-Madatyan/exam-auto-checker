# API calls reconstructed from mock exam screenshot

Base URL: `http://127.0.0.1:8000`
Auth: all endpoints require header `X-API-Key: <API_KEY>` (`API_KEY` from `.env`).

---

## 1 — Solve 2x² − 8x + 6 = 0 (4 pts) → `fact`

Student answer is factually complete (`x1=1, x2=3`), so use `POST /api/v1/fact/check`.

```bash
curl -X POST http://127.0.0.1:8000/api/v1/fact/check \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $API_KEY" \
  -d @- <<'JSON'
{
  "question_description": "Solve 2x^2 - 8x + 6 = 0.",
  "correct_answer": "x1 = 1, x2 = 3. Divide by 2: x^2 - 4x + 3 = 0, factor as (x - 1)(x - 3) = 0.",
  "student_answer": "x1 = 1\nx2 = 3",
  "max_points": 4
}
JSON
```

Request JSON:

```json
{
  "question_description": "Solve 2x^2 - 8x + 6 = 0.",
  "correct_answer": "x1 = 1, x2 = 3. Divide by 2: x^2 - 4x + 3 = 0, factor as (x - 1)(x - 3) = 0.",
  "student_answer": "x1 = 1\nx2 = 3",
  "max_points": 4
}
```

Expected: ~4/4 (factually_correct≈1, complete≈1, answers_question≈1).

---

## 2 — Car 10 m/s → 30 m/s in 5 s (6 pts) → `fact`

Student gets `a=4 m/s²` right, but `s=50 m` wrong (should be 100 m). Use `POST /api/v1/fact/check`.

```bash
curl -X POST http://127.0.0.1:8000/api/v1/fact/check \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $API_KEY" \
  -d @- <<'JSON'
{
  "question_description": "A car accelerates uniformly from 10 m/s to 30 m/s in 5 s. Find its acceleration and the distance it covers in that time.",
  "correct_answer": "Acceleration a = (30 - 10) / 5 = 4 m/s^2. Distance s = 5 * (30 + 10) / 2 = 5 * 20 = 100 m.",
  "student_answer": "30-10=20\n20/5=4\na=4m/s^2\ns=5*(30+10)/2=50m",
  "max_points": 6
}
JSON
```

Request JSON:

```json
{
  "question_description": "A car accelerates uniformly from 10 m/s to 30 m/s in 5 s. Find its acceleration and the distance it covers in that time.",
  "correct_answer": "Acceleration a = (30 - 10) / 5 = 4 m/s^2. Distance s = 5 * (30 + 10) / 2 = 5 * 20 = 100 m.",
  "student_answer": "30-10=20\n20/5=4\na=4m/s^2\ns=5*(30+10)/2=50m",
  "max_points": 6
}
```

Expected: partial credit (~4.8/6 in screenshot — correct acceleration, arithmetic slip on distance).

---

## 3 — `is_palindrome(s)` Python (5 pts) → `code`

Pure code task. Use `POST /api/v1/code/check`.

```bash
curl -X POST http://127.0.0.1:8000/api/v1/code/check \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $API_KEY" \
  -d @- <<'JSON'
{
  "question_description": "Write a Python function is_palindrome(s) that returns True if the string s reads the same forwards and backwards, and False otherwise.",
  "correct_code": "def is_palindrome(s):\n    return s == s[::-1]",
  "student_code": "def is_palindrome(s):\n    return s == s[::-1]",
  "max_points": 5
}
JSON
```

Request JSON:

```json
{
  "question_description": "Write a Python function is_palindrome(s) that returns True if the string s reads the same forwards and backwards, and False otherwise.",
  "correct_code": "def is_palindrome(s):\n    return s == s[::-1]",
  "student_code": "def is_palindrome(s):\n    return s == s[::-1]",
  "max_points": 5
}
```

Expected: 5/5 (compiles_and_runs≈1, correct_algorithm≈1, handles_edge_cases≈1).

---

## 4 — What is a hash collision? (5 pts) → `fact`

Short definitional answer with a reference answer (screenshot mentions reference answer with "appends colliding keys" / "probes for another free slot"). Use `POST /api/v1/fact/check` — not `essay` (essay is for topic+requirements+grammar, fact is for correct_answer comparison).

```bash
curl -X POST http://127.0.0.1:8000/api/v1/fact/check \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $API_KEY" \
  -d @- <<'JSON'
{
  "question_description": "What is a hash collision? Describe one way a hash table can handle it.",
  "correct_answer": "A hash collision is when two different keys hash to the same value/index. One way to handle it is chaining (append colliding keys in a linked list at that index) or open addressing (probe for another free slot).",
  "student_answer": "Hash collision is a phenomenon which happens when several keys end up having the same hash value. One way to handle it is by keeping a linked list of values which have the same hash value.",
  "max_points": 5
}
JSON
```

Request JSON:

```json
{
  "question_description": "What is a hash collision? Describe one way a hash table can handle it.",
  "correct_answer": "A hash collision is when two different keys hash to the same value/index. One way to handle it is chaining (append colliding keys in a linked list at that index) or open addressing (probe for another free slot).",
  "student_answer": "Hash collision is a phenomenon which happens when several keys end up having the same hash value. One way to handle it is by keeping a linked list of values which have the same hash value.",
  "max_points": 5
}
```

Expected: 5/5 (student describes separate chaining, conceptually equivalent to reference).

---

### Summary table

| # | Domain | Endpoint | max_points |
|---|--------|----------|------------|
| 1 | fact | `POST /api/v1/fact/check` | 4 |
| 2 | fact | `POST /api/v1/fact/check` | 6 |
| 3 | code | `POST /api/v1/code/check` | 5 |
| 4 | fact | `POST /api/v1/fact/check` | 5 |

Total: 20 pts. Reference answers for 1/2/4 were collapsed in the screenshot ("Reference answer" not expanded), so `correct_answer`/`correct_code` above are reconstructed canonical answers — swap in the exact reference text if you want byte-identical grading.
