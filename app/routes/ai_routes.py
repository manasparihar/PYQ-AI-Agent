from fastapi import APIRouter
from app.services.gemini_service import ask_gemini
import logging

logger = logging.getLogger(__name__)
router = APIRouter(tags=["AI Agent"])

@router.get("/test-ai")
def test_ai(prompt: str = "Tell me 5 important Rajasthan History topics for competitive exams"):
    """
    Test endpoint for the Gemini AI. 
    """
    try:
        logger.info(f"Received request for /test-ai with prompt: {prompt}")
        result = ask_gemini(prompt)
        return result
    except Exception as e:
        logger.error(f"Error in /test-ai route: {e}")
        return {
            "success": False, 
            "error": "Failed to process AI request.", 
            "details": str(e)
        }