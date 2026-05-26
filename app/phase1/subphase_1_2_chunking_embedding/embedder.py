"""
Phase 1.2: Embedding Pipeline

Generates vector embeddings for document chunks using BGE-Small-EN (local, free).

Features:
- Batch processing with configurable batch size
- Local embedding model (no API key required)
- Progress tracking
- 384-dimensional embeddings (BGE-Small-EN)
"""

import logging
import time
from typing import List

import numpy as np
from sentence_transformers import SentenceTransformer

from config import settings

logger = logging.getLogger(__name__)


class EmbeddingPipeline:
    """
    Generates embeddings for document chunks.

    Supports OpenAI API with automatic retry and rate limit handling.
    """

    def __init__(self, model_name: str = "BAAI/bge-small-en-v1.5", batch_size: int = 100):
        """
        Initialize embedding pipeline with local BGE model.
        
        Benefits:
        - No API key required (free, local)
        - No rate limits
        - Fast inference on CPU
        - Perfect for small datasets (83 chunks)

        Args:
            model_name: HuggingFace model name (default: BAAI/bge-small-en-v1.5).
            batch_size: Number of chunks per batch.
        """
        self.batch_size = batch_size
        self.model_name = model_name
        
        # Load BGE model (downloads once, then cached locally)
        logger.info(f"Loading BGE embedding model: {model_name}")
        logger.info("(First run will download ~130MB model, then it's cached locally)")
        self.model = SentenceTransformer(model_name)
        
        # Get actual embedding dimension from model
        self.embedding_dim = self.model.get_sentence_embedding_dimension()
        logger.info(f"Embedding Pipeline initialized (model: {model_name}, dims: {self.embedding_dim})")

    def generate_embeddings(self, chunks: List[dict]) -> List[dict]:
        """
        Generate embeddings for a list of chunks.

        Args:
            chunks: List of chunk dictionaries with 'chunk_text' field.

        Returns:
            List of chunks with added 'embedding' field.
        """
        if not chunks:
            logger.warning("No chunks provided for embedding")
            return []

        logger.info(
            f"Generating embeddings for {len(chunks)} chunks (batch size: {self.batch_size})"
        )

        # Extract texts
        texts = [chunk["chunk_text"] for chunk in chunks]

        # Process in batches
        all_embeddings = []
        total_batches = (len(texts) + self.batch_size - 1) // self.batch_size

        for batch_idx in range(0, len(texts), self.batch_size):
            batch_texts = texts[batch_idx : batch_idx + self.batch_size]
            batch_num = (batch_idx // self.batch_size) + 1

            logger.info(f"Processing batch {batch_num}/{total_batches}...")

            embeddings = self._embed_batch_with_retry(batch_texts)

            if embeddings is None:
                logger.error(f"Failed to embed batch {batch_num}")
                continue

            all_embeddings.extend(embeddings)

            # Progress log
            processed = min(batch_idx + self.batch_size, len(texts))
            logger.info(f"  Progress: {processed}/{len(texts)} chunks embedded")

        # Add embeddings to chunks
        for chunk, embedding in zip(chunks, all_embeddings):
            chunk["embedding"] = embedding

        logger.info(f"✓ Generated {len(all_embeddings)} embeddings")
        return chunks

    def _embed_batch_with_retry(
        self, texts: List[str], max_retries: int = 3
    ) -> List[List[float]] | None:
        """
        Embed a batch of texts using local BGE model.
        
        Note: No retry logic needed for local model - it won't fail due to API limits.

        Args:
            texts: List of texts to embed.
            max_retries: Unused (kept for API compatibility).

        Returns:
            List of embedding vectors, or None on failure.
        """
        try:
            # Encode texts to embeddings (automatically batched by sentence-transformers)
            embeddings = self.model.encode(
                texts,
                batch_size=self.batch_size,
                show_progress_bar=False,
                convert_to_numpy=True
            )
            
            # Convert numpy arrays to Python lists for JSON serialization
            return embeddings.tolist()
            
        except Exception as e:
            logger.error(f"Failed to embed batch: {e}")
            return None

    def validate_embedding(self, embedding: List[float]) -> bool:
        """
        Validate an embedding vector.

        Args:
            embedding: The embedding vector to validate.

        Returns:
            True if valid, False otherwise.
        """
        if not embedding:
            return False

        # Check dimensions (should match BGE's 384 dims)
        if len(embedding) != self.embedding_dim:
            logger.warning(
                f"Embedding dimension mismatch: {len(embedding)} != {self.embedding_dim}"
            )
            return False

        # Check for NaN or infinity
        if any(v != v or abs(v) == float("inf") for v in embedding):
            logger.warning("Embedding contains NaN or infinity values")
            return False

        return True
