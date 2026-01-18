"""
Document parsers for docx-tex-validator.

This module provides different parser implementations for various document formats,
allowing flexibility in choosing which document type to validate.
"""

from typing import Dict, Type

from .base import BaseParser
from .docx_parser import DocxParser
from .html_parser import HTMLParser
from .latex_parser import LaTeXParser

# Registry of available parsers
PARSERS: Dict[str, Type[BaseParser]] = {
    "docx": DocxParser,
    "html": HTMLParser,
    "latex": LaTeXParser,
}


def get_parser(parser_name: str, **kwargs) -> BaseParser:
    """
    Get a parser instance by name.

    Args:
        parser_name: Name of the parser to use (e.g., 'docx', 'html', 'latex')
        **kwargs: Configuration arguments to pass to the parser

    Returns:
        Configured parser instance

    Raises:
        ValueError: If the parser name is not recognized

    Examples:
        >>> parser = get_parser('docx')
        >>> parser = get_parser('latex')
    """
    parser_name_lower = parser_name.lower()
    if parser_name_lower not in PARSERS:
        available = ", ".join(PARSERS.keys())
        raise ValueError(f"Unknown parser: {parser_name}. Available parsers: {available}")

    parser_class = PARSERS[parser_name_lower]
    return parser_class(**kwargs)


def detect_parser(file_path: str) -> BaseParser:
    """
    Automatically detect and return the appropriate parser for a file based on its extension.

    Args:
        file_path: Path to the file

    Returns:
        Appropriate parser instance for the file

    Raises:
        ValueError: If no parser supports the file extension

    Examples:
        >>> parser = detect_parser('document.docx')
        >>> parser = detect_parser('document.html')
    """
    from pathlib import Path

    extension = Path(file_path).suffix.lower()

    for parser_class in PARSERS.values():
        parser = parser_class()
        if parser.supports_extension(extension):
            return parser

    raise ValueError(
        f"No parser found for file extension: {extension}. "
        f"Supported extensions: {', '.join(_get_all_extensions())}"
    )


def _get_all_extensions():
    """Get all supported extensions from all parsers."""
    extensions = []
    test_extensions = [".docx", ".html", ".htm", ".tex", ".latex"]
    for ext in test_extensions:
        for parser_class in PARSERS.values():
            parser = parser_class()
            if parser.supports_extension(ext) and ext not in extensions:
                extensions.append(ext)
    return extensions


__all__ = [
    "BaseParser",
    "DocxParser",
    "HTMLParser",
    "LaTeXParser",
    "PARSERS",
    "get_parser",
    "detect_parser",
]
