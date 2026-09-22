"""Benchmark jev's code-checking on binary search submissions.

Runs the check variants (check_code / check_pseudocode) on Python and
pseudocode submissions. Each returns one noul float in [0, 1] per criterion
plus the derived 0-2 score (criteria joined with coefficients).
"""

import json

from jev_exam_scoring import check_code, check_pseudocode

QUESTION = "Write a binary search algorithm"

CORRECT_REFERENCE = """def binary_search(arr, target):
    low = 0
    high = len(arr) - 1
    while low <= high:
        mid = (low + high) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            low = mid + 1
        else:
            high = mid - 1
    return -1
"""

CASES = [
    (
        "correct_recursive",
        "Correct recursive implementation",
        """def binary_search_recursive(arr, target, low=0, high=None):
    if high is None:
        high = len(arr) - 1

    if low > high:
        return -1

    mid = (low + high) // 2

    if arr[mid] == target:
        return mid
    elif arr[mid] < target:
        return binary_search_recursive(arr, target, mid + 1, high)
    else:
        return binary_search_recursive(arr, target, low, mid - 1)
""",
    ),
    (
        "correct_iterative",
        "Correct iterative implementation",
        """def binary_search(arr, target):
    low, high = 0, len(arr) - 1
    while low <= high:
        mid = (low + high) // 2
        if arr[mid] == target:
            return mid
        if arr[mid] < target:
            low = mid + 1
        else:
            high = mid - 1
    return -1
""",
    ),
    (
        "off_by_one",
        "Off-by-one: while low < high misses low == high",
        """def binary_search(arr, target):
    low = 0
    high = len(arr) - 1
    while low < high:
        mid = (low + high) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            low = mid + 1
        else:
            high = mid - 1
    return -1
""",
    ),
    (
        "linear_search",
        "Wrong algorithm: linear scan instead of binary search",
        """def linear_search(arr, target):
    for i, value in enumerate(arr):
        if value == target:
            return i
    return -1
""",
    ),
    (
        "syntax_error",
        "Syntax error: missing colon after while",
        """def binary_search(arr, target):
    low = 0
    high = len(arr) - 1
    while low <= high
        mid = (low + high) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            low = mid + 1
        else:
            high = mid - 1
    return -1
""",
    ),
    (
        "missing_return",
        "Missing return: no -1 when target not found",
        """def binary_search(arr, target):
    low = 0
    high = len(arr) - 1
    while low <= high:
        mid = (low + high) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            low = mid + 1
        else:
            high = mid - 1
""",
    ),
]


PSEUDOCODE_QUESTION = "Write a binary search algorithm in pseudocode"

PSEUDOCODE_REFERENCE = """function binary_search(arr, target):
    low = 0
    high = length(arr) - 1
    while low <= high:
        mid = (low + high) // 2
        if arr[mid] == target:
            return mid
        else if arr[mid] < target:
            low = mid + 1
        else:
            high = mid - 1
    return -1
"""

PSEUDOCODE_CASES = [
    (
        "correct_different_style",
        "Correct algorithm in a very different pseudocode style (uppercase keywords, different names)",
        """FUNCTION binarySearch(array, target):
    left = 0
    right = LENGTH(array) - 1
    WHILE left <= right:
        middle = FLOOR((left + right) / 2)
        IF array[middle] == target THEN
            RETURN middle
        ELSE IF array[middle] < target THEN
            left = middle + 1
        ELSE
            right = middle - 1
    RETURN -1
""",
    ),
    (
        "off_by_one",
        "Off-by-one: while low < high misses low == high",
        """function binary_search(arr, target):
    low = 0
    high = length(arr) - 1
    while low < high:
        mid = (low + high) // 2
        if arr[mid] == target:
            return mid
        else if arr[mid] < target:
            low = mid + 1
        else:
            high = mid - 1
    return -1
""",
    ),
    (
        "linear_search",
        "Wrong algorithm: linear scan instead of binary search",
        """function search(arr, target):
    for i = 0 to length(arr) - 1:
        if arr[i] == target:
            return i
    return -1
""",
    ),
    (
        "missing_not_found",
        "Missing result: no -1 returned when target not found",
        """function binary_search(arr, target):
    low = 0
    high = length(arr) - 1
    while low <= high:
        mid = (low + high) // 2
        if arr[mid] == target:
            return mid
        else if arr[mid] < target:
            low = mid + 1
        else:
            high = mid - 1
""",
    ),
    (
        "vague_incomplete",
        "Vague and incomplete: describes the goal but omits the halving steps",
        """function binary_search(arr, target):
    # Search the array for the target
    # Return the index where it is found, or -1 if absent
    ...
""",
    ),
]


def run_benchmark(cases, reference, question, variants) -> dict:
    """Run every case through every (name, fn) variant; return {case: {variant: result}}."""
    results = {}
    for name, description, submission in cases:
        print(f"Running: {name} ({description})")
        entry = {}
        for variant, fn in variants:
            try:
                entry[variant] = fn(submission, reference, question, 2.0)
            except Exception as exc:
                entry[variant] = {"error": str(exc)}
        results[name] = entry
    return results


def main() -> None:
    results = {
        "code": run_benchmark(
            CASES,
            CORRECT_REFERENCE,
            QUESTION,
            (("check", check_code),),
        ),
        "pseudocode": run_benchmark(
            PSEUDOCODE_CASES,
            PSEUDOCODE_REFERENCE,
            PSEUDOCODE_QUESTION,
            (("check", check_pseudocode),),
        ),
    }
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()