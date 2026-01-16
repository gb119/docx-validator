"""
Module for parsing .docx files and extracting document structure information.

This module is maintained for backward compatibility.
New code should use the parsers package instead.
"""

# Import from new location for backward compatibility
from .parsers.docx_parser import DocxParser

__all__ = ["DocxParser"]
