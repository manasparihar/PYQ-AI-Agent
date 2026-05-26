import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    GEMINI_API_KEY: str = Field(..., description="API Key for Google Gemini")
    TAVILY_API_KEY: str = Field(..., description="API Key for Tavily Search")
    
    # Allows configuring CORS in production
    FRONTEND_URL: str = Field(default="http://localhost:5173", description="Allowed CORS origin")
    
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

# Initialize settings - will throw a validation error on startup if required variables are missing
try:
    settings = Settings()
    GEMINI_API_KEY = settings.GEMINI_API_KEY
    TAVILY_API_KEY = settings.TAVILY_API_KEY
except Exception as e:
    import logging
    logging.critical(f"Environment Variable Configuration Error: {e}")
    # Provide a graceful fallback to prevent immediate crashes when testing locally without a fully configured .env
    # But in strict production, we would want this to crash (sys.exit(1)).
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
    settings = None
