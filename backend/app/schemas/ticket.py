from datetime import datetime

from pydantic import BaseModel, ConfigDict


# -----------------------------
# Create Ticket
# -----------------------------
class TicketCreate(BaseModel):
    title: str
    description: str
    priority: str


# -----------------------------
# Update Ticket
# -----------------------------
class TicketUpdate(BaseModel):
    title: str
    description: str
    priority: str
    status: str
    assigned_to: int | None = None


# -----------------------------
# Assign Ticket
# -----------------------------
class TicketAssign(BaseModel):
    assigned_to: int


# -----------------------------
# Update Status
# -----------------------------
class TicketStatusUpdate(BaseModel):
    status: str


# -----------------------------
# Ticket Response
# -----------------------------
class TicketResponse(BaseModel):
    id: int
    title: str
    description: str
    priority: str
    status: str
    created_by: int
    assigned_to: str | None = None
    created_at: datetime | None = None

    model_config = ConfigDict(
        from_attributes=True
    )