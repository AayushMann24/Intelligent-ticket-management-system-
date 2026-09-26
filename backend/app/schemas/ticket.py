from datetime import datetime
from enum import Enum
from pydantic import BaseModel, ConfigDict


class TicketPriority(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    CRITICAL = "Critical"


class TicketStatus(str, Enum):
    OPEN = "Open"
    ASSIGNED = "Assigned"
    IN_PROGRESS = "In Progress"
    PENDING = "Pending"
    RESOLVED = "Resolved"
    CLOSED = "Closed"


class TicketType(str, Enum):
    INCIDENT = "INCIDENT"
    SERVICE_REQUEST = "SERVICE_REQUEST"


class UserRole(str, Enum):
    ADMIN = "Admin"
    TECHNICIAN = "Technician"
    EMPLOYEE = "Employee"


# -----------------------------
# Create Ticket
# -----------------------------
class TicketCreate(BaseModel):
    title: str
    description: str
    priority: TicketPriority = TicketPriority.MEDIUM
    ticket_type: TicketType = TicketType.INCIDENT


# -----------------------------
# Update Ticket (Partial)
# -----------------------------
class TicketUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    priority: TicketPriority | None = None
    status: TicketStatus | None = None
    assigned_to: int | None = None
    ticket_type: TicketType | None = None


# -----------------------------
# Assign Ticket
# -----------------------------
class TicketAssign(BaseModel):
    assigned_to: int


# -----------------------------
# Unassign Ticket
# -----------------------------
class TicketUnassign(BaseModel):
    pass


# -----------------------------
# Resolve Ticket
# -----------------------------
class TicketResolve(BaseModel):
    resolution_summary: str


# -----------------------------
# Reopen Ticket
# -----------------------------
class TicketReopen(BaseModel):
    reason: str | None = None


# -----------------------------
# Close Ticket
# -----------------------------
class TicketClose(BaseModel):
    pass


# -----------------------------
# Escalate Ticket
# -----------------------------
class TicketEscalate(BaseModel):
    escalated_to: int
    escalation_reason: str


# -----------------------------
# Update Status
# -----------------------------
class TicketStatusUpdate(BaseModel):
    status: TicketStatus


# -----------------------------
# SLA Schemas (Phase 2C)
# -----------------------------

class SLAPolicyCreate(BaseModel):
    name: str
    description: str | None = None
    priority: TicketPriority
    ticket_type: TicketType | None = None
    category: str | None = None
    response_time_minutes: int
    resolution_time_minutes: int
    warning_threshold_percentage: int | None = None


class SLAPolicyUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    priority: TicketPriority | None = None
    ticket_type: TicketType | None = None
    category: str | None = None
    response_time_minutes: int | None = None
    resolution_time_minutes: int | None = None
    warning_threshold_percentage: int | None = None
    is_active: bool | None = None


class SLAPolicyResponse(BaseModel):
    id: int
    name: str
    description: str | None = None
    priority: str
    ticket_type: str | None = None
    category: str | None = None
    response_time_minutes: int
    resolution_time_minutes: int
    warning_threshold_percentage: int | None = None
    is_active: bool
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


# SLA status enum for ticket SLA info
class SLAStatus(str, Enum):
    NO_SLA = "NO_SLA"
    RESPONSE_PENDING = "RESPONSE_PENDING"
    RESPONSE_MET = "RESPONSE_MET"
    RESPONSE_BREACHED = "RESPONSE_BREACHED"
    RESOLUTION_PENDING = "RESOLUTION_PENDING"
    RESOLUTION_MET = "RESOLUTION_MET"
    RESOLUTION_BREACHED = "RESOLUTION_BREACHED"


class TicketSLAResponse(BaseModel):
    has_sla: bool
    policy: SLAPolicyResponse | None = None
    response_deadline: datetime | None = None
    resolution_deadline: datetime | None = None
    response_status: str
    resolution_status: str
    response_met_at: datetime | None = None
    resolution_met_at: datetime | None = None
    response_breached: bool = False
    resolution_breached: bool = False


# -----------------------------
# Pagination
# -----------------------------
class PaginationParams(BaseModel):
    page: int = 1
    page_size: int = 20

    class Config:
        validate_assignment = True


class PaginatedResponse(BaseModel):
    items: list
    total: int
    page: int
    page_size: int
    total_pages: int


# -----------------------------
# Ticket Response
# -----------------------------
class TicketResponse(BaseModel):
    id: int
    title: str
    description: str

    category: str | None = None
    subcategory: str | None = None
    keywords: list[str] | None = None
    confidence: float | None = None

    priority: str
    priority_reason: str | None = None

    status: str

    ticket_type: str

    created_by: int

    assigned_to: int | None = None
    assigned_name: str | None = None

    assignment_reason: str | None = None

    resolution_summary: str | None = None
    resolved_at: datetime | None = None
    resolved_by: int | None = None
    resolved_by_name: str | None = None

    escalated_by: int | None = None
    escalated_by_name: str | None = None
    escalated_to: int | None = None
    escalated_to_name: str | None = None
    escalation_reason: str | None = None
    escalated_at: datetime | None = None

    # SLA Fields (Phase 2C)
    sla_policy_id: int | None = None
    sla_response_deadline: datetime | None = None
    sla_resolution_deadline: datetime | None = None
    sla_response_status: str | None = None
    sla_resolution_status: str | None = None
    sla_response_breached: bool = False
    sla_resolution_breached: bool = False

    ai_processed: bool = False

    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)