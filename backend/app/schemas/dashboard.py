from pydantic import BaseModel


class DashboardSummary(BaseModel):
    total_tickets: int
    open_tickets: int
    assigned_tickets: int
    resolved_tickets: int

    high_priority: int
    medium_priority: int
    low_priority: int

class RecentTicketResponse(BaseModel):
    id: int
    title: str
    priority: str
    status: str

    class Config:
        from_attributes = True

class PrioritySummary(BaseModel):
    high: int
    medium: int
    low: int