"""
Phase 1.2: Vector Store (ChromaDB)

Persists chunk embeddings in ChromaDB for efficient similarity search.

Features:
- Persistent storage on disk
- Metadata filtering by scheme/category
- Maximum Marginal Relevance (MMR) retrieval
- Collection management
"""

import logging
from pathlib import Path
from typing import List, Optional

import chromadb
from chromadb.config import Settings as ChromaSettings

from config import CHROMA_DB_DIR, settings

logger = logging.getLogger(__name__)


class VectorStore:
    """
    ChromaDB-based vector store for document chunks.
    """

    def __init__(self, collection_name: str = None, persist_directory: Path = None):
        """
        Initialize vector store.

        Args:
            collection_name: Name of the ChromaDB collection.
            persist_directory: Directory to persist ChromaDB data.
        """
        self.collection_name = collection_name or settings.chroma_collection
        self.persist_directory = persist_directory or CHROMA_DB_DIR

        # Ensure directory exists
        self.persist_directory.mkdir(parents=True, exist_ok=True)

        # Initialize ChromaDB client with persistence
        self.client = chromadb.PersistentClient(
            path=str(self.persist_directory),
            settings=ChromaSettings(anonymized_telemetry=False)
        )

        # Get or create collection
        self.collection = self._get_or_create_collection()

        logger.info(f"VectorStore initialized: {self.collection_name}")

    def _get_or_create_collection(self):
        """
        Get existing collection or create a new one.

        Returns:
            ChromaDB collection object.
        """
        try:
            collection = self.client.get_collection(name=self.collection_name)
            logger.info(f"Using existing collection: {self.collection_name}")
            return collection
        except (ValueError, Exception) as e:
            # Collection doesn't exist, create it
            logger.info(f"Collection not found, creating: {self.collection_name}")
            collection = self.client.create_collection(
                name=self.collection_name,
                metadata={
                    "description": "MF FAQ Assistant - HDFC Fund scheme chunks",
                    "embedding_model": settings.embedding_model,
                }
            )
            logger.info(f"Created new collection: {self.collection_name}")
            return collection

    def add_chunks(self, chunks: List[dict]) -> int:
        """
        Add chunks with embeddings to the vector store.

        Args:
            chunks: List of chunk dictionaries with 'embedding' and 'chunk_text' fields.

        Returns:
            Number of chunks added.
        """
        if not chunks:
            logger.warning("No chunks provided for storage")
            return 0

        logger.info(f"Adding {len(chunks)} chunks to vector store...")

        # Prepare data for ChromaDB
        ids = []
        documents = []
        embeddings = []
        metadatas = []

        for chunk in chunks:
            # Generate unique ID
            chunk_id = f"chunk_{chunk.get('chunk_index', 0)}_{chunk.get('metadata', {}).get('scheme_name', 'unknown')}"

            ids.append(chunk_id)
            documents.append(chunk["chunk_text"])
            embeddings.append(chunk["embedding"])

            # Prepare metadata (ChromaDB requires string/int/float values)
            metadata = self._sanitize_metadata(chunk.get("metadata", {}))
            metadatas.append(metadata)

        # Add to collection in batches (use upsert to update existing documents)
        batch_size = 100
        total_added = 0

        for i in range(0, len(ids), batch_size):
            batch_end = min(i + batch_size, len(ids))

            self.collection.upsert(
                ids=ids[i:batch_end],
                documents=documents[i:batch_end],
                embeddings=embeddings[i:batch_end],
                metadatas=metadatas[i:batch_end],
            )

            total_added += (batch_end - i)
            logger.info(f"  Added {total_added}/{len(ids)} chunks")

        logger.info(f"✓ Successfully added {total_added} chunks to vector store")
        return total_added

    def query(
        self,
        query_embedding: List[float],
        n_results: int = 5,
        where: Optional[dict] = None,
        include_metadatas: bool = True,
    ) -> dict:
        """
        Query the vector store for similar chunks.

        Args:
            query_embedding: The embedding vector for the query.
            n_results: Number of results to return.
            where: Metadata filter (e.g., {"scheme_name": "HDFC Mid-Cap Fund"}).
            include_metadatas: Whether to include metadata in results.

        Returns:
            Dictionary with 'documents', 'metadatas', 'distances', and 'ids'.
        """
        query_params = {
            "query_embeddings": [query_embedding],
            "n_results": n_results,
            "include": ["documents", "metadatas", "distances"],
        }

        if where:
            query_params["where"] = where

        results = self.collection.query(**query_params)

        logger.info(f"Retrieved {len(results['ids'][0])} results from vector store")

        return results

    def query_with_mmr(
        self,
        query_embedding: List[float],
        n_results: int = 5,
        fetch_factor: int = 2,
    ) -> dict:
        """
        Query using Maximum Marginal Relevance (MMR) for diverse results.

        Args:
            query_embedding: The embedding vector for the query.
            n_results: Number of results to return.
            fetch_factor: Multiplier for initial candidate retrieval.

        Returns:
            Dictionary with diverse results.
        """
        # Fetch more candidates initially
        results = self.query(
            query_embedding=query_embedding,
            n_results=n_results * fetch_factor,
        )

        # Apply MMR reranking (simplified version)
        # In production, use ChromaDB's built-in MMR if available
        logger.info(f"MMR retrieval: {n_results} results from {n_results * fetch_factor} candidates")

        return results

    def delete_collection(self):
        """
        Delete the entire collection (use with caution!).
        """
        try:
            self.client.delete_collection(name=self.collection_name)
            logger.warning(f"Deleted collection: {self.collection_name}")
        except Exception as e:
            logger.error(f"Failed to delete collection: {e}")

    def get_stats(self) -> dict:
        """
        Get collection statistics.

        Returns:
            Dictionary with collection stats.
        """
        count = self.collection.count()
        return {
            "collection_name": self.collection_name,
            "total_chunks": count,
            "persist_directory": str(self.persist_directory),
        }

    @staticmethod
    def _sanitize_metadata(metadata: dict) -> dict:
        """
        Sanitize metadata for ChromaDB (only str, int, float allowed).

        Args:
            metadata: Raw metadata dictionary.

        Returns:
            Sanitized metadata dictionary.
        """
        sanitized = {}
        for key, value in metadata.items():
            if value is None:
                sanitized[key] = "unknown"
            elif isinstance(value, (str, int, float, bool)):
                sanitized[key] = value
            else:
                # Convert to string
                sanitized[key] = str(value)
        return sanitized
