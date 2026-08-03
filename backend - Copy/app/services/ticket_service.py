from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models.ticket import Ticket
from app.schemas.ticket import TicketUpdate
from app.models.user import User

def create_ticket(db: Session, ticket_data, user_id: int):

    print("Inside create_ticket()")
    print("User ID:", user_id)

    new_ticket = Ticket(
        title=ticket_data.title,
        description=ticket_data.description,
        priority=ticket_data.priority,
        created_by=user_id
    )

    print("Ticket object created")

    db.add(new_ticket)

    print("Added to session")

    db.commit()

    print("Committed")

    db.refresh(new_ticket)

    print("Refreshed")

    return new_ticket


def get_all_tickets(db: Session):
    tickets = db.query(Ticket).all()
    return tickets

    db.add(new_ticket)
    db.commit()
    db.refresh(new_ticket)

    return new_ticket
from fastapi import HTTPException

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
from fastapi import HTTPException

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

    ticket.title = ticket_data.title
    ticket.description = ticket_data.description
    ticket.priority = ticket_data.priority
    ticket.status = ticket_data.status

    db.commit()

    db.refresh(ticket)

    return ticket

from fastapi import HTTPException

def delete_ticket(db: Session, ticket_id: int):

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

from fastapi import HTTPException

def assign_ticket(
    db: Session,
    ticket_id: int,
    assigned_to: int
):
    # Find the ticket
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

    # Find the user
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

    # Only Admin or Technician can be assigned tickets
    if user.role not in ["Technician", "Admin"]:
        raise HTTPException(
            status_code=400,
            detail="Ticket can only be assigned to a Technician or Admin"
        )

    # Assign the ticket
    ticket.assigned_to = assigned_to

    db.commit()

    db.refresh(ticket)

    return ticket

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
    