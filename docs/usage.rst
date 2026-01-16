Usage Guide
===========

Specification Format
--------------------

Specifications define the validation requirements for your documents. They can be provided as JSON files or created programmatically.

JSON Format
~~~~~~~~~~~

Create a JSON file with an array of specification objects:

.. code-block:: json

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

Each specification has:

- ``name``: A short, unique identifier for the requirement
- ``description``: A detailed description of what to check
- ``category`` (optional): Category for organizing requirements

Programmatic Creation
~~~~~~~~~~~~~~~~~~~~~~

Create specifications in Python code:

.. code-block:: python

   from docx_validator import ValidationSpec

   specs = [
       ValidationSpec(
           name="Has Title",
           description="Document must contain a title in the metadata",
           category="metadata"
       ),
       ValidationSpec(
           name="Has Author",
           description="Document must have an author field",
           category="metadata"
       ),
   ]

Validation Report
-----------------

The validation report provides detailed information about the validation results.

Report Structure
~~~~~~~~~~~~~~~~

.. code-block:: python

   from docx_validator import ValidationReport

   # After running validation
   report = validator.validate("document.docx", specs)

   # Report attributes
   report.file_path        # Path to the validated document
   report.results          # List of ValidationResult objects
   report.total_specs      # Total number of specifications
   report.passed_count     # Number of passed validations
   report.failed_count     # Number of failed validations
   report.score            # Numerical score (0.0 to 1.0)

Validation Results
~~~~~~~~~~~~~~~~~~

Each validation result contains:

.. code-block:: python

   for result in report.results:
       result.spec_name    # Name of the specification
       result.passed       # Boolean: True if passed, False if failed
       result.confidence   # Confidence score (0.0 to 1.0)
       result.reasoning    # Explanation from the LLM

Command-Line Interface
----------------------

The CLI provides several commands for working with document validation.

validate Command
~~~~~~~~~~~~~~~~

Validate a document against specifications:

.. code-block:: bash

   docx-validator validate DOCUMENT [OPTIONS]

Options:

- ``--spec-file, -s FILE``: JSON file containing specifications
- ``-r, --requirement TEXT``: Add an inline requirement (format: "name:description")
- ``--output, -o FILE``: Save results to a JSON file
- ``--verbose, -v``: Show detailed output
- ``--model TEXT``: Model name to use (default: gpt-4o-mini)

Examples:

.. code-block:: bash

   # Validate with specification file
   docx-validator validate doc.docx -s specs.json

   # Validate with inline requirements
   docx-validator validate doc.docx \
     -r "Has Title:Document must have a title" \
     -r "Has Author:Document must have an author"

   # Save results and show verbose output
   docx-validator validate doc.docx -s specs.json -o results.json -v

   # Use a different model
   docx-validator validate doc.docx -s specs.json --model gpt-4

init-spec Command
~~~~~~~~~~~~~~~~~

Create a template specification file:

.. code-block:: bash

   docx-validator init-spec OUTPUT_FILE

This creates a JSON file with example specifications that you can customize.

Example:

.. code-block:: bash

   docx-validator init-spec my-specifications.json

Document Structure Analysis
---------------------------

The validator extracts comprehensive document structure information including:

- **Metadata**: Title, author, subject, keywords, creation date, modification date
- **Styles**: Paragraph styles and character styles used in the document
- **Structure**: Headings, paragraphs, lists, and document outline
- **Tables**: Table structure, cell content, and formatting
- **Sections**: Section breaks and page layout information
- **Properties**: Word count, paragraph count, page count

This information is passed to the LLM for analysis against your specifications.

Best Practices
--------------

Writing Effective Specifications
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

1. **Be Specific**: Clear, detailed descriptions help the LLM make accurate assessments
   
   - Good: "Document must use Heading 1 style for main sections and Heading 2 for subsections"
   - Poor: "Document should have headings"

2. **Use Categories**: Organize related requirements into categories for better reporting

3. **Test Incrementally**: Start with a few key requirements and expand gradually

4. **Review Reasoning**: Check the LLM's reasoning to understand how it's interpreting requirements

Model Selection
~~~~~~~~~~~~~~~

- **gpt-4o-mini**: Fast and cost-effective for most validation tasks (default)
- **gpt-4o**: More capable for complex document analysis
- **gpt-4**: Highest quality but slower and more expensive

Error Handling
~~~~~~~~~~~~~~

.. code-block:: python

   try:
       report = validator.validate("document.docx", specs)
       
       # Check for validation errors
       for result in report.results:
           if not result.passed and "error" in result.reasoning.lower():
               print(f"Error in {result.spec_name}: {result.reasoning}")
               
   except FileNotFoundError:
       print("Document file not found")
   except Exception as e:
       print(f"Validation error: {e}")
