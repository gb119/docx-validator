"""
Parser for LaTeX files.
"""

from typing import Any, Dict

from .base import BaseParser


class LaTeXParser(BaseParser):
    """Parser for extracting structure and metadata from LaTeX files."""

    def supports_extension(self, extension: str) -> bool:
        """Check if this parser supports the given file extension."""
        return extension.lower() in [".tex", ".latex"]

    def parse(self, file_path: str) -> Dict[str, Any]:
        """
        Parse a LaTeX file and extract its structure and content information.

        Args:
            file_path: Path to the LaTeX file

        Returns:
            Dictionary containing document structure information

        Raises:
            FileNotFoundError: If the file doesn't exist
            ValueError: If the file is not a valid LaTeX file
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
        """Parse LaTeX content and extract structure."""
        import re

        # Extract document class
        doc_class_match = re.search(r"\\documentclass(?:\[.*?\])?\{(.*?)\}", content)
        doc_class = doc_class_match.group(1) if doc_class_match else None

        # Extract metadata from common LaTeX commands
        metadata = {}

        title_match = re.search(r"\\title\{(.*?)\}", content, re.DOTALL)
        if title_match:
            metadata["title"] = self._clean_latex(title_match.group(1))

        author_match = re.search(r"\\author\{(.*?)\}", content, re.DOTALL)
        if author_match:
            metadata["author"] = self._clean_latex(author_match.group(1))

        date_match = re.search(r"\\date\{(.*?)\}", content, re.DOTALL)
        if date_match:
            metadata["date"] = self._clean_latex(date_match.group(1))

        # Extract sections and subsections
        sections = []
        section_patterns = [
            (r"\\section\{(.*?)\}", "section", 1),
            (r"\\subsection\{(.*?)\}", "subsection", 2),
            (r"\\subsubsection\{(.*?)\}", "subsubsection", 3),
            (r"\\chapter\{(.*?)\}", "chapter", 0),
        ]

        for pattern, section_type, level in section_patterns:
            for match in re.finditer(pattern, content, re.DOTALL):
                sections.append(
                    {
                        "type": section_type,
                        "level": level,
                        "text": self._clean_latex(match.group(1)),
                    }
                )

        # Extract environments (figures, tables, equations)
        figures = []
        figure_pattern = r"\\begin\{figure\}(.*?)\\end\{figure\}"
        for match in re.finditer(figure_pattern, content, re.DOTALL):
            fig_content = match.group(1)
            caption_match = re.search(r"\\caption\{(.*?)\}", fig_content, re.DOTALL)
            caption = self._clean_latex(caption_match.group(1)) if caption_match else ""
            label_match = re.search(r"\\label\{(.*?)\}", fig_content)
            label = label_match.group(1) if label_match else ""
            figures.append({"caption": caption, "label": label})

        tables = []
        table_pattern = r"\\begin\{table\}(.*?)\\end\{table\}"
        for match in re.finditer(table_pattern, content, re.DOTALL):
            tbl_content = match.group(1)
            caption_match = re.search(r"\\caption\{(.*?)\}", tbl_content, re.DOTALL)
            caption = self._clean_latex(caption_match.group(1)) if caption_match else ""
            label_match = re.search(r"\\label\{(.*?)\}", tbl_content)
            label = label_match.group(1) if label_match else ""
            tables.append({"caption": caption, "label": label})

        # Extract equations
        equations = []
        equation_pattern = r"\\begin\{equation\}(.*?)\\end\{equation\}"
        for match in re.finditer(equation_pattern, content, re.DOTALL):
            eq_content = match.group(1)
            label_match = re.search(r"\\label\{(.*?)\}", eq_content)
            label = label_match.group(1) if label_match else ""
            equations.append({"content": eq_content.strip(), "label": label})

        # Extract bibliography information
        has_bibliography = bool(
            re.search(r"\\bibliography\{.*?\}", content)
            or re.search(r"\\begin\{thebibliography\}", content)
        )

        # Extract citations
        citations = re.findall(r"\\cite\{(.*?)\}", content)
        citation_count = len(citations)

        # Extract packages
        packages = []
        package_pattern = r"\\usepackage(?:\[.*?\])?\{(.*?)\}"
        for match in re.finditer(package_pattern, content):
            packages.extend(match.group(1).split(","))

        return {
            "file_path": str(file_path),
            "document_type": "latex",
            "document_class": doc_class,
            "metadata": metadata,
            "sections": sections,
            "figures": figures,
            "tables": tables,
            "equations": equations,
            "packages": [pkg.strip() for pkg in packages],
            "has_bibliography": has_bibliography,
            "citation_count": citation_count,
            "raw_content": content,
        }

    def _clean_latex(self, text: str) -> str:
        """Clean LaTeX commands from text."""
        import re

        # Remove common LaTeX commands but keep the text
        text = re.sub(r"\\textbf\{(.*?)\}", r"\1", text)
        text = re.sub(r"\\textit\{(.*?)\}", r"\1", text)
        text = re.sub(r"\\emph\{(.*?)\}", r"\1", text)
        text = re.sub(r"\\[a-zA-Z]+\{(.*?)\}", r"\1", text)
        text = re.sub(r"\\[a-zA-Z]+", "", text)
        text = text.replace("{", "").replace("}", "")
        return text.strip()
