"""
Phase 1.2: Embedding Pipeline

Generates vector embeddings for document chunks using BGE-Small-EN (local, free).

Features:
- Batch processing with configurable batch size
- Local embedding model (no API key required, no rate limits)
- Progress tracking
- 384-dimensional embeddings (BGE-Small-EN)
"""

import logging
import time
from typing import List, Optional

import numpy as np
from sentence_transformers import SentenceTransformer

from config import settings

logger = logging.getLogger(__name__)


class EmbeddingPipeline:
    """
    Generates embeddings for document chunks using local BGE-Small-EN model.
    No API key required. No rate limits. Works offline.
    """

    def __init__(self, model_name: str = "BAAI/bge-small-en-v1.5", batch_size: int = 100):
        """
        Initialize embedding pipeline with local BGE model.

        Args:
            model_name: HuggingFace model name (default: BAAI/bge-small-en-v1.5).
            batch_size: Number of chunks per batch.
        """
        self.batch_size = batch_size
        self.model_name = model_name

        logger.info(f"Loading BGE embedding model: {model_name}")
        logger.info("(First run downloads ~130MB model, then cached locally)")
        self.model = SentenceTransformer(model_name)

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

        logger.info(f"Generating embeddings for {len(chunks)} chunks (batch size: {self.batch_size})")

        texts = [chunk["chunk_text"] for chunk in chunks]
        all_embeddings = []
        total_batches = (len(texts) + self.batch_size - 1) // self.batch_size

        for batch_idx in range(0, len(texts), self.batch_size):
            batch_texts = texts[batch_idx: batch_idx + self.batch_size]
            batch_num = (batch_idx // self.batch_size) + 1

            logger.info(f"Processing batch {batch_num}/{total_batches}...")

            embeddings = self._embed_batch_with_retry(batch_texts)

            if embeddings is None:
                logger.error(f"Failed to embed batch {batch_num}")
                continue

            all_embeddings.extend(embeddings)

            processed = min(batch_idx + self.batch_size, len(texts))
            logger.info(f"  Progress: {processed}/{len(texts)} chunks embedded")

        for chunk, embedding in zip(chunks, all_embeddings):
            chunk["embedding"] = embedding

        logger.info(f"✓ Generated {len(all_embeddings)} embeddings")
        return chunks

    def _embed_batch_with_retry(
        self, texts: List[str], max_retries: int = 3
    ) -> Optional[List[List[float]]]:
        """
        Embed a batch of texts using local BGE model.

        Args:
            texts: List of texts to embed.
            max_retries: Retry attempts on unexpected errors.

        Returns:
            List of embedding vectors, or None on failure.
        """
        for attempt in range(max_retries):
            try:
                embeddings = self.model.encode(
                    texts,
                    batch_size=self.batch_size,
                    show_progress_bar=False,
                    convert_to_numpy=True,
                )
                return embeddings.tolist()
            except Exception as e:
                logger.error(f"Embedding attempt {attempt + 1} failed: {e}")
                if attempt < max_retries - 1:
                    time.sleep(1)

        return None

    def embed_query(self, text: str) -> List[float]:
        """
        Embed a single query string.

        Args:
            text: Query text.

        Returns:
            Embedding vector (384 dims).
        """
        embedding = self.model.encode(text, convert_to_numpy=True)
        return embedding.tolist()

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

        if len(embedding) != self.embedding_dim:
            logger.warning(f"Embedding dimension mismatch: {len(embedding)} != {self.embedding_dim}")
            return False

        if any(v != v or abs(v) == float("inf") for v in embedding):
            logger.warning("Embedding contains NaN or infinity values")
            return False

        return True
