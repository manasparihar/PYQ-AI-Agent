from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field
import logging
import os
from app.services.pdf_service import generate_content_pdf
from app.core.security import limiter

logger = logging.getLogger(__name__)
router = APIRouter(tags=["PDF Export"])

class PDFRequest(BaseModel):
    title: str = Field(default="AI PYQ Response Export", max_length=100)
    content: str = Field(..., max_length=15000, description="Content to render into PDF")

@router.post("/generate-pdf")
@limiter.limit("5/minute") # Generating PDFs is resource intensive
def generate_pdf_endpoint(request_obj: Request, request: PDFRequest):
    """
    Endpoint: Generates a formatted PDF from any provided text content.
    """
    try:
        logger.info("Received request to generate PDF for specific content")
        
        # 1. Validate input
        if not request.content or not request.content.strip():
            raise HTTPException(status_code=400, detail="Content cannot be empty.")
            
        # 2. Generate PDF automatically using the PDF service
        pdf_path = generate_content_pdf(title=request.title, content=request.content)
        
        # 3. Construct public downloadable URL safely for any OS
        filename = os.path.basename(pdf_path)
        pdf_url = f"/generated_pdfs/{filename}"
        
        # 4. Return JSON response with frontend-ready format
        return {
            "success": True,
            "pdf_url": pdf_url,
            "filename": filename
        }
        
    except HTTPException as http_e:
        raise http_e
    except Exception as e:
        logger.error(f"Unexpected error generating PDF: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate PDF")
