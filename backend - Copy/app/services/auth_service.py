from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.user import UserCreate, UserLogin
from app.utils.security import hash_password, verify_password
from app.utils.jwt import create_access_token

def register_user(db: Session, user_data: UserCreate):
    # Check if email already exists
    existing_user = (
        db.query(User)
        .filter(User.email == user_data.email)
        .first()
    )

    if existing_user:
        raise ValueError("Email already registered")

    # Hash the password
    hashed_password = hash_password(user_data.password)

    # Create a new User object
    new_user = User(
        name=user_data.name,
        email=user_data.email,
        password=hashed_password,
    )

    # Add the user to the session
    db.add(new_user)

    # Save changes to the database
    db.commit()

    # Refresh the object to get generated values (like id)
    db.refresh(new_user)

    # Return the created user
    return new_user


def login_user(db: Session, user_data: UserLogin):
    # Find user by email
    user = (
        db.query(User)
        .filter(User.email == user_data.email)
        .first()
    )

    # Check if user exists
    if not user:
        raise ValueError("Invalid email or password")

    # Verify password
    if not verify_password(user_data.password, user.password):
        raise ValueError("Invalid email or password")

    # Return the authenticated user
    access_token = create_access_token(
    data={
        "sub": str(user.id),
        "email": user.email,
        "role": user.role
    }
)

    return {
    "access_token": access_token,
    "token_type": "bearer"
}
