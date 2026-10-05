"""
SLA Escalation Service (Phase 2D-3B)

Handles automatic escalation when SLA breaches are detected:
- Rule matching based on event type, priority, ticket type, category
- Recipient resolution using existing user/role system
- Persistent idempotency via EscalationRecord
- Notification creation via existing NotificationService
- Email sending via EmailProvider abstraction
- History recording via existing ticket history service
"""

from datetime import datetime, timezone
from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc

from app.models.ticket import Ticket
from app.models.user import User
from app.models.escalation import EscalationRule, EscalationRecord, EscalationEventType
from app.models.notification import NotificationType
from app.models.ticket_comment import TicketHistory, HistoryEventType
from app.services.notification_service import create_notification
from app.services.ticket_history_service import record_history
from app.services.email_provider import send_email, EmailResult
from app.utils.logging_config import get_logger

logger = get_logger(__name__)


# ==========================================
# Rule Matching
# ==========================================

def get_matching_escalation_rules(
    db: Session,
    event_type: EscalationEventType,
    priority: str,
    ticket_type: str = "INCIDENT",
    category: Optional[str] = None,
) -> List[EscalationRule]:
    """
    Get all active escalation rules that match the given criteria.
    Returns rules ordered by precedence (most specific first).
    
    Specificity scoring:
    - event_type + priority + ticket_type + category (4) = most specific
    - event_type + priority + ticket_type (3)
    - event_type + priority + category (3)
    - event_type + priority (2) = least specific
    """
    query = db.query(EscalationRule).filter(
        EscalationRule.is_active == True,
        EscalationRule.event_type == event_type,
        EscalationRule.priority == priority,
    )

    # Filter by ticket_type if provided
    if ticket_type:
        query = query.filter(
            or_(
                EscalationRule.ticket_type == ticket_type,
                EscalationRule.ticket_type.is_(None),
            )
        )

    # Filter by category if provided
    if category:
        query = query.filter(
            or_(
                EscalationRule.category == category,
                EscalationRule.category.is_(None),
            )
        )

    rules = query.all()

    # Sort by specificity (most specific first)
    def specificity_score(rule: EscalationRule) -> int:
        score = 2  # event_type + priority always match
        if rule.ticket_type:
            score += 1
        if rule.category:
            score += 1
        return score

    rules.sort(key=specificity_score, reverse=True)
    return rules


def get_best_matching_rule(
    db: Session,
    event_type: EscalationEventType,
    priority: str,
    ticket_type: str = "INCIDENT",
    category: Optional[str] = None,
) -> Optional[EscalationRule]:
    """Get the single best matching escalation rule."""
    rules = get_matching_escalation_rules(db, event_type, priority, ticket_type, category)
    return rules[0] if rules else None


# ==========================================
# Recipient Resolution
# ==========================================

def resolve_escalation_recipient(
    db: Session,
    ticket: Ticket,
    rule: EscalationRule,
) -> Optional[User]:
    """
    Resolve the escalation recipient based on the rule's target_role.
    
    Priority order:
    1. If target_role is "Admin", find an Admin user
    2. If target_role is "Technician", find a Technician user
    3. Fallback to Admin if no Technician found
    
    Returns None if no suitable recipient found.
    """
    target_role = rule.target_role

    # Find users with the target role who are not deleted
    query = db.query(User).filter(
        User.role == target_role,
        User.is_deleted == False,
    )

    # For Technician, prefer one with relevant specialization if available
    if target_role == "Technician" and ticket.category:
        query = query.order_by(
            # Prioritize technicians with matching specialization
            User.specialization.is_(None).desc(),
        )

    # Get the first matching user (could be enhanced with round-robin, workload, etc.)
    recipient = query.first()

    # Fallback to Admin if no Technician found and rule requested Technician
    if not recipient and target_role == "Technician":
        logger.info(f"No active Technician found for escalation, falling back to Admin")
        recipient = db.query(User).filter(
            User.role == "Admin",
            User.is_deleted == False,
        ).first()

    return recipient


# ==========================================
# Idempotency Check
# ==========================================

def check_escalation_exists(
    db: Session,
    ticket_id: int,
    event_type: EscalationEventType,
    rule_id: Optional[int] = None,
) -> Optional[EscalationRecord]:
    """
    Check if an escalation record already exists for this ticket/event/rule combination.
    Returns the existing record if found, None otherwise.
    """
    query = db.query(EscalationRecord).filter(
        EscalationRecord.ticket_id == ticket_id,
        EscalationRecord.event_type == event_type,
    )

    if rule_id:
        query = query.filter(EscalationRecord.rule_id == rule_id)

    return query.first()


# ==========================================
# Notification Creation
# ==========================================

def create_escalation_notification(
    db: Session,
    ticket: Ticket,
    recipient: User,
    event_type: EscalationEventType,
    rule: EscalationRule,
) -> Optional[int]:
    """
    Create an escalation notification using the existing NotificationService.
    Returns the notification ID if successful, None otherwise.
    """
    # Check if notifications are enabled for this rule
    if not rule.notify_enabled:
        return None
    
    try:
        # Map escalation event type to notification type
        notification_type = NotificationType.TICKET_ESCALATED

        # Build descriptive title and message
        sla_type = "Response" if event_type == EscalationEventType.RESPONSE_BREACH else "Resolution"
        title = f"SLA {sla_type} Breach - Ticket Escalated"
        message = (
            f"Ticket #{ticket.id}: {ticket.title} has breached its {sla_type.lower()} SLA "
            f"and has been escalated to {recipient.name} ({recipient.role})."
        )

        notification = create_notification(
            db=db,
            recipient_id=recipient.id,
            notification_type=notification_type,
            title=title,
            message=message,
            ticket_id=ticket.id,
        )
        return notification.id
    except Exception as e:
        logger.error(f"Failed to create escalation notification: {e}")
        return None


# ==========================================
# Email Sending
# ==========================================

def build_escalation_email(
    ticket: Ticket,
    recipient: User,
    event_type: EscalationEventType,
    rule: EscalationRule,
) -> Tuple[str, str]:
    """
    Build email subject and body for escalation notification.
    Returns (subject, body_text).
    """
    sla_type = "Response" if event_type == EscalationEventType.RESPONSE_BREACH else "Resolution"
    priority = ticket.priority
    ticket_type = ticket.ticket_type
    assigned_tech = ticket.assignee.name if ticket.assignee else "Unassigned"
    creator = ticket.creator.name if ticket.creator else "Unknown"

    subject = f"[ITMS Escalation] SLA {sla_type} Breach - Ticket #{ticket.id}: {ticket.title}"

    body_text = f"""
SLA Escalation Notification
===========================

Ticket Details:
- Ticket ID: #{ticket.id}
- Title: {ticket.title}
- Priority: {priority}
- Type: {ticket_type}
- Category: {ticket.category or 'N/A'}
- Created by: {creator}
- Currently assigned to: {assigned_tech}

SLA Breach:
- SLA Type: {sla_type}
- Response Deadline: {ticket.sla_response_deadline.isoformat() if ticket.sla_response_deadline else 'N/A'}
- Resolution Deadline: {ticket.sla_resolution_deadline.isoformat() if ticket.sla_resolution_deadline else 'N/A'}
- Breach Reason: {sla_type} SLA deadline exceeded

Escalation Details:
- Escalated to: {recipient.name} ({recipient.email})
- Recipient Role: {recipient.role}
- Escalation Rule: {rule.name}
- Escalation Reason: Automatic escalation due to SLA {sla_type.lower()} breach

Action Required:
Please review this ticket and take appropriate action to address the SLA breach.

---
This is an automated message from the ITMS SLA Escalation System.
Ticket URL: /tickets/{ticket.id}
"""

    return subject, body_text.strip()


async def send_escalation_email(
    ticket: Ticket,
    recipient: User,
    event_type: EscalationEventType,
    rule: EscalationRule,
) -> EmailResult:
    """
    Send escalation email using the email provider abstraction.
    Email failure does NOT prevent escalation from being recorded.
    """
    # Check if emails are enabled for this rule
    if not rule.email_enabled:
        return EmailResult(success=False, error="Email notifications disabled for this rule")
    
    if not recipient.email:
        logger.warning(f"Recipient {recipient.id} has no email address, skipping email")
        return EmailResult(success=False, error="Recipient has no email address")

    subject, body_text = build_escalation_email(ticket, recipient, event_type, rule)

    try:
        result = await send_email(
            to=recipient.email,
            subject=subject,
            body_text=body_text,
            from_name="ITMS SLA Escalation",
        )
        return result
    except Exception as e:
        logger.error(f"Failed to send escalation email: {e}")
        return EmailResult(success=False, error=str(e))


# ==========================================
# History Recording
# ==========================================

def record_escalation_history(
    db: Session,
    ticket: Ticket,
    recipient: User,
    event_type: EscalationEventType,
    rule: EscalationRule,
    system_user: User,
) -> None:
    """
    Record escalation event in ticket history using existing history service.
    """
    sla_type = "Response" if event_type == EscalationEventType.RESPONSE_BREACH else "Resolution"

    record_history(
        db=db,
        ticket_id=ticket.id,
        actor_id=system_user.id,
        event_type=HistoryEventType.ESCALATED,
        old_value="",
        new_value=(
            f"Ticket escalated due to {sla_type} SLA breach. "
            f"Escalated to {recipient.name} ({recipient.role}) via rule: {rule.name}. "
            f"Reason: Automatic escalation due to SLA {sla_type.lower()} breach."
        ),
    )


# ==========================================
# Main Escalation Processing
# ==========================================

async def process_escalation(
    db: Session,
    ticket: Ticket,
    event_type: EscalationEventType,
) -> bool:
    """
    Process escalation for a ticket that has breached its SLA.
    This is called AFTER the breach has been recorded by the SLA breach service.
    
    Returns True if escalation was processed (or already existed), False if no rule matched.
    """
    # Find matching escalation rule
    rule = get_best_matching_rule(
        db=db,
        event_type=event_type,
        priority=ticket.priority,
        ticket_type=ticket.ticket_type,
        category=ticket.category,
    )

    if not rule:
        logger.info(
            f"No matching escalation rule for ticket {ticket.id} "
            f"(event_type={event_type.value}, priority={ticket.priority}, "
            f"ticket_type={ticket.ticket_type}, category={ticket.category})"
        )
        return False

    # Check idempotency - has this escalation already been processed?
    existing_record = check_escalation_exists(db, ticket.id, event_type, rule.id)
    if existing_record:
        logger.info(
            f"Escalation already exists for ticket {ticket.id} "
            f"(event_type={event_type.value}, rule={rule.name})"
        )
        return True

    # Resolve recipient
    recipient = resolve_escalation_recipient(db, ticket, rule)
    if not recipient:
        logger.warning(
            f"No suitable escalation recipient found for ticket {ticket.id} "
            f"(rule={rule.name}, target_role={rule.target_role})"
        )
        return False

    # Get system user for history
    system_user = db.query(User).filter(User.email == "system@itms.local").first()
    if not system_user:
        system_user = User(
            name="ITMS System",
            email="system@itms.local",
            password="",
            role="Admin",
            is_deleted=False,
        )
        db.add(system_user)
        db.flush()

    # Create escalation record (persistent idempotency)
    escalation_record = EscalationRecord(
        ticket_id=ticket.id,
        event_type=event_type,
        rule_id=rule.id,
        recipient_id=recipient.id,
        notification_created=False,
        email_sent=False,
        history_recorded=False,
    )
    db.add(escalation_record)
    db.flush()  # Get the ID

    # Create notification if enabled
    notification_id = None
    if rule.notify_enabled:
        notification_id = create_escalation_notification(db, ticket, recipient, event_type, rule)
        if notification_id:
            escalation_record.notification_created = True
            escalation_record.notification_id = notification_id

    # Send email if enabled
    if rule.email_enabled:
        email_result = await send_escalation_email(ticket, recipient, event_type, rule)
        escalation_record.email_sent = email_result.success
        if not email_result.success:
            escalation_record.email_error = email_result.error
            logger.warning(f"Escalation email failed for ticket {ticket.id}: {email_result.error}")

    # Record history
    record_escalation_history(db, ticket, recipient, event_type, rule, system_user)
    escalation_record.history_recorded = True

    # Update ticket escalation fields
    ticket.escalated_by = system_user.id
    ticket.escalated_to = recipient.id
    ticket.escalation_reason = f"Automatic escalation due to {('Response' if event_type == EscalationEventType.RESPONSE_BREACH else 'Resolution')} SLA breach"
    ticket.escalated_at = datetime.now(timezone.utc)
    ticket.updated_at = datetime.now(timezone.utc)

    db.commit()

    logger.info(
        f"Escalation processed for ticket {ticket.id}: "
        f"event={event_type.value}, rule={rule.name}, recipient={recipient.email}, "
        f"notification={notification_id}, email_sent={escalation_record.email_sent}"
    )

    return True


# ==========================================
# Escalation Rule CRUD
# ==========================================

def create_escalation_rule(
    db: Session,
    name: str,
    event_type: EscalationEventType,
    priority: str,
    target_role: str = "Admin",
    description: Optional[str] = None,
    ticket_type: Optional[str] = None,
    category: Optional[str] = None,
    notify_enabled: bool = True,
    email_enabled: bool = True,
    is_active: bool = True,
) -> EscalationRule:
    """Create a new escalation rule."""
    # Compute precedence based on specificity
    precedence = 2  # event_type + priority
    if ticket_type:
        precedence += 1
    if category:
        precedence += 1

    rule = EscalationRule(
        name=name,
        description=description,
        event_type=event_type,
        priority=priority,
        ticket_type=ticket_type,
        category=category,
        target_role=target_role,
        notify_enabled=notify_enabled,
        email_enabled=email_enabled,
        is_active=is_active,
        precedence=precedence,
    )
    db.add(rule)
    db.commit()
    db.refresh(rule)
    return rule


def get_escalation_rule(db: Session, rule_id: int) -> Optional[EscalationRule]:
    """Get escalation rule by ID."""
    return db.query(EscalationRule).filter(EscalationRule.id == rule_id).first()


def get_escalation_rule_by_name(db: Session, name: str) -> Optional[EscalationRule]:
    """Get escalation rule by name."""
    return db.query(EscalationRule).filter(EscalationRule.name == name).first()


def list_escalation_rules(
    db: Session,
    page: int = 1,
    page_size: int = 20,
    is_active: Optional[bool] = None,
    event_type: Optional[EscalationEventType] = None,
    priority: Optional[str] = None,
) -> dict:
    """List escalation rules with pagination."""
    query = db.query(EscalationRule)

    if is_active is not None:
        query = query.filter(EscalationRule.is_active == is_active)

    if event_type:
        query = query.filter(EscalationRule.event_type == event_type)

    if priority:
        query = query.filter(EscalationRule.priority == priority)

    total = query.count()

    query = query.order_by(desc(EscalationRule.precedence), EscalationRule.name)
    offset = (page - 1) * page_size
    rules = query.offset(offset).limit(page_size).all()

    total_pages = (total + page_size - 1) // page_size

    return {
        "items": rules,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
    }


def update_escalation_rule(
    db: Session,
    rule_id: int,
    **kwargs,
) -> Optional[EscalationRule]:
    """Update escalation rule."""
    rule = get_escalation_rule(db, rule_id)
    if not rule:
        return None

    # Update precedence if specificity fields changed
    if any(k in kwargs for k in ["ticket_type", "category"]):
        precedence = 2
        ticket_type = kwargs.get("ticket_type", rule.ticket_type)
        category = kwargs.get("category", rule.category)
        if ticket_type:
            precedence += 1
        if category:
            precedence += 1
        kwargs["precedence"] = precedence

    for key, value in kwargs.items():
        if hasattr(rule, key) and key != "id":
            setattr(rule, key, value)

    rule.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(rule)
    return rule


def delete_escalation_rule(db: Session, rule_id: int) -> bool:
    """Delete (deactivate) escalation rule."""
    rule = get_escalation_rule(db, rule_id)
    if not rule:
        return False

    # Soft delete by deactivating
    rule.is_active = False
    rule.updated_at = datetime.now(timezone.utc)
    db.commit()
    return True