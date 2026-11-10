import pandas as pd

# ==========================================================
# SETTINGS
# ==========================================================

RESULTS_FILE = "results/mbpp_results.csv"
RUN_ID = "20260826_134811"

STRATEGIES = [
    "baseline",
    "execution",
    "unit_test",
    "reflection"
]

# ==========================================================
# LOAD RESULTS
# ==========================================================

df = pd.read_csv(RESULTS_FILE)

# Keep only the completed 50-problem experiment
df = df[
    df["run_id"].astype(str) == RUN_ID
].copy()

print("\n========== FAILURE ANALYSIS ==========\n")

print("Problems:", df["problem_id"].nunique())
print("Rows:", len(df))


# ==========================================================
# DETERMINE FINAL RESULT FOR EACH PROBLEM/STRATEGY
# ==========================================================

final_status = (
    df.groupby(
        ["problem_id", "feedback_strategy"]
    )["success"]
    .max()
    .unstack(fill_value=False)
)

# Ensure consistent column order
final_status = final_status.reindex(
    columns=STRATEGIES
)

# Convert True/False to SOLVED/FAILED
display_status = final_status.replace({
    True: "SOLVED",
    False: "FAILED"
})

print("\n========== FINAL STATUS ==========\n")
print(display_status.to_string())


# ==========================================================
# COUNT SOLVED PROBLEMS
# ==========================================================

print("\n========== SOLVED COUNTS ==========\n")

for strategy in STRATEGIES:

    solved = final_status[strategy].sum()
    total = len(final_status)

    print(
        f"{strategy:12} : "
        f"{solved}/{total} "
        f"({solved / total:.1%})"
    )


# ==========================================================
# PROBLEMS WHERE STRATEGIES DISAGREE
# ==========================================================

disagreement = final_status[
    final_status.nunique(axis=1) > 1
]

print(
    "\n========== STRATEGY DISAGREEMENTS ==========\n"
)

print(
    "Number of problems where strategies "
    "produced different final outcomes:",
    len(disagreement)
)

if len(disagreement) > 0:
    print()
    print(
        display_status.loc[
            disagreement.index
        ].to_string()
    )


# ==========================================================
# BASELINE-ONLY RECOVERIES
# ==========================================================

baseline_only = final_status[
    (final_status["baseline"] == True)
    &
    (final_status["execution"] == False)
    &
    (final_status["unit_test"] == False)
    &
    (final_status["reflection"] == False)
]

print("\n========== BASELINE ONLY SOLVED ==========\n")

if len(baseline_only) == 0:
    print("None")
else:
    for problem_id in baseline_only.index:
        print(problem_id)


# ==========================================================
# EXECUTION-ONLY RECOVERIES
# ==========================================================

execution_only = final_status[
    (final_status["execution"] == True)
    &
    (final_status["baseline"] == False)
    &
    (final_status["unit_test"] == False)
    &
    (final_status["reflection"] == False)
]

print("\n========== EXECUTION ONLY SOLVED ==========\n")

if len(execution_only) == 0:
    print("None")
else:
    for problem_id in execution_only.index:
        print(problem_id)


# ==========================================================
# UNIT-TEST-ONLY RECOVERIES
# ==========================================================

unit_test_only = final_status[
    (final_status["unit_test"] == True)
    &
    (final_status["baseline"] == False)
    &
    (final_status["execution"] == False)
    &
    (final_status["reflection"] == False)
]

print("\n========== UNIT TEST ONLY SOLVED ==========\n")

if len(unit_test_only) == 0:
    print("None")
else:
    for problem_id in unit_test_only.index:
        print(problem_id)


# ==========================================================
# REFLECTION-ONLY RECOVERIES
# ==========================================================

reflection_only = final_status[
    (final_status["reflection"] == True)
    &
    (final_status["baseline"] == False)
    &
    (final_status["execution"] == False)
    &
    (final_status["unit_test"] == False)
]

print("\n========== REFLECTION ONLY SOLVED ==========\n")

if len(reflection_only) == 0:
    print("None")
else:
    for problem_id in reflection_only.index:
        print(problem_id)


# ==========================================================
# PROBLEMS FAILED BY ALL STRATEGIES
# ==========================================================

failed_all = final_status[
    (final_status == False).all(axis=1)
]

print("\n========== FAILED BY ALL STRATEGIES ==========\n")

print("Count:", len(failed_all))

if len(failed_all) == 0:
    print("None")
else:
    for problem_id in failed_all.index:
        print(problem_id)


# ==========================================================
# PROBLEMS SOLVED BY ALL STRATEGIES
# ==========================================================

solved_all = final_status[
    (final_status == True).all(axis=1)
]

print("\n========== SOLVED BY ALL STRATEGIES ==========\n")

print("Count:", len(solved_all))

print("\nFailure analysis complete.")