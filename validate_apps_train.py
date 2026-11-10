
import json
from datasets import load_dataset
from apps_evaluator import evaluate

print("Loading APPS training problems...")

dataset = load_dataset(
    "metr-evals/apps",
    split="train",
    streaming=True
)

validated = 0

for row in dataset:
    if validated >= 3:
        break

    raw_tests = row.get("input_output")
    raw_solutions = row.get("solutions")

    try:
        tests = (
            json.loads(raw_tests)
            if isinstance(raw_tests, str)
            else raw_tests
        )

        solutions = (
            json.loads(raw_solutions)
            if isinstance(raw_solutions, str)
            else raw_solutions
        )
    except (ValueError, TypeError):
        continue

    if not isinstance(tests, dict):
        continue

    if tests.get("fn_name"):
        continue

    if not isinstance(solutions, list) or not solutions:
        continue

    if not tests.get("inputs") or not tests.get("outputs"):
        continue

    problem = {
        "problem_id": row["problem_id"],
        "input_output": tests
    }

    print(f"\nChecking APPS {row['problem_id']}...")
    if int(row["problem_id"]) == 0:
        print("Input preview:", repr(tests["inputs"][0][:500]))
        print("Contains Windows line endings:", "\r\n" in tests["inputs"][0])

    best = None

    for solution in solutions[:3]:
        if not isinstance(solution, str) or not solution.strip():
            continue

        try:
            result = evaluate(problem, solution)
            if int(row["problem_id"]) == 0:
              for test in result["tests"]:
                print("Expected:", repr(test["expected"]))
                print("Actual:", repr(test["actual"]))
                print("Error:", test["stderr"])
        except (ValueError, RuntimeError) as error:
            print("Skipped:", error)
            continue

        if best is None or result["passed_tests"] > best["passed_tests"]:
            best = result

        if result["passed"]:
            break

    if best is not None:
        validated += 1
        print(
            f"RESULT: {best['passed_tests']}/"
            f"{best['total_tests']} tests passed"
        )

print(f"\nReal APPS problems evaluated: {validated}")
