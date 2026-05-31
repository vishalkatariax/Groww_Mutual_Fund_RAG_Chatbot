"""
Re-embed ChromaDB collection using OpenAI text-embedding-3-small.

Drops the existing BGE-384 collection and rebuilds it with OpenAI-1536 embeddings
using the already-chunked data in data/processed/chunks.json.

Usage:
    python scripts/reembed_openai.py
"""

import json
import logging
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)


def main():
    from config import PROCESSED_DATA_DIR, settings
    from app.phase1.subphase_1_2_chunking_embedding.embedder import EmbeddingPipeline
    from app.phase1.subphase_1_2_chunking_embedding.vector_store import VectorStore

    chunks_path = PROCESSED_DATA_DIR / "chunks.json"
    if not chunks_path.exists():
        logger.error(f"chunks.json not found at {chunks_path}. Run the ingestion pipeline first.")
        sys.exit(1)

    with open(chunks_path, "r") as f:
        chunks = json.load(f)

    logger.info(f"Loaded {len(chunks)} chunks from {chunks_path}")

    # Drop old collection (BGE 384-dim)
    vs = VectorStore()
    logger.info("Dropping existing collection (BGE 384-dim)...")
    vs.delete_collection()

    # Re-create collection
    vs = VectorStore()
    logger.info("Created fresh collection for OpenAI 1536-dim embeddings")

    # Generate new embeddings
    embedder = EmbeddingPipeline()
    chunks_with_embeddings = embedder.generate_embeddings(chunks)

    # Store in ChromaDB
    added = vs.add_chunks(chunks_with_embeddings)
    logger.info(f"✓ Re-embedded and stored {added} chunks with OpenAI text-embedding-3-small")

    stats = vs.get_stats()
    logger.info(f"Collection stats: {stats}")


if __name__ == "__main__":
    main()
