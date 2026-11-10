PROBLEMS = [
    {
        "problem_id": "add_numbers_001",
        "function_name": "add_numbers",
        "prompt": """
Create a Python function called add_numbers(a, b)
that returns the sum of a and b.
""",
        "test_cases": [
            {"inputs": "(2, 3)", "expected": 5},
            {"inputs": "(-1, 1)", "expected": 0},
            {"inputs": "(0, 0)", "expected": 0},
            {"inputs": "(10, 20)", "expected": 30}
        ]
    },

    {
        "problem_id": "is_even_002",
        "function_name": "is_even",
        "prompt": """
Create a Python function called is_even(n).

Return True if n is even.
Return False if n is odd.
""",
        "test_cases": [
            {"inputs": "(2,)", "expected": True},
            {"inputs": "(7,)", "expected": False},
            {"inputs": "(0,)", "expected": True},
            {"inputs": "(-4,)", "expected": True}
        ]
    },

    {
        "problem_id": "reverse_string_003",
        "function_name": "reverse_string",
        "prompt": """
Create a Python function called reverse_string(text)
that returns the supplied string in reverse order.
""",
        "test_cases": [
            {"inputs": "('hello',)", "expected": "olleh"},
            {"inputs": "('Python',)", "expected": "nohtyP"},
            {"inputs": "('',)", "expected": ""},
            {"inputs": "('a',)", "expected": "a"}
        ]
    },

    {
        "problem_id": "find_maximum_004",
        "function_name": "find_maximum",
        "prompt": """
Create a Python function called find_maximum(numbers)
that returns the largest number in a list.

If the list is empty, return None.
""",
        "test_cases": [
            {"inputs": "([1, 2, 3],)", "expected": 3},
            {"inputs": "([-5, -2, -10],)", "expected": -2},
            {"inputs": "([7],)", "expected": 7},
            {"inputs": "([],)", "expected": None}
        ]
    },

    {
        "problem_id": "count_vowels_005",
        "function_name": "count_vowels",
        "prompt": """
Create a Python function called count_vowels(text)
that returns the number of vowels in a string.

Count a, e, i, o and u.
The function should be case-insensitive.
""",
        "test_cases": [
            {"inputs": "('hello',)", "expected": 2},
            {"inputs": "('AEIOU',)", "expected": 5},
            {"inputs": "('python',)", "expected": 1},
            {"inputs": "('',)", "expected": 0}
        ]
    }
]