"""
Phase 1.4: Input Guardrails

Protects the system from malicious, inappropriate, or privacy-violating user inputs.

Features:
- PII Detection (PAN, Aadhaar, phone, email, account numbers)
- Topic Filter (blocks non-mutual-fund queries)
- Advisory Query Detector
- Input sanitization
"""

import logging
import re
from typing import Optional, Tuple

logger = logging.getLogger(__name__)


# ──────────────────────────────────────────────────────────────────────
# PII Detection Patterns
# ──────────────────────────────────────────────────────────────────────

PII_PATTERNS = {
    "PAN": {
        "pattern": r'[A-Z]{5}[0-9]{4}[A-Z]',
        "action": "REJECT",
        "description": "PAN number detected",
    },
    "Aadhaar": {
        "pattern": r'\b\d{4}\s?\d{4}\s?\d{4}\b',
        "action": "REJECT",
        "description": "Aadhaar number detected",
    },
    "Email": {
        "pattern": r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
        "action": "STRIP",
        "description": "Email address detected",
    },
    "Phone": {
        "pattern": r'\b(\+91[\s-]?)?[6-9]\d{9}\b',
        "action": "STRIP",
        "description": "Phone number detected",
    },
    "Account Number": {
        "pattern": r'\b\d{9,18}\b',
        "action": "REJECT",
        "description": "Potential account number detected",
    },
    "OTP": {
        "pattern": r'\b\d{6}\b',
        "action": "REJECT",
        "description": "Potential OTP detected",
    },
}


class InputGuardrails:
    """
    Validates and sanitizes user input before processing.
    """

    def __init__(self):
        self.pii_patterns = PII_PATTERNS

    def validate_input(self, query: str) -> Tuple[bool, str, Optional[str]]:
        """
        Validate user input for PII and inappropriate content.

        Args:
            query: User's query string.

        Returns:
            Tuple of (is_valid, message, sanitized_query)
            - is_valid: True if query can be processed
            - message: Explanation of validation result
            - sanitized_query: Cleaned query (if valid), or None
        """
        if not query or not query.strip():
            return False, "Query cannot be empty.", None

        # Check query length
        if len(query.strip()) > 500:
            return False, "Query is too long. Please keep it under 500 characters.", None

        # Check for PII
        pii_detected = self._detect_pii(query)
        if pii_detected:
            if pii_detected["action"] == "REJECT":
                return (
                    False,
                    f"For your security, please do not share personal information like {pii_detected['type']}. "
                    f"Please re-enter your question without any personal details.",
                    None,
                )
            elif pii_detected["action"] == "STRIP":
                sanitized = self._strip_pii(query, pii_detected["type"])
                logger.info(f"PII stripped from query: {pii_detected['type']}")
                return True, f"Query received (personal information removed for security).", sanitized

        # Check topic relevance
        if not self._is_topic_relevant(query):
            return (
                False,
                "I can only answer questions about HDFC Mutual Fund schemes. "
                "Please ask about expense ratios, exit loads, minimum investments, or other scheme details.",
                None,
            )

        return True, "Query validated.", query.strip()

    def _detect_pii(self, text: str) -> Optional[dict]:
        """
        Detect PII in text.

        Args:
            text: Text to scan.

        Returns:
            Dictionary with PII type, action, and description, or None.
        """
        for pii_type, config in self.pii_patterns.items():
            if re.search(config["pattern"], text):
                return {
                    "type": pii_type,
                    "action": config["action"],
                    "description": config["description"],
                }

        return None

    def _strip_pii(self, text: str, pii_type: str) -> str:
        """
        Strip specific PII type from text.

        Args:
            text: Original text.
            pii_type: Type of PII to strip.

        Returns:
            Text with PII removed.
        """
        if pii_type == "Email":
            return re.sub(
                self.pii_patterns["Email"]["pattern"],
                "[EMAIL REMOVED]",
                text,
            )
        elif pii_type == "Phone":
            return re.sub(
                self.pii_patterns["Phone"]["pattern"],
                "[PHONE REMOVED]",
                text,
            )

        return text

    def _is_topic_relevant(self, query: str) -> bool:
        """
        Check if query is related to mutual funds.

        Args:
            query: User's query.

        Returns:
            True if query appears to be about mutual funds.
        """
        # Keywords that indicate mutual fund relevance
        mf_keywords = [
            "fund", "scheme", "mutual fund", "hdfc", "nav", "expense ratio",
            "exit load", "sip", "lumpsum", "investment", "returns",
            "portfolio", "fund manager", "category", "elss", "tax saver",
            "mid cap", "large cap", "flexi cap", "focused", "dividend",
            "growth", "direct", "regular", "lock-in", "statement",
            "capital gains", "nominee", "folio",
        ]

        # Question words (acceptable even without MF keywords)
        question_patterns = [
            "what is", "how to", "when", "where", "who",
            "minimum", "maximum", "can i", "is there",
        ]

        query_lower = query.lower()

        # Check for MF keywords
        for keyword in mf_keywords:
            if keyword in query_lower:
                return True

        # Check for question patterns
        for pattern in question_patterns:
            if query_lower.startswith(pattern):
                return True

        # Allow short factual questions about funds
        if len(query.split()) <= 5:
            return True

        return False

    def detect_advisory_intent(self, query: str) -> bool:
        """
        Detect if a query is asking for investment advice.

        Args:
            query: User's query.

        Returns:
            True if query appears to be advisory.
        """
        advisory_patterns = [
            r'\bshould\s+(i|we)\b',
            r'\bbetter\s+(fund|option|choice)\b',
            r'\bbest\s+(fund|scheme|option)\b',
            r'\brecommend',
            r'\bsuggest',
            r'\badvice',
            r'\bwhich\s+(fund|scheme)\s+.*\b(better|good|best)\b',
            r'\b(is|are)\s+.*\b(good|safe|reliable)\b',
            r'\bworth\s+investing\b',
            r'\bshould\s+i\s+invest\b',
            r'\bwhich\s+one\s+should\b',
        ]

        query_lower = query.lower()

        for pattern in advisory_patterns:
            if re.search(pattern, query_lower):
                return True

        return False
