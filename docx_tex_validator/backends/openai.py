"""
OpenAI-compatible backend for AI model interactions.

Supports OpenAI API and OpenAI-compatible endpoints like GitHub Models.
"""

import logging
import os
from typing import Optional

from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIChatModel

from .base import BaseBackend

# Set up module logger
logger = logging.getLogger(__name__)


class OpenAIBackend(BaseBackend):
    """Backend for OpenAI and OpenAI-compatible APIs.

    This includes:
    - OpenAI API (https://api.openai.com/v1)
    - GitHub Models (https://models.inference.ai.azure.com)
    - Azure OpenAI
    - Any other OpenAI-compatible endpoint

    Keyword Parameters:
        model_name (str):
            Name of the model to use.
        api_key (str):
            API key for authentication. If not provided, will try:
            - GITHUB_TOKEN environment variable
            - OPENAI_API_KEY environment variable
        base_url (str):
            Base URL for the API endpoint. If not provided, will try:
            - OPENAI_BASE_URL environment variable
            - Default to OpenAI API
        **kwargs:
            Additional configuration options.

    Examples:
        >>> backend = OpenAIBackend(model_name='gpt-4o-mini')
        >>> backend = OpenAIBackend(api_key='your-key', base_url='https://api.openai.com/v1')
    """

    def __init__(
        self,
        model_name: str = "gpt-5-turbo",
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        **kwargs,
    ):
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
        """Get an agent configured with this backend.

        Args:
            system_prompt (str):
                System prompt to use for the agent.

        Returns:
            (Agent):
                Agent instance configured for this backend.
        """
        return Agent(
            model=self.model,
            system_prompt=system_prompt,
        )

    def run_sync(self, agent: Agent, prompt: str, message_history=None):
        """Run a synchronous inference request.

        Args:
            agent (Agent):
                The agent to use for inference.
            prompt (str):
                The user prompt.

        Keyword Parameters:
            message_history (Any):
                Optional message history for context continuity.

        Returns:
            (Any):
                AgentRunResult containing the response and message history.
        """
        logger.debug("Backend run_sync called with model: %s", self.model_name)
        
        if message_history:
            response = agent.run_sync(prompt, message_history=message_history)
        else:
            response = agent.run_sync(prompt)
        
        # Log HTTP-related information if available
        # pydantic-ai abstracts the HTTP layer, but we can log what we have access to
        if hasattr(response, 'metadata') and response.metadata:
            logger.debug("HTTP/API Response metadata: %s", response.metadata)
        
        return response

    @property
    def name(self) -> str:
        """Return the name of this backend.

        Returns:
            (str):
                Backend name identifier.
        """
        return "openai"
