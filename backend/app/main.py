from fastapi import FastAPI, Depends

from app.database.connection import engine
from app.database.base import Base
from app.routers import auth
from app.dependencies.auth import verify_token
from app.routers import ticket
from app.routers.dashboard import router as dashboard_router
from app.routers import user
import app.models.user
import app.models.ticket
Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(auth.router)
app.include_router(ticket.router)
app.include_router(dashboard_router)
app.include_router(user.router)

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