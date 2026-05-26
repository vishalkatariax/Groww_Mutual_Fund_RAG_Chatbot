#!/usr/bin/env python3
"""
Run Phase 1.2: Chunking, Embedding & Vector Store

This script executes the complete Phase 1.2 pipeline:
1. Loads ingested documents from Phase 1.1
2. Chunks documents using semantic chunking
3. Generates embeddings using OpenAI
4. Stores in ChromaDB vector store

Prerequisites:
- Phase 1.1 must be completed (ingested_documents.json must exist)
- OPENAI_API_KEY must be set in .env file
- Dependencies installed: pip install -r requirements.txt
"""

import sys
from pathlib import Path

# Add project root to Python path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.phase1.subphase_1_2_chunking_embedding.pipeline import run_phase_1_2


def main():
    """Execute Phase 1.2 pipeline."""
    print("\n" + "=" * 80)
    print("Starting Phase 1.2: Chunking, Embedding & Vector Store")
    print("=" * 80 + "\n")

    try:
        stats = run_phase_1_2()

        print("\n✅ Phase 1.2 completed successfully!")
        print("\n📊 Statistics:")
        print(f"   Documents loaded: {stats['documents_loaded']}")
        print(f"   Chunks created:   {stats['chunks_created']}")
        print(f"   Embeddings:       {stats['chunks_embedded']}")
        print(f"   Stored in ChromaDB: {stats['chunks_stored']}")
        print(f"\n   Vector Store: {stats['vector_store_stats']}")

        return stats

    except FileNotFoundError as e:
        print(f"\n❌ Error: {e}")
        print("\n📝 Please run Phase 1.1 first to ingest documents:")
        print("   python scripts/run_phase_1_1.py")
        sys.exit(1)

    except Exception as e:
        print(f"\n❌ Phase 1.2 failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
