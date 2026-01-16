"""
Base parser interface for document parsing.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict


class BaseParser(ABC):
    """
    Abstract base class for document parsers.

    This defines the interface that all parser implementations must follow.
    """

    @abstractmethod
    def parse(self, file_path: str) -> Dict[str, Any]:
        """
        Parse a document file and extract its structure and content information.

        Args:
            file_path: Path to the document file

        Returns:
            Dictionary containing document structure information with at least:
                - file_path: str - Path to the document
                - metadata: dict - Document metadata (title, author, etc.)
                - content: Any - Parsed content structure

        Raises:
            FileNotFoundError: If the file doesn't exist
            ValueError: If the file is not valid for this parser
        """
        pass

    @abstractmethod
    def supports_extension(self, extension: str) -> bool:
        """
        Check if this parser supports the given file extension.

        Args:
            extension: File extension to check (e.g., '.docx', '.html', '.tex')

        Returns:
            True if this parser supports the extension, False otherwise
        """
        pass

    def validate_file(self, file_path: str) -> None:
        """
        Validate that the file exists and has a supported extension.

        Args:
            file_path: Path to the file to validate

        Raises:
            FileNotFoundError: If the file doesn't exist
            ValueError: If the file extension is not supported
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        if not self.supports_extension(path.suffix.lower()):
            raise ValueError(
                f"File extension {path.suffix} is not supported by {self.__class__.__name__}"
            )
