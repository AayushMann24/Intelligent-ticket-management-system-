from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware

from app.database.connection import engine
from app.database.base import Base
import app.models.user
import app.models.ticket

from app.dependencies.auth import verify_token

from app.routers import auth
from app.routers import ticket
from app.routers import user
from app.routers import sla
#from app.routers import ai
from app.routers.dashboard import router as dashboard_router
# AI routers - commented out for testing without langchain dependencies
# from app.routers import assistant
# from app.routers import ai
from app.config import settings
from app.utils.exception_handlers import register_exception_handlers
from app.utils.logging_config import setup_logging
from app.services.sla_scheduler import sla_scheduler_lifespan

# Initialize structured logging
setup_logging()

Base.metadata.create_all(bind=engine)

app = FastAPI(lifespan=sla_scheduler_lifespan)

# Register global exception handlers
register_exception_handlers(app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(ticket.router)
app.include_router(user.router)
app.include_router(sla.router)
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
    # Add database connectivity check here if needed
    return {"status": "ready"}