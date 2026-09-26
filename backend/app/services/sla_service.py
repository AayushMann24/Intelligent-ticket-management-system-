from datetime import datetime, timedelta, timezone
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from app.models.ticket import Ticket, SLAPolicy
from app.schemas.ticket import TicketCreate


# ==========================================
# SLA Policy Matching Logic
# ==========================================

def get_matching_policies(
    db: Session,
    priority: str,
    ticket_type: str = "INCIDENT",
    category: Optional[str] = None,
) -> List[SLAPolicy]:
    """
    Get all active SLA policies that match the given ticket attributes.
    Returns policies ordered by specificity (most specific first).
    """
    query = db.query(SLAPolicy).filter(
        SLAPolicy.is_active == True,
        SLAPolicy.priority == priority,
    )

    # Filter by ticket_type if provided
    if ticket_type:
        query = query.filter(
            or_(
                SLAPolicy.ticket_type == ticket_type,
                SLAPolicy.ticket_type.is_(None),
            )
        )

    # Filter by category if provided
    if category:
        query = query.filter(
            or_(
                SLAPolicy.category == category,
                SLAPolicy.category.is_(None),
            )
        )

    policies = query.all()

    # Sort by specificity (most specific first)
    # Specificity score: ticket_type + category + priority (3) > ticket_type + priority (2) > category + priority (2) > priority only (1)
    def specificity_score(policy: SLAPolicy) -> int:
        score = 1  # priority always matches
        if policy.ticket_type:
            score += 1
        if policy.category:
            score += 1
        return score

    policies.sort(key=specificity_score, reverse=True)
    return policies


def get_best_matching_policy(
    db: Session,
    priority: str,
    ticket_type: str = "INCIDENT",
    category: Optional[str] = None,
) -> Optional[SLAPolicy]:
    """
    Get the single best matching SLA policy for the given ticket attributes.
    Returns None if no matching policy exists.
    """
    policies = get_matching_policies(db, priority, ticket_type, category)
    return policies[0] if policies else None


# ==========================================
# SLA Deadline Calculation
# ==========================================

def calculate_response_deadline(
    created_at: datetime,
    response_time_minutes: int,
) -> datetime:
    """Calculate response deadline from creation time."""
    if created_at.tzinfo is None:
        created_at = created_at.replace(tzinfo=timezone.utc)
    return created_at + timedelta(minutes=response_time_minutes)


def calculate_resolution_deadline(
    created_at: datetime,
    resolution_time_minutes: int,
) -> datetime:
    """Calculate resolution deadline from creation time."""
    if created_at.tzinfo is None:
        created_at = created_at.replace(tzinfo=timezone.utc)
    return created_at + timedelta(minutes=resolution_time_minutes)


def calculate_sla_deadlines(
    created_at: datetime,
    policy: SLAPolicy,
) -> tuple[datetime, datetime]:
    """Calculate both response and resolution deadlines."""
    response_deadline = calculate_response_deadline(created_at, policy.response_time_minutes)
    resolution_deadline = calculate_resolution_deadline(created_at, policy.resolution_time_minutes)
    return response_deadline, resolution_deadline


# ==========================================
# SLA Assignment on Ticket Creation
# ==========================================

def assign_sla_to_ticket(
    db: Session,
    ticket: Ticket,
    ticket_data: TicketCreate,
) -> None:
    """
    Assign SLA policy to a ticket and calculate deadlines.
    Modifies the ticket object in place.
    Does not raise if no matching policy - ticket simply gets no SLA.
    """
    # Get ticket attributes for matching
    priority = ticket.priority
    ticket_type = ticket.ticket_type
    category = ticket.category

    # Find best matching policy
    policy = get_best_matching_policy(db, priority, ticket_type, category)

    if policy:
        ticket.sla_policy_id = policy.id
        response_deadline, resolution_deadline = calculate_sla_deadlines(ticket.created_at, policy)
        ticket.sla_response_deadline = response_deadline
        ticket.sla_resolution_deadline = resolution_deadline
    else:
        # No matching policy - leave SLA fields as None
        ticket.sla_policy_id = None
        ticket.sla_response_deadline = None
        ticket.sla_resolution_deadline = None


# ==========================================
# SLA State Management
# ==========================================

class SLAStatus:
    NO_SLA = "NO_SLA"
    RESPONSE_PENDING = "RESPONSE_PENDING"
    RESPONSE_MET = "RESPONSE_MET"
    RESPONSE_BREACHED = "RESPONSE_BREACHED"
    RESOLUTION_PENDING = "RESOLUTION_PENDING"
    RESOLUTION_MET = "RESOLUTION_MET"
    RESOLUTION_BREACHED = "RESOLUTION_BREACHED"


def get_sla_response_status(ticket: Ticket) -> str:
    """Get current response SLA status for a ticket."""
    if not ticket.sla_policy_id:
        return SLAStatus.NO_SLA

    if ticket.sla_response_met_at:
        return SLAStatus.RESPONSE_MET

    if ticket.sla_response_breached:
        return SLAStatus.RESPONSE_BREACHED

    if ticket.sla_response_deadline:
        now = datetime.now(timezone.utc)
        deadline = ticket.sla_response_deadline
        if deadline.tzinfo is None:
            deadline = deadline.replace(tzinfo=timezone.utc)
        if now > deadline:
            return SLAStatus.RESPONSE_BREACHED
        return SLAStatus.RESPONSE_PENDING

    return SLAStatus.NO_SLA


def get_sla_resolution_status(ticket: Ticket) -> str:
    """Get current resolution SLA status for a ticket."""
    if not ticket.sla_policy_id:
        return SLAStatus.NO_SLA

    if ticket.sla_resolution_met_at:
        return SLAStatus.RESOLUTION_MET

    if ticket.sla_resolution_breached:
        return SLAStatus.RESOLUTION_BREACHED

    if ticket.sla_resolution_deadline:
        now = datetime.now(timezone.utc)
        deadline = ticket.sla_resolution_deadline
        if deadline.tzinfo is None:
            deadline = deadline.replace(tzinfo=timezone.utc)
        if now > deadline:
            return SLAStatus.RESOLUTION_BREACHED
        return SLAStatus.RESOLUTION_PENDING

    return SLAStatus.NO_SLA


def mark_response_sla_met(db: Session, ticket: Ticket) -> bool:
    """
    Mark response SLA as met when first qualifying response occurs.
    Returns True if state changed, False otherwise.
    """
    if not ticket.sla_policy_id or ticket.sla_response_met_at:
        return False

    now = datetime.now(timezone.utc)
    ticket.sla_response_met_at = now

    # Check if met within deadline
    if ticket.sla_response_deadline:
        deadline = ticket.sla_response_deadline
        if deadline.tzinfo is None:
            deadline = deadline.replace(tzinfo=timezone.utc)
        if now > deadline:
            ticket.sla_response_breached = True
        else:
            ticket.sla_response_breached = False

    db.commit()
    return True


def mark_resolution_sla_met(db: Session, ticket: Ticket) -> bool:
    """
    Mark resolution SLA as met when ticket is resolved.
    Returns True if state changed, False otherwise.
    """
    if not ticket.sla_policy_id or ticket.sla_resolution_met_at:
        return False

    now = datetime.now(timezone.utc)
    ticket.sla_resolution_met_at = now

    # Check if met within deadline
    if ticket.sla_resolution_deadline:
        deadline = ticket.sla_resolution_deadline
        if deadline.tzinfo is None:
            deadline = deadline.replace(tzinfo=timezone.utc)
        if now > deadline:
            ticket.sla_resolution_breached = True
        else:
            ticket.sla_resolution_breached = False

    db.commit()
    return True


# ==========================================
# SLA Policy CRUD
# ==========================================

def create_sla_policy(
    db: Session,
    name: str,
    priority: str,
    response_time_minutes: int,
    resolution_time_minutes: int,
    description: Optional[str] = None,
    ticket_type: Optional[str] = None,
    category: Optional[str] = None,
    warning_threshold_percentage: Optional[int] = None,
) -> SLAPolicy:
    """Create a new SLA policy."""
    policy = SLAPolicy(
        name=name,
        description=description,
        priority=priority,
        ticket_type=ticket_type,
        category=category,
        response_time_minutes=response_time_minutes,
        resolution_time_minutes=resolution_time_minutes,
        warning_threshold_percentage=warning_threshold_percentage,
        is_active=True,
    )
    db.add(policy)
    db.commit()
    db.refresh(policy)
    return policy


def get_sla_policy(db: Session, policy_id: int) -> Optional[SLAPolicy]:
    """Get SLA policy by ID."""
    return db.query(SLAPolicy).filter(SLAPolicy.id == policy_id).first()


def get_sla_policy_by_name(db: Session, name: str) -> Optional[SLAPolicy]:
    """Get SLA policy by name."""
    return db.query(SLAPolicy).filter(SLAPolicy.name == name).first()


def list_sla_policies(
    db: Session,
    page: int = 1,
    page_size: int = 20,
    is_active: Optional[bool] = None,
    priority: Optional[str] = None,
) -> dict:
    """List SLA policies with pagination."""
    query = db.query(SLAPolicy)

    if is_active is not None:
        query = query.filter(SLAPolicy.is_active == is_active)

    if priority:
        query = query.filter(SLAPolicy.priority == priority)

    total = query.count()

    query = query.order_by(SLAPolicy.priority, SLAPolicy.ticket_type, SLAPolicy.name)

    offset = (page - 1) * page_size
    policies = query.offset(offset).limit(page_size).all()

    total_pages = (total + page_size - 1) // page_size

    return {
        "items": policies,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
    }


def update_sla_policy(
    db: Session,
    policy_id: int,
    **kwargs,
) -> Optional[SLAPolicy]:
    """Update SLA policy."""
    policy = get_sla_policy(db, policy_id)
    if not policy:
        return None

    for key, value in kwargs.items():
        if hasattr(policy, key) and key != "id":
            setattr(policy, key, value)

    policy.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(policy)
    return policy


def delete_sla_policy(db: Session, policy_id: int) -> bool:
    """
    Soft delete (deactivate) SLA policy.
    Returns True if deactivated, False if not found.
    """
    policy = get_sla_policy(db, policy_id)
    if not policy:
        return False

    # Check if any active tickets are using this policy
    active_tickets = db.query(Ticket).filter(
        Ticket.sla_policy_id == policy_id,
        Ticket.is_deleted == False,
    ).count()

    if active_tickets > 0:
        # Deactivate instead of hard delete to preserve historical references
        policy.is_active = False
        policy.updated_at = datetime.now(timezone.utc)
        db.commit()
    else:
        # No active tickets using this policy - can hard delete
        db.delete(policy)
        db.commit()

    return True


# ==========================================
# SLA Serialization for API Responses
# ==========================================

def serialize_sla_policy(policy: SLAPolicy) -> dict:
    """Serialize SLA policy for API response."""
    return {
        "id": policy.id,
        "name": policy.name,
        "description": policy.description,
        "priority": policy.priority,
        "ticket_type": policy.ticket_type,
        "category": policy.category,
        "response_time_minutes": policy.response_time_minutes,
        "resolution_time_minutes": policy.resolution_time_minutes,
        "warning_threshold_percentage": policy.warning_threshold_percentage,
        "is_active": policy.is_active,
        "created_at": policy.created_at,
        "updated_at": policy.updated_at,
    }


def serialize_ticket_sla(ticket: Ticket, policy: Optional[SLAPolicy] = None) -> dict:
    """Serialize ticket SLA information for API response."""
    if not ticket.sla_policy_id and not policy:
        return {
            "has_sla": False,
            "policy": None,
            "response_deadline": None,
            "resolution_deadline": None,
            "response_status": SLAStatus.NO_SLA,
            "resolution_status": SLAStatus.NO_SLA,
            "response_met_at": None,
            "resolution_met_at": None,
            "response_breached": False,
            "resolution_breached": False,
        }

    if not policy:
        policy = ticket.sla_policy

    response_status = get_sla_response_status(ticket)
    resolution_status = get_sla_resolution_status(ticket)

    return {
        "has_sla": True,
        "policy": serialize_sla_policy(policy) if policy else None,
        "response_deadline": ticket.sla_response_deadline,
        "resolution_deadline": ticket.sla_resolution_deadline,
        "response_status": response_status,
        "resolution_status": resolution_status,
        "response_met_at": ticket.sla_response_met_at,
        "resolution_met_at": ticket.sla_resolution_met_at,
        "response_breached": ticket.sla_response_breached,
        "resolution_breached": ticket.sla_resolution_breached,
    }