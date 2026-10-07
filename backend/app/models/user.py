from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime, timezone

from app.database.connection import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String, nullable=False)

    email = Column(String, unique=True, nullable=False, index=True)

    password = Column(String, nullable=False)

    role = Column(
        String,
        nullable=False,
        default="Employee"
    )

    # AI Assignment Field
    specialization = Column(
        String,
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

    is_deleted = Column(
        Boolean,
        default=False,
        nullable=False,
        index=True,
    )

    # Tickets created by this user
    created_tickets = relationship(
        "Ticket",
        foreign_keys="Ticket.created_by",
        back_populates="creator"
    )

    # Tickets assigned to this user
    assigned_tickets = relationship(
        "Ticket",
        foreign_keys="Ticket.assigned_to",
        back_populates="assignee"
    )

    # Comments authored by this user
    ticket_comments = relationship(
        "TicketComment",
        foreign_keys="TicketComment.author_id",
        back_populates="author",
    )

    # History events performed by this user
    ticket_history = relationship(
        "TicketHistory",
        foreign_keys="TicketHistory.actor_id",
        back_populates="actor",
    )

    # Attachments uploaded by this user
    ticket_attachments = relationship(
        "TicketAttachment",
        foreign_keys="TicketAttachment.uploaded_by",
        back_populates="uploader",
    )

    # Tickets resolved by this user (Phase 2B)
    resolved_tickets = relationship(
        "Ticket",
        foreign_keys="Ticket.resolved_by",
        back_populates="resolver",
    )

    # Tickets escalated by this user (Phase 2B)
    escalated_tickets = relationship(
        "Ticket",
        foreign_keys="Ticket.escalated_by",
        back_populates="escalator",
    )

    # Tickets escalated to this user (Phase 2B)
    escalation_received_tickets = relationship(
        "Ticket",
        foreign_keys="Ticket.escalated_to",
        back_populates="escalation_target",
    )

    # Notifications received by this user
    notifications = relationship(
        "Notification",
        foreign_keys="Notification.recipient_id",
        back_populates="recipient",
        cascade="all, delete-orphan",
        lazy="dynamic",
    )

    # Knowledge articles authored by this user
    knowledge_articles = relationship(
        "KnowledgeArticle",
        foreign_keys="KnowledgeArticle.author_id",
        back_populates="author",
        cascade="all, delete-orphan",
        lazy="dynamic",
    )