from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.api.routes import health, schemes
import time
import os
from pathlib import Path

# Create FastAPI app
app = FastAPI(
    title="MF FAQ Assistant",
    description="Facts-only Mutual Fund FAQ Assistant for HDFC schemes",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Store server start time
SERVER_START_TIME = time.time()

# Railway will provide PORT env variable, default to 8000
PORT = int(os.getenv("PORT", "8000"))

# Build allowed origins list
# FRONTEND_URL env var lets you pin a specific Vercel URL in Railway dashboard
_frontend_url = os.getenv("FRONTEND_URL", "")
_allowed_origins = [
    "http://localhost:3000",
    "http://localhost:3001",
    "http://localhost:5173",
]
if _frontend_url:
    _allowed_origins.append(_frontend_url)

# FastAPI CORSMiddleware doesn't support wildcard subdomains, so we use
# allow_origin_regex to cover all *.vercel.app deployments.
app.add_middleware(
    CORSMiddleware,
    allow_origins=_allowed_origins,
    allow_origin_regex=r"https://.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers - Chat endpoint now enabled with BGE embeddings
from app.api.routes import chat
app.include_router(chat.router)

app.include_router(health.router)
app.include_router(schemes.router)

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "MF FAQ Assistant API",
        "version": "1.0.0",
        "docs": "/docs",
        "status": "running"
    }

# Health check (simple)
@app.get("/ping")
async def ping():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

# ── Serve React frontend (production / Railway) ───────────────────────────
# Mount static files AFTER all API routes so /api/* is never intercepted.
# The built frontend lives at app/frontend/dist (built during Docker image build).
FRONTEND_DIST = Path(__file__).resolve().parent / "frontend" / "dist"

if FRONTEND_DIST.exists():
    # Serve static assets (JS, CSS, images)
    app.mount("/assets", StaticFiles(directory=str(FRONTEND_DIST / "assets")), name="assets")

    # Catch-all: serve index.html for any non-API route (SPA routing)
    @app.get("/{full_path:path}", include_in_schema=False)
    async def serve_spa(full_path: str):
        index = FRONTEND_DIST / "index.html"
        return FileResponse(str(index))
