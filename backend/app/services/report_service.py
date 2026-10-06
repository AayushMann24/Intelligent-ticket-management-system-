"""
Report Service (Phase 2E - Checkpoint 3)

Provides report generation and CSV export functionality for Admin users.
All reports use efficient SQL aggregation queries and streaming for large datasets.
"""

import csv
import io
from datetime import datetime, timezone, timedelta
from typing import Optional, List, Dict, Any, Iterator, Generator
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, case, extract, text
from sqlalchemy.sql import label

from app.models.ticket import Ticket
from app.models.user import User
from app.models.escalation import EscalationRecord, EscalationEventType
from app.models.ticket_comment import TicketHistory, HistoryEventType


def _base_ticket_query(db: Session):
    """Base query that excludes soft-deleted tickets."""
    return db.query(Ticket).filter(Ticket.is_deleted == False)


# ======================================================
# Report Filter Helpers
# ======================================================

def _apply_ticket_filters(
    query,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    priority: Optional[str] = None,
    category: Optional[str] = None,
    ticket_type: Optional[str] = None,
    assignee_id: Optional[int] = None,
    status: Optional[str] = None,
):
    """Apply common ticket filters to a query."""
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
    if status:
        query = query.filter(Ticket.status == status)
    return query


def _build_report_filename(report_type: str, start_date: Optional[datetime], end_date: Optional[datetime], extension: str = "csv") -> str:
    """Build a meaningful filename for the report."""
    date_str = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    date_range = ""
    if start_date or end_date:
        start_str = start_date.strftime("%Y%m%d") if start_date else "start"
        end_str = end_date.strftime("%Y%m%d") if end_date else "end"
        date_range = f"_{start_str}_to_{end_str}"
    return f"{report_type}_report{date_range}_{date_str}.{extension}"


# ======================================================
# CSV Generation Utilities
# ======================================================

def _csv_row_escape(value: Any) -> str:
    """Safely escape a value for CSV output."""
    if value is None:
        return ""
    s = str(value)
    # Escape quotes and wrap in quotes if contains comma, quote, or newline
    if any(c in s for c in [',', '"', '\n', '\r']):
        s = s.replace('"', '""')
        return f'"{s}"'
    return s


def _generate_csv_stream(headers: List[str], rows: Generator[List[Any], None, None]) -> Generator[str, None, None]:
    """
    Generate CSV content as a stream of strings.
    Yields CSV lines one at a time for memory efficiency.
    """
    output = io.StringIO()
    writer = csv.writer(output, quoting=csv.QUOTE_MINIMAL)
    
    # Write headers
    writer.writerow(headers)
    yield output.getvalue()
    output.seek(0)
    output.truncate(0)
    
    # Write data rows
    for row in rows:
        writer.writerow([_csv_row_escape(v) for v in row])
        yield output.getvalue()
        output.seek(0)
        output.truncate(0)


# ======================================================
# Ticket Report
# ======================================================

def generate_ticket_report_rows(
    db: Session,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    priority: Optional[str] = None,
    category: Optional[str] = None,
    ticket_type: Optional[str] = None,
    assignee_id: Optional[int] = None,
    status: Optional[str] = None,
) -> Generator[List[Any], None, None]:
    """
    Generate ticket report rows for CSV export.
    Yields rows one at a time for memory efficiency.
    """
    query = _base_ticket_query(db)
    query = _apply_ticket_filters(
        query, start_date, end_date, priority, category, ticket_type, assignee_id, status
    )
    
    # Select all fields needed for the report
    query = query.with_entities(
        Ticket.id,
        Ticket.title,
        Ticket.description,
        Ticket.priority,
        Ticket.status,
        Ticket.ticket_type,
        Ticket.category,
        Ticket.subcategory,
        Ticket.created_at,
        Ticket.updated_at,
        Ticket.resolved_at,
        Ticket.assigned_to,
        Ticket.resolved_by,
        Ticket.escalated_to,
        Ticket.sla_policy_id,
        Ticket.sla_response_deadline,
        Ticket.sla_resolution_deadline,
        Ticket.sla_response_met_at,
        Ticket.sla_resolution_met_at,
        Ticket.sla_response_breached,
        Ticket.sla_resolution_breached,
        User.name.label("assignee_name"),
        User.email.label("assignee_email"),
    ).outerjoin(User, Ticket.assigned_to == User.id).order_by(Ticket.created_at.desc())
    
    # Stream results
    for row in query.yield_per(100):
        yield [
            row.id,
            row.title,
            row.description[:500] if row.description else "",  # Truncate long descriptions
            row.priority,
            row.status,
            row.ticket_type,
            row.category or "",
            row.subcategory or "",
            row.created_at.isoformat() if row.created_at else "",
            row.updated_at.isoformat() if row.updated_at else "",
            row.resolved_at.isoformat() if row.resolved_at else "",
            row.assignee_name or "",
            row.assignee_email or "",
            "Yes" if row.escalated_to else "No",
            row.sla_response_deadline.isoformat() if row.sla_response_deadline else "",
            row.sla_resolution_deadline.isoformat() if row.sla_resolution_deadline else "",
            "Met" if row.sla_response_met_at else ("Breached" if row.sla_response_breached else "N/A"),
            "Met" if row.sla_resolution_met_at else ("Breached" if row.sla_resolution_breached else "N/A"),
        ]


def get_ticket_report_summary(
    db: Session,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    priority: Optional[str] = None,
    category: Optional[str] = None,
    ticket_type: Optional[str] = None,
    assignee_id: Optional[int] = None,
    status: Optional[str] = None,
) -> Dict[str, Any]:
    """Get summary metrics for ticket report."""
    query = _base_ticket_query(db)
    query = _apply_ticket_filters(
        query, start_date, end_date, priority, category, ticket_type, assignee_id, status
    )
    
    total = query.count()
    
    # Status distribution
    status_counts = query.with_entities(
        Ticket.status,
        func.count(Ticket.id).label("count"),
    ).group_by(Ticket.status).all()
    
    # Priority distribution
    priority_counts = query.with_entities(
        Ticket.priority,
        func.count(Ticket.id).label("count"),
    ).group_by(Ticket.priority).all()
    
    # Ticket type distribution
    type_counts = query.with_entities(
        Ticket.ticket_type,
        func.count(Ticket.id).label("count"),
    ).group_by(Ticket.ticket_type).all()
    
    return {
        "total_tickets": total,
        "by_status": {row.status: row.count for row in status_counts},
        "by_priority": {row.priority: row.count for row in priority_counts},
        "by_ticket_type": {row.ticket_type: row.count for row in type_counts},
    }


TICKET_REPORT_HEADERS = [
    "Ticket ID",
    "Title",
    "Description (truncated)",
    "Priority",
    "Status",
    "Ticket Type",
    "Category",
    "Subcategory",
    "Created At",
    "Updated At",
    "Resolved At",
    "Assignee Name",
    "Assignee Email",
    "Escalated",
    "SLA Response Deadline",
    "SLA Resolution Deadline",
    "Response SLA Status",
    "Resolution SLA Status",
]


# ======================================================
# SLA Compliance Report
# ======================================================

def generate_sla_report_rows(
    db: Session,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    priority: Optional[str] = None,
    category: Optional[str] = None,
    ticket_type: Optional[str] = None,
    assignee_id: Optional[int] = None,
) -> Generator[List[Any], None, None]:
    """
    Generate SLA compliance report rows for CSV export.
    """
    query = _base_ticket_query(db).filter(Ticket.sla_policy_id.isnot(None))
    query = _apply_ticket_filters(
        query, start_date, end_date, priority, category, ticket_type, assignee_id
    )
    
    query = query.with_entities(
        Ticket.id,
        Ticket.title,
        Ticket.priority,
        Ticket.ticket_type,
        Ticket.category,
        Ticket.status,
        Ticket.created_at,
        Ticket.assigned_to,
        Ticket.sla_policy_id,
        Ticket.sla_response_deadline,
        Ticket.sla_resolution_deadline,
        Ticket.sla_response_met_at,
        Ticket.sla_resolution_met_at,
        Ticket.sla_response_breached,
        Ticket.sla_resolution_breached,
        User.name.label("assignee_name"),
    ).outerjoin(User, Ticket.assigned_to == User.id).order_by(Ticket.created_at.desc())
    
    for row in query.yield_per(100):
        response_status = "N/A"
        if row.sla_response_deadline:
            if row.sla_response_met_at:
                response_status = "Met"
            elif row.sla_response_breached:
                response_status = "Breached"
            else:
                response_status = "Pending"
        
        resolution_status = "N/A"
        if row.sla_resolution_deadline:
            if row.sla_resolution_met_at:
                resolution_status = "Met"
            elif row.sla_resolution_breached:
                resolution_status = "Breached"
            else:
                resolution_status = "Pending"
        
        yield [
            row.id,
            row.title,
            row.priority,
            row.ticket_type,
            row.category or "",
            row.status,
            row.created_at.isoformat() if row.created_at else "",
            row.assignee_name or "",
            row.sla_response_deadline.isoformat() if row.sla_response_deadline else "",
            row.sla_resolution_deadline.isoformat() if row.sla_resolution_deadline else "",
            row.sla_response_met_at.isoformat() if row.sla_response_met_at else "",
            row.sla_resolution_met_at.isoformat() if row.sla_resolution_met_at else "",
            response_status,
            resolution_status,
        ]


def get_sla_report_summary(
    db: Session,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    priority: Optional[str] = None,
    category: Optional[str] = None,
    ticket_type: Optional[str] = None,
    assignee_id: Optional[int] = None,
) -> Dict[str, Any]:
    """Get summary metrics for SLA report."""
    query = _base_ticket_query(db).filter(Ticket.sla_policy_id.isnot(None))
    query = _apply_ticket_filters(
        query, start_date, end_date, priority, category, ticket_type, assignee_id
    )
    
    # Response SLA
    response_total = query.filter(Ticket.sla_response_deadline.isnot(None)).count()
    response_met = query.filter(Ticket.sla_response_met_at.isnot(None)).count()
    response_breached = query.filter(Ticket.sla_response_breached == True).count()
    response_pending = response_total - response_met - response_breached
    response_compliance = round((response_met / response_total * 100) if response_total > 0 else 0.0, 2)
    
    # Resolution SLA
    resolution_total = query.filter(Ticket.sla_resolution_deadline.isnot(None)).count()
    resolution_met = query.filter(Ticket.sla_resolution_met_at.isnot(None)).count()
    resolution_breached = query.filter(Ticket.sla_resolution_breached == True).count()
    resolution_pending = resolution_total - resolution_met - resolution_breached
    resolution_compliance = round((resolution_met / resolution_total * 100) if resolution_total > 0 else 0.0, 2)
    
    # By priority
    priority_stats = {}
    for p in ["Critical", "High", "Medium", "Low"]:
        p_query = query.filter(Ticket.priority == p)
        r_total = p_query.filter(Ticket.sla_response_deadline.isnot(None)).count()
        r_met = p_query.filter(Ticket.sla_response_met_at.isnot(None)).count()
        r_breached = p_query.filter(Ticket.sla_response_breached == True).count()
        rs_total = p_query.filter(Ticket.sla_resolution_deadline.isnot(None)).count()
        rs_met = p_query.filter(Ticket.sla_resolution_met_at.isnot(None)).count()
        rs_breached = p_query.filter(Ticket.sla_resolution_breached == True).count()
        priority_stats[p] = {
            "response": {"total": r_total, "met": r_met, "breached": r_breached, "compliance": round((r_met / r_total * 100) if r_total > 0 else 0.0, 2)},
            "resolution": {"total": rs_total, "met": rs_met, "breached": rs_breached, "compliance": round((rs_met / rs_total * 100) if rs_total > 0 else 0.0, 2)},
        }
    
    return {
        "response_sla": {
            "total": response_total,
            "met": response_met,
            "breached": response_breached,
            "pending": response_pending,
            "compliance_percentage": response_compliance,
        },
        "resolution_sla": {
            "total": resolution_total,
            "met": resolution_met,
            "breached": resolution_breached,
            "pending": resolution_pending,
            "compliance_percentage": resolution_compliance,
        },
        "by_priority": priority_stats,
    }


SLA_REPORT_HEADERS = [
    "Ticket ID",
    "Title",
    "Priority",
    "Ticket Type",
    "Category",
    "Status",
    "Created At",
    "Assignee",
    "Response Deadline",
    "Resolution Deadline",
    "Response Met At",
    "Resolution Met At",
    "Response SLA Status",
    "Resolution SLA Status",
]


# ======================================================
# SLA Breach Report
# ======================================================

def generate_sla_breach_report_rows(
    db: Session,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    priority: Optional[str] = None,
    category: Optional[str] = None,
    ticket_type: Optional[str] = None,
    assignee_id: Optional[int] = None,
    breach_type: Optional[str] = None,  # "response", "resolution", or None for both
) -> Generator[List[Any], None, None]:
    """
    Generate SLA breach report rows for CSV export.
    """
    conditions = []
    if breach_type == "response":
        conditions.append(Ticket.sla_response_breached == True)
    elif breach_type == "resolution":
        conditions.append(Ticket.sla_resolution_breached == True)
    else:
        conditions.append(or_(Ticket.sla_response_breached == True, Ticket.sla_resolution_breached == True))
    
    query = _base_ticket_query(db).filter(and_(*conditions))
    query = _apply_ticket_filters(
        query, start_date, end_date, priority, category, ticket_type, assignee_id
    )
    
    query = query.with_entities(
        Ticket.id,
        Ticket.title,
        Ticket.priority,
        Ticket.ticket_type,
        Ticket.category,
        Ticket.status,
        Ticket.created_at,
        Ticket.assigned_to,
        Ticket.sla_response_deadline,
        Ticket.sla_resolution_deadline,
        Ticket.sla_response_met_at,
        Ticket.sla_resolution_met_at,
        Ticket.sla_response_breached,
        Ticket.sla_resolution_breached,
        User.name.label("assignee_name"),
        User.email.label("assignee_email"),
    ).outerjoin(User, Ticket.assigned_to == User.id).order_by(Ticket.created_at.desc())
    
    for row in query.yield_per(100):
        breach_types = []
        if row.sla_response_breached:
            breach_types.append("Response")
        if row.sla_resolution_breached:
            breach_types.append("Resolution")
        
        yield [
            row.id,
            row.title,
            row.priority,
            row.ticket_type,
            row.category or "",
            row.status,
            row.created_at.isoformat() if row.created_at else "",
            row.assignee_name or "",
            row.assignee_email or "",
            row.sla_response_deadline.isoformat() if row.sla_response_deadline else "",
            row.sla_resolution_deadline.isoformat() if row.sla_resolution_deadline else "",
            row.sla_response_met_at.isoformat() if row.sla_response_met_at else "",
            row.sla_resolution_met_at.isoformat() if row.sla_resolution_met_at else "",
            ", ".join(breach_types),
        ]


SLA_BREACH_REPORT_HEADERS = [
    "Ticket ID",
    "Title",
    "Priority",
    "Ticket Type",
    "Category",
    "Status",
    "Created At",
    "Assignee Name",
    "Assignee Email",
    "Response Deadline",
    "Resolution Deadline",
    "Response Met At",
    "Resolution Met At",
    "Breach Types",
]


# ======================================================
# Escalation Report
# ======================================================

def generate_escalation_report_rows(
    db: Session,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    priority: Optional[str] = None,
    category: Optional[str] = None,
    ticket_type: Optional[str] = None,
    assignee_id: Optional[int] = None,
) -> Generator[List[Any], None, None]:
    """
    Generate escalation report rows for CSV export.
    """
    query = db.query(EscalationRecord).join(
        Ticket, EscalationRecord.ticket_id == Ticket.id
    ).filter(Ticket.is_deleted == False)
    
    if start_date:
        query = query.filter(EscalationRecord.created_at >= start_date)
    if end_date:
        query = query.filter(EscalationRecord.created_at <= end_date)
    if priority:
        query = query.filter(Ticket.priority == priority)
    if category:
        query = query.filter(Ticket.category == category)
    if ticket_type:
        query = query.filter(Ticket.ticket_type == ticket_type)
    if assignee_id:
        query = query.filter(Ticket.assigned_to == assignee_id)
    
    query = query.with_entities(
        EscalationRecord.id,
        EscalationRecord.ticket_id,
        EscalationRecord.event_type,
        EscalationRecord.rule_id,
        EscalationRecord.recipient_id,
        EscalationRecord.notification_created,
        EscalationRecord.email_sent,
        EscalationRecord.created_at,
        Ticket.title,
        Ticket.priority,
        Ticket.ticket_type,
        Ticket.category,
        Ticket.status,
        Ticket.assigned_to,
        User.name.label("recipient_name"),
        User.role.label("recipient_role"),
    ).outerjoin(User, EscalationRecord.recipient_id == User.id).order_by(EscalationRecord.created_at.desc())
    
    for row in query.yield_per(100):
        yield [
            row.id,
            row.ticket_id,
            row.title,
            row.priority,
            row.ticket_type,
            row.category or "",
            row.status,
            row.event_type.value,
            row.recipient_name or "",
            row.recipient_role or "",
            "Yes" if row.notification_created else "No",
            "Yes" if row.email_sent else "No",
            row.created_at.isoformat() if row.created_at else "",
        ]


def get_escalation_report_summary(
    db: Session,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    priority: Optional[str] = None,
    category: Optional[str] = None,
    ticket_type: Optional[str] = None,
    assignee_id: Optional[int] = None,
) -> Dict[str, Any]:
    """Get summary metrics for escalation report."""
    query = db.query(EscalationRecord).join(
        Ticket, EscalationRecord.ticket_id == Ticket.id
    ).filter(Ticket.is_deleted == False)
    
    if start_date:
        query = query.filter(EscalationRecord.created_at >= start_date)
    if end_date:
        query = query.filter(EscalationRecord.created_at <= end_date)
    if priority:
        query = query.filter(Ticket.priority == priority)
    if category:
        query = query.filter(Ticket.category == category)
    if ticket_type:
        query = query.filter(Ticket.ticket_type == ticket_type)
    if assignee_id:
        query = query.filter(Ticket.assigned_to == assignee_id)
    
    total = query.count()
    
    # By event type
    by_type = query.with_entities(
        EscalationRecord.event_type,
        func.count(EscalationRecord.id).label("count"),
    ).group_by(EscalationRecord.event_type).all()
    
    # By priority
    by_priority = query.with_entities(
        Ticket.priority,
        func.count(EscalationRecord.id).label("count"),
    ).group_by(Ticket.priority).all()
    
    # By recipient role
    by_role = query.with_entities(
        User.role,
        func.count(EscalationRecord.id).label("count"),
    ).outerjoin(User, EscalationRecord.recipient_id == User.id).group_by(User.role).all()
    
    # By day (last 30 days)
    thirty_days_ago = datetime.now(timezone.utc) - timedelta(days=30)
    daily = query.filter(EscalationRecord.created_at >= thirty_days_ago).with_entities(
        func.date(EscalationRecord.created_at).label("date"),
        func.count(EscalationRecord.id).label("count"),
    ).group_by(func.date(EscalationRecord.created_at)).order_by(func.date(EscalationRecord.created_at)).all()
    
    return {
        "total_escalations": total,
        "by_event_type": {row.event_type.value: row.count for row in by_type},
        "by_priority": {row.priority: row.count for row in by_priority},
        "by_recipient_role": {row.role: row.count for row in by_role if row.role},
        "escalations_over_time": [{"date": str(row.date), "count": row.count} for row in daily],
    }


ESCALATION_REPORT_HEADERS = [
    "Escalation ID",
    "Ticket ID",
    "Ticket Title",
    "Priority",
    "Ticket Type",
    "Category",
    "Ticket Status",
    "Event Type",
    "Recipient",
    "Recipient Role",
    "Notification Created",
    "Email Sent",
    "Escalation Time",
]


# ======================================================
# Technician Workload Report
# ======================================================

def generate_technician_report_rows(
    db: Session,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
) -> Generator[List[Any], None, None]:
    """
    Generate technician workload report rows for CSV export.
    """
    # Get all technicians and admins
    technicians = db.query(User).filter(
        User.role.in_(["Admin", "Technician"]),
        User.is_deleted == False,
    ).all()
    
    for tech in technicians:
        # Base query for this technician's tickets
        assigned_query = _base_ticket_query(db).filter(Ticket.assigned_to == tech.id)
        resolved_query = _base_ticket_query(db).filter(Ticket.resolved_by == tech.id)
        escalated_received_query = db.query(EscalationRecord).filter(EscalationRecord.recipient_id == tech.id)
        escalated_initiated_query = _base_ticket_query(db).filter(Ticket.escalated_by == tech.id)
        
        if start_date:
            assigned_query = assigned_query.filter(Ticket.created_at >= start_date)
            resolved_query = resolved_query.filter(Ticket.resolved_at >= start_date)
            escalated_received_query = escalated_received_query.filter(EscalationRecord.created_at >= start_date)
            escalated_initiated_query = escalated_initiated_query.filter(Ticket.escalated_at >= start_date)
        if end_date:
            assigned_query = assigned_query.filter(Ticket.created_at <= end_date)
            resolved_query = resolved_query.filter(Ticket.resolved_at <= end_date)
            escalated_received_query = escalated_received_query.filter(EscalationRecord.created_at <= end_date)
            escalated_initiated_query = escalated_initiated_query.filter(Ticket.escalated_at <= end_date)
        
        assigned_count = assigned_query.count()
        open_assigned = assigned_query.filter(Ticket.status.in_(["Open", "Assigned", "Pending"])).count()
        resolved_count = resolved_query.count()
        escalations_received = escalated_received_query.count()
        escalations_initiated = escalated_initiated_query.count()
        
        # SLA metrics for assigned tickets
        sla_assigned = assigned_query.filter(Ticket.sla_policy_id.isnot(None))
        response_breached = sla_assigned.filter(Ticket.sla_response_breached == True).count()
        resolution_breached = sla_assigned.filter(Ticket.sla_resolution_breached == True).count()
        
        yield [
            tech.id,
            tech.name,
            tech.email,
            tech.role,
            assigned_count,
            open_assigned,
            resolved_count,
            escalations_received,
            escalations_initiated,
            response_breached,
            resolution_breached,
        ]


def get_technician_report_summary(
    db: Session,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
) -> Dict[str, Any]:
    """Get summary metrics for technician report."""
    technicians = db.query(User).filter(
        User.role.in_(["Admin", "Technician"]),
        User.is_deleted == False,
    ).all()
    
    total_assigned = 0
    total_open = 0
    total_resolved = 0
    total_escalations_received = 0
    total_escalations_initiated = 0
    total_response_breached = 0
    total_resolution_breached = 0
    
    for tech in technicians:
        assigned_query = _base_ticket_query(db).filter(Ticket.assigned_to == tech.id)
        resolved_query = _base_ticket_query(db).filter(Ticket.resolved_by == tech.id)
        escalated_received = db.query(EscalationRecord).filter(EscalationRecord.recipient_id == tech.id)
        escalated_initiated = _base_ticket_query(db).filter(Ticket.escalated_by == tech.id)
        
        if start_date:
            assigned_query = assigned_query.filter(Ticket.created_at >= start_date)
            resolved_query = resolved_query.filter(Ticket.resolved_at >= start_date)
            escalated_received = escalated_received.filter(EscalationRecord.created_at >= start_date)
            escalated_initiated = escalated_initiated.filter(Ticket.escalated_at >= start_date)
        if end_date:
            assigned_query = assigned_query.filter(Ticket.created_at <= end_date)
            resolved_query = resolved_query.filter(Ticket.resolved_at <= end_date)
            escalated_received = escalated_received.filter(EscalationRecord.created_at <= end_date)
            escalated_initiated = escalated_initiated.filter(Ticket.escalated_at <= end_date)
        
        total_assigned += assigned_query.count()
        total_open += assigned_query.filter(Ticket.status.in_(["Open", "Assigned", "Pending"])).count()
        total_resolved += resolved_query.count()
        total_escalations_received += escalated_received.count()
        total_escalations_initiated += escalated_initiated.count()
        
        sla_assigned = assigned_query.filter(Ticket.sla_policy_id.isnot(None))
        total_response_breached += sla_assigned.filter(Ticket.sla_response_breached == True).count()
        total_resolution_breached += sla_assigned.filter(Ticket.sla_resolution_breached == True).count()
    
    return {
        "total_technicians": len(technicians),
        "total_assigned": total_assigned,
        "total_open": total_open,
        "total_resolved": total_resolved,
        "total_escalations_received": total_escalations_received,
        "total_escalations_initiated": total_escalations_initiated,
        "total_response_breached": total_response_breached,
        "total_resolution_breached": total_resolution_breached,
    }


TECHNICIAN_REPORT_HEADERS = [
    "Technician ID",
    "Name",
    "Email",
    "Role",
    "Tickets Currently Assigned",
    "Open Assigned Tickets",
    "Tickets Resolved",
    "Escalations Received",
    "Escalations Initiated",
    "Response SLA Breaches (Assigned)",
    "Resolution SLA Breaches (Assigned)",
]


# ======================================================
# Report Type Registry
# ======================================================

REPORT_TYPES = {
    "tickets": {
        "name": "Ticket Report",
        "description": "Detailed ticket listing with all fields",
        "generator": generate_ticket_report_rows,
        "summary": get_ticket_report_summary,
        "headers": TICKET_REPORT_HEADERS,
        "filters": ["start_date", "end_date", "priority", "category", "ticket_type", "assignee_id", "status"],
    },
    "sla": {
        "name": "SLA Compliance Report",
        "description": "SLA compliance metrics and ticket-level details",
        "generator": generate_sla_report_rows,
        "summary": get_sla_report_summary,
        "headers": SLA_REPORT_HEADERS,
        "filters": ["start_date", "end_date", "priority", "category", "ticket_type", "assignee_id"],
    },
    "sla_breaches": {
        "name": "SLA Breach Report",
        "description": "Detailed SLA breach listing",
        "generator": generate_sla_breach_report_rows,
        "summary": lambda *args, **kwargs: {},  # Reuse SLA summary
        "headers": SLA_BREACH_REPORT_HEADERS,
        "filters": ["start_date", "end_date", "priority", "category", "ticket_type", "assignee_id", "breach_type"],
    },
    "escalations": {
        "name": "Escalation Report",
        "description": "Escalation events and details",
        "generator": generate_escalation_report_rows,
        "summary": get_escalation_report_summary,
        "headers": ESCALATION_REPORT_HEADERS,
        "filters": ["start_date", "end_date", "priority", "category", "ticket_type", "assignee_id"],
    },
    "technicians": {
        "name": "Technician Workload Report",
        "description": "Technician workload and performance metrics",
        "generator": generate_technician_report_rows,
        "summary": get_technician_report_summary,
        "headers": TECHNICIAN_REPORT_HEADERS,
        "filters": ["start_date", "end_date"],
    },
}