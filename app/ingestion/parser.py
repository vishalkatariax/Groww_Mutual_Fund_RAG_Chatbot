"""
HTML-to-Text parser for Groww scheme pages.

Converts raw HTML scraped from Groww into clean, structured text
suitable for chunking and embedding.
"""

import re
import unicodedata

from bs4 import BeautifulSoup, NavigableString, Tag


def html_to_text(html: str) -> str:
    """
    Convert raw HTML to clean text.

    Handles:
    - Script and style removal
    - Unicode normalization
    - Table-to-text conversion (preserves row structure)
    - Whitespace cleanup
    - Special character normalization

    Args:
        html: Raw HTML content from Groww page.

    Returns:
        Cleaned text ready for chunking.
    """
    if not html or not html.strip():
        return ""

    soup = BeautifulSoup(html, "html.parser")

    # Remove script, style, and noscript tags
    for element in soup(["script", "style", "noscript", "header", "footer", "nav"]):
        element.decompose()

    # Extract text with structure preservation
    text = _extract_text_with_structure(soup)

    # Normalize unicode
    text = unicodedata.normalize("NFKC", text)

    # Clean up whitespace
    text = _clean_whitespace(text)

    return text.strip()


def _extract_text_with_structure(soup: BeautifulSoup) -> str:
    """
    Extract text while preserving heading and table structure.

    Headings are preserved with markers for later chunking.
    Tables are converted to "Label: Value" format.
    """
    parts = []

    for element in soup.children:
        if isinstance(element, Tag):
            if element.name in ("h1", "h2", "h3", "h4"):
                # Preserve headings as section markers
                heading_text = element.get_text(strip=True)
                if heading_text:
                    parts.append(f"\n## {heading_text}\n")

            elif element.name == "table":
                # Convert tables to structured text
                table_text = _table_to_text(element)
                if table_text:
                    parts.append(table_text)

            elif element.name in ("p", "li", "td", "th"):
                text = element.get_text(strip=True)
                if text:
                    parts.append(text)

            elif element.name in ("div", "section", "article", "main"):
                # Recursively process container elements
                child_text = _extract_text_with_structure(element)
                if child_text.strip():
                    parts.append(child_text)

            else:
                # Generic tag — just get text
                text = element.get_text(strip=True)
                if text:
                    parts.append(text)

        elif isinstance(element, NavigableString):
            text = str(element).strip()
            if text:
                parts.append(text)

    return "\n".join(parts)


def _table_to_text(table: Tag) -> str:
    """
    Convert an HTML table to structured "Label: Value" text.

    Preserves table relationships that would be lost in flat text extraction.
    """
    rows = []

    for tr in table.find_all("tr"):
        cells = []
        for cell in tr.find_all(["th", "td"]):
            text = cell.get_text(strip=True)
            if text:
                cells.append(text)

        if cells:
            # If 2 cells, treat as "Key: Value"
            if len(cells) == 2:
                rows.append(f"{cells[0]}: {cells[1]}")
            # If more cells, join with pipe (preserve table structure)
            else:
                rows.append(" | ".join(cells))

    if rows:
        return "\n".join(rows)

    return ""


def _clean_whitespace(text: str) -> str:
    """
    Clean up whitespace in the text.

    - Replace non-breaking spaces with regular spaces
    - Collapse multiple newlines into 2
    - Remove leading/trailing whitespace from each line
    - Remove lines with only whitespace
    """
    # Replace non-breaking spaces
    text = text.replace("\u00a0", " ")

    # Normalize special characters
    text = text.replace("\u2014", "-")  # em dash
    text = text.replace("\u2013", "-")  # en dash
    text = text.replace("\u2018", "'")  # left single quote
    text = text.replace("\u2019", "'")  # right single quote
    text = text.replace("\u201c", '"')  # left double quote
    text = text.replace("\u201d", '"')  # right double quote

    # Clean up lines
    lines = []
    for line in text.split("\n"):
        line = line.strip()
        if line:
            lines.append(line)

    # Collapse multiple blank lines
    result = "\n".join(lines)
    result = re.sub(r"\n{3,}", "\n\n", result)

    return result


def validate_content_length(text: str, min_length: int = 500) -> bool:
    """
    Validate that the cleaned text meets minimum length requirements.

    This filters out empty or near-empty pages.

    Args:
        text: Cleaned text content.
        min_length: Minimum character count required.

    Returns:
        True if the text meets the minimum length, False otherwise.
    """
    return len(text.strip()) >= min_length
