
import json
from pathlib import Path

from datasets import load_dataset

DATASET = "metr-evals/apps"
OUTPUT = Path("results/apps_competition_20.jsonl")
TARGET = 20

def main():
    print("Loading APPS test problems...")

    ds = load_dataset(
        DATASET,
        split="test",
        streaming=True
    )

    selected = []

    for row in ds:
        if str(row.get("difficulty", "")).lower() != "competition":
            continue

        raw_tests = row.get("input_output")
        if not raw_tests:
            continue

        try:
            tests = (
                json.loads(raw_tests)
                if isinstance(raw_tests, str)
                else raw_tests
            )
        except (ValueError, TypeError):
            continue

        if not isinstance(tests, dict):
            continue

        if not tests.get("inputs") or not tests.get("outputs"):
            continue

        selected.append({
            "problem_id": row["problem_id"],
            "question": row["question"],
            "difficulty": row["difficulty"],
            "input_output": tests,
            "starter_code": row.get("starter_code") or "",
            "url": row.get("url") or ""
        })

        print(f"Selected: {row['problem_id']}")

        if len(selected) == TARGET:
            break

    if len(selected) != TARGET:
        raise RuntimeError(
            f"Only found {len(selected)} suitable problems."
        )

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)

    with OUTPUT.open("w", encoding="utf-8") as file:
        for problem in selected:
            file.write(json.dumps(problem, ensure_ascii=False) + "\n")

    print(f"\nSaved {len(selected)} competition problems.")
    print(f"File: {OUTPUT}")

if __name__ == "__main__":
    main()
