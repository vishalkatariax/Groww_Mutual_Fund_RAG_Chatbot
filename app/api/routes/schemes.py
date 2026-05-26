"""
Phase 5: Schemes API Endpoint

GET /api/v1/schemes - List available mutual fund schemes
"""

import logging

from fastapi import APIRouter

from app.models.schemas import SchemeInfo, SchemesResponse
from config import GROWW_SCHEMES

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["schemes"])


@router.get(
    "/schemes",
    response_model=SchemesResponse,
    summary="List available mutual fund schemes",
    description="Returns a list of all available HDFC Mutual Fund schemes in the corpus.",
)
async def list_schemes():
    """
    Get list of all available mutual fund schemes.
    
    Returns scheme name, category, AMC, and Groww URL for each scheme.
    """
    logger.info("Fetching list of available schemes")
    
    schemes = [
        SchemeInfo(
            name=scheme["scheme_name"],
            category=scheme["category"],
            amc="HDFC Mutual Fund",
            url=scheme["url"],
        )
        for scheme in GROWW_SCHEMES
    ]
    
    return SchemesResponse(
        schemes=schemes,
        total_count=len(schemes),
    )
