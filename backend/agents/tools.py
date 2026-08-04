
from langchain_core.tools import tool

from app.database.connection import SessionLocal
from app.schemas.ticket import TicketCreate
from app.services.ticket_service import (
    create_ticket,
    get_all_tickets,
    get_ticket_by_id,
    assign_ticket,
)

@tool
def get_all_tickets_tool():
    """
    Returns all tickets from the system.
    """

    db = SessionLocal()

    try:
        tickets = get_all_tickets(db)

        return [
            {
                "id": t.id,
                "title": t.title,
                "status": t.status,
                "priority": t.priority,
            }
            for t in tickets
        ]

    finally:
        db.close()

@tool
def get_ticket_by_id_tool(ticket_id: int):
    """
    Returns details of a ticket by its ID.
    """

    db = SessionLocal()

    try:

        ticket = get_ticket_by_id(
            db,
            ticket_id
        )

        return {
            "id": ticket.id,
            "title": ticket.title,
            "description": ticket.description,
            "priority": ticket.priority,
            "status": ticket.status,
            "created_by": ticket.created_by,
            "assigned_to": ticket.assigned_to,
        }

    finally:
        db.close()

from langchain.tools import tool


@tool
def assign_ticket_tool(
    ticket_id: int,
    assigned_to: int
):
    """
    Assign a ticket to a technician or admin.
    """

    db = SessionLocal()

    try:

        ticket = assign_ticket(
            db=db,
            ticket_id=ticket_id,
            assigned_to=assigned_to,
        )

        return {
            "message": "Ticket assigned successfully",
            "ticket_id": ticket.id,
            "assigned_to": ticket.assigned_to,
            "status": ticket.status,
        }

    finally:
        db.close()


@tool
def create_ticket_tool(
    title: str,
    description: str,
    priority: str,
):
    """
    Creates a new ticket.
    """

    db = SessionLocal()

    try:

        ticket = TicketCreate(
            title=title,
            description=description,
            priority=priority
        )

        new_ticket = create_ticket(
            db,
            ticket,
            1
        )

        return {
            "message": "Ticket created successfully",
            "ticket_id": new_ticket.id,
            "title": new_ticket.title
        }

    finally:
        db.close()