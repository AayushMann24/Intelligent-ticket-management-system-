from datetime import datetime, timezone

from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    DateTime,
    Float,
    Boolean,
    JSON,
    Text,
)

from sqlalchemy.orm import relationship

from app.database.connection import Base


class Ticket(Base):
    __tablename__ = "tickets"

    id = Column(Integer, primary_key=True, index=True)

    title = Column(String, nullable=False)

    description = Column(String, nullable=False)

    priority = Column(String, default="Medium")

    status = Column(
        String,
        nullable=False,
        default="Open",
    )

    # ==========================
    # AI Fields
    # ==========================

    category = Column(String, nullable=True)

    subcategory = Column(String, nullable=True)

    keywords = Column(JSON, nullable=True)

    confidence = Column(Float, nullable=True)

    priority_reason = Column(Text, nullable=True)

    assignment_reason = Column(Text, nullable=True)

    ai_processed = Column(
        Boolean,
        default=False,
    )

    # ==========================

    created_by = Column(
        Integer,
        ForeignKey("users.id"),
    )

    assigned_to = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=True,
    )

    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )

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