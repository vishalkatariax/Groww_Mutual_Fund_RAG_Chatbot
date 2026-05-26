"""
Phase 5: Health API Endpoint

GET /api/v1/health - Health check endpoint
"""

import logging
import time
from datetime import datetime

from fastapi import APIRouter

from app.models.schemas import HealthResponse
from config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["health"])

# Track server start time
SERVER_START_TIME = time.time()


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Health check",
    description="Returns the health status of the API server and vector store.",
)
async def health_check():
    """
    Check the health status of the API server.
    
    Returns:
    - Server status (healthy/degraded/unhealthy)
    - Vector store document count
    - Last ingestion timestamp
    - LLM provider info
    - Server uptime
    """
    try:
        # Check vector store health
        vector_store_docs = 0
        last_ingestion = None
        
        try:
            from app.phase1.subphase_1_2_chunking_embedding.vector_store import VectorStore
            
            vs = VectorStore()
            collection = vs.collection
            vector_store_docs = collection.count()
            
            # Try to get last ingestion time from metadata
            if collection.metadata:
                last_ingestion = collection.metadata.get("last_ingestion")
        
        except Exception as e:
            logger.warning(f"Vector store health check failed: {e}")
            vector_store_docs = 0
        
        # Calculate uptime
        uptime_seconds = time.time() - SERVER_START_TIME
        
        # Determine health status
        if vector_store_docs > 0:
            status = "healthy"
        else:
            status = "degraded"  # Vector store empty but server running
        
        return HealthResponse(
            status=status,
            vector_store_docs=vector_store_docs,
            last_ingestion=last_ingestion,
            version="1.0.0",
            llm_provider=settings.llm_provider,
            uptime_seconds=round(uptime_seconds, 2),
        )
    
    except Exception as e:
        logger.error(f"Health check failed: {e}", exc_info=True)
        return HealthResponse(
            status="unhealthy",
            vector_store_docs=0,
            last_ingestion=None,
            version="1.0.0",
            llm_provider=settings.llm_provider,
            uptime_seconds=round(time.time() - SERVER_START_TIME, 2),
        )
