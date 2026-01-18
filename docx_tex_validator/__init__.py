"""
docx-validator: A Python library for validating Microsoft Word .docx files using LLMs.
"""

from .backends import (
    BaseBackend,
    NebulaOneBackend,
    OpenAIBackend,
    get_backend,
)
from .parsers import (
    BaseParser,
    DocxParser,
    HTMLParser,
    LaTeXParser,
    detect_parser,
    get_parser,
)
from .validator import (
    DocxValidator,
    ValidationReport,
    ValidationResult,
    ValidationSpec,
)

__version__ = "0.1.0"
__all__ = [
    "DocxValidator",
    "ValidationResult",
    "ValidationSpec",
    "ValidationReport",
    "BaseBackend",
    "OpenAIBackend",
    "NebulaOneBackend",
    "get_backend",
    "BaseParser",
    "DocxParser",
    "HTMLParser",
    "LaTeXParser",
    "get_parser",
    "detect_parser",
]
