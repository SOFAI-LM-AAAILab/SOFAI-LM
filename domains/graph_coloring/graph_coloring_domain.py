"""
Graph Coloring domain implementation for SOFAI-Core framework.

This module implements the DomainInterface for graph coloring problems.
"""

from typing import Any, Dict, List, Tuple
import os

from core.domain import DomainInterface
from domains.graph_coloring.generator import GraphColoringGenerator
from domains.graph_coloring.validator import GraphColoringValidator
from domains.graph_coloring.prompt_builder import prompt_generator
from domains.graph_coloring.solution_parser import parse_solution as parse_coloring
from domains.graph_coloring.utils import parse_graph


class GraphColoringProblem:
    """Container for graph coloring problem data."""

    def __init__(self, file_path: str, min_colors: int):
        """
        Initialize a graph coloring problem.

        Args:
            file_path: Path to the DIMACS graph file.
            min_colors: Minimum number of colors (chromatic number).
        """
        self.file_path = file_path
        self.min_colors = min_colors
        # Parse the graph to get representation
        self.graph_repr, self.num_edges, self.num_vertices, self.edges, self.vertices = parse_graph(file_path)


class GraphColoringDomain(DomainInterface):
    """
    Graph Coloring domain implementation.

    Implements the SOFAI DomainInterface for graph coloring problems using
    LLM-based solving for both S1 and S2.
    """

    def __init__(self):
        """Initialize the GraphColoringDomain."""
        self.generator = GraphColoringGenerator()

    def generate_problem(self, **kwargs) -> GraphColoringProblem:
        """
        Generate a graph coloring problem instance.

        Args:
            **kwargs: Must include:
                - num_nodes (int): Number of nodes in the graph.
                - edge_prob (float): Edge probability for Erdős–Rényi model.

        Returns:
            GraphColoringProblem: The generated problem instance.
        """
        num_nodes = kwargs.get('num_nodes', 10)
        edge_prob = kwargs.get('edge_prob', 0.5)

        # Generate one graph
        chromatic_nums = self.generator.generate_and_save_graphs(
            n_graphs=1,
            n_vertices_list=[num_nodes],
            p=edge_prob
        )

        # Get the file path and chromatic number
        file_path = list(chromatic_nums.keys())[0]
        min_colors = chromatic_nums[file_path]

        return GraphColoringProblem(file_path, min_colors)

    def validate_solution(
        self,
        problem: GraphColoringProblem,
        solution: Dict[str, int]
    ) -> Tuple[bool, Any]:
        """
        Validate a graph coloring solution.

        Args:
            problem: The GraphColoringProblem instance.
            solution: Dictionary mapping vertices to colors.

        Returns:
            Tuple[bool, Any]: (is_valid, feedback)
                - is_valid: True if no adjacent vertices share colors.
                - feedback: List of (u, v) edges with violations, or None.
        """
        validator = GraphColoringValidator(problem.file_path)
        is_valid, errors = validator.validate_coloring(solution)
        return is_valid, errors if errors else None

    def build_prompt(
        self,
        problem: GraphColoringProblem,
        episodic_examples: List[Tuple[str, str]] = None
    ) -> str:
        """
        Build a prompt for the LLM to solve graph coloring.

        Args:
            problem: The GraphColoringProblem instance.
            episodic_examples: Optional list of (problem, solution) examples.

        Returns:
            str: Formatted prompt for the LLM.
        """
        return prompt_generator(
            problem.graph_repr,
            problem.min_colors,
            additional_examples=episodic_examples
        )

    def parse_solution(self, llm_response: str) -> Dict[str, int]:
        """
        Parse LLM response to extract color assignments.

        Args:
            llm_response: Raw text from the LLM.

        Returns:
            Dict[str, int]: Mapping of vertices to colors.
        """
        return parse_coloring(llm_response)

    def run_s2_solver(self, problem: GraphColoringProblem, llm_solver: Any) -> Tuple[Dict[str, int], int]:
        """
        Run the S2 LLM solver (slower, more deliberate reasoning).

        Uses the same prompt as S1, but invoked after S1 has failed to find a solution.

        Args:
            problem: The graph coloring problem instance.
            llm_solver: LLMSolver instance configured for S2.

        Returns:
            Tuple[Dict[str, int], int]: (coloring, max_color_used)
        """
        # Build the same prompt as S1 (no episodic examples for S2)
        initial_prompt = self.build_prompt(problem, episodic_examples=None)
        messages = [{"role": "user", "content": initial_prompt}]

        # Generate solution using S2 LLM
        llm_response = llm_solver.generate_response(messages)

        # Parse solution
        solution = self.parse_solution(llm_response)

        # Calculate max color used as metadata
        max_color = max(solution.values()) if solution else 0

        return solution, max_color

    def get_problem_representation(self, problem: GraphColoringProblem) -> str:
        """
        Get string representation for episodic memory.

        Args:
            problem: The GraphColoringProblem instance.

        Returns:
            str: DIMACS format graph representation.
        """
        return problem.graph_repr

    def format_solution_for_memory(self, solution: Dict[str, int]) -> str:
        """
        Format solution for episodic memory storage.

        Args:
            solution: Vertex-to-color mapping.

        Returns:
            str: Solution in (vertex color) format.
        """
        return "\n".join([f"({v} {c})" for v, c in solution.items()])

    def format_feedback(self, feedback: List[Tuple[str, str]]) -> str:
        """
        Format validation feedback for the LLM.

        Args:
            feedback: List of (u, v) edges with color violations.

        Returns:
            str: Human-readable feedback string.
        """
        if not feedback:
            return "Solution is correct!"

        feedback_list = [
            f"adjacent vertices {edge[0]} and {edge[1]} have the same color"
            for edge in feedback
        ]
        return " | ".join(feedback_list)
