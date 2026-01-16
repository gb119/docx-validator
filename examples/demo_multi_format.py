"""
Demo script showing multi-format document validation.

This script demonstrates how to validate documents in different formats
(HTML and LaTeX) using the same specification file.

Note: This demo uses mock backend to avoid requiring API keys.
"""

from unittest.mock import Mock

from docx_validator import DocxValidator, ValidationSpec

# Define format-agnostic specifications
specs = [
    ValidationSpec(
        name="Has Title",
        description="Document must contain a title in metadata or title element",
        category="metadata",
    ),
    ValidationSpec(
        name="Has Author",
        description="Document must specify an author",
        category="metadata",
    ),
    ValidationSpec(
        name="Has Multiple Sections",
        description="Document must be organized with multiple sections or headings",
        category="structure",
    ),
]

print("=" * 70)
print("Multi-Format Document Validation Demo")
print("=" * 70)
print()

# Validate HTML document
print("1. Validating HTML document (sample_document.html)...")
print("-" * 70)

html_validator = DocxValidator(parser="html", api_key="demo_key")

# Mock the backend to avoid API calls
mock_response = Mock()
mock_response.data = "Result: PASS\nConfidence: 0.95\nReasoning: Document meets requirements"
mock_response.all_messages = Mock(return_value=[])
html_validator.backend.run_sync = Mock(return_value=mock_response)

try:
    html_report = html_validator.validate("examples/sample_document.html", specs)
    print(f"✓ HTML validation completed")
    print(f"  File: {html_report.file_path}")
    print(f"  Total specs: {html_report.total_specs}")
    print(f"  Parser detected: HTMLParser")
except Exception as e:
    print(f"✗ Error: {e}")

print()

# Validate LaTeX document
print("2. Validating LaTeX document (sample_document.tex)...")
print("-" * 70)

latex_validator = DocxValidator(parser="latex", api_key="demo_key")

# Mock the backend to avoid API calls
latex_validator.backend.run_sync = Mock(return_value=mock_response)

try:
    latex_report = latex_validator.validate("examples/sample_document.tex", specs)
    print(f"✓ LaTeX validation completed")
    print(f"  File: {latex_report.file_path}")
    print(f"  Total specs: {latex_report.total_specs}")
    print(f"  Parser detected: LaTeXParser")
except Exception as e:
    print(f"✗ Error: {e}")

print()

# Demonstrate auto-detection
print("3. Auto-detection demo...")
print("-" * 70)

from docx_validator.parsers import detect_parser

for file_path in ["examples/sample_document.html", "examples/sample_document.tex"]:
    parser = detect_parser(file_path)
    print(f"✓ {file_path} → {parser.__class__.__name__}")

print()
print("=" * 70)
print("Demo completed!")
print()
print("Key Features Demonstrated:")
print("  • Same specifications work across multiple formats")
print("  • Explicit parser selection with parser='html' or parser='latex'")
print("  • Auto-detection from file extension")
print("  • Consistent API across all document formats")
print()
print("For actual validation with LLM, set API keys:")
print("  export OPENAI_API_KEY=your_key")
print("  docx-validator validate document.html -s specs.json")
print("=" * 70)
