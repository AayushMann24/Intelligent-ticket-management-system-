from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.user import UserCreate, UserLogin
from app.utils.security import hash_password, verify_password
from app.utils.jwt import create_access_token


# ==========================================
# Register User
# ==========================================
def register_user(db: Session, user_data: UserCreate):

    existing_user = (
        db.query(User)
        .filter(User.email == user_data.email)
        .first()
    )

    if existing_user:
        raise ValueError("Email already registered")

    hashed_password = hash_password(user_data.password)

    new_user = User(
        name=user_data.name,
        email=user_data.email,
        password=hashed_password,
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


# ==========================================
# Login User
# ==========================================
def login_user(db: Session, user_data: UserLogin):

    user = (
        db.query(User)
        .filter(User.email == user_data.email)
        .first()
    )

    if not user:
        raise ValueError("Invalid email or password")

    if not verify_password(
        user_data.password,
        user.password,
    ):
        raise ValueError("Invalid email or password")

    access_token = create_access_token(
        data={
            "sub": str(user.id),
            "email": user.email,
            "role": user.role,
        }
    )

    return {
    "access_token": access_token,
    "token_type": "bearer",

    "id": user.id,
    "name": user.name,
    "email": user.email,
    "role": user.role,
}