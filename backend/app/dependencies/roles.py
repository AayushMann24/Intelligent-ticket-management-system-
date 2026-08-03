from fastapi import Depends, HTTPException, status

from app.dependencies.auth import verify_token


def require_admin(
    user=Depends(verify_token)
):
    """
    Allows access only to Admin users.
    """

    if user["role"] != "Admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )

    return user


def require_technician(
    user=Depends(verify_token)
):
    """
    Allows access only to Technician users.
    """

    if user["role"] != "Technician":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Technician access required"
        )

    return user


def require_employee(
    user=Depends(verify_token)
):
    """
    Allows access only to Employee users.
    """

    if user["role"] != "Employee":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Employee access required"
        )

    return user


def require_admin_or_technician(
    user=Depends(verify_token)
):
    """
    Allows access to Admins and Technicians.
    """

    if user["role"] not in ["Admin", "Technician"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin or Technician access required"
        )

    return user


def require_authenticated_user(
    user=Depends(verify_token)
):
    """
    Allows any authenticated user.
    Useful for APIs that only require login.
    """

    return user