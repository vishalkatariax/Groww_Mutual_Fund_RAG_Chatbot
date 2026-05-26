# Edge Cases — Phase 7: Testing, Evaluation & Deployment

## Overview

This document catalogs all identified edge cases for Phase 7 of the Mutual Fund FAQ Assistant. Each edge case includes a description, expected behavior, and mitigation strategy.

---

## 1. Unit Testing Edge Cases

### 1.1 — Intent Classifier Returns Unrecognized Intent

| Field | Detail |
|---|---|
| **Edge Case** | The LLM-based intent classifier returns a string not in the expected set (`FACTUAL`, `ADVISORY`, `AMBIGUOUS`), e.g., `"MIXED"` or `"UNKNOWN"` |
| **Trigger** | LLM generates an unexpected classification label |
| **Impact** | Downstream routing logic crashes on unmatched intent |
| **Expected Behavior** | Default to `AMBIGUOUS` for any unrecognized intent |
| **Mitigation** | Add a default case in the intent router: if intent not in allowed set, treat as `AMBIGUOUS`; log unrecognized intents for prompt tuning; unit test should verify all unknown intents route to the clarification handler |

### 1.2 — Response Validator Receives Non-String Input

| Field | Detail |
|---|---|
| **Edge Case** | Response validator function receives `None`, a list, or an integer instead of a string |
| **Trigger** | LLM API returns a non-standard response format |
| **Impact** | Validator crashes trying to call string methods (e.g., `.split()`) |
| **Expected Behavior** | Validator should handle non-string input gracefully |
| **Mitigation** | Type-check input at validator entry: if not a string, return invalid immediately; unit test with `None`, `123`, `[]`, `{}` as inputs; all should return `valid=False` |

### 1.3 — Chunking Logic Produces Zero Chunks

| Field | Detail |
|---|---|
| **Edge Case** | The chunker receives valid text but produces 0 chunks (e.g., text is all whitespace after cleaning) |
| **Trigger** | Aggressive content cleaning strips all text |
| **Impact** | No data enters the vector store; downstream tests fail |
| **Expected Behavior** | Chunker should return an empty list (not crash); caller should handle gracefully |
| **Mitigation** | Unit test with empty string, whitespace-only, and stripped-to-nothing inputs; assert chunker returns `[]` without error; caller should log a warning if 0 chunks produced |

### 1.4 — PII Detector Regex Matches Across Word Boundaries

| Field | Detail |
|---|---|
| **Edge Case** | PAN regex `[A-Z]{5}[0-9]{4}[A-Z]` matches inside a longer string like "ABCDE1234FGHIJ" (false positive) |
| **Trigger** | Text contains consecutive uppercase letters and digits that look like PAN |
| **Impact** | False positive PII detection; legitimate queries rejected |
| **Expected Behavior** | PAN regex should use word boundaries |
| **Mitigation** | Use `\b[A-Z]{5}[0-9]{4}[A-Z]\b` with word boundaries; unit test with false positive cases; verify that "ABCDE1234F" matches but "ABCDE1234FGHIJ" does not |

### 1.5 — Test Fixtures Become Stale

| Field | Detail |
|---|---|
| **Edge Case** | Test fixtures (expected expense ratios, fund names, URLs) become outdated when Groww pages are updated |
| **Trigger** | Groww updates fund data; test expectations don't match reality |
| **Impact** | Tests fail on valid data; false negatives |
| **Expected Behavior** | Test fixtures should be clearly separated from live data |
| **Mitigation** | Label all test fixtures with `# Fixture date: 2026-05-26`; test the pipeline logic, not the specific data values; use mock data that tests format/structure compliance, not exact numbers; add a comment noting that specific values may need updates |

---

## 2. Integration Testing Edge Cases

### 2.1 — End-to-End Test Fails Due to LLM Non-Determinism

| Field | Detail |
|---|---|
| **Edge Case** | Even with `temperature=0.0`, LLM responses vary slightly between runs, causing assertion failures |
| **Trigger** | Running integration tests multiple times |
| **Impact** | Flaky tests; CI pipeline fails intermittently |
| **Expected Behavior** | Integration tests should test structure, not exact wording |
| **Mitigation** | Assert response contains expected key phrases (not exact match); use `assert "expense ratio" in answer.lower()` instead of `assert answer == "..."`; validate response structure (has source_url, has last_updated, ≤ 3 sentences); use mock LLM responses for deterministic CI runs |

### 2.2 — ChromaDB State Leaks Between Tests

| Field | Detail |
|---|---|
| **Edge Case** | A test inserts data into ChromaDB, and the next test sees that leftover data |
| **Trigger** | Tests share a ChromaDB instance without cleanup |
| **Impact** | Tests pass in isolation but fail when run together; false positives |
| **Expected Behavior** | Each test should start with a clean ChromaDB state |
| **Mitigation** | Use a separate test collection (e.g., `mf_faq_corpus_test`); delete and recreate the collection before each test; or use an in-memory ChromaDB instance for testing; add `pytest` fixtures for setup/teardown |

### 2.3 — API Test Server Port Conflict

| Field | Detail |
|---|---|
| **Edge Case** | Integration tests start a test FastAPI server on port 8000, but another process is using that port |
| **Trigger** | Running tests while the dev server is running |
| **Impact** | Test server fails to start; all API tests fail |
| **Expected Behavior** | Test server should use a random available port |
| **Mitigation** | Use `pytest` with `httpx.AsyncClient` (no real server needed); or bind to port 0 (OS assigns available port); pass the test server URL as a fixture |

### 2.4 — External API Calls in Integration Tests

| Field | Detail |
|---|---|
| **Edge Case** | Integration tests call the real OpenAI API, incurring costs and depending on network |
| **Trigger** | Running full integration tests without mocking |
| **Impact** | Test cost; flaky tests due to API issues; slow test execution |
| **Expected Behavior** | Integration tests should mock external API calls by default |
| **Mitigation** | Use `unittest.mock.patch` or `pytest-mock` to mock OpenAI API calls; provide a `--live` flag for optional real API testing; mock ChromaDB queries with pre-computed results; document the live test flag in test README |

---

## 3. Evaluation Dataset Edge Cases

### 3.1 — Golden Test Set Contains Ambiguous Expected Answers

| Field | Detail |
|---|---|
| **Edge Case** | A test question like "What is the risk level?" could have multiple valid answers ("Very High Risk", "High Risk" depending on date) |
| **Trigger** | Riskometer rating changes between factsheet dates |
| **Impact** | Evaluation unfairly penalizes correct answers that don't match the exact expected string |
| **Expected Behavior** | Expected answers should include all valid variants |
| **Mitigation** | Define expected answers as a set of acceptable values: `expected: ["Very High Risk", "High Risk"]`; or use partial matching: `assert any(v in answer for v in expected_values)`; document the date of the expected answer |

### 3.2 — Advisory Query Test Cases Not Comprehensive Enough

| Field | Detail |
|---|---|
| **Edge Case** | The advisory test set only includes obvious advisory queries ("Should I invest?") but misses subtle ones ("Is this fund safe?") |
| **Trigger** | Limited test imagination |
| **Impact** | Advisory detector passes tests but fails in production on subtle cases |
| **Expected Behavior** | Advisory test set should cover the full spectrum of advisory phrasing |
| **Mitigation** | Categorize advisory queries: direct, indirect, hypothetical, comparative, normative; ensure at least 3 test cases per category; add adversarial test cases specifically designed to bypass the classifier; review and expand test set after production deployment |

### 3.3 — Edge Case Test for Performance Comparison Refusal

| Field | Detail |
|---|---|
| **Edge Case** | User asks "What is the 1-year return of HDFC Mid-Cap Fund?" — this is factual (a specific number) but touches performance |
| **Trigger** | Performance data exists on Groww pages |
| **Impact** | Inconsistent handling: sometimes answered, sometimes refused |
| **Expected Behavior** | Stating a factual return number is acceptable; comparing returns is not |
| **Mitigation** | Clearly define in the golden test set: single-fund return query = factual (answer with value + source); multi-fund return comparison = advisory (refuse); document this distinction explicitly in the evaluation criteria |

### 3.4 — Test Dataset References Specific Fund Data That Changes

| Field | Detail |
|---|---|
| **Edge Case** | Golden test expects expense ratio of 1.03% but HDFC revises it to 0.95% |
| **Trigger** | AMC updates fees; Groww page reflects new data |
| **Impact** | All accuracy tests fail after the change |
| **Expected Behavior** | Test should validate that an answer is present and sourced, not that a specific number matches |
| **Mitigation** | Split test validation into: (a) structural checks (has answer, has source, ≤ 3 sentences) — always valid; (b) value checks (exact number) — may need periodic updates; mark value-dependent tests as "data-sensitive" with update date |

---

## 4. Quality Metrics Edge Cases

### 4.1 — Factual Accuracy Drops Below 95% Target

| Field | Detail |
|---|---|
| **Edge Case** | System achieves only 85% factual accuracy in evaluation |
| **Trigger** | Poor retrieval quality, embedding model mismatch, or stale corpus |
| **Impact** | Unreliable answers in production |
| **Expected Behavior** | System should not be deployed until accuracy target is met |
| **Mitigation** | If accuracy < 95%, block deployment; generate a failure report with specific failing questions; investigate: (a) retrieval relevance, (b) context quality, (c) LLM adherence; iterate on prompt engineering and chunking strategy; re-run evaluation after fixes |

### 4.2 — Advisory Refusal Rate Not 100%

| Field | Detail |
|---|---|
| **Edge Case** | 1 out of 15 advisory queries is not properly refused |
| **Trigger** | Subtle advisory phrasing bypasses the intent classifier |
| **Impact** | Compliance violation |
| **Expected Behavior** | 100% refusal rate is non-negotiable; even 1 miss is a deployment blocker |
| **Mitigation** | If any advisory query is not refused, treat as a critical failure; do not deploy; add the missed case to the test set; strengthen the intent classifier (additional few-shot examples); re-run full evaluation |

### 4.3 — Latency p95 Exceeds 3 Seconds

| Field | Detail |
|---|---|
| **Edge Case** | End-to-end response time exceeds 3 seconds for 5% of queries |
| **Trigger** | Slow LLM API, large context, or network latency |
| **Impact** | Poor user experience |
| **Expected Behavior** | Optimize the pipeline to meet the latency target |
| **Mitigation** | Profile the pipeline: measure time at each stage (embedding, retrieval, LLM); optimize the slowest stage; reduce Top-K from 5 to 3 if retrieval is fast enough; use a smaller LLM (GPT-4o-mini is already optimized); implement response streaming; cache frequent queries |

---

## 5. Deployment Edge Cases

### 5.1 — Docker Compose Fails to Start All Services

| Field | Detail |
|---|---|
| **Edge Case** | `docker-compose up` starts the backend but the frontend container fails |
| **Trigger** | Build error, missing environment variable, or port conflict |
| **Impact** | Partial deployment; backend running but no UI |
| **Expected Behavior** | Docker Compose should report the failure clearly |
| **Mitigation** | Use `docker-compose up --abort-on-container-exit` in CI; add health checks to all containers; set `restart: unless-stopped` for production; validate all services are healthy with a deployment smoke test script |

### 5.2 — First Request After Deployment Is Very Slow

| Field | Detail |
|---|---|
| **Edge Case** | The first API request after a fresh deployment takes 10+ seconds (cold start) |
| **Trigger** | ChromaDB loading, model initialization, or JIT compilation |
| **Impact** | Bad first impression; monitoring alerts |
| **Expected Behavior** | Implement a warmup phase during deployment |
| **Mitigation** | Add a startup event in FastAPI that: (a) loads ChromaDB collection into memory, (b) sends a test query through the full pipeline; mark the service as "healthy" only after warmup completes; the `/health` endpoint returns 503 during warmup |

### 5.3 — Deployed Version Mismatch Between Frontend and Backend

| Field | Detail |
|---|---|
| **Edge Case** | Frontend is deployed with a newer API contract but backend still runs the old version |
| **Trigger** | Staggered deployment where frontend updates first |
| **Impact** | API calls fail; missing fields cause frontend errors |
| **Expected Behavior** | API versioning should prevent contract mismatches |
| **Mitigation** | Use API versioning (`/api/v1/`); frontend should handle missing fields gracefully (see Phase 6 edge cases); deploy backend before frontend; use feature flags for new fields; add API contract testing in CI |

### 5.4 — Production Logs Fill Up Disk

| Field | Detail |
|---|---|
| **Edge Case** | Verbose logging in production fills up the server disk over time |
| **Trigger** | High query volume with detailed logging enabled |
| **Impact** | Server runs out of disk space; services crash |
| **Expected Behavior** | Log rotation should be configured |
| **Mitigation** | Configure log rotation in Docker: `max-size: "10m"`, `max-file: "3"`; set log level to `INFO` in production (not `DEBUG`); use structured JSON logging for easier parsing; monitor disk usage; archive old logs to external storage |

### 5.5 — SSL Certificate Expiry

| Field | Detail |
|---|---|
| **Edge Case** | SSL certificate for the production domain expires |
| **Trigger** | Certificate not renewed before expiry |
| **Impact** | Users cannot access the application; browser shows security warning |
| **Expected Behavior** | Auto-renew certificates; monitor expiry dates |
| **Mitigation** | Use Let's Encrypt with certbot auto-renewal; set up monitoring for certificate expiry (alert 30 days before); if using cloud hosting, use managed SSL; add SSL expiry check to the `/health` endpoint |

### 5.6 — Rollback Needed After Bad Deployment

| Field | Detail |
|---|---|
| **Edge Case** | A deployment introduces a critical bug and needs to be rolled back |
| **Trigger** | Post-deployment testing reveals a critical issue |
| **Impact** | System is broken in production |
| **Expected Behavior** | Quick rollback to the previous working version |
| **Mitigation** | Tag Docker images with version numbers; maintain the previous version's container image; implement blue-green deployment for zero-downtime rollbacks; test rollback procedure in staging; document rollback steps in deployment runbook |

---

## 6. CI/CD Pipeline Edge Cases

### 6.1 — CI Pipeline Fails on Lint but Code Is Functionally Correct

| Field | Detail |
|---|---|
| **Edge Case** | `ruff` or `mypy` reports style/type errors that don't affect functionality |
| **Trigger** | Code written without strict adherence to linting rules |
| **Impact** | CI blocks deployment of working code |
| **Expected Behavior** | Linting should be enforced; fix the errors, don't skip the checks |
| **Mitigation** | Configure ruff/mypy rules at the start of the project; run linting locally before pushing; use `ruff format` for auto-fixable issues; never disable lint checks in CI; if a rule is too strict, configure it in `ruff.toml` or `mypy.ini` |

### 6.2 — Test Coverage Below 80% Target

| Field | Detail |
|---|---|
| **Edge Case** | Code coverage is 72% after writing all planned tests |
| **Trigger** | Some code paths not covered (e.g., error handlers, edge cases) |
| **Impact** | CI may block merge; untested code in production |
| **Expected Behavior** | Add tests for uncovered code paths |
| **Mitigation** | Generate coverage report (`pytest --cov`); identify uncovered lines; add targeted tests for error handlers, fallback paths, and guardrails; if a path is truly unreachable, add `pragma: no cover`; document why coverage is below target if it cannot be reached |

### 6.3 — GitHub Actions Runner Runs Out of Resources

| Field | Detail |
|---|---|
| **Edge Case** | CI job runs out of memory or disk space on the GitHub Actions runner |
| **Trigger** | Large dependency installation, Docker image builds, or test data |
| **Impact** | CI pipeline fails with OOM error |
| **Expected Behavior** | Optimize CI resource usage |
| **Mitigation** | Cache pip dependencies between runs; use smaller Docker images (Alpine-based); split test jobs into smaller parallel jobs; don't run the full ChromaDB in CI — use mocks; monitor CI resource usage |

---

## Edge Case Summary Table

| # | Edge Case | Severity | Phase Component | Auto-Recoverable |
|---|---|---|---|---|
| 1.1 | Unrecognized intent from classifier | Medium | Unit Testing | Yes (default to AMBIGUOUS) |
| 1.2 | Non-string input to validator | Medium | Unit Testing | Yes (type check) |
| 1.3 | Chunker produces zero chunks | Medium | Unit Testing | Yes (return empty list) |
| 1.4 | PII regex false positives | Medium | Unit Testing | Yes (word boundaries) |
| 1.5 | Stale test fixtures | Low | Unit Testing | No (manual update) |
| 2.1 | LLM non-determinism in tests | Medium | Integration Testing | Yes (structure-based assertions) |
| 2.2 | ChromaDB state leaks between tests | High | Integration Testing | Yes (test fixtures / cleanup) |
| 2.3 | API test server port conflict | Medium | Integration Testing | Yes (random port / httpx) |
| 2.4 | External API calls in tests | High | Integration Testing | Yes (mocking) |
| 3.1 | Ambiguous expected answers | Medium | Evaluation Dataset | Yes (acceptable value sets) |
| 3.2 | Incomplete advisory test cases | High | Evaluation Dataset | No (manual expansion) |
| 3.3 | Performance query classification | Medium | Evaluation Dataset | Yes (clear criteria docs) |
| 3.4 | Changing fund data in test set | Medium | Evaluation Dataset | Yes (structural vs value checks) |
| 4.1 | Accuracy below 95% target | Critical | Quality Metrics | No (block deployment) |
| 4.2 | Advisory refusal < 100% | Critical | Quality Metrics | No (block deployment) |
| 4.3 | Latency p95 > 3 seconds | High | Quality Metrics | Yes (optimize pipeline) |
| 5.1 | Docker Compose partial failure | High | Deployment | Yes (health checks) |
| 5.2 | Cold start latency | Medium | Deployment | Yes (warmup phase) |
| 5.3 | Frontend/backend version mismatch | High | Deployment | Yes (API versioning) |
| 5.4 | Production logs fill disk | Medium | Deployment | Yes (log rotation) |
| 5.5 | SSL certificate expiry | High | Deployment | Yes (auto-renewal) |
| 5.6 | Rollback needed | Critical | Deployment | Yes (blue-green / tagged images) |
| 6.1 | Lint failures on correct code | Low | CI/CD | No (fix code) |
| 6.2 | Test coverage < 80% | Medium | CI/CD | Partial (add tests) |
| 6.3 | CI runner resource exhaustion | Medium | CI/CD | Yes (caching / mocking) |
