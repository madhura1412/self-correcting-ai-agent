
import csv
import tempfile
from pathlib import Path
from unittest.mock import patch

import run_apps_experiment as runner


# ==========================================
# TEST INTERRUPTED EXPERIMENT RESUMPTION
# ==========================================

with tempfile.TemporaryDirectory() as folder:
    folder = Path(folder)

    # A simple simulated APPS problem.
    fake_problem = {
        "problem_id": 3000,
        "question": "Print 5",
        "input_output": {
            "inputs": [""],
            "outputs": ["5\n"],
        },
    }

    calls = []

    # Simulate initial code generation.
    def fake_generate(question):
        calls.append("generate")
        return "print(0)"

    # Simulate code correction.
    def fake_correct(**kwargs):
        strategy = kwargs["feedback_strategy"]
        calls.append(strategy)

        # Interrupt baseline during its
        # second correction request.
        if (
            strategy == "baseline"
            and calls.count("baseline") == 2
        ):
            raise KeyboardInterrupt(
                "Simulated interruption"
            )

        # Baseline remains incorrect.
        if strategy == "baseline":
            return "print(0)"

        # Other strategies correct the code.
        return "print(5)"

    # Simulate evaluation without Docker.
    def fake_evaluate(problem, code):
        passed = code == "print(5)"

        return {
            "passed": passed,
            "passed_tests": int(passed),
            "total_tests": 1,
            "tests": [
                {
                    "test": 1,
                    "passed": passed,
                    "status": "ok",
                    "expected": "5",
                    "actual": (
                        "5" if passed else "0"
                    ),
                    "stderr": "",
                }
            ],
        }

    # Replace expensive real functions
    # with fast simulated functions.
    with (
        patch.object(
            runner,
            "RESULTS_DIR",
            folder,
        ),
        patch.object(
            runner,
            "load_problems",
            return_value=[fake_problem],
        ),
        patch.object(
            runner,
            "check_docker",
        ),
        patch.object(
            runner,
            "generate_apps_code",
            side_effect=fake_generate,
        ),
        patch.object(
            runner,
            "correct_apps_code",
            side_effect=fake_correct,
        ),
        patch.object(
            runner,
            "evaluate",
            side_effect=fake_evaluate,
        ),
    ):

        # ==================================
        # FIRST RUN: SIMULATE INTERRUPTION
        # ==================================

        try:
            runner.run_experiment("pilot")
        except KeyboardInterrupt:
            print(
                "\nSimulated interruption detected."
            )

        # Verify that baseline attempts
        # 1 and 2 were saved.
        attempts_path = (
            folder
            / "apps_pilot_resumable_attempts.csv"
        )

        with attempts_path.open(
            newline="",
            encoding="utf-8",
        ) as file:
            interrupted_attempts = list(
                csv.DictReader(file)
            )

        assert len(interrupted_attempts) == 2

        assert [
            int(row["attempt"])
            for row in interrupted_attempts
        ] == [1, 2]

        print(
            "Attempts saved before interruption: 2"
        )

        # ==================================
        # SECOND RUN: RESUME EXPERIMENT
        # ==================================

        runner.run_experiment("pilot")

        # ==================================
        # THIRD RUN: CHECK NO DUPLICATES
        # ==================================

        calls_before = len(calls)

        runner.run_experiment("pilot")

        assert len(calls) == calls_before, (
            "Completed work was repeated."
        )

        # ==================================
        # VERIFY FINAL CSV RESULTS
        # ==================================

        summary_path = (
            folder
            / "apps_pilot_resumable_results.csv"
        )

        with summary_path.open(
            newline="",
            encoding="utf-8",
        ) as file:
            summary = list(
                csv.DictReader(file)
            )

        with attempts_path.open(
            newline="",
            encoding="utf-8",
        ) as file:
            attempts = list(
                csv.DictReader(file)
            )

        # Four strategies must be recorded.
        assert len(summary) == 4

        # Baseline: 5 attempts.
        # Other strategies: 2 each.
        assert len(attempts) == 11

        # Check baseline results.
        baseline = next(
            row
            for row in summary
            if row["strategy"] == "baseline"
        )

        assert baseline["final_pass"] == "False"
        assert baseline["attempts"] == "5"

        # Check other strategies.
        for strategy in [
            "execution",
            "unit_test",
            "reflection",
        ]:
            row = next(
                row
                for row in summary
                if row["strategy"] == strategy
            )

            assert row["final_pass"] == "True"
            assert row["attempts"] == "2"

        # Verify baseline attempt numbers.
        baseline_attempts = [
            int(row["attempt"])
            for row in attempts
            if row["strategy"] == "baseline"
        ]

        assert baseline_attempts == [
            1, 2, 3, 4, 5
        ]

        # Check that every attempt is unique.
        attempt_keys = [
            (
                row["problem_id"],
                row["strategy"],
                row["attempt"],
            )
            for row in attempts
        ]

        assert len(attempt_keys) == len(
            set(attempt_keys)
        ), "Duplicate attempts detected."

        # Initial code should be generated once.
        assert calls.count("generate") == 1

        # Verify the first two saved attempts
        # were not regenerated after resuming.
        assert calls.count("baseline") == 5

        # ==================================
        # TEST RESULTS
        # ==================================

        print(
            "\nInterrupted resume test PASSED"
        )

        print(
            "Summary rows:",
            len(summary),
        )

        print(
            "Attempt rows:",
            len(attempts),
        )

        print(
            "Baseline attempts:",
            baseline_attempts,
        )

        print(
            "Initial generations:",
            calls.count("generate"),
        )

        print(
            "Duplicate attempts: 0"
        )

        print(
            "Completed work repeated: 0"
        )
