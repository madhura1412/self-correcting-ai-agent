
import argparse
import csv
import json
import os
import subprocess
import time
from pathlib import Path

from apps_agent import generate_apps_code
from apps_feedback import correct_apps_code
from apps_evaluator import evaluate


# ==========================================
# CONFIGURATION
# ==========================================

DATASET = Path("results/apps_competition_20.jsonl")
RESULTS_DIR = Path("results")

STRATEGIES = [
    "baseline",
    "execution",
    "unit_test",
    "reflection",
]

MAX_ATTEMPTS = 5
DOCKER_IMAGE = "python:3.11-alpine"

SUMMARY_FIELDS = [
    "problem_id",
    "strategy",
    "initial_pass",
    "final_pass",
    "attempts",
    "passed_tests",
    "total_tests",
    "execution_time",
]

ATTEMPT_FIELDS = [
    "problem_id",
    "strategy",
    "attempt",
    "passed",
    "passed_tests",
    "total_tests",
    "code",
    "test_results",
]


# ==========================================
# SAFETY CHECKS
# ==========================================

def check_docker():
    print("Checking Docker...", flush=True)

    try:
        result = subprocess.run(
            [
                "docker",
                "run",
                "--rm",
                "--network",
                "none",
                DOCKER_IMAGE,
                "python",
                "-c",
                "print(2 + 3)",
            ],
            capture_output=True,
            text=True,
            timeout=60,
        )

    except (
        FileNotFoundError,
        subprocess.TimeoutExpired,
    ) as error:
        raise RuntimeError(
            f"Docker is unavailable: {error}"
        ) from error

    if (
        result.returncode != 0
        or result.stdout.strip() != "5"
    ):
        raise RuntimeError(
            "Docker execution failed:\n"
            + result.stderr
        )

    print("Docker check PASSED", flush=True)


def check_evaluation(result):
    """Stop if the evaluator cannot run reliably."""

    for test in result["tests"]:
        status = str(test.get("status", "")).lower()
        stderr = str(test.get("stderr", "")).lower()

        infrastructure_messages = [
            "docker api",
            "docker daemon",
            "cannot connect to docker",
            "dockerdesktoplinuxengine",
            "failed to connect to the docker",
            "cannot find the file specified",
        ]

        if any(
            message in stderr
            for message in infrastructure_messages
        ):
            raise RuntimeError(
                "Docker infrastructure failure. "
                "Experiment stopped safely."
            )

        if status in [
            "docker_error",
            "infrastructure_error",
        ]:
            raise RuntimeError(
                "Evaluator infrastructure failure. "
                "Experiment stopped safely."
            )


# ==========================================
# LOAD DATASET
# ==========================================

def load_problems():
    with DATASET.open(encoding="utf-8") as file:
        problems = [
            json.loads(line)
            for line in file
            if line.strip()
        ]

    ids = [
        int(problem["problem_id"])
        for problem in problems
    ]

    if len(ids) != len(set(ids)):
        raise ValueError(
            "Duplicate problem IDs in dataset."
        )

    for problem in problems:
        tests = problem["input_output"]

        if isinstance(tests, str):
            tests = json.loads(tests)

        if not isinstance(tests, dict):
            raise ValueError(
                "Invalid APPS test format."
            )

        if tests.get("fn_name"):
            raise ValueError(
                "Function-call APPS tests "
                "are not supported."
            )

        if (
            not tests.get("inputs")
            or len(tests["inputs"])
            != len(tests["outputs"])
        ):
            raise ValueError(
                f"Invalid tests for APPS "
                f"{problem['problem_id']}"
            )

        problem["input_output"] = tests

    return problems


# ==========================================
# FEEDBACK
# ==========================================

def get_feedback(result):
    errors = []
    test_details = []

    for test in result["tests"]:
        if test["passed"]:
            continue

        if test["status"] != "ok":
            errors.append(
                f"Test {test['test']}: "
                f"{test['status']}\n"
                f"{test['stderr']}"
            )

        test_details.append(
            f"Test {test['test']}\n"
            f"Expected: {test['expected']}\n"
            f"Actual: {test['actual']}\n"
            f"Status: {test['status']}\n"
            f"Error: {test['stderr']}"
        )

    return (
        "\n".join(errors),
        "\n\n".join(test_details),
    )


# ==========================================
# FILE HELPERS
# ==========================================

def read_csv(path):
    if not path.exists():
        return []

    with path.open(
        newline="",
        encoding="utf-8",
    ) as file:
        return list(csv.DictReader(file))


def append_csv(path, fields, row):
    new_file = not path.exists()

    with path.open(
        "a",
        newline="",
        encoding="utf-8",
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=fields,
        )

        if new_file:
            writer.writeheader()

        writer.writerow(row)
        file.flush()
        os.fsync(file.fileno())


def save_json_atomic(path, data):
    temp_path = path.with_suffix(".tmp")

    with temp_path.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            data,
            file,
            ensure_ascii=False,
            indent=2,
        )
        file.flush()
        os.fsync(file.fileno())

    os.replace(temp_path, path)


def load_checkpoint(path):
    if not path.exists():
        return {
            "problems": {},
            "completed": [],
        }

    with path.open(encoding="utf-8") as file:
        return json.load(file)


# ==========================================
# RECONSTRUCT EVALUATION
# ==========================================

def restore_evaluation(record):
    tests = json.loads(
        record["test_results"]
    )

    return {
        "passed": (
            str(record["passed"]).lower()
            == "true"
        ),
        "passed_tests": int(
            record["passed_tests"]
        ),
        "total_tests": int(
            record["total_tests"]
        ),
        "tests": tests,
    }


# ==========================================
# RUN EXPERIMENT
# ==========================================

def run_experiment(mode):
    check_docker()

    problems = load_problems()

    if mode == "pilot":
        problems = [
            problem
            for problem in problems
            if int(problem["problem_id"]) == 3000
        ]

    else:
        expected_ids = set(
            range(3000, 3020)
        )

        actual_ids = {
            int(problem["problem_id"])
            for problem in problems
        }

        if actual_ids != expected_ids:
            raise ValueError(
                "Expected exactly APPS "
                "problems 3000-3019."
            )

        problems.sort(
            key=lambda p: int(p["problem_id"])
        )

    RESULTS_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    prefix = f"apps_{mode}_resumable"

    summary_path = (
        RESULTS_DIR / f"{prefix}_results.csv"
    )

    attempts_path = (
        RESULTS_DIR / f"{prefix}_attempts.csv"
    )

    checkpoint_path = (
        RESULTS_DIR / f"{prefix}_checkpoint.json"
    )

    checkpoint = load_checkpoint(
        checkpoint_path
    )

    existing_summary = read_csv(
        summary_path
    )

    existing_attempts = read_csv(
        attempts_path
    )

    completed = {
        (
            str(row["problem_id"]),
            row["strategy"],
        )
        for row in existing_summary
    }

    print("=" * 55)
    print("APPS RESUMABLE EXPERIMENT")
    print("=" * 55)
    print("Mode:", mode)
    print("Problems:", len(problems))
    print("Completed strategies:", len(completed))
    print("Summary:", summary_path)
    print("Attempts:", attempts_path)
    print("Checkpoint:", checkpoint_path)
    print("=" * 55)

    for number, problem in enumerate(
        problems,
        start=1,
    ):
        pid = str(problem["problem_id"])
        question = problem["question"]

        print(
            f"\nProblem {number}/{len(problems)} "
            f"(APPS {pid})",
            flush=True,
        )

        if all(
            (pid, strategy) in completed
            for strategy in STRATEGIES
        ):
            print(
                "All strategies completed. Skipping."
            )
            continue

        # Save and reuse the common initial code.
        problem_state = checkpoint[
            "problems"
        ].get(pid)

        if problem_state is None:
            print(
                "Generating initial solution...",
                flush=True,
            )

            initial_code = generate_apps_code(
                question
            )

            initial_result = evaluate(
                problem,
                initial_code,
            )

            check_evaluation(initial_result)

            problem_state = {
                "initial_code": initial_code,
                "initial_result": initial_result,
            }

            checkpoint[
                "problems"
            ][pid] = problem_state

            save_json_atomic(
                checkpoint_path,
                checkpoint,
            )

        initial_code = problem_state[
            "initial_code"
        ]

        initial_result = problem_state[
            "initial_result"
        ]

        # Process each strategy.
        for strategy in STRATEGIES:
            key = (pid, strategy)

            if key in completed:
                print(
                    f"{strategy}: already completed"
                )
                continue

            print(
                f"\nStrategy: {strategy}",
                flush=True,
            )

            start = time.perf_counter()

            # Find previously saved attempts.
            previous = [
                row
                for row in existing_attempts
                if (
                    str(row["problem_id"]) == pid
                    and row["strategy"] == strategy
                )
            ]

            if previous:
                previous.sort(
                    key=lambda row: int(
                        row["attempt"]
                    )
                )

                last = previous[-1]

                code = last["code"]
                result = restore_evaluation(
                    last
                )

                attempts = int(
                    last["attempt"]
                )

                print(
                    f"Resuming from attempt "
                    f"{attempts}",
                    flush=True,
                )

            else:
                code = initial_code
                result = initial_result
                attempts = 1

                append_csv(
                    attempts_path,
                    ATTEMPT_FIELDS,
                    {
                        "problem_id": pid,
                        "strategy": strategy,
                        "attempt": attempts,
                        "passed": result["passed"],
                        "passed_tests": result[
                            "passed_tests"
                        ],
                        "total_tests": result[
                            "total_tests"
                        ],
                        "code": code,
                        "test_results": json.dumps(
                            result["tests"],
                            ensure_ascii=False,
                        ),
                    },
                )

            # Correct code until solved or
            # maximum attempts reached.
            while (
                not result["passed"]
                and attempts < MAX_ATTEMPTS
            ):
                error, test_feedback = (
                    get_feedback(result)
                )

                print(
                    f"Attempt {attempts + 1}/"
                    f"{MAX_ATTEMPTS}",
                    flush=True,
                )

                code = correct_apps_code(
                    problem=question,
                    previous_code=code,
                    feedback_strategy=strategy,
                    error=error,
                    test_feedback=test_feedback,
                )

                result = evaluate(
                    problem,
                    code,
                )

                check_evaluation(result)

                attempts += 1

                append_csv(
                    attempts_path,
                    ATTEMPT_FIELDS,
                    {
                        "problem_id": pid,
                        "strategy": strategy,
                        "attempt": attempts,
                        "passed": result["passed"],
                        "passed_tests": result[
                            "passed_tests"
                        ],
                        "total_tests": result[
                            "total_tests"
                        ],
                        "code": code,
                        "test_results": json.dumps(
                            result["tests"],
                            ensure_ascii=False,
                        ),
                    },
                )

            elapsed = (
                time.perf_counter()
                - start
            )

            append_csv(
                summary_path,
                SUMMARY_FIELDS,
                {
                    "problem_id": pid,
                    "strategy": strategy,
                    "initial_pass": initial_result[
                        "passed"
                    ],
                    "final_pass": result["passed"],
                    "attempts": attempts,
                    "passed_tests": result[
                        "passed_tests"
                    ],
                    "total_tests": result[
                        "total_tests"
                    ],
                    "execution_time": round(
                        elapsed,
                        2,
                    ),
                },
            )

            completed.add(key)

            # Update cached attempt records
            # for later strategies.
            existing_attempts = read_csv(
                attempts_path
            )

            print(
                f"Result: "
                f"{result['passed_tests']}/"
                f"{result['total_tests']} "
                f"after {attempts} attempts",
                flush=True,
            )

    print("\n" + "=" * 55)
    print("EXPERIMENT COMPLETED")
    print("=" * 55)
    print("Summary:", summary_path)
    print("Attempts:", attempts_path)
    print("Checkpoint:", checkpoint_path)


# ==========================================
# COMMAND-LINE INTERFACE
# ==========================================

def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--mode",
        choices=["pilot", "full"],
        default="pilot",
    )

    args = parser.parse_args()

    run_experiment(args.mode)


if __name__ == "__main__":
    main()
