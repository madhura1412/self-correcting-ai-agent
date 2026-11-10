
import csv
import os
from datetime import datetime

from load_mbpp import load_mbpp_problems
from feedback import correct_code
from executor import execute_mbpp_code


PROBLEM_ID = "mbpp_95"
ORIGINAL_RESULTS = "results/mbpp_results_100.csv"
ORIGINAL_RUN_ID = "20261001_183513"

RUN_ID = "mbpp95_reflection_" + datetime.now().strftime("%Y%m%d_%H%M%S")
RESULTS_FILE = os.path.join("results", f"{RUN_ID}.csv")


def main():
    # Load the original failed baseline solution.
    with open(
        ORIGINAL_RESULTS,
        newline="",
        encoding="utf-8-sig",
    ) as file:
        rows = list(csv.DictReader(file))

    original = next(
        (
            row for row in rows
            if row["run_id"] == ORIGINAL_RUN_ID
            and row["problem_id"] == PROBLEM_ID
            and row["feedback_strategy"] == "baseline"
            and row["attempt_type"] == "initial"
        ),
        None,
    )

    if original is None:
        raise ValueError("Original failed solution was not found.")

    # Load the matching MBPP problem and its original tests.
    problems = load_mbpp_problems(100)
    problem_data = next(
        p for p in problems if p["problem_id"] == PROBLEM_ID
    )

    problem = f"""
{problem_data['prompt']}

Required function call:
{problem_data['required_call']}
"""

    code = original["code"]
    error = original["error"]

    # Ask the updated reflection strategy to correct the original code.
    corrected_code = correct_code(
        problem=problem,
        previous_code=code,
        feedback_strategy="reflection",
        error=error,
        test_feedback=error,
    )

    result = execute_mbpp_code(
        corrected_code,
        problem_data["tests"],
        problem_data["test_imports"],
    )

    success = bool(result.get("success", False))
    final_error = result.get("error", "") or ""

    os.makedirs("results", exist_ok=True)

    with open(
        RESULTS_FILE,
        "w",
        newline="",
        encoding="utf-8",
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=[
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
                "test_feedback",
            ],
        )

        writer.writeheader()
        writer.writerow({
            "timestamp": datetime.now().isoformat(),
            "run_id": RUN_ID,
            "problem_id": PROBLEM_ID,
            "feedback_strategy": "improved_reflection",
            "attempt": 1,
            "attempt_type": "correction",
            "success": success,
            "execution_time": result.get("execution_time", 0),
            "code": corrected_code,
            "error": final_error,
            "test_feedback": error,
        })

    print("\n--- Corrected code ---")
    print(corrected_code)
    print("\n--- Test result ---")
    print("PASS" if success else "FAIL")
    if final_error:
        print(final_error)
    print(f"\nResults saved to: {RESULTS_FILE}")


if __name__ == "__main__":
    main()
