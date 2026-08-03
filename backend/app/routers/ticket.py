from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.connection import get_db

from app.schemas.ticket import (
    TicketCreate,
    TicketResponse,
    TicketUpdate,
    TicketAssign,
    TicketStatusUpdate,
)

from app.services.ticket_service import (
    create_ticket,
    get_all_tickets,
    get_ticket_by_id,
    update_ticket,
    delete_ticket,
    assign_ticket,
    get_my_assigned_tickets,
    update_ticket_status,   
)

from app.dependencies.roles import (
    require_admin,
    require_authenticated_user,
    require_technician,
    require_admin_or_technician
)
router = APIRouter(
    prefix="/tickets",
    tags=["Tickets"]
)


# ==================================================
# Create Ticket
# ==================================================
@router.post("/", response_model=TicketResponse)
def create_new_ticket(
    ticket: TicketCreate,
    db: Session = Depends(get_db),
    user=Depends(require_authenticated_user)
):
    print("Router reached")
    print("Authenticated user:", user)

    result = create_ticket(
        db=db,
        ticket_data=ticket,
        user_id=user["id"]
    )

    print("Ticket created successfully")

    return result


# ==================================================
# Get All Tickets
# ==================================================
@router.get("/", response_model=list[TicketResponse])
def get_tickets(
    db: Session = Depends(get_db),
    user=Depends(require_authenticated_user)
):
    return get_all_tickets(db)


# ==================================================
# Get My Assigned Tickets
# ==================================================
@router.get(
    "/my-assigned",
    response_model=list[TicketResponse]
)
def get_my_tickets(
    db: Session = Depends(get_db),
    user=Depends(require_technician)
):
    return get_my_assigned_tickets(
        db=db,
        user_id=user["id"]
    )


# ==================================================
# Get Ticket By ID
# ==================================================
@router.get("/{ticket_id}", response_model=TicketResponse)
def get_ticket(
    ticket_id: int,
    db: Session = Depends(get_db),
    user=Depends(require_authenticated_user)
):
    return get_ticket_by_id(
        db=db,
        ticket_id=ticket_id
    )


# ==================================================
# Update Ticket
# ==================================================
@router.put("/{ticket_id}", response_model=TicketResponse)
def update_existing_ticket(
    ticket_id: int,
    ticket: TicketUpdate,
    db: Session = Depends(get_db),
    user=Depends(require_authenticated_user)
):
    return update_ticket(
        db=db,
        ticket_id=ticket_id,
        ticket_data=ticket
    )


# ==================================================
# Assign Ticket
# ==================================================
@router.put(
    "/{ticket_id}/assign",
    response_model=TicketResponse
)
def assign_ticket_to_user(
    ticket_id: int,
    ticket: TicketAssign,
    db: Session = Depends(get_db),
    user=Depends(require_admin)
):
    return assign_ticket(
        db=db,
        ticket_id=ticket_id,
        assigned_to=ticket.assigned_to
    )

# ==================================================
# Ticket
# ==================================================
@router.patch(
    "/{ticket_id}/status",
    response_model=TicketResponse
)
def update_status(
    ticket_id: int,
    status_data: TicketStatusUpdate,
    db: Session = Depends(get_db),
    user=Depends(require_admin_or_technician)
):
    return update_ticket_status(
        db,
        ticket_id,
        status_data.status
    )

# ==================================================
# Delete Ticket
# ==================================================
@router.delete("/{ticket_id}")
def delete_existing_ticket(
    ticket_id: int,
    db: Session = Depends(get_db),
    user=Depends(require_admin)
):
    return delete_ticket(
        db=db,
        ticket_id=ticket_id
    )