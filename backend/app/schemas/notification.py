from datetime import datetime
from enum import Enum
from pydantic import BaseModel, ConfigDict
from typing import Optional, List


class NotificationType(str, Enum):
    """Notification types for the ITMS system."""
    TICKET_ASSIGNED = "TICKET_ASSIGNED"
    TICKET_REASSIGNED = "TICKET_REASSIGNED"
    SLA_RESPONSE_WARNING = "SLA_RESPONSE_WARNING"
    SLA_RESPONSE_BREACHED = "SLA_RESPONSE_BREACHED"
    SLA_RESOLUTION_WARNING = "SLA_RESOLUTION_WARNING"
    SLA_RESOLUTION_BREACHED = "SLA_RESOLUTION_BREACHED"
    TICKET_ESCALATED = "TICKET_ESCALATED"
    SYSTEM = "SYSTEM"


class NotificationResponse(BaseModel):
    """Response model for a single notification."""
    id: int
    notification_type: str
    title: str
    message: str
    ticket_id: Optional[int] = None
    is_read: bool
    read_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class NotificationListResponse(BaseModel):
    """Paginated response for notification list."""
    items: List[NotificationResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class UnreadCountResponse(BaseModel):
    """Response for unread notification count."""
    unread_count: int


class MarkReadRequest(BaseModel):
    """Request to mark notification as read."""
    pass  # No body needed, just the notification_id in path