"""
Phase 1.4: Domain Allowlist Enhancement

Comprehensive domain validation for URLs in both input queries and output responses.

Extends the basic domain validation from Phase 1.1 with:
- URL extraction from text
- Multiple domain support
- Subdomain handling
- URL normalization
"""

import logging
import re
from typing import List, Optional
from urllib.parse import urlparse

from config import settings

logger = logging.getLogger(__name__)


class DomainAllowlist:
    """
    Validates and manages allowed domains for source URLs.
    """

    def __init__(self, allowed_domains: List[str] = None):
        """
        Initialize domain allowlist.

        Args:
            allowed_domains: List of allowed domain names.
        """
        self.allowed_domains = allowed_domains or settings.allow_domains

    def is_domain_allowed(self, url: str) -> bool:
        """
        Check if a URL's domain is in the allowlist.

        Args:
            url: URL to validate.

        Returns:
            True if domain is allowed.
        """
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.lower()

            # Strip 'www.' prefix
            if domain.startswith("www."):
                domain = domain[4:]

            # Check exact match or subdomain
            for allowed in self.allowed_domains:
                if domain == allowed:
                    return True
                if domain.endswith(f".{allowed}"):
                    return True

            return False

        except Exception as e:
            logger.error(f"Error validating domain: {e}")
            return False

    def extract_urls_from_text(self, text: str) -> List[str]:
        """
        Extract all URLs from text.

        Args:
            text: Text to search for URLs.

        Returns:
            List of URLs found.
        """
        # URL pattern
        url_pattern = r'https?://[^\s<>"\']+'

        urls = re.findall(url_pattern, text)

        # Clean up URLs (remove trailing punctuation)
        cleaned_urls = []
        for url in urls:
            # Remove trailing punctuation that's not part of URL
            url = url.rstrip('.,;:!?)"\'')
            cleaned_urls.append(url)

        return cleaned_urls

    def validate_all_urls_in_text(self, text: str) -> dict:
        """
        Validate all URLs in text against allowlist.

        Args:
            text: Text containing URLs.

        Returns:
            Dictionary with validation results.
        """
        urls = self.extract_urls_from_text(text)

        results = {
            "total_urls": len(urls),
            "valid_urls": [],
            "invalid_urls": [],
            "all_valid": True,
        }

        for url in urls:
            if self.is_domain_allowed(url):
                results["valid_urls"].append(url)
            else:
                results["invalid_urls"].append(url)
                results["all_valid"] = False

        return results

    def normalize_url(self, url: str) -> str:
        """
        Normalize a URL for consistent comparison.

        Args:
            url: URL to normalize.

        Returns:
            Normalized URL.
        """
        try:
            parsed = urlparse(url)

            # Lowercase scheme and netloc
            scheme = parsed.scheme.lower()
            netloc = parsed.netloc.lower()

            # Remove 'www.' prefix
            if netloc.startswith("www."):
                netloc = netloc[4:]

            # Remove trailing slash from path
            path = parsed.path.rstrip('/')

            # Reconstruct URL
            normalized = f"{scheme}://{netloc}{path}"

            # Add query string if present
            if parsed.query:
                normalized += f"?{parsed.query}"

            # Add fragment if present
            if parsed.fragment:
                normalized += f"#{parsed.fragment}"

            return normalized

        except Exception as e:
            logger.warning(f"Failed to normalize URL: {e}")
            return url

    def add_domain(self, domain: str):
        """
        Add a domain to the allowlist.

        Args:
            domain: Domain name to add.
        """
        if domain not in self.allowed_domains:
            self.allowed_domains.append(domain)
            logger.info(f"Added domain to allowlist: {domain}")

    def remove_domain(self, domain: str):
        """
        Remove a domain from the allowlist.

        Args:
            domain: Domain name to remove.
        """
        if domain in self.allowed_domains:
            self.allowed_domains.remove(domain)
            logger.info(f"Removed domain from allowlist: {domain}")

    def get_allowed_domains(self) -> List[str]:
        """
        Get list of allowed domains.

        Returns:
            List of domain names.
        """
        return self.allowed_domains.copy()
