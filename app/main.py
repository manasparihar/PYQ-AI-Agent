from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from slowapi.errors import RateLimitExceeded
from slowapi import _rate_limit_exceeded_handler
from app.core.security import limiter, PayloadSizeLimitMiddleware, TimeoutMiddleware
from app.config import settings
import logging

from app.routes import ai_routes
from app.routes import search_routes
from app.routes import conversation_routes
from app.routes import pdf_routes

# Configure logging to print useful logs in terminal
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI application
app = FastAPI(
    title="PYQ AI Agent API",
    description="Backend for AI-powered PYQ Agent using Gemini and Tavily",
    version="1.0.0"
)

# 1. Attach Rate Limiter to FastAPI app
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# 2. Add Security Middlewares (Order matters: outermost first)
app.add_middleware(TimeoutMiddleware)
app.add_middleware(PayloadSizeLimitMiddleware)

# 3. Add Secure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL] if settings and settings.FRONTEND_URL else ["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "HEAD", "OPTIONS"], # Limit methods
    allow_headers=["*"],
)

# Mount the static directory so the frontend can download PDFs
import os
os.makedirs("generated_pdfs", exist_ok=True)
app.mount("/generated_pdfs", StaticFiles(directory="generated_pdfs"), name="generated_pdfs")

# 4. Hardened Global exception handler
# Prevents leaking internal stack traces or database errors to the public client
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.critical(f"Unhandled system error on {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"success": False, "error": "Internal Server Error. Please try again later."}
    )

# Safely include routers
try:
    app.include_router(ai_routes.router)
    app.include_router(search_routes.router)
    app.include_router(conversation_routes.router)
    app.include_router(pdf_routes.router)
    logger.info("Routers included successfully.")
except Exception as e:
    logger.error(f"Error including routers during startup: {e}")

@app.get("/")
@app.head("/")
async def root():
    """
    Root endpoint to verify the API is running.
    """
    return {"message": "API running"}

@app.get("/health")
@app.head("/health")
async def health_check():
    """
    Health check endpoint for monitoring the status of the service.
    """
    return {"status": "healthy"}
