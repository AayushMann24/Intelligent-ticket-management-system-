from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional

from app.database.connection import get_db
from app.dependencies.roles import require_authenticated_user
from app.dependencies.csrf import csrf_protect
from app.services.notification_service import (
    get_notifications_for_user,
    get_unread_count,
    mark_notification_as_read,
    mark_all_notifications_as_read,
)
from app.schemas.notification import (
    NotificationListResponse,
    UnreadCountResponse,
    NotificationResponse,
    NotificationType,
)

router = APIRouter(
    prefix="/notifications",
    tags=["Notifications"],
)


@router.get(
    "/",
    response_model=NotificationListResponse,
)
def list_notifications(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    unread_only: bool = Query(False, description="Show only unread notifications"),
    notification_type: Optional[NotificationType] = Query(None, description="Filter by notification type"),
    sort_by: str = Query("created_at", pattern="^(created_at|notification_type|is_read)$", description="Sort field"),
    sort_order: str = Query("desc", pattern="^(asc|desc)$", description="Sort order"),
    db: Session = Depends(get_db),
    user=Depends(require_authenticated_user),
):
    """
    Get paginated list of notifications for the authenticated user.
    
    Supports filtering by read status and notification type.
    """
    return get_notifications_for_user(
        db=db,
        user_id=user["id"],
        page=page,
        page_size=page_size,
        unread_only=unread_only,
        notification_type=notification_type,
        sort_by=sort_by,
        sort_order=sort_order,
    )


@router.get(
    "/unread-count",
    response_model=UnreadCountResponse,
)
def get_unread_notification_count(
    db: Session = Depends(get_db),
    user=Depends(require_authenticated_user),
):
    """Get the count of unread notifications for the authenticated user."""
    return get_unread_count(db=db, user_id=user["id"])


@router.patch(
    "/{notification_id}/read",
    response_model=NotificationResponse,
    dependencies=[Depends(csrf_protect)],
)
def mark_as_read(
    notification_id: int,
    db: Session = Depends(get_db),
    user=Depends(require_authenticated_user),
):
    """
    Mark a notification as read.
    
    Users can only mark their own notifications as read.
    """
    notification = mark_notification_as_read(
        db=db,
        notification_id=notification_id,
        user_id=user["id"],
    )
    
    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )
    
    return notification


@router.post(
    "/mark-all-read",
    response_model=dict,
    dependencies=[Depends(csrf_protect)],
)
def mark_all_as_read(
    db: Session = Depends(get_db),
    user=Depends(require_authenticated_user),
):
    """Mark all unread notifications for the authenticated user as read."""
    count = mark_all_notifications_as_read(db=db, user_id=user["id"])
    return {"message": f"Marked {count} notifications as read", "marked_count": count}