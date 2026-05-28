from fastapi import APIRouter, HTTPException, Path, Request
from fastapi.responses import StreamingResponse
from app.schemas.conversation_schema import ChatRequest
from app.services.conversation_service import (
    create_new_session,
    add_message_to_session,
    get_session_history,
    delete_session
)
from app.services.pyq_pipeline_service import generate_pyq_response
from app.core.security import limiter
import logging
import asyncio

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/conversation", tags=["Conversation Memory"])

@router.post("/create-session")
def create_session_endpoint():
    """
    Endpoint: Creates a new temporary chat session and returns its ID.
    """
    try:
        session_id = create_new_session()
        return {"success": True, "session_id": session_id}
    except Exception as e:
        logger.error(f"Error creating session: {e}")
        raise HTTPException(status_code=500, detail="Failed to create session")

@router.post("/chat/{session_id}")
def chat_endpoint(request: ChatRequest, session_id: str = Path(..., description="The ID of the session")):
    """
    Endpoint: Accepts a user prompt, generates an AI response, 
    and stores both messages in the RAM memory for this session.
    """
    try:
        history = get_session_history(session_id)
        
        # 1. Store the user's message in RAM
        add_message_to_session(session_id, role="user", content=request.prompt)
        
        logger.info(f"Generating structured PYQ response for session {session_id}")
        
        # 2. Run the PYQ pipeline
        ai_response_text = generate_pyq_response(request.prompt, history)
        
        # 3. Store the AI's response in RAM
        add_message_to_session(session_id, role="assistant", content=ai_response_text)
        
        return {
            "success": True,
            "session_id": session_id,
            "response": ai_response_text
        }
        
    except ValueError as ve:
        logger.error(f"Validation error in chat endpoint: {ve}")
        raise HTTPException(status_code=404, detail=str(ve))
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/chat-stream/{session_id}")
@limiter.limit("10/minute")
def chat_stream_endpoint(request: Request, chat_req: ChatRequest, session_id: str = Path(..., description="The ID of the session")):
    """
    Endpoint: Streams the generated PYQ response.
    Note: Due to the multi-step pipeline (extraction, classification, deduplication),
    the initial wait time will be longer, but the final output is streamed for UX.
    """
    try:
        history = get_session_history(session_id)
        
        # 1. Store the user's message in RAM
        add_message_to_session(session_id, role="user", content=chat_req.prompt)
        
        logger.info(f"Generating structured PYQ response for session {session_id} (Streaming)")
        
        async def event_generator():
            # Send an immediate heartbeat to prevent Render 504 Gateway Timeout
            yield " "
            await asyncio.sleep(0.1)
            
            # Run the heavy synchronous pipeline in a background thread to not block the event loop
            final_response_text = await asyncio.to_thread(generate_pyq_response, chat_req.prompt, history)
            
            # Simulate streaming by yielding chunks of the final string
            chunk_size = 50
            for i in range(0, len(final_response_text), chunk_size):
                yield final_response_text[i:i+chunk_size]
                await asyncio.sleep(0.02)  # slight delay to mimic typing
            
            # Save to memory once done
            add_message_to_session(session_id, role="assistant", content=final_response_text)
            
        return StreamingResponse(event_generator(), media_type="text/event-stream")
        
    except ValueError as ve:
        logger.error(f"Validation error in chat-stream endpoint: {ve}")
        raise HTTPException(status_code=404, detail=str(ve))
    except Exception as e:
        logger.error(f"Error in chat-stream endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/session/{session_id}")
def get_session_endpoint(session_id: str = Path(..., description="The ID of the session")):
    """
    Endpoint: Returns the complete conversation history for a given session.
    """
    try:
        history = get_session_history(session_id)
        return {
            "success": True,
            "session_id": session_id,
            "messages": history
        }
    except ValueError as ve:
        raise HTTPException(status_code=404, detail=str(ve))
    except Exception as e:
        logger.error(f"Error fetching session: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch session history")

@router.delete("/session/{session_id}")
def delete_session_endpoint(session_id: str = Path(..., description="The ID of the session to delete")):
    """
    Endpoint: Deletes a session completely from memory.
    """
    try:
        success = delete_session(session_id)
        if not success:
            raise ValueError(f"Session ID {session_id} not found.")
            
        return {"success": True, "message": f"Session {session_id} deleted successfully"}
    except ValueError as ve:
        raise HTTPException(status_code=404, detail=str(ve))
    except Exception as e:
        logger.error(f"Error deleting session: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete session")
