from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session

from app.database.connection import get_db

from app.schemas.ticket import (
    SLAPolicyCreate,
    SLAPolicyUpdate,
    SLAPolicyResponse,
    TicketSLAResponse,
    PaginatedResponse,
)

from app.services.sla_service import (
    create_sla_policy,
    get_sla_policy,
    list_sla_policies,
    update_sla_policy,
    delete_sla_policy,
    serialize_sla_policy,
    serialize_ticket_sla,
)

from app.dependencies.roles import (
    require_admin,
    require_authenticated_user,
)

from app.models.ticket import Ticket
from app.services.ticket_utils import _can_view_ticket


router = APIRouter(
    prefix="/sla",
    tags=["SLA Policies"],
)


# ======================================================
# SLA Policy Management (Admin Only)
# ======================================================

@router.post(
    "/policies",
    response_model=SLAPolicyResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_sla_policy_endpoint(
    policy_data: SLAPolicyCreate,
    db: Session = Depends(get_db),
    user=Depends(require_admin),
):
    """Create a new SLA policy."""
    # Check if name already exists
    from app.services.sla_service import get_sla_policy_by_name
    existing = get_sla_policy_by_name(db, policy_data.name)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"SLA policy with name '{policy_data.name}' already exists"
        )

    policy = create_sla_policy(
        db=db,
        name=policy_data.name,
        priority=policy_data.priority.value,
        response_time_minutes=policy_data.response_time_minutes,
        resolution_time_minutes=policy_data.resolution_time_minutes,
        description=policy_data.description,
        ticket_type=policy_data.ticket_type.value if policy_data.ticket_type else None,
        category=policy_data.category,
        warning_threshold_percentage=policy_data.warning_threshold_percentage,
    )

    return serialize_sla_policy(policy)


@router.get(
    "/policies",
    response_model=dict,
)
def get_sla_policies(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    is_active: bool | None = Query(None, description="Filter by active status"),
    priority: str | None = Query(None, description="Filter by priority"),
    db: Session = Depends(get_db),
    user=Depends(require_admin),
):
    """List SLA policies with pagination."""
    result = list_sla_policies(
        db=db,
        page=page,
        page_size=page_size,
        is_active=is_active,
        priority=priority,
    )

    return {
        "items": [serialize_sla_policy(p) for p in result["items"]],
        "total": result["total"],
        "page": result["page"],
        "page_size": result["page_size"],
        "total_pages": result["total_pages"],
    }


@router.get(
    "/policies/{policy_id}",
    response_model=SLAPolicyResponse,
)
def get_sla_policy_endpoint(
    policy_id: int,
    db: Session = Depends(get_db),
    user=Depends(require_admin),
):
    """Get SLA policy by ID."""
    policy = get_sla_policy(db, policy_id)
    if not policy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="SLA policy not found"
        )
    return serialize_sla_policy(policy)


@router.put(
    "/policies/{policy_id}",
    response_model=SLAPolicyResponse,
)
def update_sla_policy_endpoint(
    policy_id: int,
    policy_data: SLAPolicyUpdate,
    db: Session = Depends(get_db),
    user=Depends(require_admin),
):
    """Update SLA policy."""
    # Convert to dict, excluding None values
    update_data = policy_data.model_dump(exclude_unset=True)

    # Convert enums to values
    if "priority" in update_data and hasattr(update_data["priority"], "value"):
        update_data["priority"] = update_data["priority"].value
    if "ticket_type" in update_data and hasattr(update_data["ticket_type"], "value"):
        update_data["ticket_type"] = update_data["ticket_type"].value

    policy = update_sla_policy(db, policy_id, **update_data)
    if not policy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="SLA policy not found"
        )

    return serialize_sla_policy(policy)


@router.delete(
    "/policies/{policy_id}",
    response_model=dict,
)
def delete_sla_policy_endpoint(
    policy_id: int,
    db: Session = Depends(get_db),
    user=Depends(require_admin),
):
    """Delete (deactivate) SLA policy."""
    success = delete_sla_policy(db, policy_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="SLA policy not found"
        )

    return {"message": "SLA policy deleted successfully"}


# ======================================================
# Ticket SLA Information (Authorized Viewers)
# ======================================================

@router.get(
    "/tickets/{ticket_id}",
    response_model=TicketSLAResponse,
)
def get_ticket_sla(
    ticket_id: int,
    db: Session = Depends(get_db),
    user=Depends(require_authenticated_user),
):
    """Get SLA information for a specific ticket."""
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found"
        )

    # Resource-level authorization
    if not _can_view_ticket(user["id"], user["role"], ticket):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found"
        )

    from app.services.sla_service import get_sla_policy
    policy = None
    if ticket.sla_policy_id:
        policy = get_sla_policy(db, ticket.sla_policy_id)

    return serialize_ticket_sla(ticket, policy)