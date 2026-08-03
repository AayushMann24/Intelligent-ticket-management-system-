from pydantic import BaseModel


class DashboardSummary(BaseModel):
    total_tickets: int
    open_tickets: int
    in_progress_tickets: int
    resolved_tickets: int

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