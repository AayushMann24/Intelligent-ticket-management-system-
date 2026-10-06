from fastapi import FastAPI, Depends, Request, Response
from fastapi.middleware.cors import CORSMiddleware

from app.database.connection import engine
import app.models.user
import app.models.ticket
import app.models.notification
import app.models.escalation

from app.dependencies.auth import verify_token

from app.routers import auth
from app.routers import ticket
from app.routers import user
from app.routers import sla
from app.routers import notification
from app.routers import analytics
from app.routers import reports
#from app.routers import ai
from app.routers.dashboard import router as dashboard_router
# AI routers - commented out for testing without langchain dependencies
# from app.routers import assistant
# from app.routers import ai
from app.config import settings
from sqlalchemy import text
from app.database.connection import SessionLocal
from app.utils.exception_handlers import register_exception_handlers
from app.utils.logging_config import setup_logging
from app.services.sla_scheduler import sla_scheduler_lifespan
from app.utils.security_headers import SecurityHeadersMiddleware

# Initialize structured logging
setup_logging()

app = FastAPI(lifespan=sla_scheduler_lifespan)

# Register global exception handlers
register_exception_handlers(app)

# Security Headers Middleware - added FIRST to wrap all responses including errors
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
#app.include_router(ai.router)
app.include_router(dashboard_router)
# app.include_router(assistant.router)


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
    return {"status": "healthy"}


@app.get("/ready")
def readiness_check():
    try:
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        return {"status": "ready"}
    except Exception as e:
        return {"status": "not ready", "detail": str(e)}
# Moved imports to top of file
