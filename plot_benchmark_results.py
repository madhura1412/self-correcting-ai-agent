
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np


# Load the combined results
df = pd.read_csv(
    "results/benchmark_comparison.csv"
)

strategies = [
    "baseline",
    "execution",
    "unit_test",
    "reflection"
]

benchmarks = ["MBPP", "HumanEval"]

# Create one chart for each benchmark
for benchmark in benchmarks:

    data = (
        df[df["benchmark"] == benchmark]
        .set_index("strategy")
        .reindex(strategies)
    )

    x = np.arange(len(strategies))
    width = 0.35

    fig, ax = plt.subplots(figsize=(10, 6))

    bars1 = ax.bar(
        x - width / 2,
        data["pass_at_1_pct"],
        width,
        label="Pass@1"
    )

    bars2 = ax.bar(
        x + width / 2,
        data["final_success_pct"],
        width,
        label="Final success"
    )

    ax.set_title(
        f"{benchmark}: Pass@1 vs Final Success"
    )

    ax.set_ylabel("Success rate (%)")
    ax.set_xlabel("Feedback strategy")
    ax.set_xticks(x)
    ax.set_xticklabels(strategies)
    ax.set_ylim(0, 100)
    ax.legend()

    ax.bar_label(
        bars1,
        fmt="%.1f%%",
        padding=3
    )

    ax.bar_label(
        bars2,
        fmt="%.1f%%",
        padding=3
    )

    plt.tight_layout()

    output = (
        f"results/{benchmark.lower()}_"
        "pass1_vs_final_success.png"
    )

    plt.savefig(
        output,
        dpi=300,
        bbox_inches="tight"
    )

    plt.close(fig)

    print(f"Saved chart: {output}")


# ---------------------------------------------------------
# RECOVERY RATE COMPARISON
# ---------------------------------------------------------

for benchmark in benchmarks:

    data = (
        df[df["benchmark"] == benchmark]
        .set_index("strategy")
        .reindex(strategies)
    )

    fig, ax = plt.subplots(figsize=(9, 6))

    bars = ax.bar(
        strategies,
        data["recovery_rate_pct"]
    )

    ax.set_title(
        f"{benchmark}: Recovery Rate by Feedback Strategy"
    )

    ax.set_xlabel("Feedback strategy")
    ax.set_ylabel("Recovery rate (%)")
    ax.set_ylim(0, 100)

    ax.bar_label(
        bars,
        fmt="%.1f%%",
        padding=3
    )

    plt.tight_layout()

    output = (
        f"results/{benchmark.lower()}_"
        "recovery_rate.png"
    )

    plt.savefig(
        output,
        dpi=300,
        bbox_inches="tight"
    )

    plt.close(fig)

    print(f"Saved chart: {output}")


# ---------------------------------------------------------
# EXECUTION TIME AND AVERAGE ATTEMPTS
# ---------------------------------------------------------

for benchmark in benchmarks:

    data = (
        df[df["benchmark"] == benchmark]
        .set_index("strategy")
        .reindex(strategies)
    )

    # Total recorded execution time
    fig, ax = plt.subplots(figsize=(9, 6))

    bars = ax.bar(
        strategies,
        data["total_execution_time_sec"]
    )

    ax.set_title(
        f"{benchmark}: Total Recorded Execution Time"
    )
    ax.set_xlabel("Feedback strategy")
    ax.set_ylabel("Execution time (seconds)")

    ax.bar_label(
        bars,
        fmt="%.1f",
        padding=3
    )

    plt.tight_layout()

    output = (
        f"results/{benchmark.lower()}_"
        "execution_time.png"
    )

    plt.savefig(output, dpi=300, bbox_inches="tight")
    plt.close(fig)

    print(f"Saved chart: {output}")

    # Average attempts
    fig, ax = plt.subplots(figsize=(9, 6))

    bars = ax.bar(
        strategies,
        data["average_attempts"]
    )

    ax.set_title(
        f"{benchmark}: Average Attempts per Problem"
    )
    ax.set_xlabel("Feedback strategy")
    ax.set_ylabel("Average attempts")
    ax.set_ylim(0, 5)

    ax.bar_label(
        bars,
        fmt="%.2f",
        padding=3
    )

    plt.tight_layout()

    output = (
        f"results/{benchmark.lower()}_"
        "average_attempts.png"
    )

    plt.savefig(output, dpi=300, bbox_inches="tight")
    plt.close(fig)

    print(f"Saved chart: {output}")