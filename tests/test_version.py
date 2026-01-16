"""
Tests for version consistency across the package.
"""

import re
from pathlib import Path


def _get_version_from_init():
    """Helper function to extract version from __init__.py."""
    init_path = Path(__file__).parent.parent / "docx_validator" / "__init__.py"
    init_content = init_path.read_text()

    # Extract __version__ value
    version_match = re.search(r'__version__\s*=\s*["\']([^"\']+)["\']', init_content)
    if version_match is None:
        raise ValueError("__version__ not found in __init__.py")

    return version_match.group(1)


def test_version_defined():
    """Test that __version__ is defined in the package."""
    version = _get_version_from_init()

    assert version is not None
    assert len(version) > 0


def test_version_format():
    """Test that version follows semantic versioning format."""
    version = _get_version_from_init()

    # Simple semantic versioning pattern
    pattern = r"^\d+\.\d+\.\d+(?:-[a-zA-Z0-9.]+)?(?:\+[a-zA-Z0-9.]+)?$"
    assert re.match(pattern, version), f"Version '{version}' does not match semantic versioning"


def test_cli_uses_package_version():
    """Test that CLI imports version from the package."""
    # Read cli.py to check it imports __version__
    cli_path = Path(__file__).parent.parent / "docx_validator" / "cli.py"
    cli_content = cli_path.read_text()

    # Check that cli.py imports __version__
    assert (
        "from . import __version__" in cli_content
        or "from docx_validator import __version__" in cli_content
    )
    # Check that cli.py uses __version__ instead of a hardcoded string
    assert "@click.version_option(version=__version__)" in cli_content


def test_docs_conf_imports_version():
    """Test that docs/conf.py imports version from the package."""
    docs_conf_path = Path(__file__).parent.parent / "docs" / "conf.py"
    conf_content = docs_conf_path.read_text()

    # Check that conf.py imports __version__
    assert "from docx_validator import __version__" in conf_content
    # Check that it uses __version__ for release and version
    assert "release = __version__" in conf_content
    assert "version = __version__" in conf_content


def test_pyproject_uses_dynamic_version():
    """Test that pyproject.toml uses dynamic versioning."""
    pyproject_path = Path(__file__).parent.parent / "pyproject.toml"
    pyproject_content = pyproject_path.read_text()

    # Check that version is in the dynamic list using regex
    dynamic_version_pattern = r'dynamic\s*=\s*\[.*["\']version["\'].*\]'
    assert re.search(dynamic_version_pattern, pyproject_content), (
        "Version should be in the dynamic list in [project] section"
    )

    # Check that version is NOT hardcoded in [project] section
    lines = pyproject_content.split("\n")
    in_project_section = False
    for line in lines:
        if line.strip() == "[project]":
            in_project_section = True
        elif line.strip().startswith("[") and line.strip() != "[project]":
            in_project_section = False
        elif in_project_section and re.match(r'^\s*version\s*=\s*["\']', line):
            assert False, "Version should not be hardcoded in [project] section"

    # Check that setuptools.dynamic configuration exists
    assert "[tool.setuptools.dynamic]" in pyproject_content
    setuptools_dynamic_pattern = r"version\s*=\s*\{.*attr.*docx_validator\.__version__.*\}"
    assert re.search(setuptools_dynamic_pattern, pyproject_content), (
        "setuptools.dynamic should configure version from docx_validator.__version__"
    )


if __name__ == "__main__":
    import pytest

    pytest.main([__file__, "-v"])
