"""
Basic tests for code debugging domain.

Note: Full validation requires LEETCODE_SESSION environment variable.
"""

import os
from domains.code_debugging.code_debugging_domain import CodeDebuggingDomain
from domains.code_debugging.data_loader import load_problem_from_dataset, BUG_TYPES
from domains.code_debugging.solution_parser import parse_fixed_code


def test_data_loader():
    """Test loading problems from DebugBench dataset."""
    print("Testing data loader...")

    # Test loading random problem
    problem = load_problem_from_dataset(language="Python3")
    assert problem.slug != ""
    assert problem.buggy_code != ""
    assert problem.bug_type in BUG_TYPES
    print(f"✓ Loaded random problem: {problem.slug} ({problem.bug_type})")

    # Test loading specific bug type
    problem = load_problem_from_dataset(language="Python3", bug_type="condition error")
    assert problem.bug_type == "condition error"
    print(f"✓ Loaded condition error bug problem: {problem.slug}")


def test_solution_parser():
    """Test parsing fixed code from LLM responses."""
    print("\nTesting solution parser...")

    # Test with <code></code> tags
    response1 = "<code>\ndef fixed():\n    return True\n</code>\n<exp>Fixed the bug</exp>"
    code1 = parse_fixed_code(response1)
    assert "def fixed()" in code1
    print("✓ Parsed code from <code></code> tags")

    # Test with markdown code blocks
    response2 = "```python\ndef fixed():\n    return True\n```"
    code2 = parse_fixed_code(response2)
    assert "def fixed()" in code2
    print("✓ Parsed code from markdown code blocks")


def test_domain_interface():
    """Test CodeDebuggingDomain interface methods."""
    print("\nTesting domain interface...")

    domain = CodeDebuggingDomain()

    # Test generate_problem
    problem = domain.generate_problem()
    assert problem.buggy_code != ""
    print(f"✓ Generated problem: {problem.slug}")

    # Test build_prompt
    prompt = domain.build_prompt(problem, episodic_examples=None)
    assert "Faulty Python3 Implementation" in prompt
    assert problem.buggy_code in prompt
    print("✓ Built prompt successfully")

    # Test parse_solution
    llm_response = "<code>\ndef solution():\n    pass\n</code>"
    solution = domain.parse_solution(llm_response)
    assert "def solution()" in solution
    print("✓ Parsed solution successfully")

    # Test get_problem_representation
    repr_str = domain.get_problem_representation(problem)
    assert problem.slug in repr_str
    print("✓ Got problem representation")

    # Test format_solution_for_memory
    memory_str = domain.format_solution_for_memory("def fixed(): pass")
    assert "Fixed Code" in memory_str
    print("✓ Formatted solution for memory")


def test_validator_env_check():
    """Test validator environment setup."""
    print("\nTesting validator environment...")

    from domains.code_debugging.utils import check_leetcode_session

    has_session = check_leetcode_session()
    if has_session:
        print("✓ LEETCODE_SESSION is set")
    else:
        print("⚠ LEETCODE_SESSION not set (LeetCode validation will not work)")


if __name__ == "__main__":
    print("Running Code Debugging Domain Tests\n" + "="*50)

    try:
        test_data_loader()
        test_solution_parser()
        test_domain_interface()
        test_validator_env_check()

        print("\n" + "="*50)
        print("✓ All tests passed!")

    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
