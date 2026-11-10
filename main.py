from agent import generate_code
from executor import execute_code, create_test_feedback
from feedback import correct_code
from logger import log_attempt
from problems import PROBLEMS


MAX_ATTEMPTS = 5

STRATEGIES = [
    "baseline",
    "execution",
    "unit_test",
    "reflection"
]


for problem_data in PROBLEMS:

    problem_id = problem_data["problem_id"]
    function_name = problem_data["function_name"]
    problem = problem_data["prompt"]
    test_cases = problem_data["test_cases"]

    print("\n")
    print("#" * 60)
    print(f"PROBLEM: {problem_id}")
    print("#" * 60)

    tests = create_test_feedback(
        function_name,
        test_cases
    )

    print("\nGenerating initial solution...")

    initial_code = generate_code(problem)

    print("\nINITIAL CODE:")
    print(initial_code)

    for feedback_strategy in STRATEGIES:

        print("\n")
        print("=" * 50)
        print(f"STRATEGY: {feedback_strategy.upper()}")
        print("=" * 50)

        # Every strategy starts from the same initial code
        code = initial_code

        for attempt in range(1, MAX_ATTEMPTS + 1):

            print(
                f"\n========== ATTEMPT {attempt} =========="
            )

            print("\nCODE:")
            print(code)

            result = execute_code(
                code,
                tests
            )

            error = result["error"]
            test_feedback = result["output"]

            log_attempt(
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
                print(result["output"])

                break

            print("\nFAILED!")

            print("\nTEST FEEDBACK:")
            print(test_feedback)

            print("\nERROR:")
            print(error)

            if attempt < MAX_ATTEMPTS:

                print("\nSending feedback to AI...")

                code = correct_code(
                    problem=problem,
                    previous_code=code,
                    feedback_strategy=feedback_strategy,
                    error=error,
                    test_feedback=test_feedback
                )

        else:

            print("\nMaximum attempts reached.")
            print("Problem was not solved.")


print("\n")
print("=" * 60)
print("EXPERIMENT FINISHED")
print("=" * 60)