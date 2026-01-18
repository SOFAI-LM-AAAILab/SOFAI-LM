import os
import sys
import time
from typing import Tuple, Dict

try:
    from domains.code_debugging.leetcode_tester import LeetCodeTester
except ImportError:
    print("Warning: LeetCodeTester not found. LeetCode validation will not work.")
    LeetCodeTester = None


# Global tester instance (singleton pattern)
_tester_instance = None
_last_submission_time = 0
SUBMISSION_COOLDOWN = 15  # seconds


def get_leetcode_tester() -> 'LeetCodeTester':
    """
    Get or create LeetCodeTester singleton instance.

    Returns:
        LeetCodeTester: The tester instance.

    Raises:
        EnvironmentError: If LEETCODE_SESSION is not set.
    """
    global _tester_instance

    if _tester_instance is None:
        if not os.environ.get('LEETCODE_SESSION'):
            raise EnvironmentError(
                "LEETCODE_SESSION environment variable not set. "
                "Please set it to your LeetCode session cookie value."
            )

        if LeetCodeTester is None:
            raise ImportError("LeetCodeTester could not be imported from DebugBench")

        _tester_instance = LeetCodeTester()

    return _tester_instance


def validate_code_with_leetcode(code: str, task_id: str, language: str = "python") -> Tuple[bool, Dict]:
    """
    Validate code using LeetCode API.

    Args:
        code: The Python code to validate.
        task_id: LeetCode problem slug (e.g., 'two-sum').
        language: Programming language (default: Python3).

    Returns:
        Tuple[bool, Dict]: (is_valid, feedback)
            - is_valid: True if all test cases passed
            - feedback: Dict with submission results
    """
    global _last_submission_time

    try:
        # Enforce cooldown to avoid rate limiting
        time_since_last = time.time() - _last_submission_time
        if time_since_last < SUBMISSION_COOLDOWN:
            wait_time = SUBMISSION_COOLDOWN - time_since_last
            print(f"Waiting {wait_time:.1f}s before next LeetCode submission...")
            time.sleep(wait_time)

        # Get tester instance
        tester = get_leetcode_tester()

        # Submit code
        reward, submission_result = tester.test(code=code, task_id=task_id, language=language)

        # Update last submission time
        _last_submission_time = time.time()

        # Check if accepted
        is_valid = reward and submission_result.get('status_msg') == 'Accepted'

        return is_valid, submission_result

    except EnvironmentError as e:
        return False, {"error": str(e), "status_msg": "Environment Error"}
    except Exception as e:
        return False, {"error": str(e), "status_msg": "Validation Error"}
