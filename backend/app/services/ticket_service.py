from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models.ticket import Ticket
from app.models.user import User
from app.schemas.ticket import TicketUpdate
from app.constants.status import TICKET_STATUS


# ==========================================
# Create Ticket
# ==========================================
def create_ticket(db: Session, ticket_data, user_id: int):

    new_ticket = Ticket(
        title=ticket_data.title,
        description=ticket_data.description,
        priority=ticket_data.priority,
        created_by=user_id
    )

    db.add(new_ticket)
    db.commit()
    db.refresh(new_ticket)

    return new_ticket


# ==========================================
# Get All Tickets
# ==========================================
def get_all_tickets(db: Session):
    return db.query(Ticket).all()


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
    class TicketStatusUpdate(BaseModel):
        status: str

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