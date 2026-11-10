import csv
import os
from agent import generate_code
from executor import execute_mbpp_code
from feedback import correct_code
from logger import log_attempt
from load_mbpp import load_mbpp_problems
from datetime import datetime


MAX_ATTEMPTS = 5

STRATEGIES = [
    "baseline",
    "execution",
    "unit_test",
    "reflection"
]

RESULTS_FILE = "results/mbpp_results_100.csv"

# This is the run that was interrupted
RESUME_RUN_ID = "20261001_183513"


# ---------------------------------------------------------
# LOAD PREVIOUS RESULTS
# ---------------------------------------------------------

previous_results = []

if os.path.exists(RESULTS_FILE):

    with open(
        RESULTS_FILE,
        "r",
        newline="",
        encoding="utf-8"
    ) as file:

        reader = csv.DictReader(file)

        for row in reader:

            if row["run_id"] == RESUME_RUN_ID:
                previous_results.append(row)


print("\n")
print("=" * 60)
print("RESUMING MBPP 100-PROBLEM EXPERIMENT")
print("=" * 60)

print(
    f"\nPrevious rows found for run {RESUME_RUN_ID}: "
    f"{len(previous_results)}"
)


# ---------------------------------------------------------
# HELPER FUNCTIONS
# ---------------------------------------------------------

def get_strategy_rows(problem_id, strategy):

    return [
        row
        for row in previous_results
        if row["problem_id"] == problem_id
        and row["feedback_strategy"] == strategy
    ]


def get_last_row(problem_id, strategy):

    rows = get_strategy_rows(
        problem_id,
        strategy
    )

    if not rows:
        return None

    return rows[-1]


def strategy_completed(problem_id, strategy):

    last_row = get_last_row(
        problem_id,
        strategy
    )

    if last_row is None:
        return False

    if last_row["success"] == "True":
        return True

    if int(last_row["attempt"]) >= MAX_ATTEMPTS:
        return True

    return False


def get_initial_code(problem_id):

    rows = [
        row
        for row in previous_results
        if row["problem_id"] == problem_id
    ]

    if not rows:
        return None

    # The baseline attempt 1 contains the original
    # initial solution shared by all strategies.
    for row in rows:

        if (
            row["feedback_strategy"] == "baseline"
            and row["attempt"] == "1"
        ):
            return row["code"]

    return None


# ---------------------------------------------------------
# LOAD MBPP
# ---------------------------------------------------------

problems = load_mbpp_problems(100)


# ---------------------------------------------------------
# RUN / RESUME EXPERIMENT
# ---------------------------------------------------------

for problem_data in problems:

    problem_id = problem_data["problem_id"]
    problem = problem_data["prompt"]
    required_call = problem_data["required_call"]
    test_list = problem_data["tests"]
    test_imports = problem_data["test_imports"]

    print("\n")
    print("#" * 60)
    print(f"MBPP PROBLEM: {problem_id}")
    print("#" * 60)

    print("\nPROMPT:")
    print(problem)

    enhanced_problem = f"""
    {problem}

    The benchmark tests require this exact function interface:

    {required_call}

    Your solution must define the function name and parameters
    needed for that call.

    Return only valid Python code.
    """


    # -----------------------------------------------------
    # GET OR GENERATE INITIAL CODE
    # -----------------------------------------------------

    initial_code = get_initial_code(problem_id)

    if initial_code is not None:

        print("\nUsing previously saved initial solution.")

    else:

        print("\nGenerating initial solution...")

        initial_code = generate_code(
            enhanced_problem
        )

        print("\nINITIAL CODE:")
        print(initial_code)


    # -----------------------------------------------------
    # EACH FEEDBACK STRATEGY
    # -----------------------------------------------------

    for feedback_strategy in STRATEGIES:

        print("\n")
        print("=" * 50)
        print(
            f"STRATEGY: {feedback_strategy.upper()}"
        )
        print("=" * 50)


        # -------------------------------------------------
        # CHECK WHETHER THIS STRATEGY IS ALREADY COMPLETE
        # -------------------------------------------------

        if strategy_completed(
            problem_id,
            feedback_strategy
        ):

            last_row = get_last_row(
                problem_id,
                feedback_strategy
            )

            print(
                f"\n{feedback_strategy} already completed."
            )

            print(
                f"Last attempt: {last_row['attempt']}"
            )

            print(
                f"Success: {last_row['success']}"
            )

            print("Skipping...")

            continue


        # -------------------------------------------------
        # CHECK PREVIOUS ATTEMPTS
        # -------------------------------------------------

        last_row = get_last_row(
            problem_id,
            feedback_strategy
        )


        if last_row is None:

            # Strategy has never started.
            # Use the common initial solution.

            code = initial_code

            attempt = 1

            print(
                "\nStarting strategy from initial solution."
            )

        else:

            # Strategy was interrupted.
            # Continue from its last saved attempt.

            code = last_row["code"]

            previous_attempt = int(
                last_row["attempt"]
            )

            attempt = previous_attempt + 1

            print(
                f"\nResuming from attempt {attempt}."
            )


        # -------------------------------------------------
        # ATTEMPTS
        # -------------------------------------------------

        while attempt <= MAX_ATTEMPTS:

            print(
                f"\n========== ATTEMPT {attempt} =========="
            )

            print("\nCODE:")
            print(code)


            # -------------------------------------------------
            # EXECUTE
            # -------------------------------------------------

            result = execute_mbpp_code(
                code=code,
                test_list=test_list,
                test_imports=test_imports
            )

            error = result["error"]
            test_feedback = result["output"]


            # -------------------------------------------------
            # LOG
            # -------------------------------------------------

            log_attempt(
                run_id=RESUME_RUN_ID,
                problem_id=problem_id,
                feedback_strategy=feedback_strategy,
                attempt=attempt,
                success=result["success"],
                execution_time=result["execution_time"],
                code=code,
                error=error,
                test_feedback=test_feedback,
                results_file=RESULTS_FILE
            )


            # -------------------------------------------------
            # SUCCESS
            # -------------------------------------------------

            if result["success"]:

                print("\nSUCCESS!")
                print(test_feedback)

                break


            # -------------------------------------------------
            # FAILURE
            # -------------------------------------------------

            print("\nFAILED!")

            print("\nTEST FEEDBACK:")
            print(test_feedback)

            print("\nERROR:")
            print(error)


            # -------------------------------------------------
            # MAX ATTEMPTS
            # -------------------------------------------------

            if attempt >= MAX_ATTEMPTS:

                print(
                    "\nMaximum attempts reached."
                )

                print(
                    "Problem was not solved."
                )

                break


            # -------------------------------------------------
            # CORRECTION
            # -------------------------------------------------

            print(
                "\nSending feedback to AI..."
            )

            code = correct_code(
                problem=enhanced_problem,
                previous_code=code,
                feedback_strategy=feedback_strategy,
                error=error,
                test_feedback=test_feedback
            )

            attempt += 1


print("\n")
print("=" * 60)
print("MBPP 100-PROBLEM EXPERIMENT FINISHED")
print("=" * 60)