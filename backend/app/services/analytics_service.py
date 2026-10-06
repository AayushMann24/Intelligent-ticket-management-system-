"""
Analytics Service (Phase 2E - Checkpoint 1)

Provides aggregated operational metrics for Admin users.
All metrics use efficient SQL aggregation queries.
"""

from datetime import datetime, timezone, timedelta
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, case, extract
from sqlalchemy.sql import label

from app.models.ticket import Ticket, SLAPolicy
from app.models.user import User
from app.models.escalation import EscalationRecord, EscalationEventType
from app.models.ticket_comment import TicketHistory, HistoryEventType


def _base_ticket_query(db: Session):
    """Base query that excludes soft-deleted tickets."""
    return db.query(Ticket).filter(Ticket.is_deleted == False)


# ======================================================
# Overview Metrics
# ======================================================

def get_ticket_overview_metrics(db: Session) -> Dict[str, int]:
    """
    Get high-level ticket overview metrics.
    Returns counts for all statuses and key metrics.
    """
    base_query = _base_ticket_query(db)
    
    # Single query with conditional aggregation
    result = base_query.with_entities(
        func.count(Ticket.id).label("total_tickets"),
        func.sum(case((Ticket.status == "Open", 1), else_=0)).label("open_tickets"),
        func.sum(case((Ticket.status == "Assigned", 1), else_=0)).label("assigned_tickets"),
        func.sum(case((Ticket.status == "Pending", 1), else_=0)).label("pending_tickets"),
        func.sum(case((Ticket.status == "Resolved", 1), else_=0)).label("resolved_tickets"),
        func.sum(case((Ticket.status == "Closed", 1), else_=0)).label("closed_tickets"),
        func.sum(case((Ticket.assigned_to.is_(None), 1), else_=0)).label("unassigned_tickets"),
        func.sum(case((Ticket.escalated_to.isnot(None), 1), else_=0)).label("escalated_tickets"),
    ).first()
    
    return {
        "total_tickets": result.total_tickets or 0,
        "open_tickets": result.open_tickets or 0,
        "assigned_tickets": result.assigned_tickets or 0,
        "pending_tickets": result.pending_tickets or 0,
        "resolved_tickets": result.resolved_tickets or 0,
        "closed_tickets": result.closed_tickets or 0,
        "unassigned_tickets": result.unassigned_tickets or 0,
        "escalated_tickets": result.escalated_tickets or 0,
    }


# ======================================================
# Priority Analytics
# ======================================================

def get_priority_analytics(db: Session) -> Dict[str, int]:
    """
    Get ticket counts grouped by priority.
    Returns all priority levels with zero counts where no tickets exist.
    """
    base_query = _base_ticket_query(db)
    
    # Get all possible priority values from the model
    priorities = ["Critical", "High", "Medium", "Low"]
    
    result = base_query.with_entities(
        Ticket.priority,
        func.count(Ticket.id).label("count"),
    ).group_by(Ticket.priority).all()
    
    # Build dict with all priorities, defaulting to 0
    priority_counts = {p: 0 for p in priorities}
    for row in result:
        priority_counts[row.priority] = row.count
    
    return priority_counts


# ======================================================
# Category & Type Analytics
# ======================================================

def get_category_analytics(db: Session, limit: int = 20) -> List[Dict[str, Any]]:
    """
    Get ticket counts grouped by category.
    Returns list sorted by count descending.
    """
    base_query = _base_ticket_query(db)
    
    result = base_query.with_entities(
        Ticket.category,
        func.count(Ticket.id).label("count"),
    ).filter(
        Ticket.category.isnot(None)
    ).group_by(Ticket.category).order_by(
        func.count(Ticket.id).desc()
    ).limit(limit).all()
    
    return [
        {"category": row.category, "count": row.count}
        for row in result
    ]


def get_ticket_type_analytics(db: Session) -> List[Dict[str, int]]:
    """
    Get ticket counts grouped by ticket type.
    """
    base_query = _base_ticket_query(db)
    
    result = base_query.with_entities(
        Ticket.ticket_type,
        func.count(Ticket.id).label("count"),
    ).group_by(Ticket.ticket_type).all()
    
    return [
        {"ticket_type": row.ticket_type, "count": row.count}
        for row in result
    ]


# ======================================================
# SLA Analytics
# ======================================================

def get_sla_analytics(db: Session) -> Dict[str, Any]:
    """
    Get comprehensive SLA analytics.
    Uses existing SLA fields - does not recalculate deadlines.
    """
    base_query = _base_ticket_query(db)
    
    # Response SLA metrics
    response_sla_query = base_query.filter(Ticket.sla_policy_id.isnot(None))
    
    response_total = response_sla_query.filter(
        Ticket.sla_response_deadline.isnot(None)
    ).count()
    
    response_met = response_sla_query.filter(
        Ticket.sla_response_met_at.isnot(None)
    ).count()
    
    response_breached = response_sla_query.filter(
        Ticket.sla_response_breached == True
    ).count()
    
    response_compliance = (
        (response_met / response_total * 100) if response_total > 0 else 0.0
    )
    
    # Resolution SLA metrics
    resolution_total = response_sla_query.filter(
        Ticket.sla_resolution_deadline.isnot(None)
    ).count()
    
    resolution_met = response_sla_query.filter(
        Ticket.sla_resolution_met_at.isnot(None)
    ).count()
    
    resolution_breached = response_sla_query.filter(
        Ticket.sla_resolution_breached == True
    ).count()
    
    resolution_compliance = (
        (resolution_met / resolution_total * 100) if resolution_total > 0 else 0.0
    )
    
    # Tickets with any SLA
    tickets_with_sla = response_sla_query.count()
    
    return {
        "response_sla": {
            "tickets_with_response_sla": response_total,
            "met_count": response_met,
            "breached_count": response_breached,
            "compliance_percentage": round(response_compliance, 2),
        },
        "resolution_sla": {
            "tickets_with_resolution_sla": resolution_total,
            "met_count": resolution_met,
            "breached_count": resolution_breached,
            "compliance_percentage": round(resolution_compliance, 2),
        },
        "tickets_with_sla": tickets_with_sla,
    }


# ======================================================
# Escalation Analytics
# ======================================================

def get_escalation_analytics(db: Session) -> Dict[str, Any]:
    """
    Get comprehensive escalation analytics using EscalationRecord.
    Uses authoritative escalation data, not derived from notifications.
    """
    # Total escalations
    total_escalations = db.query(EscalationRecord).count()
    
    # By event type
    response_escalations = db.query(EscalationRecord).filter(
        EscalationRecord.event_type == EscalationEventType.RESPONSE_BREACH
    ).count()
    
    resolution_escalations = db.query(EscalationRecord).filter(
        EscalationRecord.event_type == EscalationEventType.RESOLUTION_BREACH
    ).count()
    
    # By priority (join with tickets)
    by_priority = db.query(
        Ticket.priority,
        func.count(EscalationRecord.id).label("count"),
    ).join(
        EscalationRecord, EscalationRecord.ticket_id == Ticket.id
    ).filter(
        Ticket.is_deleted == False
    ).group_by(Ticket.priority).all()
    
    priority_counts = {row.priority: row.count for row in by_priority}
    
    # By recipient role (join with users)
    by_role = db.query(
        User.role,
        func.count(EscalationRecord.id).label("count"),
    ).join(
        EscalationRecord, EscalationRecord.recipient_id == User.id
    ).group_by(User.role).all()
    
    role_counts = {row.role: row.count for row in by_role}
    
    # Over time (daily for last 30 days)
    thirty_days_ago = datetime.now(timezone.utc) - timedelta(days=30)
    
    daily_escalations = db.query(
        func.date(EscalationRecord.created_at).label("date"),
        func.count(EscalationRecord.id).label("count"),
    ).filter(
        EscalationRecord.created_at >= thirty_days_ago
    ).group_by(
        func.date(EscalationRecord.created_at)
    ).order_by(
        func.date(EscalationRecord.created_at)
    ).all()
    
    escalations_over_time = [
        {"date": str(row.date), "count": row.count}
        for row in daily_escalations
    ]
    
    # Currently escalated tickets (escalated_to is not null, not resolved/closed)
    currently_escalated = db.query(Ticket).filter(
        Ticket.is_deleted == False,
        Ticket.escalated_to.isnot(None),
        Ticket.status.notin_(["Resolved", "Closed"]),
    ).count()
    
    return {
        "total_escalations": total_escalations,
        "response_sla_escalations": response_escalations,
        "resolution_sla_escalations": resolution_escalations,
        "by_priority": priority_counts,
        "by_recipient_role": role_counts,
        "escalations_over_time": escalations_over_time,
        "currently_escalated_tickets": currently_escalated,
    }


# ======================================================
# Response & Resolution Time Analytics
# ======================================================

def get_response_resolution_time_analytics(db: Session) -> Dict[str, Any]:
    """
    Calculate average response and resolution times.
    Uses existing timestamps - does not invent data.
    """
    base_query = _base_ticket_query(db)
    
    # Average first response time (for tickets with sla_response_met_at)
    response_times = base_query.filter(
        Ticket.sla_response_met_at.isnot(None),
        Ticket.created_at.isnot(None),
        Ticket.sla_response_met_at.isnot(None),
    ).with_entities(
        func.avg(
            func.extract('epoch', Ticket.sla_response_met_at - Ticket.created_at) / 60
        ).label("avg_response_minutes"),
    ).first()
    
    avg_response_minutes = response_times.avg_response_minutes
    
    # Average resolution time (for resolved tickets with resolved_at)
    resolution_times = base_query.filter(
        Ticket.resolved_at.isnot(None),
        Ticket.created_at.isnot(None),
        Ticket.status.in_(["Resolved", "Closed"]),
    ).with_entities(
        func.avg(
            func.extract('epoch', Ticket.resolved_at - Ticket.created_at) / 60
        ).label("avg_resolution_minutes"),
    ).first()
    
    avg_resolution_minutes = resolution_times.avg_resolution_minutes
    
    return {
        "average_first_response_minutes": round(avg_response_minutes, 2) if avg_response_minutes else None,
        "average_resolution_minutes": round(avg_resolution_minutes, 2) if avg_resolution_minutes else None,
        "note": "Only calculated for tickets with applicable timestamps. Returns None if insufficient data.",
    }


# ======================================================
# Technician Workload Analytics
# ======================================================

def get_technician_workload_analytics(db: Session) -> List[Dict[str, Any]]:
    """
    Get technician workload metrics.
    Returns metrics per technician (Admin and Technician roles).
    """
    # Get all technicians and admins
    technicians = db.query(User).filter(
        User.role.in_(["Admin", "Technician"]),
        User.is_deleted == False,
    ).all()
    
    workload_data = []
    
    for tech in technicians:
        # Tickets currently assigned
        assigned_count = db.query(Ticket).filter(
            Ticket.is_deleted == False,
            Ticket.assigned_to == tech.id,
        ).count()
        
        # Open assigned tickets
        open_assigned = db.query(Ticket).filter(
            Ticket.is_deleted == False,
            Ticket.assigned_to == tech.id,
            Ticket.status.in_(["Open", "Assigned", "Pending"]),
        ).count()
        
        # Resolved tickets (historical)
        resolved_count = db.query(Ticket).filter(
            Ticket.is_deleted == False,
            Ticket.resolved_by == tech.id,
        ).count()
        
        # Escalated tickets (where tech was recipient)
        escalated_count = db.query(EscalationRecord).filter(
            EscalationRecord.recipient_id == tech.id,
        ).count()
        
        # Escalated by this technician (manual escalation)
        escalated_by = db.query(Ticket).filter(
            Ticket.is_deleted == False,
            Ticket.escalated_by == tech.id,
        ).count()
        
        workload_data.append({
            "technician_id": tech.id,
            "technician_name": tech.name,
            "technician_email": tech.email,
            "role": tech.role,
            "tickets_currently_assigned": assigned_count,
            "open_assigned_tickets": open_assigned,
            "tickets_resolved": resolved_count,
            "escalations_received": escalated_count,
            "escalations_initiated": escalated_by,
        })
    
    return workload_data


# ======================================================
# Time-Series / Trends Analytics
# ======================================================

def _get_date_filter(
    created_at_field,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
):
    """Build date filter conditions."""
    conditions = []
    if start_date:
        conditions.append(created_at_field >= start_date)
    if end_date:
        conditions.append(created_at_field <= end_date)
    return conditions


def get_ticket_trends(
    db: Session,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    granularity: str = "daily",
) -> Dict[str, Any]:
    """
    Get ticket trend data over time.
    Supports daily, weekly, monthly granularity.
    """
    base_query = _base_ticket_query(db)
    
    # Build date filters
    conditions = [Ticket.is_deleted == False]
    if start_date:
        conditions.append(Ticket.created_at >= start_date)
    if end_date:
        conditions.append(Ticket.created_at <= end_date)
    
    # Determine date truncation
    if granularity == "daily":
        date_trunc = func.date(Ticket.created_at)
    elif granularity == "weekly":
        date_trunc = func.date_trunc('week', Ticket.created_at)
    elif granularity == "monthly":
        date_trunc = func.date_trunc('month', Ticket.created_at)
    else:
        date_trunc = func.date(Ticket.created_at)
    
    # Tickets created
    created_query = base_query.filter(and_(*conditions)).with_entities(
        date_trunc.label("period"),
        func.count(Ticket.id).label("created"),
    ).group_by(date_trunc).order_by(date_trunc)
    
    # Tickets resolved
    resolved_query = base_query.filter(
        and_(*conditions),
        Ticket.resolved_at.isnot(None),
        Ticket.status.in_(["Resolved", "Closed"]),
    ).with_entities(
        func.date(Ticket.resolved_at).label("period"),
        func.count(Ticket.id).label("resolved"),
    ).group_by(func.date(Ticket.resolved_at)).order_by(func.date(Ticket.resolved_at))
    
    # SLA breaches
    breach_query = db.query(
        func.date(TicketHistory.created_at).label("period"),
        func.count(TicketHistory.id).label("breaches"),
    ).join(
        Ticket, TicketHistory.ticket_id == Ticket.id
    ).filter(
        Ticket.is_deleted == False,
        TicketHistory.event_type.in_([
            HistoryEventType.SLA_RESPONSE_BREACHED,
            HistoryEventType.SLA_RESOLUTION_BREACHED,
        ]),
    )
    if start_date:
        breach_query = breach_query.filter(TicketHistory.created_at >= start_date)
    if end_date:
        breach_query = breach_query.filter(TicketHistory.created_at <= end_date)
    breach_query = breach_query.group_by(
        func.date(TicketHistory.created_at)
    ).order_by(func.date(TicketHistory.created_at))
    
    # Escalations
    escalation_query = db.query(
        func.date(EscalationRecord.created_at).label("period"),
        func.count(EscalationRecord.id).label("escalations"),
    )
    if start_date:
        escalation_query = escalation_query.filter(EscalationRecord.created_at >= start_date)
    if end_date:
        escalation_query = escalation_query.filter(EscalationRecord.created_at <= end_date)
    escalation_query = escalation_query.group_by(
        func.date(EscalationRecord.created_at)
    ).order_by(func.date(EscalationRecord.created_at))
    
    # Execute queries and combine
    created_data = {str(row.period): row.created for row in created_query.all()}
    resolved_data = {str(row.period): row.resolved for row in resolved_query.all()}
    breach_data = {str(row.period): row.breaches for row in breach_query.all()}
    escalation_data = {str(row.period): row.escalations for row in escalation_query.all()}
    
    # Combine all periods
    all_periods = set()
    all_periods.update(created_data.keys())
    all_periods.update(resolved_data.keys())
    all_periods.update(breach_data.keys())
    all_periods.update(escalation_data.keys())
    
    trends = []
    for period in sorted(all_periods):
        trends.append({
            "period": period,
            "tickets_created": created_data.get(period, 0),
            "tickets_resolved": resolved_data.get(period, 0),
            "sla_breaches": breach_data.get(period, 0),
            "escalations": escalation_data.get(period, 0),
        })
    
    return {
        "granularity": granularity,
        "trends": trends,
    }


# ======================================================
# Filtered Analytics
# ======================================================

def get_filtered_ticket_analytics(
    db: Session,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    priority: Optional[str] = None,
    category: Optional[str] = None,
    ticket_type: Optional[str] = None,
    assignee_id: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Get filtered ticket analytics.
    Supports date range, priority, category, ticket_type, assignee filters.
    """
    query = _base_ticket_query(db)
    
    if start_date:
        query = query.filter(Ticket.created_at >= start_date)
    if end_date:
        query = query.filter(Ticket.created_at <= end_date)
    if priority:
        query = query.filter(Ticket.priority == priority)
    if category:
        query = query.filter(Ticket.category == category)
    if ticket_type:
        query = query.filter(Ticket.ticket_type == ticket_type)
    if assignee_id:
        query = query.filter(Ticket.assigned_to == assignee_id)
    
    # Status counts
    status_counts = query.with_entities(
        Ticket.status,
        func.count(Ticket.id).label("count"),
    ).group_by(Ticket.status).all()
    
    # Priority counts
    priority_counts = query.with_entities(
        Ticket.priority,
        func.count(Ticket.id).label("count"),
    ).group_by(Ticket.priority).all()
    
    total = query.count()
    
    return {
        "total": total,
        "by_status": {row.status: row.count for row in status_counts},
        "by_priority": {row.priority: row.count for row in priority_counts},
    }