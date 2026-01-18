"""
Tests for the parser abstraction and new parsers (HTML, LaTeX).
"""

import os
import tempfile

import pytest

from docx_tex_validator.parsers import (
    DocxParser,
    HTMLParser,
    LaTeXParser,
    detect_parser,
    get_parser,
)


def test_get_parser_docx():
    """Test getting a DOCX parser by name."""
    parser = get_parser("docx")
    assert isinstance(parser, DocxParser)


def test_get_parser_html():
    """Test getting an HTML parser by name."""
    parser = get_parser("html")
    assert isinstance(parser, HTMLParser)


def test_get_parser_latex():
    """Test getting a LaTeX parser by name."""
    parser = get_parser("latex")
    assert isinstance(parser, LaTeXParser)


def test_get_parser_invalid():
    """Test that get_parser raises ValueError for invalid parser name."""
    with pytest.raises(ValueError, match="Unknown parser"):
        get_parser("invalid")


def test_detect_parser_docx():
    """Test auto-detecting DOCX parser from file extension."""
    parser = detect_parser("test.docx")
    assert isinstance(parser, DocxParser)


def test_detect_parser_html():
    """Test auto-detecting HTML parser from file extension."""
    parser = detect_parser("test.html")
    assert isinstance(parser, HTMLParser)

    parser = detect_parser("test.htm")
    assert isinstance(parser, HTMLParser)


def test_detect_parser_latex():
    """Test auto-detecting LaTeX parser from file extension."""
    parser = detect_parser("test.tex")
    assert isinstance(parser, LaTeXParser)

    parser = detect_parser("test.latex")
    assert isinstance(parser, LaTeXParser)


def test_detect_parser_invalid():
    """Test that detect_parser raises ValueError for unsupported extension."""
    with pytest.raises(ValueError, match="No parser found"):
        detect_parser("test.pdf")


def test_html_parser_basic():
    """Test parsing a basic HTML file."""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Test Document</title>
        <meta name="author" content="Test Author">
    </head>
    <body>
        <h1>Main Heading</h1>
        <p>This is a paragraph.</p>
        <h2>Subheading</h2>
        <p>Another paragraph.</p>
    </body>
    </html>
    """

    with tempfile.NamedTemporaryFile(mode="w", suffix=".html", delete=False) as f:
        f.write(html_content)
        temp_path = f.name

    try:
        parser = HTMLParser()
        result = parser.parse(temp_path)

        assert result["document_type"] == "html"
        assert result["metadata"]["title"] == "Test Document"
        # Author is only extracted if BeautifulSoup is available
        if "author" in result["metadata"]:
            assert result["metadata"]["author"] == "Test Author"
        assert len(result["headings"]) >= 2
        assert len(result["paragraphs"]) >= 2
        assert result["has_title"] is True
    finally:
        os.unlink(temp_path)


def test_html_parser_invalid_extension():
    """Test that HTML parser rejects invalid extensions."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        f.write("test")
        temp_path = f.name

    try:
        parser = HTMLParser()
        with pytest.raises(ValueError, match="is not supported by HTMLParser"):
            parser.parse(temp_path)
    finally:
        os.unlink(temp_path)


def test_latex_parser_basic():
    """Test parsing a basic LaTeX file."""
    latex_content = r"""
    \documentclass{article}
    \usepackage{amsmath}
    \title{Test Document}
    \author{Test Author}
    \date{\today}

    \begin{document}
    \maketitle

    \section{Introduction}
    This is the introduction.

    \subsection{Background}
    Some background information.

    \begin{figure}
        \caption{A test figure}
        \label{fig:test}
    \end{figure}

    \begin{equation}
        E = mc^2
        \label{eq:einstein}
    \end{equation}

    See Figure \ref{fig:test} and Equation \ref{eq:einstein}.

    \cite{test2023}

    \end{document}
    """

    with tempfile.NamedTemporaryFile(mode="w", suffix=".tex", delete=False) as f:
        f.write(latex_content)
        temp_path = f.name

    try:
        parser = LaTeXParser()
        result = parser.parse(temp_path)

        assert result["document_type"] == "latex"
        assert result["document_class"] == "article"
        assert result["metadata"]["title"] == "Test Document"
        assert result["metadata"]["author"] == "Test Author"
        assert len(result["sections"]) >= 2
        assert len(result["figures"]) == 1
        assert len(result["equations"]) == 1
        assert result["figures"][0]["label"] == "fig:test"
        assert result["equations"][0]["label"] == "eq:einstein"
        assert result["citation_count"] == 1
        assert "amsmath" in result["packages"]
    finally:
        os.unlink(temp_path)


def test_latex_parser_invalid_extension():
    """Test that LaTeX parser rejects invalid extensions."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        f.write("test")
        temp_path = f.name

    try:
        parser = LaTeXParser()
        with pytest.raises(ValueError, match="is not supported by LaTeXParser"):
            parser.parse(temp_path)
    finally:
        os.unlink(temp_path)


def test_html_parser_supports_extension():
    """Test HTML parser extension support."""
    parser = HTMLParser()
    assert parser.supports_extension(".html") is True
    assert parser.supports_extension(".htm") is True
    assert parser.supports_extension(".HTML") is True
    assert parser.supports_extension(".docx") is False
    assert parser.supports_extension(".tex") is False


def test_latex_parser_supports_extension():
    """Test LaTeX parser extension support."""
    parser = LaTeXParser()
    assert parser.supports_extension(".tex") is True
    assert parser.supports_extension(".latex") is True
    assert parser.supports_extension(".TEX") is True
    assert parser.supports_extension(".docx") is False
    assert parser.supports_extension(".html") is False


def test_docx_parser_supports_extension():
    """Test DOCX parser extension support."""
    parser = DocxParser()
    assert parser.supports_extension(".docx") is True
    assert parser.supports_extension(".DOCX") is True
    assert parser.supports_extension(".html") is False
    assert parser.supports_extension(".tex") is False


def test_parser_file_not_found():
    """Test that parsers raise FileNotFoundError for missing files."""
    for parser_class in [DocxParser, HTMLParser, LaTeXParser]:
        parser = parser_class()
        with pytest.raises(FileNotFoundError):
            parser.parse("nonexistent_file.test")


def test_validator_with_html_parser():
    """Test that validator can be initialized with HTML parser."""
    import os

    from docx_tex_validator import DocxValidator

    os.environ["OPENAI_API_KEY"] = "test_key"

    try:
        validator = DocxValidator(parser="html", api_key="test_key")
        assert isinstance(validator.parser, HTMLParser)
    finally:
        if "OPENAI_API_KEY" in os.environ:
            del os.environ["OPENAI_API_KEY"]


def test_validator_with_latex_parser():
    """Test that validator can be initialized with LaTeX parser."""
    import os

    from docx_tex_validator import DocxValidator

    os.environ["OPENAI_API_KEY"] = "test_key"

    try:
        validator = DocxValidator(parser="latex", api_key="test_key")
        assert isinstance(validator.parser, LaTeXParser)
    finally:
        if "OPENAI_API_KEY" in os.environ:
            del os.environ["OPENAI_API_KEY"]


def test_validator_auto_detect_parser():
    """Test that validator can auto-detect parser from file extension."""
    import os
    from unittest.mock import Mock, patch

    from docx_tex_validator import DocxValidator, ValidationSpec

    os.environ["OPENAI_API_KEY"] = "test_key"

    try:
        # Create validator without specifying parser
        validator = DocxValidator(api_key="test_key")

        # Mock the parser to avoid file operations
        mock_html_parser = Mock()
        mock_html_parser.parse = Mock(
            return_value={
                "document_type": "html",
                "metadata": {"title": "Test"},
                "headings": [],
                "paragraphs": [],
            }
        )

        mock_latex_parser = Mock()
        mock_latex_parser.parse = Mock(
            return_value={"document_type": "latex", "metadata": {"title": "Test"}, "sections": []}
        )

        specs = [ValidationSpec(name="Test", description="Test spec")]

        # Mock backend to avoid API calls
        validator.backend.run_sync = Mock(
            return_value=Mock(
                data="Result: PASS\nConfidence: 1.0\nReasoning: Test",
                all_messages=Mock(return_value=[]),
            )
        )

        # Test HTML file detection
        with patch("docx_tex_validator.validator.detect_parser", return_value=mock_html_parser):
            report = validator.validate("test.html", specs)
            assert report.file_path == "test.html"

        # Test LaTeX file detection
        with patch("docx_tex_validator.validator.detect_parser", return_value=mock_latex_parser):
            report = validator.validate("test.tex", specs)
            assert report.file_path == "test.tex"

    finally:
        if "OPENAI_API_KEY" in os.environ:
            del os.environ["OPENAI_API_KEY"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
