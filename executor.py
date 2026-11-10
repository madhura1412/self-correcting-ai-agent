import subprocess
import tempfile
import os
import sys
import time


def execute_code(code, tests, timeout=5):
    """
    Execute generated Python code with test cases.

    Returns:
        success
        output
        error
        execution_time
    """

    full_code = code + "\n\n" + tests

    temp_path = None
    start_time = time.time()

    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".py",
            delete=False,
            encoding="utf-8"
        ) as temp_file:

            temp_file.write(full_code)
            temp_path = temp_file.name

        result = subprocess.run(
            [sys.executable, temp_path],
            capture_output=True,
            text=True,
            timeout=timeout
        )

        execution_time = time.time() - start_time

        return {
            "success": result.returncode == 0,
            "output": result.stdout,
            "error": result.stderr,
            "execution_time": execution_time
        }

    except subprocess.TimeoutExpired:

        execution_time = time.time() - start_time

        return {
            "success": False,
            "output": "",
            "error": "Execution timed out.",
            "execution_time": execution_time
        }

    except Exception as e:

        execution_time = time.time() - start_time

        return {
            "success": False,
            "output": "",
            "error": str(e),
            "execution_time": execution_time
        }

    finally:
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)


def create_test_feedback(function_name, test_cases):
    """
    Create Python test code that prints detailed
    information when a test fails.
    """

    test_code = []

    for i, test in enumerate(test_cases, start=1):

        inputs = test["inputs"]
        expected = test["expected"]

        test_code.append(
            f"""
try:
    actual = {function_name}{inputs}

    if actual == {repr(expected)}:
        print("TEST {i}: PASS")

    else:
        print("TEST {i}: FAIL")
        print("INPUT: {inputs}")
        print("EXPECTED: {repr(expected)}")
        print("ACTUAL:", actual)
        raise AssertionError("Unit test failed")

except Exception as e:
    print("TEST {i}: ERROR")
    print("INPUT: {inputs}")
    print("EXPECTED: {repr(expected)}")
    print("ERROR:", type(e).__name__, str(e))
    raise
"""
        )

    test_code.append(
        """
print("All tests passed!")
"""
    )

    return "\n".join(test_code)

def create_mbpp_tests(test_list):
    """
    Convert MBPP assertion tests into executable tests
    with useful feedback.
    """

    test_code = []

    for i, test in enumerate(test_list, start=1):

        safe_test = repr(test)

        test_code.append(
            f"""
try:
    {test}
    print("TEST {i}: PASS")

except AssertionError as e:
    print("TEST {i}: FAIL")
    print("FAILED TEST:", {safe_test})
    print("ERROR TYPE: AssertionError")
    print("ERROR MESSAGE:", str(e))
    raise

except Exception as e:
    print("TEST {i}: ERROR")
    print("FAILED TEST:", {safe_test})
    print("ERROR TYPE:", type(e).__name__)
    print("ERROR MESSAGE:", str(e))
    raise
"""
        )

    test_code.append(
        """
print("All MBPP tests passed!")
"""
    )

    return "\n".join(test_code)


def execute_mbpp_code(
    code,
    test_list,
    test_imports=None,
    timeout=5
):
    """
    Execute generated code against original MBPP tests.
    """

    if test_imports is None:
        test_imports = []

    imports = "\n".join(test_imports)

    tests = create_mbpp_tests(test_list)

    full_program = (
        imports
        + "\n\n"
        + code
        + "\n\n"
        + tests
    )

    return execute_code(
        full_program,
        "",
        timeout=timeout
    )

if __name__ == "__main__":

    sample_code = """
def divide_numbers(a, b):
    return a / b if b != 0 else 0
"""

    test_cases = [
        {
            "inputs": "(10, 2)",
            "expected": 5
        },
        {
            "inputs": "(9, 3)",
            "expected": 3
        },
        {
            "inputs": "(5, 0)",
            "expected": 0
        },
        {
            "inputs": "(-10, 2)",
            "expected": -5
        }
    ]

    tests = create_test_feedback(
        "divide_numbers",
        test_cases
    )

    result = execute_code(
        sample_code,
        tests
    )

    print("SUCCESS:", result["success"])

    print("\nOUTPUT:")
    print(result["output"])

    if result["error"]:
        print("\nERROR:")
        print(result["error"])

    print(
        "\nEXECUTION TIME:",
        round(result["execution_time"], 4),
        "seconds"
    )