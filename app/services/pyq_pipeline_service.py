import logging
import json
import re
from app.services.search_service import search_pyq_pdfs
from app.services.gemini_service import ask_gemini
from app.services.question_classifier import classify_questions
from app.services.deduplication_service import remove_duplicates
from app.services.question_formatter import format_questions

logger = logging.getLogger(__name__)

def generate_pyq_response(topic: str, history: list = None) -> str:
    """
    Orchestrates the PYQ generation pipeline.
    Flow:
    1. Search relevant PYQ sources
    2. Extract candidate questions (using Gemini)
    3. Classify topic relevance
    4. Remove duplicates
    5. Format professionally
    """
    logger.info(f"Starting PYQ pipeline for topic: {topic}")
    
    # 1. Search for Context
    # Try to fetch some context using search
    search_results = search_pyq_pdfs(topic)
    context_text = ""
    if search_results.get("success"):
        for res in search_results.get("results", [])[:3]:
            context_text += f"- Title: {res.get('title')}\n  URL: {res.get('url')}\n  Snippet: {res.get('content')}\n\n"
            
    history_context = ""
    if history:
        history_context = "Previous Conversation Context:\n"
        for msg in history[-4:]:
            role = msg.get("role", "user").capitalize()
            content = msg.get("content", "")
            history_context += f"{role}: {content}\n"
    
    # 2. Extract Candidate Questions
    extraction_prompt = f"""
    You are an expert PYQ extractor for competitive exams (RPSC, REET, RSSB, SSC, Banking, SI, Teacher Exams).
    Extract or generate highly accurate Previous Year Questions for the topic: "{topic}".
    If search context is provided, use it to ensure authenticity.
    
    {history_context}
    
    Search Context:
    {context_text}
    
    Return a raw JSON array of objects. Do NOT use markdown code blocks.
    Ensure answers are concise, factual, and not long explanations.
    Do not invent fake years or exams. If exact year is unknown, use "Various Exams".
    Provide exactly 5 to 7 high-quality questions.
    
    Format EXACTLY like this:
    [
        {{
            "question_text": "Full text of the question including options if MCQ.",
            "exam_year": "Exam Name - Year",
            "answer": "Concise correct answer."
        }}
    ]
    """
    
    logger.info("Extracting candidate questions using Gemini...")
    extraction_response = ask_gemini(extraction_prompt)
    if not extraction_response.get("success"):
        return "Failed to extract candidate questions. Please try again."
        
    raw_text = extraction_response.get("response", "")
    
    # Clean JSON format from markdown
    raw_text = raw_text.replace("```json", "").replace("```", "").strip()
    
    # Find JSON array boundaries
    start_idx = raw_text.find('[')
    end_idx = raw_text.rfind(']') + 1
    if start_idx != -1 and end_idx != 0:
        raw_text = raw_text[start_idx:end_idx]
    
    try:
        candidates = json.loads(raw_text)
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse Gemini candidate extraction as JSON. Text: {raw_text[:100]}... Error: {e}")
        return "Failed to process question data. Please try another query."
        
    if not candidates:
        return "No candidate questions could be generated."
        
    # 3. Classify and Filter
    logger.info(f"Classifying {len(candidates)} candidate questions...")
    classified_candidates = classify_questions(topic, candidates)
    
    # 4. Remove Duplicates
    logger.info(f"Deduplicating {len(classified_candidates)} questions...")
    unique_candidates = remove_duplicates(classified_candidates)
    
    # 5. Format Output
    logger.info("Formatting final output...")
    final_output = format_questions(unique_candidates)
    
    return final_output
