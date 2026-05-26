"""
Phase 5: Refusal Handler

Handles advisory and ambiguous queries by generating appropriate refusal responses.
Ensures compliance by never providing investment advice.
"""

import logging
from datetime import datetime
from typing import Optional

logger = logging.getLogger(__name__)


class RefusalHandler:
    """
    Generates polite refusal responses for advisory and out-of-scope queries.
    """
    
    def __init__(self):
        self.advisory_refusal_template = (
            "I'm unable to provide investment advice or recommend specific funds. "
            "I can only share factual details about mutual fund schemes, such as "
            "expense ratios, exit loads, and minimum investment amounts. "
            "For personalized investment advice, please consult a SEBI-registered advisor "
            "or visit {source_url} for more information."
        )
        
        self.ambiguous_refusal_template = (
            "I'd be happy to help with specific factual questions about mutual fund schemes. "
            "For example, you can ask about expense ratios, exit loads, minimum SIP amounts, "
            "or lock-in periods. "
            "For more details, please visit {source_url}."
        )
        
        self.out_of_scope_template = (
            "I can only answer questions about HDFC Mutual Fund schemes. "
            "Please ask about expense ratios, exit loads, minimum investments, "
            "or other scheme-specific details. "
            "For more information, visit {source_url}."
        )
    
    def handle_advisory(self, query: str, source_url: Optional[str] = None) -> dict:
        """
        Generate refusal response for advisory query.
        
        Args:
            query: Original user query.
            source_url: Source URL to cite.
            
        Returns:
            Dictionary with refusal response and metadata.
        """
        logger.info(f"Handling advisory query: {query[:50]}...")
        
        url = source_url or "https://groww.in/mutual-funds"
        response_text = self.advisory_refusal_template.format(source_url=url)
        
        return {
            "answer": response_text,
            "source_url": url,
            "last_updated": datetime.now().strftime("%Y-%m-%d"),
            "is_refusal": True,
            "query_type": "advisory",
            "reason": "Advisory intent detected - investment advice not provided",
        }
    
    def handle_ambiguous(self, query: str, source_url: Optional[str] = None) -> dict:
        """
        Generate clarification request for ambiguous query.
        
        Args:
            query: Original user query.
            source_url: Source URL to cite.
            
        Returns:
            Dictionary with clarification response.
        """
        logger.info(f"Handling ambiguous query: {query[:50]}...")
        
        url = source_url or "https://groww.in/mutual-funds"
        response_text = self.ambiguous_refusal_template.format(source_url=url)
        
        return {
            "answer": response_text,
            "source_url": url,
            "last_updated": datetime.now().strftime("%Y-%m-%d"),
            "is_refusal": True,
            "query_type": "ambiguous",
            "reason": "Ambiguous intent detected - clarification requested",
        }
    
    def handle_out_of_scope(self, query: str, source_url: Optional[str] = None) -> dict:
        """
        Generate refusal response for out-of-scope query.
        
        Args:
            query: Original user query.
            source_url: Source URL to cite.
            
        Returns:
            Dictionary with out-of-scope response.
        """
        logger.info(f"Handling out-of-scope query: {query[:50]}...")
        
        url = source_url or "https://groww.in/mutual-funds"
        response_text = self.out_of_scope_template.format(source_url=url)
        
        return {
            "answer": response_text,
            "source_url": url,
            "last_updated": datetime.now().strftime("%Y-%m-%d"),
            "is_refusal": True,
            "query_type": "factual",
            "reason": "Out-of-scope query - not related to HDFC Mutual Funds",
        }
    
    def handle_not_found(self, query: str, source_url: Optional[str] = None) -> dict:
        """
        Generate response when information is not found in corpus.
        
        Args:
            query: Original user query.
            source_url: Source URL to cite.
            
        Returns:
            Dictionary with not-found response.
        """
        logger.info(f"Handling not-found query: {query[:50]}...")
        
        url = source_url or "https://groww.in/mutual-funds"
        response_text = (
            f"I could not find this information in my current data. "
            f"Please check the official HDFC Mutual Fund website or "
            f"visit {url} for the latest details."
        )
        
        return {
            "answer": response_text,
            "source_url": url,
            "last_updated": datetime.now().strftime("%Y-%m-%d"),
            "is_refusal": False,
            "query_type": "factual",
            "reason": "Information not found in corpus",
        }


# Singleton instance
refusal_handler = RefusalHandler()
