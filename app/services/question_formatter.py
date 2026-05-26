import logging

logger = logging.getLogger(__name__)

def format_questions(questions: list) -> str:
    """
    Formats the final questions into the strict PDF-friendly layout:
    
    Q1. [Question text]
    ([Exam Name] - [Year])
    
    Answer:
    [Concise Answer Text]
    
    ------------------------------------------------
    """
    if not questions:
        return "No relevant PYQs found for this topic."
        
    formatted_output = ""
    for i, q in enumerate(questions, 1):
        q_text = q.get("question_text", "Unknown Question").strip()
        exam_year = q.get("exam_year", "Exam - Year Unknown").strip()
        answer = q.get("answer", "Answer not available.").strip()
        
        # Ensure concise answers (remove long paragraphs if present, though generation should handle it)
        answer_lines = [line.strip() for line in answer.split('\n') if line.strip()]
        concise_answer = " ".join(answer_lines)
        
        # Avoid fake years / exams by ensuring it has alphanumeric characters and not just placeholders
        if "exam" in exam_year.lower() and "year" in exam_year.lower() and "unknown" in exam_year.lower():
             exam_year = "Various Exams"
        
        formatted_output += f"Q{i}. {q_text}\n"
        formatted_output += f"({exam_year})\n\n"
        formatted_output += f"Answer:\n{concise_answer}\n\n"
        formatted_output += "-" * 48 + "\n\n"
        
    return formatted_output.strip()
