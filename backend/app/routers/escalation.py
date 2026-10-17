"""
Escalation Administration Router (Phase 2D-4)

Admin-only API for managing SLA escalation rules and inspecting escalation
records (including email delivery status).

All endpoints require the Admin role. State-changing endpoints additionally
enforce CSRF protection via the shared dependency, matching the SLA policy API.
Credential material (SMTP passwords etc.) is never returned or accepted here.
"""

from typing import Optional

from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.dependencies.roles import require_admin
from app.dependencies.csrf import csrf_protect

from app.models.escalation import EscalationEventType

from app.schemas.escalation import (
    EscalationRuleCreate,
    EscalationRuleUpdate,
    EscalationRuleResponse,
    EscalationRuleListResponse,
    EscalationRecordResponse,
    EscalationRecordListResponse,
)

from app.services.escalation_service import (
    create_escalation_rule,
    get_escalation_rule,
    get_escalation_rule_by_name,
    list_escalation_rules,
    update_escalation_rule,
    delete_escalation_rule,
    get_escalation_record,
    list_escalation_records,
    serialize_escalation_rule,
    serialize_escalation_record,
)

from app.utils.logging_config import get_logger

logger = get_logger(__name__)

router = APIRouter(
    prefix="/escalations",
    tags=["Escalations"],
)


# ======================================================
# Escalation Rule Management (Admin Only)
# ======================================================

@router.post(
    "/rules",
    response_model=EscalationRuleResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(csrf_protect)],
)
def create_escalation_rule_endpoint(
    rule_data: EscalationRuleCreate,
    db: Session = Depends(get_db),
    user=Depends(require_admin),
):
    """Create a new escalation rule."""
    existing = get_escalation_rule_by_name(db, rule_data.name)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Escalation rule with name '{rule_data.name}' already exists",
        )

    rule = create_escalation_rule(
        db=db,
        name=rule_data.name,
        event_type=rule_data.event_type,
        priority=rule_data.priority.value,
        target_role=rule_data.target_role.value,
        description=rule_data.description,
        ticket_type=rule_data.ticket_type.value if rule_data.ticket_type else None,
        category=rule_data.category,
        notify_enabled=rule_data.notify_enabled,
        email_enabled=rule_data.email_enabled,
        is_active=rule_data.is_active,
    )

    logger.info(f"Admin created escalation rule '{rule.name}' (id={rule.id})")
    return serialize_escalation_rule(rule)


@router.get(
    "/rules",
    response_model=EscalationRuleListResponse,
)
def list_escalation_rules_endpoint(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    event_type: Optional[EscalationEventType] = Query(None, description="Filter by SLA event type"),
    priority: Optional[str] = Query(None, description="Filter by priority"),
    db: Session = Depends(get_db),
    user=Depends(require_admin),
):
    """List escalation rules with pagination, ordered by precedence."""
    result = list_escalation_rules(
        db=db,
        page=page,
        page_size=page_size,
        is_active=is_active,
        event_type=event_type,
        priority=priority,
    )

    return {
        "items": [serialize_escalation_rule(r) for r in result["items"]],
        "total": result["total"],
        "page": result["page"],
        "page_size": result["page_size"],
        "total_pages": result["total_pages"],
    }


@router.get(
    "/rules/{rule_id}",
    response_model=EscalationRuleResponse,
)
def get_escalation_rule_endpoint(
    rule_id: int,
    db: Session = Depends(get_db),
    user=Depends(require_admin),
):
    """Get an escalation rule by ID."""
    rule = get_escalation_rule(db, rule_id)
    if not rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Escalation rule not found",
        )
    return serialize_escalation_rule(rule)


@router.put(
    "/rules/{rule_id}",
    response_model=EscalationRuleResponse,
    dependencies=[Depends(csrf_protect)],
)
def update_escalation_rule_endpoint(
    rule_id: int,
    rule_data: EscalationRuleUpdate,
    db: Session = Depends(get_db),
    user=Depends(require_admin),
):
    """Update an escalation rule."""
    rule = get_escalation_rule(db, rule_id)
    if not rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Escalation rule not found",
        )

    update_data = rule_data.model_dump(exclude_unset=True)

    # Guard against renaming onto an existing rule's unique name.
    if "name" in update_data and update_data["name"] != rule.name:
        duplicate = get_escalation_rule_by_name(db, update_data["name"])
        if duplicate and duplicate.id != rule_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Escalation rule with name '{update_data['name']}' already exists",
            )

    # Normalise enums to their stored string values.
    if "priority" in update_data and hasattr(update_data["priority"], "value"):
        update_data["priority"] = update_data["priority"].value
    if "ticket_type" in update_data and hasattr(update_data["ticket_type"], "value"):
        update_data["ticket_type"] = update_data["ticket_type"].value
    if "target_role" in update_data and hasattr(update_data["target_role"], "value"):
        update_data["target_role"] = update_data["target_role"].value

    updated = update_escalation_rule(db, rule_id, **update_data)
    logger.info(f"Admin updated escalation rule id={rule_id}")
    return serialize_escalation_rule(updated)


@router.delete(
    "/rules/{rule_id}",
    response_model=dict,
    dependencies=[Depends(csrf_protect)],
)
def deactivate_escalation_rule_endpoint(
    rule_id: int,
    db: Session = Depends(get_db),
    user=Depends(require_admin),
):
    """
    Deactivate (soft-delete) an escalation rule.

    Rules are never hard-deleted so historical EscalationRecord references
    remain intact.
    """
    rule = get_escalation_rule(db, rule_id)
    if not rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Escalation rule not found",
        )

    delete_escalation_rule(db, rule_id)
    logger.info(f"Admin deactivated escalation rule id={rule_id}")
    return {
        "message": "Escalation rule deactivated successfully",
        "rule_id": rule_id,
        "is_active": False,
    }


# ======================================================
# Escalation Records (Admin Only, Read-Only)
# ======================================================

@router.get(
    "/records",
    response_model=EscalationRecordListResponse,
)
def list_escalation_records_endpoint(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    event_type: Optional[EscalationEventType] = Query(None, description="Filter by SLA event type"),
    ticket_id: Optional[int] = Query(None, description="Filter by ticket ID"),
    rule_id: Optional[int] = Query(None, description="Filter by rule ID"),
    email_sent: Optional[bool] = Query(None, description="Filter by email delivery success"),
    db: Session = Depends(get_db),
    user=Depends(require_admin),
):
    """List escalation records with delivery status, newest first."""
    result = list_escalation_records(
        db=db,
        page=page,
        page_size=page_size,
        event_type=event_type,
        ticket_id=ticket_id,
        rule_id=rule_id,
        email_sent=email_sent,
    )

    return {
        "items": [serialize_escalation_record(r) for r in result["items"]],
        "total": result["total"],
        "page": result["page"],
        "page_size": result["page_size"],
        "total_pages": result["total_pages"],
    }


@router.get(
    "/records/{record_id}",
    response_model=EscalationRecordResponse,
)
def get_escalation_record_endpoint(
    record_id: int,
    db: Session = Depends(get_db),
    user=Depends(require_admin),
):
    """Get a single escalation record, including delivery status."""
    record = get_escalation_record(db, record_id)
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Escalation record not found",
        )
    return serialize_escalation_record(record)
