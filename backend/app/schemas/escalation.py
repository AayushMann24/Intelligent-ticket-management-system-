"""
Escalation API Schemas (Phase 2D-4)

Request/response models for the Admin-only escalation administration API.
Reuses the canonical escalation enums defined on the ORM models and the
existing ticket priority/type enums so validation stays consistent with the
SLA policy API.
"""

from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field

from app.models.escalation import EscalationEventType
from app.schemas.ticket import TicketPriority, TicketType


class EscalationTargetRole(str, Enum):
    """Roles that an escalation can be routed to.

    Mirrors the recipient resolution logic in escalation_service
    (Admin / Technician only; Employees are never escalation recipients).
    """

    ADMIN = "Admin"
    TECHNICIAN = "Technician"


# -----------------------------
# Escalation Rule Schemas
# -----------------------------

class EscalationRuleCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    event_type: EscalationEventType
    priority: TicketPriority
    ticket_type: Optional[TicketType] = None
    category: Optional[str] = None
    target_role: EscalationTargetRole = EscalationTargetRole.ADMIN
    notify_enabled: bool = True
    email_enabled: bool = True
    is_active: bool = True


class EscalationRuleUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=200)
    description: Optional[str] = None
    event_type: Optional[EscalationEventType] = None
    priority: Optional[TicketPriority] = None
    ticket_type: Optional[TicketType] = None
    category: Optional[str] = None
    target_role: Optional[EscalationTargetRole] = None
    notify_enabled: Optional[bool] = None
    email_enabled: Optional[bool] = None
    is_active: Optional[bool] = None


class EscalationRuleResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    event_type: EscalationEventType
    priority: str
    ticket_type: Optional[str] = None
    category: Optional[str] = None
    target_role: str
    notify_enabled: bool
    email_enabled: bool
    is_active: bool
    precedence: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class EscalationRuleListResponse(BaseModel):
    items: List[EscalationRuleResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


# -----------------------------
# Escalation Record Schemas
# -----------------------------

class EscalationRecordResponse(BaseModel):
    id: int
    ticket_id: int
    event_type: EscalationEventType
    rule_id: Optional[int] = None
    recipient_id: Optional[int] = None

    notification_created: bool
    notification_id: Optional[int] = None

    email_sent: bool
    email_error: Optional[str] = None
    # Derived, human-readable delivery state. "delivered" is only used when the
    # provider confirmed success (email_sent is True).
    delivery_status: str

    history_recorded: bool

    # Convenience fields (joined for admin readability)
    ticket_title: Optional[str] = None
    recipient_name: Optional[str] = None
    recipient_role: Optional[str] = None
    rule_name: Optional[str] = None

    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class EscalationRecordListResponse(BaseModel):
    items: List[EscalationRecordResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
