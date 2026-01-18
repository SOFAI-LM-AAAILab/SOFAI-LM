"""
SOFAI-Core main entry point.

This CLI application allows users to run the SOFAI framework with different domains.
"""

import argparse
import os
import sys
import subprocess

from core.metacognitive_module import MCModule
from domains.graph_coloring.graph_coloring_domain import GraphColoringDomain
from domains.code_debugging.code_debugging_domain import CodeDebuggingDomain


def ensure_ollama_running():
    """Ensure Ollama service is running."""
    try:
        # Try to start Ollama service in the background
        subprocess.Popen(
            ["ollama", "serve"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        print("Started Ollama service...")
    except Exception as e:
        print(f"Warning: Could not start Ollama service: {e}")
        print("Please ensure Ollama is installed and running.")


def ensure_model_available(model_name: str):
    """
    Check if an Ollama model is available locally, and pull it if not.

    Args:
        model_name: Name of the Ollama model to check/pull.
    """
    try:
        # Check if model exists
        result = subprocess.run(
            ['ollama', 'list'],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0 and model_name in result.stdout:
            print(f"Model '{model_name}' is available.")
            return

        # Model not found, attempt to pull
        print(f"Model '{model_name}' not found locally. Pulling...")
        pull_result = subprocess.run(
            ['ollama', 'pull', model_name],
            timeout=600  # 10 minutes timeout for large models
        )
        if pull_result.returncode == 0:
            print(f"Model '{model_name}' pulled successfully.")
        else:
            print(f"Warning: Failed to pull model '{model_name}'.")
    except subprocess.TimeoutExpired:
        print(f"Warning: Timeout while pulling model '{model_name}'.")
    except FileNotFoundError:
        print("Warning: Ollama not found. Please install Ollama first.")
    except Exception as e:
        print(f"Warning: Could not check/pull model '{model_name}': {e}")


def main():
    """Main entry point for SOFAI-Core."""
    parser = argparse.ArgumentParser(
        description="SOFAI-Core: Modular neurosymbolic framework for CSPs"
    )

    # Domain selection
    parser.add_argument(
        "--domain",
        type=str,
        required=True,
        choices=["graph_coloring", "code_debugging"],
        help="Domain to solve"
    )

    # S1 LLM and S2 LRM configuration
    parser.add_argument(
        "--s1-llm",
        type=str,
        default="gemma3:1b",
        help="Ollama model for S1 LLM (default: gemma3:1b)"
    )

    parser.add_argument(
        "--max-iterations",
        type=int,
        default=5,
        help="Maximum S1 refinement iterations (default: 5)"
    )

    parser.add_argument(
        "--s2-lrm",
        type=str,
        default="deepseek-r1:1.5b",
        help="Ollama model for S2 LRM (default: deepseek-r1:1.5b)"
    )

    # Graph coloring specific arguments
    parser.add_argument(
        "--nodes",
        type=int,
        default=10,
        help="Number of nodes for graph coloring (default: 10)"
    )

    parser.add_argument(
        "--edge-prob",
        type=float,
        default=0.5,
        help="Edge probability for Erdős–Rényi graph (default: 0.5)"
    )

    # Code Debugging specific arguments
    parser.add_argument(
        "--bug-type",
        type=str,
        default=None,
        help="Specific bug type to solve (e.g., 'condition', 'variable_misuse'). If not specified, random."
    )

    parser.add_argument(
        "--problem-index",
        type=int,
        default=None,
        help="Specific problem index within the bug type file. If not specified, random."
    )

    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose output"
    )

    args = parser.parse_args()

    # Ensure Ollama is running
    ensure_ollama_running()

    # Ensure required models are available (auto-pull if needed)
    ensure_model_available(args.s1_llm)
    if args.s2_lrm and args.s2_lrm != args.s1_llm:
        ensure_model_available(args.s2_lrm)

    # Initialize domain
    print(f"\n{'='*60}")
    print(f"SOFAI-Core Framework")
    print(f"Domain: {args.domain}")
    print(f"S1 LLM: {args.s1_llm}")
    print(f"S2 LRM: {args.s2_lrm}")
    print(f"{'='*60}\n")

    if args.domain == "graph_coloring":
        domain = GraphColoringDomain()
        problem_kwargs = {
            'num_nodes': args.nodes,
            'edge_prob': args.edge_prob
        }
    elif args.domain == "code_debugging":
        print("Initializing Code Debugging domain (DebugBench)...")

        # Check for LEETCODE_SESSION
        if not os.environ.get('LEETCODE_SESSION'):
            print("\nWARNING: LEETCODE_SESSION environment variable not set.")
            print("LeetCode validation will not work without it.")
            print("Set it using: export LEETCODE_SESSION='your_cookie_value'\n")

        domain = CodeDebuggingDomain()
        problem_kwargs = {
            'bug_type': args.bug_type,
            'problem_index': args.problem_index
        }
    else:
        print(f"Error: Domain '{args.domain}' not implemented yet.")
        sys.exit(1)

    # Generate problem
    print("Generating problem instance...")
    problem = domain.generate_problem(**problem_kwargs)

    if args.domain == "graph_coloring":
        print(f"Generated graph with {problem.num_vertices} vertices " +
              f"and {problem.num_edges} edges")
        print(f"Chromatic number: {problem.min_colors}")
        print(f"Problem file: {problem.file_path}\n")
    elif args.domain == "code_debugging":
        print(f"\n{'='*80}")
        print(f"Problem: {problem.slug}")
        print(f"Bug Type: {problem.bug_type}")
        print(f"Level: {problem.level}")
        print(f"Description: {problem.description[:200]}...")
        print(f"\nBuggy Code:\n{problem.buggy_code[:300]}...")
        print(f"{'='*80}\n")

    # Initialize and run MC module
    mc = MCModule(
        domain=domain,
        s1_llm=args.s1_llm,
        max_iterations=args.max_iterations,
        s2_lrm=args.s2_lrm
    )

    # Solve
    result = mc.solve(problem, verbose=args.verbose)

    # Display results
    print("\n" + "="*60)
    print("RESULTS")
    print("="*60)
    print(f"Solved: {result['solved']}")
    print(f"Solution found by: {'S1 (LLM)' if result['s1_solved'] else 'S2 (LRM)' if result['s2_solved'] else 'None'}")
    print(f"Iterations: {result['iterations']}")
    print(f"S1 time: {result['s1_time']:.2f}s")
    print(f"S2 time: {result['s2_time']:.2f}s")
    print(f"Total time: {result['total_time']:.2f}s")
    print("\nSolution:")

    # Handle different solution formats for different domains
    if args.domain == "graph_coloring" and isinstance(result['solution'], dict):
        for vertex, color in sorted(result['solution'].items()):
            print(f"  {vertex}: {color}")
    elif args.domain == "code_debugging" and isinstance(result['solution'], str):
        print(f"{result['solution'][:500]}...")  # Show first 500 chars of fixed code
    else:
        print(f"{result['solution']}")

    print("="*60 + "\n")


if __name__ == "__main__":
    main()
