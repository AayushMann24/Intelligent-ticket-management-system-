from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel


# ======================================================
# Existing Dashboard Schemas
# ======================================================

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


# ======================================================
# Analytics Response Schemas (Phase 2E - Checkpoint 1)
# ======================================================

class TicketOverviewResponse(BaseModel):
    total_tickets: int
    open_tickets: int
    assigned_tickets: int
    pending_tickets: int
    resolved_tickets: int
    closed_tickets: int
    unassigned_tickets: int
    escalated_tickets: int


class PriorityCountResponse(BaseModel):
    priority: str
    count: int


class CategoryCountResponse(BaseModel):
    category: str
    count: int


class TicketTypeCountResponse(BaseModel):
    ticket_type: str
    count: int


class SLAResponseMetrics(BaseModel):
    tickets_with_response_sla: int
    met_count: int
    breached_count: int
    compliance_percentage: float


class SLAResolutionMetrics(BaseModel):
    tickets_with_resolution_sla: int
    met_count: int
    breached_count: int
    compliance_percentage: float


class SLAAnalyticsResponse(BaseModel):
    response_sla: SLAResponseMetrics
    resolution_sla: SLAResolutionMetrics
    tickets_with_sla: int


class EscalationAnalyticsResponse(BaseModel):
    total_escalations: int
    response_sla_escalations: int
    resolution_sla_escalations: int
    by_priority: Dict[str, int]
    by_recipient_role: Dict[str, int]
    escalations_over_time: List[Dict[str, Any]]
    currently_escalated_tickets: int


class ResponseResolutionTimeResponse(BaseModel):
    average_first_response_minutes: Optional[float]
    average_resolution_minutes: Optional[float]
    note: str


class TechnicianWorkloadItem(BaseModel):
    technician_id: int
    technician_name: str
    technician_email: str
    role: str
    tickets_currently_assigned: int
    open_assigned_tickets: int
    tickets_resolved: int
    escalations_received: int
    escalations_initiated: int


class TechnicianWorkloadResponse(BaseModel):
    workload: List[TechnicianWorkloadItem]


class TrendPoint(BaseModel):
    period: str
    tickets_created: int
    tickets_resolved: int
    sla_breaches: int
    escalations: int


class TrendResponse(BaseModel):
    granularity: str
    trends: List[TrendPoint]


class FilteredTicketAnalyticsResponse(BaseModel):
    total: int
    by_status: Dict[str, int]
    by_priority: Dict[str, int]


class AnalyticsFilters(BaseModel):
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    priority: Optional[str] = None
    category: Optional[str] = None
    ticket_type: Optional[str] = None
    assignee_id: Optional[int] = None
    granularity: Optional[str] = "daily"