from fastapi import Request
import logging
from typing import Callable
from fastapi.routing import APIRoute
import time

logger = logging.getLogger(__name__)

async def request_logging_middleware(request: Request, call_next: Callable):
    """Middleware to log request details and route matching"""
    start_time = time.time()
    
    # Log request details
    logger.debug(f"Request started: {request.method} {request.url.path}")
    logger.debug(f"Available routes: {[route.path for route in request.app.routes]}")
    
    # Find matching route
    matched_route = None
    for route in request.app.routes:
        if isinstance(route, APIRoute):
            match, child_scope = route.matches({"type": "http", "path": request.url.path})
            if match:
                matched_route = route
                break
    
    if matched_route:
        logger.debug(f"Matched route: {matched_route.path} -> {matched_route.endpoint.__name__}")
    else:
        logger.warning(f"No matching route found for {request.url.path}")
    
    # Process request
    response = await call_next(request)
    
    # Log response
    duration = time.time() - start_time
    logger.debug(
        f"Request completed: {request.method} {request.url.path} "
        f"-> {response.status_code} ({duration:.2f}s)"
    )
    
    return response
