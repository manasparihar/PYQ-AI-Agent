"""
Centralized prompt management system for PYQ (Previous Year Questions) Agent.
Ensures Gemini generates consistent, PDF-friendly, and highly structured outputs.
"""

BASE_INSTRUCTIONS = """
You are an expert PYQ (Previous Year Questions) Agent for competitive exams (RPSC, REET, RSSB, SSC, Banking, SI, Teacher Exams).
Your primary goal is to provide accurate, high-quality past exam questions based on the user's request.

STRICT FORMATTING RULES:
You MUST format EVERY question exactly like this, with NO exceptions, NO markdown clutter, and NO conversational filler text before or after the questions:

Q1. [Question text]
([Exam Name] - [Year])

Answer:
[Concise Answer Text]

------------------------------------------------

Rules:
1. Do NOT use paragraphs for explanations. Keep answers extremely concise and factual.
2. Do NOT use heavy markdown (like **, *, #) as it breaks PDF formatting.
3. Separate each question block with exactly one line of 48 hyphens (------------------------------------------------).
4. If it's an MCQ, list the options clearly as A), B), C), D) within the question text.
5. Never add introductory or concluding remarks like "Here are the questions...". Start directly with Q1.
6. AVOID HALLUCINATIONS: Do not invent fake years or fake exams. Use "Various Exams" if the exact year is unknown.
7. TOPIC FILTERING: Ensure every question belongs strongly to the requested topic.
"""

# Specialized prompts for specific subjects to guide the AI's focus
TOPIC_PROMPTS = {
    "rajasthan_history": "Focus on key historical events, dynasties (Mewar, Marwar), 1857 revolt, and integration of Rajasthan.",
    "polity": "Focus on the Constitution of India, fundamental rights, parliament, and state legislature.",
    "geography": "Focus on physical features, climate, rivers, and economic geography of India and Rajasthan.",
    "science": "Focus on general science topics, biology, physics, chemistry, and recent technological advancements.",
    "current_affairs": "Focus on recent national and international events, appointments, sports, and awards."
}

def build_pyq_prompt(user_prompt: str, history: list) -> str:
    """
    Builds the final prompt combining base instructions, history, and the new user prompt.
    """
    # Start with the strict base instructions
    final_prompt = BASE_INSTRUCTIONS + "\n\n"
    
    # Add conversation history for context
    if history:
        final_prompt += "Previous Context:\n"
        # Only take the last 4 messages to avoid context overflow and confusing the strict formatting
        recent_history = history[-4:] 
        for msg in recent_history:
            role = msg.get("role", "user").capitalize()
            content = msg.get("content", "")
            final_prompt += f"{role}: {content}\n"
        final_prompt += "\n"
        
    final_prompt += f"User Request: {user_prompt}\n"
    final_prompt += "Assistant Response (STRICT FORMAT ONLY):"
    
    return final_prompt
