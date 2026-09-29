from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session

from app.database.connection import get_db

from app.schemas.ticket import (
    TicketCreate,
    TicketResponse,
    TicketUpdate,
    TicketAssign,
    TicketStatusUpdate,
    TicketUnassign,
    TicketResolve,
    TicketReopen,
    TicketClose,
    TicketEscalate,
    PaginationParams,
    PaginatedResponse,
)

from app.services.ticket_service import (
    create_ticket,
    get_tickets_for_user,
    get_ticket_by_id,
    update_ticket,
    delete_ticket,
    assign_ticket,
    reassign_ticket,
    unassign_ticket,
    start_work,
    mark_pending,
    resolve_ticket,
    reopen_ticket,
    close_ticket,
    escalate_ticket,
    get_my_assigned_tickets,
    update_ticket_status,
    get_workflow_actions,
)

from app.dependencies.roles import (
    require_admin,
    require_authenticated_user,
    require_technician,
    require_admin_or_technician,
)
from app.dependencies.csrf import csrf_protect

# Import comment, history, and attachment routers
from app.routers import ticket_comment, ticket_history, ticket_attachment

router = APIRouter(
    prefix="/tickets",
    tags=["Tickets"],
)

router.include_router(ticket_comment.router)
router.include_router(ticket_history.router)
router.include_router(ticket_attachment.router)


# ======================================================
# Create Ticket
# ======================================================

@router.post("/", response_model=TicketResponse, dependencies=[Depends(csrf_protect)])
def create_new_ticket(
    ticket: TicketCreate,
    db: Session = Depends(get_db),
    user=Depends(require_authenticated_user),
):

    return create_ticket(
        db=db,
        ticket_data=ticket,
        user_id=user["id"],
    )


# ======================================================
# Get Tickets (Role Based) with Pagination
# ======================================================

@router.get("/", response_model=dict)
def get_tickets(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    status: str | None = Query(None, description="Filter by status"),
    priority: str | None = Query(None, description="Filter by priority"),
    ticket_type: str | None = Query(None, description="Filter by ticket type"),
    search: str | None = Query(None, description="Search in title/description"),
    sort_by: str = Query("created_at", description="Sort field"),
    sort_order: str = Query("desc", pattern="^(asc|desc)$", description="Sort order"),
    db: Session = Depends(get_db),
    user=Depends(require_authenticated_user),
):

    return get_tickets_for_user(
        db=db,
        user_id=user["id"],
        role=user["role"],
        page=page,
        page_size=page_size,
        status=status,
        priority=priority,
        ticket_type=ticket_type,
        search=search,
        sort_by=sort_by,
        sort_order=sort_order,
    )


# ======================================================
# My Assigned Tickets with Pagination
# ======================================================

@router.get(
    "/my-assigned",
    response_model=dict,
)
def get_my_tickets(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    status: str | None = Query(None, description="Filter by status"),
    priority: str | None = Query(None, description="Filter by priority"),
    search: str | None = Query(None, description="Search in title/description"),
    sort_by: str = Query("created_at", description="Sort field"),
    sort_order: str = Query("desc", pattern="^(asc|desc)$", description="Sort order"),
    db: Session = Depends(get_db),
    user=Depends(require_technician),
):

    return get_my_assigned_tickets(
        db,
        user["id"],
        page=page,
        page_size=page_size,
        status=status,
        priority=priority,
        search=search,
        sort_by=sort_by,
        sort_order=sort_order,
    )


# ======================================================
# Ticket By ID
# ======================================================

@router.get(
    "/{ticket_id}",
    response_model=TicketResponse,
)
def get_ticket(
    ticket_id: int,
    db: Session = Depends(get_db),
    user=Depends(require_authenticated_user),
):

    ticket = get_ticket_by_id(
        db,
        ticket_id,
    )

    # Resource-level authorization: check if user can view this ticket
    from app.services.ticket_service import _can_view_ticket
    if not _can_view_ticket(user["id"], user["role"], ticket):
        raise HTTPException(
            status_code=404,
            detail="Ticket not found",
        )

    return ticket


# ======================================================
# Update Ticket (Basic Fields)
# ======================================================

@router.put(
    "/{ticket_id}",
    response_model=TicketResponse,
    dependencies=[Depends(csrf_protect)],
)
def update_existing_ticket(
    ticket_id: int,
    ticket: TicketUpdate,
    db: Session = Depends(get_db),
    user=Depends(require_authenticated_user),
):

    return update_ticket(
        db,
        ticket_id,
        ticket,
        user["id"],
        user["role"],
    )


# ======================================================
# WORKFLOW ENDPOINTS (Phase 2B)
# ======================================================

# --- Assign Ticket ---
@router.put(
    "/{ticket_id}/assign",
    response_model=TicketResponse,
    dependencies=[Depends(csrf_protect)],
)
def assign_ticket_to_user(
    ticket_id: int,
    ticket: TicketAssign,
    db: Session = Depends(get_db),
    user=Depends(require_admin),
):

    return assign_ticket(
        db,
        ticket_id,
        ticket.assigned_to,
        user["id"],
        user["role"],
    )


# --- Reassign Ticket ---
@router.put(
    "/{ticket_id}/reassign",
    response_model=TicketResponse,
    dependencies=[Depends(csrf_protect)],
)
def reassign_ticket_to_user(
    ticket_id: int,
    ticket: TicketAssign,
    db: Session = Depends(get_db),
    user=Depends(require_admin),
):

    return reassign_ticket(
        db,
        ticket_id,
        ticket.assigned_to,
        user["id"],
        user["role"],
    )


# --- Unassign Ticket ---
@router.post(
    "/{ticket_id}/unassign",
    response_model=TicketResponse,
    dependencies=[Depends(csrf_protect)],
)
def unassign_ticket_from_user(
    ticket_id: int,
    _: TicketUnassign,
    db: Session = Depends(get_db),
    user=Depends(require_admin),
):

    return unassign_ticket(
        db,
        ticket_id,
        user["id"],
        user["role"],
    )


# --- Start Work (Transition to IN_PROGRESS) ---
@router.post(
    "/{ticket_id}/start-work",
    response_model=TicketResponse,
    dependencies=[Depends(csrf_protect)],
)
def start_work_on_ticket(
    ticket_id: int,
    db: Session = Depends(get_db),
    user=Depends(require_admin_or_technician),
):

    return start_work(
        db,
        ticket_id,
        user["id"],
        user["role"],
    )


# --- Mark Pending ---
@router.post(
    "/{ticket_id}/mark-pending",
    response_model=TicketResponse,
    dependencies=[Depends(csrf_protect)],
)
def mark_ticket_pending(
    ticket_id: int,
    db: Session = Depends(get_db),
    user=Depends(require_admin_or_technician),
):

    return mark_pending(
        db,
        ticket_id,
        user["id"],
        user["role"],
    )


# --- Resolve Ticket ---
@router.post(
    "/{ticket_id}/resolve",
    response_model=TicketResponse,
    dependencies=[Depends(csrf_protect)],
)
def resolve_ticket_endpoint(
    ticket_id: int,
    data: TicketResolve,
    db: Session = Depends(get_db),
    user=Depends(require_admin_or_technician),
):

    return resolve_ticket(
        db,
        ticket_id,
        data.resolution_summary,
        user["id"],
        user["role"],
    )


# --- Reopen Ticket ---
@router.post(
    "/{ticket_id}/reopen",
    response_model=TicketResponse,
    dependencies=[Depends(csrf_protect)],
)
def reopen_ticket_endpoint(
    ticket_id: int,
    data: TicketReopen,
    db: Session = Depends(get_db),
    user=Depends(require_authenticated_user),
):

    return reopen_ticket(
        db,
        ticket_id,
        data.reason,
        user["id"],
        user["role"],
    )


# --- Close Ticket ---
@router.post(
    "/{ticket_id}/close",
    response_model=TicketResponse,
    dependencies=[Depends(csrf_protect)],
)
def close_ticket_endpoint(
    ticket_id: int,
    _: TicketClose,
    db: Session = Depends(get_db),
    user=Depends(require_admin_or_technician),
):

    return close_ticket(
        db,
        ticket_id,
        user["id"],
        user["role"],
    )


# --- Escalate Ticket ---
@router.post(
    "/{ticket_id}/escalate",
    response_model=TicketResponse,
    dependencies=[Depends(csrf_protect)],
)
def escalate_ticket_endpoint(
    ticket_id: int,
    data: TicketEscalate,
    db: Session = Depends(get_db),
    user=Depends(require_admin_or_technician),
):

    return escalate_ticket(
        db,
        ticket_id,
        data.escalated_to,
        data.escalation_reason,
        user["id"],
        user["role"],
    )


# --- Get Workflow Actions ---
@router.get(
    "/{ticket_id}/workflow-actions",
    response_model=dict,
)
def get_ticket_workflow_actions(
    ticket_id: int,
    db: Session = Depends(get_db),
    user=Depends(require_authenticated_user),
):

    return get_workflow_actions(
        db,
        ticket_id,
        user["id"],
        user["role"],
    )


# ======================================================
# Update Status (Legacy - with transition validation)
# ======================================================

@router.patch(
    "/{ticket_id}/status",
    response_model=TicketResponse,
    dependencies=[Depends(csrf_protect)],
)
def update_status(
    ticket_id: int,
    status_data: TicketStatusUpdate,
    db: Session = Depends(get_db),
    user=Depends(require_admin_or_technician),
):

    return update_ticket_status(
        db,
        ticket_id,
        status_data.status,
        user["id"],
        user["role"],
    )


# ======================================================
# Delete Ticket
# ======================================================

@router.delete("/{ticket_id}", dependencies=[Depends(csrf_protect)])
def delete_existing_ticket(
    ticket_id: int,
    db: Session = Depends(get_db),
    user=Depends(require_authenticated_user),
):

    return delete_ticket(
        db,
        ticket_id,
        user["id"],
        user["role"],
    )