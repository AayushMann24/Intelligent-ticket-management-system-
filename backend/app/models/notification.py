from datetime import datetime, timezone
from enum import Enum

from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Boolean,
    ForeignKey,
    DateTime,
    Index,
    Enum as SQLEnum,
)
from sqlalchemy.orm import relationship

from app.database.connection import Base


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


class Notification(Base):
    """Notification model for in-app notifications."""
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)

    recipient_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    notification_type = Column(
        SQLEnum(NotificationType),
        nullable=False,
        index=True,
    )

    title = Column(String, nullable=False)

    message = Column(Text, nullable=False)

    ticket_id = Column(
        Integer,
        ForeignKey("tickets.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    is_read = Column(
        Boolean,
        default=False,
        nullable=False,
        index=True,
    )

    read_at = Column(
        DateTime(timezone=True),
        nullable=True,
    )

    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True,
    )

    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    recipient = relationship("User", foreign_keys=[recipient_id])
    ticket = relationship("Ticket", foreign_keys=[ticket_id])

    __table_args__ = (
        Index("ix_notifications_recipient_unread", "recipient_id", "is_read"),
        Index("ix_notifications_recipient_created", "recipient_id", "created_at"),
        Index("ix_notifications_ticket_recipient", "ticket_id", "recipient_id"),
    )