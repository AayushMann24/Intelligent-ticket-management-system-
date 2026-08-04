from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.schemas.dashboard import DashboardSummary

from app.services.dashboard_service import (
    get_dashboard_summary,
    get_recent_tickets,
    get_ticket_trend,
)

from app.services.activity_service import (
    get_recent_activity,
)

router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"],
)


@router.get(
    "/summary",
    response_model=DashboardSummary,
)
def dashboard_summary(
    db: Session = Depends(get_db),
):
    return get_dashboard_summary(db)


@router.get("/recent-tickets")
def recent_tickets(
    db: Session = Depends(get_db),
):
    tickets = get_recent_tickets(db)

    return [
        {
            "id": ticket.id,
            "title": ticket.title,
            "status": ticket.status,
            "priority": ticket.priority,
            "assigned_to": ticket.assigned_to,
        }
        for ticket in tickets
    ]


@router.get("/trend")
def ticket_trend(
    db: Session = Depends(get_db),
):
    return get_ticket_trend(db)


@router.get("/activity")
def activity(
    db: Session = Depends(get_db),
):
    return get_recent_activity(db)