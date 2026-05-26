from slowapi import Limiter
from slowapi.util import get_remote_address
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi.responses import JSONResponse
import logging
import asyncio

logger = logging.getLogger(__name__)

# 1. Rate Limiting Initialization
# Uses the user's IP address to track limits
limiter = Limiter(key_func=get_remote_address)

# 2. Payload Size Limit Middleware
# Rejects any request with a body larger than 2MB to prevent memory-exhaustion DoS attacks
MAX_PAYLOAD_SIZE = 2 * 1024 * 1024 # 2MB

class PayloadSizeLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.method in ["POST", "PUT", "PATCH"]:
            content_length = request.headers.get("content-length")
            if content_length and int(content_length) > MAX_PAYLOAD_SIZE:
                logger.warning(f"Rejected oversized payload from {request.client.host}: {content_length} bytes")
                return JSONResponse(
                    status_code=413,
                    content={"success": False, "error": "Request body too large. Maximum size is 2MB."}
                )
        return await call_next(request)

# 3. Timeout Middleware
# Ensures no single request hangs the server for more than 45 seconds
class TimeoutMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
            return await asyncio.wait_for(call_next(request), timeout=45.0)
        except asyncio.TimeoutError:
            logger.error(f"Request timeout for {request.url.path}")
            return JSONResponse(
                status_code=504,
                content={"success": False, "error": "Request timed out. The server took too long to respond."}
            )
