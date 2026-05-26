"""
Phase 5: Pydantic Schemas for API Request/Response Models

Defines all data validation models used by the FastAPI endpoints.
"""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


# ──────────────────────────────────────────────────────────────────────
# Chat API Schemas
# ──────────────────────────────────────────────────────────────────────

class ChatRequest(BaseModel):
    """Request model for POST /api/v1/chat"""
    
    query: str = Field(
        ...,
        min_length=1,
        max_length=500,
        description="User's question about mutual funds",
        examples=["What is the expense ratio of HDFC Mid-Cap Fund?"],
    )
    
    session_id: Optional[str] = Field(
        default=None,
        description="Optional session identifier for tracking conversations",
        examples=["session_12345"],
    )


class ChatResponse(BaseModel):
    """Response model for POST /api/v1/chat"""
    
    answer: str = Field(
        ...,
        description="The assistant's response",
        examples=["The expense ratio of HDFC Mid-Cap Fund is 1.03% for direct plan."],
    )
    
    source_url: Optional[str] = Field(
        default=None,
        description="Source URL cited in the response",
        examples=["https://groww.in/mutual-funds/hdfc-mid-cap-fund-direct-growth"],
    )
    
    last_updated: str = Field(
        default_factory=lambda: datetime.now().strftime("%Y-%m-%d"),
        description="Date when the data was last updated",
        examples=["2026-05-26"],
    )
    
    is_refusal: bool = Field(
        default=False,
        description="True if the response is an advisory refusal",
    )
    
    query_type: str = Field(
        ...,
        description="Type of query: factual, advisory, or ambiguous",
        pattern="^(factual|advisory|ambiguous)$",
        examples=["factual"],
    )
    
    response_time_ms: Optional[float] = Field(
        default=None,
        description="Response time in milliseconds",
        examples=[1250.5],
    )
    
    chunks_retrieved: Optional[int] = Field(
        default=None,
        description="Number of context chunks retrieved",
        examples=[3],
    )


# ──────────────────────────────────────────────────────────────────────
# Schemes API Schemas
# ──────────────────────────────────────────────────────────────────────

class SchemeInfo(BaseModel):
    """Information about a single mutual fund scheme"""
    
    name: str = Field(
        ...,
        description="Scheme name",
        examples=["HDFC Mid-Cap Fund"],
    )
    
    category: str = Field(
        ...,
        description="Scheme category",
        examples=["mid_cap"],
    )
    
    amc: str = Field(
        default="HDFC Mutual Fund",
        description="Asset Management Company",
        examples=["HDFC Mutual Fund"],
    )
    
    url: str = Field(
        ...,
        description="Groww URL for the scheme",
        examples=["https://groww.in/mutual-funds/hdfc-mid-cap-fund-direct-growth"],
    )


class SchemesResponse(BaseModel):
    """Response model for GET /api/v1/schemes"""
    
    schemes: List[SchemeInfo] = Field(
        ...,
        description="List of available mutual fund schemes",
    )
    
    total_count: int = Field(
        ...,
        description="Total number of schemes",
        examples=[5],
    )


# ──────────────────────────────────────────────────────────────────────
# Health API Schemas
# ──────────────────────────────────────────────────────────────────────

class HealthResponse(BaseModel):
    """Response model for GET /api/v1/health"""
    
    status: str = Field(
        ...,
        description="Health status: healthy, degraded, or unhealthy",
        examples=["healthy"],
    )
    
    vector_store_docs: int = Field(
        default=0,
        description="Number of documents in vector store",
        examples=[150],
    )
    
    last_ingestion: Optional[str] = Field(
        default=None,
        description="Timestamp of last data ingestion",
        examples=["2026-05-26T11:30:00Z"],
    )
    
    version: str = Field(
        default="1.0.0",
        description="API version",
        examples=["1.0.0"],
    )
    
    llm_provider: str = Field(
        default="groq",
        description="Current LLM provider",
        examples=["groq"],
    )
    
    uptime_seconds: Optional[float] = Field(
        default=None,
        description="Server uptime in seconds",
        examples=[3600.0],
    )


# ──────────────────────────────────────────────────────────────────────
# Error Schemas
# ──────────────────────────────────────────────────────────────────────

class ErrorResponse(BaseModel):
    """Standard error response model"""
    
    error: str = Field(
        ...,
        description="Error type",
        examples=["ValidationError"],
    )
    
    message: str = Field(
        ...,
        description="Human-readable error message",
        examples=["Query cannot be empty"],
    )
    
    details: Optional[dict] = Field(
        default=None,
        description="Additional error details",
    )
    
    request_id: Optional[str] = Field(
        default=None,
        description="Unique request identifier for debugging",
    )
