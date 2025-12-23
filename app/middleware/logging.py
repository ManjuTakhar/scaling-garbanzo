import logging
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger("uvicorn.error")

class LogRequestMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        # Log request details
        logger.info(f"Request: {request.method} {request.url}")
        logger.info(f"Headers: {request.headers}")
        
        # Read the body if it's a POST request
        if request.method in ["POST", "PUT", "PATCH"]:
            body = await request.body()
            logger.info(f"Body: {body.decode('utf-8')}")
        
        # Call the next middleware or endpoint
        response = await call_next(request)
        
        return response 