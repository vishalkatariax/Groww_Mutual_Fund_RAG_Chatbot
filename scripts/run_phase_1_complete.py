#!/usr/bin/env python3
"""
Run Phase 1.1 (Data Ingestion) and Phase 1.2 (Chunking & Embedding)

This script:
1. Scrapes 5 Groww scheme pages
2. Parses and cleans the HTML
3. Adds metadata
4. Chunks the documents
5. Generates embeddings
6. Stores in ChromaDB
"""

import sys
import os
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

# Set environment
os.environ.setdefault('PYTHONPATH', str(project_root))

def run_phase_1_1():
    """Run Phase 1.1: Data Ingestion"""
    print("\n" + "=" * 80)
    print("PHASE 1.1: Corpus Collection & Data Ingestion")
    print("=" * 80 + "\n")
    
    try:
        from app.phase1.subphase_1_1_corpus_collection.pipeline import IngestionPipeline
        
        pipeline = IngestionPipeline()
        documents = pipeline.run()
        
        print(f"\n✅ Phase 1.1 completed!")
        print(f"   Documents ingested: {len(documents)}")
        
        return len(documents)
        
    except Exception as e:
        print(f"\n❌ Phase 1.1 failed: {e}")
        import traceback
        traceback.print_exc()
        return 0

def run_phase_1_2():
    """Run Phase 1.2: Chunking & Embedding"""
    print("\n" + "=" * 80)
    print("PHASE 1.2: Chunking, Embedding & Vector Store")
    print("=" * 80 + "\n")
    
    try:
        from app.phase1.subphase_1_2_chunking_embedding.pipeline import run_phase_1_2
        
        stats = run_phase_1_2()
        
        print(f"\n✅ Phase 1.2 completed!")
        print(f"   Documents loaded: {stats['documents_loaded']}")
        print(f"   Chunks created: {stats['chunks_created']}")
        print(f"   Embeddings generated: {stats['chunks_embedded']}")
        print(f"   Stored in ChromaDB: {stats['chunks_stored']}")
        
        return stats
        
    except Exception as e:
        print(f"\n❌ Phase 1.2 failed: {e}")
        import traceback
        traceback.print_exc()
        return None

def main():
    """Run both phases"""
    print("\n" + "=" * 80)
    print("PHASE 1: Complete Data Pipeline (Ingestion + Chunking + Embedding)")
    print("=" * 80)
    
    # Run Phase 1.1
    doc_count = run_phase_1_1()
    
    if doc_count == 0:
        print("\n❌ Cannot proceed to Phase 1.2 - no documents ingested")
        sys.exit(1)
    
    # Run Phase 1.2
    stats = run_phase_1_2()
    
    if stats is None:
        print("\n❌ Phase 1.2 failed")
        sys.exit(1)
    
    # Summary
    print("\n" + "=" * 80)
    print("PHASE 1 COMPLETE - Summary")
    print("=" * 80)
    print(f"✅ Documents ingested: {doc_count}")
    print(f"✅ Chunks created: {stats['chunks_created']}")
    print(f"✅ Embeddings stored: {stats['chunks_stored']}")
    print(f"✅ Vector store: ChromaDB")
    print(f"✅ Data location: {project_root}/data/")
    print("=" * 80 + "\n")

if __name__ == "__main__":
    main()
