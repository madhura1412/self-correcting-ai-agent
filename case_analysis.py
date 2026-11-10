import pandas as pd

# ==========================================================
# SETTINGS
# ==========================================================

RESULTS_FILE = "results/mbpp_results.csv"
RUN_ID = "20260826_134811"

INTERESTING_PROBLEMS = [
    "mbpp_102",
    "mbpp_11",
    "mbpp_63",
    "mbpp_69",
    "mbpp_72",
    "mbpp_74",
    "mbpp_92",
    "mbpp_95"
]

# ==========================================================
# LOAD DATA
# ==========================================================

df = pd.read_csv(RESULTS_FILE)

df = df[
    df["run_id"].astype(str) == RUN_ID
].copy()

df = df[
    df["problem_id"].isin(INTERESTING_PROBLEMS)
].copy()

df = df.sort_values(
    [
        "problem_id",
        "feedback_strategy",
        "attempt"
    ]
)

# ==========================================================
# DISPLAY EACH CASE
# ==========================================================

for problem_id in INTERESTING_PROBLEMS:

    problem_df = df[
        df["problem_id"] == problem_id
    ]

    print("\n")
    print("#" * 70)
    print(f"PROBLEM: {problem_id}")
    print("#" * 70)

    for strategy in [
        "baseline",
        "execution",
        "unit_test",
        "reflection"
    ]:

        strategy_df = problem_df[
            problem_df["feedback_strategy"] == strategy
        ]

        print("\n" + "=" * 60)
        print(f"STRATEGY: {strategy.upper()}")
        print("=" * 60)

        for _, row in strategy_df.iterrows():

            print(
                f"\nATTEMPT {row['attempt']} "
                f"- SUCCESS: {row['success']}"
            )

            print("\nCODE:")
            print(row["code"])

            if not row["success"]:

                print("\nERROR:")
                print(row["error"])

                print("\nTEST FEEDBACK:")
                print(row["test_feedback"])

            print("-" * 60)


print("\nCase analysis complete.")