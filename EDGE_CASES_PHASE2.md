# Edge Cases — Phase 2: Chunking, Embedding & Vector Store Setup

## Overview

This document catalogs all identified edge cases for Phase 2 of the Mutual Fund FAQ Assistant. Each edge case includes a description, expected behavior, and mitigation strategy.

---

## 1. Chunking Engine Edge Cases

### 1.1 — Heading-Based Split Fails (No Headings)

| Field | Detail |
|---|---|
| **Edge Case** | A Groww scheme page's clean text may have no HTML headings (H1/H2/H3) after conversion, making heading-based chunking impossible |
| **Trigger** | Groww renders all content in `<div>` sections without semantic heading tags |
| **Impact** | Heading-based chunker produces a single massive chunk |
| **Expected Behavior** | Chunker should fall back to fixed-size chunking |
| **Mitigation** | If 0 heading splits are detected, automatically switch to fixed-size mode (512 tokens, 64 overlap); log the fallback event |

### 1.2 — Very Short Sections After Heading Split

| Field | Detail |
|---|---|
| **Edge Case** | A heading split may produce a chunk with only 1–2 sentences (e.g., a "Riskometer" section with just "High") |
| **Trigger** | Page has many small heading-separated sections |
| **Impact** | Vector search retrieves overly sparse chunks with insufficient context |
| **Expected Behavior** | Merge adjacent short chunks until minimum token threshold is met |
| **Mitigation** | If chunk < 50 tokens, merge with the next chunk; preserve both section headings in metadata; log merged chunks |

### 1.3 — Very Long Sections (No Heading Breaks)

| Field | Detail |
|---|---|
| **Edge Case** | A single section (e.g., "Portfolio Holdings" table) may span 2000+ tokens with no heading break |
| **Trigger** | HDFC Mid-Cap Fund page has a large holdings table under one heading |
| **Impact** | Fixed-size fallback produces chunks that split mid-table or mid-sentence |
| **Expected Behavior** | Long sections should be split at sentence boundaries, not mid-word |
| **Mitigation** | Split at sentence boundaries (period + space) closest to the target chunk size; never split in the middle of a number (e.g., "1.03" should not become "1." + "03"); table rows should not be split across chunks |

### 1.4 — Table Rows Split Across Chunks

| Field | Detail |
|---|---|
| **Edge Case** | Fixed-size chunking may split a table mid-row (e.g., "Exit Load: |" in one chunk and "1% for units < 1 year" in the next) |
| **Trigger** | Tables that exceed chunk size limit |
| **Impact** | Incomplete data retrieved during vector search; LLM receives partial table rows |
| **Expected Behavior** | Table rows must remain intact within a single chunk |
| **Mitigation** | Detect table-like patterns (repeated delimiters: `|`, tab-separated); treat each table row as an atomic unit; if a table row doesn't fit in remaining chunk space, move it to the next chunk; add overlap to include the table header row in each chunk that contains table data |

### 1.5 — Overlap Creates Near-Duplicate Chunks

| Field | Detail |
|---|---|
| **Edge Case** | 64-token overlap between consecutive chunks may cause near-duplicate vectors |
| **Trigger** | Short documents where overlap is a high % of chunk content |
| **Impact** | Vector search returns multiple nearly-identical chunks, wasting Top-K slots |
| **Expected Behavior** | Deduplication during retrieval should filter near-duplicate results |
| **Mitigation** | During context assembly (Phase 3), apply cosine similarity check between retrieved chunks — if > 0.95, keep only the higher-scoring one; log when dedup occurs |

### 1.6 — Chunk Contains Only Numbers / Symbols

| Field | Detail |
|---|---|
| **Edge Case** | A chunk may contain only numeric data (e.g., a row of NAV values: "45.23 44.98 44.67 ...") without any textual context |
| **Trigger** | Table-heavy sections where the header is in a different chunk |
| **Impact** | Embedding model produces a low-quality vector; retrieval may match on irrelevant numeric queries |
| **Expected Behavior** | Chunks should contain sufficient textual context for meaningful embedding |
| **Mitigation** | If chunk is > 70% numbers/symbols by character count, merge with the previous chunk; prepend the section heading to the chunk text as context |

---

## 2. Embedding Pipeline Edge Cases

### 2.1 — OpenAI API Rate Limit / Timeout

| Field | Detail |
|---|---|
| **Edge Case** | Embedding API may rate limit (429) or timeout when processing a large batch of chunks |
| **Trigger** | Embedding 200+ chunks in a single batch request |
| **Impact** | Embedding generation fails; vector store remains incomplete |
| **Expected Behavior** | Implement retry with exponential backoff and reduce batch size |
| **Mitigation** | Start with batch size of 100; on 429, reduce to 25 and retry; on timeout, split batch in half; max 3 retries per batch; log all API errors with timestamps |

### 2.2 — OpenAI API Key Invalid / Expired

| Field | Detail |
|---|---|
| **Edge Case** | The OpenAI API key may be invalid, expired, or have insufficient quota |
| **Trigger** | First embedding request after key rotation or quota exhaustion |
| **Impact** | Entire embedding pipeline fails |
| **Expected Behavior** | Fail fast with a clear error message; do not silently proceed with empty embeddings |
| **Mitigation** | Validate API key with a single test embedding before batch processing; if auth fails, abort and alert; provide fallback to local embedding model (BAAI/bge-small-en-v1.5) |

### 2.3 — Embedding Dimension Mismatch

| Field | Detail |
|---|---|
| **Edge Case** | If the embedding model is changed (e.g., from OpenAI 1536-dim to BGE 384-dim), existing vectors in ChromaDB become incompatible |
| **Trigger** | Switching embedding providers between ingestion runs |
| **Impact** | Vector search returns garbage results or crashes |
| **Expected Behavior** | ChromaDB collection should be recreated when embedding model changes |
| **Mitigation** | Store `embedding_model` and `embedding_dimensions` in collection metadata; on startup, verify these match the configured model; if mismatch detected, force re-ingestion with warning log |

### 2.4 — Empty Chunk Text Sent to Embedding API

| Field | Detail |
|---|---|
| **Edge Case** | After chunking and cleaning, a chunk may have empty text (all content stripped as boilerplate) |
| **Trigger** | Aggressive boilerplate removal strips all content from a short chunk |
| **Impact** | OpenAI API returns an error for empty input |
| **Expected Behavior** | Empty chunks should be filtered out before embedding |
| **Mitigation** | Validate `chunk_text` is non-empty and > 10 characters before sending to embedding API; log and discard empty chunks; update chunk count in ingestion report |

### 2.5 — Local Embedding Model (BGE) Out of Memory

| Field | Detail |
|---|---|
| **Edge Case** | Running BAAI/bge-small-en-v1.5 locally may cause OOM on resource-constrained machines |
| **Trigger** | Batch embedding on a machine with < 4GB RAM |
| **Impact** | Process crashes; partial embeddings stored |
| **Expected Behavior** | Process should reduce batch size and retry |
| **Mitigation** | Process chunks one at a time if batch OOM occurs; use `torch.no_grad()` context; monitor memory usage; if OOM persists, fall back to OpenAI cloud embedding |

---

## 3. Vector Store Edge Cases

### 3.1 — ChromaDB Persistence Failure

| Field | Detail |
|---|---|
| **Edge Case** | ChromaDB fails to persist data to disk (e.g., disk full, permission error) |
| **Trigger** | Writing to `./data/chroma_db` when disk is at capacity |
| **Impact** | All embeddings lost on restart; must re-ingest |
| **Expected Behavior** | Persistence errors should be caught and reported immediately |
| **Mitigation** | Check disk space before starting ingestion; wrap persist operations in try/except; maintain a backup copy of the vector store after each successful ingestion; log persistence status |

### 3.2 — Duplicate Chunk IDs in ChromaDB

| Field | Detail |
|---|---|
| **Edge Case** | Re-running ingestion without clearing ChromaDB may produce duplicate chunk IDs |
| **Trigger** | Running the ingestion pipeline twice |
| **Impact** | ChromaDB may overwrite or error on duplicate IDs; vector counts become inaccurate |
| **Expected Behavior** | Re-ingestion should either update existing entries or clear the collection first |
| **Mitigation** | Before ingestion, check if collection already has data; if yes, prompt to either (a) clear and re-ingest, or (b) upsert (update + insert); use deterministic chunk IDs based on `doc_id + chunk_index` to ensure idempotency |

### 3.3 — Zero Vectors in Collection

| Field | Detail |
|---|---|
| **Edge Case** | After ingestion, the collection may contain 0 vectors (e.g., all chunks failed embedding) |
| **Trigger** | All chunks were empty or all embedding API calls failed |
| **Impact** | Vector search returns no results; assistant cannot answer any query |
| **Expected Behavior** | Ingestion pipeline should validate vector count before completing |
| **Mitigation** | After ingestion, assert `collection.count() > 0`; if 0, log critical error and abort; require manual intervention before proceeding to Phase 3 |

### 3.4 — Cosine Similarity Returns No Results Above Threshold

| Field | Detail |
|---|---|
| **Edge Case** | Vector search with `min_score: 0.6` may return 0 results for a well-formed query |
| **Trigger** | Query embedding is semantically distant from all stored chunks (e.g., user uses uncommon phrasing) |
| **Impact** | Assistant returns "I could not find this information" for valid queries |
| **Expected Behavior** | Gradually lower the threshold before giving up |
| **Mitigation** | If 0 results at 0.6, retry at 0.4; if still 0, retry at 0.2; if still 0, return fallback message; log the threshold level at which results were found |

### 3.5 — ChromaDB Collection Metadata Lost

| Field | Detail |
|---|---|
| **Edge Case** | ChromaDB metadata (embedding model name, dimensions) may be lost after an upgrade or corruption |
| **Trigger** | ChromaDB version upgrade or storage corruption |
| **Impact** | Cannot verify embedding model compatibility |
| **Expected Behavior** | Metadata should be re-initialized if missing |
| **Mitigation** | Store collection metadata both in ChromaDB and in a separate `metadata.json` file; on startup, if ChromaDB metadata is missing, attempt to restore from `metadata.json` |

---

## Edge Case Summary Table

| # | Edge Case | Severity | Phase Component | Auto-Recoverable |
|---|---|---|---|---|
| 1.1 | No headings for split | Medium | Chunking Engine | Yes (fallback to fixed-size) |
| 1.2 | Very short sections | Medium | Chunking Engine | Yes (merge adjacent) |
| 1.3 | Very long sections | Medium | Chunking Engine | Yes (sentence boundary split) |
| 1.4 | Table rows split across chunks | High | Chunking Engine | Yes (atomic row handling) |
| 1.5 | Near-duplicate chunks from overlap | Medium | Chunking Engine | Yes (retrieval dedup) |
| 1.6 | Chunk is only numbers/symbols | Medium | Chunking Engine | Yes (merge + prepend heading) |
| 2.1 | API rate limit / timeout | High | Embedding Pipeline | Yes (backoff + retry) |
| 2.2 | Invalid API key | High | Embedding Pipeline | No (manual intervention) |
| 2.3 | Embedding dimension mismatch | High | Vector Store | No (force re-ingestion) |
| 2.4 | Empty chunk text | Medium | Embedding Pipeline | Yes (filter + discard) |
| 2.5 | Local model OOM | Medium | Embedding Pipeline | Yes (reduce batch / fallback) |
| 3.1 | Persistence failure | High | Vector Store | No (manual intervention) |
| 3.2 | Duplicate chunk IDs | Medium | Vector Store | Yes (upsert / clear-first) |
| 3.3 | Zero vectors after ingestion | Critical | Vector Store | No (manual intervention) |
| 3.4 | No results above similarity threshold | Medium | Vector Store | Yes (lower threshold) |
| 3.5 | Collection metadata lost | Low | Vector Store | Yes (restore from backup) |
