import google.generativeai as genai
from app.config import GEMINI_API_KEY
import logging

logger = logging.getLogger(__name__)

# Safely initialize the model outside the request flow to avoid startup crashes
try:
    if GEMINI_API_KEY and GEMINI_API_KEY != "your_gemini_api_key_here":
        genai.configure(api_key=GEMINI_API_KEY)
    else:
        logger.warning("GEMINI_API_KEY is not set or invalid in .env.")
except Exception as e:
    logger.error(f"Failed to configure Gemini API at startup: {e}")

def ask_gemini(prompt: str):
    """
    Safely asks Gemini a question and handles errors without hanging.
    """
    try:
        if not GEMINI_API_KEY or GEMINI_API_KEY == "your_gemini_api_key_here":
            return {"success": False, "error": "Gemini API key is missing. Please check .env file."}
            
        logger.info("Initializing Gemini model instance.")
        model = genai.GenerativeModel("gemini-2.5-flash")
        
        logger.info("Sending prompt to Gemini API.")
        response = model.generate_content(prompt)
        
        if not response or not response.text:
            return {"success": False, "error": "Empty response returned from Gemini."}

        cleaned_response = response.text.strip()
        return {
            "success": True,
            "response": cleaned_response
        }

    except Exception as e:
        logger.error(f"Gemini API error occurred: {e}")
        return {
            "success": False,
            "error": "Failed to communicate with Gemini API.",
            "details": str(e)
        }

def stream_gemini_generator(prompt: str):
    """
    Generator that yields chunks of the Gemini response as they stream in.
    """
    if not GEMINI_API_KEY or GEMINI_API_KEY == "your_gemini_api_key_here":
        yield "Error: Gemini API key is missing. Please check .env file."
        return
        
    try:
        logger.info("Initializing Gemini model instance for streaming.")
        model = genai.GenerativeModel("gemini-2.5-flash")
        
        logger.info("Sending prompt to Gemini API with stream=True.")
        response = model.generate_content(prompt, stream=True)
        
        for chunk in response:
            if chunk.text:
                yield chunk.text
                
    except Exception as e:
        logger.error(f"Gemini API streaming error occurred: {e}")
        yield f"\n\nError: Failed to stream from Gemini API. Details: {str(e)}"