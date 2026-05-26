"""
Data models for ingested documents and chunks.
"""

from datetime import date
from typing import Optional

from pydantic import BaseModel, Field, HttpUrl


class IngestedDocument(BaseModel):
    """Represents a raw ingested document from a Groww scheme page."""

    doc_id: str = Field(description="Unique identifier (UUID)")
    scheme_name: str = Field(description="Canonical scheme name, e.g. 'HDFC Mid-Cap Fund'")
    amc_name: str = Field(default="HDFC Mutual Fund")
    source_url: HttpUrl = Field(description="Groww page URL")
    category: str = Field(description="Fund category: mid_cap, flexi_cap, focused, elss, large_cap")
    content_raw: str = Field(description="Raw HTML/text as scraped")
    content_clean: str = Field(description="Cleaned text after parsing")
    scraped_date: date = Field(description="Date the page was scraped")
    last_verified_date: Optional[date] = Field(
        default=None, description="Date shown on Groww page (if available)"
    )
    is_official: bool = Field(default=True)
    domain_verified: bool = Field(default=True)
    source_type: str = Field(default="groww_scheme_page")

    class Config:
        json_schema_extra = {
            "example": {
                "doc_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
                "scheme_name": "HDFC Mid-Cap Fund",
                "amc_name": "HDFC Mutual Fund",
                "source_url": "https://groww.in/mutual-funds/hdfc-mid-cap-fund-direct-growth",
                "category": "mid_cap",
                "content_raw": "<html>...</html>",
                "content_clean": "HDFC Mid-Cap Fund expense ratio...",
                "scraped_date": "2026-05-26",
                "last_verified_date": "2026-05-25",
                "is_official": True,
                "domain_verified": True,
                "source_type": "groww_scheme_page",
            }
        }


class DocumentChunk(BaseModel):
    """Represents a single chunk of a document ready for embedding."""

    chunk_id: str = Field(description="Unique identifier (UUID)")
    doc_id: str = Field(description="Parent document UUID")
    chunk_text: str = Field(description="Cleaned chunk content")
    chunk_index: int = Field(description="Position in parent document (0-based)")
    token_count: int = Field(description="Number of tokens in chunk_text")
    metadata: dict = Field(
        description="Metadata for ChromaDB: scheme_name, source_url, category, etc."
    )

    class Config:
        json_schema_extra = {
            "example": {
                "chunk_id": "x1y2z3-a4b5c6-d7e8f9",
                "doc_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
                "chunk_text": "The expense ratio of HDFC Mid-Cap Fund (Direct) is 1.03%...",
                "chunk_index": 3,
                "token_count": 87,
                "metadata": {
                    "scheme_name": "HDFC Mid-Cap Fund",
                    "amc_name": "HDFC Mutual Fund",
                    "source_type": "groww_scheme_page",
                    "category": "mid_cap",
                    "source_url": "https://groww.in/mutual-funds/hdfc-mid-cap-fund-direct-growth",
                    "section_heading": "Fund Details",
                    "scraped_date": "2026-05-26",
                },
            }
        }
