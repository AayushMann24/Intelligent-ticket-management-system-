from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from app.database.base import Base


class Ticket(Base):
    __tablename__ = "tickets"

    id = Column(Integer, primary_key=True, index=True)

    title = Column(String, nullable=False)

    description = Column(String, nullable=False)

    priority = Column(String, default="Medium")

    status = Column(String, default="Open")

    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )
    creator = relationship("User")
    assigned_to = Column(
    Integer,
    ForeignKey("users.id"),
    nullable=True
)