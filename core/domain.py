"""
Abstract domain interface for SOFAI-Core framework.

This module defines the DomainInterface abstract base class that all domain
implementations must inherit from.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Tuple


class DomainInterface(ABC):
    """
    Abstract base class defining the interface for domain-specific implementations.

    Each domain (e.g., graph coloring, planning) must implement this interface
    to integrate with the SOFAI framework.
    """

    @abstractmethod
    def generate_problem(self, **kwargs) -> Any:
        """
        Generate a problem instance for this domain.

        Args:
            **kwargs: Domain-specific parameters for problem generation.

        Returns:
            Any: A problem instance in domain-specific format.
        """
        pass

    @abstractmethod
    def validate_solution(self, problem: Any, solution: Any) -> Tuple[bool, Any]:
        """
        Validate a proposed solution for correctness.

        Args:
            problem: The problem instance.
            solution: The proposed solution.

        Returns:
            Tuple[bool, Any]: (is_valid, feedback)
                - is_valid: True if solution is correct, False otherwise.
                - feedback: Domain-specific feedback (e.g., list of errors,
                  error messages, or None if valid).
        """
        pass

    @abstractmethod
    def build_prompt(
        self,
        problem: Any,
        episodic_examples: List[Tuple[str, str]] = None
    ) -> str:
        """
        Construct a prompt for the LLM solver.

        Args:
            problem: The problem instance.
            episodic_examples: Optional list of (problem, solution) tuples
                from episodic memory.

        Returns:
            str: A formatted prompt string for the LLM.
        """
        pass

    @abstractmethod
    def parse_solution(self, llm_response: str) -> Any:
        """
        Parse the LLM's response to extract the solution.

        Args:
            llm_response: Raw text response from the LLM.

        Returns:
            Any: Parsed solution in domain-specific format.
        """
        pass

    @abstractmethod
    def run_s2_solver(self, problem: Any, llm_solver: Any) -> Tuple[Any, Any]:
        """
        Run the System 2 solver for this domain using an LLM.

        Args:
            problem: The problem instance.
            llm_solver: LLMSolver instance to use for S2.

        Returns:
            Tuple[Any, Any]: (solution, metadata)
                - solution: The solution from S2.
                - metadata: Additional information (e.g., number of colors used,
                  plan length, etc.).
        """
        pass

    @abstractmethod
    def get_problem_representation(self, problem: Any) -> str:
        """
        Get a string representation of the problem for episodic memory.

        This representation is used for similarity matching in episodic memory
        retrieval (BM25).

        Args:
            problem: The problem instance.

        Returns:
            str: String representation suitable for BM25 matching.
        """
        pass

    @abstractmethod
    def format_solution_for_memory(self, solution: Any) -> str:
        """
        Format a solution for storage in episodic memory.

        Args:
            solution: The solution to format.

        Returns:
            str: String representation of the solution.
        """
        pass

    @abstractmethod
    def format_feedback(self, feedback: Any) -> str:
        """
        Format validation feedback for presentation to the LLM.

        Args:
            feedback: Raw feedback from validate_solution.

        Returns:
            str: Human-readable feedback string for the LLM.
        """
        pass
