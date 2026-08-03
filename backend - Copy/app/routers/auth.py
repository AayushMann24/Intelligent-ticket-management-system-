from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.schemas.user import UserCreate, UserLogin, UserResponse,Token
from app.services.auth_service import register_user, login_user

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_user(
    user: UserCreate,
    db: Session = Depends(get_db),
):
    try:
        return register_user(db, user)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post(
    "/login",
    response_model=Token,
    status_code=status.HTTP_200_OK,
)
def login(
    user: UserLogin,
    db: Session = Depends(get_db),
):
    try:
        return login_user(db, user)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
        )