from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models.ticket import Ticket
from app.models.user import User
from app.schemas.ticket import TicketUpdate
from app.constants.status import TICKET_STATUS
from agents.graph import graph

# ==========================================
# Create Ticket
# ==========================================
from langchain_core.messages import HumanMessage


def create_ticket(
    db: Session,
    ticket_data,
    user_id: int,
):

    # =====================================
    # Build AI State
    # =====================================

    state = {
        "messages": [
            HumanMessage(
                content=f"""
Title:
{ticket_data.title}

Description:
{ticket_data.description}
"""
            )
        ],

        "title": ticket_data.title,
        "description": ticket_data.description,

        "category": None,
        "subcategory": None,
        "keywords": [],

        "confidence": None,

        "priority": None,
        "priority_reason": None,

        "assigned_to": None,
        "assigned_name": None,
        "assignment_reason": None,

        "analytics": {},

        "final_response": None,

        "next": "",
    }

    # =====================================
    # Run Multi-Agent Workflow
    # =====================================

    ai_result = graph.invoke(state)

    print(ai_result)

    # =====================================
    # Save Ticket
    # =====================================

    new_ticket = Ticket(

    # =====================================
    # Ticket Details
    # =====================================

    title=ticket_data.title,

    description=ticket_data.description,

    # =====================================
    # AI Ticket Analysis
    # =====================================

    category=ai_result.get("category"),

    subcategory=ai_result.get("subcategory"),

    keywords=ai_result.get("keywords"),

    confidence=ai_result.get("confidence"),

    # =====================================
    # AI Priority
    # =====================================

    priority=(
        ai_result.get("priority")
        or ticket_data.priority
    ),

    priority_reason=ai_result.get(
        "priority_reason"
    ),

    # =====================================
    # AI Assignment
    # =====================================

    assigned_to=ai_result.get(
        "assigned_to"
    ),

    assignment_reason=ai_result.get(
        "assignment_reason"
    ),

    # =====================================
    # AI Status
    # =====================================

    ai_processed=True,

    # =====================================
    # Creator
    # =====================================

    created_by=user_id,
)

# ==========================================
# Get All Tickets
# ==========================================
from sqlalchemy.orm import joinedload

def get_all_tickets(db: Session):
    tickets = (
        db.query(Ticket)
        .options(joinedload(Ticket.assignee))
        .all()
    )

    result = []

    for ticket in tickets:
        result.append({
            "id": ticket.id,
            "title": ticket.title,
            "description": ticket.description,
            "priority": ticket.priority,
            "status": ticket.status,
            "created_by": ticket.created_by,
            "assigned_to": (
                ticket.assignee.name
                if ticket.assignee
                else "Unassigned"
            ),
            "created_at": ticket.created_at,
        })

    return result


# ==========================================
# Get Ticket By ID
# ==========================================
def get_ticket_by_id(db: Session, ticket_id: int):

    ticket = (
        db.query(Ticket)
        .filter(Ticket.id == ticket_id)
        .first()
    )

    if not ticket:
        raise HTTPException(
            status_code=404,
            detail="Ticket not found"
        )

    return ticket


# ==========================================
# Update Ticket
# ==========================================
def update_ticket(
    db: Session,
    ticket_id: int,
    ticket_data: TicketUpdate
):

    ticket = (
        db.query(Ticket)
        .filter(Ticket.id == ticket_id)
        .first()
    )

    if not ticket:
        raise HTTPException(
            status_code=404,
            detail="Ticket not found"
        )

    # Validate Status
    if ticket_data.status not in TICKET_STATUS:
        raise HTTPException(
            status_code=400,
            detail="Invalid ticket status"
        )

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
def delete_ticket(
    db: Session,
    ticket_id: int
):

    ticket = (
        db.query(Ticket)
        .filter(Ticket.id == ticket_id)
        .first()
    )

    if not ticket:
        raise HTTPException(
            status_code=404,
            detail="Ticket not found"
        )

    db.delete(ticket)
    db.commit()

    return {
        "message": "Ticket deleted successfully"
    }


# ==========================================
# Assign Ticket
# ==========================================
def assign_ticket(
    db: Session,
    ticket_id: int,
    assigned_to: int
):

    ticket = (
        db.query(Ticket)
        .filter(Ticket.id == ticket_id)
        .first()
    )

    if not ticket:
        raise HTTPException(
            status_code=404,
            detail="Ticket not found"
        )

    user = (
        db.query(User)
        .filter(User.id == assigned_to)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    if user.role not in ["Admin", "Technician"]:
        raise HTTPException(
            status_code=400,
            detail="Ticket can only be assigned to an Admin or Technician"
        )

    ticket.assigned_to = assigned_to

    # Automatically update status
    ticket.status = "Assigned"

    db.commit()
    db.refresh(ticket)

    return ticket


# ==========================================
# My Assigned Tickets
# ==========================================
def get_my_assigned_tickets(
    db: Session,
    user_id: int
):

    tickets = (
        db.query(Ticket)
        .filter(Ticket.assigned_to == user_id)
        .all()
    )

    return tickets


# ==========================================
# Update Ticket Status
# ==========================================
def update_ticket_status(
    db: Session,
    ticket_id: int,
    status: str
):
    ticket = (
        db.query(Ticket)
        .filter(Ticket.id == ticket_id)
        .first()
    )

    if not ticket:
        raise HTTPException(
            status_code=404,
            detail="Ticket not found"
        )

    # Validate status
    if status not in TICKET_STATUS:
        raise HTTPException(
            status_code=400,
            detail="Invalid ticket status"
        )

    ticket.status = status

    db.commit()
    db.refresh(ticket)

    return ticket