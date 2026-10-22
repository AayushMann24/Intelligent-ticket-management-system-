from fastapi import FastAPI, Depends, Request, Response
from fastapi.middleware.cors import CORSMiddleware

from app.database.connection import engine
import app.models.user
import app.models.ticket
import app.models.notification
import app.models.escalation
import app.models.knowledge
import app.models.user_preferences

from app.dependencies.auth import verify_token

from app.routers import auth
from app.routers import ticket
from app.routers import user
from app.routers import sla
from app.routers import notification
from app.routers import analytics
from app.routers import reports
from app.routers import knowledge
from app.routers import assistant
from app.routers import conversations
from app.routers import escalation
from app.routers.dashboard import router as dashboard_router
from app.config import settings
from sqlalchemy import text
from app.database.connection import SessionLocal
from app.utils.exception_handlers import register_exception_handlers
from app.utils.logging_config import setup_logging
from app.services.sla_scheduler import sla_scheduler_lifespan, get_scheduler_status
from app.utils.security_headers import SecurityHeadersMiddleware
from app.utils.request_id import RequestIdMiddleware

# Initialize structured logging
setup_logging()

app = FastAPI(lifespan=sla_scheduler_lifespan)

# Register global exception handlers
register_exception_handlers(app)

# Request ID Middleware - added FIRST to ensure all requests get an ID
app.add_middleware(RequestIdMiddleware)

# Security Headers Middleware - added early to wrap all responses including errors
if settings.security_headers_enabled:
    app.add_middleware(SecurityHeadersMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def add_rate_limit_headers(request: Request, call_next):
    """Add rate limit headers to responses."""
    response = await call_next(request)
    
    # Add rate limit headers if they were set by the rate limit dependency
    if hasattr(request.state, "rate_limit_remaining"):
        response.headers["X-RateLimit-Remaining"] = str(request.state.rate_limit_remaining)
    if hasattr(request.state, "rate_limit_retry_after") and request.state.rate_limit_retry_after > 0:
        response.headers["Retry-After"] = str(request.state.rate_limit_retry_after)
    
    return response


app.include_router(auth.router)
app.include_router(ticket.router)
app.include_router(user.router)
app.include_router(sla.router)
app.include_router(notification.router)
app.include_router(analytics.router)
app.include_router(reports.router)
app.include_router(knowledge.router)
app.include_router(assistant.router)
app.include_router(conversations.router)
app.include_router(escalation.router)
app.include_router(dashboard_router)


@app.get("/")
def home():
    return {
        "message": "ITMS Backend Running Successfully"
    }


@app.get("/profile")
def profile(user=Depends(verify_token)):
    return {
        "message": "Login Successful",
        "user": user
    }


@app.get("/health")
def health_check():
    """Liveness probe - confirms the application process is responsive.
    
    This endpoint should be lightweight and not check external dependencies.
    Used by container orchestrators to determine if the process is alive.
    """
    return {
        "status": "healthy",
        "service": "itms-backend",
    }


@app.get("/ready")
def readiness_check():
    """Readiness probe - verifies required dependencies are available.
    
    Checks database connectivity and returns appropriate HTTP status codes.
    Used by container orchestrators to determine if the service can receive traffic.
    """
    try:
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        
        # Check SLA scheduler status if enabled
        scheduler_status = get_scheduler_status()
        
        return {
            "status": "ready",
            "service": "itms-backend",
            "database": "connected",
            "scheduler": "running" if scheduler_status["running"] else "stopped",
        }
    except Exception as e:
        # Log the error but don't expose details in production
        import logging
        logger = logging.getLogger(__name__)
        logger.error("Readiness check failed", extra={"error": str(e)})
        
        from fastapi import Response
        return Response(
            content='{"status": "not ready", "service": "itms-backend", "database": "disconnected"}',
            status_code=503,
            media_type="application/json",
        )
# Moved imports to top of file