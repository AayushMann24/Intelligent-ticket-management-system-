from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models.user import User
from app.models.ticket import Ticket
# ==========================================
# Get All Users
# ==========================================
def get_all_users(db: Session):

    users = db.query(User).all()

    return users

# ==========================================
# Get User By ID
# ==========================================
def get_user_by_id(
    db: Session,
    user_id: int
):

    user = (
        db.query(User)
        .filter(User.id == user_id)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    return user

# ==========================================
# Update User Role
# ==========================================
def update_user_role(
    db: Session,
    user_id: int,
    role: str
):

    user = (
        db.query(User)
        .filter(User.id == user_id)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    allowed_roles = [
        "Admin",
        "Technician",
        "Employee"
    ]

    if role not in allowed_roles:
        raise HTTPException(
            status_code=400,
            detail="Invalid role"
        )

    user.role = role

    db.commit()

    db.refresh(user)

    return user

# ==========================================
# Get Current Logged-in User
# ==========================================
def get_current_user(
    db: Session,
    user_id: int,
):
    user = (
        db.query(User)
        .filter(User.id == user_id)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )

    return user