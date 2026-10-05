from datetime import datetime, timezone, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from app.models.ticket import Ticket
from app.models.ticket_comment import TicketHistory, HistoryEventType
from app.models.user import User
from app.services.ticket_history_service import record_history
from app.services.notification_service import create_notification
from app.models.notification import NotificationType


def get_system_user(db: Session) -> User:
    """Get or create the system user for background tasks."""
    system_user = db.query(User).filter(User.email == "system@itms.local").first()
    if not system_user:
        system_user = User(
            name="ITMS System",
            email="system@itms.local",
            password="",  # Not used for system user
            role="Admin",
            is_deleted=False,
        )
        db.add(system_user)
        db.commit()
        db.refresh(system_user)
    return system_user


# ==========================================
# SLA Breach Detection Service (Phase 2C-2)
# ==========================================

def find_candidate_tickets_for_response_breach(db: Session) -> list[Ticket]:
    """
    Find tickets that may have a response SLA breach.
    Uses database-side filtering for efficiency.
    """
    now = datetime.now(timezone.utc)
    return db.query(Ticket).filter(
        Ticket.is_deleted == False,
        Ticket.sla_policy_id.isnot(None),
        Ticket.sla_response_deadline.isnot(None),
        Ticket.sla_response_deadline <= now,
        Ticket.sla_response_met_at.is_(None),  # Response not yet met
        Ticket.sla_response_breached == False,  # Breach not yet recorded
        # Exclude resolved/closed tickets - their response window is irrelevant after resolution
        Ticket.status.notin_(["Resolved", "Closed"]),
    ).all()


def find_candidate_tickets_for_resolution_breach(db: Session) -> list[Ticket]:
    """
    Find tickets that may have a resolution SLA breach.
    Uses database-side filtering for efficiency.
    """
    now = datetime.now(timezone.utc)
    return db.query(Ticket).filter(
        Ticket.is_deleted == False,
        Ticket.sla_policy_id.isnot(None),
        Ticket.sla_resolution_deadline.isnot(None),
        Ticket.sla_resolution_deadline <= now,
        Ticket.sla_resolution_met_at.is_(None),  # Resolution not yet met
        Ticket.sla_resolution_breached == False,  # Breach not yet recorded
        # Exclude closed tickets - resolution SLA is moot after closure
        # But include Resolved tickets that were resolved AFTER the deadline
        # (the mark_resolution_sla_met would have set the breach flag then)
        Ticket.status != "Closed",
    ).all()


def process_response_breach(db: Session, ticket: Ticket) -> bool:
    """
    Process a response SLA breach for a single ticket.
    Returns True if breach was processed, False if already breached/no action needed.
    Idempotent: safe to call multiple times.
    """
    # Double-check conditions (race condition protection)
    if (
        not ticket.sla_policy_id
        or not ticket.sla_response_deadline
        or ticket.sla_response_met_at is not None
        or ticket.sla_response_breached
        or ticket.status in ["Resolved", "Closed"]
    ):
        return False

    now = datetime.now(timezone.utc)
    deadline = ticket.sla_response_deadline
    if deadline.tzinfo is None:
        deadline = deadline.replace(tzinfo=timezone.utc)
    if now < deadline:
        return False

    # Mark breach
    ticket.sla_response_breached = True
    ticket.updated_at = now

    # Get system user for history
    system_user = get_system_user(db)

    # Record history event
    record_history(
        db=db,
        ticket_id=ticket.id,
        actor_id=system_user.id,
        event_type=HistoryEventType.SLA_RESPONSE_BREACHED,
        old_value="",
        new_value=f"Response SLA breached. Deadline was {ticket.sla_response_deadline.isoformat()}",
    )

    # Create notification for assigned user (and creator if different)
    if ticket.assigned_to:
        create_notification(
            db=db,
            recipient_id=ticket.assigned_to,
            notification_type=NotificationType.SLA_RESPONSE_BREACHED,
            title="SLA Response Breached",
            message=f"Ticket #{ticket.id}: {ticket.title} has breached its response SLA deadline.",
            ticket_id=ticket.id,
        )
    # Also notify ticket creator if different from assignee
    elif ticket.created_by:
        create_notification(
            db=db,
            recipient_id=ticket.created_by,
            notification_type=NotificationType.SLA_RESPONSE_BREACHED,
            title="SLA Response Breached",
            message=f"Ticket #{ticket.id}: {ticket.title} has breached its response SLA deadline.",
            ticket_id=ticket.id,
        )

    db.commit()
    return True


def process_resolution_breach(db: Session, ticket: Ticket) -> bool:
    """
    Process a resolution SLA breach for a single ticket.
    Returns True if breach was processed, False if already breached/no action needed.
    Idempotent: safe to call multiple times.
    """
    # Double-check conditions (race condition protection)
    if (
        not ticket.sla_policy_id
        or not ticket.sla_resolution_deadline
        or ticket.sla_resolution_met_at is not None
        or ticket.sla_resolution_breached
        or ticket.status == "Closed"
    ):
        return False

    # If ticket is Resolved but resolution_met_at is None, it was resolved after deadline
    # and mark_resolution_sla_met should have handled it. But we handle it here too.
    now = datetime.now(timezone.utc)
    deadline = ticket.sla_resolution_deadline
    if deadline.tzinfo is None:
        deadline = deadline.replace(tzinfo=timezone.utc)
    if now < deadline:
        return False

    # Mark breach
    ticket.sla_resolution_breached = True
    ticket.updated_at = now

    # Get system user for history
    system_user = get_system_user(db)

    # Record history event
    record_history(
        db=db,
        ticket_id=ticket.id,
        actor_id=system_user.id,
        event_type=HistoryEventType.SLA_RESOLUTION_BREACHED,
        old_value="",
        new_value=f"Resolution SLA breached. Deadline was {ticket.sla_resolution_deadline.isoformat()}",
    )

    # Create notification for assigned user (and creator if different)
    if ticket.assigned_to:
        create_notification(
            db=db,
            recipient_id=ticket.assigned_to,
            notification_type=NotificationType.SLA_RESOLUTION_BREACHED,
            title="SLA Resolution Breached",
            message=f"Ticket #{ticket.id}: {ticket.title} has breached its resolution SLA deadline.",
            ticket_id=ticket.id,
        )
    # Also notify ticket creator if different from assignee
    elif ticket.created_by:
        create_notification(
            db=db,
            recipient_id=ticket.created_by,
            notification_type=NotificationType.SLA_RESOLUTION_BREACHED,
            title="SLA Resolution Breached",
            message=f"Ticket #{ticket.id}: {ticket.title} has breached its resolution SLA deadline.",
            ticket_id=ticket.id,
        )

    db.commit()
    return True


def check_all_sla_breaches(db: Session) -> dict:
    """
    Main entry point for SLA breach checking.
    Returns summary of actions taken.
    """
    results = {
        "response_breaches_processed": 0,
        "resolution_breaches_processed": 0,
        "response_candidates": 0,
        "resolution_candidates": 0,
        "errors": [],
    }

    # Process response SLA breaches
    try:
        response_candidates = find_candidate_tickets_for_response_breach(db)
        results["response_candidates"] = len(response_candidates)

        for ticket in response_candidates:
            try:
                if process_response_breach(db, ticket):
                    results["response_breaches_processed"] += 1
            except Exception as e:
                error_msg = f"Failed to process response breach for ticket {ticket.id}: {e}"
                results["errors"].append(error_msg)
                # Continue processing other tickets
    except Exception as e:
        results["errors"].append(f"Error querying response breach candidates: {e}")

    # Process resolution SLA breaches
    try:
        resolution_candidates = find_candidate_tickets_for_resolution_breach(db)
        results["resolution_candidates"] = len(resolution_candidates)

        for ticket in resolution_candidates:
            try:
                if process_resolution_breach(db, ticket):
                    results["resolution_breaches_processed"] += 1
            except Exception as e:
                error_msg = f"Failed to process resolution breach for ticket {ticket.id}: {e}"
                results["errors"].append(error_msg)
                # Continue processing other tickets
    except Exception as e:
        results["errors"].append(f"Error querying resolution breach candidates: {e}")

    return results


# ==========================================
# Warning Threshold Helpers (for future use)
# ==========================================

def get_tickets_in_warning_window(db: Session) -> list[tuple[Ticket, str]]:
    """
    Get tickets that are in their warning window (approaching deadline).
    Returns list of (ticket, warning_type) where warning_type is 'response' or 'resolution'.
    """
    now = datetime.now(timezone.utc)
    warning_tickets = []

    # Get all active tickets with SLA
    tickets = db.query(Ticket).filter(
        Ticket.is_deleted == False,
        Ticket.sla_policy_id.isnot(None),
    ).all()

    for ticket in tickets:
        if ticket.status in ["Closed"]:
            continue

        # Check response warning
        if (
            ticket.sla_response_deadline
            and ticket.sla_response_met_at is None
            and not ticket.sla_response_breached
            and ticket.status not in ["Resolved", "Closed"]
        ):
            policy = ticket.sla_policy
            if policy and policy.warning_threshold_percentage:
                deadline = ticket.sla_response_deadline
                total_minutes = policy.response_time_minutes
                warning_minutes = int(total_minutes * policy.warning_threshold_percentage / 100)
                warning_start = deadline - timedelta(minutes=warning_minutes)
                
                if now >= warning_start and now < deadline:
                    warning_tickets.append((ticket, "response"))

        # Check resolution warning
        if (
            ticket.sla_resolution_deadline
            and ticket.sla_resolution_met_at is None
            and not ticket.sla_resolution_breached
            and ticket.status != "Closed"
        ):
            policy = ticket.sla_policy
            if policy and policy.warning_threshold_percentage:
                deadline = ticket.sla_resolution_deadline
                total_minutes = policy.resolution_time_minutes
                warning_minutes = int(total_minutes * policy.warning_threshold_percentage / 100)
                warning_start = deadline - timedelta(minutes=warning_minutes)
                
                if now >= warning_start and now < deadline:
                    warning_tickets.append((ticket, "resolution"))

    return warning_tickets


# Need to import timedelta for warning calculation
from datetime import timedelta