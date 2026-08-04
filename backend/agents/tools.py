from langchain_core.tools import tool

from app.database.connection import SessionLocal

from app.schemas.ticket import (
    TicketCreate,
    TicketUpdate,
)

from app.services.ticket_service import (
    create_ticket,
    get_all_tickets,
    get_ticket_by_id,
    assign_ticket,
    update_ticket,
    update_ticket_status,
    delete_ticket,
)


# ==========================================
# Create Ticket
# ==========================================
@tool
def create_ticket_tool(
    title: str,
    description: str,
    priority: str,
):
    """
    Create a new ticket.
    """

    db = SessionLocal()

    try:

        ticket = TicketCreate(
            title=title,
            description=description,
            priority=priority,
        )

        new_ticket = create_ticket(
            db=db,
            ticket_data=ticket,
            user_id=1,      # Replace later with logged-in user
        )

        return {
            "message": "Ticket created successfully",
            "ticket_id": new_ticket.id,
            "title": new_ticket.title,
        }

    finally:
        db.close()


# ==========================================
# Get All Tickets
# ==========================================
@tool
def get_all_tickets_tool():
    """
    Return all tickets.
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


# ==========================================
# Get Ticket By ID
# ==========================================
@tool
def get_ticket_by_id_tool(ticket_id: int):
    """
    Return a ticket by its ID.
    """

    db = SessionLocal()

    try:

        ticket = get_ticket_by_id(
            db,
            ticket_id,
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


# ==========================================
# Assign Ticket
# ==========================================
@tool
def assign_ticket_tool(
    ticket_id: int,
    assigned_to: int,
):
    """
    Assign a ticket to a technician/admin.
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


# ==========================================
# Update Ticket
# ==========================================
@tool
def update_ticket_tool(
    ticket_id: int,
    title: str,
    description: str,
    priority: str,
    status: str,
):
    """
    Update a ticket.
    """

    db = SessionLocal()

    try:

        ticket_data = TicketUpdate(
            title=title,
            description=description,
            priority=priority,
            status=status,
        )

        ticket = update_ticket(
            db=db,
            ticket_id=ticket_id,
            ticket_data=ticket_data,
        )

        return {
            "message": "Ticket updated successfully",
            "ticket_id": ticket.id,
            "title": ticket.title,
            "priority": ticket.priority,
            "status": ticket.status,
        }

    finally:
        db.close()


# ==========================================
# Update Ticket Status
# ==========================================
@tool
def update_ticket_status_tool(
    ticket_id: int,
    status: str,
):
    """
    Update only the ticket status.
    """

    db = SessionLocal()

    try:

        ticket = update_ticket_status(
            db=db,
            ticket_id=ticket_id,
            status=status,
        )

        return {
            "message": "Ticket status updated successfully",
            "ticket_id": ticket.id,
            "status": ticket.status,
        }

    finally:
        db.close()


# ==========================================
# Delete Ticket
# ==========================================
@tool
def delete_ticket_tool(ticket_id: int):
    """
    Delete a ticket.
    """

    db = SessionLocal()

    try:

        result = delete_ticket(
            db=db,
            ticket_id=ticket_id,
        )

        return result

    finally:
        db.close()