"""
Phase 1.2: Chunking, Embedding & Vector Store Pipeline

Orchestrates the complete workflow:
1. Load ingested documents from Phase 1.1
2. Chunk documents using semantic chunking
3. Generate embeddings using OpenAI
4. Store in ChromaDB vector store
"""

import json
import logging
from pathlib import Path
from typing import List

from config import RAW_DATA_DIR, PROCESSED_DATA_DIR
from app.phase1.subphase_1_2_chunking_embedding.chunker import ChunkingEngine
from app.phase1.subphase_1_2_chunking_embedding.embedder import EmbeddingPipeline
from app.phase1.subphase_1_2_chunking_embedding.vector_store import VectorStore

logger = logging.getLogger(__name__)


class Phase1_2Pipeline:
    """
    Orchestrates Phase 1.2: Chunking, Embedding & Vector Store.

    Workflow:
        Load Documents → Chunk → Embed → Store in ChromaDB
    """

    def __init__(self):
        self.chunker = ChunkingEngine()
        self.embedder = None  # Lazy initialization (needs API key)
        self.vector_store = VectorStore()
        self.all_chunks = []

    def run(self, documents_path: Path = None) -> dict:
        """
        Execute the complete Phase 1.2 pipeline.

        Args:
            documents_path: Path to JSON file with ingested documents (from Phase 1.1).

        Returns:
            Dictionary with pipeline statistics.
        """
        logger.info("=" * 60)
        logger.info("PHASE 1.2: Chunking, Embedding & Vector Store")
        logger.info("=" * 60)

        # Step 1: Load documents
        if documents_path is None:
            documents_path = RAW_DATA_DIR / "ingested_documents.json"

        documents = self._load_documents(documents_path)
        logger.info(f"Loaded {len(documents)} documents from {documents_path}")

        # Step 2: Chunk documents
        logger.info("\n" + "=" * 60)
        logger.info("STEP 2: Chunking Documents")
        logger.info("=" * 60)

        self.all_chunks = self._chunk_documents(documents)
        logger.info(f"✓ Created {len(self.all_chunks)} chunks total")

        # Step 3: Generate embeddings
        logger.info("\n" + "=" * 60)
        logger.info("STEP 3: Generating Embeddings")
        logger.info("=" * 60)

        if self.embedder is None:
            self.embedder = EmbeddingPipeline()

        self.all_chunks = self.embedder.generate_embeddings(self.all_chunks)

        # Step 4: Store in vector database
        logger.info("\n" + "=" * 60)
        logger.info("STEP 4: Storing in ChromaDB")
        logger.info("=" * 60)

        chunks_added = self.vector_store.add_chunks(self.all_chunks)

        # Step 5: Save chunked data to disk
        logger.info("\n" + "=" * 60)
        logger.info("STEP 5: Saving Chunked Data")
        logger.info("=" * 60)

        self._save_chunks(self.all_chunks)

        # Return statistics
        stats = {
            "documents_loaded": len(documents),
            "chunks_created": len(self.all_chunks),
            "chunks_embedded": sum(1 for c in self.all_chunks if "embedding" in c),
            "chunks_stored": chunks_added,
            "vector_store_stats": self.vector_store.get_stats(),
        }

        logger.info("\n" + "=" * 60)
        logger.info("PHASE 1.2 COMPLETE")
        logger.info("=" * 60)
        logger.info(f"Documents: {stats['documents_loaded']}")
        logger.info(f"Chunks: {stats['chunks_created']}")
        logger.info(f"Embeddings: {stats['chunks_embedded']}")
        logger.info(f"Stored: {stats['chunks_stored']}")
        logger.info("=" * 60)

        return stats

    def _load_documents(self, path: Path) -> List[dict]:
        """
        Load ingested documents from JSON file.

        Args:
            path: Path to JSON file.

        Returns:
            List of document dictionaries.
        """
        if not path.exists():
            raise FileNotFoundError(
                f"Documents file not found: {path}\n"
                f"Please run Phase 1.1 first to ingest documents."
            )

        with open(path, "r", encoding="utf-8") as f:
            documents = json.load(f)

        if not isinstance(documents, list):
            raise ValueError("Expected JSON array of documents")

        return documents

    def _chunk_documents(self, documents: List[dict]) -> List[dict]:
        """
        Chunk all documents using the chunking engine.

        Args:
            documents: List of document dictionaries.

        Returns:
            List of chunk dictionaries.
        """
        all_chunks = []

        for idx, doc in enumerate(documents, 1):
            logger.info(f"\nChunking document {idx}/{len(documents)}: {doc.get('scheme_name', 'Unknown')}")

            # Extract text and metadata
            text = doc.get("content_clean", "")
            metadata = {
                "doc_id": doc.get("doc_id", "unknown"),
                "scheme_name": doc.get("scheme_name", "unknown"),
                "amc_name": doc.get("amc_name", "unknown"),
                "source_url": str(doc.get("source_url", "")),
                "category": doc.get("category", "unknown"),
            }

            # Chunk the document
            chunks = self.chunker.chunk_document(text, metadata)
            all_chunks.extend(chunks)

            logger.info(f"  ✓ Created {len(chunks)} chunks")

        return all_chunks

    def _save_chunks(self, chunks: List[dict]):
        """
        Save chunks (without embeddings) to processed data directory.

        Args:
            chunks: List of chunk dictionaries.
        """
        output_path = PROCESSED_DATA_DIR / "chunks.json"

        # Remove embeddings for storage (they're in ChromaDB)
        chunks_without_embeddings = []
        for chunk in chunks:
            chunk_copy = {k: v for k, v in chunk.items() if k != "embedding"}
            chunks_without_embeddings.append(chunk_copy)

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(chunks_without_embeddings, f, indent=2, ensure_ascii=False)

        logger.info(f"✓ Saved {len(chunks)} chunks to {output_path}")


def run_phase_1_2():
    """
    Main entry point for Phase 1.2.
    """
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    # Run pipeline
    pipeline = Phase1_2Pipeline()
    stats = pipeline.run()

    return stats


if __name__ == "__main__":
    stats = run_phase_1_2()
    print("\nPhase 1.2 Statistics:")
    print(json.dumps(stats, indent=2))
