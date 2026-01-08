"""Utility functions for code debugging domain."""

import os


def get_debugbench_path() -> str:
    """Get the path to DebugBench dataset directory."""
    return os.path.join(os.path.dirname(__file__), '../../DebugBench')


def get_benchmark_path() -> str:
    """Get the path to DebugBench benchmark directory."""
    return os.path.join(get_debugbench_path(), 'benchmark')


def check_leetcode_session() -> bool:
    """
    Check if LEETCODE_SESSION environment variable is set.

    Returns:
        bool: True if set, False otherwise.
    """
    return 'LEETCODE_SESSION' in os.environ
