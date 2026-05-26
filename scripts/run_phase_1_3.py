#!/usr/bin/env python3
"""
Run Phase 1.3: RAG Pipeline Testing

This script tests the RAG (Retrieval-Augmented Generation) pipeline:
1. Loads vector store from Phase 1.2
2. Tests retrieval with sample queries
3. Validates responses
4. Displays results

Prerequisites:
- Phase 1.2 must be completed (ChromaDB must have chunks)
- OPENAI_API_KEY must be set in .env file
- Dependencies installed: pip install -r requirements.txt
"""

import sys
from pathlib import Path

# Add project root to Python path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.phase1.subphase_1_3_rag_setup.rag_pipeline import run_phase_1_3_test


def main():
    """Execute Phase 1.3 RAG testing."""
    print("\n" + "=" * 80)
    print("Starting Phase 1.3: RAG Pipeline Testing")
    print("=" * 80 + "\n")

    try:
        results = run_phase_1_3_test()

        print("\n✅ Phase 1.3 testing completed!")
        print(f"\n📊 Test Results:")
        print(f"   Total queries tested: {len(results)}")

        for idx, result in enumerate(results, 1):
            print(f"\n   Test {idx}:")
            print(f"   Query: {result['metadata']['query']}")
            print(f"   Chunks retrieved: {result['metadata']['chunks_retrieved']}")
            print(f"   Validation passed: {result['validation']['passed']}")
            if result['validation']['warnings']:
                print(f"   Warnings: {result['validation']['warnings']}")

        return results

    except Exception as e:
        print(f"\n❌ Phase 1.3 failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
