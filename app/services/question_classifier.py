import json
import logging
from app.services.gemini_service import ask_gemini

logger = logging.getLogger(__name__)

def classify_questions(topic: str, questions: list) -> list:
    """
    Evaluates candidate questions to determine if they belong to the requested topic, 
    their confidence score as a real PYQ, and their exam relevance.
    """
    if not questions:
        return []
        
    prompt = f"""
    You are an expert PYQ evaluator. I will provide you with a requested topic and a list of candidate questions.
    For each question, evaluate:
    1. is_relevant: Does it strongly belong to the requested topic "{topic}"? (true/false)
    2. confidence_score: From 0 to 100, how confident are you this is a real competitive exam PYQ?
    3. exam_relevance: Is it highly relevant for exams like RPSC, SSC, Banking, etc.? (High/Medium/Low)
    
    Return ONLY a raw JSON array of objects, in the same order as the questions. 
    Do NOT include markdown like ```json or any other text.
    Example:
    [
        {{"is_relevant": true, "confidence_score": 95, "exam_relevance": "High"}},
        {{"is_relevant": false, "confidence_score": 40, "exam_relevance": "Low"}}
    ]
    
    Questions:
    """
    
    for i, q in enumerate(questions):
        prompt += f"\n{i+1}. {q.get('question_text', '')}"
        
    try:
        response = ask_gemini(prompt)
        if response.get("success"):
            text = response.get("response", "")
            # Clean up potential markdown formatting
            text = text.replace("```json", "").replace("```", "").strip()
            
            # Find JSON array boundaries if there is extra text
            start_idx = text.find('[')
            end_idx = text.rfind(']') + 1
            if start_idx != -1 and end_idx != 0:
                text = text[start_idx:end_idx]
                
            evaluations = json.loads(text)
            
            classified_questions = []
            for i, q in enumerate(questions):
                if i < len(evaluations):
                    eval_data = evaluations[i]
                    # Filter based on strict criteria
                    if eval_data.get("is_relevant") and eval_data.get("confidence_score", 0) > 60 and eval_data.get("exam_relevance") in ["High", "Medium"]:
                        q["classification"] = eval_data
                        classified_questions.append(q)
            
            # If everything was filtered out, fallback to returning the original list
            # so the user doesn't get an empty response. We assume generation is mostly good.
            if not classified_questions and questions:
                return questions
                
            return classified_questions
    except Exception as e:
        logger.error(f"Error classifying questions: {e}")
        # Fallback: return all if classification fails to avoid breaking pipeline
        return questions
        
    return questions
