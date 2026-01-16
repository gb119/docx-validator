# docx-validator

A Python library and command-line tool that uses LLMs (via GitHub Models and pydantic-ai) to validate Microsoft Word .docx files against specification requirements.

📚 **[Read the Documentation](https://gb119.github.io/docx-validator/)**

## Features

- 🤖 **LLM-Powered Validation**: Uses GitHub Models through pydantic-ai for intelligent document analysis
- 📄 **Document Structure Analysis**: Extracts and analyzes document structure, styles, tables, metadata, and more
- ✅ **Specification-Based Validation**: Define custom validation requirements for your documents
- 📊 **Normalized Results**: Returns True/False validation results with numerical scoring
- 🖥️ **CLI and Library**: Use as a command-line tool or integrate into your Python projects
- 📦 **Easy Distribution**: GitHub Actions workflows for building wheel and conda packages

## Installation

### From PyPI (once published)

```bash
pip install docx-validator
```

### From Source

```bash
git clone https://github.com/gb119/docx-validator.git
cd docx-validator
pip install -e .
```

### Using Conda (once published)

```bash
conda install -c conda-forge docx-validator
```

## Quick Start

### Command-Line Usage

1. **Create a specification file:**

```bash
docx-validator init-spec specifications.json
```

2. **Validate a document:**

```bash
export GITHUB_TOKEN="your_github_token"
docx-validator validate document.docx --spec-file specifications.json
```

3. **Use inline specifications:**

```bash
docx-validator validate document.docx \
  -r "Has Title:Document must have a title in metadata" \
  -r "Has Author:Document must have an author"
```

4. **Save results to a file:**

```bash
docx-validator validate document.docx -s specs.json -o results.json -v
```

### Python Library Usage

```python
from docx_validator import DocxValidator, ValidationSpec

# Create validator (uses GITHUB_TOKEN environment variable)
validator = DocxValidator(model_name="gpt-4o-mini")

# Define specifications
specs = [
    ValidationSpec(
        name="Has Title",
        description="Document must contain a title in the metadata"
    ),
    ValidationSpec(
        name="Uses Heading Styles",
        description="Document must use heading styles (Heading 1, Heading 2, etc.)"
    ),
]

# Validate document
report = validator.validate("document.docx", specs)

# Check results
print(f"Score: {report.score:.2%}")
print(f"Passed: {report.passed_count}/{report.total_specs}")

for result in report.results:
    print(f"{result.spec_name}: {'✓' if result.passed else '✗'}")
    if result.reasoning:
        print(f"  Reasoning: {result.reasoning}")
```

## Configuration

### GitHub Models API

By default, `docx-validator` uses GitHub Models for LLM inference. You need to:

1. Get a GitHub token with access to GitHub Models
2. Set it as an environment variable:

```bash
export GITHUB_TOKEN="your_github_token"
```

### Custom OpenAI-Compatible Endpoints

You can use any OpenAI-compatible API:

```python
validator = DocxValidator(
    model_name="gpt-4",
    api_key="your_api_key",
    base_url="https://api.openai.com/v1"
)
```

## Specification Format

Specifications can be provided as JSON files:

```json
[
  {
    "name": "Has Title",
    "description": "Document must contain a title in the metadata",
    "category": "metadata"
  },
  {
    "name": "Has Headings",
    "description": "Document must use heading styles (Heading 1, Heading 2, etc.)",
    "category": "structure"
  },
  {
    "name": "Has Table of Contents",
    "description": "Document should include a table of contents",
    "category": "structure"
  }
]
```

## Validation Report

The validation report includes:

- **file_path**: Path to the validated document
- **results**: List of individual validation results
  - **spec_name**: Name of the specification
  - **passed**: Boolean indicating if validation passed
  - **confidence**: Confidence score (0.0-1.0)
  - **reasoning**: Explanation from the LLM
- **total_specs**: Total number of specifications
- **passed_count**: Number of passed validations
- **failed_count**: Number of failed validations
- **score**: Numerical score (passed_count / total_specs)

## Development

### Setup Development Environment

```bash
git clone https://github.com/gb119/docx-validator.git
cd docx-validator
pip install -e ".[dev]"
```

### Running Tests

```bash
pytest
```

### Code Formatting

```bash
ruff check .
ruff format .
```

## GitHub Actions

The project includes two GitHub Actions workflows:

1. **build-wheel.yml**: Builds Python wheel packages on tag push
2. **build-conda.yml**: Builds conda packages for multiple platforms and Python versions

To trigger a release:

```bash
git tag v0.1.0
git push origin v0.1.0
```

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Author

GB119
