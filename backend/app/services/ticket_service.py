from datetime import datetime, timezone
from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload
from fastapi import HTTPException


from app.models.ticket import Ticket
from app.models.user import User
from app.schemas.ticket import TicketUpdate, TicketAssign, TicketResolve, TicketReopen, TicketClose, TicketEscalate, TicketType
from app.constants.status import TICKET_STATUS, TicketStatus

# Optional AI service import for testing
try:
    from app.services.ai_service import AIService
except ImportError:
    AIService = None

# History service for automatic recording
from app.services.ticket_history_service import record_history, HistoryEventType
# SLA service for automatic SLA assignment
from app.services.sla_service import assign_sla_to_ticket, mark_response_sla_met, mark_resolution_sla_met
# Notification service
from app.services.notification_service import create_notification
from app.models.notification import NotificationType
from app.services.ticket_utils import (
    _base_ticket_query,
    _base_user_query,
    _can_view_ticket,
    _can_modify_ticket,
    _can_delete_ticket,
    _can_view_ticket_history,
)


# ==========================================
# State Transition Policy (Phase 2B)
# ==========================================

# Valid status transitions: current_status -> list of allowed next statuses
VALID_TRANSITIONS = {
    TicketStatus.OPEN: [
        TicketStatus.ASSIGNED,
        TicketStatus.IN_PROGRESS,
        TicketStatus.RESOLVED,  # Direct resolution allowed for simple issues
        TicketStatus.CLOSED,    # Direct closure allowed (e.g., duplicate, invalid)
    ],
    TicketStatus.ASSIGNED: [
        TicketStatus.IN_PROGRESS,
        TicketStatus.OPEN,      # Reassign/unassign back to open
        TicketStatus.RESOLVED,  # Quick resolution
        TicketStatus.CLOSED,    # Direct closure
    ],
    TicketStatus.IN_PROGRESS: [
        TicketStatus.PENDING,
        TicketStatus.RESOLVED,
        TicketStatus.OPEN,      # Reopen/return to open
        TicketStatus.ASSIGNED,  # Reassign
    ],
    TicketStatus.PENDING: [
        TicketStatus.IN_PROGRESS,
        TicketStatus.RESOLVED,
        TicketStatus.OPEN,
    ],
    TicketStatus.RESOLVED: [
        TicketStatus.CLOSED,
        TicketStatus.OPEN,      # Reopen
        TicketStatus.IN_PROGRESS,  # Reopen to in progress
    ],
    TicketStatus.CLOSED: [
        TicketStatus.OPEN,      # Reopen after closure
    ],
}

# Role-based transition permissions
# Which roles can initiate which transitions
TRANSITION_PERMISSIONS = {
    TicketStatus.OPEN: {
        TicketStatus.ASSIGNED: ["Admin"],
        TicketStatus.IN_PROGRESS: ["Admin", "Technician"],
        TicketStatus.RESOLVED: ["Admin", "Technician"],
        TicketStatus.CLOSED: ["Admin"],
    },
    TicketStatus.ASSIGNED: {
        TicketStatus.IN_PROGRESS: ["Admin", "Technician"],
        TicketStatus.OPEN: ["Admin", "Technician"],
        TicketStatus.RESOLVED: ["Admin", "Technician"],
        TicketStatus.CLOSED: ["Admin"],
    },
    TicketStatus.IN_PROGRESS: {
        TicketStatus.PENDING: ["Admin", "Technician"],
        TicketStatus.RESOLVED: ["Admin", "Technician"],
        TicketStatus.OPEN: ["Admin", "Technician"],
        TicketStatus.ASSIGNED: ["Admin"],
    },
    TicketStatus.PENDING: {
        TicketStatus.IN_PROGRESS: ["Admin", "Technician"],
        TicketStatus.RESOLVED: ["Admin", "Technician"],
        TicketStatus.OPEN: ["Admin", "Technician"],
    },
    TicketStatus.RESOLVED: {
        TicketStatus.CLOSED: ["Admin", "Technician"],
        TicketStatus.OPEN: ["Admin", "Technician"],
        TicketStatus.IN_PROGRESS: ["Admin", "Technician"],
    },
    TicketStatus.CLOSED: {
        TicketStatus.OPEN: ["Admin"],
    },
}


def validate_transition(current_status: str, new_status: str, user_role: str) -> bool:
    """
    Validate if a status transition is allowed for the given role.
    Raises HTTPException if invalid.
    """
    if current_status == new_status:
        return True  # No change, always allowed

    # Check if transition is valid
    allowed_next = VALID_TRANSITIONS.get(current_status, [])
    if new_status not in allowed_next:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid status transition from '{current_status}' to '{new_status}'"
        )

    # Check role permission
    allowed_roles = TRANSITION_PERMISSIONS.get(current_status, {}).get(new_status, [])
    if user_role not in allowed_roles:
        raise HTTPException(
            status_code=403,
            detail=f"Role '{user_role}' not authorized for transition from '{current_status}' to '{new_status}'"
        )

    return True


def get_valid_transitions(current_status: str, user_role: str) -> list[str]:
    """Get list of valid next statuses for the current user role."""
    allowed_next = VALID_TRANSITIONS.get(current_status, [])
    return [
        status for status in allowed_next
        if user_role in TRANSITION_PERMISSIONS.get(current_status, {}).get(status, [])
    ]


# ==========================================
# Base query with soft delete filter
# ==========================================
def _base_ticket_query(db: Session):
    """Base query that excludes soft-deleted tickets."""
    return db.query(Ticket).filter(Ticket.is_deleted == False)


def _base_user_query(db: Session):
    """Base query that excludes soft-deleted users."""
    return db.query(User).filter(User.is_deleted == False)


# ==========================================
# Get Available Technicians
# ==========================================
def get_available_technicians(db: Session):
    """
    Returns all technicians/admins with their
    specialization and current workload using an optimized join.
    """
    # Subquery to calculate workload per technician
    workload_subquery = (
        _base_ticket_query(db)
        .filter(Ticket.status.in_(["Open", "Assigned", "In Progress"]))
        .with_entities(
            Ticket.assigned_to,
            func.count(Ticket.id).label("workload")
        )
        .group_by(Ticket.assigned_to)
        .subquery()
    )

    # Query users with outer join to include technicians with 0 workload
    technicians = (
        _base_user_query(db)
        .outerjoin(workload_subquery, User.id == workload_subquery.c.assigned_to)
        .filter(User.role.in_(["Admin", "Technician"]))
        .with_entities(User, func.coalesce(workload_subquery.c.workload, 0).label("workload"))
        .all()
    )

    result = [
        {
            "id": tech.id,
            "name": tech.name,
            "specialization": tech.specialization or "Other",
            "workload": workload,
        }
        for tech, workload in technicians
    ]

    return result


# ==========================================
# Build Ticket Helper
# ==========================================
def build_ticket(ticket_data, ai_result: dict, user_id: int) -> Ticket:
    """
    Constructs a Ticket ORM object from input data and AI state outputs.
    User-provided priority takes precedence over AI suggestion.
    """
    return Ticket(
        title=ticket_data.title,
        description=ticket_data.description,
        ticket_type=ticket_data.ticket_type.value if hasattr(ticket_data.ticket_type, 'value') else ticket_data.ticket_type,
        category=ai_result.get("category"),
        subcategory=ai_result.get("subcategory"),
        keywords=ai_result.get("keywords"),
        confidence=ai_result.get("confidence"),
        priority=ticket_data.priority or ai_result.get("priority"),
        priority_reason=ai_result.get("priority_reason"),
        assigned_to=ai_result.get("assigned_to"),
        assignment_reason=ai_result.get("assignment_reason"),
        ai_processed=True,
        created_by=user_id,
    )


# ==========================================
# Create Ticket
# ==========================================
def create_ticket(db: Session, ticket_data, user_id: int):
    # Build AI State
    technicians = get_available_technicians(db)

    # Use AI service if available, otherwise use defaults
    if AIService:
        ai_result = AIService.analyze_ticket(
            title=ticket_data.title,
            description=ticket_data.description,
            technicians=technicians,
        )
    else:
        # Default values for testing
        ai_result = {
            "category": "Other",
            "subcategory": "General",
            "keywords": [],
            "confidence": 0.0,
            "priority": ticket_data.priority,
            "priority_reason": "Default priority",
            "assigned_to": None,
            "assignment_reason": "AI service not available",
        }

    # Instantiate via helper function
    new_ticket = build_ticket(ticket_data, ai_result, user_id)

    db.add(new_ticket)
    db.flush()  # Flush to get the ID assigned

    # Assign SLA policy and calculate deadlines
    assign_sla_to_ticket(db, new_ticket, ticket_data)

    # Record history
    record_history(
        db=db,
        ticket_id=new_ticket.id,
        actor_id=user_id,
        event_type=HistoryEventType.TICKET_CREATED,
        new_value=f"Ticket created: {new_ticket.title}",
    )

    db.commit()
    db.refresh(new_ticket)

    return new_ticket


# ==========================================
# Get Tickets Based On User Role (with pagination)
# ==========================================
def get_tickets_for_user(
    db: Session,
    user_id: int,
    role: str,
    page: int = 1,
    page_size: int = 20,
    status: str | None = None,
    priority: str | None = None,
    ticket_type: str | None = None,
    search: str | None = None,
    sort_by: str = "created_at",
    sort_order: str = "desc",
):
    query = (
        _base_ticket_query(db)
        .options(
            joinedload(Ticket.assignee),
            joinedload(Ticket.resolver),
            joinedload(Ticket.escalator),
            joinedload(Ticket.escalation_target),
        )
    )

    # ==========================================
    # Admin -> See Every Ticket
    # ==========================================
    if role == "Admin":
        pass  # No additional filter

    # ==========================================
    # Technician -> Only Assigned Tickets
    # ==========================================
    elif role == "Technician":
        query = query.filter(Ticket.assigned_to == user_id)

    # ==========================================
    # Employee -> Only Created Tickets
    # ==========================================
    else:
        query = query.filter(Ticket.created_by == user_id)

    # Apply filters
    if status:
        query = query.filter(Ticket.status == status)
    if priority:
        query = query.filter(Ticket.priority == priority)
    if ticket_type:
        query = query.filter(Ticket.ticket_type == ticket_type)
    if search:
        query = query.filter(
            Ticket.title.ilike(f"%{search}%") | Ticket.description.ilike(f"%{search}%")
        )

    # Get total count before pagination
    total = query.count()

    # Apply sorting
    sort_column = getattr(Ticket, sort_by, Ticket.created_at)
    if sort_order == "desc":
        query = query.order_by(sort_column.desc())
    else:
        query = query.order_by(sort_column.asc())

    # Apply pagination
    offset = (page - 1) * page_size
    tickets = query.offset(offset).limit(page_size).all()

    total_pages = (total + page_size - 1) // page_size

    return {
        "items": [
            _serialize_ticket(ticket)
            for ticket in tickets
        ],
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
    }


def _serialize_ticket(ticket: Ticket) -> dict:
    """Serialize ticket with all Phase 2B fields."""
    return {
        "id": ticket.id,
        "title": ticket.title,
        "description": ticket.description,

        # AI Classification
        "category": ticket.category,
        "subcategory": ticket.subcategory,
        "keywords": ticket.keywords,
        "confidence": ticket.confidence,

        # Priority
        "priority": ticket.priority,
        "priority_reason": ticket.priority_reason,

        # Status
        "status": ticket.status,

        # Ticket Type (Phase 2B)
        "ticket_type": ticket.ticket_type,

        # Creator
        "created_by": ticket.created_by,

        # Assignment
        "assigned_to": ticket.assigned_to,
        "assigned_name": (
            ticket.assignee.name
            if ticket.assignee
            else None
        ),
        "assignment_reason": ticket.assignment_reason,

        # Resolution (Phase 2B)
        "resolution_summary": ticket.resolution_summary,
        "resolved_at": ticket.resolved_at,
        "resolved_by": ticket.resolved_by,
        "resolved_by_name": (
            ticket.resolver.name
            if ticket.resolver
            else None
        ),

        # Escalation (Phase 2B)
        "escalated_by": ticket.escalated_by,
        "escalated_by_name": (
            ticket.escalator.name
            if ticket.escalator
            else None
        ),
        "escalated_to": ticket.escalated_to,
        "escalated_to_name": (
            ticket.escalation_target.name
            if ticket.escalation_target
            else None
        ),
        "escalation_reason": ticket.escalation_reason,
        "escalated_at": ticket.escalated_at,

        # AI Metadata
        "ai_processed": ticket.ai_processed,

        # Timestamp
        "created_at": ticket.created_at,
        "updated_at": ticket.updated_at,
    }


# ==========================================
# Get Ticket By ID
# ==========================================
def get_ticket_by_id(
    db: Session,
    ticket_id: int,
):
    ticket = (
        _base_ticket_query(db)
        .options(
            joinedload(Ticket.assignee),
            joinedload(Ticket.resolver),
            joinedload(Ticket.escalator),
            joinedload(Ticket.escalation_target),
        )
        .filter(Ticket.id == ticket_id)
        .first()
    )

    if not ticket:
        raise HTTPException(
            status_code=404,
            detail="Ticket not found",
        )

    return ticket


def _can_view_ticket(user_id: int, user_role: str, ticket: Ticket) -> bool:
    """Check if user can view a ticket."""
    # Admin can view any ticket
    if user_role == "Admin":
        return True
    # Creator can view their own ticket
    if ticket.created_by == user_id:
        return True
    # Assignee can view their assigned ticket
    if ticket.assigned_to == user_id:
        return True
    return False


# ==========================================
# Update Ticket (Partial - for basic fields)
# ==========================================
def update_ticket(
    db: Session,
    ticket_id: int,
    ticket_data: TicketUpdate,
    user_id: int,
    user_role: str,
):

    ticket = get_ticket_by_id(
        db,
        ticket_id,
    )

    # Resource-level authorization
    if not _can_modify_ticket(user_id, user_role, ticket):
        raise HTTPException(
            status_code=403,
            detail="Not authorized to modify this ticket"
        )

    # Track changes for history
    history_events = []

    if ticket_data.title is not None and ticket_data.title != ticket.title:
        history_events.append((
            HistoryEventType.TITLE_CHANGED,
            ticket.title,
            ticket_data.title,
        ))
        ticket.title = ticket_data.title

    if ticket_data.description is not None and ticket_data.description != ticket.description:
        history_events.append((
            HistoryEventType.DESCRIPTION_CHANGED,
            ticket.description,
            ticket_data.description,
        ))
        ticket.description = ticket_data.description

    if ticket_data.priority is not None and ticket_data.priority != ticket.priority:
        history_events.append((
            HistoryEventType.PRIORITY_CHANGED,
            ticket.priority,
            ticket_data.priority.value if hasattr(ticket_data.priority, 'value') else ticket_data.priority,
        ))
        ticket.priority = ticket_data.priority.value if hasattr(ticket_data.priority, 'value') else ticket_data.priority

    if ticket_data.ticket_type is not None:
        new_type = ticket_data.ticket_type.value if hasattr(ticket_data.ticket_type, 'value') else ticket_data.ticket_type
        if new_type != ticket.ticket_type:
            history_events.append((
                HistoryEventType.TYPE_CHANGED,
                ticket.ticket_type,
                new_type,
            ))
            ticket.ticket_type = new_type

    # Note: status and assigned_to changes should go through explicit workflow endpoints
    # This prevents bypassing transition validation

    # Record history events
    for event_type, old_val, new_val in history_events:
        record_history(
            db=db,
            ticket_id=ticket_id,
            actor_id=user_id,
            event_type=event_type,
            old_value=old_val,
            new_value=new_val,
        )

    db.commit()
    db.refresh(ticket)

    return ticket


# ==========================================
# Delete Ticket (Soft Delete)
# ==========================================
def delete_ticket(
    db: Session,
    ticket_id: int,
    user_id: int,
    user_role: str,
):

    ticket = get_ticket_by_id(
        db,
        ticket_id,
    )

    # Resource-level authorization
    if not _can_delete_ticket(user_id, user_role, ticket):
        raise HTTPException(
            status_code=403,
            detail="Not authorized to delete this ticket"
        )

    ticket.is_deleted = True
    ticket.updated_at = func.now()

    db.commit()

    return {
        "message": "Ticket deleted successfully"
    }


def _can_modify_ticket(user_id: int, user_role: str, ticket: Ticket) -> bool:
    """Check if user can modify a ticket (basic fields)."""
    # Admin can modify any ticket
    if user_role == "Admin":
        return True
    # Creator can modify their own ticket
    if ticket.created_by == user_id:
        return True
    # Assignee can modify their assigned ticket
    if ticket.assigned_to == user_id:
        return True
    return False


def _can_delete_ticket(user_id: int, user_role: str, ticket: Ticket) -> bool:
    """Check if user can delete a ticket."""
    # Only Admin can delete tickets
    if user_role == "Admin":
        return True
    return False


# ==========================================
# WORKFLOW OPERATIONS (Phase 2B)
# ==========================================

# --- Assign Ticket ---
def assign_ticket(db: Session, ticket_id: int, assigned_to: int, user_id: int, user_role: str):
    ticket = get_ticket_by_id(db, ticket_id)

    # Only Admin can assign tickets
    if user_role != "Admin":
        raise HTTPException(
            status_code=403,
            detail="Only Admin can assign tickets"
        )

    user = _base_user_query(db).filter(User.id == assigned_to).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.role not in ["Admin", "Technician"]:
        raise HTTPException(
            status_code=400,
            detail="Ticket can only be assigned to an Admin or Technician"
        )

    # Validate transition
    validate_transition(ticket.status, TicketStatus.ASSIGNED, user_role)

    old_assigned = ticket.assigned_to
    ticket.assigned_to = assigned_to
    ticket.status = TicketStatus.ASSIGNED

    db.commit()
    db.refresh(ticket)

    # Record history
    event_type = HistoryEventType.REASSIGNED if old_assigned else HistoryEventType.ASSIGNED
    record_history(
        db=db,
        ticket_id=ticket_id,
        actor_id=user_id,
        event_type=event_type,
        old_value=str(old_assigned) if old_assigned else "Unassigned",
        new_value=str(assigned_to),
    )

    # Also record status change
    if ticket.status != "Assigned":  # Only if status actually changed
        record_history(
            db=db,
            ticket_id=ticket_id,
            actor_id=user_id,
            event_type=HistoryEventType.STATUS_CHANGED,
            old_value=ticket.status,  # This was the old status before change
            new_value=TicketStatus.ASSIGNED,
        )

    # Create notification for assigned user
    notification_type = NotificationType.TICKET_REASSIGNED if old_assigned else NotificationType.TICKET_ASSIGNED
    create_notification(
        db=db,
        recipient_id=assigned_to,
        notification_type=notification_type,
        title=f"Ticket {notification_type.value.replace('_', ' ').title()}",
        message=f"Ticket #{ticket_id}: {ticket.title} has been {'reassigned to' if old_assigned else 'assigned to'} you.",
        ticket_id=ticket_id,
    )

    return ticket


# --- Reassign Ticket ---
def reassign_ticket(db: Session, ticket_id: int, assigned_to: int, user_id: int, user_role: str):
    """Reassign an already assigned ticket to a different technician."""
    ticket = get_ticket_by_id(db, ticket_id)

    # Only Admin can reassign tickets
    if user_role != "Admin":
        raise HTTPException(
            status_code=403,
            detail="Only Admin can reassign tickets"
        )

    if not ticket.assigned_to:
        raise HTTPException(
            status_code=400,
            detail="Ticket is not currently assigned. Use assign endpoint instead."
        )

    user = _base_user_query(db).filter(User.id == assigned_to).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.role not in ["Admin", "Technician"]:
        raise HTTPException(
            status_code=400,
            detail="Ticket can only be assigned to an Admin or Technician"
        )

    if ticket.assigned_to == assigned_to:
        raise HTTPException(
            status_code=400,
            detail="Ticket is already assigned to this user"
        )

    old_assigned = ticket.assigned_to
    ticket.assigned_to = assigned_to
    # Status remains ASSIGNED (or IN_PROGRESS if it was already started)

    db.commit()
    db.refresh(ticket)

    # Record history
    record_history(
        db=db,
        ticket_id=ticket_id,
        actor_id=user_id,
        event_type=HistoryEventType.REASSIGNED,
        old_value=str(old_assigned),
        new_value=str(assigned_to),
    )

    # Create notification for newly assigned user
    create_notification(
        db=db,
        recipient_id=assigned_to,
        notification_type=NotificationType.TICKET_REASSIGNED,
        title="Ticket Reassigned",
        message=f"Ticket #{ticket_id}: {ticket.title} has been reassigned to you.",
        ticket_id=ticket_id,
    )

    return ticket


# --- Unassign Ticket ---
def unassign_ticket(db: Session, ticket_id: int, user_id: int, user_role: str):
    ticket = get_ticket_by_id(db, ticket_id)

    # Only Admin can unassign tickets
    if user_role != "Admin":
        raise HTTPException(
            status_code=403,
            detail="Only Admin can unassign tickets"
        )

    if not ticket.assigned_to:
        raise HTTPException(
            status_code=400,
            detail="Ticket is not currently assigned"
        )

    # Validate transition back to OPEN
    validate_transition(ticket.status, TicketStatus.OPEN, user_role)

    old_assigned = ticket.assigned_to
    ticket.assigned_to = None
    ticket.status = TicketStatus.OPEN
    ticket.assignment_reason = None

    db.commit()
    db.refresh(ticket)

    # Record history
    record_history(
        db=db,
        ticket_id=ticket_id,
        actor_id=user_id,
        event_type=HistoryEventType.UNASSIGNED,
        old_value=str(old_assigned),
        new_value="Unassigned",
    )

    # Record status change
    record_history(
        db=db,
        ticket_id=ticket_id,
        actor_id=user_id,
        event_type=HistoryEventType.STATUS_CHANGED,
        old_value=ticket.status,  # Will be the old status
        new_value=TicketStatus.OPEN,
    )

    return ticket


# --- Start Work (Transition to IN_PROGRESS) ---
def start_work(db: Session, ticket_id: int, user_id: int, user_role: str):
    """Technician starts working on an assigned ticket."""
    ticket = get_ticket_by_id(db, ticket_id)

    # Must be assignee or admin
    if user_role != "Admin" and ticket.assigned_to != user_id:
        raise HTTPException(
            status_code=403,
            detail="Only the assigned technician or Admin can start work"
        )

    if not ticket.assigned_to:
        raise HTTPException(
            status_code=400,
            detail="Ticket must be assigned before starting work"
        )

    # Validate transition
    validate_transition(ticket.status, TicketStatus.IN_PROGRESS, user_role)

    old_status = ticket.status
    ticket.status = TicketStatus.IN_PROGRESS

    db.commit()
    db.refresh(ticket)

    # Mark response SLA as met when technician starts work (first response)
    mark_response_sla_met(db, ticket)

    record_history(
        db=db,
        ticket_id=ticket_id,
        actor_id=user_id,
        event_type=HistoryEventType.STATUS_CHANGED,
        old_value=old_status,
        new_value=TicketStatus.IN_PROGRESS,
    )

    return ticket


# --- Mark Pending ---
def mark_pending(db: Session, ticket_id: int, user_id: int, user_role: str):
    ticket = get_ticket_by_id(db, ticket_id)

    # Must be assignee or admin
    if user_role != "Admin" and ticket.assigned_to != user_id:
        raise HTTPException(
            status_code=403,
            detail="Only the assigned technician or Admin can mark pending"
        )

    validate_transition(ticket.status, "Pending", user_role)

    old_status = ticket.status
    ticket.status = "Pending"

    db.commit()
    db.refresh(ticket)

    record_history(
        db=db,
        ticket_id=ticket_id,
        actor_id=user_id,
        event_type=HistoryEventType.STATUS_CHANGED,
        old_value=old_status,
        new_value="Pending",
    )

    return ticket


# --- Resolve Ticket ---
def resolve_ticket(db: Session, ticket_id: int, resolution_summary: str, user_id: int, user_role: str):
    ticket = get_ticket_by_id(db, ticket_id)

    # Must be assignee or admin
    if user_role != "Admin" and ticket.assigned_to != user_id:
        raise HTTPException(
            status_code=403,
            detail="Only the assigned technician or Admin can resolve tickets"
        )

    if not resolution_summary or not resolution_summary.strip():
        raise HTTPException(
            status_code=400,
            detail="Resolution summary is required"
        )

    validate_transition(ticket.status, TicketStatus.RESOLVED, user_role)

    old_status = ticket.status
    ticket.status = TicketStatus.RESOLVED
    ticket.resolution_summary = resolution_summary.strip()
    ticket.resolved_at = datetime.now(timezone.utc)
    ticket.resolved_by = user_id

    db.commit()
    db.refresh(ticket)

    # Mark resolution SLA as met
    mark_resolution_sla_met(db, ticket)

    # Record history - status change
    record_history(
        db=db,
        ticket_id=ticket_id,
        actor_id=user_id,
        event_type=HistoryEventType.STATUS_CHANGED,
        old_value=old_status,
        new_value=TicketStatus.RESOLVED,
    )

    # Record history - resolution
    record_history(
        db=db,
        ticket_id=ticket_id,
        actor_id=user_id,
        event_type=HistoryEventType.TICKET_RESOLVED,
        old_value=old_status,
        new_value=f"Resolved: {resolution_summary.strip()}",
    )

    return ticket


# --- Reopen Ticket ---
def reopen_ticket(db: Session, ticket_id: int, reason: str | None, user_id: int, user_role: str):
    ticket = get_ticket_by_id(db, ticket_id)

    # Creator, assignee, or admin can reopen
    if user_role != "Admin" and ticket.created_by != user_id and ticket.assigned_to != user_id:
        raise HTTPException(
            status_code=403,
            detail="Not authorized to reopen this ticket"
        )

    if ticket.status not in [TicketStatus.RESOLVED, TicketStatus.CLOSED]:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot reopen ticket with status '{ticket.status}'. Only Resolved or Closed tickets can be reopened."
        )

    # Determine target status based on current status
    if ticket.status == TicketStatus.CLOSED:
        target_status = TicketStatus.OPEN
        event_type = HistoryEventType.TICKET_REOPENED_AFTER_CLOSURE
    else:
        target_status = TicketStatus.OPEN
        event_type = HistoryEventType.TICKET_REOPENED

    validate_transition(ticket.status, target_status, user_role)

    old_status = ticket.status
    ticket.status = target_status
    ticket.resolution_summary = None
    ticket.resolved_at = None
    ticket.resolved_by = None

    db.commit()
    db.refresh(ticket)

    # Record history - status change
    record_history(
        db=db,
        ticket_id=ticket_id,
        actor_id=user_id,
        event_type=HistoryEventType.STATUS_CHANGED,
        old_value=old_status,
        new_value=target_status,
    )

    # Record history - reopen event
    reopen_detail = f"Reopened: {reason}" if reason else "Reopened"
    record_history(
        db=db,
        ticket_id=ticket_id,
        actor_id=user_id,
        event_type=event_type,
        old_value=old_status,
        new_value=reopen_detail,
    )

    return ticket


# --- Close Ticket ---
def close_ticket(db: Session, ticket_id: int, user_id: int, user_role: str):
    ticket = get_ticket_by_id(db, ticket_id)

    # Only Admin or Technician can close (but typically Technician closes their resolved tickets)
    if user_role not in ["Admin", "Technician"]:
        raise HTTPException(
            status_code=403,
            detail="Only Admin or Technician can close tickets"
        )

    # Technician can only close their own tickets
    if user_role == "Technician" and ticket.assigned_to != user_id:
        raise HTTPException(
            status_code=403,
            detail="Technicians can only close their own assigned tickets"
        )

    if ticket.status != TicketStatus.RESOLVED:
        raise HTTPException(
            status_code=400,
            detail=f"Only Resolved tickets can be closed. Current status: {ticket.status}"
        )

    validate_transition(ticket.status, TicketStatus.CLOSED, user_role)

    old_status = ticket.status
    ticket.status = TicketStatus.CLOSED

    db.commit()
    db.refresh(ticket)

    record_history(
        db=db,
        ticket_id=ticket_id,
        actor_id=user_id,
        event_type=HistoryEventType.STATUS_CHANGED,
        old_value=old_status,
        new_value=TicketStatus.CLOSED,
    )

    record_history(
        db=db,
        ticket_id=ticket_id,
        actor_id=user_id,
        event_type=HistoryEventType.TICKET_CLOSED,
        old_value=old_status,
        new_value="Ticket closed",
    )

    return ticket


# --- Escalate Ticket ---
def escalate_ticket(db: Session, ticket_id: int, escalated_to: int, escalation_reason: str, user_id: int, user_role: str):
    ticket = get_ticket_by_id(db, ticket_id)

    # Only Admin or Technician can escalate
    if user_role not in ["Admin", "Technician"]:
        raise HTTPException(
            status_code=403,
            detail="Only Admin or Technician can escalate tickets"
        )

    # Technician can only escalate their own tickets
    if user_role == "Technician" and ticket.assigned_to != user_id:
        raise HTTPException(
            status_code=403,
            detail="Technicians can only escalate their own assigned tickets"
        )

    if not escalation_reason or not escalation_reason.strip():
        raise HTTPException(
            status_code=400,
            detail="Escalation reason is required"
        )

    target_user = _base_user_query(db).filter(User.id == escalated_to).first()
    if not target_user:
        raise HTTPException(status_code=404, detail="Target user not found")

    if target_user.role not in ["Admin", "Technician"]:
        raise HTTPException(
            status_code=400,
            detail="Ticket can only be escalated to an Admin or Technician"
        )

    ticket.escalated_by = user_id
    ticket.escalated_to = escalated_to
    ticket.escalation_reason = escalation_reason.strip()
    ticket.escalated_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(ticket)

    record_history(
        db=db,
        ticket_id=ticket_id,
        actor_id=user_id,
        event_type=HistoryEventType.ESCALATED,
        old_value="",
        new_value=f"Escalated to {target_user.name}: {escalation_reason.strip()}",
    )

    # Create notification for escalation target
    create_notification(
        db=db,
        recipient_id=escalated_to,
        notification_type=NotificationType.TICKET_ESCALATED,
        title="Ticket Escalated",
        message=f"Ticket #{ticket_id}: {ticket.title} has been escalated to you. Reason: {escalation_reason.strip()}",
        ticket_id=ticket_id,
    )

    return ticket


# ==========================================
# My Assigned Tickets (with pagination)
# ==========================================
def get_my_assigned_tickets(
    db: Session,
    user_id: int,
    page: int = 1,
    page_size: int = 20,
    status: str | None = None,
    priority: str | None = None,
    search: str | None = None,
    sort_by: str = "created_at",
    sort_order: str = "desc",
):
    query = (
        _base_ticket_query(db)
        .filter(Ticket.assigned_to == user_id)
        .options(
            joinedload(Ticket.assignee),
            joinedload(Ticket.resolver),
            joinedload(Ticket.escalator),
            joinedload(Ticket.escalation_target),
        )
    )

    if status:
        query = query.filter(Ticket.status == status)
    if priority:
        query = query.filter(Ticket.priority == priority)
    if search:
        query = query.filter(
            Ticket.title.ilike(f"%{search}%") | Ticket.description.ilike(f"%{search}%")
        )

    total = query.count()

    sort_column = getattr(Ticket, sort_by, Ticket.created_at)
    if sort_order == "desc":
        query = query.order_by(sort_column.desc())
    else:
        query = query.order_by(sort_column.asc())

    offset = (page - 1) * page_size
    tickets = query.offset(offset).limit(page_size).all()

    total_pages = (total + page_size - 1) // page_size

    return {
        "items": [_serialize_ticket(ticket) for ticket in tickets],
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
    }


# ==========================================
# Update Ticket Status (Legacy - kept for backwards compat)
# ==========================================
def update_ticket_status(db: Session, ticket_id: int, status: str, user_id: int, user_role: str):
    """
    Legacy endpoint - uses transition validation.
    Prefer explicit workflow endpoints (start_work, resolve_ticket, etc.)
    """
    ticket = get_ticket_by_id(db, ticket_id)

    if status not in TICKET_STATUS:
        raise HTTPException(status_code=400, detail="Invalid ticket status")

    # Resource-level authorization
    if not _can_modify_ticket(user_id, user_role, ticket):
        raise HTTPException(
            status_code=403,
            detail="Not authorized to update this ticket's status"
        )

    # Validate transition
    validate_transition(ticket.status, status, user_role)

    old_status = ticket.status
    ticket.status = status

    db.commit()
    db.refresh(ticket)

    record_history(
        db=db,
        ticket_id=ticket_id,
        actor_id=user_id,
        event_type=HistoryEventType.STATUS_CHANGED,
        old_value=old_status,
        new_value=status,
    )

    return ticket


# ==========================================
# Get Valid Transitions for UI
# ==========================================
def get_workflow_actions(db: Session, ticket_id: int, user_id: int, user_role: str) -> dict:
    """Get available workflow actions for the current user on this ticket."""
    ticket = get_ticket_by_id(db, ticket_id)

    # Check view permission
    if not _can_view_ticket(user_id, user_role, ticket):
        raise HTTPException(status_code=404, detail="Ticket not found")

    actions = {
        "can_assign": False,
        "can_reassign": False,
        "can_unassign": False,
        "can_start_work": False,
        "can_mark_pending": False,
        "can_resolve": False,
        "can_reopen": False,
        "can_close": False,
        "can_escalate": False,
        "valid_status_transitions": [],
    }

    valid_transitions = get_valid_transitions(ticket.status, user_role)
    actions["valid_status_transitions"] = valid_transitions

    # Assign - Admin only, ticket unassigned
    if user_role == "Admin" and not ticket.assigned_to and ticket.status in [TicketStatus.OPEN]:
        actions["can_assign"] = True

    # Reassign - Admin only, ticket assigned
    if user_role == "Admin" and ticket.assigned_to:
        actions["can_reassign"] = True

    # Unassign - Admin only, ticket assigned
    if user_role == "Admin" and ticket.assigned_to:
        actions["can_unassign"] = True

    # Start work - Assignee or Admin, ticket assigned and in ASSIGNED/OPEN
    if (user_role == "Admin" or ticket.assigned_to == user_id) and ticket.assigned_to:
        if ticket.status in [TicketStatus.OPEN, TicketStatus.ASSIGNED]:
            if TicketStatus.IN_PROGRESS in valid_transitions:
                actions["can_start_work"] = True

    # Mark pending - Assignee or Admin, ticket in IN_PROGRESS
    if (user_role == "Admin" or ticket.assigned_to == user_id) and ticket.assigned_to:
        if ticket.status == TicketStatus.IN_PROGRESS:
            if "Pending" in valid_transitions:
                actions["can_mark_pending"] = True

    # Resolve - Assignee or Admin, ticket assigned
    if (user_role == "Admin" or ticket.assigned_to == user_id) and ticket.assigned_to:
        if TicketStatus.RESOLVED in valid_transitions:
            actions["can_resolve"] = True

    # Reopen - Creator, Assignee, or Admin, ticket RESOLVED or CLOSED
    if user_role == "Admin" or ticket.created_by == user_id or ticket.assigned_to == user_id:
        if ticket.status in [TicketStatus.RESOLVED, TicketStatus.CLOSED]:
            actions["can_reopen"] = True

    # Close - Admin or Technician (own tickets), ticket RESOLVED
    if user_role in ["Admin", "Technician"]:
        if ticket.status == TicketStatus.RESOLVED:
            if user_role == "Admin" or ticket.assigned_to == user_id:
                if TicketStatus.CLOSED in valid_transitions:
                    actions["can_close"] = True

    # Escalate - Admin or Technician (own tickets)
    if user_role in ["Admin", "Technician"]:
        if user_role == "Admin" or ticket.assigned_to == user_id:
            actions["can_escalate"] = True

    return actions