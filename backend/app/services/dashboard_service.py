from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.ticket import Ticket


# ======================================================
# Helper
# ======================================================

def _ticket_query(db: Session, user):
    role = user["role"]

    if role == "Admin":
        return db.query(Ticket)

    if role == "Technician":
        return db.query(Ticket).filter(
            Ticket.assigned_to == user["id"]
        )

    # Employee
    return db.query(Ticket).filter(
        Ticket.created_by == user["id"]
    )


# ======================================================
# Dashboard Summary
# ======================================================

def get_dashboard_summary(db: Session, user):

    query = _ticket_query(db, user)

    return {

        "total_tickets": query.count(),

        "open_tickets": query.filter(
            Ticket.status == "Open"
        ).count(),

        "assigned_tickets": query.filter(
            Ticket.status == "Assigned"
        ).count(),

        "resolved_tickets": query.filter(
            Ticket.status == "Resolved"
        ).count(),

        "high_priority": query.filter(
            Ticket.priority == "High"
        ).count(),

        "medium_priority": query.filter(
            Ticket.priority == "Medium"
        ).count(),

        "low_priority": query.filter(
            Ticket.priority == "Low"
        ).count(),

    }


# ======================================================
# Recent Tickets
# ======================================================

def get_recent_tickets(
    db: Session,
    user,
    limit: int = 5,
):

    return (
        _ticket_query(db, user)
        .order_by(Ticket.created_at.desc())
        .limit(limit)
        .all()
    )


# ======================================================
# Ticket Trend
# ======================================================

def get_ticket_trend(db: Session, user):

    result = (
        _ticket_query(db, user)
        .with_entities(
            func.date(Ticket.created_at).label("date"),
            func.count(Ticket.id).label("tickets"),
        )
        .group_by(func.date(Ticket.created_at))
        .order_by(func.date(Ticket.created_at))
        .all()
    )

    return [

        {
            "date": str(row.date),
            "tickets": row.tickets,
        }

        for row in result

    ]