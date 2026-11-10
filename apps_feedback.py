
import ollama
from apps_agent import MODEL_NAME, clean_apps_code


def correct_apps_code(
    problem,
    previous_code,
    feedback_strategy,
    error="",
    test_feedback="",
    max_tokens=2048
):
    output_rules = """
IMPORTANT RULES:
- Return only executable Python 3 code.
- Write a complete stdin/stdout program.
- Read input from standard input.
- Print answers to standard output.
- Handle multiple test cases if required.
- Do not include explanations or Markdown.
- Do not modify or hardcode benchmark test cases.
"""

    if feedback_strategy == "baseline":
        prompt = f"""
Solve this programming problem again from scratch.

Problem:
{problem}

Generate a new independent solution.

{output_rules}
"""

    elif feedback_strategy == "execution":
        prompt = f"""
Solve this programming problem:

{problem}

Previous code:
{previous_code}

Execution error:
{error if error else "No execution error was reported."}

Correct the implementation using the execution feedback.
Check the problem requirements carefully.

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

Correct the implementation using the test feedback.
Check edge cases and input/output requirements.

{output_rules}
"""

    elif feedback_strategy == "reflection":
        prompt = f"""
You are an expert competitive programming assistant.

Programming problem:
{problem}

Previous implementation:
{previous_code}

Execution error:
{error if error else "No execution error was reported."}

Test feedback:
{test_feedback}

Reflect carefully on why the previous solution failed.
Identify potential logical errors and missing edge cases.
Develop a corrected solution that follows the problem
requirements and input/output format.

Return only the complete corrected Python program.

{output_rules}
"""

    else:
        raise ValueError(
            f"Unknown feedback strategy: {feedback_strategy}"
        )

    response = ollama.chat(
        model=MODEL_NAME,
        messages=[
            {"role": "user", "content": prompt}
        ],
        options={
            "num_predict": max_tokens,
            "temperature": 0
        }
    )

    return clean_apps_code(response["message"]["content"])
