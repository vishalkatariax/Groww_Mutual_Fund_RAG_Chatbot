###############################################################################
# MF FAQ Assistant — Single-container Dockerfile for Railway
#
# Stages:
#   frontend-builder  — builds React app with Node
#   py-builder        — installs Python deps (PyTorch CPU + requirements.txt)
#   production        — final lean image with everything bundled
###############################################################################

# ── Stage 1: Build React frontend ─────────────────────────────────────────
FROM node:20-alpine AS frontend-builder

WORKDIR /frontend

COPY app/frontend/package.json app/frontend/package-lock.json ./
RUN npm ci

COPY app/frontend/ .

# VITE_API_URL is empty — api.ts uses relative /api/v1/* paths
# FastAPI serves both API and frontend on the same Railway origin
RUN npm run build

# ── Stage 2: Install Python dependencies ──────────────────────────────────
FROM python:3.11-slim AS py-builder

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /build

COPY requirements.txt .

# PyTorch CPU-only must be installed before sentence-transformers
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu \
    && pip install --no-cache-dir -r requirements.txt

# ── Stage 3: Production image ──────────────────────────────────────────────
FROM python:3.11-slim AS production

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy installed Python packages from builder
COPY --from=py-builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=py-builder /usr/local/bin /usr/local/bin

# Copy application source
COPY app/ ./app/
COPY config.py .
COPY scripts/build_vectorstore.py ./scripts/build_vectorstore.py

# Copy built React frontend
COPY --from=frontend-builder /frontend/dist ./app/frontend/dist

# Copy pre-chunked data (small JSON files, no binary blobs)
COPY data/processed/ ./data/processed/
RUN mkdir -p data/raw data/chroma_db

# Pre-download BGE model and build ChromaDB — runs as a script, not inline Python
# so Docker parser never sees import/from statements as Dockerfile instructions
RUN python scripts/build_vectorstore.py

# Non-root user for security
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:${PORT:-8000}/ping || exit 1

# Railway injects $PORT at runtime
CMD ["sh", "-c", "python -m uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
