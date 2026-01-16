# docx-validator

A Python library and command-line tool that uses LLMs to validate Microsoft Word .docx files against specification requirements. Supports multiple AI backends including OpenAI, GitHub Models, and NebulaOne.

📚 **[Read the Documentation](https://gb119.github.io/docx-validator/)**

## Features

- 🤖 **Multiple AI Backends**: Supports OpenAI, GitHub Models, and NebulaOne for flexible deployment
- 📄 **Document Structure Analysis**: Extracts and analyzes document structure, styles, tables, metadata, and more
- ✅ **Specification-Based Validation**: Define custom validation requirements for your documents
- 📊 **Normalized Results**: Returns True/False validation results with numerical scoring
- 🖥️ **CLI and Library**: Use as a command-line tool or integrate into your Python projects
- 🔌 **Pluggable Architecture**: Easy to extend with custom AI backends
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
conda install -c phygbu docx-validator
```

## Quick Start

### Command-Line Usage

1. **Create a specification file:**

```bash
docx-validator init-spec specifications.json
```

2. **Validate a document (using default OpenAI backend):**

```bash
export OPENAI_API_KEY="your_openai_api_key"
docx-validator validate document.docx --spec-file specifications.json
```

3. **Use GitHub Models:**

```bash
export GITHUB_TOKEN="your_github_token"
docx-validator validate document.docx -b github -s specifications.json
```

4. **Use NebulaOne:**

```bash
export NEBULAONE_API_KEY="your_nebulaone_api_key"
export NEBULAONE_BASE_URL="https://api.nebulaone.example"
docx-validator validate document.docx -b nebulaone -m nebula-1 -s specifications.json
```

5. **Use inline specifications:**

```bash
docx-validator validate document.docx \
  -r "Has Title:Document must have a title in metadata" \
  -r "Has Author:Document must have an author"
```

6. **Save results to a file:**

```bash
docx-validator validate document.docx -s specs.json -o results.json -v
```

### Python Library Usage

#### Using OpenAI (default)

```python
from docx_validator import DocxValidator, ValidationSpec

# Create validator with OpenAI backend (default)
validator = DocxValidator(
    backend="openai",
    model_name="gpt-4o-mini",
    api_key="your_openai_api_key"
)

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

#### Using GitHub Models

```python
from docx_validator import DocxValidator, ValidationSpec

# Create validator with GitHub Models backend
validator = DocxValidator(
    backend="github",
    model_name="gpt-4o-mini",
    api_key="your_github_token"
)

# Use as shown above
```

#### Using NebulaOne

```python
from docx_validator import DocxValidator, ValidationSpec

# Create validator with NebulaOne backend
validator = DocxValidator(
    backend="nebulaone",
    model_name="nebula-1",
    api_key="your_nebulaone_api_key",
    base_url="https://api.nebulaone.example"
)

# Use as shown above
```

## Configuration

### Supported Backends

docx-validator supports multiple AI backends:

1. **OpenAI** (`backend="openai"`): Direct OpenAI API access
2. **GitHub Models** (`backend="github"`): GitHub's AI model service
3. **NebulaOne** (`backend="nebulaone"`): NebulaOne AI service

### Environment Variables

Different backends use different environment variables for configuration:

#### OpenAI Backend

```bash
export OPENAI_API_KEY="your_openai_api_key"
# Optional: Custom endpoint
export OPENAI_BASE_URL="https://api.openai.com/v1"
```

#### GitHub Models Backend

```bash
export GITHUB_TOKEN="your_github_token"
# Optional: Custom endpoint (defaults to GitHub Models)
export OPENAI_BASE_URL="https://models.inference.ai.azure.com"
```

#### NebulaOne Backend

```bash
export NEBULAONE_API_KEY="your_nebulaone_api_key"
export NEBULAONE_BASE_URL="https://api.nebulaone.example"
```

### Custom Backend Configuration

You can pass any custom configuration to a backend:

```python
validator = DocxValidator(
    backend="openai",
    model_name="gpt-4",
    api_key="your_api_key",
    base_url="https://api.openai.com/v1",
    # Additional backend-specific options
    temperature=0.7,
    max_tokens=2000
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

### Example Specifications

The `examples/` directory contains ready-to-use specification files:

- **`sample_specifications.json`**: Basic document validation (metadata, headings, layout)
- **`structured_document_specifications.json`**: Comprehensive validation for academic/technical documents including:
  - Title and heading structure with proper styles
  - Figures with captions (using Insert Caption function)
  - Cross-references to figures
  - Tables with captions (using Insert Caption function)
  - Cross-references to tables
  - Numbered equations on their own line
  - Cross-references to equations

See `examples/README.md` for detailed information about each specification file.

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

The project includes three GitHub Actions workflows:

1. **build-wheel.yml**: Builds Python wheel packages on tag push
2. **build-conda.yml**: Builds conda packages for multiple platforms and Python versions
   - Uses mamba for faster environment resolution
   - Automatically uploads to the phygbu channel on anaconda.org when tags are pushed
   - Requires `ANACONDA_TOKEN` secret to be configured in repository settings
3. **docs.yml**: Builds and deploys documentation

To trigger a release:

```bash
git tag v0.1.0
git push origin v0.1.0
```

This will build both wheel and conda packages, and upload them to PyPI (if configured) and the phygbu anaconda channel.

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Author

GB119
