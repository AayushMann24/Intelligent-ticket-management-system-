from pydantic import BaseModel


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
# Ticket Response
# -----------------------------
class TicketResponse(BaseModel):
    id: int
    title: str
    description: str
    priority: str
    status: str
    created_by: int
    assigned_to: int | None = None

class Config:
        from_attributes = True

class TicketStatusUpdate(BaseModel):
        status: str
    
class TicketStatusUpdate(BaseModel):
        status: str