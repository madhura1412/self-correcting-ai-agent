import pandas as pd
import matplotlib.pyplot as plt

# ==========================================================
# SETTINGS
# ==========================================================

RESULTS_FILE = "results/mbpp_results_100.csv"
RUN_ID = "20261001_183513"

STRATEGIES = [
    "baseline",
    "execution",
    "unit_test",
    "reflection"
]

# ==========================================================
# LOAD DATA
# ==========================================================

df = pd.read_csv(RESULTS_FILE)

df = df[
    df["run_id"].astype(str) == RUN_ID
].copy()

print("Rows loaded:", len(df))
print("Problems:", df["problem_id"].nunique())
print(
    "Strategies:",
    df["feedback_strategy"].unique()
)

# ==========================================================
# CHECK DATA COMPLETENESS
# ==========================================================

print("\n========== DATA COMPLETENESS ==========\n")

for strategy in STRATEGIES:

    strategy_df = df[
        df["feedback_strategy"] == strategy
    ]

    problems = strategy_df[
        "problem_id"
    ].nunique()

    print(
        f"{strategy}: "
        f"{problems} problems"
    )

# ==========================================================
# CALCULATE METRICS
# ==========================================================

summary = []

for strategy in STRATEGIES:

    strategy_df = df[
        df["feedback_strategy"] == strategy
    ]

    total_problems = (
        strategy_df["problem_id"]
        .nunique()
    )

    # ------------------------------------------------------
    # PASS@1
    # ------------------------------------------------------

    first_attempt = strategy_df[
        strategy_df["attempt"] == 1
    ]

    pass_at_1 = (
        first_attempt
        .groupby("problem_id")["success"]
        .max()
        .sum()
    )

    pass_at_1_rate = (
        pass_at_1 / total_problems
    )

    # ------------------------------------------------------
    # FINAL SUCCESS
    # ------------------------------------------------------

    final_results = (
        strategy_df
        .groupby("problem_id")["success"]
        .max()
    )

    final_solved = final_results.sum()

    final_success_rate = (
        final_solved / total_problems
    )

    # ------------------------------------------------------
    # IMPROVEMENT
    # ------------------------------------------------------

    improvement = (
        final_success_rate
        - pass_at_1_rate
    )

    # ------------------------------------------------------
    # RECOVERY
    # ------------------------------------------------------

    initial_failures = (
        total_problems - pass_at_1
    )

    recovered = (
        final_solved - pass_at_1
    )

    if initial_failures > 0:

        recovery_rate = (
            recovered / initial_failures
        )

    else:

        recovery_rate = 0

    # ------------------------------------------------------
    # ATTEMPTS
    # ------------------------------------------------------

    attempts_per_problem = (
        strategy_df
        .groupby("problem_id")["attempt"]
        .max()
    )

    avg_attempts = (
        attempts_per_problem.mean()
    )

    # ------------------------------------------------------
    # EXECUTION TIME
    # ------------------------------------------------------

    total_execution_time = (
        strategy_df["execution_time"]
        .sum()
    )

    average_execution_time = (
        strategy_df["execution_time"]
        .mean()
    )

    # ------------------------------------------------------
    # UNSOLVED
    # ------------------------------------------------------

    unsolved = (
        total_problems - final_solved
    )

    # ------------------------------------------------------
    # SAVE SUMMARY
    # ------------------------------------------------------

    summary.append({

        "Strategy": strategy,

        "Problems": total_problems,

        "Pass@1": pass_at_1_rate,

        "Final Success": final_success_rate,

        "Improvement": improvement,

        "Initial Failures": initial_failures,

        "Recovered": recovered,

        "Recovery Rate": recovery_rate,

        "Unsolved": unsolved,

        "Average Attempts": avg_attempts,

        "Total Execution Time":
            total_execution_time,

        "Average Execution Time":
            average_execution_time
    })


summary_df = pd.DataFrame(summary)

# ==========================================================
# DISPLAY RESULTS
# ==========================================================

print(
    "\n========== 100-PROBLEM RESULTS ==========\n"
)

print(
    summary_df.to_string(
        index=False
    )
)

# ==========================================================
# SAVE RESULTS TABLE
# ==========================================================

summary_df.to_csv(
    "results/mbpp_100_summary.csv",
    index=False
)

print(
    "\nSummary saved to:"
)

print(
    "results/mbpp_100_summary.csv"
)

# ==========================================================
# GRAPH 1: PASS@1 VS FINAL SUCCESS
# ==========================================================

plot_df = summary_df.set_index(
    "Strategy"
)[
    ["Pass@1", "Final Success"]
]

plot_df.plot(
    kind="bar",
    figsize=(9, 6)
)

plt.title(
    "Pass@1 vs Final Success Rate - MBPP 100"
)

plt.ylabel("Success Rate")
plt.xlabel("Feedback Strategy")

plt.ylim(0, 1)

plt.xticks(rotation=0)

plt.tight_layout()

plt.savefig(
    "results/pass1_vs_final_success_100.png",
    dpi=300
)

plt.close()

# ==========================================================
# GRAPH 2: RECOVERY RATE
# ==========================================================

summary_df.set_index(
    "Strategy"
)["Recovery Rate"].plot(
    kind="bar",
    figsize=(9, 6)
)

plt.title(
    "Recovery Rate After Initial Failure - MBPP 100"
)

plt.ylabel("Recovery Rate")
plt.xlabel("Feedback Strategy")

plt.ylim(0, 1)

plt.xticks(rotation=0)

plt.tight_layout()

plt.savefig(
    "results/recovery_rate_100.png",
    dpi=300
)

plt.close()

# ==========================================================
# GRAPH 3: AVERAGE ATTEMPTS
# ==========================================================

summary_df.set_index(
    "Strategy"
)["Average Attempts"].plot(
    kind="bar",
    figsize=(9, 6)
)

plt.title(
    "Average Attempts per Problem - MBPP 100"
)

plt.ylabel("Average Attempts")
plt.xlabel("Feedback Strategy")

plt.xticks(rotation=0)

plt.tight_layout()

plt.savefig(
    "results/average_attempts_100.png",
    dpi=300
)

plt.close()

# ==========================================================
# GRAPH 4: EXECUTION TIME
# ==========================================================

summary_df.set_index(
    "Strategy"
)["Total Execution Time"].plot(
    kind="bar",
    figsize=(9, 6)
)

plt.title(
    "Total Execution Time - MBPP 100"
)

plt.ylabel("Execution Time (seconds)")
plt.xlabel("Feedback Strategy")

plt.xticks(rotation=0)

plt.tight_layout()

plt.savefig(
    "results/execution_time_100.png",
    dpi=300
)

plt.close()

print(
    "\nGraphs created successfully!"
)