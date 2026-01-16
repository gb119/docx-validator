"""
OpenAI-compatible backend for AI model interactions.

Supports OpenAI API and OpenAI-compatible endpoints like GitHub Models.
"""

import os
from typing import Optional

from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIChatModel

from .base import BaseBackend


class OpenAIBackend(BaseBackend):
    """
    Backend for OpenAI and OpenAI-compatible APIs.

    This includes:
    - OpenAI API (https://api.openai.com/v1)
    - GitHub Models (https://models.inference.ai.azure.com)
    - Azure OpenAI
    - Any other OpenAI-compatible endpoint
    """

    def __init__(
        self,
        model_name: str = "gpt-4o-mini",
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        **kwargs,
    ):
        """
        Initialize the OpenAI backend.

        Args:
            model_name: Name of the model to use (default: gpt-4o-mini)
            api_key: API key for authentication. If not provided, will try:
                    - GITHUB_TOKEN environment variable
                    - OPENAI_API_KEY environment variable
            base_url: Base URL for the API endpoint. If not provided, will try:
                     - OPENAI_BASE_URL environment variable
                     - Default to OpenAI API
            **kwargs: Additional configuration options
        """
        super().__init__(model_name, api_key, **kwargs)

        # Set API key from environment if not provided
        if self.api_key is None:
            self.api_key = os.getenv("GITHUB_TOKEN") or os.getenv("OPENAI_API_KEY")

        # Set base URL from environment if not provided
        if base_url is not None:
            os.environ["OPENAI_BASE_URL"] = base_url
        elif "OPENAI_BASE_URL" not in os.environ:
            # Set default for GitHub Models if using GITHUB_TOKEN
            if os.getenv("GITHUB_TOKEN"):
                os.environ["OPENAI_BASE_URL"] = "https://models.inference.ai.azure.com"

        # Set API key in environment for pydantic-ai
        if self.api_key:
            os.environ["OPENAI_API_KEY"] = self.api_key

        self.model = OpenAIChatModel(self.model_name)

    def get_agent(self, system_prompt: str) -> Agent:
        """
        Get an agent configured with this backend.

        Args:
            system_prompt: System prompt to use for the agent

        Returns:
            Agent instance configured for this backend
        """
        return Agent(
            model=self.model,
            system_prompt=system_prompt,
        )

    def run_sync(self, agent: Agent, prompt: str) -> str:
        """
        Run a synchronous inference request.

        Args:
            agent: The agent to use for inference
            prompt: The user prompt

        Returns:
            The model's response as a string
        """
        response = agent.run_sync(prompt)
        return str(response.data)

    @property
    def name(self) -> str:
        """Return the name of this backend."""
        return "openai"
