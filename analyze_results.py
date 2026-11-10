import pandas as pd
import matplotlib.pyplot as plt

# ==========================================================
# SETTINGS
# ==========================================================

RESULTS_FILE = "results/mbpp_results.csv"
RUN_ID = "20260826_134811"

# ==========================================================
# LOAD DATA
# ==========================================================

df = pd.read_csv(RESULTS_FILE)

# Select only the completed 50-problem experiment
df = df[df["run_id"].astype(str) == RUN_ID].copy()

print("Rows loaded:", len(df))
print("Problems:", df["problem_id"].nunique())
print("Strategies:", df["feedback_strategy"].unique())

# ==========================================================
# CALCULATE METRICS
# ==========================================================

summary = []

for strategy in [
    "baseline",
    "execution",
    "unit_test",
    "reflection"
]:

    strategy_df = df[
        df["feedback_strategy"] == strategy
    ]

    total_problems = strategy_df["problem_id"].nunique()

    # Attempt 1 results
    first_attempt = strategy_df[
        strategy_df["attempt"] == 1
    ]

    pass_at_1 = first_attempt["success"].sum()

    # Was each problem eventually solved?
    final_results = (
        strategy_df
        .groupby("problem_id")["success"]
        .max()
    )

    final_solved = final_results.sum()

    pass_at_1_rate = pass_at_1 / total_problems

    final_success_rate = final_solved / total_problems

    improvement = (
        final_success_rate - pass_at_1_rate
    )

    # Number of attempts used per problem
    attempts_per_problem = (
        strategy_df
        .groupby("problem_id")["attempt"]
        .max()
    )

    avg_attempts = attempts_per_problem.mean()

    # Recovery among initial failures
    initial_failures = total_problems - pass_at_1

    recovered = final_solved - pass_at_1

    if initial_failures > 0:
        recovery_rate = recovered / initial_failures
    else:
        recovery_rate = 0

    summary.append({
        "Strategy": strategy,
        "Pass@1": pass_at_1_rate,
        "Final Success": final_success_rate,
        "Improvement": improvement,
        "Recovered": recovered,
        "Recovery Rate": recovery_rate,
        "Average Attempts": avg_attempts
    })

summary_df = pd.DataFrame(summary)

print("\n========== RESULTS SUMMARY ==========\n")

print(summary_df.to_string(index=False))

# ==========================================================
# GRAPH 1: PASS@1 VS FINAL SUCCESS
# ==========================================================

plot_df = summary_df.set_index("Strategy")[
    ["Pass@1", "Final Success"]
]

plot_df.plot(
    kind="bar",
    figsize=(9, 6)
)

plt.title("Pass@1 vs Final Success Rate")
plt.ylabel("Success Rate")
plt.xlabel("Feedback Strategy")
plt.ylim(0, 1)
plt.xticks(rotation=0)
plt.tight_layout()

plt.savefig(
    "results/pass1_vs_final_success.png",
    dpi=300
)

plt.close()

# ==========================================================
# GRAPH 2: RECOVERY RATE
# ==========================================================

summary_df.set_index("Strategy")[
    "Recovery Rate"
].plot(
    kind="bar",
    figsize=(9, 6)
)

plt.title("Recovery Rate After Initial Failure")
plt.ylabel("Recovery Rate")
plt.xlabel("Feedback Strategy")
plt.ylim(0, 0.5)
plt.xticks(rotation=0)
plt.tight_layout()

plt.savefig(
    "results/recovery_rate.png",
    dpi=300
)

plt.close()

# ==========================================================
# GRAPH 3: AVERAGE ATTEMPTS
# ==========================================================

summary_df.set_index("Strategy")[
    "Average Attempts"
].plot(
    kind="bar",
    figsize=(9, 6)
)

plt.title("Average Attempts per Problem")
plt.ylabel("Average Attempts")
plt.xlabel("Feedback Strategy")
plt.xticks(rotation=0)
plt.tight_layout()

plt.savefig(
    "results/average_attempts.png",
    dpi=300
)

plt.close()

print("\nGraphs created successfully!")