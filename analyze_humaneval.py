
import pandas as pd

FILE = "results/humaneval_results.csv"

df = pd.read_csv(FILE)

df["success"] = (
    df["success"].astype(str).str.strip().str.lower() == "true"
)
df["attempt"] = pd.to_numeric(df["attempt"])

results = []

for strategy, group in df.groupby("feedback_strategy"):

    # First attempt for each problem
    first = group[group["attempt"] == 1].drop_duplicates(
        subset=["problem_id"]
    )

    # Whether each problem passed at least once
    final = group.groupby("problem_id")["success"].any()

    # Initial failures
    initial = first.set_index("problem_id")["success"]

    initial_failures = initial[~initial]

    # Problems that failed initially but later passed
    recovered = sum(
        not initial.get(problem_id, False) and passed
        for problem_id, passed in final.items()
    )

    pass_at_1 = first["success"].mean() * 100
    final_success = final.mean() * 100

    recovery_rate = (
        recovered / len(initial_failures) * 100
        if len(initial_failures) else 0
    )

    # Number of attempts per problem, including early stopping
    attempts_per_problem = group.groupby("problem_id")[
        "attempt"
    ].max()

    results.append({
        "Strategy": strategy,
        "Problems": group["problem_id"].nunique(),
        "Pass@1 (%)": round(pass_at_1, 2),
        "Final success (%)": round(final_success, 2),
        "Initial failures": len(initial_failures),
        "Recovered": recovered,
        "Recovery rate (%)": round(recovery_rate, 2),
        "Average attempts": round(
            attempts_per_problem.mean(), 2
        )
    })

summary = pd.DataFrame(results)

print("\nHUMANEVAL STRATEGY COMPARISON")
print(summary.to_string(index=False))

summary.to_csv(
    "results/humaneval_summary.csv",
    index=False
)

print("\nSaved: results/humaneval_summary.csv")
