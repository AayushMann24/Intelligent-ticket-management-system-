from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.schemas.ticket_comment import (
    TicketHistoryResponse,
    TicketHistoryListResponse,
    TimelineResponse,
)
from app.services.ticket_history_service import (
    get_ticket_history,
    get_ticket_timeline,
)
from app.dependencies.roles import (
    require_authenticated_user,
)

router = APIRouter(
    tags=["Ticket History"],
)


@router.get(
    "/{ticket_id}/history",
    response_model=TicketHistoryListResponse,
)
def list_ticket_history(
    ticket_id: int,
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db),
    user=Depends(require_authenticated_user),
):
    return get_ticket_history(
        db=db,
        ticket_id=ticket_id,
        user_id=user["id"],
        user_role=user["role"],
        page=page,
        page_size=page_size,
    )


@router.get(
    "/{ticket_id}/timeline",
    response_model=TimelineResponse,
)
def get_ticket_timeline_endpoint(
    ticket_id: int,
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=200, description="Items per page"),
    db: Session = Depends(get_db),
    user=Depends(require_authenticated_user),
):
    return get_ticket_timeline(
        db=db,
        ticket_id=ticket_id,
        user_id=user["id"],
        user_role=user["role"],
        page=page,
        page_size=page_size,
    )