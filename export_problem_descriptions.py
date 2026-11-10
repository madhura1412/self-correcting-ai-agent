import csv
from load_mbpp import load_mbpp_problems
from load_humaneval import load_humaneval

OUTPUT_FILE = "problem_descriptions_for_categorisation.csv"

rows = []

# Export the same first 100 MBPP test problems used in the experiment.
for item in load_mbpp_problems(100):
    rows.append({
        "dataset": "MBPP",
        "problem_id": item["problem_id"],
        "task_id": item["task_id"],
        "prompt": item["prompt"],
        "entry_point": item.get("required_call", ""),
        "tests": "\n".join(item.get("tests", [])),
    })

# Export all HumanEval test problems (normally 164).
for item in load_humaneval():
    rows.append({
        "dataset": "HumanEval",
        "problem_id": item["task_id"],
        "task_id": item["task_id"],
        "prompt": item["prompt"],
        "entry_point": item.get("entry_point", ""),
        "tests": item.get("test", ""),
    })

with open(OUTPUT_FILE, "w", newline="", encoding="utf-8-sig") as f:
    writer = csv.DictWriter(
        f,
        fieldnames=[
            "dataset",
            "problem_id",
            "task_id",
            "prompt",
            "entry_point",
            "tests",
        ],
    )
    writer.writeheader()
    writer.writerows(rows)

mbpp_count = sum(row["dataset"] == "MBPP" for row in rows)
humaneval_count = sum(row["dataset"] == "HumanEval" for row in rows)

print(f"Export complete: {OUTPUT_FILE}")
print(f"MBPP problems: {mbpp_count}")
print(f"HumanEval problems: {humaneval_count}")
print(f"Total problems: {len(rows)}")
print("No model was called and no benchmark experiment was rerun.")
