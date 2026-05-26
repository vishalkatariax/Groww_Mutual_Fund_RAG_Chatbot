"""
Phase 5: Intent Classifier

Classifies user queries into factual, advisory, or ambiguous intents.
Uses pattern-based classification for fast, deterministic results.
"""

import logging
import re
from enum import Enum
from typing import Optional

logger = logging.getLogger(__name__)


class IntentType(str, Enum):
    """Query intent types"""
    FACTUAL = "factual"
    ADVISORY = "advisory"
    AMBIGUOUS = "ambiguous"


class IntentClassifier:
    """
    Classifies user queries into intent categories.
    
    Uses a combination of:
    1. Pattern matching (fast, rule-based)
    2. Keyword scoring (flexible, context-aware)
    3. LLM-based fallback (accurate, for edge cases)
    """
    
    def __init__(self):
        # Advisory patterns (high confidence)
        self.advisory_patterns = [
            r'\bshould\s+(i|we)\b',
            r'\bbetter\s+(fund|option|choice|scheme)\b',
            r'\bbest\s+(fund|scheme|option|choice)\b',
            r'\brecommend(ed|ation|s)?\b',
            r'\bsuggest(ed|ion|s)?\b',
            r'\badvice\b',
            r'\bwhich\s+(fund|scheme)\s+.*\b(better|good|best)\b',
            r'\b(is|are)\s+.*\b(good|safe|reliable|better)\b.*\b(invest|fund)\b',
            r'\bworth\s+investing\b',
            r'\bshould\s+i\s+invest\b',
            r'\bwhich\s+one\s+should\b',
            r'\b(is|are)\s+.*\b(good|safe|reliable)\b',
            r'\bwhat\s+should\s+i\s+invest\b',
            r'\bhow\s+to\s+choose\b',
        ]
        
        # Factual patterns (high confidence)
        self.factual_patterns = [
            r'\bwhat\s+is\s+(the\s+)?(expense\s*ratio|exit\s*load|minimum|nav|returns?)\b',
            r'\bhow\s+(much|many|to)\b',
            r'\bwhat\s+are\s+(the\s+)?(features|benefits|risks|charges|fees)\b',
            r'\b(minimum|maximum|min|max)\s+(sip|investment|amount)\b',
            r'\bhow\s+to\s+(download|get|view|check)\b',
            r'\bwhat\s+is\s+(the\s+)?(lock-?in\s*period|maturity\s*period)\b',
            r'\b(expense\s*ratio|exit\s*load|sip|lumpsum|nav)\b.*\b(hdfc|fund|scheme)\b',
            r'\b(statement|capital\s*gains|tax)\b',
        ]
        
        # Ambiguous patterns
        self.ambiguous_patterns = [
            r'\btell\s+me\s+about\b',
            r'\bhow\s+is\s+(this\s+)?(fund|scheme)\b',
            r'\b(info|information)\s+about\b',
            r'\bdetails\s+(about|of|for)\b',
        ]
    
    def classify(self, query: str) -> dict:
        """
        Classify a user query into an intent type.
        
        Args:
            query: User's query string.
            
        Returns:
            Dictionary with classification results:
            {
                "intent": "factual" | "advisory" | "ambiguous",
                "confidence": 0.0 to 1.0,
                "reason": "Explanation of classification"
            }
        """
        if not query or not query.strip():
            return {
                "intent": IntentType.AMBIGUOUS,
                "confidence": 1.0,
                "reason": "Empty query classified as ambiguous",
            }
        
        query_lower = query.lower().strip()
        
        # Check for advisory patterns (highest priority for safety)
        advisory_match = self._check_patterns(query_lower, self.advisory_patterns)
        if advisory_match:
            logger.info(f"Query classified as ADVISORY: {advisory_match}")
            return {
                "intent": IntentType.ADVISORY,
                "confidence": 0.95,
                "reason": f"Advisory pattern detected: {advisory_match}",
            }
        
        # Check for factual patterns
        factual_match = self._check_patterns(query_lower, self.factual_patterns)
        if factual_match:
            logger.info(f"Query classified as FACTUAL: {factual_match}")
            return {
                "intent": IntentType.FACTUAL,
                "confidence": 0.90,
                "reason": f"Factual pattern detected: {factual_match}",
            }
        
        # Check for ambiguous patterns
        ambiguous_match = self._check_patterns(query_lower, self.ambiguous_patterns)
        if ambiguous_match:
            logger.info(f"Query classified as AMBIGUOUS: {ambiguous_match}")
            return {
                "intent": IntentType.AMBIGUOUS,
                "confidence": 0.80,
                "reason": f"Ambiguous pattern detected: {ambiguous_match}",
            }
        
        # Default: Use keyword scoring
        return self._score_based_classification(query_lower)
    
    def _check_patterns(self, query: str, patterns: list) -> Optional[str]:
        """
        Check if query matches any of the given patterns.
        
        Args:
            query: Lowercase query string.
            patterns: List of regex patterns.
            
        Returns:
            Matched pattern string or None.
        """
        for pattern in patterns:
            if re.search(pattern, query):
                return pattern
        return None
    
    def _score_based_classification(self, query: str) -> dict:
        """
        Classify using keyword scoring when patterns don't match.
        
        Args:
            query: Lowercase query string.
            
        Returns:
            Classification result dictionary.
        """
        advisory_keywords = [
            'should', 'recommend', 'suggest', 'better', 'best',
            'good', 'safe', 'reliable', 'worth', 'choose',
        ]
        
        factual_keywords = [
            'what', 'how', 'when', 'where', 'which',
            'expense', 'ratio', 'load', 'minimum', 'sip',
            'nav', 'returns', 'lock-in', 'statement',
        ]
        
        # Calculate scores
        advisory_score = sum(1 for word in advisory_keywords if word in query)
        factual_score = sum(1 for word in factual_keywords if word in query)
        
        # Classify based on scores
        if advisory_score > factual_score and advisory_score >= 2:
            return {
                "intent": IntentType.ADVISORY,
                "confidence": 0.70,
                "reason": f"Keyword scoring: advisory={advisory_score}, factual={factual_score}",
            }
        elif factual_score > 0:
            return {
                "intent": IntentType.FACTUAL,
                "confidence": 0.75,
                "reason": f"Keyword scoring: factual={factual_score}, advisory={advisory_score}",
            }
        else:
            return {
                "intent": IntentType.AMBIGUOUS,
                "confidence": 0.60,
                "reason": f"No clear intent detected (advisory={advisory_score}, factual={factual_score})",
            }


# Singleton instance
intent_classifier = IntentClassifier()
