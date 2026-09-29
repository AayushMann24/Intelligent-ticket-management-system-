"""Cookie utilities for secure authentication."""

from typing import Optional
from fastapi import Response, Request
from app.config import settings


def set_auth_cookies(
    response: Response,
    access_token: str,
    refresh_token: str,
) -> None:
    """Set authentication cookies with secure flags."""
    if not settings.cookie_enabled:
        return
    
    # Access token cookie (short-lived)
    response.set_cookie(
        key=settings.access_token_cookie_name,
        value=access_token,
        max_age=settings.access_token_expire_minutes * 60,
        path=settings.cookie_path,
        domain=settings.cookie_domain or None,
        secure=settings.cookie_secure,
        httponly=True,
        samesite=settings.cookie_samesite,
    )
    
    # Refresh token cookie (long-lived)
    response.set_cookie(
        key=settings.refresh_token_cookie_name,
        value=refresh_token,
        max_age=settings.refresh_token_expire_days * 24 * 60 * 60,
        path=settings.cookie_path,
        domain=settings.cookie_domain or None,
        secure=settings.cookie_secure,
        httponly=True,
        samesite=settings.cookie_samesite,
    )


def clear_auth_cookies(response: Response) -> None:
    """Clear authentication cookies."""
    if not settings.cookie_enabled:
        return
    
    response.delete_cookie(
        key=settings.access_token_cookie_name,
        path=settings.cookie_path,
        domain=settings.cookie_domain or None,
        secure=settings.cookie_secure,
        httponly=True,
        samesite=settings.cookie_samesite,
    )
    
    response.delete_cookie(
        key=settings.refresh_token_cookie_name,
        path=settings.cookie_path,
        domain=settings.cookie_domain or None,
        secure=settings.cookie_secure,
        httponly=True,
        samesite=settings.cookie_samesite,
    )


def get_token_from_cookie(request: Request, cookie_name: str) -> Optional[str]:
    """Get token from cookie."""
    if not settings.cookie_enabled:
        return None
    return request.cookies.get(cookie_name)


def get_access_token_from_cookie(request: Request) -> Optional[str]:
    """Get access token from cookie."""
    return get_token_from_cookie(request, settings.access_token_cookie_name)


def get_refresh_token_from_cookie(request: Request) -> Optional[str]:
    """Get refresh token from cookie."""
    return get_token_from_cookie(request, settings.refresh_token_cookie_name)