"""
Phase 1.4: Compliance Pipeline

Orchestrates all input and output guardrails to ensure every query and response
is compliant, safe, and within scope.

Workflow:
    User Query → Input Guardrails → RAG Pipeline → Output Guardrails → Final Response
"""

import logging
from typing import Optional, Tuple

from app.phase1.subphase_1_4_compliance.input_guardrails import InputGuardrails
from app.phase1.subphase_1_4_compliance.output_guardrails import OutputGuardrails
from app.phase1.subphase_1_4_compliance.domain_allowlist_enhanced import DomainAllowlist

logger = logging.getLogger(__name__)


class CompliancePipeline:
    """
    Orchestrates all compliance checks for the MF FAQ Assistant.
    """

    def __init__(self):
        self.input_guardrails = InputGuardrails()
        self.output_guardrails = OutputGuardrails()
        self.domain_allowlist = DomainAllowlist()

    def process_query(self, query: str) -> Tuple[bool, str, Optional[str]]:
        """
        Process a user query through input guardrails.

        Args:
            query: Raw user query.

        Returns:
            Tuple of (is_valid, message, sanitized_query)
        """
        logger.info(f"Processing query through input guardrails: {query[:50]}...")

        # Step 1: Validate input
        is_valid, message, sanitized_query = self.input_guardrails.validate_input(query)

        if not is_valid:
            logger.warning(f"Query failed input validation: {message}")
            return False, message, None

        # Step 2: Check for advisory intent (for routing, not rejection)
        is_advisory = self.input_guardrails.detect_advisory_intent(sanitized_query)

        if is_advisory:
            logger.info("Advisory intent detected in query")
            # Return special message to trigger refusal handler
            return (
                False,
                "ADVISORY_DETECTED",
                sanitized_query,
            )

        logger.info("Query passed input guardrails")
        return True, "Query validated.", sanitized_query

    def process_response(
        self,
        response: str,
        source_url: Optional[str] = None,
        is_refusal: bool = False,
    ) -> Tuple[bool, str, Optional[str]]:
        """
        Process a response through output guardrails.

        Args:
            response: LLM-generated response.
            source_url: Source URL to cite.
            is_refusal: True if this is an advisory refusal.

        Returns:
            Tuple of (is_valid, message, final_response)
        """
        logger.info(f"Processing response through output guardrails ({len(response)} chars)")

        # Step 1: Validate response
        is_valid, message, validated_response = self.output_guardrails.validate_response(
            response=response,
            source_url=source_url,
            is_refusal=is_refusal,
        )

        if not is_valid:
            logger.warning(f"Response failed output validation: {message}")
            return False, message, None

        # Step 2: Sanitize response (defensive)
        sanitized_response = self.output_guardrails.sanitize_response(validated_response)

        # Step 3: Append disclaimer and source
        final_response = self.output_guardrails.append_disclaimer(
            response=sanitized_response,
            source_url=source_url,
        )

        logger.info(f"Response passed output guardrails ({len(final_response)} chars)")
        return True, "Response validated.", final_response

    def validate_source_url(self, url: str) -> bool:
        """
        Validate a source URL against domain allowlist.

        Args:
            url: URL to validate.

        Returns:
            True if URL is from allowed domain.
        """
        return self.domain_allowlist.is_domain_allowed(url)

    def get_compliance_report(self) -> dict:
        """
        Get a report of current compliance configuration.

        Returns:
            Dictionary with compliance settings.
        """
        return {
            "allowed_domains": self.domain_allowlist.get_allowed_domains(),
            "pii_patterns": list(self.input_guardrails.pii_patterns.keys()),
            "max_response_sentences": self.output_guardrails.max_sentences,
            "advisory_patterns_count": len(self.output_guardrails.advisory_patterns),
        }


def run_phase_1_4_tests():
    """
    Test the compliance pipeline with various scenarios.

    Returns:
        Dictionary with test results.
    """
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    pipeline = CompliancePipeline()

    print("\n" + "=" * 80)
    print("PHASE 1.4: Compliance Pipeline Testing")
    print("=" * 80)

    # Test cases
    test_cases = {
        "input_guardrails": [
            {
                "name": "Valid factual query",
                "query": "What is the expense ratio of HDFC Mid-Cap Fund?",
                "expected": True,
            },
            {
                "name": "PII - PAN number",
                "query": "My PAN is ABCDE1234F, what is the expense ratio?",
                "expected": False,
            },
            {
                "name": "PII - Email",
                "query": "Send details to user@example.com",
                "expected": True,  # Should strip email and proceed
            },
            {
                "name": "Advisory query",
                "query": "Should I invest in HDFC Mid-Cap Fund?",
                "expected": False,  # ADVISORY_DETECTED
            },
            {
                "name": "Out-of-scope query",
                "query": "Tell me about Bitcoin investment",
                "expected": False,
            },
            {
                "name": "Empty query",
                "query": "",
                "expected": False,
            },
        ],
        "output_guardrails": [
            {
                "name": "Valid response",
                "response": "The expense ratio of HDFC Mid-Cap Fund is 1.03% for direct plan.",
                "source_url": "https://groww.in/mutual-funds/hdfc-mid-cap-fund-direct-growth",
                "is_refusal": False,
                "expected": True,
            },
            {
                "name": "Too many sentences",
                "response": "The expense ratio is 1.03%. This is for direct plan. The regular plan is 1.55%. Please check the website.",
                "source_url": "https://groww.in/mutual-funds/hdfc-mid-cap-fund-direct-growth",
                "is_refusal": False,
                "expected": False,
            },
            {
                "name": "Advisory language",
                "response": "You should invest in this fund for better returns.",
                "source_url": "https://groww.in/mutual-funds/hdfc-mid-cap-fund-direct-growth",
                "is_refusal": False,
                "expected": False,
            },
            {
                "name": "Invalid source URL",
                "response": "The expense ratio is 1.03%.",
                "source_url": "https://example.com/invalid",
                "is_refusal": False,
                "expected": False,
            },
            {
                "name": "Refusal response",
                "response": "I cannot provide investment advice. Please consult a SEBI-registered advisor.",
                "source_url": None,
                "is_refusal": True,
                "expected": True,
            },
        ],
        "domain_validation": [
            {
                "name": "Valid Groww URL",
                "url": "https://groww.in/mutual-funds/hdfc-mid-cap-fund-direct-growth",
                "expected": True,
            },
            {
                "name": "Invalid domain",
                "url": "https://example.com/something",
                "expected": False,
            },
            {
                "name": "URL with www",
                "url": "https://www.groww.in/mutual-funds",
                "expected": True,
            },
        ],
    }

    # Run tests
    results = {}

    # Test 1: Input Guardrails
    print("\n" + "-" * 80)
    print("Test Suite 1: Input Guardrails")
    print("-" * 80)

    input_results = []
    for test in test_cases["input_guardrails"]:
        is_valid, message, sanitized = pipeline.process_query(test["query"])

        # For advisory, we check if message contains ADVISORY_DETECTED
        if test["expected"] is False and message == "ADVISORY_DETECTED":
            passed = True
        else:
            passed = is_valid == test["expected"]

        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"\n{status}: {test['name']}")
        print(f"  Query: {test['query'][:60]}...")
        print(f"  Expected: {test['expected']}, Got: {is_valid}")
        print(f"  Message: {message}")

        input_results.append({
            "name": test["name"],
            "passed": passed,
            "expected": test["expected"],
            "actual": is_valid,
        })

    results["input_guardrails"] = input_results

    # Test 2: Output Guardrails
    print("\n" + "-" * 80)
    print("Test Suite 2: Output Guardrails")
    print("-" * 80)

    output_results = []
    for test in test_cases["output_guardrails"]:
        is_valid, message, final_response = pipeline.process_response(
            response=test["response"],
            source_url=test["source_url"],
            is_refusal=test["is_refusal"],
        )

        passed = is_valid == test["expected"]
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"\n{status}: {test['name']}")
        print(f"  Response: {test['response'][:60]}...")
        print(f"  Expected: {test['expected']}, Got: {is_valid}")
        print(f"  Message: {message}")

        output_results.append({
            "name": test["name"],
            "passed": passed,
            "expected": test["expected"],
            "actual": is_valid,
        })

    results["output_guardrails"] = output_results

    # Test 3: Domain Validation
    print("\n" + "-" * 80)
    print("Test Suite 3: Domain Validation")
    print("-" * 80)

    domain_results = []
    for test in test_cases["domain_validation"]:
        is_valid = pipeline.validate_source_url(test["url"])
        passed = is_valid == test["expected"]

        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"\n{status}: {test['name']}")
        print(f"  URL: {test['url']}")
        print(f"  Expected: {test['expected']}, Got: {is_valid}")

        domain_results.append({
            "name": test["name"],
            "passed": passed,
            "expected": test["expected"],
            "actual": is_valid,
        })

    results["domain_validation"] = domain_results

    # Summary
    print("\n" + "=" * 80)
    print("PHASE 1.4 TESTING SUMMARY")
    print("=" * 80)

    total_tests = 0
    passed_tests = 0

    for suite_name, suite_results in results.items():
        suite_passed = sum(1 for r in suite_results if r["passed"])
        suite_total = len(suite_results)
        total_tests += suite_total
        passed_tests += suite_passed

        print(f"\n{suite_name}:")
        print(f"  Passed: {suite_passed}/{suite_total}")

    print(f"\nTotal: {passed_tests}/{total_tests} tests passed")

    if passed_tests == total_tests:
        print("\n✅ ALL TESTS PASSED!")
    else:
        print(f"\n⚠️  {total_tests - passed_tests} test(s) failed")

    return results


if __name__ == "__main__":
    results = run_phase_1_4_tests()
