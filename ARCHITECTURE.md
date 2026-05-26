# Mutual Fund FAQ Assistant — Phase-Wise Architecture

## 1. System Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                        USER INTERFACE (Web Chat)                     │
│  ┌──────────┐  ┌──────────────────┐  ┌──────────────────────────┐  │
│  │ Welcome  │  │ Example Questions │  │ Disclaimer Banner        │  │
│  │ Message  │  │ (3 suggestions)   │  │ "Facts-only. No advice." │  │
│  └──────────┘  └──────────────────┘  └──────────────────────────┘  │
└──────────────────────────────┬──────────────────────────────────────┘
                               │ HTTP / WebSocket
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         API GATEWAY (FastAPI)                        │
│  ┌─────────────┐  ┌──────────────┐  ┌───────────────────────────┐ │
│  │ /chat       │  │ /health      │  │ CORS / Rate Limiting      │ │
│  │ POST        │  │ GET          │  │ Middleware                │ │
│  └──────┬──────┘  └──────────────┘  └───────────────────────────┘ │
└─────────┼───────────────────────────────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      QUERY PROCESSING PIPELINE                       │
│                                                                     │
│  ┌────────────────┐    ┌─────────────────┐    ┌─────────────────┐  │
│  │ Intent         │───▶│ Advisory        │───▶│ Factual Query   │  │
│  │ Classifier     │    │ Refusal Handler  │    │ Pipeline (RAG)  │  │
│  └────────────────┘    └─────────────────┘    └────────┬────────┘  │
└─────────────────────────────────────────────────────────┼───────────┘
                                                          │
          ┌───────────────────────────────────────────────┘
          ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        RAG PIPELINE                                  │
│                                                                     │
│  ┌──────────────┐  ┌───────────────┐  ┌──────────────┐            │
│  │ Embed Query  │▶│ Vector Search  │▶│ Context       │            │
│  │ (OpenAI /    │  │ (Top-K Chunks) │  │ Assembler     │            │
│  │  HuggingFace) │  │               │  │              │            │
│  └──────────────┘  └───────────────┘  └──────┬───────┘            │
│                                               │                     │
│                                               ▼                     │
│  ┌──────────────┐  ┌───────────────┐  ┌──────────────┐            │
│  │ Response     │◀│ LLM Generator  │◀│ Prompt       │            │
│  │ Validator    │  │ (GPT-4o-mini  │  │ Builder      │            │
│  │ & Post-Proc  │  │  / Llama 3)   │  │              │            │
│  └──────────────┘  └───────────────┘  └──────────────┘            │
└─────────────────────────────────────────────────────────────────────┘
          │                                    ▲
          │                                    │
          ▼                                    │
┌─────────────────────────┐    ┌──────────────────────────────────────┐
│   VECTOR STORE          │    │   DOCUMENT CORPUS (Ingestion Phase)  │
│   (ChromaDB /           │    │                                      │
│    Pinecone /           │◀───│  ┌───────────┐  ┌──────────────────┐│
│    Qdrant)              │    │  │ Web       │  │ Chunking &       ││
│                         │    │  │ Scraper   │  │ Embedding Engine  ││
│  ┌───────────────────┐  │    │  └───────────┘  └──────────────────┘│
│  │ Collection:       │  │    │  ┌───────────┐  ┌──────────────────┐│
│  │  mf_faq_corpus    │  │    │  │ Metadata  │  │ Source Validator ││
│  │                   │  │    │  │ Tagger    │  │ (Official-only)  ││
│  └───────────────────┘  │    │  └───────────┘  └──────────────────┘│
└─────────────────────────┘    └─────────────────────────────────────┘
```

---

## 2. Phase-Wise Detailed Architecture

---

### PHASE 1 — Corpus Collection & Data Ingestion

**Duration Estimate:** 1–2 weeks  
**Objective:** Build a curated, verified corpus of official mutual fund documents

#### 1.1 AMC & Scheme Selection

| Decision | Detail |
|---|---|
| Selected AMC | HDFC Mutual Fund |
| Data Source | Groww (groww.in) — sole data source for this project |
| Total URLs | Exactly 5 scheme pages (no additional sources) |

**Selected Schemes:**

| # | Scheme Name | Category | URL |
|---|---|---|---|
| 1 | HDFC Mid-Cap Fund | Mid-Cap | https://groww.in/mutual-funds/hdfc-mid-cap-fund-direct-growth |
| 2 | HDFC Equity Fund | Flexi-Cap / Multi-Cap | https://groww.in/mutual-funds/hdfc-equity-fund-direct-growth |
| 3 | HDFC Focused Fund | Focused / Large-Cap | https://groww.in/mutual-funds/hdfc-focused-fund-direct-growth |
| 4 | HDFC ELSS Tax Saver Fund | ELSS | https://groww.in/mutual-funds/hdfc-elss-tax-saver-fund-direct-plan-growth |
| 5 | HDFC Large Cap Fund | Large-Cap | https://groww.in/mutual-funds/hdfc-large-cap-fund-direct-growth |

#### 1.2 Source Taxonomy

```
Corpus (Groww Only — 5 URLs)
├── https://groww.in/mutual-funds/hdfc-mid-cap-fund-direct-growth
│   └── HDFC Mid-Cap Fund — scheme details, expense ratio, exit load, etc.
├── https://groww.in/mutual-funds/hdfc-equity-fund-direct-growth
│   └── HDFC Equity Fund — scheme details, expense ratio, exit load, etc.
├── https://groww.in/mutual-funds/hdfc-focused-fund-direct-growth
│   └── HDFC Focused Fund — scheme details, expense ratio, exit load, etc.
├── https://groww.in/mutual-funds/hdfc-elss-tax-saver-fund-direct-plan-growth
│   └── HDFC ELSS Tax Saver Fund — scheme details, lock-in, tax info, etc.
└── https://groww.in/mutual-funds/hdfc-large-cap-fund-direct-growth
    └── HDFC Large Cap Fund — scheme details, expense ratio, exit load, etc.

Note: No additional URLs (KIM, SID, Factsheet PDFs, AMC FAQs, AMFI/SEBI pages)
      will be used. All factual data is sourced exclusively from these 5 Groww pages.
```

#### 1.3 Ingestion Pipeline

```
5 Groww URLs (HTML Only)
     │
     ▼
┌──────────────┐     ┌────────────────┐
│ Web Scraper  │────▶│ HTML-to-Text   │
│ (Playwright/ │     │ Converter      │
│  requests)   │     │ (BeautifulSoup)│
└──────────────┘     └────────┬───────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │ Source Validator │
                    │ (Domain Allow-  │
                    │  list:          │
                    │  groww.in only) │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │ Metadata Tagger │
                    │ - scheme_name   │
                    │ - source_url    │
                    │ - amc_name      │
                    │ - category      │
                    │ - scraped_date  │
                    └─────────────────┘
```

#### 1.4 Data Schema for Ingested Documents

```json
{
  "doc_id": "uuid",
  "scheme_name": "HDFC Mid-Cap Fund",
  "amc_name": "HDFC Mutual Fund",
  "source_url": "https://groww.in/mutual-funds/hdfc-mid-cap-fund-direct-growth",
  "category": "mid_cap | flexi_cap | focused | elss | large_cap",
  "content_raw": "...",
  "content_clean": "...",
  "scraped_date": "2026-05-26",
  "last_verified_date": "2026-05-26",
  "is_official": true,
  "domain_verified": true
}
```

#### 1.5 Automated Data Refresh with GitHub Actions

To ensure the corpus always contains the latest data from Groww, we use GitHub Actions as a scheduler:

```yaml
# .github/workflows/data-refresh.yml
name: Refresh MF Corpus Data

on:
  schedule:
    # Run every Monday at 6:00 AM UTC (11:30 AM IST)
    - cron: '0 6 * * 1'
  workflow_dispatch:  # Allow manual trigger
    inputs:
      force_refresh:
        description: 'Force refresh even if no changes detected'
        required: false
        default: 'false'

jobs:
  refresh-corpus:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
          
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          playwright install chromium
          
      - name: Run data ingestion
        env:
          GROQ_API_KEY: ${{ secrets.GROQ_API_KEY }}
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
        run: |
          python scripts/refresh_corpus.py
          
      - name: Check for changes
        run: |
          git diff --exit-code data/processed/ || echo "CHANGES_DETECTED=true" >> $GITHUB_ENV
          
      - name: Commit and push if changes detected
        if: env.CHANGES_DETECTED == 'true' || github.event.inputs.force_refresh == 'true'
        run: |
          git config user.name 'github-actions[bot]'
          git config user.email 'github-actions[bot]@users.noreply.github.com'
          git add data/
          git commit -m "🔄 Auto-refresh: Updated corpus data ($(date +'%Y-%m-%d'))"
          git push
          
      - name: Create PR if significant changes
        if: env.CHANGES_DETECTED == 'true'
        uses: peter-evans/create-pull-request@v5
        with:
          title: "🔄 Auto-refresh: Corpus data updated"
          body: |
            Automated corpus refresh detected. Please review changes:
            - Scraped date: $(date +'%Y-%m-%d')
            - Source: groww.in (5 scheme pages)
            - Changes: See diff for details
          branch: auto-refresh/corpus-update
```

**Benefits:**
- ✅ **Automatic weekly updates** - Ensures data stays current without manual intervention
- ✅ **Change detection** - Only commits if actual changes detected (saves storage)
- ✅ **Manual trigger** - Can run on-demand via GitHub UI
- ✅ **Pull Request workflow** - Allows review before merging major changes
- ✅ **Transparent history** - All updates tracked in git history
- ✅ **No server costs** - Uses free GitHub Actions minutes (2000 min/month)

**Schedule Options:**

| Frequency | Cron | Use Case |
|-----------|------|----------|
| Weekly (Recommended) | `0 6 * * 1` | Monday 6 AM UTC |
| Bi-weekly | `0 6 1,15 * *` | 1st & 15th of month |
| Monthly | `0 6 1 * *` | 1st of month at 6 AM UTC |
| Daily | `0 6 * * *` | Every day (overkill for MF data) |

**Fallback Strategy:**
- If scraping fails (rate limit, site down), GitHub Actions will notify via email
- Previous successful run data remains intact (no rollback needed)
- Manual trigger available for emergency updates

#### 1.6 Deliverables

- Corpus of exactly 5 Groww scheme pages with metadata (no additional sources)
- Source validation report (all URLs from groww.in only)
- Data storage in structured JSON/Parquet format
- GitHub Actions workflow for automated data refresh
- Data freshness monitoring and alerting

---

### PHASE 2 — Chunking, Embedding & Vector Store Setup

**Duration Estimate:** 1 week  
**Objective:** Transform raw documents into searchable vector embeddings

#### 2.1 Chunking Strategy

```
Clean Document Text
        │
        ▼
┌───────────────────────────────────┐
│         CHUNKING ENGINE            │
│                                    │
│  Strategy: Semantic Chunking       │
│  ┌──────────────────────────────┐  │
│  │ Primary: Heading-based split │  │
│  │ (Split on H1/H2/H3 headers) │  │
│  └──────────────────────────────┘  │
│  ┌──────────────────────────────┐  │
│  │ Fallback: Fixed-size chunks  │  │
│  │ Chunk size: 512 tokens       │  │
│  │ Overlap: 64 tokens           │  │
│  └──────────────────────────────┘  │
│  ┌──────────────────────────────┐  │
│  │ Table-aware chunking         │  │
│  │ (Preserve table rows intact) │  │
│  └──────────────────────────────┘  │
└───────────────┬───────────────────┘
                │
                ▼
         Chunk Objects
```

#### 2.2 Chunk Data Schema

```json
{
  "chunk_id": "uuid",
  "doc_id": "parent_doc_uuid",
  "chunk_text": "The expense ratio of HDFC Mid-Cap Fund is 1.03%...",
  "chunk_index": 3,
  "token_count": 87,
  "metadata": {
    "scheme_name": "HDFC Mid-Cap Fund",
    "amc_name": "HDFC Mutual Fund",
    "doc_type": "GROWW_SCHEME_PAGE",
    "category": "mid_cap",
    "source_url": "https://groww.in/mutual-funds/hdfc-mid-cap-fund-direct-growth",
    "section_heading": "Fees and Expenses",
    "scraped_date": "2026-05-26"
  }
}
```

#### 2.3 Embedding Pipeline

```
Chunk Text
     │
     ▼
┌───────────────────────────────────────────┐
│          EMBEDDING ENGINE                  │
│                                            │
│  Option A (Cloud):                         │
│    Model: text-embedding-3-small (OpenAI)  │
│    Dimensions: 1536                        │
│    Cost: ~$0.02 / 1M tokens               │
│                                            │
│  Option B (Local):                         │
│    Model: BAAI/bge-small-en-v1.5           │
│    Dimensions: 384                         │
│    Cost: Free (self-hosted)                │
│                                            │
│  Batch size: 100 chunks / request          │
└───────────────┬───────────────────────────┘
                │
                ▼
        Embedding Vectors []
```

#### 2.4 Vector Store Configuration

```
┌────────────────────────────────────────────┐
│           VECTOR STORE (ChromaDB)           │
│                                            │
│  Collection: mf_faq_corpus                 │
│  Distance: cosine                          │
│  Persist: ./data/chroma_db                 │
│                                            │
│  ┌──────────────────────────────────────┐  │
│  │ Index Configuration                  │  │
│  │ - HNSW index                         │  │
│  │ - M: 16 (connections per node)       │  │
│  │ - ef_construction: 200               │  │
│  │ - ef_search: 50                      │  │
│  └──────────────────────────────────────┘  │
│                                            │
│  Total expected vectors: ~100–300          │
│  (5 pages × ~20–60 chunks each)           │
└────────────────────────────────────────────┘
```

#### 2.5 Deliverables

- Chunked corpus with metadata
- Embedded vectors stored in ChromaDB
- Retrieval quality baseline report (sample queries)

---

### PHASE 3 — Retrieval & RAG Pipeline

**Duration Estimate:** 1–2 weeks  
**Objective:** Build the core retrieval-augmented generation pipeline

#### 3.1 Query Processing Flow

```
User Query
     │
     ▼
┌──────────────────┐
│ Query Pre-       │
│ Processor        │
│ - Normalize      │
│ - Spell correct  │
│ - Entity extract │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐     ┌──────────────────┐
│ Intent           │────▶│ ADVISORY intent?  │
│ Classifier       │     │ → Route to       │
│                  │     │   Refusal Handler │
│ Classes:         │     └──────────────────┘
│ - FACTUAL       │
│ - ADVISORY      │
│ - AMBIGUOUS     │
└────────┬─────────┘
         │ FACTUAL
         ▼
┌──────────────────┐
│ Query Embedding  │
│ (Same model as   │
│  corpus)         │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ Vector Search    │
│ - Top-K: 5       │
│ - Min score: 0.6 │
│ - MMR diversity   │
│   (lambda: 0.7)  │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ Context          │
│ Assembler        │
│ - Deduplicate    │
│ - Re-rank by     │
│   relevance      │
│ - Token budget:  │
│   2048 tokens    │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ Prompt Builder   │
│ (See 3.2)        │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ LLM Generator    │
└──────────────────┘
```

#### 3.2 Prompt Template Design

```
┌─────────────────────────────────────────────────────────────┐
│                    SYSTEM PROMPT                             │
│                                                             │
│  You are a facts-only mutual fund FAQ assistant.            │
│                                                             │
│  RULES:                                                     │
│  1. Answer ONLY with factual information from the context   │
│  2. Maximum 3 sentences per response                        │
│  3. Include exactly ONE source citation link                │
│  4. If the context does not contain the answer, say:        │
│     "I could not find this information in the available   │
│      scheme pages. Please check Groww directly."          │
│  5. NEVER provide investment advice or recommendations      │
│  6. NEVER compare fund performance or calculate returns     │
│  7. For performance queries, provide the factsheet link     │
│  8. Always append: "Last updated from sources: <date>"      │
│                                                             │
│  RESPONSE FORMAT:                                           │
│  <factual_answer>                                           │
│  Source: <url>                                              │
│  Last updated from sources: <date>                          │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                    USER PROMPT TEMPLATE                      │
│                                                             │
│  Context:                                                   │
│  {retrieved_chunks_with_metadata}                           │
│                                                             │
│  Question: {user_query}                                     │
└─────────────────────────────────────────────────────────────┘
```

#### 3.3 Advisory Refusal Prompt

```
┌─────────────────────────────────────────────────────────────┐
│                REFUSAL PROMPT TEMPLATE                       │
│                                                             │
│  The user has asked an advisory question: "{query}"         │
│                                                             │
│  Respond politely with:                                     │
│  1. A clear statement that you cannot provide investment    │
│     advice or recommendations                               │
│  2. A reminder that you only provide factual information    │
│  3. A suggestion to visit Groww for more details          │
│                                                             │
│  Example:                                                   │
│  "I'm unable to provide investment advice or recommend      │
│   specific funds. I can only share factual details about    │
│   mutual fund schemes. For more information, please visit  │
│   the scheme page on Groww."                               │
│  Last updated from sources: {date}                          │
└─────────────────────────────────────────────────────────────┘
```

#### 3.4 Intent Classifier Design

```
┌──────────────────────────────────────────────────────────┐
│               INTENT CLASSIFIER                           │
│                                                           │
│  Approach: LLM-based few-shot classifier                  │
│                                                           │
│  FACTUAL queries (route to RAG):                          │
│  - "What is the expense ratio of HDFC Mid-Cap Fund?"      │
│  - "What is the exit load for HDFC ELSS Tax Saver?"       │
│  - "Minimum SIP amount for HDFC Large Cap Fund?"        │
│  - "How to download my capital gains statement?"          │
│                                                           │
│  ADVISORY queries (route to Refusal):                     │
│  - "Should I invest in this fund?"                        │
│  - "Which fund is better?"                                │
│  - "Is this a good time to invest?"                       │
│  - "What should I invest in for tax saving?"              │
│                                                           │
│  AMBIGUOUS queries (default to Refusal with clarification)│
│  - "Tell me about this fund" → Ask for specific question  │
│  - "How is this fund?" → Clarify factual vs advisory      │
└──────────────────────────────────────────────────────────┘
```

#### 3.5 Response Validation & Post-Processing

```
LLM Raw Response
       │
       ▼
┌──────────────────────────────────────┐
│        RESPONSE VALIDATOR             │
│                                       │
│  Check 1: Sentence count ≤ 3          │
│  Check 2: Contains source URL         │
│  Check 3: Contains "Last updated"     │
│  Check 4: No advisory language        │
│           (flagged keywords:           │
│            "should", "recommend",      │
│            "better", "best",           │
│            "suggest", "advice")        │
│  Check 5: Source URL is from          │
│           allow-listed domains         │
└──────────────┬───────────────────────┘
               │
        ┌──────┴──────┐
        │  Valid?     │
        ├───YES───────┤──▶ Return to user
        └───NO────────┤──▶ Regenerate with stricter prompt
                       │    (max 2 retries, then fallback)
                       │
                       ▼
              ┌─────────────────┐
              │ Fallback:       │
              │ "I couldn't     │
              │ verify this     │
              │ information.    │
              │ Please check    │
              │ Groww directly. │
              └─────────────────┘
```

#### 3.6 Deliverables

- End-to-end RAG pipeline (query → response)
- Prompt templates with versioning
- Intent classifier with test cases
- Response validator module

---

### PHASE 4 — Compliance, Safety & Guardrails

**Duration Estimate:** 1 week  
**Objective:** Ensure every response is compliant, safe, and within scope

#### 4.1 Guardrail Architecture

```
User Query
     │
     ▼
┌───────────────────┐
│ INPUT GUARDRAILS  │
│                    │
│ ┌───────────────┐  │
│ │ PII Detector  │  │
│ │ (Scan for     │  │
│ │  PAN, Aadhaar,│  │
│ │  phone, email)│  │
│ └───────────────┘  │
│ ┌───────────────┐  │
│ │ Topic Filter  │  │
│ │ (Block non-MF │  │
│ │  queries)     │  │
│ └───────────────┘  │
│ ┌───────────────┐  │
│ │ Advisory      │  │
│ │ Detector      │  │
│ └───────────────┘  │
└────────┬──────────┘
         │
         ▼
    [RAG Pipeline]
         │
         ▼
┌───────────────────┐
│ OUTPUT GUARDRAILS │
│                    │
│ ┌───────────────┐  │
│ │ Advisory      │  │
│ │ Language      │  │
│ │ Filter        │  │
│ └───────────────┘  │
│ ┌───────────────┐  │
│ │ Source URL    │  │
│ │ Validator     │  │
│ │ (Allow-list)  │  │
│ └───────────────┘  │
│ ┌───────────────┐  │
│ │ Length        │  │
│ │ Enforcer      │  │
│ │ (≤3 sentences)│  │
│ └───────────────┘  │
│ ┌───────────────┐  │
│ │ Disclaimer    │  │
│ │ Appender      │  │
│ └───────────────┘  │
└───────────────────┘
```

#### 4.2 Domain Allow-List

```python
ALLOWED_DOMAINS = [
    # Sole data source for this project
    "groww.in",
]
```

#### 4.3 PII Detection Rules

| Pattern | Action |
|---|---|
| PAN Number (e.g., ABCDE1234F) | Reject query, warn user |
| Aadhaar (12 digits) | Reject query, warn user |
| Email address | Strip from query, proceed |
| Phone number (10 digits) | Strip from query, proceed |
| Account number | Reject query, warn user |
| OTP | Reject query, warn user |

#### 4.4 Deliverables

- Input/output guardrail modules
- PII detection service
- Domain allow-list configuration
- Advisory language filter

---

### PHASE 5 — API & Backend Development

**Duration Estimate:** 1–2 weeks  
**Objective:** Build the backend API server and integrate all pipeline components

#### 5.1 Technology Stack

| Layer | Technology | Rationale |
|---|---|---|
| API Framework | FastAPI | Async, auto-docs, Python-native |
| LLM | GPT-4o-mini (primary) / Llama 3 (fallback) | Cost-effective, high quality |
| Embeddings | text-embedding-3-small | OpenAI ecosystem consistency |
| Vector Store | ChromaDB | Lightweight, local, no infra needed |
| Caching | Redis (optional) | Cache frequent queries |
| Task Queue | Celery (optional) | For async ingestion jobs |
| Containerization | Docker | Reproducible deployment |

#### 5.2 API Design

```
┌─────────────────────────────────────────────────────────────┐
│                     API ENDPOINTS                            │
│                                                             │
│  POST /api/v1/chat                                          │
│  ├── Request: { "query": string, "session_id": string }     │
│  └── Response: {                                            │
│        "answer": string,                                    │
│        "source_url": string,                                │
│        "last_updated": string,                              │
│        "is_refusal": boolean,                               │
│        "query_type": "factual" | "advisory" | "ambiguous"  │
│      }                                                      │
│                                                             │
│  GET  /api/v1/schemes                                       │
│  └── Response: { "schemes": [{ "name": string,              │
│                               "category": string,           │
│                               "amc": string }] }            │
│                                                             │
│  GET  /api/v1/health                                        │
│  └── Response: { "status": "healthy",                       │
│                   "vector_store_docs": number,               │
│                   "last_ingestion": string }                 │
└─────────────────────────────────────────────────────────────┘
```

#### 5.3 Application Structure

```
mf-faq-assistant/
├── app/
│   ├── __init__.py
│   ├── main.py                  # FastAPI app entry
│   ├── config.py                # Settings & env vars
│   ├── api/
│   │   ├── __init__.py
│   │   ├── routes/
│   │   │   ├── chat.py          # /chat endpoint
│   │   │   ├── schemes.py       # /schemes endpoint
│   │   │   └── health.py        # /health endpoint
│   │   └── middleware/
│   │       ├── rate_limiter.py
│   │       └── cors.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── intent_classifier.py # Classify factual vs advisory
│   │   ├── rag_pipeline.py      # RAG orchestration
│   │   ├── prompt_builder.py    # Template management
│   │   ├── response_validator.py # Post-processing
│   │   └── refusal_handler.py   # Advisory query handler
│   ├── guardrails/
│   │   ├── __init__.py
│   │   ├── input_guard.py       # PII detection, topic filter
│   │   ├── output_guard.py      # Source validation, length
│   │   └── domain_allowlist.py  # URL verification
│   ├── ingestion/
│   │   ├── __init__.py
│   │   ├── scraper.py           # Web scraping engine
│   │   ├── parser.py            # HTML parsing
│   │   ├── chunker.py           # Text chunking logic
│   │   ├── embedder.py          # Embedding generation
│   │   └── vector_store.py      # ChromaDB interface
│   └── models/
│       ├── __init__.py
│       ├── schemas.py           # Pydantic models
│       └── document.py          # Document data model
├── data/
│   ├── raw/                     # Scraped raw content
│   ├── processed/               # Cleaned & chunked data
│   └── chroma_db/               # Vector store persistence
├── tests/
│   ├── test_rag_pipeline.py
│   ├── test_intent_classifier.py
│   ├── test_guardrails.py
│   └── test_api.py
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── .env.example
└── README.md
```

#### 5.4 Configuration Management

```
┌─────────────────────────────────────────────────────────────┐
│                  CONFIGURATION (.env)                        │
│                                                             │
│  # LLM Settings                                             │
│  LLM_PROVIDER=openai                                        │
│  LLM_MODEL=gpt-4o-mini                                     │
│  LLM_TEMPERATURE=0.0                                        │
│  LLM_MAX_TOKENS=256                                         │
│                                                             │
│  # Embedding Settings                                       │
│  EMBEDDING_MODEL=text-embedding-3-small                     │
│  EMBEDDING_DIMENSIONS=1536                                  │
│                                                             │
│  # Vector Store                                             │
│  VECTOR_STORE_PATH=./data/chroma_db                         │
│  VECTOR_STORE_COLLECTION=mf_faq_corpus                      │
│                                                             │
│  # Retrieval                                                │
│  RETRIEVAL_TOP_K=5                                          │
│  RETRIEVAL_MIN_SCORE=0.6                                    │
│  RETRIEVAL_MMR_LAMBDA=0.7                                   │
│                                                             │
│  # Chunking                                                 │
│  CHUNK_SIZE=512                                              │
│  CHUNK_OVERLAP=64                                            │
│                                                             │
│  # API                                                      │
│  API_RATE_LIMIT=30/minute                                   │
│  API_CORS_ORIGINS=["http://localhost:3000"]                 │
└─────────────────────────────────────────────────────────────┘
```

#### 5.5 Deliverables

- FastAPI application with all endpoints
- Configuration management system
- Docker containerization
- API documentation (auto-generated via FastAPI)

---

### PHASE 6 — Frontend & User Interface

**Duration Estimate:** 1 week  
**Objective:** Build a minimal, clean chat interface

#### 6.1 UI Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    FRONTEND (React + Vite)                    │
│                                                             │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  Disclaimer Banner (sticky top)                        │  │
│  │  ⚠ "Facts-only. No investment advice."                │  │
│  └───────────────────────────────────────────────────────┘  │
│                                                             │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  Welcome Section                                       │  │
│  │  "Hi! I'm your Mutual Fund FAQ Assistant.             │  │
│  │   Ask me factual questions about mutual fund schemes." │  │
│  └───────────────────────────────────────────────────────┘  │
│                                                             │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  Example Questions (clickable chips)                   │  │
│  │  ┌──────────────────┐ ┌────────────────────┐          │  │
│  │  │ "What is the     │ │ "What is the exit  │          │  │
│  │  │  expense ratio   │ │  load for HDFC      │          │  │
│  │  │  of HDFC          │ │  ELSS Tax Saver    │          │  │
│  │  │  Mid-Cap Fund?"   │ │  Fund?"            │          │  │
│  │  └──────────────────┘ └────────────────────┘          │  │
│  │  ┌──────────────────────────────────────┐              │  │
│  │  │ "What is the lock-in period for      │              │  │
│  │  │  HDFC ELSS Tax Saver   │              │  │
│  │  │  Fund?"                │              │  │
│  │  └──────────────────────────────────────┘              │  │
│  └───────────────────────────────────────────────────────┘  │
│                                                             │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  Chat Area                                             │  │
│  │  ┌─────────────────────────────────────────────────┐  │  │
│  │  │ User: What is the expense ratio?                │  │  │
│  │  │                                                  │  │  │
│  │  │ Bot: The expense ratio of HDFC Mid-Cap Fund     │  │  │
│  │  │ is 1.03% (direct plan) and 1.55% (regular plan).│  │  │
│  │  │ Source: https://groww.in/mutual-funds/hdfc-      │  │  │
│  │  │ mid-cap-fund-direct-growth                       │  │  │
│  │  │ Last updated from sources: 2026-05-26           │  │  │
│  │  └─────────────────────────────────────────────────┘  │  │
│  └───────────────────────────────────────────────────────┘  │
│                                                             │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  Input Bar                                             │  │
│  │  [Type your question...                    ] [Send ▶]  │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

#### 6.2 Component Architecture

```
src/
├── App.tsx
├── components/
│   ├── ChatWindow.tsx         # Main chat container
│   ├── MessageBubble.tsx      # Individual message display
│   ├── SourceLink.tsx         # Clickable source citation
│   ├── DisclaimerBanner.tsx   # Sticky disclaimer
│   ├── ExampleQuestions.tsx   # Clickable question chips
│   ├── InputBar.tsx           # Text input + send button
│   └── WelcomeSection.tsx     # Welcome message
├── hooks/
│   ├── useChat.ts             # Chat state management
│   └── useApi.ts              # API client hook
├── services/
│   └── api.ts                 # Backend API client
├── types/
│   └── index.ts               # TypeScript interfaces
└── styles/
    └── globals.css            # Tailwind CSS
```

#### 6.3 UI Requirements Checklist

| Requirement | Implementation |
|---|---|
| Welcome message | Static hero section on initial load |
| 3 example questions | Clickable chips that auto-submit |
| Disclaimer banner | Sticky top banner, always visible |
| Source links | Clickable URLs in each response |
| Last updated date | Appended to every response |
| Refusal responses | Styled differently (info/warning) |
| Loading state | Typing indicator during generation |
| Error handling | Graceful error messages |
| Mobile responsive | Responsive layout via Tailwind |

#### 6.4 Deliverables

- React + Vite frontend application
- Responsive chat interface
- API integration layer
- Build & deployment configuration

---

### PHASE 7 — Testing, Evaluation & Deployment

**Duration Estimate:** 1–2 weeks  
**Objective:** Validate quality, accuracy, and compliance; deploy to production

#### 7.1 Testing Strategy

```
┌─────────────────────────────────────────────────────────────┐
│                   TESTING PYRAMID                             │
│                                                             │
│                    ╱ ╲                                      │
│                   ╱   ╲        E2E Tests                    │
│                  ╱ E2E ╲       - Full user journeys         │
│                 ╱───────╲      - Advisory query rejection   │
│                ╱         ╲                                   │
│               ╱ Integration ╲  - RAG pipeline end-to-end    │
│              ╱               ╲ - API endpoint tests         │
│             ╱─────────────────╲                              │
│            ╱                   ╲                             │
│           ╱    Unit Tests       ╲ - Intent classifier       │
│          ╱                       ╲- Response validator      │
│         ╱─────────────────────────╲- Guardrail checks      │
│        ╱                           ╲- Chunking logic       │
│       ╱   Static / Lint / Type      ╲                      │
│      ╱───────────────────────────────╲                     │
└─────────────────────────────────────────────────────────────┘
```

#### 7.2 Evaluation Dataset

```
┌──────────────────────────────────────────────────────────────┐
│                 GOLDEN TEST SET                               │
│                                                              │
│  FACTUAL QUERIES (30+ questions)                             │
│  ┌────────────────────────────────────────────────────────┐  │
│  │ Q: "What is the expense ratio of [Scheme]?"            │  │
│  │ Expected: Exact value + source URL                     │  │
│  │                                                        │  │
│  │ Q: "What is the minimum SIP amount for [Scheme]?"      │  │
│  │ Expected: Amount + source URL                          │  │
│  │                                                        │  │
│  │ Q: "What is the lock-in period for [ELSS Scheme]?"     │  │
│  │ Expected: "3 years" + source URL                       │  │
│  │                                                        │  │
│  │ Q: "How to download my capital gains statement?"       │  │
│  │ Expected: Step reference + source URL                  │  │
│  └────────────────────────────────────────────────────────┘  │
│                                                              │
│  ADVISORY QUERIES (15+ questions)                            │
│  ┌────────────────────────────────────────────────────────┐  │
│  │ Q: "Should I invest in HDFC Mid-Cap Fund?"             │  │
│  │ Expected: Polite refusal + suggestion to visit Groww    │  │
│  │                                                        │  │
│  │ Q: "Which is better: Fund A or Fund B?"                │  │
│  │ Expected: Polite refusal + suggestion to visit Groww    │  │
│  └────────────────────────────────────────────────────────┘  │
│                                                              │
│  EDGE CASES (10+ questions)                                  │
│  ┌────────────────────────────────────────────────────────┐  │
│  │ Q: Query with PAN number embedded                      │  │
│  │ Expected: Rejection + PII warning                      │  │
│  │                                                        │  │
│  │ Q: "Tell me about Bitcoin"                             │  │
│  │ Expected: Out-of-scope refusal                         │  │
│  │                                                        │  │
│  │ Q: "Return of HDFC Mid-Cap vs HDFC Large Cap"         │  │
│  │ Expected: No comparison, link to Groww scheme pages    │  │
│  └────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────┘
```

#### 7.3 Quality Metrics

| Metric | Target | Measurement Method |
|---|---|---|
| Factual Accuracy | ≥ 95% | Compare answers against gold-standard |
| Source Citation Rate | 100% | Every factual response has a valid URL |
| Advisory Refusal Rate | 100% | All advisory queries properly refused |
| Response Length Compliance | ≥ 98% | ≤ 3 sentences per response |
| PII Rejection Rate | 100% | All PII-containing queries rejected |
| Source URL Validity | 100% | All cited URLs from allow-listed domains |
| Latency (p95) | < 3 seconds | End-to-end query to response |
| "Last updated" inclusion | 100% | Every response includes date footer |

#### 7.4 Deployment Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                  DEPLOYMENT (Docker Compose)                  │
│                                                             │
│  ┌──────────────────┐  ┌──────────────────┐                 │
│  │ Frontend         │  │ Backend (FastAPI) │                 │
│  │ Nginx Container  │  │ uvicorn + app     │                 │
│  │ Port: 80         │  │ Port: 8000        │                 │
│  │                  │  │                   │                 │
│  │ - Static React   │  │ - RAG pipeline    │                 │
│  │   build files    │  │ - Guardrails      │                 │
│  │ - Proxy /api/*   │  │ - ChromaDB        │                 │
│  │   to backend     │  │ - LLM client      │                 │
│  └──────────────────┘  └──────────────────┘                 │
│                                                             │
│  Optional:                                                  │
│  ┌──────────────────┐                                       │
│  │ Redis Container  │  Cache frequent queries               │
│  │ Port: 6379       │                                       │
│  └──────────────────┘                                       │
└─────────────────────────────────────────────────────────────┘
```

#### 7.5 CI/CD Pipeline

```
┌────────────┐    ┌────────────┐    ┌────────────┐    ┌────────────┐
│ Git Push   │───▶│ Lint &     │───▶│ Unit &     │───▶│ Build      │
│            │    │ Type Check │    │ Integration│    │ Docker     │
│            │    │ (ruff,     │    │ Tests      │    │ Images     │
│            │    │  mypy)     │    │            │    │            │
└────────────┘    └────────────┘    └────────────┘    └────────────┘
                                                             │
                                                             ▼
                                                      ┌────────────┐
                                                      │ Deploy     │
                                                      │ (local /   │
                                                      │  cloud)    │
                                                      └────────────┘
```

#### 7.5.1 GitHub Actions Workflows

The project uses multiple GitHub Actions workflows for different purposes:

**1. Data Refresh Workflow** (`.github/workflows/data-refresh.yml`)

- **Trigger:** Every Monday 6:00 AM UTC (11:30 AM IST)
- **Purpose:** Automatically scrape latest data from 5 Groww URLs
- **Actions:**
  - Compare scraped data with existing corpus
  - If changes detected: Commit, push, and create Pull Request
  - If no changes: Skip commit (saves storage)
- **Monitoring:** Email notifications on failure, manual trigger available

**2. CI Pipeline** (`.github/workflows/ci.yml`)

- **Trigger:** On push to main or PR to main
- **Purpose:** Ensure code quality and test coverage
- **Jobs:**
  - Lint & Type Check (ruff, mypy)
  - Unit Tests (intent classifier, RAG, guardrails, compliance)
  - Integration Tests (end-to-end pipeline, API endpoints)
  - Docker Build (backend + frontend images)
- **Requirement:** ≥80% code coverage

**3. Deployment Workflow** (`.github/workflows/deploy.yml`)

- **Trigger:** On version tag push (v1.0.0, v1.1.0, etc.)
- **Purpose:** Release to production with approval gate
- **Steps:**
  - Run full test suite
  - Build and push Docker images
  - Deploy to staging (automatic)
  - Deploy to production (manual approval required)
  - Post-deployment health checks

**Workflow Summary:**

| Workflow | File | Trigger | Purpose |
|----------|------|---------|---------|
| Data Refresh | `data-refresh.yml` | Weekly schedule | Keep corpus data fresh |
| CI Pipeline | `ci.yml` | Push/PR to main | Code quality & testing |
| Deployment | `deploy.yml` | Version tag | Release to production |

#### 7.6 Deliverables

- Test suite with ≥ 80% code coverage
- Golden evaluation dataset with expected outputs
- Quality metrics report
- Docker-based deployment setup
- CI/CD pipeline configuration

---

## 3. Technology Stack Summary

| Component | Technology | Version |
|---|---|---|
| Language | Python | 3.11+ |
| API Framework | FastAPI | 0.110+ |
| LLM (Primary) | Groq (Llama 3.1-8b-instant) | Latest |
| LLM (Fallback) | OpenAI GPT-4o-mini | Latest |
| Embeddings | text-embedding-3-small | Latest |
| Vector Store | ChromaDB | 0.4+ |
| Frontend | React + Vite + TypeScript | 18+ / 5+ |
| Styling | Tailwind CSS | 3+ |
| Web Scraping | Playwright + BeautifulSoup4 | Latest |
| Containerization | Docker + Docker Compose | Latest |
| Caching | Redis (optional) | 7+ |
| CI/CD | GitHub Actions (Scheduled Workflows) | Latest |

---

## 4. Data Flow Summary

```
User Query
    │
    ▼
[Input Guardrails: PII Detection + Topic Filter]
    │
    ▼
[Intent Classifier: Factual / Advisory / Ambiguous]
    │
    ├── Advisory ──────▶ [Refusal Handler] ──▶ Response
    │
    └── Factual ──▶ [Query Embedding]
                        │
                        ▼
                   [Vector Search: Top-K Chunks]
                        │
                        ▼
                   [Context Assembly + Prompt Build]
                        │
                        ▼
                   [LLM Generation]
                        │
                        ▼
                   [Output Guardrails: Source + Length + Language Check]
                        │
                        ▼
                   [Append Source + Last Updated]
                        │
                        ▼
                   Response to User
```

---

## 5. Risk & Mitigation

| Risk | Impact | Mitigation |
|---|---|---|
| LLM hallucination | Incorrect financial facts | Strict context-only prompting + response validator |
| Advisory query leakage | Compliance violation | Dual-layer intent classification + output guardrails |
| Source URL decay | Broken citations | Periodic URL health checks + re-scraping |
| PII in user queries | Privacy violation | Input PII detection + query rejection |
| Vector store drift | Stale information | **GitHub Actions automated weekly refresh** (Section 1.5) |
| Rate limiting by Groww | Incomplete corpus | Respectful scraping with delays + caching + retry logic |

---

## 6. Phase Timeline

| Phase | Name | Duration | Dependencies |
|---|---|---|---|
| 1 | Corpus Collection & Ingestion | 1–2 weeks | None |
| 2 | Chunking, Embedding & Vector Store | 1 week | Phase 1 |
| 3 | Retrieval & RAG Pipeline | 1–2 weeks | Phase 2 |
| 4 | Compliance, Safety & Guardrails | 1 week | Phase 3 |
| 5 | API & Backend Development | 1–2 weeks | Phase 4 |
| 6 | Frontend & User Interface | 1 week | Phase 5 |
| 7 | Testing, Evaluation & Deployment | 1–2 weeks | Phase 6 |
| **Total** | | **7–12 weeks** | |

---

## 7. Known Limitations

- Corpus limited to exactly 5 Groww scheme pages for HDFC Mutual Fund only
- **Data freshness:** Automated weekly refresh via GitHub Actions (every Monday 11:30 AM IST)
- No real-time NAV or market data (depends on Groww page update frequency)
- No multi-turn conversational memory (stateless per query)
- English language only
- No user authentication or session persistence
- Performance queries receive factsheet links only (no calculations)
- Chunking quality depends on document structure consistency
- LLM temperature set to 0.0 for determinism, but minor variation possible
