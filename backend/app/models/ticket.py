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
    )

    priority_reason = Column(
        Text,
        nullable=True,
    )

    # =====================================================
    # Assignment
    # =====================================================

    assigned_to = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=True,
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
    )

    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
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