"""CSRF protection dependency for state-changing requests."""

from fastapi import Request, Depends, HTTPException, status
from app.utils.csrf import validate_csrf_token
from app.config import settings


async def csrf_protect(request: Request) -> None:
    """Validate CSRF token for state-changing requests using cookie auth.
    
    This dependency should be applied to all state-changing endpoints
    (POST, PUT, PATCH, DELETE) that use cookie-based authentication.
    """
    if not settings.csrf_enabled:
        return
    
    # Skip for safe methods
    if request.method in ("GET", "HEAD", "OPTIONS"):
        return
    
    # Skip for auth endpoints that establish cookies
    path = request.url.path
    if path in ("/auth/login", "/auth/register", "/auth/refresh", "/auth/logout"):
        return
    
    # Check if using cookie auth
    from app.config import settings as s
    has_auth_cookie = (
        s.access_token_cookie_name in request.cookies or
        s.refresh_token_cookie_name in request.cookies
    )
    
    # Check for Bearer token (API clients don't need CSRF)
    has_bearer_token = "authorization" in request.headers
    
    # Only enforce CSRF for cookie-based auth
    if has_auth_cookie and not has_bearer_token:
        if not validate_csrf_token(request):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid or missing CSRF token",
            )