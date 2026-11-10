
import csv
import os
import time

from agent import generate_code
from executor import execute_code
from load_humaneval import load_humaneval
from logger import log_attempt
from feedback import correct_code


RESULTS_FILE = "results/humaneval_results.csv"

STRATEGIES = [
    "baseline",
    "execution",
    "unit_test",
    "reflection"
]

MAX_ATTEMPTS = 5
RUN_ID = "humaneval_20261013"


# ---------------------------------------------------------
# READ EXISTING RESULTS
# ---------------------------------------------------------

def load_logged_results():

    logged = {}

    if not os.path.exists(RESULTS_FILE):
        return logged

    with open(
        RESULTS_FILE,
        "r",
        newline="",
        encoding="utf-8"
    ) as file:

        reader = csv.DictReader(file)

        for row in reader:

            key = (
                row["problem_id"],
                row["feedback_strategy"],
                int(row["attempt"])
            )

            logged[key] = row

    return logged


def already_logged(logged, task_id, strategy, attempt):

    return (
        task_id,
        strategy,
        attempt
    ) in logged


# ---------------------------------------------------------
# GET COMMON INITIAL SOLUTION
# ---------------------------------------------------------

def get_saved_initial_code(task_id, logged):

    row = logged.get((task_id, "baseline", 1))

    if row and row.get("code"):
        return row["code"]

    return None


# ---------------------------------------------------------
# RUN ONE HUMAN-EVAL TEST
# ---------------------------------------------------------

def run_test(code, tests, entry_point):

    test_code = tests + f"\n\ncheck({entry_point})"

    return execute_code(
        code=code,
        tests=test_code
    )


# ---------------------------------------------------------
# MAIN EXPERIMENT
# ---------------------------------------------------------

def main():

    problems = load_humaneval()
    logged = load_logged_results()

    print("=" * 60)
    print("HUMANEVAL SELF-CORRECTION EXPERIMENT")
    print("=" * 60)

    print(f"Total problems: {len(problems)}")
    print(f"Maximum attempts: {MAX_ATTEMPTS}")
    print(f"Strategies: {', '.join(STRATEGIES)}")

    for index, problem_data in enumerate(problems, start=1):

        task_id = problem_data["task_id"]
        prompt = problem_data["prompt"]
        tests = problem_data["test"]
        entry_point = problem_data["entry_point"]

        print("\n" + "#" * 60)
        print(f"Problem {index}/{len(problems)}: {task_id}")
        print("#" * 60)

        # Reuse the initial baseline code if available.
        initial_code = get_saved_initial_code(task_id, logged)

        if initial_code is None:

            print("Generating common initial solution...")

            initial_code = generate_code(prompt)

        # Every strategy begins with the same initial code.
        for strategy in STRATEGIES:

            print(f"\nSTRATEGY: {strategy.upper()}")

            code = initial_code
            previous_error = ""
            previous_feedback = ""
            strategy_succeeded = False

            # Resume from existing attempts when possible.
            start_attempt = 1

            for attempt in range(1, MAX_ATTEMPTS + 1):

                key = (task_id, strategy, attempt)

                if key in logged:

                    saved = logged[key]

                    code = saved.get("code") or code

                    print(
                        f"Attempt {attempt} already recorded; "
                        "skipping execution."
                    )

                    if saved.get("success", "").lower() == "true":
                        strategy_succeeded = True
                        break

                    previous_error = saved.get("error", "")
                    previous_feedback = saved.get(
                        "test_feedback", ""
                    )

                    start_attempt = attempt + 1
                    continue

                start_attempt = attempt
                break

            if strategy_succeeded:
                print("Strategy already succeeded.")
                continue

            if start_attempt > MAX_ATTEMPTS:
                print("All attempts already recorded.")
                continue

            # Recover the latest failed code before resuming.
            if start_attempt > 1:

                previous_row = logged.get(
                    (task_id, strategy, start_attempt - 1)
                )

                if previous_row:

                    code = previous_row.get("code") or code
                    previous_error = previous_row.get("error", "")
                    previous_feedback = previous_row.get(
                        "test_feedback", ""
                    )

            # Execute remaining attempts.
            for attempt in range(start_attempt, MAX_ATTEMPTS + 1):

                # Generate a correction after a failed attempt.
                if attempt > 1:

                    print(
                        f"\nGenerating correction for attempt {attempt}..."
                    )

                    try:

                        code = correct_code(
                            problem=prompt,
                            previous_code=code,
                            feedback_strategy=strategy,
                            error=previous_error,
                            test_feedback=previous_feedback
                        )

                    except Exception as exc:

                        print("Correction generation failed:", exc)
                        break

                    if not code or not code.strip():

                        print("The model returned empty code.")
                        break

                print(f"\n--- ATTEMPT {attempt} ---")
                print(code)

                start_time = time.time()

                try:

                    result = run_test(
                        code=code,
                        tests=tests,
                        entry_point=entry_point
                    )

                except Exception as exc:

                    result = {
                        "success": False,
                        "output": "",
                        "error": str(exc),
                        "execution_time": time.time() - start_time
                    }

                success = bool(result["success"])

                error = result.get("error", "") or ""
                output = result.get("output", "") or ""

                # HumanEval assertion failures commonly appear
                # in stderr, so pass that information as feedback.
                test_feedback = output if output.strip() else error

                # Save each attempt immediately.
                log_attempt(
                    run_id=RUN_ID,
                    problem_id=task_id,
                    feedback_strategy=strategy,
                    attempt=attempt,
                    success=success,
                    execution_time=result.get(
                        "execution_time",
                        time.time() - start_time
                    ),
                    code=code,
                    error=error,
                    test_feedback=test_feedback,
                    results_file=RESULTS_FILE
                )

                # Update in-memory results to prevent duplicates
                # if this process continues.
                logged[(task_id, strategy, attempt)] = {
                    "problem_id": task_id,
                    "feedback_strategy": strategy,
                    "attempt": str(attempt),
                    "success": str(success),
                    "code": code,
                    "error": error,
                    "test_feedback": test_feedback
                }

                if success:

                    print(f"ATTEMPT {attempt}: SUCCESS")
                    strategy_succeeded = True
                    break

                print(f"ATTEMPT {attempt}: FAILED")

                if error:
                    print(error[-1000:])

                previous_error = error
                previous_feedback = test_feedback

            if not strategy_succeeded:
                print(
                    f"{strategy.upper()} did not solve "
                    f"{task_id} within the available attempts."
                )

    print("\n" + "=" * 60)
    print("HUMANEVAL EXPERIMENT FINISHED")
    print(f"Results saved to: {RESULTS_FILE}")
    print("=" * 60)


if __name__ == "__main__":
    main()
