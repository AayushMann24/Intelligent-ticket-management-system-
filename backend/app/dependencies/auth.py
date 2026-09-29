from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError

from app.utils.jwt import decode_token
from app.utils.cookies import get_access_token_from_cookie

security = HTTPBearer(auto_error=False)


def verify_token(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    # Try to get token from Authorization header first (API clients)
    token = None
    if credentials:
        token = credentials.credentials
    else:
        # Fallback to cookie (browser clients)
        token = get_access_token_from_cookie(request)

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )

    try:
        payload = decode_token(token)

        user_id = payload.get("sub")
        role = payload.get("role")
        email = payload.get("email")
        token_type = payload.get("type")

        if user_id is None or token_type == "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
            )

        return {
            "id": int(user_id),
            "role": role,
            "email": email,
        }

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )