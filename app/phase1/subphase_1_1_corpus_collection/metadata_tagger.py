"""
Metadata tagger for ingested documents.

Tags each document with scheme metadata derived from the known Groww URLs.
"""

from datetime import date
from typing import Optional

from config import GROWW_SCHEMES, SCHEME_URL_TO_NAME


# Category inference fallback: if category is not found in known schemes,
# infer it from the scheme name.
CATEGORY_KEYWORDS = {
    "elss": ["elss", "tax saver", "tax saving"],
    "mid_cap": ["mid cap", "mid-cap", "midcap"],
    "large_cap": ["large cap", "large-cap", "largecap"],
    "focused": ["focused"],
    "flexi_cap": ["equity", "flexi cap", "multi cap", "diversified"],
}


def infer_category(scheme_name: str) -> Optional[str]:
    """
    Infer the fund category from the scheme name.

    Uses keyword matching against known category patterns.

    Args:
        scheme_name: The name of the mutual fund scheme.

    Returns:
        Category string (e.g., "mid_cap") or None if not inferred.
    """
    name_lower = scheme_name.lower()

    for category, keywords in CATEGORY_KEYWORDS.items():
        for keyword in keywords:
            if keyword in name_lower:
                return category

    return None


def tag_document(url: str, scraped_date: Optional[date] = None) -> dict:
    """
    Tag a document with metadata based on its source URL.

    Looks up the URL in the known scheme list. If not found,
    attempts to infer the category from the URL path.

    Args:
        url: The Groww scheme page URL.
        scraped_date: Date the page was scraped (defaults to today).

    Returns:
        Dictionary of metadata fields.
    """
    from app.guardrails.domain_allowlist import normalize_url

    normalized_url = normalize_url(url)
    scraped_date = scraped_date or date.today()

    # Look up in known schemes
    scheme_name = SCHEME_URL_TO_NAME.get(normalized_url)
    category = None

    if scheme_name:
        # Find the matching scheme to get category
        for scheme in GROWW_SCHEMES:
            if scheme["url"] == normalized_url:
                category = scheme["category"]
                break
    else:
        # Infer from URL path
        path = normalized_url.lower()
        category = infer_category(path)
        scheme_name = "Unknown Scheme"

    if category is None:
        category = "unknown"

    return {
        "scheme_name": scheme_name,
        "amc_name": "HDFC Mutual Fund",
        "source_url": normalized_url,
        "category": category,
        "scraped_date": scraped_date.isoformat(),
        "source_type": "groww_scheme_page",
    }


def validate_metadata(metadata: dict) -> bool:
    """
    Validate that all required metadata fields are present and valid.

    Args:
        metadata: The metadata dictionary to validate.

    Returns:
        True if all required fields are present, False otherwise.
    """
    required_fields = [
        "scheme_name",
        "amc_name",
        "source_url",
        "category",
        "scraped_date",
        "source_type",
    ]

    for field in required_fields:
        if field not in metadata:
            return False

        if not metadata[field]:
            return False

    return True
