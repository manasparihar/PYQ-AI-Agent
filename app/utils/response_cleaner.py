"""
Utility functions to clean and format AI responses for PDF generation.
"""
import re

def clean_ai_response(response_text: str) -> str:
    """
    Cleans up the AI response by removing excessive markdown and messy formatting 
    to ensure the output is ready for beautiful PDF export.
    """
    if not response_text:
        return ""
        
    cleaned = response_text
    
    # 1. Remove bold and italic markdown clutter (**, __, ##)
    cleaned = cleaned.replace("**", "")
    cleaned = cleaned.replace("__", "")
    cleaned = cleaned.replace("## ", "")
    cleaned = cleaned.replace("### ", "")
    
    # 2. Remove conversational fillers if Gemini disobeys instructions
    fillers = [
        "Here are the questions:",
        "Here are some previous year questions:",
        "Certainly!",
        "Sure,"
    ]
    for filler in fillers:
        if cleaned.strip().startswith(filler):
            cleaned = cleaned.replace(filler, "", 1)
            
    # 3. Normalize the separator
    # Sometimes AI might output varying lengths of hyphens. We normalize it to exactly 48 hyphens.
    cleaned = re.sub(r'-{10,}', '-' * 48, cleaned)
    
    # 4. Strip leading/trailing whitespaces and empty lines at the start
    cleaned = cleaned.strip()
    
    return cleaned
