
import csv
import json
from pathlib import Path

OUTPUT = Path("results/apps_logging_test.csv")

test_record = {
    "problem_id": 3000,
    "strategy": "baseline",
    "attempt": 1,
    "passed": False,
    "passed_tests": 0,
    "total_tests": 6,
    "code": "print('test')",
    "test_results": json.dumps([
        {"test": 1, "passed": False}
    ])
}

with OUTPUT.open("w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(
        f, fieldnames=test_record.keys()
    )
    writer.writeheader()
    writer.writerow(test_record)

with OUTPUT.open(encoding="utf-8", newline="") as f:
    rows = list(csv.DictReader(f))

assert len(rows) == 1
assert rows[0]["problem_id"] == "3000"
assert rows[0]["strategy"] == "baseline"
assert rows[0]["attempt"] == "1"

print("CSV logging test PASSED")
print("Saved:", OUTPUT)
