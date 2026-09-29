from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserLogin, UserResponse, Token, RefreshTokenRequest
from app.services.auth_service import register_user, login_user, refresh_access_token, logout_user
from app.dependencies.auth import verify_token
from app.dependencies.rate_limit import auth_rate_limit_dependency
from app.utils.cookies import set_auth_cookies, clear_auth_cookies, get_refresh_token_from_cookie
from app.utils.csrf import get_csrf_token_for_response, set_csrf_cookie

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(auth_rate_limit_dependency)],
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
    dependencies=[Depends(auth_rate_limit_dependency)],
)
def login(
    user: UserLogin,
    db: Session = Depends(get_db),
    response: Response = None,
):
    try:
        token_data = login_user(db, user)
        
        # Set HttpOnly cookies for browser clients
        if response:
            set_auth_cookies(response, token_data["access_token"], token_data["refresh_token"])
            # Set CSRF cookie for subsequent requests
            get_csrf_token_for_response(response)
        
        return token_data
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
        )


@router.post(
    "/refresh",
    response_model=Token,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(auth_rate_limit_dependency)],
)
def refresh_token(
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
    refresh_request: RefreshTokenRequest = None,
):
    # Get refresh token from cookie (browser) or request body (API client)
    refresh_token = None
    if refresh_request and refresh_request.refresh_token:
        refresh_token = refresh_request.refresh_token
    else:
        refresh_token = get_refresh_token_from_cookie(request)
    
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token not provided",
        )
    
    try:
        token_data = refresh_access_token(db, refresh_token)
        
        # Set new HttpOnly cookies (rotation)
        set_auth_cookies(response, token_data["access_token"], token_data["refresh_token"])
        # Refresh CSRF token
        get_csrf_token_for_response(response)
        
        return token_data
    except ValueError as e:
        # Clear cookies on refresh failure
        clear_auth_cookies(response)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
        )


@router.post(
    "/logout",
    status_code=status.HTTP_200_OK,
)
def logout(
    response: Response,
    user=Depends(verify_token),
    db: Session = Depends(get_db),
):
    try:
        result = logout_user(db, user["id"])
        # Clear auth cookies
        clear_auth_cookies(response)
        return result
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Logout failed",
        )