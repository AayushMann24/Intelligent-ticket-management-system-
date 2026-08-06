from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from dotenv import load_dotenv
import os

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")

security = HTTPBearer()


def verify_token(
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    token = credentials.credentials

    print("\n======================================")
    print("TOKEN RECEIVED")
    print(token)
    print("======================================")

    try:

        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM],
        )

        print("\nPAYLOAD DECODED SUCCESSFULLY")
        print(payload)
        print()

        user_id = payload.get("sub")
        role = payload.get("role")
        email = payload.get("email")

        if user_id is None:
            raise HTTPException(
                status_code=401,
                detail="Invalid token",
            )

        return {
            "id": int(user_id),
            "role": role,
            "email": email,
        }

    except JWTError as e:

        print("\nJWT ERROR")
        print(type(e).__name__)
        print(str(e))
        print()

        raise HTTPException(
            status_code=401,
            detail=str(e),
        )