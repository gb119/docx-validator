# Document Format Support

The docx-tex-validator now supports multiple document formats beyond just Microsoft Word DOCX files. The tool can validate HTML and LaTeX documents using the same specification files.

## Supported Formats

- **DOCX** (`.docx`) - Microsoft Word documents
- **HTML** (`.html`, `.htm`) - HTML web pages
- **LaTeX** (`.tex`, `.latex`) - LaTeX documents

## How It Works

The validator uses a pluggable parser architecture that automatically detects the document format based on the file extension. Each parser extracts relevant structure and metadata from the document, which is then validated against your specifications using the LLM.

## Usage

### Auto-Detection

By default, the validator automatically detects the document format from the file extension:

```bash
# Validate a DOCX file
doc_validator validate document.docx -s specs.json

# Validate an HTML file
doc_validator validate document.html -s specs.json

# Validate a LaTeX file
doc_validator validate document.tex -s specs.json
```

### Explicit Parser Selection

You can also explicitly specify which parser to use with the `-p` or `--parser` option:

```bash
# Force HTML parser
doc_validator validate document.html -p html -s specs.json

# Force LaTeX parser
doc_validator validate document.tex -p latex -s specs.json
```

## Python API

### Using Specific Parsers

```python
from docx_tex_validator import DocxValidator, ValidationSpec

# Validate HTML document
validator = DocxValidator(parser="html")
specs = [ValidationSpec(name="Has Title", description="Document must have a title")]
report = validator.validate("document.html", specs)

# Validate LaTeX document
validator = DocxValidator(parser="latex")
report = validator.validate("document.tex", specs)
```

### Auto-Detection

```python
from docx_tex_validator import DocxValidator, ValidationSpec

# Parser is auto-detected from file extension
validator = DocxValidator()
specs = [ValidationSpec(name="Has Title", description="Document must have a title")]

# Works with any supported format
report = validator.validate("document.docx", specs)  # Uses DocxParser
report = validator.validate("document.html", specs)  # Uses HTMLParser
report = validator.validate("document.tex", specs)   # Uses LaTeXParser
```

### Using Parsers Directly

You can also use the parsers directly to extract document structure without validation:

```python
from docx_tex_validator.parsers import HTMLParser, LaTeXParser, detect_parser

# Use a specific parser
html_parser = HTMLParser()
structure = html_parser.parse("document.html")
print(structure["metadata"]["title"])

# Auto-detect parser
parser = detect_parser("document.tex")
structure = parser.parse("document.tex")
```

## Extracted Information

### DOCX Documents

- Paragraphs with styles and formatting
- Tables with cell contents
- Sections with page layout
- Headers and footers
- Metadata (title, author, subject, dates)
- Document styles
- Raw XML content for advanced validation

### HTML Documents

- Title and meta tags
- Headings (h1-h6) with hierarchy
- Paragraphs
- Tables with structure
- Lists (ordered and unordered)
- Raw HTML content

### LaTeX Documents

- Document class
- Metadata (title, author, date)
- Sections, subsections, and chapters
- Figures with captions and labels
- Tables with captions and labels
- Equations with labels
- Citations and bibliography information
- Packages used
- Raw LaTeX content

## Writing Format-Agnostic Specifications

Since different formats have different structures, you may want to write specifications that work across formats:

```json
[
  {
    "name": "Has Title",
    "description": "Document must contain a title (in metadata for DOCX, <title> tag for HTML, \\title command for LaTeX)",
    "category": "metadata"
  },
  {
    "name": "Has Sections",
    "description": "Document must have multiple sections or headings to organize content",
    "category": "structure"
  },
  {
    "name": "Contains Tables",
    "description": "Document should include at least one table",
    "category": "content"
  }
]
```

The LLM-based validation understands the structure differences and validates appropriately for each format.

## Example Files

The `examples/` directory contains sample documents in different formats:

- `sample_document.html` - Sample HTML document
- `sample_document.tex` - Sample LaTeX document

You can use these to test the validator with different formats.

## Extending with New Formats

The parser architecture is designed to be extensible. To add support for new document formats:

1. Create a new parser class that inherits from `BaseParser`
2. Implement the `parse()` and `supports_extension()` methods
3. Register the parser in `docx_tex_validator/parsers/__init__.py`

See the existing parsers for examples.
