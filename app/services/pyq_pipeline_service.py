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
    Provide up to 20 high-quality questions.
    
    Return questions ONLY in this exact JSON array format:
    [
        {{
            "question_text": "Full text of the question including options if MCQ.",
            "exam_year": "Exam Name - Year",
            "answer": "Concise correct answer."
        }}
    ]
    
    Do not add introductions. Do not add explanations. Do not add markdown headings.
    """
    
    logger.info("Extracting candidate questions using Gemini...")
    extraction_response = ask_gemini(extraction_prompt)
    if not extraction_response.get("success"):
        logger.error(f"Gemini API failed: {extraction_response}")
        return "Failed to extract candidate questions. Please try again."
        
    raw_text = extraction_response.get("response", "")
    
    logger.info("\n===== RAW GEMINI RESPONSE =====")
    logger.info(raw_text[:500] + "..." if len(raw_text) > 500 else raw_text)
    logger.info("================================")
    
    # --- ROBUST EXTRACTION PIPELINE ---
    candidates = []
    
    # 1. Try JSON Parsing First
    cleaned_text = raw_text.replace("```json", "").replace("```", "").strip()
    start_idx = cleaned_text.find('[')
    end_idx = cleaned_text.rfind(']') + 1
    
    if start_idx != -1 and end_idx != 0:
        json_str = cleaned_text[start_idx:end_idx]
        try:
            candidates = json.loads(json_str)
            logger.info(f"Successfully extracted {len(candidates)} questions using JSON parser.")
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse Gemini candidate extraction as JSON. Error: {e}")
            
    # 2. Fallback to Regex if JSON parsing fails or returns empty
    if not candidates:
        logger.info("Starting Regex fallback extraction...")
        # Split text by common question numbers: Q1., 1., Question 1:, etc.
        question_blocks = re.split(r'(?i)(?:^|\n)(?:Q\d+\.?|\d+\.?|Question\s*\d+\:?)\s+', raw_text)
        
        for block in question_blocks:
            block = block.strip()
            if not block:
                continue
                
            ans_match = re.search(r'(?i)\n*Answer\s*:\s*(.*)', block, re.DOTALL)
            if ans_match:
                question_part = block[:ans_match.start()].strip()
                answer_part = ans_match.group(1).strip()
                
                # Extract exam year if formatted in parentheses at the end
                exam_match = re.search(r'\(([^)]+)\)$', question_part)
                exam_year = "Various Exams"
                if exam_match:
                    exam_year = exam_match.group(1)
                    question_text = question_part[:exam_match.start()].strip()
                else:
                    question_text = question_part
                    
                candidates.append({
                    "question_text": question_text,
                    "exam_year": exam_year,
                    "answer": answer_part
                })
                
        if candidates:
            logger.info(f"Successfully extracted {len(candidates)} questions using Regex fallback parser.")
        else:
            logger.error("Regex parsing also failed to extract any questions.")
            
    if not candidates:
        return "Failed to process question data due to formatting mismatch. Please try another query."
        
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
