###############################################################################
# MF FAQ Assistant — Single-container Dockerfile for Railway
#
# Strategy: Build React frontend, then copy dist into the Python image.
# FastAPI serves the SPA from /app/app/frontend/dist at runtime.
#
# For local docker-compose, the separate frontend service uses
# app/frontend/Dockerfile instead.
###############################################################################

# ── Stage 1: Build React frontend ─────────────────────────────────────────
FROM node:20-alpine AS frontend-builder

WORKDIR /frontend

COPY app/frontend/package.json app/frontend/package-lock.json ./
RUN npm ci

COPY app/frontend/ .

# VITE_API_URL left empty → api.ts falls back to relative '/api/v1'
# which works because FastAPI serves both API and frontend on the same origin.
RUN npm run build

# ── Stage 2: Python base ───────────────────────────────────────────────────
FROM python:3.11-slim AS base

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# ── Stage 3: Install Python dependencies ──────────────────────────────────
FROM python:3.11-slim AS py-builder

COPY requirements.txt .
# Install PyTorch CPU-only first (sentence-transformers dependency, ~200MB lighter than GPU)
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu \
    && pip install --no-cache-dir -r requirements.txt

# ── Stage 4: Production image ──────────────────────────────────────────────
FROM base AS production

# Copy Python packages
COPY --from=py-builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=py-builder /usr/local/bin /usr/local/bin

# Copy backend source
COPY app/ ./app/
COPY config.py .

# Copy built frontend into the location FastAPI expects
COPY --from=frontend-builder /frontend/dist ./app/frontend/dist

# Copy pre-built chunks (JSON, small — used to rebuild ChromaDB at build time)
COPY data/processed/ ./data/processed/
RUN mkdir -p data/raw data/chroma_db

# Pre-download BGE model and build ChromaDB from chunks in one step
RUN python -c "
from sentence_transformers import SentenceTransformer
print('Downloading BGE model...')
SentenceTransformer('BAAI/bge-small-en-v1.5')
print('BGE model cached')
" && python -c "
import sys, json
sys.path.insert(0, '/app')
from app.phase1.subphase_1_2_chunking_embedding.embedder import EmbeddingPipeline
from app.phase1.subphase_1_2_chunking_embedding.vector_store import VectorStore
chunks_path = '/app/data/processed/chunks.json'
with open(chunks_path) as f:
    chunks = json.load(f)
vs = VectorStore()
if vs.collection.count() == 0:
    embedder = EmbeddingPipeline()
    chunks = embedder.generate_embeddings(chunks)
    vs.add_chunks(chunks)
    print(f'Built ChromaDB: {vs.collection.count()} chunks')
else:
    print(f'ChromaDB already has {vs.collection.count()} chunks')
"

# Non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:${PORT:-8000}/ping || exit 1

# Railway injects $PORT; fall back to 8000 locally
CMD ["sh", "-c", "python -m uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
