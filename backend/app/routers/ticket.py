from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.connection import get_db

from app.schemas.ticket import (
    TicketCreate,
    TicketResponse,
    TicketUpdate,
)

from app.services.ticket_service import (
    create_ticket,
    get_all_tickets,
    get_ticket_by_id,
    update_ticket,
    delete_ticket,
)

from app.dependencies.roles import (
    require_admin,
    require_authenticated_user,
)

router = APIRouter(
    prefix="/tickets",
    tags=["Tickets"]
)


@router.post("/", response_model=TicketResponse)
def create_new_ticket(
    ticket: TicketCreate,
    db: Session = Depends(get_db),
    user=Depends(require_authenticated_user)
):
    return create_ticket(
        db,
        ticket,
        user["id"]
    )


@router.get("/", response_model=list[TicketResponse])
def get_tickets(
    db: Session = Depends(get_db),
    user=Depends(require_authenticated_user)
):
    return get_all_tickets(db)


@router.get("/{ticket_id}", response_model=TicketResponse)
def get_ticket(
    ticket_id: int,
    db: Session = Depends(get_db),
    user=Depends(require_authenticated_user)
):
    return get_ticket_by_id(db, ticket_id)


@router.put("/{ticket_id}", response_model=TicketResponse)
def update_existing_ticket(
    ticket_id: int,
    ticket: TicketUpdate,
    db: Session = Depends(get_db),
    user=Depends(require_authenticated_user)
):
    return update_ticket(
        db,
        ticket_id,
        ticket
    )


@router.delete("/{ticket_id}")
def delete_existing_ticket(
    ticket_id: int,
    db: Session = Depends(get_db),
    user=Depends(require_admin)
):
    return delete_ticket(
        db,
        ticket_id
    )