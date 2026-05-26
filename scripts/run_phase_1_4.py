#!/usr/bin/env python3
"""
Run Phase 1.4: Compliance, Safety & Guardrails Testing

This script tests all compliance and guardrail components:
1. Input guardrails (PII detection, topic filter)
2. Output guardrails (advisory filter, source validator)
3. Domain allowlist validation
4. End-to-end compliance pipeline

Prerequisites:
- Dependencies installed: pip install -r requirements.txt
"""

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from app.phase1.subphase_1_4_compliance.compliance_pipeline import run_phase_1_4_tests


def main():
    """Execute Phase 1.4 testing."""
    print("\n" + "=" * 80)
    print("Starting Phase 1.4: Compliance, Safety & Guardrails")
    print("=" * 80 + "\n")

    try:
        results = run_phase_1_4_tests()

        # Count total passed/failed
        total_passed = 0
        total_failed = 0

        for suite_name, suite_results in results.items():
            for result in suite_results:
                if result["passed"]:
                    total_passed += 1
                else:
                    total_failed += 1

        if total_failed == 0:
            print("\n✅ Phase 1.4 completed successfully!")
            print(f"   All {total_passed} tests passed")
        else:
            print(f"\n⚠️  Phase 1.4 completed with {total_failed} failures")
            print(f"   Passed: {total_passed}, Failed: {total_failed}")

        return results

    except Exception as e:
        print(f"\n❌ Phase 1.4 failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
