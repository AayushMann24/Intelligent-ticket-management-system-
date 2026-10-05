from datetime import datetime, timezone

from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Float,
    Boolean,
    JSON,
    ForeignKey,
    DateTime,
    Index,
)

from sqlalchemy.orm import relationship

from app.database.connection import Base


class Ticket(Base):
    __tablename__ = "tickets"

    # =====================================================
    # Primary Information
    # =====================================================

    id = Column(Integer, primary_key=True, index=True)

    title = Column(String, nullable=False)

    description = Column(Text, nullable=False)

    # =====================================================
    # AI Ticket Analysis
    # =====================================================

    category = Column(
        String,
        nullable=True,
        index=True,
    )

    subcategory = Column(
        String,
        nullable=True,
    )

    keywords = Column(
        JSON,
        nullable=True,
    )

    confidence = Column(
        Float,
        nullable=True,
    )

    # =====================================================
    # Priority
    # =====================================================

    priority = Column(
        String,
        nullable=False,
        default="Medium",
        index=True,
    )

    priority_reason = Column(
        Text,
        nullable=True,
    )

    # =====================================================
    # Ticket Type (Phase 2B)
    # =====================================================

    ticket_type = Column(
        String,
        nullable=False,
        default="INCIDENT",
        index=True,
    )

    # =====================================================
    # Assignment
    # =====================================================

    assigned_to = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=True,
        index=True,
    )

    assignment_reason = Column(
        Text,
        nullable=True,
    )

    # =====================================================
    # Ticket Status
    # =====================================================

    status = Column(
        String,
        nullable=False,
        default="Open",
        index=True,
    )

    # =====================================================
    # Resolution (Phase 2B)
    # =====================================================

    resolution_summary = Column(
        Text,
        nullable=True,
    )

    resolved_at = Column(
        DateTime(timezone=True),
        nullable=True,
    )

    resolved_by = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=True,
        index=True,
    )

    # =====================================================
    # Escalation Foundation (Phase 2B)
    # =====================================================

    escalated_by = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=True,
        index=True,
    )

    escalated_to = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=True,
        index=True,
    )

    escalation_reason = Column(
        Text,
        nullable=True,
    )

    escalated_at = Column(
        DateTime(timezone=True),
        nullable=True,
    )

    # =====================================================
    # SLA Fields (Phase 2C)
    # =====================================================

    sla_policy_id = Column(
        Integer,
        ForeignKey("sla_policies.id"),
        nullable=True,
        index=True,
    )

    sla_response_deadline = Column(
        DateTime(timezone=True),
        nullable=True,
    )

    sla_resolution_deadline = Column(
        DateTime(timezone=True),
        nullable=True,
    )

    sla_response_met_at = Column(
        DateTime(timezone=True),
        nullable=True,
    )

    sla_resolution_met_at = Column(
        DateTime(timezone=True),
        nullable=True,
    )

    sla_response_breached = Column(
        Boolean,
        default=False,
        nullable=False,
    )

    sla_resolution_breached = Column(
        Boolean,
        default=False,
        nullable=False,
    )

    # =====================================================
    # AI Metadata
    # =====================================================

    ai_processed = Column(
        Boolean,
        nullable=False,
        default=False,
    )

    # =====================================================
    # Creator Information
    # =====================================================

    created_by = Column(
        Integer,
        ForeignKey("users.id"),
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

    # =====================================================
    # Relationships
    # =====================================================

    creator = relationship(
        "User",
        foreign_keys="Ticket.created_by",
        back_populates="created_tickets",
    )

    assignee = relationship(
        "User",
        foreign_keys="Ticket.assigned_to",
        back_populates="assigned_tickets",
    )

    resolver = relationship(
        "User",
        foreign_keys="Ticket.resolved_by",
        back_populates="resolved_tickets",
    )

    escalator = relationship(
        "User",
        foreign_keys="Ticket.escalated_by",
        back_populates="escalated_tickets",
    )

    escalation_target = relationship(
        "User",
        foreign_keys="Ticket.escalated_to",
        back_populates="escalation_received_tickets",
    )

    sla_policy = relationship(
        "SLAPolicy",
        foreign_keys="Ticket.sla_policy_id",
        back_populates="tickets",
    )

    comments = relationship(
        "TicketComment",
        back_populates="ticket",
        cascade="all, delete-orphan",
        lazy="dynamic",
    )

    history = relationship(
        "TicketHistory",
        back_populates="ticket",
        cascade="all, delete-orphan",
        lazy="dynamic",
    )

    attachments = relationship(
        "TicketAttachment",
        back_populates="ticket",
        cascade="all, delete-orphan",
        lazy="dynamic",
    )

    notifications = relationship(
        "Notification",
        back_populates="ticket",
        cascade="all, delete-orphan",
        lazy="dynamic",
    )

    # =====================================================
    # Table Indexes
    # =====================================================

    __table_args__ = (
        Index("ix_tickets_status_priority", "status", "priority"),
        Index("ix_tickets_assigned_status", "assigned_to", "status"),
        Index("ix_tickets_created_status", "created_by", "status"),
        Index("ix_tickets_deleted_created", "is_deleted", "created_at"),
        Index("ix_tickets_sla_policy", "sla_policy_id"),
    )


class SLAPolicy(Base):
    """SLA Policy model for defining response and resolution time targets."""
    __tablename__ = "sla_policies"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String, nullable=False, unique=True, index=True)

    description = Column(Text, nullable=True)

    # Scope fields - at least priority is required
    priority = Column(
        String,
        nullable=False,
        index=True,
    )

    ticket_type = Column(
        String,
        nullable=True,
        index=True,
    )

    category = Column(
        String,
        nullable=True,
        index=True,
    )

    # Time targets in minutes
    response_time_minutes = Column(
        Integer,
        nullable=False,
    )

    resolution_time_minutes = Column(
        Integer,
        nullable=False,
    )

    # Warning threshold as percentage (e.g., 80 means warn at 80% of deadline)
    warning_threshold_percentage = Column(
        Integer,
        nullable=True,
    )

    is_active = Column(
        Boolean,
        default=True,
        nullable=False,
        index=True,
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

    # Relationship to tickets using this policy
    tickets = relationship("Ticket", back_populates="sla_policy")

    __table_args__ = (
        Index("ix_sla_policies_priority_type", "priority", "ticket_type"),
        Index("ix_sla_policies_active_priority", "is_active", "priority"),
    )