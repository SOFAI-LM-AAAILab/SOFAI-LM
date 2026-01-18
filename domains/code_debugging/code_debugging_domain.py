from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple
from core.domain import DomainInterface
from domains.code_debugging.data_loader import load_problem_from_dataset
from domains.code_debugging.validator import validate_code_with_leetcode
from domains.code_debugging.prompt_builder import build_debugging_prompt
from domains.code_debugging.solution_parser import parse_fixed_code


@dataclass
class CodeDebuggingProblem:
    """Represents a code debugging problem from DebugBench."""
    slug: str
    description: str
    examples: List[str]
    constraints: str
    level: str
    buggy_code: str
    oracle_code: str
    explanations: str
    content: str
    bug_type: str


class CodeDebuggingDomain(DomainInterface):
    """Code debugging domain using DebugBench dataset and LeetCode validation."""

    def __init__(self):
        """Initialize the code debugging domain."""
        self.language = "Python3"  # For data loader (file lookup)
        self.leetcode_language = "python"  # For LeetCode API

    def generate_problem(self, **kwargs) -> CodeDebuggingProblem:
        """
        Load a random problem from DebugBench dataset.

        Args:
            bug_type (str, optional): Specific bug type to load (e.g., 'condition', 'variable_misuse').
                                      If None, randomly selects from all bug types.
            problem_index (int, optional): Specific problem index within the bug type file.
                                           If None, randomly selects.

        Returns:
            CodeDebuggingProblem: A debugging problem instance.
        """
        bug_type = kwargs.get('bug_type', None)
        problem_index = kwargs.get('problem_index', None)

        problem = load_problem_from_dataset(
            language=self.language,
            bug_type=bug_type,
            problem_index=problem_index
        )

        return problem

    def validate_solution(self, problem: CodeDebuggingProblem, solution: str) -> Tuple[bool, Any]:
        """
        Validate the fixed code using LeetCode API.

        Args:
            problem: The debugging problem instance.
            solution: The fixed code (string).

        Returns:
            Tuple[bool, Any]: (is_valid, feedback)
                - is_valid: True if code passes all LeetCode test cases
                - feedback: Dict with validation results or error messages
        """
        is_valid, feedback = validate_code_with_leetcode(
            code=solution,
            task_id=problem.slug,
            language=self.leetcode_language  # Use lowercase for LeetCode API
        )

        return is_valid, feedback

    def build_prompt(self, problem: CodeDebuggingProblem, episodic_examples: Optional[List[Tuple[str, str]]]) -> str:
        """
        Build the LLM prompt using IO_INTENTION_PROMPT format.

        Args:
            problem: The debugging problem instance.
            episodic_examples: Optional list of (problem_repr, solution_repr) tuples from memory.

        Returns:
            str: The complete prompt for the LLM.
        """
        return build_debugging_prompt(problem, episodic_examples)

    def parse_solution(self, llm_response: str) -> str:
        """
        Parse the LLM response to extract fixed code from <code></code> tags.

        Args:
            llm_response: Raw LLM response text.

        Returns:
            str: Extracted fixed code, or empty string if parsing fails.
        """
        return parse_fixed_code(llm_response)

    def run_s2_solver(self, problem: CodeDebuggingProblem, llm_solver: Any) -> Tuple[str, Dict]:
        """
        Run the S2 LLM solver (slower, more deliberate reasoning).

        Uses the same prompt as S1, but invoked after S1 has failed to find a solution.

        Args:
            problem: The debugging problem instance.
            llm_solver: LLMSolver instance configured for S2.

        Returns:
            Tuple[str, Dict]: (fixed_code, metadata)
        """
        # Build the same prompt as S1 (no episodic examples for S2)
        initial_prompt = self.build_prompt(problem, episodic_examples=None)
        messages = [{"role": "user", "content": initial_prompt}]

        # Generate solution using S2 LLM
        llm_response = llm_solver.generate_response(messages)

        # Parse solution
        fixed_code = self.parse_solution(llm_response)

        # Metadata: just indicate S2 was used
        metadata = {"solver": "S2_LLM"}

        return fixed_code, metadata

    def get_problem_representation(self, problem: CodeDebuggingProblem) -> str:
        """
        Get string representation of problem for episodic memory retrieval.

        Args:
            problem: The debugging problem instance.

        Returns:
            str: String representation combining slug, description, and bug type.
        """
        return f"Problem: {problem.slug}\nBug Type: {problem.bug_type}\nDescription: {problem.description[:200]}..."

    def format_solution_for_memory(self, solution: str) -> str:
        """
        Format solution for episodic memory storage.

        Args:
            solution: The fixed code.

        Returns:
            str: Formatted solution string.
        """
        return f"Fixed Code:\n{solution}"

    def format_feedback(self, feedback: Any) -> str:
        """
        Format validation feedback for LLM refinement.

        Args:
            feedback: Validation feedback dict from LeetCode API.

        Returns:
            str: Human-readable feedback string.
        """
        if isinstance(feedback, dict):
            status = feedback.get('status_msg', 'Unknown')
            runtime = feedback.get('runtime', 'N/A')
            memory = feedback.get('memory', 'N/A')

            if status == "Accepted":
                return f"Solution accepted! Runtime: {runtime}, Memory: {memory}"
            else:
                error_msg = feedback.get('full_runtime_error', feedback.get('compile_error', ''))
                last_testcase = feedback.get('last_testcase', '')
                expected = feedback.get('expected_output', '')
                actual = feedback.get('code_output', '')

                feedback_str = f"Status: {status}\n"
                if error_msg:
                    feedback_str += f"Error: {error_msg}\n"
                if last_testcase:
                    feedback_str += f"Failed Test Case: {last_testcase}\n"
                if expected and actual:
                    feedback_str += f"Expected: {expected}\nActual: {actual}\n"

                return feedback_str

        return f"Validation failed: {feedback}"
