# Edge Cases — Phase 5: API & Backend Development

## Overview

This document catalogs all identified edge cases for Phase 5 of the Mutual Fund FAQ Assistant. Each edge case includes a description, expected behavior, and mitigation strategy.

---

## 1. API Endpoint Edge Cases

### 1.1 — Malformed JSON Request Body

| Field | Detail |
|---|---|
| **Edge Case** | POST /api/v1/chat receives invalid JSON (e.g., missing closing brace, trailing comma) |
| **Trigger** | Frontend bug or manual API testing error |
| **Impact** | FastAPI returns 422 Unprocessable Entity; may expose internal error details |
| **Expected Behavior** | Return a clean 422 error with user-friendly message; no stack trace |
| **Mitigation** | FastAPI's built-in Pydantic validation handles this; customize the 422 handler to return: `{"error": "Invalid request format. Please provide a valid JSON with 'query' field."}`; never expose raw Pydantic error details in production |

### 1.2 — Missing Required Fields

| Field | Detail |
|---|---|
| **Edge Case** | POST /api/v1/chat receives `{}` or `{"session_id": "abc"}` without the `query` field |
| **Trigger** | Client omits the required `query` field |
| **Impact** | Pipeline receives None for query; crashes downstream |
| **Expected Behavior** | Return 422 with specific field error |
| **Mitigation** | Pydantic model enforces `query: str` as required; FastAPI returns 422 automatically; customize error to: `{"error": "The 'query' field is required."}` |

### 1.3 — Query Field Is Not a String

| Field | Detail |
|---|---|
| **Edge Case** | POST /api/v1/chat receives `{"query": 12345}` or `{"query": ["list", "of", "strings"]}` |
| **Trigger** | Client sends wrong data type |
| **Impact** | Pipeline expects string; may crash or produce unexpected behavior |
| **Expected Behavior** | Return 422 with type mismatch error |
| **Mitigation** | Pydantic type validation rejects non-string `query`; return: `{"error": "The 'query' field must be a string."}` |

### 1.4 — Extremely Large Request Body

| Field | Detail |
|---|---|
| **Edge Case** | POST /api/v1/chat receives a query with > 10,000 characters |
| **Trigger** | User pastes a huge block of text or a malicious payload |
| **Impact** | Increased processing time; potential DoS vector |
| **Expected Behavior** | Reject queries exceeding a reasonable length |
| **Mitigation** | Add Pydantic field validator: `query: str = Field(max_length=1000)`; return 422: `{"error": "Query must be 1000 characters or less."}`; log rejected long queries |

### 1.5 — Concurrent Requests Exceeding Rate Limit

| Field | Detail |
|---|---|
| **Edge Case** | More than 30 requests per minute from a single IP |
| **Trigger** | Bot crawling, load testing, or accidental frontend loop |
| **Impact** | Backend overwhelmed; degraded performance for all users |
| **Expected Behavior** | Return 429 Too Many Requests |
| **Mitigation** | Implement rate limiting middleware (e.g., `slowapi`); configure 30 req/min per IP; return 429 with `Retry-After` header; log rate-limited IPs for abuse monitoring |

### 1.6 — CORS Preflight Request from Unknown Origin

| Field | Detail |
|---|---|
| **Edge Case** | A browser from an unexpected origin (not localhost:3000) sends a CORS preflight OPTIONS request |
| **Trigger** | App accessed from a different domain or port |
| **Impact** | Browser blocks the request; frontend cannot communicate with backend |
| **Expected Behavior** | Only allow CORS from configured origins |
| **Mitigation** | Configure CORS middleware with explicit `allow_origins` from `.env`; in development, allow `http://localhost:3000`; in production, allow only the deployed frontend domain; reject all other origins with 403 |

---

## 2. RAG Pipeline Integration Edge Cases

### 2.1 — ChromaDB Not Initialized on Startup

| Field | Detail |
|---|---|
| **Edge Case** | Backend starts but ChromaDB collection is empty (first run without ingestion) |
| **Trigger** | Fresh deployment without running the ingestion pipeline first |
| **Impact** | All queries return "not found"; poor user experience |
| **Expected Behavior** | `/health` endpoint should report empty vector store; `/chat` should return informative message |
| **Mitigation** | On startup, check `collection.count()`; if 0, set a global flag `corpus_loaded=False`; `/health` returns `{"status": "degraded", "vector_store_docs": 0}`; `/chat` returns: "The assistant is still being set up. Please try again in a few minutes." |

### 2.2 — ChromaDB Connection Lost During Request

| Field | Detail |
|---|---|
| **Edge Case** | ChromaDB persistence file is corrupted or locked mid-request |
| **Trigger** | Concurrent write + read operations on SQLite-backed ChromaDB |
| **Impact** | Vector search fails; 500 error returned |
| **Expected Behavior** | Graceful degradation; return cached or fallback response |
| **Mitigation** | Wrap ChromaDB queries in try/except; if connection fails, return: "I'm experiencing a temporary issue. Please try again."; log the error; implement a health check that monitors ChromaDB connectivity |

### 2.3 — LLM API Key Rotation During Runtime

| Field | Detail |
|---|---|
| **Edge Case** | OpenAI API key is rotated while the backend is running |
| **Trigger** | Key compromised or regular rotation policy |
| **Impact** | All LLM calls fail with 401 |
| **Expected Behavior** | Backend should reload configuration without restart |
| **Mitigation** | Read API key from environment on each request (with caching for 5 min); if 401 detected, invalidate cache and re-read from env; log authentication failures; alert on repeated 401s |

### 2.4 — LLM API Quota Exhausted

| Field | Detail |
|---|---|
| **Edge Case** | OpenAI account runs out of credits or hits monthly spend limit |
| **Trigger** | Heavy usage or billing issue |
| **Impact** | All LLM calls fail with 429 or 402 |
| **Expected Behavior** | Fall back to local LLM (Llama 3 via Ollama) |
| **Mitigation** | If OpenAI returns 429/402, switch to fallback LLM provider; log the fallback event; monitor remaining quota via OpenAI dashboard; alert when < 10% quota remaining |

---

## 3. Configuration Management Edge Cases

### 3.1 — Missing .env File

| Field | Detail |
|---|---|
| **Edge Case** | Application starts without a `.env` file |
| **Trigger** | Fresh clone without copying `.env.example` |
| **Impact** | Missing required config (API keys, DB paths); crash on startup |
| **Expected Behavior** | Fail fast with clear error listing missing variables |
| **Mitigation** | On startup, validate all required env vars; if missing, print: `"ERROR: Missing required environment variables: OPENAI_API_KEY, ... Copy .env.example to .env and fill in the values."`; exit with code 1 |

### 3.2 — Invalid Configuration Values

| Field | Detail |
|---|---|
| **Edge Case** | `.env` contains `RETRIEVAL_TOP_K=abc` (non-integer) or `LLM_TEMPERATURE=5.0` (out of range) |
| **Trigger** | Manual configuration error |
| **Impact** | Unexpected behavior at runtime |
| **Expected Behavior** | Validate all config values on startup; reject invalid values |
| **Mitigation** | Use Pydantic `BaseSettings` for config validation; set type constraints and ranges: `LLM_TEMPERATURE: float = Field(ge=0.0, le=2.0)`; fail fast with descriptive error if validation fails |

### 3.3 — ChromaDB Path Points to Non-Existent Directory

| Field | Detail |
|---|---|
| **Edge Case** | `VECTOR_STORE_PATH=./data/chroma_db` but the `data` directory doesn't exist |
| **Trigger** | First-time setup |
| **Impact** | ChromaDB fails to persist |
| **Expected Behavior** | Auto-create the directory if it doesn't exist |
| **Mitigation** | On startup, `os.makedirs(VECTOR_STORE_PATH, exist_ok=True)`; log directory creation; ensure parent directories also exist |

---

## 4. Docker & Deployment Edge Cases

### 4.1 — Port 8000 Already in Use

| Field | Detail |
|---|---|
| **Edge Case** | Another process is using port 8000 when the backend tries to start |
| **Trigger** | Previous instance not properly stopped; another service on same port |
| **Impact** | Backend fails to start |
| **Expected Behavior** | Clear error message; option to use alternative port |
| **Mitigation** | uvicorn reports "Address already in use"; catch this and print: "Port 8000 is in use. Kill the existing process or set PORT env variable."; allow port configuration via env: `PORT=8001` |

### 4.2 — Docker Container Runs Out of Memory

| Field | Detail |
|---|---|
| **Edge Case** | Backend container exceeds memory limit (especially if using local LLM fallback) |
| **Trigger** | Llama 3 model loading in memory-constrained container |
| **Impact** | Container killed by OOM killer |
| **Expected Behavior** | Set appropriate memory limits; disable local LLM if insufficient memory |
| **Mitigation** | Set Docker memory limit to 2GB minimum (4GB if using local LLM); check available memory on startup; if < 1GB free, disable local LLM fallback and log a warning; monitor memory usage via `/health` endpoint |

### 4.3 — Data Volume Not Mounted

| Field | Detail |
|---|---|
| **Edge Case** | Docker container starts without mounting the `./data` volume |
| **Trigger** | docker-compose.yml misconfiguration |
| **Impact** | ChromaDB data lost on container restart |
| **Expected Behavior** | Data should persist across container restarts |
| **Mitigation** | In docker-compose.yml, define a named volume for `./data`; on startup, check if vector store directory is empty and log a warning; document volume mounting in README |

### 4.4 — Container Time Drift

| Field | Detail |
|---|---|
| **Edge Case** | Docker container's system clock is wrong (common in some Docker setups) |
| **Trigger** | Timezone not set in container |
| **Impact** | `scraped_date` and `last_updated` timestamps are incorrect |
| **Expected Behavior** | Container should use the host's timezone |
| **Mitigation** | Set `TZ=Asia/Kolkata` in Dockerfile; or mount `/etc/localtime` from host; validate timestamps on startup against an external time source |

---

## 5. Middleware & Security Edge Cases

### 5.1 — SQL Injection via Query Field

| Field | Detail |
|---|---|
| **Edge Case** | User sends `{"query": "'; DROP TABLE users; --"}` |
| **Trigger** | Malicious input attempt |
| **Impact** | No SQL database in use (ChromaDB), so no actual injection risk; but should still be sanitized |
| **Expected Behavior** | Input is treated as plain text; no special SQL interpretation |
| **Mitigation** | No SQL is used in the system; ChromaDB queries use parameterized APIs; still, sanitize input by stripping control characters and limiting length; log suspicious patterns for security monitoring |

### 5.2 — XSS via Query or Response

| Field | Detail |
|---|---|
| **Edge Case** | User sends `{"query": "<script>alert('xss')</script>"}` and the LLM reflects it back |
| **Trigger** | Malicious input attempt targeting frontend |
| **Impact** | If frontend renders raw HTML, XSS executes |
| **Expected Behavior** | All user input and LLM output should be treated as plain text |
| **Mitigation** | Frontend must use `textContent` or React's default JSX escaping (auto-escapes HTML); never use `dangerouslySetInnerHTML`; API responses should have `Content-Type: application/json` (never HTML); strip HTML tags from LLM output in response validator |

### 5.3 — Excessive Logging of User Queries

| Field | Detail |
|---|---|
| **Edge Case** | Query logs may accidentally contain PII or sensitive financial questions |
| **Trigger** | Normal logging captures full user queries |
| **Impact** | Privacy violation; PII in log files |
| **Expected Behavior** | Log query metadata but not full query text; strip PII before logging |
| **Mitigation** | Run PII detection before logging; if PII detected, log only: "Query contained PII — rejected"; for non-PII queries, log truncated query (first 50 chars) + query type + response time; never log source URLs with tracking params |

---

## Edge Case Summary Table

| # | Edge Case | Severity | Phase Component | Auto-Recoverable |
|---|---|---|---|---|
| 1.1 | Malformed JSON request | Medium | API Endpoints | Yes (422 error) |
| 1.2 | Missing required fields | Medium | API Endpoints | Yes (422 error) |
| 1.3 | Wrong data type for query | Medium | API Endpoints | Yes (422 error) |
| 1.4 | Extremely large request | Medium | API Endpoints | Yes (validation) |
| 1.5 | Rate limit exceeded | High | Middleware | Yes (429 + Retry-After) |
| 1.6 | CORS from unknown origin | Medium | Middleware | Yes (403 rejection) |
| 2.1 | ChromaDB not initialized | High | RAG Integration | Yes (degraded mode) |
| 2.2 | ChromaDB connection lost | High | RAG Integration | Yes (fallback response) |
| 2.3 | API key rotation during runtime | Medium | Configuration | Yes (cache invalidation) |
| 2.4 | API quota exhausted | High | RAG Integration | Yes (fallback to local LLM) |
| 3.1 | Missing .env file | High | Configuration | No (fail fast) |
| 3.2 | Invalid config values | Medium | Configuration | No (fail fast) |
| 3.3 | ChromaDB path missing | Low | Configuration | Yes (auto-create dir) |
| 4.1 | Port already in use | Medium | Docker | Yes (configurable port) |
| 4.2 | Container OOM | High | Docker | Partial (disable local LLM) |
| 4.3 | Data volume not mounted | High | Docker | No (data loss risk) |
| 4.4 | Container time drift | Low | Docker | Yes (set timezone) |
| 5.1 | SQL injection attempt | Low | Security | Yes (no SQL used) |
| 5.2 | XSS attempt | Medium | Security | Yes (auto-escaping) |
| 5.3 | Excessive query logging | Medium | Security / Privacy | Yes (PII stripping) |
