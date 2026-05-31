from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import health, schemes
import time
import os

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
_frontend_url = os.getenv("FRONTEND_URL", "")
_allowed_origins = [
    "http://localhost:3000",
    "http://localhost:3001",
    "http://localhost:5173",
]
if _frontend_url:
    _allowed_origins.append(_frontend_url)

app.add_middleware(
    CORSMiddleware,
    allow_origins=_allowed_origins,
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
