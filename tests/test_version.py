"""
Tests for version consistency across the package.
"""

import re
import sys
from pathlib import Path


def test_version_defined():
    """Test that __version__ is defined in the package."""
    # Read __version__ directly from __init__.py to avoid import issues
    init_path = Path(__file__).parent.parent / "docx_validator" / "__init__.py"
    init_content = init_path.read_text()
    
    # Extract __version__ value
    version_match = re.search(r'__version__\s*=\s*["\']([^"\']+)["\']', init_content)
    assert version_match is not None, "__version__ not found in __init__.py"
    
    version = version_match.group(1)
    assert version is not None
    assert len(version) > 0


def test_version_format():
    """Test that version follows semantic versioning format."""
    # Read __version__ directly from __init__.py to avoid import issues
    init_path = Path(__file__).parent.parent / "docx_validator" / "__init__.py"
    init_content = init_path.read_text()
    
    # Extract __version__ value
    version_match = re.search(r'__version__\s*=\s*["\']([^"\']+)["\']', init_content)
    assert version_match is not None, "__version__ not found in __init__.py"
    
    version = version_match.group(1)
    
    # Simple semantic versioning pattern
    pattern = r'^\d+\.\d+\.\d+(?:-[a-zA-Z0-9.]+)?(?:\+[a-zA-Z0-9.]+)?$'
    assert re.match(pattern, version), f"Version '{version}' does not match semantic versioning"


def test_cli_uses_package_version():
    """Test that CLI imports version from the package."""
    # Read cli.py to check it imports __version__
    cli_path = Path(__file__).parent.parent / "docx_validator" / "cli.py"
    cli_content = cli_path.read_text()
    
    # Check that cli.py imports __version__
    assert "from . import __version__" in cli_content or "from docx_validator import __version__" in cli_content
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
    
    # Check that version is in the dynamic list
    assert 'dynamic = ["version"]' in pyproject_content or "dynamic = ['version']" in pyproject_content
    # Check that version is NOT hardcoded in [project]
    # We'll check there's no line like: version = "0.1.0" in [project] section
    lines = pyproject_content.split('\n')
    in_project_section = False
    for line in lines:
        if line.strip() == '[project]':
            in_project_section = True
        elif line.strip().startswith('[') and line.strip() != '[project]':
            in_project_section = False
        elif in_project_section and line.strip().startswith('version = '):
            assert False, "Version should not be hardcoded in [project] section"
    
    # Check that setuptools.dynamic configuration exists
    assert '[tool.setuptools.dynamic]' in pyproject_content
    assert 'version = {attr = "docx_validator.__version__"}' in pyproject_content


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])
