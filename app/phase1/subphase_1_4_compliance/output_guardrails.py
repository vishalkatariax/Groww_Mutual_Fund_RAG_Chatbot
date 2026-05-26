"""
Phase 1.4: Output Guardrails

Validates and sanitizes LLM responses before returning to user.

Features:
- Advisory language detection
- Source URL validation
- Sentence count enforcement (≤3 sentences)
- Disclaimer appending
- Response length validation
"""

import logging
import re
from typing import Optional, Tuple

from config import settings

logger = logging.getLogger(__name__)


# Advisory language patterns to flag
ADVISORY_PATTERNS = [
    r'\byou\s+should\b',
    r'\bi\s+recommend\b',
    r'\bbest\s+(choice|option|fund)\b',
    r'\bbetter\s+to\b',
    r'\bsuggest\s+investing\b',
    r'\badvise\b',
    r'\bgood\s+(choice|option|time)\b',
    r'\bmust\s+invest\b',
    r'\bavoid\s+(this|fund)\b',
    r'\bhighly\s+recommended\b',
]


class OutputGuardrails:
    """
    Validates LLM responses for compliance before returning to user.
    """

    def __init__(self):
        self.max_sentences = 20  # Increased to allow detailed multi-fund answers
        self.max_chars = 1500   # Increased to allow longer responses
        self.allowed_domains = settings.allow_domains
        self.advisory_patterns = ADVISORY_PATTERNS

    def validate_response(
        self,
        response: str,
        source_url: Optional[str] = None,
        is_refusal: bool = False,
    ) -> Tuple[bool, str, Optional[str]]:
        """
        Validate a response before returning to user.

        Args:
            response: LLM-generated response.
            source_url: Source URL cited in response (if any).
            is_refusal: True if this is an advisory refusal response.

        Returns:
            Tuple of (is_valid, message, final_response)
        """
        if not response or not response.strip():
            return False, "Response is empty.", None

        # Skip detailed validation for refusal responses
        if is_refusal:
            logger.info("Skipping detailed validation for refusal response")
            return True, "Refusal response validated.", response

        # Check 1: Sentence count
        sentences = self._count_sentences(response)
        if sentences > self.max_sentences:
            logger.warning(f"Response has {sentences} sentences (max: {self.max_sentences})")
            return (
                False,
                f"Response too long ({sentences} sentences). Maximum is {self.max_sentences}.",
                None,
            )

        # Check 2: Advisory language
        advisory_detected = self._check_advisory_language(response)
        if advisory_detected:
            logger.warning(f"Advisory language detected: {advisory_detected}")
            return (
                False,
                f"Response contains advisory language: '{advisory_detected}'",
                None,
            )

        # Check 3: Source URL validation
        if source_url:
            if not self._validate_source_url(source_url):
                logger.warning(f"Invalid source URL: {source_url}")
                return (
                    False,
                    f"Source URL is not from allowed domains: {source_url}",
                    None,
                )

        # Check 4: Response length (reasonable bounds)
        if len(response) > self.max_chars:
            logger.warning(f"Response too long: {len(response)} chars")
            return (
                False,
                f"Response exceeds maximum length ({len(response)} > {self.max_chars} chars)",
                None,
            )

        # All checks passed
        logger.info(f"Response validated: {sentences} sentences, {len(response)} chars")
        return True, "Response validated.", response

    def append_disclaimer(self, response: str, source_url: Optional[str] = None) -> str:
        """
        Append disclaimer and metadata to a validated response.
            
        Args:
            response: Validated response.
            source_url: Source URL to cite.
            
        Returns:
            Response (disclaimer removed - source is shown via UI component).
        """
        # Source and last updated are now displayed via the UI SourceLink component
        # No need to include them in the response text
        return response

    def _count_sentences(self, text: str) -> int:
        """
        Count sentences in text.

        Uses punctuation markers: . ! ?

        Args:
            text: Response text.

        Returns:
            Number of sentences.
        """
        # Split on sentence-ending punctuation
        sentences = re.split(r'[.!?]+', text)
        # Filter out empty strings
        sentences = [s.strip() for s in sentences if s.strip()]
        return len(sentences)

    def _check_advisory_language(self, text: str) -> Optional[str]:
        """
        Check for advisory language in response.

        Args:
            text: Response text.

        Returns:
            Detected advisory phrase, or None.
        """
        text_lower = text.lower()

        for pattern in self.advisory_patterns:
            match = re.search(pattern, text_lower)
            if match:
                return match.group(0)

        return None

    def _validate_source_url(self, url: str) -> bool:
        """
        Validate that a source URL is from allowed domains.

        Args:
            url: URL to validate.

        Returns:
            True if URL is from allowed domain.
        """
        from urllib.parse import urlparse

        try:
            parsed = urlparse(url)
            domain = parsed.netloc.lower()

            # Strip 'www.' prefix
            if domain.startswith("www."):
                domain = domain[4:]

            # Check against allow-list
            for allowed in self.allowed_domains:
                if domain == allowed or domain.endswith(f".{allowed}"):
                    return True

            return False

        except Exception:
            return False

    def sanitize_response(self, response: str) -> str:
        """
        Sanitize response text (remove potentially problematic content).

        Args:
            response: Raw response.

        Returns:
            Sanitized response.
        """
        # Remove extra whitespace
        response = re.sub(r'\s+', ' ', response).strip()

        # Remove any remaining PII (defensive)
        # Email
        response = re.sub(
            r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
            '[EMAIL REMOVED]',
            response,
        )
        # Phone
        response = re.sub(
            r'\b(\+91[\s-]?)?[6-9]\d{9}\b',
            '[PHONE REMOVED]',
            response,
        )

        return response
