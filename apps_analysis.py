
from pathlib import Path
import json

import pandas as pd
import matplotlib.pyplot as plt

# -------------------------------------------------
# 1. Locate experiment files
# -------------------------------------------------
RESULTS_DIR = Path(__file__).resolve().parent / "results"
GRAPHS_DIR = RESULTS_DIR / "apps_graphs"
GRAPHS_DIR.mkdir(parents=True, exist_ok=True)

results = pd.read_csv(
    RESULTS_DIR / "apps_full_resumable_results.csv"
)
attempts = pd.read_csv(
    RESULTS_DIR / "apps_full_resumable_attempts.csv"
)

with open(
    RESULTS_DIR / "apps_full_resumable_checkpoint.json",
    "r",
    encoding="utf-8",
) as file:
    checkpoint = json.load(file)

print("Results columns:", results.columns.tolist())
print("Attempts columns:", attempts.columns.tolist())

# -------------------------------------------------
# 2. Standardize column names
# -------------------------------------------------
results.columns = results.columns.str.strip().str.lower()
attempts.columns = attempts.columns.str.strip().str.lower()

def find_column(df, candidates):
    for name in candidates:
        if name in df.columns:
            return name
    return None

strategy_col = find_column(
    results, ["strategy", "feedback_strategy"]
)
problem_col = find_column(
    results, ["problem_id", "id"]
)
passed_col = find_column(
    results, ["final_pass", "final_passed", "passed", "success"]
)
tests_col = find_column(
    results, ["final_passed_tests", "passed_tests"]
)
time_col = find_column(
    results, ["execution_time", "total_time", "elapsed_time"]
)

if not strategy_col or not problem_col or not passed_col:
    raise ValueError(
        "Could not identify required columns. "
        "Check the printed Results columns above."
    )

def save_graph(filename):
    plt.tight_layout()
    plt.savefig(GRAPHS_DIR / filename, dpi=300)
    plt.close()
    print("Saved:", filename)

# -------------------------------------------------
# 3. Graph 1: Final success rate
# -------------------------------------------------
results[passed_col] = (
    results[passed_col]
    .astype(str)
    .str.lower()
    .isin(["true", "1", "yes"])
)

success = (
    results.groupby(strategy_col)[passed_col]
    .mean()
    .mul(100)
    .sort_index()
)

plt.figure(figsize=(9, 5))
bars = plt.bar(success.index, success.values)
plt.title("APPS: Final Problem Success Rate")
plt.xlabel("Feedback Strategy")
plt.ylabel("Success Rate (%)")
plt.ylim(0, max(10, success.max() * 1.3))

for bar, value in zip(bars, success.values):
    plt.text(
        bar.get_x() + bar.get_width() / 2,
        value + 0.2,
        f"{value:.1f}%",
        ha="center",
    )

save_graph("01_success_rate.png")

# -------------------------------------------------
# 4. Graph 2: Final test cases passed
# -------------------------------------------------
if tests_col:
    test_totals = (
        results.groupby(strategy_col)[tests_col]
        .sum()
        .sort_index()
    )

    plt.figure(figsize=(9, 5))
    bars = plt.bar(test_totals.index, test_totals.values)
    plt.title("APPS: Final Test Cases Passed")
    plt.xlabel("Feedback Strategy")
    plt.ylabel("Number of Passing Test Cases")

    for bar, value in zip(bars, test_totals.values):
        plt.text(
            bar.get_x() + bar.get_width() / 2,
            value + 0.2,
            str(int(value)),
            ha="center",
        )

    save_graph("02_test_cases_passed.png")

# -------------------------------------------------
# 5. Graph 3: Initial vs final test performance
# -------------------------------------------------
initial_scores = {}

for problem_id, info in checkpoint.get("problems", {}).items():
    initial_scores[str(problem_id)] = (
        info.get("initial_result", {}).get("passed_tests", 0)
    )

if tests_col:
    comparison = results.copy()
    comparison["initial_tests"] = (
        comparison[problem_col]
        .astype(str)
        .map(initial_scores)
    )

    summary = comparison.groupby(strategy_col)[
        ["initial_tests", tests_col]
    ].sum()

    summary.plot(kind="bar", figsize=(10, 5))
    plt.title("APPS: Initial vs Final Passing Tests")
    plt.xlabel("Feedback Strategy")
    plt.ylabel("Passing Test Cases")
    plt.xticks(rotation=0)
    plt.legend(["Initial", "Final"])

    save_graph("03_initial_vs_final.png")

# -------------------------------------------------
# 6. Graph 4: Performance across attempts
# -------------------------------------------------
attempt_strategy = find_column(
    attempts, ["strategy", "feedback_strategy"]
)
attempt_number = find_column(
    attempts, ["attempt", "attempt_number"]
)
attempt_tests = find_column(
    attempts, ["passed_tests", "tests_passed"]
)

if attempt_strategy and attempt_number and attempt_tests:
    progress = (
        attempts.groupby(
            [attempt_strategy, attempt_number]
        )[attempt_tests]
        .mean()
        .unstack(0)
        .sort_index()
    )

    progress.plot(marker="o", figsize=(10, 5))
    plt.title("APPS: Mean Passing Tests by Attempt")
    plt.xlabel("Attempt Number")
    plt.ylabel("Average Passing Tests per Problem")
    plt.xticks([1, 2, 3, 4, 5])
    plt.grid(alpha=0.3)

    save_graph("04_attempt_progress.png")

# -------------------------------------------------
# 7. Graph 5: Execution time comparison
# -------------------------------------------------
if time_col:
    times = (
        results.groupby(strategy_col)[time_col]
        .sum()
        .sort_index()
    )

    plt.figure(figsize=(9, 5))
    plt.bar(times.index, times.values)
    plt.title("APPS: Recorded Execution Time")
    plt.xlabel("Feedback Strategy")
    plt.ylabel("Recorded Time (seconds)")

    save_graph("05_execution_time.png")

# -------------------------------------------------
# 8. Graph 6: Benchmark comparison
# -------------------------------------------------
benchmark_data = pd.DataFrame({
    "Strategy": [
        "Baseline", "Execution",
        "Unit Test", "Reflection"
    ],
    "MBPP": [75, 70, 73, 74],
    "HumanEval": [84.15, 80.49, 79.88, 81.10],
    "APPS": [5, 5, 5, 5],
})

benchmark_data.set_index("Strategy").plot(
    kind="bar",
    figsize=(11, 6),
)

plt.title("Final Success Rates Across Three Benchmarks")
plt.xlabel("Feedback Strategy")
plt.ylabel("Final Success Rate (%)")
plt.ylim(0, 100)
plt.xticks(rotation=0)
plt.legend(title="Benchmark")

save_graph("06_benchmark_comparison.png")

print("\nAPPS graph generation completed.")
print("Graph folder:", GRAPHS_DIR)
