
import os
import pandas as pd


# ---------------------------------------------------------
# FILE PATHS
# ---------------------------------------------------------

RESULTS_DIR = "results"

MBPP_SUMMARY = os.path.join(
    RESULTS_DIR, "mbpp_100_summary.csv"
)

HUMANEVAL_SUMMARY = os.path.join(
    RESULTS_DIR, "humaneval_summary.csv"
)

MBPP_RAW = os.path.join(
    RESULTS_DIR, "mbpp_results_100.csv"
)

HUMANEVAL_RAW = os.path.join(
    RESULTS_DIR, "humaneval_results.csv"
)

OUTPUT_FILE = os.path.join(
    RESULTS_DIR, "benchmark_comparison.csv"
)


# ---------------------------------------------------------
# NORMALISE COLUMN NAMES
# ---------------------------------------------------------

def normalise_columns(df):

    df = df.copy()

    df.columns = [
        str(column).strip().lower().replace(" ", "_")
        for column in df.columns
    ]

    return df


def find_column(df, *names):

    for name in names:

        if name in df.columns:
            return name

    return None


# ---------------------------------------------------------
# LOAD AND STANDARDISE A SUMMARY
# ---------------------------------------------------------

def load_summary(path, benchmark):

    if not os.path.exists(path):

        raise FileNotFoundError(
            f"Summary file not found: {path}"
        )

    df = normalise_columns(
        pd.read_csv(path)
    )

    required = {
        "strategy": find_column(
            df, "strategy", "feedback_strategy"
        ),
        "problems": find_column(
            df, "problems"
        ),
        "pass1": find_column(
            df, "pass@1", "pass@1_(%)", "pass_at_1_pct"
        ),
        "final": find_column(
            df, "final_success",
            "final_success_(%)", "final_success_pct"
        ),
        "initial_failures": find_column(
            df, "initial_failures"
        ),
        "recovered": find_column(
            df, "recovered"
        ),
        "recovery": find_column(
            df, "recovery_rate",
            "recovery_rate_(%)", "recovery_rate_pct"
        ),
        "attempts": find_column(
            df, "average_attempts"
        ),
    }

    missing = [
        name
        for name, column in required.items()
        if column is None
    ]

    if missing:

        raise ValueError(
            f"Missing columns in {path}: {missing}\n"
            f"Available columns: {list(df.columns)}"
        )

    output = pd.DataFrame({

        "benchmark": benchmark,

        "strategy": df[required["strategy"]],

        "problems": df[required["problems"]],

        "pass_at_1_pct": pd.to_numeric(
            df[required["pass1"]], errors="coerce"
        ),

        "final_success_pct": pd.to_numeric(
            df[required["final"]], errors="coerce"
        ),

        "initial_failures": df[
            required["initial_failures"]
        ],

        "recovered": df[required["recovered"]],

        "recovery_rate_pct": pd.to_numeric(
            df[required["recovery"]], errors="coerce"
        ),

        "average_attempts": df[required["attempts"]],
    })

    # MBPP summary stores rates as fractions.
    # Convert them to percentages.
    if benchmark == "MBPP":

        output["pass_at_1_pct"] *= 100

        output["final_success_pct"] *= 100

        output["recovery_rate_pct"] *= 100

    # HumanEval summary already stores percentages.
    return output


# ---------------------------------------------------------
# ADD EXECUTION-TIME STATISTICS
# ---------------------------------------------------------

def add_execution_times(comparison, raw_path):

    comparison = comparison.copy()

    comparison["total_execution_time_sec"] = pd.NA

    comparison["average_execution_time_sec"] = pd.NA

    if not os.path.exists(raw_path):

        print(
            f"Warning: raw results file not found: {raw_path}"
        )

        return comparison

    raw = normalise_columns(
        pd.read_csv(raw_path)
    )

    required_columns = {
        "feedback_strategy",
        "execution_time"
    }

    if not required_columns.issubset(raw.columns):

        print(
            f"Warning: timing columns missing in {raw_path}"
        )

        return comparison

    raw["execution_time"] = pd.to_numeric(
        raw["execution_time"],
        errors="coerce"
    )

    timing = (
        raw.groupby("feedback_strategy")["execution_time"]
        .agg(["sum", "mean"])
        .reset_index()
    )

    timing = timing.rename(columns={
        "feedback_strategy": "strategy",
        "sum": "total_execution_time_sec",
        "mean": "average_execution_time_sec",
    })

    comparison = comparison.drop(
        columns=[
            "total_execution_time_sec",
            "average_execution_time_sec"
        ]
    ).merge(
        timing,
        on="strategy",
        how="left"
    )

    return comparison


# ---------------------------------------------------------
# MAIN
# ---------------------------------------------------------

def main():

    os.makedirs(RESULTS_DIR, exist_ok=True)

    print("Loading MBPP summary...")

    mbpp = load_summary(
        MBPP_SUMMARY,
        "MBPP"
    )

    print("Loading HumanEval summary...")

    humaneval = load_summary(
        HUMANEVAL_SUMMARY,
        "HumanEval"
    )

    # Add timing statistics separately for each benchmark.
    mbpp = add_execution_times(
        mbpp,
        MBPP_RAW
    )

    humaneval = add_execution_times(
        humaneval,
        HUMANEVAL_RAW
    )

    # Combine both benchmarks.
    comparison = pd.concat(
        [mbpp, humaneval],
        ignore_index=True
    )

    # Consistent strategy ordering.
    strategy_order = [
        "baseline",
        "execution",
        "unit_test",
        "reflection"
    ]

    comparison["strategy"] = pd.Categorical(
        comparison["strategy"],
        categories=strategy_order,
        ordered=True
    )

    comparison = comparison.sort_values(
        ["benchmark", "strategy"]
    ).reset_index(drop=True)

    # Save final CSV.
    comparison.to_csv(
        OUTPUT_FILE,
        index=False,
        float_format="%.4f"
    )

    # Display results.
    display_columns = [
        "benchmark",
        "strategy",
        "problems",
        "pass_at_1_pct",
        "final_success_pct",
        "initial_failures",
        "recovered",
        "recovery_rate_pct",
        "average_attempts",
        "total_execution_time_sec",
        "average_execution_time_sec"
    ]

    print("\n" + "=" * 90)
    print("COMBINED BENCHMARK COMPARISON")
    print("=" * 90)

    print(
        comparison[display_columns].to_string(
            index=False
        )
    )

    print("\nSaved successfully:")
    print(OUTPUT_FILE)

    print(
        "\nNote: Execution times exclude Ollama generation "
        "time unless it was explicitly measured by the executor."
    )


if __name__ == "__main__":
    main()
