"""
Phase 5: Chat API Endpoint

POST /api/v1/chat - Main chat endpoint for processing user queries
"""

import logging
import time
import uuid
from typing import Optional

from fastapi import APIRouter, HTTPException

from app.core.intent_classifier import intent_classifier
from app.core.refusal_handler import refusal_handler
from app.core.response_validator import response_validator
from app.models.schemas import ChatRequest, ChatResponse, ErrorResponse
from app.phase1.subphase_1_3_rag_setup.rag_pipeline import RAGPipeline
from app.phase1.subphase_1_4_compliance.compliance_pipeline import CompliancePipeline
from config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["chat"])

# Lazy initialization of pipelines (deferred until first use)
_rag_pipeline = None
_compliance_pipeline = None


def get_rag_pipeline():
    """Lazy load RAG pipeline on first use."""
    global _rag_pipeline
    if _rag_pipeline is None:
        try:
            _rag_pipeline = RAGPipeline()
        except ValueError as e:
            logger.error(f"Failed to initialize RAG pipeline: {e}")
            raise
    return _rag_pipeline


def get_compliance_pipeline():
    """Lazy load compliance pipeline on first use."""
    global _compliance_pipeline
    if _compliance_pipeline is None:
        try:
            _compliance_pipeline = CompliancePipeline()
        except Exception as e:
            logger.error(f"Failed to initialize compliance pipeline: {e}")
            raise
    return _compliance_pipeline


@router.post(
    "/chat",
    response_model=ChatResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Bad Request - Invalid input"},
        422: {"model": ErrorResponse, "description": "Validation Error"},
        500: {"model": ErrorResponse, "description": "Internal Server Error"},
    },
    summary="Process user chat query",
    description="Processes a user query through the RAG pipeline and returns a factual response about HDFC Mutual Fund schemes.",
)
async def chat(request: ChatRequest):
    """
    Process a user query and return a response.
    
    Workflow:
    1. Input guardrails validation
    2. Intent classification (factual/advisory/ambiguous)
    3. Route to RAG pipeline or refusal handler
    4. Output guardrails validation
    5. Return compliant response
    """
    start_time = time.time()
    request_id = str(uuid.uuid4())
    
    try:
        logger.info(f"[{request_id}] Processing query: {request.query[:50]}...")
        
        # Step 1: Input guardrails validation
        compliance_pipeline = get_compliance_pipeline()
        is_valid, message, sanitized_query = compliance_pipeline.process_query(request.query)
        
        if not is_valid:
            if message == "ADVISORY_DETECTED":
                # Route to refusal handler
                refusal_response = refusal_handler.handle_advisory(
                    query=sanitized_query or request.query,
                    source_url="https://groww.in/mutual-funds",
                )
                response_time = (time.time() - start_time) * 1000
                
                return ChatResponse(
                    answer=refusal_response["answer"],
                    source_url=refusal_response["source_url"],
                    last_updated=refusal_response["last_updated"],
                    is_refusal=True,
                    query_type="advisory",
                    response_time_ms=round(response_time, 2),
                )
            else:
                # Input validation failed
                response_time = (time.time() - start_time) * 1000
                raise HTTPException(
                    status_code=400,
                    detail={
                        "error": "ValidationError",
                        "message": message,
                        "request_id": request_id,
                    },
                )
        
        # Step 2: Intent classification
        intent_result = intent_classifier.classify(sanitized_query)
        intent_type = intent_result["intent"]
        
        logger.info(f"[{request_id}] Intent: {intent_type} (confidence: {intent_result['confidence']})")
        
        # Step 3: Route based on intent
        if intent_type == "advisory":
            refusal_response = refusal_handler.handle_advisory(
                query=sanitized_query,
                source_url="https://groww.in/mutual-funds",
            )
            response_time = (time.time() - start_time) * 1000
            
            return ChatResponse(
                answer=refusal_response["answer"],
                source_url=refusal_response["source_url"],
                last_updated=refusal_response["last_updated"],
                is_refusal=True,
                query_type="advisory",
                response_time_ms=round(response_time, 2),
            )
        
        elif intent_type == "ambiguous":
            refusal_response = refusal_handler.handle_ambiguous(
                query=sanitized_query,
                source_url="https://groww.in/mutual-funds",
            )
            response_time = (time.time() - start_time) * 1000
            
            return ChatResponse(
                answer=refusal_response["answer"],
                source_url=refusal_response["source_url"],
                last_updated=refusal_response["last_updated"],
                is_refusal=True,
                query_type="ambiguous",
                response_time_ms=round(response_time, 2),
            )
        
        else:
            # Factual query - route to RAG pipeline
            try:
                rag_pipeline = get_rag_pipeline()
                rag_result = rag_pipeline.query(sanitized_query)
                answer = rag_result.get("response", "")
                
                if not answer:
                    logger.warning(f"[{request_id}] RAG pipeline returned empty response")
                    answer = "I couldn't generate a response to your question. Please try rewording it."
                    rag_result = {"metadata": {"chunks_retrieved": 0}}
                
                source_url = None
                
                # Extract source URL from metadata if available
                if rag_result.get("retrieved_chunks"):
                    source_url = rag_result["retrieved_chunks"][0].get("metadata", {}).get("source_url")
            except Exception as rag_error:
                logger.error(f"[{request_id}] RAG pipeline error: {rag_error}", exc_info=True)
                raise HTTPException(
                    status_code=500,
                    detail={
                        "error": "RAGPipelineError",
                        "message": f"Error processing query through RAG: {str(rag_error)}",
                        "request_id": request_id,
                    },
                )
            
            # Step 4: Output guardrails validation
            is_valid, val_message, validated_response = compliance_pipeline.process_response(
                response=answer,
                source_url=source_url,
                is_refusal=False,
            )
            
            if not is_valid:
                logger.warning(f"[{request_id}] Response validation failed: {val_message}")
                # Fallback to refusal
                fallback_response = refusal_handler.handle_not_found(
                    query=sanitized_query,
                    source_url=source_url or "https://groww.in/mutual-funds",
                )
                answer = fallback_response["answer"]
                source_url = fallback_response["source_url"]
            else:
                answer = validated_response or answer
            
            # Calculate response time
            response_time = (time.time() - start_time) * 1000
            
            from datetime import datetime
            today = datetime.now().strftime("%Y-%m-%d")
            
            return ChatResponse(
                answer=answer,
                source_url=source_url,
                last_updated=today,
                is_refusal=False,
                query_type="factual",
                response_time_ms=round(response_time, 2),
                chunks_retrieved=rag_result.get("metadata", {}).get("chunks_retrieved", 0),
            )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[{request_id}] Unexpected error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                "error": "InternalError",
                "message": "An unexpected error occurred while processing your query",
                "request_id": request_id,
            },
        )
