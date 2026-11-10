
import csv
import os
from datetime import datetime

from load_mbpp import load_mbpp_problems
from feedback import correct_code
from executor import execute_mbpp_code


# Five problems that failed on the original baseline attempt
TARGET_IDS = {
    "mbpp_20",
    "mbpp_59",
    "mbpp_63",
    "mbpp_69",
    "mbpp_95",
}

ORIGINAL_RESULTS = "results/mbpp_results_100.csv"
ORIGINAL_RUN_ID = "20261001_183513"

MAX_CORRECTION_ATTEMPTS = 4

RUN_ID = (
    "improved_reflection_test_"
    + datetime.now().strftime("%Y%m%d_%H%M%S")
)

RESULTS_FILE = os.path.join("results", f"{RUN_ID}.csv")

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
    "test_feedback",
]


def load_original_initial_failures():
    """Load the original baseline code and errors for the five problems."""
    with open(
        ORIGINAL_RESULTS,
        newline="",
        encoding="utf-8-sig",
    ) as file:
        rows = list(csv.DictReader(file))

    initial_rows = {}

    for row in rows:
        if (
            row["run_id"] == ORIGINAL_RUN_ID
            and row["feedback_strategy"] == "baseline"
            and row["attempt_type"] == "initial"
            and row["problem_id"] in TARGET_IDS
        ):
            initial_rows[row["problem_id"]] = row

    missing = TARGET_IDS - set(initial_rows)
    if missing:
        raise ValueError(
            f"Original initial rows not found for: {sorted(missing)}"
        )

    return initial_rows


def main():
    problems = load_mbpp_problems(100)
    problems_by_id = {
        problem["problem_id"]: problem
        for problem in problems
    }

    original_rows = load_original_initial_failures()

    print("\nOriginal failed problems loaded:")
    for problem_id in sorted(original_rows):
        print(f"- {problem_id}")

    os.makedirs("results", exist_ok=True)

    with open(
        RESULTS_FILE,
        "w",
        newline="",
        encoding="utf-8",
    ) as file:
        writer = csv.DictWriter(file, fieldnames=FIELDNAMES)
        writer.writeheader()

        for problem_id in sorted(TARGET_IDS):
            if problem_id not in problems_by_id:
                raise ValueError(
                    f"{problem_id} was not found in the loaded MBPP dataset"
                )

            problem_data = problems_by_id[problem_id]
            original = original_rows[problem_id]

            problem = problem_data["prompt"]
            required_call = problem_data["required_call"]
            test_list = problem_data["tests"]
            test_imports = problem_data["test_imports"]

            enhanced_problem = f"""
{problem}

Required function call:
{required_call}
"""

            code = original["code"]
            previous_error = original["error"]
            previous_test_feedback = original.get("test_feedback", "")

            print(f"\n{'=' * 55}")
            print(f"Problem: {problem_id}")
            print(f"Starting from the original failed baseline code.")

            for attempt in range(1, MAX_CORRECTION_ATTEMPTS + 1):
                # Use the same benchmark executor and tests.
                result = execute_mbpp_code(
                    code,
                    test_list,
                    test_imports,
                )

                success = bool(result.get("success", False))
                error = result.get("error", "") or ""
                execution_time = result.get("execution_time", 0)

                writer.writerow({
                    "timestamp": datetime.now().isoformat(),
                    "run_id": RUN_ID,
                    "problem_id": problem_id,
                    "feedback_strategy": "improved_reflection",
                    "attempt": attempt,
                    "attempt_type": "correction",
                    "success": success,
                    "execution_time": execution_time,
                    "code": code,
                    "error": error,
                    "test_feedback": error,
                })
                file.flush()

                print(
                    f"Correction {attempt}: "
                    f"{'PASS' if success else 'FAIL'}"
                )

                if success:
                    break

                if attempt < MAX_CORRECTION_ATTEMPTS:
                    code = correct_code(
                        problem=enhanced_problem,
                        previous_code=code,
                        feedback_strategy="reflection",
                        error=error or previous_error,
                        test_feedback=error or previous_test_feedback,
                    )

                    previous_error = error
                    previous_test_feedback = error

    print("\nTest completed.")
    print(f"Run ID: {RUN_ID}")
    print(f"Results saved to: {RESULTS_FILE}")


if __name__ == "__main__":
    main()
