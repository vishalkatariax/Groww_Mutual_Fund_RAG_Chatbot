"""
Phase 5: Response Validator

Validates LLM-generated responses for compliance before returning to users.
Ensures responses meet all architectural requirements.
"""

import logging
import re
from typing import Optional, Tuple

from config import settings

logger = logging.getLogger(__name__)


class ResponseValidator:
    """
    Validates responses for:
    - Sentence count (≤3 sentences)
    - Advisory language detection
    - Source URL validation
    - Response length limits
    - PII presence
    """
    
    def __init__(self):
        self.max_sentences = 5  # Increased from 3 to allow more complete factual answers
        self.max_chars = 800  # Increased from 500 to provide adequate context
        self.allowed_domains = settings.allow_domains
        
        self.advisory_patterns = [
            r'\byou\s+should\b',
            r'\bi\s+recommend\b',
            r'\bbest\s+(choice|option|fund)\b',
            r'\bbetter\s+to\b',
            r'\bgood\s+(choice|option|time)\b',
            r'\bmust\s+invest\b',
            r'\bhighly\s+recommended\b',
        ]
    
    def validate(self, response: str, source_url: Optional[str] = None, is_refusal: bool = False) -> Tuple[bool, str]:
        """
        Validate a response for compliance.
        
        Args:
            response: LLM-generated response.
            source_url: Source URL cited in response.
            is_refusal: True if this is a refusal response (relaxed validation).
            
        Returns:
            Tuple of (is_valid, message).
        """
        if not response or not response.strip():
            return False, "Response is empty"
        
        # Skip detailed validation for refusal responses
        if is_refusal:
            logger.info("Skipping detailed validation for refusal response")
            return True, "Refusal response accepted"
        
        # Check 1: Sentence count
        sentence_count = self._count_sentences(response)
        if sentence_count > self.max_sentences:
            return False, f"Response too long ({sentence_count} sentences, max {self.max_sentences})"
        
        # Check 2: Advisory language
        advisory_match = self._check_advisory_language(response)
        if advisory_match:
            return False, f"Advisory language detected: '{advisory_match}'"
        
        # Check 3: Source URL validation
        if source_url and not self._validate_url(source_url):
            return False, f"Invalid source URL: {source_url}"
        
        # Check 4: Response length
        if len(response) > self.max_chars:
            return False, f"Response exceeds max length ({len(response)} > {self.max_chars} chars)"
        
        # Check 5: PII detection (defensive)
        if self._contains_pii(response):
            return False, "Response contains potential PII"
        
        return True, "Response validated successfully"
    
    def _count_sentences(self, text: str) -> int:
        """Count sentences in text."""
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        return len(sentences)
    
    def _check_advisory_language(self, text: str) -> Optional[str]:
        """Check for advisory language patterns."""
        text_lower = text.lower()
        for pattern in self.advisory_patterns:
            match = re.search(pattern, text_lower)
            if match:
                return match.group(0)
        return None
    
    def _validate_url(self, url: str) -> bool:
        """Validate that URL is from allowed domains."""
        from urllib.parse import urlparse
        
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            
            if domain.startswith("www."):
                domain = domain[4:]
            
            for allowed in self.allowed_domains:
                if domain == allowed or domain.endswith(f".{allowed}"):
                    return True
            
            return False
        except Exception:
            return False
    
    def _contains_pii(self, text: str) -> bool:
        """Check for PII patterns in text."""
        pii_patterns = [
            r'[A-Z]{5}[0-9]{4}[A-Z]',  # PAN
            r'\b\d{4}\s?\d{4}\s?\d{4}\b',  # Aadhaar
            r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',  # Email
            r'\b(\+91[\s-]?)?[6-9]\d{9}\b',  # Phone
        ]
        
        for pattern in pii_patterns:
            if re.search(pattern, text):
                return True
        
        return False


# Singleton instance
response_validator = ResponseValidator()
