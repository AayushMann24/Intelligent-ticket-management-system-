from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.connection import get_db

from app.schemas.dashboard import DashboardSummary

from app.dependencies.roles import require_authenticated_user

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


# ===================================================
# Dashboard Summary
# ===================================================

@router.get(
    "/summary",
    response_model=DashboardSummary,
)
def dashboard_summary(
    db: Session = Depends(get_db),
    user=Depends(require_authenticated_user),
):

    return get_dashboard_summary(
        db,
        user,
    )


# ===================================================
# Recent Tickets
# ===================================================

@router.get("/recent-tickets")
def recent_tickets(
    db: Session = Depends(get_db),
    user=Depends(require_authenticated_user),
):

    tickets = get_recent_tickets(
        db,
        user,
    )

    return [

        {
            "id": ticket.id,
            "title": ticket.title,
            "status": ticket.status,
            "priority": ticket.priority,
            "assigned_to": (
                ticket.assignee.name
                if ticket.assignee
                else "Unassigned"
            ),
            "created_at": ticket.created_at,
        }

        for ticket in tickets

    ]


# ===================================================
# Trend
# ===================================================

@router.get("/trend")
def ticket_trend(
    db: Session = Depends(get_db),
    user=Depends(require_authenticated_user),
):

    return get_ticket_trend(
        db,
        user,
    )


# ===================================================
# Activity
# ===================================================

@router.get("/activity")
def activity(
    db: Session = Depends(get_db),
):

    return get_recent_activity(db)