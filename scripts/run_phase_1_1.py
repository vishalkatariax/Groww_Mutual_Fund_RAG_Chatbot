#!/usr/bin/env python3
"""
Run Phase 1.1: Corpus Collection & Data Ingestion

This script executes the complete Phase 1.1 pipeline:
1. Scrapes 5 HDFC Mutual Fund scheme pages from Groww
2. Parses HTML to clean text
3. Tags with metadata
4. Saves to JSON

Prerequisites:
- OPENAI_API_KEY must be set in .env file (for future phases)
- Playwright browsers installed: playwright install
- Dependencies installed: pip install -r requirements.txt
"""

import sys
from pathlib import Path

# Add project root to Python path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.phase1.subphase_1_1_corpus_collection.pipeline import run_phase_1_1


def main():
    """Execute Phase 1.1 pipeline."""
    print("\n" + "=" * 80)
    print("Starting Phase 1.1: Corpus Collection & Data Ingestion")
    print("=" * 80 + "\n")

    try:
        stats = run_phase_1_1()

        print("\n✅ Phase 1.1 completed successfully!")
        print("\n📊 Statistics:")
        print(f"   URLs scraped:    {stats['urls_scraped']}")
        print(f"   Successful:      {stats['successful']}")
        print(f"   Failed:          {stats['failed']}")
        print(f"   Documents saved: {stats['documents_saved']}")
        print(f"\n   Output: {stats['output_file']}")

        return stats

    except Exception as e:
        print(f"\n❌ Phase 1.1 failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
