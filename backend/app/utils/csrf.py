"""CSRF protection utilities for cookie-based authentication."""

import secrets
from typing import Optional
from fastapi import Request, Response
from app.config import settings


def generate_csrf_token() -> str:
    """Generate a secure CSRF token."""
    return secrets.token_urlsafe(32)


def set_csrf_cookie(response: Response, token: str) -> None:
    """Set CSRF token as a non-HttpOnly cookie so frontend can read it."""
    if not settings.csrf_enabled:
        return
    
    response.set_cookie(
        key=settings.csrf_cookie_name,
        value=token,
        max_age=60 * 60 * 24 * 7,  # 7 days
        path=settings.cookie_path,
        domain=settings.cookie_domain or None,
        secure=settings.cookie_secure,
        httponly=False,  # Must be readable by JavaScript
        samesite=settings.cookie_samesite,
    )


def get_csrf_token_from_request(request: Request) -> Optional[str]:
    """Extract CSRF token from request header only.
    
    The cookie is only for the frontend to read and send in the header.
    For validation, we require the header to be present.
    """
    if not settings.csrf_enabled:
        return None
    
    # Check header only (required for validation)
    token = request.headers.get(settings.csrf_header_name)
    
    if token:
        return token
    
    # No fallback to cookie - header is required for validation
    return None


def validate_csrf_token(request: Request) -> bool:
    """Validate CSRF token from request."""
    if not settings.csrf_enabled:
        return True
    
    # GET, HEAD, OPTIONS don't need CSRF protection
    if request.method in ("GET", "HEAD", "OPTIONS"):
        return True
    
    # For auth endpoints that establish cookies, we allow without CSRF
    # (login, register, refresh, logout are handled specially)
    path = request.url.path
    if path in ("/auth/login", "/auth/register", "/auth/refresh", "/auth/logout"):
        return True
    
    # Check if request has a valid session (auth cookie)
    has_auth_cookie = (
        settings.access_token_cookie_name in request.cookies or
        settings.refresh_token_cookie_name in request.cookies
    )
    
    # Also check for Bearer token (API clients)
    has_bearer_token = "authorization" in request.headers
    
    # Only require CSRF if using cookie auth
    if not has_auth_cookie and not has_bearer_token:
        return True  # No auth, let auth dependency handle it
    
    # For Bearer token API clients, CSRF not needed
    if has_bearer_token and not has_auth_cookie:
        return True
    
    # Cookie-based auth requires CSRF
    token = get_csrf_token_from_request(request)
    if not token:
        return False
    
    # In a stateless approach, we'd compare with a stored token
    # For double-submit cookie pattern, the token in header must match cookie
    cookie_token = request.cookies.get(settings.csrf_cookie_name)
    if not cookie_token:
        return False
    
    return secrets.compare_digest(token, cookie_token)


def get_csrf_token_for_response(response: Response) -> str:
    """Get or generate CSRF token for a response."""
    # Check if already set in response cookies
    for cookie in response.headers.getlist("set-cookie") or []:
        if cookie.startswith(f"{settings.csrf_cookie_name}="):
            # Extract token from cookie
            parts = cookie.split(";")[0].split("=")
            if len(parts) == 2:
                return parts[1]
    
    # Generate new token
    token = generate_csrf_token()
    set_csrf_cookie(response, token)
    return token