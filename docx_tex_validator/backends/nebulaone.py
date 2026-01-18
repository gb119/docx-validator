"""
NebulaOne backend for AI model interactions.

NebulaOne is assumed to be an OpenAI-compatible API endpoint.
"""

import os
from typing import Optional

from .openai import OpenAIBackend


class NebulaOneBackend(OpenAIBackend):
    """Backend for NebulaOne AI models.

    NebulaOne is treated as an OpenAI-compatible endpoint with specific defaults.
    You can configure the endpoint URL via the NEBULAONE_BASE_URL environment variable
    or the base_url parameter.

    Keyword Parameters:
        model_name (str):
            Name of the model to use.
        api_key (str):
            API key for authentication. If not provided, will try:
            - NEBULAONE_API_KEY environment variable
            - OPENAI_API_KEY environment variable
        base_url (str):
            Base URL for the NebulaOne API endpoint. If not provided, will try:
            - NEBULAONE_BASE_URL environment variable
            - Default to a common NebulaOne endpoint
        **kwargs:
            Additional configuration options.

    Examples:
        >>> backend = NebulaOneBackend(model_name='nebula-1')
        >>> backend = NebulaOneBackend(api_key='your-key', base_url='https://api.nebulaone.example')
    """

    def __init__(
        self,
        model_name: str = "nebula-1",
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        **kwargs,
    ):
        # Set API key from NebulaOne environment variable if not provided
        if api_key is None:
            api_key = os.getenv("NEBULAONE_API_KEY") or os.getenv("OPENAI_API_KEY")

        # Set base URL from NebulaOne environment variable if not provided
        if base_url is None:
            base_url = os.getenv("NEBULAONE_BASE_URL")
            # Note: If NebulaOne has a specific default endpoint, it should be set here
            # For now, we'll let it fall back to None and require configuration

        # Initialize the parent OpenAI backend with NebulaOne configuration
        super().__init__(model_name=model_name, api_key=api_key, base_url=base_url, **kwargs)

    @property
    def name(self) -> str:
        """Return the name of this backend.

        Returns:
            (str):
                Backend name identifier.
        """
        return "nebulaone"
