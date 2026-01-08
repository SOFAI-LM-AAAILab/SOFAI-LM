import re


def parse_fixed_code(llm_response: str) -> str:
    """
    Parse LLM response to extract fixed code from <code></code> tags.

    Args:
        llm_response: Raw LLM response text.

    Returns:
        str: Extracted fixed code, or empty string if parsing fails.
    """
    # Try to extract code between <code></code> tags
    code_match = re.search(r'<code>\s*(.*?)\s*</code>', llm_response, re.DOTALL)

    if code_match:
        fixed_code = code_match.group(1).strip()
        return fixed_code

    # Fallback: try to find code block markers
    if '```python' in llm_response:
        code_match = re.search(r'```python\s*(.*?)\s*```', llm_response, re.DOTALL)
        if code_match:
            return code_match.group(1).strip()

    if '```' in llm_response:
        code_match = re.search(r'```\s*(.*?)\s*```', llm_response, re.DOTALL)
        if code_match:
            return code_match.group(1).strip()

    # Last resort: return entire response (might be just code)
    return llm_response.strip()


def parse_explanation(llm_response: str) -> str:
    """
    Parse LLM response to extract explanation from <exp></exp> tags.

    Args:
        llm_response: Raw LLM response text.

    Returns:
        str: Extracted explanation, or empty string if not found.
    """
    exp_match = re.search(r'<exp>\s*(.*?)\s*</exp>', llm_response, re.DOTALL)

    if exp_match:
        return exp_match.group(1).strip()

    return ""
