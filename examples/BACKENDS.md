# Backend Examples for docx-validator

This directory contains examples of using different AI backends with docx-validator.

## Quick Examples

### Using OpenAI

```python
from docx_validator import DocxValidator, ValidationSpec

# Create validator with OpenAI backend
validator = DocxValidator(
    backend="openai",
    model_name="gpt-4o-mini",
    api_key="your_openai_api_key"
)

specs = [
    ValidationSpec(
        name="Has Title",
        description="Document must contain a title in the metadata"
    )
]

report = validator.validate("document.docx", specs)
print(f"Validation score: {report.score:.2%}")
```

### Using GitHub Models

```python
from docx_validator import DocxValidator, ValidationSpec

# Create validator with GitHub Models backend
validator = DocxValidator(
    backend="github",
    model_name="gpt-4o-mini",
    api_key="your_github_token"
)

# Use as above
```

### Using NebulaOne

```python
from docx_validator import DocxValidator, ValidationSpec

# Create validator with NebulaOne backend
validator = DocxValidator(
    backend="nebulaone",
    model_name="nebula-1",
    api_key="your_nebulaone_api_key",
    base_url="https://api.nebulaone.example"
)

# Use as above
```

## Command Line Examples

### OpenAI
```bash
export OPENAI_API_KEY="your_openai_api_key"
docx-validator validate document.docx -s specs.json
```

### GitHub Models
```bash
export GITHUB_TOKEN="your_github_token"
docx-validator validate document.docx -b github -s specs.json
```

### NebulaOne
```bash
export NEBULAONE_API_KEY="your_nebulaone_api_key"
export NEBULAONE_BASE_URL="https://api.nebulaone.example"
docx-validator validate document.docx -b nebulaone -m nebula-1 -s specs.json
```

## Creating Custom Backends

You can create custom backends by extending the `BaseBackend` class:

```python
from docx_validator.backends import BaseBackend
from pydantic_ai import Agent

class MyCustomBackend(BaseBackend):
    def __init__(self, model_name: str, api_key: str = None, **kwargs):
        super().__init__(model_name, api_key, **kwargs)
        # Initialize your custom model here
    
    def get_agent(self, system_prompt: str) -> Agent:
        # Return a configured agent
        pass
    
    def run_sync(self, agent: Agent, prompt: str) -> str:
        # Run inference and return response
        pass
    
    @property
    def name(self) -> str:
        return "my_custom_backend"
```

Then use it:

```python
from docx_validator import DocxValidator

validator = DocxValidator(backend=MyCustomBackend())
```
