from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.dependencies.auth import verify_token
from app.schemas.dashboard import DashboardSummary
from app.services.dashboard_service import get_dashboard_summary
from app.schemas.dashboard import (
    DashboardSummary,
    RecentTicketResponse,
    PrioritySummary,
)
from app.services.dashboard_service import (
    get_dashboard_summary,
    get_recent_tickets,
    get_priority_summary,
)

router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"]
)


@router.get(
    "/summary",
    response_model=DashboardSummary
)
def dashboard_summary(
    db: Session = Depends(get_db),
    user=Depends(verify_token)
):
    return get_dashboard_summary(db)

@router.get(
    "/recent-tickets",
    response_model=list[RecentTicketResponse]
)
def recent_tickets(
    db: Session = Depends(get_db),
    user=Depends(verify_token)
):
    return get_recent_tickets(db)

@router.get(
    "/priority-summary",
    response_model=PrioritySummary
)
def priority_summary(
    db: Session = Depends(get_db),
    user=Depends(verify_token)
):
    return get_priority_summary(db)