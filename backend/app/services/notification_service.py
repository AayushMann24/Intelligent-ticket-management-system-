from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy.orm import Session, joinedload
from fastapi import HTTPException, status

from app.models.notification import Notification, NotificationType
from app.models.user import User
from app.schemas.notification import (
    NotificationResponse,
    NotificationListResponse,
    UnreadCountResponse,
)
from app.utils.logging_config import get_logger

logger = get_logger(__name__)


# ==========================================
# Notification Creation
# ==========================================

def create_notification(
    db: Session,
    recipient_id: int,
    notification_type: NotificationType,
    title: str,
    message: str,
    ticket_id: Optional[int] = None,
) -> NotificationResponse:
    """
    Create a new notification for a user.
    
    Args:
        db: Database session
        recipient_id: ID of the user who should receive the notification
        notification_type: Type of notification
        title: Short title for the notification
        message: Detailed message
        ticket_id: Optional ticket ID related to the notification
        
    Returns:
        The created notification
        
    Raises:
        HTTPException: If recipient does not exist
    """
    # Validate recipient exists
    recipient = db.query(User).filter(User.id == recipient_id, User.is_deleted == False).first()
    if not recipient:
        logger.warning(f"Attempted to create notification for non-existent user {recipient_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recipient user not found"
        )

    notification = Notification(
        recipient_id=recipient_id,
        notification_type=notification_type,
        title=title,
        message=message,
        ticket_id=ticket_id,
    )

    db.add(notification)
    db.commit()
    db.refresh(notification)

    logger.info(f"Created notification {notification.id} for user {recipient_id} (type: {notification_type.value})")

    return NotificationResponse.model_validate(notification)


# ==========================================
# Notification Retrieval
# ==========================================

def get_notifications_for_user(
    db: Session,
    user_id: int,
    page: int = 1,
    page_size: int = 20,
    unread_only: bool = False,
    notification_type: Optional[NotificationType] = None,
    sort_by: str = "created_at",
    sort_order: str = "desc",
) -> NotificationListResponse:
    """
    Get notifications for a user with pagination and filtering.
    
    Args:
        db: Database session
        user_id: ID of the user
        page: Page number (1-indexed)
        page_size: Items per page
        unread_only: If True, only return unread notifications
        notification_type: Optional filter by notification type
        sort_by: Field to sort by
        sort_order: Sort order (asc/desc)
        
    Returns:
        Paginated list of notifications
    """
    query = db.query(Notification).filter(Notification.recipient_id == user_id)

    if unread_only:
        query = query.filter(Notification.is_read == False)

    if notification_type:
        query = query.filter(Notification.notification_type == notification_type)

    total = query.count()

    # Apply sorting
    sort_column = getattr(Notification, sort_by, Notification.created_at)
    if sort_order == "desc":
        query = query.order_by(sort_column.desc())
    else:
        query = query.order_by(sort_column.asc())

    # Apply pagination
    offset = (page - 1) * page_size
    notifications = query.offset(offset).limit(page_size).all()

    total_pages = (total + page_size - 1) // page_size

    return NotificationListResponse(
        items=[NotificationResponse.model_validate(n) for n in notifications],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


def get_unread_count(db: Session, user_id: int) -> UnreadCountResponse:
    """
    Get the count of unread notifications for a user.
    
    Args:
        db: Database session
        user_id: ID of the user
        
    Returns:
        Unread count response
    """
    count = db.query(Notification).filter(
        Notification.recipient_id == user_id,
        Notification.is_read == False,
    ).count()

    return UnreadCountResponse(unread_count=count)


# ==========================================
# Notification State Updates
# ==========================================

def mark_notification_as_read(
    db: Session,
    notification_id: int,
    user_id: int,
) -> Optional[NotificationResponse]:
    """
    Mark a notification as read.
    
    Args:
        db: Database session
        notification_id: ID of the notification
        user_id: ID of the user (for authorization)
        
    Returns:
        The updated notification, or None if not found
        
    Raises:
        HTTPException: If notification belongs to another user
    """
    notification = db.query(Notification).filter(Notification.id == notification_id).first()
    
    if not notification:
        return None

    # Authorization: users can only mark their own notifications as read
    if notification.recipient_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to modify this notification"
        )

    if not notification.is_read:
        notification.is_read = True
        notification.read_at = datetime.now(timezone.utc)
        notification.updated_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(notification)
        logger.info(f"User {user_id} marked notification {notification_id} as read")

    return NotificationResponse.model_validate(notification)


def mark_all_notifications_as_read(
    db: Session,
    user_id: int,
) -> int:
    """
    Mark all unread notifications for a user as read.
    
    Args:
        db: Database session
        user_id: ID of the user
        
    Returns:
        Number of notifications marked as read
    """
    now = datetime.now(timezone.utc)
    
    updated = db.query(Notification).filter(
        Notification.recipient_id == user_id,
        Notification.is_read == False,
    ).update({
        Notification.is_read: True,
        Notification.read_at: now,
        Notification.updated_at: now,
    })
    
    db.commit()
    
    if updated > 0:
        logger.info(f"User {user_id} marked {updated} notifications as read")
    
    return updated