Development
===========

Setting Up Development Environment
-----------------------------------

Clone the repository and install development dependencies:

.. code-block:: bash

   git clone https://github.com/gb119/docx-validator.git
   cd docx-validator
   pip install -e ".[dev]"

This installs the package in editable mode with development tools including:

- pytest for testing
- pytest-cov for coverage reports
- ruff for linting and formatting

Running Tests
-------------

Run all tests:

.. code-block:: bash

   pytest

Run tests with coverage:

.. code-block:: bash

   pytest --cov=docx_validator --cov-report=html

View coverage report:

.. code-block:: bash

   open htmlcov/index.html  # macOS
   xdg-open htmlcov/index.html  # Linux
   start htmlcov/index.html  # Windows

Code Quality
------------

Linting
~~~~~~~

Check code style with ruff:

.. code-block:: bash

   ruff check .

Formatting
~~~~~~~~~~

Format code with ruff:

.. code-block:: bash

   ruff format .

Configuration
~~~~~~~~~~~~~

Ruff is configured in ``pyproject.toml``:

- Line length: 100 characters
- Target Python version: 3.9+
- Selected rules: E (errors), F (pyflakes), I (isort), N (naming), W (warnings)

Building Documentation
----------------------

Install documentation dependencies:

.. code-block:: bash

   pip install -e ".[docs]"

Build the documentation:

.. code-block:: bash

   cd docs
   sphinx-build -b html . _build/html

View the documentation:

.. code-block:: bash

   open _build/html/index.html  # macOS
   xdg-open _build/html/index.html  # Linux
   start _build/html/index.html  # Windows

Or use the simpler make command (on Unix-like systems):

.. code-block:: bash

   cd docs
   make html
   open _build/html/index.html

Clean build artifacts:

.. code-block:: bash

   cd docs
   make clean

Release Process
---------------

Building Packages
~~~~~~~~~~~~~~~~~

Wheel Package
^^^^^^^^^^^^^

The project uses GitHub Actions to build wheel packages automatically when a tag is pushed:

.. code-block:: bash

   git tag v0.1.0
   git push origin v0.1.0

This triggers the ``build-wheel.yml`` workflow which:

1. Builds the wheel and source distribution
2. Checks the distribution with twine
3. Uploads artifacts
4. Creates a GitHub release

Conda Package
^^^^^^^^^^^^^

The ``build-conda.yml`` workflow builds conda packages for multiple platforms:

- Ubuntu, Windows, and macOS
- Python 3.9, 3.10, 3.11, and 3.12
- Uses mamba for faster environment resolution
- Automatically uploads to the phygbu channel on anaconda.org

To trigger:

.. code-block:: bash

   git tag v0.1.0
   git push origin v0.1.0

**Required Secrets:**

The conda build workflow requires the following secret to be configured in GitHub repository settings:

- ``ANACONDA_TOKEN``: An anaconda.org API token with permission to upload packages to the phygbu channel

To create an anaconda token:

1. Log in to anaconda.org
2. Go to Settings → Access
3. Create a new token with "Allow write access to the API site" permission
4. Add the token as ``ANACONDA_TOKEN`` in GitHub repository secrets (Settings → Secrets and variables → Actions)

Manual Building
~~~~~~~~~~~~~~~

Build wheel locally:

.. code-block:: bash

   python -m pip install build
   python -m build

Build conda package locally:

.. code-block:: bash

   # Using conda
   conda install conda-build
   conda build conda-recipe

   # Or using mamba (faster)
   mamba install conda-build
   mamba build conda-recipe

Version Bumping
~~~~~~~~~~~~~~~

Update version in:

1. ``pyproject.toml`` - ``version`` field
2. ``docx_validator/__init__.py`` - ``__version__`` variable
3. ``docs/conf.py`` - ``release`` and ``version`` variables

Project Structure
-----------------

.. code-block:: text

   docx-validator/
   ├── .github/
   │   └── workflows/          # GitHub Actions workflows
   │       ├── build-conda.yml
   │       ├── build-wheel.yml
   │       └── docs.yml        # Documentation build and deploy
   ├── docs/                   # Sphinx documentation
   │   ├── conf.py
   │   ├── index.rst
   │   └── ...
   ├── docx_validator/         # Main package
   │   ├── __init__.py
   │   ├── cli.py             # Command-line interface
   │   ├── parser.py          # Document parser
   │   └── validator.py       # Core validation logic
   ├── examples/              # Example documents and specs
   ├── tests/                 # Test suite
   │   ├── __init__.py
   │   └── test_validator.py
   ├── .gitignore
   ├── LICENSE
   ├── README.md
   └── pyproject.toml         # Project configuration

Contributing
------------

Contributions are welcome! Here's how to contribute:

1. Fork the repository
2. Create a feature branch (``git checkout -b feature/my-feature``)
3. Make your changes
4. Run tests and linting
5. Commit your changes (``git commit -am 'Add new feature'``)
6. Push to the branch (``git push origin feature/my-feature``)
7. Create a Pull Request

Guidelines
~~~~~~~~~~

- Follow the existing code style
- Add tests for new features
- Update documentation as needed
- Keep commits focused and atomic
- Write clear commit messages

License
-------

This project is licensed under the MIT License. See the LICENSE file for details.
