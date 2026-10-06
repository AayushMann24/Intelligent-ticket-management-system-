"""
Analytics Router (Phase 2E - Checkpoint 1)

Provides Admin-only analytics endpoints for ITSM reporting.
"""

from datetime import datetime
from typing import Optional, List
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.dependencies.roles import require_admin
from app.services.analytics_service import (
    get_ticket_overview_metrics,
    get_priority_analytics,
    get_category_analytics,
    get_ticket_type_analytics,
    get_sla_analytics,
    get_escalation_analytics,
    get_response_resolution_time_analytics,
    get_technician_workload_analytics,
    get_ticket_trends,
    get_filtered_ticket_analytics,
)
from app.schemas.dashboard import (
    TicketOverviewResponse,
    SLAAnalyticsResponse,
    EscalationAnalyticsResponse,
    ResponseResolutionTimeResponse,
    TechnicianWorkloadResponse,
    TrendResponse,
    FilteredTicketAnalyticsResponse,
    AnalyticsFilters,
    PriorityCountResponse,
    CategoryCountResponse,
    TicketTypeCountResponse,
)
from app.utils.logging_config import get_logger

logger = get_logger(__name__)

router = APIRouter(
    prefix="/analytics",
    tags=["Analytics"],
    dependencies=[Depends(require_admin)],  # Admin-only access
)


# ======================================================
# Overview Endpoints
# ======================================================

@router.get(
    "/overview",
    response_model=TicketOverviewResponse,
    summary="Get ticket overview metrics",
    description="Get high-level ticket counts including all statuses and key metrics.",
)
def analytics_overview(
    db: Session = Depends(get_db),
):
    """Get ticket overview metrics."""
    logger.info("Admin requested ticket overview metrics")
    return get_ticket_overview_metrics(db)


# ======================================================
# Priority Analytics
# ======================================================

@router.get(
    "/tickets/priority",
    response_model=List[PriorityCountResponse],
    summary="Get ticket counts by priority",
    description="Get ticket counts grouped by priority level.",
)
def analytics_priority(
    db: Session = Depends(get_db),
):
    """Get ticket counts by priority."""
    logger.info("Admin requested priority analytics")
    priority_counts = get_priority_analytics(db)
    return [{"priority": k, "count": v} for k, v in priority_counts.items()]


# ======================================================
# Category Analytics
# ======================================================

@router.get(
    "/tickets/category",
    response_model=List[CategoryCountResponse],
    summary="Get ticket counts by category",
    description="Get ticket counts grouped by category.",
)
def analytics_category(
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """Get ticket counts by category."""
    logger.info("Admin requested category analytics")
    return get_category_analytics(db, limit=limit)


# ======================================================
# Ticket Type Analytics
# ======================================================

@router.get(
    "/tickets/type",
    response_model=List[TicketTypeCountResponse],
    summary="Get ticket counts by ticket type",
    description="Get ticket counts grouped by ticket type.",
)
def analytics_ticket_type(
    db: Session = Depends(get_db),
):
    """Get ticket counts by ticket type."""
    logger.info("Admin requested ticket type analytics")
    return get_ticket_type_analytics(db)


# ======================================================
# SLA Analytics
# ======================================================

@router.get(
    "/sla",
    response_model=SLAAnalyticsResponse,
    summary="Get SLA analytics",
    description="Get comprehensive SLA metrics including compliance percentages.",
)
def analytics_sla(
    db: Session = Depends(get_db),
):
    """Get SLA analytics."""
    logger.info("Admin requested SLA analytics")
    return get_sla_analytics(db)


# ======================================================
# Escalation Analytics
# ======================================================

@router.get(
    "/escalations",
    response_model=EscalationAnalyticsResponse,
    summary="Get escalation analytics",
    description="Get comprehensive escalation metrics using EscalationRecord data.",
)
def analytics_escalations(
    db: Session = Depends(get_db),
):
    """Get escalation analytics."""
    logger.info("Admin requested escalation analytics")
    return get_escalation_analytics(db)


# ======================================================
# Response & Resolution Time
# ======================================================

@router.get(
    "/timing",
    response_model=ResponseResolutionTimeResponse,
    summary="Get response and resolution time analytics",
    description="Get average first response time and average resolution time.",
)
def analytics_timing(
    db: Session = Depends(get_db),
):
    """Get response and resolution time analytics."""
    logger.info("Admin requested timing analytics")
    return get_response_resolution_time_analytics(db)


# ======================================================
# Technician Workload
# ======================================================

@router.get(
    "/technicians",
    response_model=TechnicianWorkloadResponse,
    summary="Get technician workload analytics",
    description="Get workload metrics for all technicians and admins.",
)
def analytics_technicians(
    db: Session = Depends(get_db),
):
    """Get technician workload analytics."""
    logger.info("Admin requested technician workload analytics")
    workload = get_technician_workload_analytics(db)
    return {"workload": workload}


# ======================================================
# Trends / Time-Series
# ======================================================

@router.get(
    "/trends",
    response_model=TrendResponse,
    summary="Get ticket trends over time",
    description="Get time-series data for tickets created, resolved, SLA breaches, and escalations.",
)
def analytics_trends(
    start_date: Optional[datetime] = Query(None, description="Start date for trend data"),
    end_date: Optional[datetime] = Query(None, description="End date for trend data"),
    granularity: str = Query("daily", regex="^(daily|weekly|monthly)$"),
    db: Session = Depends(get_db),
):
    """Get ticket trends over time."""
    logger.info(
        f"Admin requested trends: start={start_date}, end={end_date}, granularity={granularity}"
    )
    return get_ticket_trends(
        db=db,
        start_date=start_date,
        end_date=end_date,
        granularity=granularity,
    )


# ======================================================
# Filtered Ticket Analytics
# ======================================================

@router.get(
    "/tickets/filtered",
    response_model=FilteredTicketAnalyticsResponse,
    summary="Get filtered ticket analytics",
    description="Get ticket analytics with optional filters for date range, priority, category, ticket type, and assignee.",
)
def analytics_tickets_filtered(
    start_date: Optional[datetime] = Query(None, description="Filter start date"),
    end_date: Optional[datetime] = Query(None, description="Filter end date"),
    priority: Optional[str] = Query(None, description="Filter by priority"),
    category: Optional[str] = Query(None, description="Filter by category"),
    ticket_type: Optional[str] = Query(None, description="Filter by ticket type"),
    assignee_id: Optional[int] = Query(None, description="Filter by assignee ID"),
    db: Session = Depends(get_db),
):
    """Get filtered ticket analytics."""
    logger.info(
        f"Admin requested filtered analytics: priority={priority}, category={category}, "
        f"ticket_type={ticket_type}, assignee_id={assignee_id}, "
        f"start_date={start_date}, end_date={end_date}"
    )
    return get_filtered_ticket_analytics(
        db=db,
        start_date=start_date,
        end_date=end_date,
        priority=priority,
        category=category,
        ticket_type=ticket_type,
        assignee_id=assignee_id,
    )


# ======================================================
# Comprehensive Dashboard Endpoint
# ======================================================

@router.get(
    "/dashboard",
    summary="Get all analytics data for dashboard",
    description="Get all analytics data in a single response for dashboard rendering.",
)
def analytics_dashboard(
    start_date: Optional[datetime] = Query(None, description="Filter start date for trends"),
    end_date: Optional[datetime] = Query(None, description="Filter end date for trends"),
    granularity: str = Query("daily", regex="^(daily|weekly|monthly)$"),
    db: Session = Depends(get_db),
):
    """
    Get comprehensive analytics data for dashboard rendering.
    Returns all metrics in a single response.
    """
    logger.info("Admin requested comprehensive dashboard analytics")
    
    return {
        "overview": get_ticket_overview_metrics(db),
        "priority": get_priority_analytics(db),
        "category": get_category_analytics(db),
        "ticket_type": get_ticket_type_analytics(db),
        "sla": get_sla_analytics(db),
        "escalations": get_escalation_analytics(db),
        "timing": get_response_resolution_time_analytics(db),
        "technicians": get_technician_workload_analytics(db),
        "trends": get_ticket_trends(
            db=db,
            start_date=start_date,
            end_date=end_date,
            granularity=granularity,
        ),
    }