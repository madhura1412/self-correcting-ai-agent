import csv
import os
from datetime import datetime


DEFAULT_RESULTS_FILE = os.path.join(
    "results",
    "demo_results.csv"
)


FIELDNAMES = [
    "timestamp",
    "run_id",
    "problem_id",
    "feedback_strategy",
    "attempt",
    "attempt_type",
    "success",
    "execution_time",
    "code",
    "error",
    "test_feedback"
]


def log_attempt(
    run_id,
    problem_id,
    feedback_strategy,
    attempt,
    success,
    execution_time,
    code,
    error,
    test_feedback,
    results_file=DEFAULT_RESULTS_FILE
):

    os.makedirs(
        os.path.dirname(results_file),
        exist_ok=True
    )

    file_exists = os.path.exists(results_file)

    row = {
        "timestamp": datetime.now().isoformat(),
        "run_id": run_id,
        "problem_id": problem_id,
        "feedback_strategy": feedback_strategy,
        "attempt": attempt,
        "attempt_type": (
            "initial"
            if attempt == 1
            else "correction"
        ),
        "success": success,
        "execution_time": round(execution_time, 4),
        "code": code,
        "error": error,
        "test_feedback": test_feedback
    }

    with open(
        results_file,
        "a",
        newline="",
        encoding="utf-8"
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=FIELDNAMES
        )

        if not file_exists:
            writer.writeheader()

        writer.writerow(row)