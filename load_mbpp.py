from datasets import load_dataset

import re


def extract_required_call(test_list):
    """
    Extract the first function call used in MBPP tests.
    Example:
    assert find_Volume(10,8,6) == 240
    -> find_Volume(10,8,6)
    """

    if not test_list:
        return ""

    first_test = test_list[0]

    match = re.search(r"assert\s+([A-Za-z_]\w*\s*\([^)]*\))", first_test)

    if match:
        return match.group(1)

    return ""

def load_mbpp_problems(num_problems=10):

    print("Loading MBPP dataset...")

    dataset = load_dataset(
        "google-research-datasets/mbpp",
        "sanitized"
    )

    problems = []

    for item in dataset["test"].select(range(num_problems)):

        problem = {
            "problem_id": f"mbpp_{item['task_id']}",
            "task_id": item["task_id"],
            "prompt": item["prompt"],
            "tests": item["test_list"],
            "test_imports": item["test_imports"],
            "required_call": extract_required_call(item["test_list"])
        }

        problems.append(problem)

    return problems


if __name__ == "__main__":

    problems = load_mbpp_problems(10)

    print("\nLoaded problems:", len(problems))

    for problem in problems:

        print("\n" + "=" * 60)

        print("PROBLEM ID:")
        print(problem["problem_id"])

        print("\nPROMPT:")
        print(problem["prompt"])

        print("\nTESTS:")

        for test in problem["tests"]:
            print(test)