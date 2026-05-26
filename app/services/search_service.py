from tavily import TavilyClient
from app.config import TAVILY_API_KEY
import logging
import concurrent.futures

logger = logging.getLogger(__name__)

# Safely initialize Tavily client to prevent startup errors
tavily_client = None
try:
    if TAVILY_API_KEY:
        tavily_client = TavilyClient(api_key=TAVILY_API_KEY)
    else:
        logger.warning("TAVILY_API_KEY is not set in .env.")
except Exception as e:
    logger.error(f"Failed to initialize Tavily client at startup: {e}")

def _run_tavily_search(query: str):
    """
    Helper function to run the actual search.
    """
    return tavily_client.search(
        query=query,
        search_depth="advanced",
        max_results=5,
        include_images=False
    )

def search_pyq_pdfs(topic: str) -> dict:
    """
    Uses Tavily API to search for Previous Year Question (PYQ) PDFs 
    with timeout handling and error catching to prevent server hanging.
    """
    if not tavily_client:
        return {
            "success": False,
            "error": "TAVILY_API_KEY is missing or invalid. Check .env file."
        }
        
    try:
        from app.services.search_optimizer import run_optimized_search
        
        logger.info(f"Executing optimized multi-strategy search for topic: {topic}")
        
        # Use ThreadPoolExecutor to implement a manual timeout
        # This prevents the aggregate API calls from blocking the server forever
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(run_optimized_search, topic, tavily_client)
            try:
                # Give it up to 15 seconds to run all parallel queries
                results = future.result(timeout=15)
            except concurrent.futures.TimeoutError:
                logger.error("Tavily optimized search timed out after 15 seconds.")
                return {
                    "success": False,
                    "error": "Search request timed out. The Tavily API took too long to respond."
                }
        
        logger.info(f"Successfully retrieved and ranked {len(results)} optimized results.")
        
        return {
            "success": True,
            "topic": topic,
            "results": results
        }
        
    except Exception as e:
        logger.error(f"Tavily API error occurred: {e}")
        return {
            "success": False,
            "error": "Failed to complete search request.",
            "details": str(e)
        }
