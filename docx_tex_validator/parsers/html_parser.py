"""
Parser for HTML files.
"""

from typing import Any, Dict

from .base import BaseParser


class HTMLParser(BaseParser):
    """Parser for extracting structure and metadata from HTML files.

    Examples:
        >>> parser = HTMLParser()
        >>> structure = parser.parse("document.html")
        >>> print(structure['metadata']['title'])
    """

    def supports_extension(self, extension: str) -> bool:
        """Check if this parser supports the given file extension.

        Args:
            extension (str):
                File extension to check.

        Returns:
            (bool):
                True if extension is '.html' or '.htm', False otherwise.
        """
        return extension.lower() in [".html", ".htm"]

    def parse(self, file_path: str) -> Dict[str, Any]:
        """Parse an HTML file and extract its structure and content information.

        Args:
            file_path (str):
                Path to the HTML file.

        Returns:
            (Dict[str, Any]):
                Dictionary containing document structure information.

        Raises:
            FileNotFoundError:
                If the file doesn't exist.
            ValueError:
                If the file is not a valid HTML file.
        """
        self.validate_file(file_path)

        try:
            from bs4 import BeautifulSoup

            with open(file_path, "r", encoding="utf-8", errors="replace") as f:
                content = f.read()

            soup = BeautifulSoup(content, "html.parser")
            structure = self._parse_with_beautifulsoup(file_path, soup, content)

            return structure

        except ImportError as e:
            raise ImportError(
                "BeautifulSoup4 is required for HTML parsing. "
                "Install it with: pip install beautifulsoup4"
            ) from e
        except Exception as e:
            raise ValueError(f"Failed to parse HTML file: {e}") from e

    def _parse_with_beautifulsoup(
        self, file_path: str, soup: Any, raw_content: str
    ) -> Dict[str, Any]:
        """Parse HTML using BeautifulSoup.

        Args:
            file_path (str):
                Path to the HTML file.
            soup (Any):
                BeautifulSoup object.
            raw_content (str):
                Raw HTML content.

        Returns:
            (Dict[str, Any]):
                Dictionary containing parsed HTML structure.
        """
        # Extract metadata from meta tags and title
        metadata = {}
        title_tag = soup.find("title")
        metadata["title"] = title_tag.get_text() if title_tag else ""

        # Look for common meta tags
        author_meta = soup.find("meta", attrs={"name": "author"})
        if author_meta:
            metadata["author"] = author_meta.get("content", "")

        description_meta = soup.find("meta", attrs={"name": "description"})
        if description_meta:
            metadata["description"] = description_meta.get("content", "")

        # Extract headings
        headings = []
        for level in range(1, 7):
            for heading in soup.find_all(f"h{level}"):
                headings.append(
                    {"level": level, "text": heading.get_text(strip=True), "tag": f"h{level}"}
                )

        # Extract paragraphs
        paragraphs = []
        for para in soup.find_all("p"):
            paragraphs.append({"text": para.get_text(strip=True)})

        # Extract tables
        tables = []
        for table in soup.find_all("table"):
            rows = table.find_all("tr")
            table_data = []
            for row in rows:
                cells = row.find_all(["td", "th"])
                row_data = [cell.get_text(strip=True) for cell in cells]
                table_data.append(row_data)
            tables.append(
                {"rows": len(rows), "columns": len(cells) if rows else 0, "cells": table_data}
            )

        # Extract lists
        lists = []
        for list_type in ["ul", "ol"]:
            for lst in soup.find_all(list_type):
                items = [li.get_text(strip=True) for li in lst.find_all("li")]
                lists.append({"type": list_type, "items": items})

        return {
            "file_path": str(file_path),
            "document_type": "html",
            "metadata": metadata,
            "headings": headings,
            "paragraphs": paragraphs,
            "tables": tables,
            "lists": lists,
            "has_title": bool(metadata.get("title")),
            "raw_content": raw_content,
        }

