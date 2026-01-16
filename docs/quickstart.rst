Quick Start
===========

Command-Line Usage
------------------

Initialize a Specification File
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Create a template specification file:

.. code-block:: bash

   docx-validator init-spec specifications.json

This creates a JSON file with example specifications that you can customize.

Validate a Document
~~~~~~~~~~~~~~~~~~~

Validate a document against a specification file:

.. code-block:: bash

   export GITHUB_TOKEN="your_github_token"
   docx-validator validate document.docx --spec-file specifications.json

Use Inline Specifications
~~~~~~~~~~~~~~~~~~~~~~~~~~

You can also provide specifications directly on the command line:

.. code-block:: bash

   docx-validator validate document.docx \
     -r "Has Title:Document must have a title in metadata" \
     -r "Has Author:Document must have an author"

Save Results to a File
~~~~~~~~~~~~~~~~~~~~~~

Save validation results to a JSON file:

.. code-block:: bash

   docx-validator validate document.docx -s specs.json -o results.json -v

Python Library Usage
--------------------

Basic Example
~~~~~~~~~~~~~

.. code-block:: python

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

Custom Model Configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Use a custom OpenAI-compatible model:

.. code-block:: python

   from docx_validator import DocxValidator
   import os

   # Set environment variables for custom endpoint
   os.environ["OPENAI_API_KEY"] = "your_api_key"
   os.environ["OPENAI_BASE_URL"] = "https://api.openai.com/v1"

   validator = DocxValidator(model_name="gpt-4")

Working with Validation Results
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Get detailed results
   report = validator.validate("document.docx", specs)

   # Access individual results
   for result in report.results:
       print(f"Specification: {result.spec_name}")
       print(f"Passed: {result.passed}")
       print(f"Confidence: {result.confidence:.2f}")
       print(f"Reasoning: {result.reasoning}")
       print()

   # Get summary statistics
   print(f"Total specs: {report.total_specs}")
   print(f"Passed: {report.passed_count}")
   print(f"Failed: {report.failed_count}")
   print(f"Score: {report.score:.2%}")
