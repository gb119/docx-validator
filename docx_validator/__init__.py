"""
docx-validator: A Python library for validating Microsoft Word .docx files using LLMs.
"""

from .validator import DocxValidator, ValidationResult, ValidationSpec

__version__ = "0.1.0"
__all__ = ["DocxValidator", "ValidationResult", "ValidationSpec"]
