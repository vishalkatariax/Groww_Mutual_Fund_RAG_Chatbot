"""
Configuration settings for the MF FAQ Assistant.

All settings can be overridden via environment variables or a .env file.
"""

from pathlib import Path
from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings

# ──────────────────────────────────────────────────────────────────────
# Project Root & Directories
# ──────────────────────────────────────────────────────────────────────

PROJECT_ROOT = Path(__file__).resolve().parent
DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
CHROMA_DB_DIR = DATA_DIR / "chroma_db"

# Ensure directories exist
for _dir in (DATA_DIR, RAW_DATA_DIR, PROCESSED_DATA_DIR, CHROMA_DB_DIR):
    _dir.mkdir(parents=True, exist_ok=True)


# ──────────────────────────────────────────────────────────────────────
# Groww Scheme Configuration — Exactly 5 URLs
# ──────────────────────────────────────────────────────────────────────

GROWW_SCHEMES: List[dict] = [
    {
        "scheme_name": "HDFC Mid-Cap Fund",
        "category": "mid_cap",
        "url": "https://groww.in/mutual-funds/hdfc-mid-cap-fund-direct-growth",
    },
    {
        "scheme_name": "HDFC Equity Fund",
        "category": "flexi_cap",
        "url": "https://groww.in/mutual-funds/hdfc-equity-fund-direct-growth",
    },
    {
        "scheme_name": "HDFC Focused Fund",
        "category": "focused",
        "url": "https://groww.in/mutual-funds/hdfc-focused-fund-direct-growth",
    },
    {
        "scheme_name": "HDFC ELSS Tax Saver Fund",
        "category": "elss",
        "url": "https://groww.in/mutual-funds/hdfc-elss-tax-saver-fund-direct-plan-growth",
    },
    {
        "scheme_name": "HDFC Large Cap Fund",
        "category": "large_cap",
        "url": "https://groww.in/mutual-funds/hdfc-large-cap-fund-direct-growth",
    },
]

GROWW_URLS: List[str] = [scheme["url"] for scheme in GROWW_SCHEMES]
SCHEME_NAME_TO_URL: dict = {s["scheme_name"]: s["url"] for s in GROWW_SCHEMES}
SCHEME_URL_TO_NAME: dict = {s["url"]: s["scheme_name"] for s in GROWW_SCHEMES}


class Settings(BaseSettings):
    """Application settings loaded from environment / .env file."""

    # ── LLM Settings ──
    llm_provider: str = Field(default="groq", description="groq | openai")
    llm_model: str = Field(default="llama-3.1-8b-instant")
    llm_temperature: float = Field(default=0.0, ge=0.0, le=2.0)
    llm_max_tokens: int = Field(default=256, gt=0)
    groq_api_key: str = Field(default="", description="Required when llm_provider=groq")
    openai_api_key: str = Field(default="", description="Required when llm_provider=openai")

    # ── Embedding Settings ──
    embedding_model: str = Field(default="text-embedding-3-small")
    embedding_dimensions: int = Field(default=1536)
    # ── Vector Store Settings ──
    vector_store_path: str = Field(default=str(CHROMA_DB_DIR))
    vector_store_collection: str = Field(default="mf_faq_corpus")
    chroma_collection: str = Field(default="mf_faq_corpus")

    # ── Retrieval Settings ──
    retrieval_top_k: int = Field(default=5, gt=0)
    retrieval_min_score: float = Field(default=0.6, ge=0.0, le=1.0)
    retrieval_mmr_lambda: float = Field(default=0.7, ge=0.0, le=1.0)
    rag_top_k: int = Field(default=5, gt=0, description="Number of chunks to retrieve for RAG")

    # ── Chunking Settings ──
    chunk_size: int = Field(default=512, gt=0)
    chunk_overlap: int = Field(default=64, gt=0)
    min_chunk_tokens: int = Field(default=50, description="Minimum tokens before merging")

    # ── API Settings ──
    api_rate_limit: str = Field(default="30/minute")
    api_cors_origins: List[str] = Field(default=["http://localhost:3000"])
    api_port: int = Field(default=8000, gt=0, lt=65536)

    # ── Scraping Settings ──
    scraping_delay: float = Field(default=5.0, description="Seconds between Groww requests")
    scraping_max_retries: int = Field(default=3, gt=0)
    scraping_timeout: int = Field(default=30, description="Seconds for page load")
    min_content_length: int = Field(default=500, description="Minimum chars to accept a page")

    # ── Ingestion Settings ──
    allow_domains: List[str] = Field(default=["groww.in"])

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Singleton instance
settings = Settings()
