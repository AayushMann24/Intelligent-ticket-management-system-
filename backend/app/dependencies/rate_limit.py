"""FastAPI dependencies for rate limiting."""

from fastapi import Request, Depends, status
from app.utils.rate_limiter import rate_limiter, get_client_identifier
from app.config import settings
from app.utils.exceptions import RateLimitExceededError


async def rate_limit_dependency(
    request: Request,
    max_requests: int = settings.rate_limit_requests,
    window_seconds: int = settings.rate_limit_window_seconds,
) -> None:
    """Generic rate limit dependency.
    
    Args:
        request: FastAPI request object
        max_requests: Maximum requests allowed in window
        window_seconds: Time window in seconds
        
    Raises:
        RateLimitExceededError: If limit exceeded
    """
    if not settings.rate_limit_enabled:
        return
    
    identifier = await get_client_identifier(request)
    endpoint = request.url.path
    
    allowed, remaining, retry_after = await rate_limiter.check_rate_limit(
        identifier=identifier,
        endpoint=endpoint,
        max_requests=max_requests,
        window_seconds=window_seconds,
    )
    
    # Add rate limit headers
    request.state.rate_limit_remaining = remaining
    request.state.rate_limit_retry_after = retry_after
    
    if not allowed:
        raise RateLimitExceededError(
            message="Rate limit exceeded. Please try again later.",
            retry_after=retry_after,
            details={"retry_after": retry_after}
        )


async def auth_rate_limit_dependency(request: Request) -> None:
    """Rate limit dependency for authentication endpoints.
    
    Uses stricter limits configured for auth endpoints.
    """
    await rate_limit_dependency(
        request,
        max_requests=settings.auth_rate_limit_requests,
        window_seconds=settings.auth_rate_limit_window_seconds,
    )