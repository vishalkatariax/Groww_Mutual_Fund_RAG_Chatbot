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
FROM base AS py-builder

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
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

# Create data directories
RUN mkdir -p data/raw data/processed data/chroma_db

# Non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:${PORT:-8000}/ping || exit 1

# Railway injects $PORT; fall back to 8000 locally
CMD ["sh", "-c", "python -m uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
