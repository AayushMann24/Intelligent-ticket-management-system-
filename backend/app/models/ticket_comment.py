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


class HistoryEventType(str, Enum):
    TICKET_CREATED = "TICKET_CREATED"
    STATUS_CHANGED = "STATUS_CHANGED"
    PRIORITY_CHANGED = "PRIORITY_CHANGED"
    ASSIGNED = "ASSIGNED"
    REASSIGNED = "REASSIGNED"
    UNASSIGNED = "UNASSIGNED"
    CATEGORY_CHANGED = "CATEGORY_CHANGED"
    SUBCATEGORY_CHANGED = "SUBCATEGORY_CHANGED"
    TITLE_CHANGED = "TITLE_CHANGED"
    DESCRIPTION_CHANGED = "DESCRIPTION_CHANGED"
    COMMENT_ADDED = "COMMENT_ADDED"
    INTERNAL_NOTE_ADDED = "INTERNAL_NOTE_ADDED"
    ATTACHMENT_ADDED = "ATTACHMENT_ADDED"
    ATTACHMENT_REMOVED = "ATTACHMENT_REMOVED"
    TICKET_REOPENED = "TICKET_REOPENED"
    TICKET_RESOLVED = "TICKET_RESOLVED"
    TICKET_CLOSED = "TICKET_CLOSED"
    TICKET_REOPENED_AFTER_CLOSURE = "TICKET_REOPENED_AFTER_CLOSURE"
    PRIORITY_REASON_CHANGED = "PRIORITY_REASON_CHANGED"
    ASSIGNMENT_REASON_CHANGED = "ASSIGNMENT_REASON_CHANGED"
    TYPE_CHANGED = "TYPE_CHANGED"
    ESCALATED = "ESCALATED"
    SLA_RESPONSE_BREACHED = "SLA_RESPONSE_BREACHED"
    SLA_RESOLUTION_BREACHED = "SLA_RESOLUTION_BREACHED"


class TicketComment(Base):
    __tablename__ = "ticket_comments"

    id = Column(Integer, primary_key=True, index=True)

    ticket_id = Column(
        Integer,
        ForeignKey("tickets.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    author_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    body = Column(Text, nullable=False)

    is_internal = Column(
        Boolean,
        default=False,
        nullable=False,
        index=True,
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

    is_deleted = Column(
        Boolean,
        default=False,
        nullable=False,
        index=True,
    )

    # Relationships
    ticket = relationship("Ticket", back_populates="comments")
    author = relationship("User", back_populates="ticket_comments")

    __table_args__ = (
        Index("ix_ticket_comments_ticket_created", "ticket_id", "created_at"),
        Index("ix_ticket_comments_author_created", "author_id", "created_at"),
        Index("ix_ticket_comments_ticket_internal", "ticket_id", "is_internal"),
    )


class TicketHistory(Base):
    __tablename__ = "ticket_history"

    id = Column(Integer, primary_key=True, index=True)

    ticket_id = Column(
        Integer,
        ForeignKey("tickets.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    actor_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    event_type = Column(
        SQLEnum(HistoryEventType),
        nullable=False,
        index=True,
    )

    old_value = Column(Text, nullable=True)
    new_value = Column(Text, nullable=True)

    metadata_json = Column(Text, nullable=True)

    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True,
    )

    # Relationships
    ticket = relationship("Ticket", back_populates="history")
    actor = relationship("User", back_populates="ticket_history")

    __table_args__ = (
        Index("ix_ticket_history_ticket_created", "ticket_id", "created_at"),
        Index("ix_ticket_history_actor_created", "actor_id", "created_at"),
        Index("ix_ticket_history_ticket_event", "ticket_id", "event_type"),
    )


class TicketAttachment(Base):
    __tablename__ = "ticket_attachments"

    id = Column(Integer, primary_key=True, index=True)

    ticket_id = Column(
        Integer,
        ForeignKey("tickets.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    uploaded_by = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    original_filename = Column(String, nullable=False)
    stored_filename = Column(String, nullable=False)
    content_type = Column(String, nullable=False)
    file_size = Column(Integer, nullable=False)

    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True,
    )

    is_deleted = Column(
        Boolean,
        default=False,
        nullable=False,
        index=True,
    )

    # Relationships
    ticket = relationship("Ticket", back_populates="attachments")
    uploader = relationship("User", back_populates="ticket_attachments")

    __table_args__ = (
        Index("ix_ticket_attachments_ticket_created", "ticket_id", "created_at"),
    )