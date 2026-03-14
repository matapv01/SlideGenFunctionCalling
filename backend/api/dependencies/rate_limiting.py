# File: backend/api/dependencies/rate_limiting.py

import time
from typing import Dict, Tuple
from fastapi import HTTPException, Depends
from backend.api.schemas.auth_schema import UserResponse
from backend.api.dependencies import get_current_active_user
from backend.api.constants import RateLimitConfig, EndpointNames

# Simple in-memory rate limiting storage
# In production, this should use Redis or similar persistent storage
_rate_limit_storage: Dict[str, Dict[str, Tuple[int, float]]] = {}
_last_cleanup = time.time()

def _get_current_window_start(window_seconds: int) -> int:
    """Get the start of the current time window"""
    return int(time.time() // window_seconds) * window_seconds

def _cleanup_expired_entries():
    """Clean up entries older than 1 hour to prevent memory leak"""
    global _last_cleanup
    current_time = time.time()
    expired_cutoff = current_time - 3600  # 1 hour ago

    # Only cleanup if enough time has passed to avoid excessive overhead
    if current_time - _last_cleanup < RateLimitConfig.CLEANUP_INTERVAL:
        return

    _last_cleanup = current_time

    expired_users = []
    for user_id, user_data in _rate_limit_storage.items():
        expired_endpoints = [
            endpoint for endpoint, (_, window_start) in user_data.items()
            if window_start < expired_cutoff
        ]

        for endpoint in expired_endpoints:
            del user_data[endpoint]

        if not user_data:
            expired_users.append(user_id)

    for user_id in expired_users:
        del _rate_limit_storage[user_id]

def create_rate_limiter(max_requests: int, window_seconds: int, endpoint_name: str):
    """
    Create a rate limiter dependency that allows max_requests per window_seconds per user.

    Args:
        max_requests: Maximum number of requests allowed in the time window
        window_seconds: Time window in seconds
        endpoint_name: Name of endpoint for tracking
    """
    def rate_limiter(current_user: UserResponse = Depends(get_current_active_user)):
        # Periodic cleanup
        _cleanup_expired_entries()

        user_id = str(current_user.id)
        current_window = _get_current_window_start(window_seconds)

        # Get or create user's rate limit data
        if user_id not in _rate_limit_storage:
            _rate_limit_storage[user_id] = {}

        user_data = _rate_limit_storage[user_id]

        # Get or initialize endpoint data
        if endpoint_name not in user_data:
            user_data[endpoint_name] = (0, current_window)

        count, window_start = user_data[endpoint_name]

        # Reset if we're in a new window
        if window_start != current_window:
            count = 0
            window_start = current_window

        # Check if limit exceeded
        if count >= max_requests:
            time_until_reset = (window_start + window_seconds) - time.time()
            raise HTTPException(
                status_code=429,
                detail=f"Rate limit exceeded for {endpoint_name}. Try again in {int(time_until_reset)} seconds."
            )

        # Increment counter
        user_data[endpoint_name] = (count + 1, window_start)

        return current_user

    return rate_limiter

# Pre-configured rate limiters for common use cases
idea_structure_rate_limiter = create_rate_limiter(
    max_requests=RateLimitConfig.IDEA_STRUCTURE_MAX_REQUESTS,
    window_seconds=RateLimitConfig.IDEA_STRUCTURE_WINDOW,
    endpoint_name=EndpointNames.IDEA_STRUCTURE
)

idea_stream_rate_limiter = create_rate_limiter(
    max_requests=RateLimitConfig.IDEA_STREAM_MAX_REQUESTS,
    window_seconds=RateLimitConfig.IDEA_STREAM_WINDOW,
    endpoint_name=EndpointNames.IDEA_STREAM
)