"""
LLM-based System 1 solver for SOFAI-Core framework.

This module provides a domain-agnostic wrapper for LLM interaction using Ollama.
"""

import ollama


class LLMSolver:
    """
    Domain-agnostic LLM solver (System 1).

    Provides a clean interface for interacting with LLMs via Ollama.
    """

    def __init__(self, model: str = "mistral"):
        """
        Initialize the LLM solver.

        Args:
            model: Name of the Ollama model to use (default: mistral).
        """
        self.model = model

    def generate_response(self, messages: list) -> str:
        """
        Generate a response from the LLM given a conversation history.

        Args:
            messages: List of message dictionaries with 'role' and 'content' keys.
                Example: [{"role": "user", "content": "..."}]

        Returns:
            str: The complete response from the LLM.
        """
        stream = ollama.chat(
            model=self.model,
            messages=messages,
            stream=True,
        )
        response = ""
        for chunk in stream:
            response += chunk["message"]["content"]
        return response
