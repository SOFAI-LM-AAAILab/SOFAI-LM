import json
import os
import random
from typing import Optional


# All bug types available in DebugBench Python3
BUG_TYPES = [
    "condition error", "double", "faulty indexing", "illegal comment",
    "illegal indentation", "illegal keywords", "missing colons",
    "misused == or =", "operation error", "other error", "quadruple",
    "triple", "unclosed parentheses", "unclosed string",
    "undefined methods", "undefined objects", "variable error"
]

# Path to DebugBench dataset
DEBUGBENCH_PATH = os.path.join(os.path.dirname(__file__), "data")


def load_problem_from_dataset(
    language: str = "Python3",
    bug_type: Optional[str] = None,
    problem_index: Optional[int] = None
):
    """
    Load a problem from DebugBench dataset.

    Args:
        language: Programming language (default: Python3)
        bug_type: Specific bug type to load. If None, randomly selects from BUG_TYPES.
        problem_index: Specific problem index in the file. If None, randomly selects.

    Returns:
        CodeDebuggingProblem: A problem instance.

    Raises:
        FileNotFoundError: If the dataset file doesn't exist.
        ValueError: If the problem index is out of range.
    """
    # Import here to avoid circular dependency
    from domains.code_debugging.code_debugging_domain import CodeDebuggingProblem

    # Select bug type
    if bug_type is None:
        bug_type = random.choice(BUG_TYPES)
    elif bug_type not in BUG_TYPES:
        raise ValueError(f"Invalid bug_type '{bug_type}'. Must be one of {BUG_TYPES}")

    # Construct file path
    language_lower = language.lower().replace("3", "")  # python3 -> python
    filename = f"{language_lower}3_{bug_type}.json"
    filepath = os.path.join(DEBUGBENCH_PATH, filename)

    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Dataset file not found: {filepath}")

    # Load JSON data
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Select problem
    if problem_index is None:
        problem_index = random.randint(0, len(data) - 1)
    elif problem_index >= len(data):
        raise ValueError(f"Problem index {problem_index} out of range (max: {len(data) - 1})")

    problem_data = data[problem_index]

    # Create problem instance
    problem = CodeDebuggingProblem(
        slug=problem_data.get('slug', 'unknown'),
        description=problem_data.get('description', ''),
        examples=problem_data.get('examples', []),
        constraints=problem_data.get('constraints', ''),
        level=problem_data.get('level', 'medium'),
        buggy_code=problem_data.get('buggy_code', ''),
        oracle_code=problem_data.get('oracle_code', ''),
        explanations=problem_data.get('explanations', ''),
        content=problem_data.get('content', ''),
        bug_type=bug_type
    )

    return problem


def get_available_bug_types() -> list:
    """Get list of all available bug types."""
    return BUG_TYPES.copy()


def get_problem_count(language: str = "Python3", bug_type: str = "condition") -> int:
    """
    Get the number of problems for a specific bug type.

    Args:
        language: Programming language (default: Python3)
        bug_type: Bug type to count

    Returns:
        int: Number of problems in the file
    """
    language_lower = language.lower().replace("3", "")
    filename = f"{language_lower}3_{bug_type}.json"
    filepath = os.path.join(DEBUGBENCH_PATH, filename)

    if not os.path.exists(filepath):
        return 0

    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)

    return len(data)
