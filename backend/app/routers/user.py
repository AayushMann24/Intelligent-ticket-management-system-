from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.connection import get_db

from app.dependencies.roles import require_admin

from app.schemas.user import (
    UserResponse,
    UserRoleUpdate,
)

from app.services.user_service import (
    get_all_users,
    get_user_by_id,
    update_user_role,
)

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)

@router.get(
    "/",
    response_model=list[UserResponse]
)
def get_users(
    db: Session = Depends(get_db),
    user=Depends(require_admin)
):
    return get_all_users(db)


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