from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    DateTime
)
from sqlalchemy.orm import relationship

from app.database.base import Base


class Ticket(Base):
    __tablename__ = "tickets"

    id = Column(Integer, primary_key=True, index=True)

    title = Column(String, nullable=False)

    description = Column(String, nullable=False)

    priority = Column(String, default="Medium")

    status = Column(String, default="Open")

    # User who created the ticket
    created_by = Column(
        Integer,
        ForeignKey("users.id")
    )

    # Technician assigned to the ticket
    assigned_to = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=True
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    # Relationship to the creator
    creator = relationship(
        "User",
        foreign_keys="Ticket.created_by",
        back_populates="created_tickets"
    )

    # Relationship to the assigned technician
    assignee = relationship(
        "User",
        foreign_keys="Ticket.assigned_to",
        back_populates="assigned_tickets"
    )