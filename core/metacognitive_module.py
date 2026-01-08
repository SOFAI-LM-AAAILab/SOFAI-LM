"""
Core metacognitive module for SOFAI-Core framework.

This module implements the domain-agnostic solving logic that coordinates
System 1 (LLM), System 2 (LLM), episodic memory, and iterative refinement.
"""

import time
from typing import Any, Dict, Optional

from core.domain import DomainInterface
from core.llm_solver import LLMSolver
from core.episodic_memory import EpisodicMemory
from core.improvement_trend_evaluator import ImprovementTrendEvaluator


class MCModule:
    """
    Domain-agnostic metacognitive module implementing the SOFAI architecture.

    This module coordinates the iterative refinement loop between System 1 (LLM)
    and System 2 (LLM), leveraging episodic memory and feedback mechanisms.
    """

    def __init__(
        self,
        domain: DomainInterface,
        llm_model: str = "mistral",
        max_iterations: int = 5,
        s2_llm_model: Optional[str] = None
    ):
        """
        Initialize the SOFAI metacognitive module.

        Args:
            domain: Domain-specific implementation of DomainInterface.
            llm_model: Name of the LLM model to use for S1 (default: mistral).
            max_iterations: Maximum number of S1 refinement iterations (default: 5).
            s2_llm_model: Name of the LLM model to use for S2. If None, uses same as llm_model (default: None).
        """
        self.domain = domain
        self.llm_solver = LLMSolver(model=llm_model)
        self.s2_llm_solver = LLMSolver(model=s2_llm_model if s2_llm_model else llm_model)
        self.episodic_memory = EpisodicMemory()
        self.max_iterations = max_iterations

    def solve(self, problem: Any, verbose: bool = True) -> Dict[str, Any]:
        """
        Solve a problem using the SOFAI architecture.

        Args:
            problem: The problem instance (domain-specific format).
            verbose: If True, print progress information (default: True).

        Returns:
            Dict containing:
                - 'solved': bool, whether a valid solution was found
                - 'solution': the solution object
                - 's1_solved': bool, whether S1 found the solution
                - 's2_solved': bool, whether S2 was invoked and found the solution
                - 'iterations': number of S1 iterations performed
                - 's1_time': time spent in S1 (seconds)
                - 's2_time': time spent in S2 (seconds)
                - 'total_time': total solving time (seconds)
        """
        start_time = time.time()
        s1_time = 0
        s2_time = 0
        iteration = 0
        s1_solved = False
        s2_solved = False
        solution = None

        # Initialize trend evaluator for this solve attempt
        trend_evaluator = ImprovementTrendEvaluator()

        # Get problem representation for episodic memory
        problem_repr = self.domain.get_problem_representation(problem)

        # Build initial prompt (with episodic examples if available)
        episodic_examples = None
        if self.episodic_memory.memory:
            if verbose:
                print("Retrieving similar examples from episodic memory...")
            episodic_examples = self.episodic_memory.retrieve_similar(problem_repr)

        initial_prompt = self.domain.build_prompt(problem, episodic_examples)
        messages = [{"role": "user", "content": initial_prompt}]

        if verbose:
            print(f"\n{'='*60}")
            print("Starting SOFAI solve process...")
            print(f"{'='*60}\n")

        # System 1 iterative refinement loop
        while iteration < self.max_iterations:
            iteration += 1
            if verbose:
                print(f"--- Iteration {iteration}/{self.max_iterations} ---")

            # S1: Generate solution using LLM
            s1_iter_start = time.time()
            llm_response = self.llm_solver.generate_response(messages)
            s1_iter_time = time.time() - s1_iter_start
            s1_time += s1_iter_time

            if verbose:
                print(f"S1 response generated in {s1_iter_time:.2f}s")

            # Parse solution from LLM response
            solution = self.domain.parse_solution(llm_response)

            # Validate solution
            is_valid, feedback = self.domain.validate_solution(problem, solution)

            if is_valid:
                if verbose:
                    print("✓ Valid solution found by S1!")
                s1_solved = True
                # Store successful solution in episodic memory
                solution_repr = self.domain.format_solution_for_memory(solution)
                self.episodic_memory.add_memory(problem_repr, solution_repr)
                break

            # Solution is invalid - provide feedback
            if verbose:
                feedback_str = self.domain.format_feedback(feedback)
                print(f"✗ Invalid solution. Feedback: {feedback_str}")

            # Update trend evaluator
            trend_evaluator.update_feedback(feedback)

            # Check if we should invoke S2 (max iterations or no improvement)
            if iteration == self.max_iterations or trend_evaluator.get_no_improvement_flag():
                if verbose:
                    if iteration == self.max_iterations:
                        print(f"\nReached maximum iterations ({self.max_iterations})")
                    else:
                        print("\nNo improvement detected in feedback")
                    print("Invoking System 2 (LLM solver)...\n")

                # S2: LLM solver
                s2_start = time.time()
                s2_solution, s2_metadata = self.domain.run_s2_solver(problem, self.s2_llm_solver)
                s2_time = time.time() - s2_start

                if verbose:
                    print(f"S2 completed in {s2_time:.2f}s")

                solution = s2_solution
                s2_solved = True

                # Store S2 solution in episodic memory
                solution_repr = self.domain.format_solution_for_memory(solution)
                self.episodic_memory.add_memory(problem_repr, solution_repr)
                break

            # Continue refinement - add feedback to conversation
            feedback_str = self.domain.format_feedback(feedback)
            messages.append({"role": "assistant", "content": llm_response})
            messages.append({"role": "user", "content": f"Feedback: {feedback_str}"})

        total_time = time.time() - start_time

        if verbose:
            print(f"\n{'='*60}")
            print("Solve process completed")
            print(f"{'='*60}")
            print(f"Total time: {total_time:.2f}s")
            print(f"S1 time: {s1_time:.2f}s")
            print(f"S2 time: {s2_time:.2f}s")
            print(f"Iterations: {iteration}")
            print(f"Solved by: {'S1' if s1_solved else 'S2' if s2_solved else 'None'}")
            print(f"{'='*60}\n")

        return {
            'solved': s1_solved or s2_solved,
            'solution': solution,
            's1_solved': s1_solved,
            's2_solved': s2_solved,
            'iterations': iteration,
            's1_time': s1_time,
            's2_time': s2_time,
            'total_time': total_time
        }
