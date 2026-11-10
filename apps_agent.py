
import ollama

MODEL_NAME = "deepseek-coder:6.7b"

def clean_apps_code(response):
    code = response.strip()

    if "```python" in code:
        code = code.split("```python", 1)[1]
        code = code.split("```", 1)[0]
    elif "```" in code:
        code = code.split("```", 1)[1]
        code = code.split("```", 1)[0]

    return code.strip()


def generate_apps_code(problem, max_tokens=2048):
    prompt = f"""
You are an expert competitive programming assistant.

Solve the following programming problem using Python 3.

PROBLEM:
{problem}

REQUIREMENTS:
- Write a complete Python 3 program.
- Read input from standard input (stdin).
- Print the required output to standard output (stdout).
- Handle multiple test cases if required by the problem.
- Do not define a function-only solution without an entry point.
- Do not include explanations or Markdown formatting.
- Return only executable Python code.
"""

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
