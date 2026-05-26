import difflib
import logging

logger = logging.getLogger(__name__)

def remove_duplicates(questions: list) -> list:
    """
    Removes exact and semantically similar duplicate questions using SequenceMatcher.
    """
    if not questions:
        return []
        
    unique_questions = []
    
    for current_q in questions:
        current_text = current_q.get("question_text", "").lower().strip()
        is_duplicate = False
        
        for unique_q in unique_questions:
            unique_text = unique_q.get("question_text", "").lower().strip()
            
            # Use SequenceMatcher for semantic similarity
            similarity = difflib.SequenceMatcher(None, current_text, unique_text).ratio()
            
            if similarity > 0.85: # 85% similarity threshold
                is_duplicate = True
                break
                
        if not is_duplicate:
            unique_questions.append(current_q)
            
    return unique_questions
