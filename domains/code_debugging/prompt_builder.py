from typing import List, Optional, Tuple


# IO_INTENTION_PROMPT from DebugBench
IO_INTENTION_PROMPT_TEMPLATE = """Observe the function intention and its corresponding {LANG} implementation which is complete with no extra context. The implementation is faulty. Your task is to fix up the code and explain on the modification in less than 20 words.
You have to write the fixed code again. You should put <code></code> and <exp></exp> on the boundary of the code and the explanation. Do not write anything else in your response. Your reply should be like this:
<code>
fixed code
</code>
<exp>
short explanation about the bug
</exp>

Function Intention:
{DESCRIPTION}

Examples:
{EXAMPLES}

Constraints:
{CONSTRAINTS}

Faulty {LANG} Implementation:
{BUGGY_CODE}
"""


def build_debugging_prompt(problem, episodic_examples: Optional[List[Tuple[str, str]]]) -> str:
    """
    Build debugging prompt using IO_INTENTION_PROMPT format.

    Args:
        problem: The debugging problem instance.
        episodic_examples: Optional list of (problem_repr, solution_repr) tuples from memory.

    Returns:
        str: Complete prompt for the LLM.
    """
    # Format examples
    examples_str = "\n".join(problem.examples) if problem.examples else "No examples provided."

    # Build main prompt
    prompt = IO_INTENTION_PROMPT_TEMPLATE.format(
        LANG="Python3",
        DESCRIPTION=problem.description,
        EXAMPLES=examples_str,
        CONSTRAINTS=problem.constraints if problem.constraints else "No constraints specified.",
        BUGGY_CODE=problem.buggy_code
    )

    # Add episodic examples if available
    if episodic_examples and len(episodic_examples) > 0:
        episodic_str = "\n\n--- Similar Past Problems ---\n"
        for i, (prob_repr, sol_repr) in enumerate(episodic_examples[:3], 1):  # Max 3 examples
            episodic_str += f"\nExample {i}:\n{prob_repr}\n{sol_repr}\n"
        episodic_str += "\n--- End of Similar Examples ---\n\n"

        # Insert episodic examples before the main problem
        prompt = episodic_str + prompt

    return prompt
