from pydantic import BaseModel


class TicketCreate(BaseModel):
    title: str
    description: str
    priority: str


class TicketResponse(BaseModel):
    id: int
    title: str
    description: str
    priority: str
    status: str
    created_by: int

class TicketUpdate(BaseModel):
    title: str
    description: str
    priority: str
    status: str
    class Config:
        from_attributes = True
