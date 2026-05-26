import uuid
import datetime
import logging
from typing import Dict, List

logger = logging.getLogger(__name__)

# Temporary in-memory storage for conversations (Disappears on server restart)
# Format: { "session_id": [{"role": "user", "content": "...", "timestamp": "..."}, ...] }
conversation_store: Dict[str, List[dict]] = {}

def create_new_session() -> str:
    """
    Creates a new unique session ID and initializes an empty message list in memory.
    """
    session_id = str(uuid.uuid4())
    conversation_store[session_id] = []
    logger.info(f"Created new conversation session: {session_id}")
    return session_id

def add_message_to_session(session_id: str, role: str, content: str) -> dict:
    """
    Appends a message (either 'user' or 'assistant') to an existing session in memory.
    """
    if session_id not in conversation_store:
        raise ValueError(f"Session ID {session_id} not found.")
        
    timestamp = datetime.datetime.now().isoformat()
    message = {
        "role": role,
        "content": content,
        "timestamp": timestamp
    }
    
    conversation_store[session_id].append(message)
    logger.info(f"Added {role} message to session {session_id}")
    return message

def get_session_history(session_id: str) -> List[dict]:
    """
    Retrieves the complete list of messages for a given session ID.
    """
    if session_id not in conversation_store:
        raise ValueError(f"Session ID {session_id} not found.")
        
    return conversation_store[session_id]

def delete_session(session_id: str) -> bool:
    """
    Completely deletes a session from memory.
    """
    if session_id in conversation_store:
        del conversation_store[session_id]
        logger.info(f"Deleted conversation session: {session_id}")
        return True
    return False
