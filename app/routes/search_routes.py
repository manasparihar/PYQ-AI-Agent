from fastapi import APIRouter, Query, Request
from app.services.search_service import search_pyq_pdfs
from app.core.security import limiter
import logging

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Search Agent"])

@router.get("/search-pdfs")
@limiter.limit("20/minute") # Protect search queries
def search_pdfs_endpoint(request: Request, topic: str = Query("Rajasthan History", description="Topic to search PYQ PDFs for")):
    """
    Endpoint to dynamically search for previous year question PDFs.
    """
    try:
        logger.info(f"Received request for /search-pdfs with topic: {topic}")
        result = search_pyq_pdfs(topic)
        return result
    except Exception as e:
        logger.error(f"Error in /search-pdfs route: {e}")
        return {
            "success": False, 
            "error": "Failed to perform search.", 
            "details": str(e)
        }
