
import csv
from load_mbpp import load_mbpp_problems

RESULTS_FILE = "results/mbpp_results_100.csv"
OUTPUT_FILE = "results/failed_problem_descriptions.csv"

# Identify problems that initially failed for baseline.
with open(RESULTS_FILE, newline="", encoding="utf-8-sig") as f:
    rows = list(csv.DictReader(f))

failed_ids = {
    row["problem_id"]
    for row in rows
    if row["feedback_strategy"] == "baseline"
    and row["attempt_type"] == "initial"
    and row["success"].lower() == "false"
}

problems = load_mbpp_problems(100)

with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(
        f,
        fieldnames=["problem_id", "prompt", "required_call", "tests"]
    )
    writer.writeheader()

    for problem in problems:
        if problem["problem_id"] in failed_ids:
            writer.writerow({
                "problem_id": problem["problem_id"],
                "prompt": problem["prompt"],
                "required_call": problem["required_call"],
                "tests": " | ".join(problem["tests"])
            })

print("Failed problems exported:", len(failed_ids))
print("Saved to:", OUTPUT_FILE)
