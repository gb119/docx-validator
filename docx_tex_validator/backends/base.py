"""
Base backend interface for AI model interactions.
"""

from abc import ABC, abstractmethod
from typing import Any, Optional


class BaseBackend(ABC):
    """Abstract base class for AI model backends.

    This defines the interface that all backend implementations must follow.

    Keyword Parameters:
        model_name (str):
            Name of the model to use.
        api_key (str):
            API key for authentication (if required).
        **kwargs:
            Additional backend-specific configuration.
    """

    def __init__(self, model_name: str, api_key: Optional[str] = None, **kwargs):
        self.model_name = model_name
        self.api_key = api_key
        self.config = kwargs

    @abstractmethod
    def get_agent(self, system_prompt: str) -> Any:
        """Get an agent configured with this backend.

        Args:
            system_prompt (str):
                System prompt to use for the agent.

        Returns:
            (Any):
                Agent instance configured for this backend.
        """
        pass

    @abstractmethod
    def run_sync(self, agent: Any, prompt: str, message_history=None) -> Any:
        """Run a synchronous inference request.

        Args:
            agent (Any):
                The agent to use for inference.
            prompt (str):
                The user prompt.

        Keyword Parameters:
            message_history (Any):
                Optional message history for context continuity.

        Returns:
            (Any):
                The model's response (typically AgentRunResult or similar).
        """
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """Return the name of this backend.

        Returns:
            (str):
                Backend name identifier.
        """
        pass
