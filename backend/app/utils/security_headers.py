"""Security Headers middleware for FastAPI.

Implements HTTP security headers including Content Security Policy (CSP),
HSTS, X-Content-Type-Options, X-Frame-Options, Referrer-Policy,
and Permissions-Policy.
"""

from typing import Optional
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from app.config import settings


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Middleware to add security headers to all responses."""

    def __init__(self, app, csp_policy: Optional[str] = None):
        super().__init__(app)
        self._csp_policy = csp_policy or self._build_csp_policy()

    def _build_csp_policy(self) -> str:
        """Build the Content Security Policy based on application requirements.
        
        The policy is designed for:
        - React frontend served from same origin (or static files)
        - FastAPI backend API
        - Swagger UI at /docs and /redoc (requires inline scripts/styles)
        - No external CDNs, Google Fonts, or third-party scripts
        - HttpOnly authentication cookies
        - CSRF protection via header
        """
        # Base directives for the main application
        directives = [
            "default-src 'self'",
            # Scripts: React bundles, no inline scripts, no eval
            "script-src 'self'",
            # Styles: CSS bundles, Tailwind CSS-in-JS (in bundles), no external fonts
            "style-src 'self'",
            # Images: self-hosted, data URIs for inline images
            "img-src 'self' data:",
            # Fonts: system fonts only (Inter via system-ui fallback), no external font CDNs
            "font-src 'self'",
            # Connect: API calls to backend (same origin in production, localhost in dev)
            "connect-src 'self'",
            # No plugins/objects
            "object-src 'none'",
            # Base URI restricted to self
            "base-uri 'self'",
            # Prevent framing
            "frame-ancestors 'none'",
            # Forms only to self
            "form-action 'self'",
            # Disallow upgrade-insecure-requests in dev (HTTP), enable in prod via config if needed
        ]
        
        # For development, Swagger UI (/docs, /redoc) needs inline scripts and styles
        # We handle this by using a more permissive CSP for those paths in the middleware
        # The base policy above is restrictive for the main app
        
        return "; ".join(directives)

    def _get_csp_for_path(self, path: str) -> str:
        """Get CSP policy for a specific path.
        
        Swagger UI at /docs and /redoc requires 'unsafe-inline' for scripts and styles
        because it uses inline scripts/styles from the bundled Swagger UI.
        """
        if path.startswith("/docs") or path.startswith("/redoc") or path.startswith("/openapi.json"):
            # Swagger UI needs inline scripts and styles
            # We allow 'unsafe-inline' only for these documentation endpoints
            return (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline'; "
                "style-src 'self' 'unsafe-inline'; "
                "img-src 'self' data:; "
                "font-src 'self'; "
                "connect-src 'self'; "
                "object-src 'none'; "
                "base-uri 'self'; "
                "frame-ancestors 'none'; "
                "form-action 'self'"
            )
        return self._csp_policy

    def _should_add_hsts(self, request: Request) -> bool:
        """Determine if HSTS should be added.
        
        HSTS should only be sent over HTTPS connections.
        In development (HTTP), we must NOT send HSTS.
        """
        if not settings.hsts_enabled:
            return False
        
        # Only add HSTS for HTTPS
        # Check both the request URL scheme and X-Forwarded-Proto header
        scheme = request.url.scheme
        forwarded_proto = request.headers.get("x-forwarded-proto", "")
        
        is_https = scheme == "https" or forwarded_proto == "https"
        return is_https

    def _build_hsts_header(self) -> str:
        """Build the HSTS header value."""
        parts = [f"max-age={settings.hsts_max_age}"]
        if settings.hsts_include_subdomains:
            parts.append("includeSubDomains")
        if settings.hsts_preload:
            parts.append("preload")
        return "; ".join(parts)

    async def dispatch(self, request: Request, call_next):
        response: Response = await call_next(request)
        
        if not settings.security_headers_enabled:
            return response

        # Content-Security-Policy
        if settings.csp_enabled:
            csp = self._get_csp_for_path(request.url.path)
            response.headers["Content-Security-Policy"] = csp

        # X-Content-Type-Options: Prevent MIME type sniffing
        response.headers["X-Content-Type-Options"] = "nosniff"

        # X-Frame-Options: Prevent clickjacking
        response.headers["X-Frame-Options"] = "DENY"

        # Referrer-Policy: Control referrer information
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        # Permissions-Policy: Control browser features
        # Disable unnecessary APIs for security
        permissions_policy = (
            "accelerometer=(), "
            "camera=(), "
            "geolocation=(), "
            "gyroscope=(), "
            "magnetometer=(), "
            "microphone=(), "
            "payment=(), "
            "usb=(), "
            "interest-cohort=()"
        )
        response.headers["Permissions-Policy"] = permissions_policy

        # Strict-Transport-Security (HSTS) - only for HTTPS
        if self._should_add_hsts(request):
            response.headers["Strict-Transport-Security"] = self._build_hsts_header()

        # Remove server header if present (information leakage)
        # Note: Starlette/Uvicorn doesn't add this by default, but proxies might
        if "server" in response.headers:
            del response.headers["server"]

        return response


def get_csp_policy_for_testing() -> str:
    """Return the base CSP policy for testing purposes."""
    middleware = SecurityHeadersMiddleware(None)
    return middleware._build_csp_policy()


def get_swagger_csp_policy_for_testing() -> str:
    """Return the Swagger UI CSP policy for testing purposes."""
    middleware = SecurityHeadersMiddleware(None)
    return middleware._get_csp_for_path("/docs")