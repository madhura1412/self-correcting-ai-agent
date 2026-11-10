
from feedback import correct_code

problem = """
Write a function called find_max(numbers)
that returns the largest number in a list.
"""

previous_code = """
def find_max(numbers):
    return min(numbers)
"""

corrected_code = correct_code(
    problem=problem,
    previous_code=previous_code,
    feedback_strategy="no_feedback"
)

print("Original code:")
print(previous_code)

print("\nCorrected code:")
print(corrected_code)
