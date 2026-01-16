Installation
============

From PyPI
---------

Once published, you can install docx-validator from PyPI:

.. code-block:: bash

   pip install docx-validator

From Source
-----------

To install from source:

.. code-block:: bash

   git clone https://github.com/gb119/docx-validator.git
   cd docx-validator
   pip install -e .

For development, install with the development dependencies:

.. code-block:: bash

   pip install -e ".[dev]"

For documentation building, install with the docs dependencies:

.. code-block:: bash

   pip install -e ".[docs]"

Using Conda
-----------

Once published to conda-forge, you can install using conda:

.. code-block:: bash

   conda install -c conda-forge docx-validator

Requirements
------------

- Python >= 3.9
- pydantic-ai >= 0.0.1
- python-docx >= 1.0.0
- click >= 8.0.0
- pydantic >= 2.0.0

Configuration
-------------

GitHub Models API
~~~~~~~~~~~~~~~~~

By default, ``docx-validator`` uses GitHub Models for LLM inference. You need to:

1. Get a GitHub token with access to GitHub Models
2. Set it as an environment variable:

.. code-block:: bash

   export GITHUB_TOKEN="your_github_token"

Custom OpenAI-Compatible Endpoints
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You can use any OpenAI-compatible API by setting environment variables:

.. code-block:: bash

   export OPENAI_API_KEY="your_api_key"
   export OPENAI_BASE_URL="https://api.openai.com/v1"

Or by passing parameters when creating the validator:

.. code-block:: python

   from docx_validator import DocxValidator

   validator = DocxValidator(
       model_name="gpt-4",
       api_key="your_api_key"
   )
