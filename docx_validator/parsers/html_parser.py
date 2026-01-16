"""
Parser for HTML files.
"""

from typing import Any, Dict

from .base import BaseParser


class HTMLParser(BaseParser):
    """Parser for extracting structure and metadata from HTML files."""

    def supports_extension(self, extension: str) -> bool:
        """Check if this parser supports the given file extension."""
        return extension.lower() in [".html", ".htm"]

    def parse(self, file_path: str) -> Dict[str, Any]:
        """
        Parse an HTML file and extract its structure and content information.

        Args:
            file_path: Path to the HTML file

        Returns:
            Dictionary containing document structure information

        Raises:
            FileNotFoundError: If the file doesn't exist
            ValueError: If the file is not a valid HTML file
        """
        self.validate_file(file_path)

        try:
            # Use BeautifulSoup for HTML parsing if available, otherwise basic parsing
            try:
                from bs4 import BeautifulSoup

                has_bs4 = True
            except ImportError:
                has_bs4 = False

            with open(file_path, "r", encoding="utf-8", errors="replace") as f:
                content = f.read()

            if has_bs4:
                soup = BeautifulSoup(content, "html.parser")
                structure = self._parse_with_beautifulsoup(file_path, soup, content)
            else:
                structure = self._parse_basic(file_path, content)

            return structure

        except Exception as e:
            raise ValueError(f"Failed to parse HTML file: {e}") from e

    def _parse_with_beautifulsoup(
        self, file_path: str, soup: Any, raw_content: str
    ) -> Dict[str, Any]:
        """Parse HTML using BeautifulSoup."""
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

    def _parse_basic(self, file_path: str, content: str) -> Dict[str, Any]:
        """Basic HTML parsing without BeautifulSoup."""
        import re

        # Extract title
        title_match = re.search(r"<title>(.*?)</title>", content, re.IGNORECASE | re.DOTALL)
        title = title_match.group(1).strip() if title_match else ""

        # Extract headings using regex
        headings = []
        for level in range(1, 7):
            pattern = rf"<h{level}[^>]*>(.*?)</h{level}>"
            for match in re.finditer(pattern, content, re.IGNORECASE | re.DOTALL):
                text = re.sub(r"<[^>]+>", "", match.group(1)).strip()
                headings.append({"level": level, "text": text, "tag": f"h{level}"})

        # Extract paragraphs
        paragraphs = []
        pattern = r"<p[^>]*>(.*?)</p>"
        for match in re.finditer(pattern, content, re.IGNORECASE | re.DOTALL):
            text = re.sub(r"<[^>]+>", "", match.group(1)).strip()
            if text:
                paragraphs.append({"text": text})

        return {
            "file_path": str(file_path),
            "document_type": "html",
            "metadata": {"title": title},
            "headings": headings,
            "paragraphs": paragraphs,
            "tables": [],
            "lists": [],
            "has_title": bool(title),
            "raw_content": content,
        }
