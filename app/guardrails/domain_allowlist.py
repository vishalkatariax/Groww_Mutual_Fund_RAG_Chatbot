"""
Domain allow-list validation for source URLs.

Only URLs from groww.in are accepted as valid data sources.
"""

from urllib.parse import urlparse

from config import settings


def validate_domain(url: str) -> bool:
    """
    Validate that a URL belongs to an allowed domain.

    Args:
        url: The URL to validate.

    Returns:
        True if the URL's domain is in the allow-list, False otherwise.
    """
    try:
        parsed = urlparse(url)
        domain = parsed.netloc.lower()

        # Strip 'www.' prefix if present
        if domain.startswith("www."):
            domain = domain[4:]

        # Check against allow-list
        for allowed in settings.allow_domains:
            if domain == allowed or domain.endswith(f".{allowed}"):
                return True

        return False

    except Exception:
        return False


def validate_is_groww(url: str) -> bool:
    """
    Specifically check if a URL is from groww.in.

    Args:
        url: The URL to validate.

    Returns:
        True if the URL is from groww.in, False otherwise.
    """
    return validate_domain(url)


def normalize_url(url: str) -> str:
    """
    Normalize a URL by stripping query parameters and fragments.

    Only the base URL path is validated; tracking parameters are removed.

    Args:
        url: The URL to normalize.

    Returns:
        The cleaned base URL.
    """
    try:
        parsed = urlparse(url)
        # Force HTTPS
        scheme = "https"
        # Strip query parameters and fragments
        return f"{scheme}://{parsed.netloc}{parsed.path}"
    except Exception:
        return url


def validate_url_in_known_schemes(url: str) -> bool:
    """
    Check if a URL matches one of the 5 known Groww scheme pages.

    This is stricter than domain validation — only the exact 5 URLs are accepted.

    Args:
        url: The URL to validate.

    Returns:
        True if the URL matches one of the 5 scheme pages.
    """
    from config import GROWW_URLS

    normalized = normalize_url(url)
    return normalized in GROWW_URLS
