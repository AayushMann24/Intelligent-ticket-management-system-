from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload
from fastapi import HTTPException


from app.models.ticket import Ticket
from app.models.user import User
from app.schemas.ticket import TicketUpdate
from app.constants.status import TICKET_STATUS
from app.services.ai_service import AIService


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
        db.query(
            Ticket.assigned_to,
            func.count(Ticket.id).label("workload")
        )
        .filter(Ticket.status.in_(["Open", "Assigned"]))
        .group_by(Ticket.assigned_to)
        .subquery()
    )

    # Query users with outer join to include technicians with 0 workload
    technicians = (
        db.query(User, func.coalesce(workload_subquery.c.workload, 0).label("workload"))
        .outerjoin(workload_subquery, User.id == workload_subquery.c.assigned_to)
        .filter(User.role.in_(["Admin", "Technician"]))
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
    """
    return Ticket(
        title=ticket_data.title,
        description=ticket_data.description,
        category=ai_result.get("category"),
        subcategory=ai_result.get("subcategory"),
        keywords=ai_result.get("keywords"),
        confidence=ai_result.get("confidence"),
        priority=ai_result.get("priority") or ticket_data.priority,
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

    ai_result = AIService.analyze_ticket(
        title=ticket_data.title,
        description=ticket_data.description,
        technicians=technicians,
)


    # Instantiate via helper function
    new_ticket = build_ticket(ticket_data, ai_result, user_id)

    db.add(new_ticket)
    db.commit()
    db.refresh(new_ticket)

    return new_ticket


# ==========================================
# Get All Tickets
# ==========================================
def get_all_tickets(db: Session):
    tickets = (
        db.query(Ticket)
        .options(joinedload(Ticket.assignee))
        .all()
    )

    return [
        {
            "id": ticket.id,
            "title": ticket.title,
            "description": ticket.description,

            # AI Analysis
            "category": ticket.category,
            "subcategory": ticket.subcategory,
            "keywords": ticket.keywords,
            "confidence": ticket.confidence,

            # AI Priority
            "priority": ticket.priority,
            "priority_reason": ticket.priority_reason,

            # Status
            "status": ticket.status,

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

            # AI Metadata
            "ai_processed": ticket.ai_processed,

            # Timestamp
            "created_at": ticket.created_at,
        }
        for ticket in tickets
    ]

# ==========================================
# Get Ticket By ID
# ==========================================
def get_ticket_by_id(db: Session, ticket_id: int):
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()

    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    return ticket


# ==========================================
# Update Ticket
# ==========================================
def update_ticket(db: Session, ticket_id: int, ticket_data: TicketUpdate):
    ticket = get_ticket_by_id(db, ticket_id)

    if ticket_data.status not in TICKET_STATUS:
        raise HTTPException(status_code=400, detail="Invalid ticket status")

    ticket.title = ticket_data.title
    ticket.description = ticket_data.description
    ticket.priority = ticket_data.priority
    ticket.status = ticket_data.status

    db.commit()
    db.refresh(ticket)

    return ticket


# ==========================================
# Delete Ticket
# ==========================================
def delete_ticket(db: Session, ticket_id: int):
    ticket = get_ticket_by_id(db, ticket_id)

    db.delete(ticket)
    db.commit()

    return {"message": "Ticket deleted successfully"}


# ==========================================
# Assign Ticket
# ==========================================
def assign_ticket(db: Session, ticket_id: int, assigned_to: int):
    ticket = get_ticket_by_id(db, ticket_id)

    user = db.query(User).filter(User.id == assigned_to).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.role not in ["Admin", "Technician"]:
        raise HTTPException(
            status_code=400,
            detail="Ticket can only be assigned to an Admin or Technician"
        )

    ticket.assigned_to = assigned_to
    ticket.status = "Assigned"

    db.commit()
    db.refresh(ticket)

    return ticket


# ==========================================
# My Assigned Tickets
# ==========================================
def get_my_assigned_tickets(db: Session, user_id: int):
    return db.query(Ticket).filter(Ticket.assigned_to == user_id).all()


# ==========================================
# Update Ticket Status
# ==========================================
def update_ticket_status(db: Session, ticket_id: int, status: str):
    ticket = get_ticket_by_id(db, ticket_id)

    if status not in TICKET_STATUS:
        raise HTTPException(status_code=400, detail="Invalid ticket status")

    ticket.status = status

    db.commit()
    db.refresh(ticket)

    return ticket