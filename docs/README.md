# MF FAQ Assistant — Phase 1 Implementation

## 📁 Project Structure

```
.
├── app/
│   └── phase1/
│       ├── subphase_1_1_corpus_collection/    # Phase 1.1: Web Scraping & Ingestion
│       │   ├── scraper.py                     # Playwright-based Groww scraper
│       │   ├── parser.py                      # HTML-to-Text converter
│       │   ├── metadata_tagger.py             # Scheme metadata tagging
│       │   ├── domain_allowlist.py            # Groww URL validation
│       │   └── pipeline.py                    # Phase 1.1 orchestration
│       │
│       ├── subphase_1_2_chunking_embedding/   # Phase 1.2: Chunking & Vector Store
│       │   ├── chunker.py                     # Semantic chunking engine
│       │   ├── embedder.py                    # OpenAI embedding pipeline
│       │   ├── vector_store.py                # ChromaDB integration
│       │   └── pipeline.py                    # Phase 1.2 orchestration
│       │
│       ├── subphase_1_3_rag_setup/            # Phase 1.3: RAG Pipeline
│       │   └── rag_pipeline.py                # RAG retrieval & response generation
│       │
│       ├── subphase_1_4_compliance/           # Phase 1.4: (Future)
│       └── subphase_1_5_testing/              # Phase 1.5: (Future)
│
├── scripts/
│   ├── run_phase_1_1.py                       # Run Phase 1.1
│   ├── run_phase_1_2.py                       # Run Phase 1.2
│   └── run_phase_1_3.py                       # Run Phase 1.3
│
├── data/
│   ├── raw/                                   # Ingested documents (JSON)
│   ├── processed/                             # Chunked data (JSON)
│   └── chroma_db/                             # Vector store (ChromaDB)
│
├── config.py                                  # Configuration settings
├── requirements.txt                           # Python dependencies
├── .env.example                               # Environment variables template
└── .gitignore                                 # Git ignore rules
```

---

## 🚀 Quick Start

### Step 1: Setup Environment

1. **Copy the environment template:**
   ```bash
   cp .env.example .env
   ```

2. **Edit `.env` and add your OpenAI API key:**
   ```env
   OPENAI_API_KEY=your_openai_api_key_here
   ```
   
   > Get your API key from: https://platform.openai.com/api-keys

3. **Install dependencies:**
   ```bash
   pip3 install -r requirements.txt
   playwright install
   ```

---

### Step 2: Run Phase 1.1 — Corpus Collection & Data Ingestion

This phase scrapes 5 HDFC Mutual Fund scheme pages from Groww:

- HDFC Mid-Cap Fund
- HDFC Equity Fund
- HDFC Focused Fund
- HDFC ELSS Tax Saver Fund
- HDFC Large Cap Fund

**Run:**
```bash
python3 scripts/run_phase_1_1.py
```

**Output:**
- `data/raw/ingested_documents.json` — 5 documents with metadata

**Expected duration:** 2–5 minutes (depends on network speed)

---

### Step 3: Run Phase 1.2 — Chunking, Embedding & Vector Store

This phase:
1. Chunks documents using semantic chunking (512 tokens, 64 overlap)
2. Generates embeddings using OpenAI (text-embedding-3-small)
3. Stores in ChromaDB vector database

**Run:**
```bash
python3 scripts/run_phase_1_2.py
```

**Output:**
- `data/processed/chunks.json` — All chunks with metadata
- `data/chroma_db/` — ChromaDB persistent storage

**Expected duration:** 1–3 minutes (depends on number of chunks & API rate limits)

---

### Step 4: Run Phase 1.3 — RAG Pipeline Testing

This phase tests the RAG (Retrieval-Augmented Generation) pipeline with sample queries:

- "What is the expense ratio of HDFC Mid-Cap Fund?"
- "What is the minimum SIP amount for HDFC ELSS Tax Saver Fund?"
- "What is the exit load for HDFC Equity Fund?"

**Run:**
```bash
python3 scripts/run_phase_1_3.py
```

**Output:**
- Console display of queries, responses, and validation results

**Expected duration:** 30–60 seconds

---

## 📊 Phase Dependencies

```
Phase 1.1 (Scraping)
       ↓
Phase 1.2 (Chunking + Embedding + Vector Store)
       ↓
Phase 1.3 (RAG Pipeline Testing)
```

**Important:** You must run phases in order. Each phase depends on the output of the previous phase.

---

## 🔧 Configuration

All settings are in [config.py](file:///Users/vishalkataria/Documents/Docs/config.py) and can be overridden via `.env`:

| Setting | Default | Description |
|---|---|---|
| `OPENAI_API_KEY` | (required) | OpenAI API key |
| `LLM_MODEL` | gpt-4o-mini | LLM model for response generation |
| `EMBEDDING_MODEL` | text-embedding-3-small | Embedding model |
| `CHUNK_SIZE` | 512 | Tokens per chunk |
| `CHUNK_OVERLAP` | 64 | Overlap between chunks |
| `RAG_TOP_K` | 5 | Number of chunks to retrieve |
| `SCRAPE_DELAY` | 5.0 | Seconds between Groww requests |

---

## 🐛 Troubleshooting

### Issue: "OPENAI_API_KEY is required"
**Solution:** Create `.env` file with your OpenAI API key (see Step 1)

### Issue: "Documents file not found: ingested_documents.json"
**Solution:** Run Phase 1.1 first before running Phase 1.2

### Issue: "Playwright browser not found"
**Solution:** Run `playwright install` to download browsers

### Issue: "Rate limit error from OpenAI API"
**Solution:** The embedder has automatic retry with exponential backoff. Wait and retry.

---

## 📝 Data Flow

### Phase 1.1 Output
```json
[
  {
    "doc_id": "uuid-1",
    "scheme_name": "HDFC Mid-Cap Fund",
    "amc_name": "HDFC Mutual Fund",
    "source_url": "https://groww.in/mutual-funds/hdfc-mid-cap-fund-direct-growth",
    "category": "mid_cap",
    "content_clean": "...",
    "scraped_date": "2026-05-26"
  }
]
```

### Phase 1.2 Output
- **chunks.json**: Array of chunk dictionaries with metadata
- **ChromaDB**: Vector embeddings with metadata filtering

### Phase 1.3 Output
```json
{
  "response": "The expense ratio of HDFC Mid-Cap Fund is 1.03%.",
  "retrieved_chunks": [...],
  "validation": {
    "passed": true,
    "warnings": []
  }
}
```

---

## 🎯 Next Steps

After completing Phase 1:

- **Phase 2–6**: Implement remaining phases as per [ARCHITECTURE.md](/Users/vishalkataria/Documents/Docs/ARCHITECTURE.md)
- **Edge Cases**: Review edge case documents in `/Users/vishalkataria/Documents/Docs/EDGE_CASES_PHASE*.md`
- **Testing**: Add unit tests in `tests/` directory

---

## 📚 Documentation

- [ARCHITECTURE.md](/Users/vishalkataria/Documents/Docs/ARCHITECTURE.md) — Complete phase-wise architecture
- [EDGE_CASES_PHASE1.md](/Users/vishalkataria/Documents/Docs/EDGE_CASES_PHASE1.md) — Phase 1 edge cases
- [EDGE_CASES_PHASE2.md](/Users/vishalkataria/Documents/Docs/EDGE_CASES_PHASE2.md) — Phase 2 edge cases
- [EDGE_CASES_PHASE3.md](/Users/vishalkataria/Documents/Docs/EDGE_CASES_PHASE3.md) — Phase 3 edge cases

---

## ⚠️ Important Notes

1. **Groww URLs only**: This project uses exactly 5 Groww URLs — no additional sources
2. **Factual responses only**: The RAG pipeline is designed to provide factual information, not investment advice
3. **Rate limits**: OpenAI API has rate limits. The pipeline includes retry logic but may take longer for large batches
4. **ChromaDB persistence**: Vector store data is persisted to disk in `data/chroma_db/`

---

**Created:** 2026-05-26  
**Last Updated:** 2026-05-26
