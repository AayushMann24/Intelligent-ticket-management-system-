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
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from app.database.connection import Base


class EscalationEventType(str, Enum):
    """SLA event types that can trigger escalation."""
    RESPONSE_BREACH = "RESPONSE_BREACH"
    RESOLUTION_BREACH = "RESOLUTION_BREACH"


class EscalationRule(Base):
    """
    Escalation rule defining when and how to escalate an SLA breach.
    Rules are evaluated in order of specificity (priority + event_type + ticket_type + category).
    """
    __tablename__ = "escalation_rules"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String, nullable=False, unique=True, index=True)

    description = Column(Text, nullable=True)

    # Rule matching criteria
    # SLA event type that triggers this rule
    event_type = Column(
        SQLEnum(EscalationEventType),
        nullable=False,
        index=True,
    )

    # Priority that this rule applies to (e.g., "Critical", "High", "Medium", "Low")
    priority = Column(
        String,
        nullable=False,
        index=True,
    )

    # Optional ticket type filter
    ticket_type = Column(
        String,
        nullable=True,
        index=True,
    )

    # Optional category filter
    category = Column(
        String,
        nullable=True,
        index=True,
    )

    # Escalation target - role to escalate to
    # Options: "Admin", "Technician", or specific user ID if needed
    target_role = Column(
        String,
        nullable=False,
        default="Admin",
    )

    # Whether to create in-app notification
    notify_enabled = Column(
        Boolean,
        default=True,
        nullable=False,
    )

    # Whether to send email
    email_enabled = Column(
        Boolean,
        default=True,
        nullable=False,
    )

    # Whether this rule is active
    is_active = Column(
        Boolean,
        default=True,
        nullable=False,
        index=True,
    )

    # Rule precedence - higher number = higher precedence (more specific)
    # This is computed automatically based on specificity
    precedence = Column(
        Integer,
        default=0,
        nullable=False,
    )

    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    __table_args__ = (
        Index("ix_escalation_rules_active_priority", "is_active", "priority"),
        Index("ix_escalation_rules_active_event", "is_active", "event_type"),
    )


class EscalationRecord(Base):
    """
    Persistent record of an escalation to ensure idempotency.
    One record per (ticket, event_type, rule) combination.
    """
    __tablename__ = "escalation_records"

    id = Column(Integer, primary_key=True, index=True)

    ticket_id = Column(
        Integer,
        ForeignKey("tickets.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # The SLA event type that triggered this escalation
    event_type = Column(
        SQLEnum(EscalationEventType),
        nullable=False,
        index=True,
    )

    # The rule that was matched
    rule_id = Column(
        Integer,
        ForeignKey("escalation_rules.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    # The user who was the escalation recipient
    recipient_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    # Whether notification was created
    notification_created = Column(
        Boolean,
        default=False,
        nullable=False,
    )

    # Notification ID if created
    notification_id = Column(
        Integer,
        ForeignKey("notifications.id", ondelete="SET NULL"),
        nullable=True,
    )

    # Whether email was sent (or attempted)
    email_sent = Column(
        Boolean,
        default=False,
        nullable=False,
    )

    # Email error if any
    email_error = Column(
        Text,
        nullable=True,
    )

    # Whether history event was recorded
    history_recorded = Column(
        Boolean,
        default=False,
        nullable=False,
    )

    # Additional metadata (JSON string)
    metadata_json = Column(
        Text,
        nullable=True,
    )

    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    ticket = relationship("Ticket", foreign_keys=[ticket_id])
    rule = relationship("EscalationRule", foreign_keys=[rule_id])
    recipient = relationship("User", foreign_keys=[recipient_id])
    notification = relationship("Notification", foreign_keys=[notification_id])

    __table_args__ = (
        # Unique constraint to prevent duplicate escalations for the same condition
        UniqueConstraint("ticket_id", "event_type", "rule_id", name="uq_escalation_ticket_event_rule"),
        Index("ix_escalation_records_ticket_event", "ticket_id", "event_type"),
    )