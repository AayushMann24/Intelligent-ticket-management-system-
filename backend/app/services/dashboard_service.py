from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.ticket import Ticket


# ==========================================
# Dashboard Summary
# ==========================================

def get_dashboard_summary(db: Session):

    return {
        "total_tickets": db.query(Ticket).count(),

        "open_tickets": db.query(Ticket)
        .filter(Ticket.status == "Open")
        .count(),

        "assigned_tickets": db.query(Ticket)
        .filter(Ticket.status == "Assigned")
        .count(),

        "resolved_tickets": db.query(Ticket)
        .filter(Ticket.status == "Resolved")
        .count(),

        "high_priority": db.query(Ticket)
        .filter(Ticket.priority == "High")
        .count(),

        "medium_priority": db.query(Ticket)
        .filter(Ticket.priority == "Medium")
        .count(),

        "low_priority": db.query(Ticket)
        .filter(Ticket.priority == "Low")
        .count(),
    }


# ==========================================
# Recent Tickets
# ==========================================

def get_recent_tickets(
    db: Session,
    limit: int = 5,
):

    return (
        db.query(Ticket)
        .order_by(Ticket.created_at.desc())
        .limit(limit)
        .all()
    )


# ==========================================
# Priority Summary
# ==========================================

def get_priority_summary(db: Session):

    return {

        "high": db.query(Ticket)
        .filter(Ticket.priority == "High")
        .count(),

        "medium": db.query(Ticket)
        .filter(Ticket.priority == "Medium")
        .count(),

        "low": db.query(Ticket)
        .filter(Ticket.priority == "Low")
        .count(),

    }


# ==========================================
# Ticket Trend
# ==========================================

def get_ticket_trend(db: Session):

    result = (
        db.query(
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