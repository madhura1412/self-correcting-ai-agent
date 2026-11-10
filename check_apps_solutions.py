
import json
from datasets import load_dataset

with open("results/apps_competition_20.jsonl", encoding="utf-8") as f:
    selected_ids = {
        int(json.loads(line)["problem_id"])
        for line in f if line.strip()
    }

dataset = load_dataset(
    "metr-evals/apps",
    split="test",
    streaming=True
)

found = 0
available = 0

for row in dataset:
    pid = int(row["problem_id"])

    if pid not in selected_ids:
        continue

    found += 1
    raw = row.get("solutions")

    try:
        solutions = json.loads(raw) if isinstance(raw, str) and raw.strip() else raw
    except (ValueError, TypeError):
        solutions = []

    count = len(solutions) if isinstance(solutions, list) else 0

    print(f"APPS {pid}: {count} reference solutions")

    if count > 0:
        available += 1

    if found == len(selected_ids):
        break

print(f"\nProblems checked: {found}")
print(f"Problems with reference solutions: {available}")
