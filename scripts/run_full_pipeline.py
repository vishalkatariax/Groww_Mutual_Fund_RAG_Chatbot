#!/usr/bin/env python3
"""
MF FAQ Assistant - Full Pipeline Orchestrator

Runs all Phase 1 subphases in sequence:
1. Phase 1.1: Corpus Collection & Data Ingestion
2. Phase 1.2: Chunking, Embedding & Vector Store
3. Phase 1.3: RAG Setup & Testing
4. Phase 1.4: Compliance & Guardrails
5. Phase 1.5: Testing & Validation

Usage:
    python3 scripts/run_full_pipeline.py              # Run all phases
    python3 scripts/run_full_pipeline.py --phase 1.1  # Run specific phase
    python3 scripts/run_full_pipeline.py --help       # Show help
"""

import sys
import os
import argparse
import time
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

# Set environment
os.environ.setdefault('PYTHONPATH', str(project_root))


def run_phase_1_1():
    """Phase 1.1: Corpus Collection & Data Ingestion"""
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
    """Phase 1.2: Chunking, Embedding & Vector Store"""
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


def run_phase_1_3():
    """Phase 1.3: RAG Setup & Testing"""
    print("\n" + "=" * 80)
    print("PHASE 1.3: RAG Setup & Testing")
    print("=" * 80 + "\n")
    
    try:
        from app.phase1.subphase_1_3_rag_setup.rag_pipeline import run_phase_1_3_test
        
        results = run_phase_1_3_test()
        
        print(f"\n✅ Phase 1.3 completed!")
        print(f"   Test queries run: {len(results)}")
        
        return len(results)
        
    except Exception as e:
        print(f"\n❌ Phase 1.3 failed: {e}")
        import traceback
        traceback.print_exc()
        return 0


def run_phase_1_4():
    """Phase 1.4: Compliance & Guardrails"""
    print("\n" + "=" * 80)
    print("PHASE 1.4: Compliance & Guardrails Setup")
    print("=" * 80 + "\n")
    
    try:
        from app.phase1.subphase_1_4_compliance.compliance_pipeline import run_compliance_test
        
        results = run_compliance_test()
        
        print(f"\n✅ Phase 1.4 completed!")
        print(f"   Compliance tests passed: {results}")
        
        return results
        
    except Exception as e:
        print(f"\n❌ Phase 1.4 failed: {e}")
        import traceback
        traceback.print_exc()
        return 0


def run_phase_1_5():
    """Phase 1.5: Testing & Validation"""
    print("\n" + "=" * 80)
    print("PHASE 1.5: Testing & Validation")
    print("=" * 80 + "\n")
    
    try:
        # Import and run tests
        print("Running integration tests...")
        
        # Test RAG pipeline
        from app.phase1.subphase_1_3_rag_setup.rag_pipeline import RAGPipeline
        rag = RAGPipeline()
        
        test_queries = [
            "What is the minimum SIP amount?",
            "What is the expense ratio?",
            "Tell me about HDFC Mid-Cap Fund",
        ]
        
        passed = 0
        for query in test_queries:
            try:
                result = rag.query(query)
                if result.get("response"):
                    passed += 1
                    print(f"  ✓ Query: {query}")
                else:
                    print(f"  ✗ Query: {query} - No response")
            except Exception as e:
                print(f"  ✗ Query: {query} - Error: {e}")
        
        print(f"\n✅ Phase 1.5 completed!")
        print(f"   Tests passed: {passed}/{len(test_queries)}")
        
        return passed
        
    except Exception as e:
        print(f"\n❌ Phase 1.5 failed: {e}")
        import traceback
        traceback.print_exc()
        return 0


def main():
    """Run the full pipeline or specific phase"""
    parser = argparse.ArgumentParser(description="MF FAQ Assistant - Full Pipeline Orchestrator")
    parser.add_argument("--phase", type=str, choices=["1.1", "1.2", "1.3", "1.4", "1.5", "all"],
                       default="all", help="Run specific phase or all phases (default: all)")
    args = parser.parse_args()
    
    print("\n" + "=" * 80)
    print("MF FAQ ASSISTANT - PIPELINE ORCHESTRATOR")
    print("=" * 80)
    print(f"Project Root: {project_root}")
    print(f"Mode: {'All Phases' if args.phase == 'all' else f'Phase {args.phase}'}")
    print("=" * 80)
    
    start_time = time.time()
    
    # Run requested phases
    if args.phase == "all" or args.phase == "1.1":
        doc_count = run_phase_1_1()
        if doc_count == 0 and args.phase == "all":
            print("\n❌ Cannot proceed - no documents ingested")
            sys.exit(1)
    
    if args.phase == "all" or args.phase == "1.2":
        stats = run_phase_1_2()
        if stats is None and args.phase == "all":
            print("\n❌ Cannot proceed - chunking/embedding failed")
            sys.exit(1)
    
    if args.phase == "all" or args.phase == "1.3":
        test_count = run_phase_1_3()
    
    if args.phase == "all" or args.phase == "1.4":
        compliance_results = run_phase_1_4()
    
    if args.phase == "all" or args.phase == "1.5":
        test_results = run_phase_1_5()
    
    # Summary
    elapsed = time.time() - start_time
    
    print("\n" + "=" * 80)
    print("PIPELINE COMPLETE - Summary")
    print("=" * 80)
    print(f"✅ Total time: {elapsed:.2f} seconds")
    print(f"✅ Data location: {project_root}/data/")
    print(f"✅ ChromaDB: {project_root}/data/chroma_db/")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    main()
