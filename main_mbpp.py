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

RUN_ID = datetime.now().strftime("%Y%m%d_%H%M%S")


problems = load_mbpp_problems(50)


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

    print("\nGenerating initial solution...")

    enhanced_problem = f"""
    {problem}

    The benchmark tests require this exact function interface:

    {required_call}

    Your solution must define the function name and parameters
    needed for that call.

    Return only valid Python code.
    """

    initial_code = generate_code(enhanced_problem)

    print("\nINITIAL CODE:")
    print(initial_code)

    for feedback_strategy in STRATEGIES:

        print("\n")
        print("=" * 50)
        print(
            f"STRATEGY: {feedback_strategy.upper()}"
        )
        print("=" * 50)

        # Fair comparison:
        # every strategy starts with same initial code
        code = initial_code

        for attempt in range(
            1,
            MAX_ATTEMPTS + 1
        ):

            print(
                f"\n========== ATTEMPT {attempt} =========="
            )

            print("\nCODE:")
            print(code)

            result = execute_mbpp_code(
                code=code,
                test_list=test_list,
                test_imports=test_imports
            )

            error = result["error"]
            test_feedback = result["output"]

            log_attempt(
                run_id=RUN_ID,
                problem_id=problem_id,
                feedback_strategy=feedback_strategy,
                attempt=attempt,
                success=result["success"],
                execution_time=result["execution_time"],
                code=code,
                error=error,
                test_feedback=test_feedback
            )

            if result["success"]:

                print("\nSUCCESS!")
                print(test_feedback)

                break

            print("\nFAILED!")

            print("\nTEST FEEDBACK:")
            print(test_feedback)

            print("\nERROR:")
            print(error)

            if attempt < MAX_ATTEMPTS:

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

        else:

            print(
                "\nMaximum attempts reached."
            )

            print(
                "Problem was not solved."
            )


print("\n")
print("=" * 60)
print("MBPP EXPERIMENT FINISHED")
print("=" * 60)