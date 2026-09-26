from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models.user import User
from app.models.ticket import Ticket


def _base_user_query(db: Session):
    """Base query that excludes soft-deleted users."""
    return db.query(User).filter(User.is_deleted == False)


def _user_to_dict(user: User) -> dict:
    """Convert User model to dict for serialization."""
    return {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "role": user.role,
        "specialization": user.specialization,
        "created_at": user.created_at,
        "updated_at": user.updated_at,
    }


# ==========================================
# Get Technicians/Admins (for assignment & escalation)
# ==========================================
def get_technicians(
    db: Session,
    page: int = 1,
    page_size: int = 100,
):
    """Get all users with Admin or Technician role for assignment/escalation."""
    query = _base_user_query(db).filter(User.role.in_(["Admin", "Technician"]))

    total = query.count()

    query = query.order_by(User.name.asc())

    offset = (page - 1) * page_size
    users = query.offset(offset).limit(page_size).all()

    total_pages = (total + page_size - 1) // page_size

    return {
        "items": [_user_to_dict(u) for u in users],
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
    }


# ==========================================
# Get All Users (with pagination)
# ==========================================
def get_all_users(
    db: Session,
    page: int = 1,
    page_size: int = 20,
    search: str | None = None,
    role: str | None = None,
    sort_by: str = "created_at",
    sort_order: str = "desc",
):
    query = _base_user_query(db)

    if search:
        query = query.filter(
            User.name.ilike(f"%{search}%") | User.email.ilike(f"%{search}%")
        )
    if role:
        query = query.filter(User.role == role)

    total = query.count()

    sort_column = getattr(User, sort_by, User.created_at)
    if sort_order == "desc":
        query = query.order_by(sort_column.desc())
    else:
        query = query.order_by(sort_column.asc())

    offset = (page - 1) * page_size
    users = query.offset(offset).limit(page_size).all()

    total_pages = (total + page_size - 1) // page_size

    return {
        "items": [_user_to_dict(u) for u in users],
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
    }


# ==========================================
# Get User By ID
# ==========================================
def get_user_by_id(
    db: Session,
    user_id: int
):

    user = (
        _base_user_query(db)
        .filter(User.id == user_id)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    return _user_to_dict(user)


# ==========================================
# Update User Role
# ==========================================
def update_user_role(
    db: Session,
    user_id: int,
    role: str
):

    user = (
        _base_user_query(db)
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

    return _user_to_dict(user)


# ==========================================
# Get Current Logged-in User
# ==========================================
def get_current_user(
    db: Session,
    user_id: int,
):
    user = (
        _base_user_query(db)
        .filter(User.id == user_id)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )

    return _user_to_dict(user)