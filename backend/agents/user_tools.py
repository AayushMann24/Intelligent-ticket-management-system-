from langchain_core.tools import tool

from app.database.connection import SessionLocal

from app.services.user_service import (
    get_all_users,
    get_user_by_id,
    update_user_role,
)


# ==========================================
# Get All Users
# ==========================================

@tool
def get_all_users_tool():
    """
    Return all users.
    """

    db = SessionLocal()

    try:

        users = get_all_users(db)

        return [
            {
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "role": user.role,
            }
            for user in users
        ]

    finally:
        db.close()


# ==========================================
# Get User By ID
# ==========================================

@tool
def get_user_by_id_tool(user_id: int):
    """
    Return a user by ID.
    """

    db = SessionLocal()

    try:

        user = get_user_by_id(
            db=db,
            user_id=user_id,
        )

        return {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role": user.role,
        }

    finally:
        db.close()


# ==========================================
# Update User Role
# ==========================================

@tool
def update_user_role_tool(
    user_id: int,
    role: str,
):
    """
    Update a user's role.
    """

    db = SessionLocal()

    try:

        user = update_user_role(
            db=db,
            user_id=user_id,
            role=role,
        )

        return {
            "message": "User role updated successfully",
            "id": user.id,
            "name": user.name,
            "role": user.role,
        }

    finally:
        db.close()