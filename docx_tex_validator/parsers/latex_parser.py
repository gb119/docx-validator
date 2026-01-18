"""
Parser for LaTeX files.
"""

import re
from typing import Any, Dict

from .base import BaseParser


class LaTeXParser(BaseParser):
    """Parser for extracting structure and metadata from LaTeX files.

    Examples:
        >>> parser = LaTeXParser()
        >>> structure = parser.parse("document.tex")
        >>> print(structure['metadata']['title'])
    """

    def supports_extension(self, extension: str) -> bool:
        """Check if this parser supports the given file extension.

        Args:
            extension (str):
                File extension to check.

        Returns:
            (bool):
                True if extension is '.tex' or '.latex', False otherwise.
        """
        return extension.lower() in [".tex", ".latex"]

    def parse(self, file_path: str) -> Dict[str, Any]:
        """Parse a LaTeX file and extract its structure and content information.

        Args:
            file_path (str):
                Path to the LaTeX file.

        Returns:
            (Dict[str, Any]):
                Dictionary containing document structure information.

        Raises:
            FileNotFoundError:
                If the file doesn't exist.
            ValueError:
                If the file is not a valid LaTeX file.
        """
        self.validate_file(file_path)

        try:
            with open(file_path, "r", encoding="utf-8", errors="replace") as f:
                content = f.read()

            structure = self._parse_latex(file_path, content)
            return structure

        except Exception as e:
            raise ValueError(f"Failed to parse LaTeX file: {e}") from e

    def _parse_latex(self, file_path: str, content: str) -> Dict[str, Any]:
        """Parse LaTeX content and extract structure using TexSoup.

        Args:
            file_path (str):
                Path to the LaTeX file.
            content (str):
                Raw LaTeX content.

        Returns:
            (Dict[str, Any]):
                Dictionary containing parsed LaTeX structure.
        """
        from TexSoup import TexSoup

        # Parse LaTeX with TexSoup
        soup = TexSoup(content, tolerance=1)

        # Extract document class
        doc_class = None
        doc_class_cmd = soup.find("documentclass")
        if doc_class_cmd and doc_class_cmd.args:
            doc_class = str(doc_class_cmd.args[0]).strip("{}")

        # Extract metadata from common LaTeX commands
        metadata = {}

        title_cmd = soup.find("title")
        if title_cmd and title_cmd.args:
            metadata["title"] = self._clean_latex(str(title_cmd.args[0]))

        author_cmd = soup.find("author")
        if author_cmd and author_cmd.args:
            metadata["author"] = self._clean_latex(str(author_cmd.args[0]))

        date_cmd = soup.find("date")
        if date_cmd and date_cmd.args:
            metadata["date"] = self._clean_latex(str(date_cmd.args[0]))

        # Extract sections and subsections
        sections = []
        section_types = [
            ("chapter", 0),
            ("section", 1),
            ("subsection", 2),
            ("subsubsection", 3),
        ]

        for section_type, level in section_types:
            for section_cmd in soup.find_all(section_type):
                if section_cmd.args:
                    sections.append(
                        {
                            "type": section_type,
                            "level": level,
                            "text": self._clean_latex(str(section_cmd.args[0])),
                        }
                    )

        # Extract environments (figures, tables, equations)
        figures = []
        for figure in soup.find_all("figure"):
            caption_cmd = figure.find("caption")
            if caption_cmd and caption_cmd.args:
                caption = self._clean_latex(str(caption_cmd.args[0]))
            else:
                caption = ""

            label_cmd = figure.find("label")
            if label_cmd and label_cmd.args:
                label = str(label_cmd.args[0]).strip("{}")
            else:
                label = ""

            figures.append({"caption": caption, "label": label})

        tables = []
        for table in soup.find_all("table"):
            caption_cmd = table.find("caption")
            if caption_cmd and caption_cmd.args:
                caption = self._clean_latex(str(caption_cmd.args[0]))
            else:
                caption = ""

            label_cmd = table.find("label")
            if label_cmd and label_cmd.args:
                label = str(label_cmd.args[0]).strip("{}")
            else:
                label = ""

            tables.append({"caption": caption, "label": label})

        # Extract equations
        equations = []
        for equation in soup.find_all("equation"):
            label_cmd = equation.find("label")
            label = str(label_cmd.args[0]).strip("{}") if label_cmd and label_cmd.args else ""

            # Get equation content by extracting text from children, excluding label
            eq_parts = []
            for child in equation.contents:
                child_str = str(child).strip()
                # Skip label commands
                if not child_str.startswith("\\label"):
                    eq_parts.append(child_str)

            eq_content = " ".join(eq_parts).strip()

            equations.append({"content": eq_content, "label": label})

        # Extract bibliography information
        has_bibliography = bool(
            soup.find("bibliography") or soup.find("thebibliography")
        )

        # Extract citations
        citations = soup.find_all("cite")
        citation_count = len(citations)

        # Extract packages
        packages = []
        for usepackage_cmd in soup.find_all("usepackage"):
            if usepackage_cmd.args:
                pkg_names = str(usepackage_cmd.args[0]).strip("{}")
                packages.extend([pkg.strip() for pkg in pkg_names.split(",")])

        return {
            "file_path": str(file_path),
            "document_type": "latex",
            "document_class": doc_class,
            "metadata": metadata,
            "sections": sections,
            "figures": figures,
            "tables": tables,
            "equations": equations,
            "packages": packages,
            "has_bibliography": has_bibliography,
            "citation_count": citation_count,
            "raw_content": content,
        }

    def _clean_latex(self, text: str) -> str:
        """Clean LaTeX commands from text.

        Args:
            text (str):
                Text containing LaTeX commands.

        Returns:
            (str):
                Cleaned text with LaTeX commands removed.
        """
        # Remove common LaTeX commands but keep the text
        text = re.sub(r"\\textbf\{(.*?)\}", r"\1", text)
        text = re.sub(r"\\textit\{(.*?)\}", r"\1", text)
        text = re.sub(r"\\emph\{(.*?)\}", r"\1", text)
        text = re.sub(r"\\[a-zA-Z]+\{(.*?)\}", r"\1", text)
        text = re.sub(r"\\[a-zA-Z]+", "", text)
        text = text.replace("{", "").replace("}", "")
        return text.strip()
