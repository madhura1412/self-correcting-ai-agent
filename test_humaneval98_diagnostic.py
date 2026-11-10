
from feedback import correct_code
from agent import validate_syntax

problem = """
Write a function called count_upper that counts the number
of uppercase vowels in a given string.
"""

previous_code = """
def count_upper(s):
    return sum(1 for c in s if c.isupper())
"""

test_feedback = """
The implementation is incorrect because it counts all uppercase
letters rather than only uppercase vowels.
Count only A, E, I, O, U.
"""

corrected_code = correct_code(
    problem=problem,
    previous_code=previous_code,
    feedback_strategy="reflection",
    error="",
    test_feedback=test_feedback,
)

print("\n=== CORRECTED CODE ===")
print(corrected_code)

valid, syntax_error = validate_syntax(corrected_code)
print("\nSyntax valid:", valid)
if not valid:
    print("Syntax error:", syntax_error)

if valid:
    namespace = {}
    exec(corrected_code, namespace)
    count_upper = namespace["count_upper"]

    test_cases = [
        ("HELLO", 2),
        ("AEIOU", 5),
        ("Hello World", 0),
        ("AbEcIdOfU", 5),
    ]

    print("\n=== FUNCTIONAL TESTS ===")
    for text, expected in test_cases:
        try:
            actual = count_upper(text)
            print(
                f"Input: {text!r} | Expected: {expected} | "
                f"Actual: {actual} | Passed: {actual == expected}"
            )
        except Exception as exc:
            print(f"Input: {text!r} | ERROR: {exc}")
