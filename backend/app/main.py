from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware

from app.database.connection import engine
from app.database.base import Base
from app.routers import assistant
import app.models.user
import app.models.ticket

from app.dependencies.auth import verify_token

from app.routers import auth
from app.routers import ticket
from app.routers import user
#from app.routers import ai
from app.routers.dashboard import router as dashboard_router

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(ticket.router)
app.include_router(user.router)
#app.include_router(ai.router)
app.include_router(dashboard_router)
app.include_router(assistant.router)

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
from dotenv import load_dotenv
import os

load_dotenv()

print("SECRET_KEY:", os.getenv("SECRET_KEY"))
print("ALGORITHM:", os.getenv("ALGORITHM"))