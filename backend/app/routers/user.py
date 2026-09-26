from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database.connection import get_db

from app.dependencies.roles import (
    require_admin,
    require_authenticated_user,
)

from app.schemas.user import (
    UserResponse,
    UserRoleUpdate,
)

from app.services.user_service import (
    get_all_users,
    get_user_by_id,
    update_user_role,
    get_current_user,
    get_technicians,
)

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)

# ==================================================
# Current Logged-in User
# ==================================================
@router.get(
    "/me",
    response_model=UserResponse,
)
def current_user(
    db: Session = Depends(get_db),
    user=Depends(require_authenticated_user),
):
    return get_current_user(
        db,
        user["id"],
    )


# ==================================================
# Get Technicians/Admins (for assignment & escalation)
# ==================================================
@router.get(
    "/technicians",
    response_model=dict
)
def get_technicians_endpoint(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db),
    user=Depends(require_authenticated_user),
):
    return get_technicians(
        db,
        page=page,
        page_size=page_size,
    )


# ==================================================
# Get All Users (with pagination)
# ==================================================
@router.get(
    "/",
    response_model=dict
)
def get_users(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    search: str | None = Query(None, description="Search in name/email"),
    role: str | None = Query(None, description="Filter by role"),
    sort_by: str = Query("created_at", description="Sort field"),
    sort_order: str = Query("desc", pattern="^(asc|desc)$", description="Sort order"),
    db: Session = Depends(get_db),
    user=Depends(require_admin)
):
    return get_all_users(
        db,
        page=page,
        page_size=page_size,
        search=search,
        role=role,
        sort_by=sort_by,
        sort_order=sort_order,
    )


# ==================================================
# Get User By ID
# ==================================================
@router.get(
    "/{user_id}",
    response_model=UserResponse
)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    user=Depends(require_admin)
):
    return get_user_by_id(
        db,
        user_id
    )


# ==================================================
# Update User Role
# ==================================================
@router.put(
    "/{user_id}/role",
    response_model=UserResponse
)
def change_user_role(
    user_id: int,
    role_data: UserRoleUpdate,
    db: Session = Depends(get_db),
    user=Depends(require_admin)
):
    return update_user_role(
        db,
        user_id,
        role_data.role
    )