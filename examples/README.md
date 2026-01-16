# Example Specification Files

This directory contains example specification files that can be used with docx-validator to validate different aspects of Word documents.

## Available Specification Files

### 1. `sample_specifications.json`
A basic set of validation specifications covering:
- Document metadata (title, author)
- Basic structure (headings, paragraphs)
- Page layout

**Usage:**
```bash
docx-validator validate document.docx --spec-file examples/sample_specifications.json
```

### 2. `structured_document_specifications.json`
A comprehensive specification file for validating well-structured academic or technical documents. This specification validates:

#### Document Structure
- **Title with Proper Style**: Validates that the document has a properly formatted title using Word's Title or Heading 1 style
- **Heading Styles for Structure**: Ensures the document uses proper heading hierarchy (Heading 1, 2, 3, etc.) demonstrating use of Word's style function

#### Figures
- **Figure with Numbered Caption**: Validates presence of figures with captions created using Word's Insert Caption function (format: "Figure X: Description")
- **Cross-Reference to Figure**: Ensures figures are referenced in the text using Word's Cross-Reference function for automatic linking

#### Tables
- **Table with Numbered Caption**: Validates presence of tables with captions created using Word's Insert Caption function (format: "Table X: Description")
- **Cross-Reference to Table**: Ensures tables are referenced in the text using Word's Cross-Reference function for automatic linking

#### Equations
- **Numbered Equation on Own Line**: Validates presence of equations positioned on their own line, numbered using Word's Insert Caption function
- **Cross-Reference to Equation**: Ensures equations are referenced in the text using Word's Cross-Reference function for automatic linking

#### Formatting
- **Page Numbers**: Validates that the document has page numbers added using Word's Insert Page Number function, visible in the header or footer

#### References
- **At Least 5 References**: Validates presence of at least 5 references listed under a 'References' or 'Bibliography' heading, formatted in either Harvard (author-date) or Numeric (numbered) style
- **Properly Formatted In-Text Citations**: Ensures in-text citations are properly formatted and match the reference style, ideally created using EndNote or Word's Citation & Bibliography tools

**Usage:**
```bash
docx-validator validate document.docx --spec-file examples/structured_document_specifications.json
```

## Creating Custom Specifications

You can create your own specification files by following the JSON format:

```json
[
  {
    "name": "Your Specification Name",
    "description": "Detailed description of what to validate",
    "category": "optional_category"
  }
]
```

### Tips for Writing Good Specifications

1. **Be Specific**: Clearly describe what you're looking for in the document
2. **Use Categories**: Group related specifications together using the category field
3. **Focus on Structure**: The validator analyzes document structure, styles, and metadata rather than content quality
4. **Mention Tools**: When validating features created with specific Word functions (Insert Caption, Cross-Reference, etc.), mention them in the description

## Generating a Starter Specification File

Use the CLI to generate a basic specification file:

```bash
docx-validator init-spec my_specifications.json
```

This will create a file with basic validation requirements that you can customize.
