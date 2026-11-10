
from feedback import correct_code
from agent import validate_syntax

problem = """
Write a function called sort_third that sorts the elements
at indices divisible by three in ascending order.
All other elements must remain unchanged.
"""

previous_code = """
def sort_third(l: list):
    indices = [i for i in range(len(l)) if (i + 1) % 3 == 0]
    values = [l[i] for i in indices]
    values.sort()
    for i, value in zip(indices, values):
        l[i] = value
    return l
"""

error = ""
test_feedback = """
AssertionError: The output does not match the expected result.
Correct the indexing logic. Indices divisible by 3 are
0, 3, 6, ...; do not use (i + 1) % 3.
"""

corrected_code = correct_code(
    problem=problem,
    previous_code=previous_code,
    feedback_strategy="reflection",
    error=error,
    test_feedback=test_feedback,
)

print("\n=== CORRECTED CODE ===")
print(corrected_code)

valid, syntax_error = validate_syntax(corrected_code)

print("\n=== SYNTAX CHECK ===")
print("Valid:", valid)
print("Error:", syntax_error)

test_cases = [
    ([1, 3, 2, 6, 5, 4], [1, 3, 2, 6, 5, 4]),
    ([9, 8, 7, 6, 5, 4, 3], [3, 8, 7, 6, 5, 4, 9]),
]

print("\n=== FUNCTIONAL TESTS ===")

namespace = {}
exec(corrected_code, namespace)
sort_third = namespace["sort_third"]

for input_list, expected in test_cases:
    result = sort_third(input_list.copy())
    passed = result == expected
    print(
        f"Input: {input_list} | "
        f"Expected: {expected} | "
        f"Actual: {result} | "
        f"Passed: {passed}"
    )