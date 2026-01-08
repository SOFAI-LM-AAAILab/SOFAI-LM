"""
Solution parser for graph coloring domain.

This module extracts color assignments from LLM responses.
"""

import re


def parse_solution(response: str) -> dict:
    """
    Parse the LLM response to extract coloring assignments.

    Args:
        response: The string response from the LLM, potentially including
            irrelevant text alongside vertex-color pairs.

    Returns:
        dict: A dictionary with vertices as keys and their assigned colors as values.
            Example: {'a': 1, 'b': 2, 'c': 1}
    """
    coloring_assignment = {}
    lines = response.strip().split('\n')
    # Regex to capture vertex-color pair in format (vertex color)
    pattern = re.compile(r"\((\w+)\s+(\d+)\)")

    for line in lines:
        line = line.strip()
        match = pattern.match(line)
        if match:
            vertex, color = match.groups()
            coloring_assignment[vertex] = int(color)

    return coloring_assignment
