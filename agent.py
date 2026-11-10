
import ollama
import os

MODEL_NAME = "deepseek-coder:6.7b"
DEBUG_OUTPUT = True


# ---------------------------------------------------------
# VALIDATE GENERATED PYTHON SYNTAX
# ---------------------------------------------------------

def validate_syntax(code):
    """Check Python syntax without executing the generated code."""
    try:
        compile(code, "<generated_code>", "exec")
        return True, ""
    except SyntaxError as exc:
        return False, f"Line {exc.lineno}: {exc.msg}"


# ---------------------------------------------------------
# CLEAN MODEL OUTPUT
# ---------------------------------------------------------

def clean_code(code):
    """Extract Python code from an LLM response."""

    code = code.strip()

    # Extract code from a Markdown Python block
    if "```python" in code:
        start = code.find("```python") + len("```python")
        end = code.find("```", start)

        if end != -1:
            code = code[start:end]

    # Extract code from another Markdown block
    elif "```" in code:
        start = code.find("```") + len("```")
        end = code.find("```", start)

        if end != -1:
            code = code[start:end]

    code = code.strip()

    # Remove explanation before the actual Python code
    lines = code.splitlines()
    code_start = None

    for i, line in enumerate(lines):
        stripped = line.strip()

        if (
            stripped.startswith("def ")
            or stripped.startswith("import ")
            or stripped.startswith("from ")
            or stripped.startswith("class ")
            or stripped.startswith("@")
        ):
            code_start = i
            break

    if code_start is not None:
        lines = lines[code_start:]

    code = "\n".join(lines).strip()

    return code


# ---------------------------------------------------------
# GENERATE CODE USING OLLAMA
# ---------------------------------------------------------

def generate_code(problem):

    prompt = f"""
You are a Python programming assistant.

Solve the following programming problem:

{problem}

STRICT REQUIREMENTS:
- Return ONLY valid Python code.
- Do not include explanations.
- Do not include introductory text.
- Do not use Markdown code blocks.
- Do not include benchmark tests unless explicitly requested.
- Return the complete Python implementation only.
"""

    response = ollama.chat(
        model=MODEL_NAME,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        options={
            "num_predict": 512
        }
    )

    if DEBUG_OUTPUT:
        print("\n=== PROMPT SENT TO MODEL ===")
        print(prompt)

    # Preserve the original model response
    raw_code = response["message"]["content"]

    # Apply the existing cleaning function
    cleaned_code = clean_code(raw_code)

    # Check syntax of the cleaned code
    syntax_valid, syntax_error = validate_syntax(cleaned_code)

    # Save diagnostic information
    if DEBUG_OUTPUT:
        os.makedirs("results/diagnostics", exist_ok=True)

        diagnostic_path = os.path.join(
            "results",
            "diagnostics",
            "latest_diagnostic.txt"
        )

        with open(
            diagnostic_path,
            "w",
            encoding="utf-8"
        ) as file:

            file.write("=== RAW OLLAMA RESPONSE ===\n")
            file.write(raw_code)

            file.write("\n\n=== CLEANED CODE ===\n")
            file.write(cleaned_code)

            file.write("\n\n=== SYNTAX VALIDATION ===\n")
            file.write(f"Valid: {syntax_valid}\n")
            file.write(f"Error: {syntax_error}\n")

        print(f"Syntax valid: {syntax_valid}")

        if not syntax_valid:
            print(f"Syntax error: {syntax_error}")

        print(f"Diagnostic saved to: {diagnostic_path}")

    return cleaned_code


# ---------------------------------------------------------
# SIMPLE STANDALONE TEST
# ---------------------------------------------------------

if __name__ == "__main__":

    problem = """
Create a function called add_numbers(a, b)
that returns the sum of a and b.
"""

    generated_code = generate_code(problem)

    print("\nGENERATED CODE:")
    print("----------------")
    print(generated_code)

    syntax_valid, syntax_error = validate_syntax(generated_code)

    print("\nFINAL SYNTAX CHECK:")
    print("-------------------")
    print(f"Valid: {syntax_valid}")

    if not syntax_valid:
        print(f"Error: {syntax_error}")
