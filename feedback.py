
import re
from agent import generate_code


def correct_code(
    problem,
    previous_code,
    feedback_strategy,
    error="",
    test_feedback=""
):
    """
    Generate a corrected solution using one of four strategies.
    """

    output_rules = """
IMPORTANT OUTPUT RULES:
- Return ONLY valid Python code.
- Do not include explanations.
- Do not use Markdown code fences.
- Do not modify benchmark tests.
- Return the complete Python implementation.
"""

    if feedback_strategy == "baseline":
        prompt = f"""
Solve this programming problem again from scratch.

Problem:
{problem}

Generate a new solution.

{output_rules}
"""

    elif feedback_strategy == "execution":
        prompt = f"""
Solve this programming problem:

{problem}

Previous code:
{previous_code}

Execution error:
{error}

Correct the implementation using the execution error.
Keep the required function name and parameters.

{output_rules}
"""

    elif feedback_strategy == "unit_test":
        prompt = f"""
Solve this programming problem:

{problem}

Previous code:
{previous_code}

Unit test feedback:
{test_feedback}

Correct the implementation to satisfy the benchmark tests.
Keep the required function name and parameters.

{output_rules}
"""

    elif feedback_strategy == "no_feedback":
        prompt = f"""
You are an expert Python programmer.

Original programming problem:
{problem}

Previously generated Python solution:
{previous_code}

Independently review the previous solution against the original problem.
Check for logical mistakes, missing edge cases, and incorrect assumptions.
Correct the implementation if necessary; a complete rewrite is allowed.
Preserve the required function name and parameters.
Do not use execution errors, test results, or other external feedback.
Return only the complete Python implementation.

{output_rules}
"""

    elif feedback_strategy == "reflection":
        prompt = f"""
You are an expert Python programmer correcting a failed solution.

Programming problem:
{problem}

Previous implementation:
{previous_code}

Execution error:
{error}

Test feedback:
{test_feedback}



Your previous implementation may contain a logical error.

Carefully examine the actual programming problem and the supplied test feedback. Identify the specific cause of failure and correct it. Do not merely reformat or repeat the previous code.

Do not reuse problem-specific assumptions from unrelated examples.

Check the implementation against the stated requirements and relevant edge cases before returning it.
Keep the required function name and parameters.
Return only the complete Python implementation.



{output_rules}
"""

    else:
        raise ValueError(
            f"Unknown feedback strategy: {feedback_strategy}"
        )

    generated_code = generate_code(prompt)

    # Repair a function-name mismatch when an explicit required
    # function call is included in the problem description.
    match = re.search(
        r"Required function call:\s*([A-Za-z_]\w*)\s*\(",
        problem
    )

    if match:
        required_name = match.group(1)

        generated_code = re.sub(
            r"(?m)^(\s*def\s+)[A-Za-z_]\w*(\s*\()",
            lambda m: m.group(1) + required_name + m.group(2),
            generated_code,
            count=1
        )

    return generated_code
