"""
AI model backends for docx-tex-validator.

This module provides different backend implementations for AI model interactions,
allowing flexibility in choosing which AI service to use.
"""

from typing import Dict, Type

from .base import BaseBackend
from .nebulaone import NebulaOneBackend
from .openai import OpenAIBackend

# Registry of available backends
BACKENDS: Dict[str, Type[BaseBackend]] = {
    "openai": OpenAIBackend,
    "github": OpenAIBackend,  # GitHub Models use OpenAI-compatible API
    "nebulaone": NebulaOneBackend,
}


def get_backend(backend_name: str, **kwargs) -> BaseBackend:
    """
    Get a backend instance by name.

    Args:
        backend_name: Name of the backend to use (e.g., 'openai', 'github', 'nebulaone')
        **kwargs: Configuration arguments to pass to the backend

    Returns:
        Configured backend instance

    Raises:
        ValueError: If the backend name is not recognized

    Examples:
        >>> backend = get_backend('openai', model_name='gpt-4')
        >>> backend = get_backend('nebulaone', api_key='your-key')
    """
    backend_name_lower = backend_name.lower()
    if backend_name_lower not in BACKENDS:
        available = ", ".join(BACKENDS.keys())
        raise ValueError(f"Unknown backend: {backend_name}. Available backends: {available}")

    backend_class = BACKENDS[backend_name_lower]
    return backend_class(**kwargs)


__all__ = [
    "BaseBackend",
    "OpenAIBackend",
    "NebulaOneBackend",
    "BACKENDS",
    "get_backend",
]
