from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models.ticket import Ticket
from app.schemas.ticket import TicketUpdate


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