from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.ticket import Ticket


# ==========================================
# Dashboard Summary
# ==========================================

def get_dashboard_summary(db: Session):

    total = db.query(Ticket).count()

    open_count = (
        db.query(Ticket)
        .filter(Ticket.status == "Open")
        .count()
    )

    assigned_count = (
        db.query(Ticket)
        .filter(Ticket.status == "Assigned")
        .count()
    )

    resolved_count = (
        db.query(Ticket)
        .filter(Ticket.status == "Resolved")
        .count()
    )

    high = (
        db.query(Ticket)
        .filter(Ticket.priority == "High")
        .count()
    )

    medium = (
        db.query(Ticket)
        .filter(Ticket.priority == "Medium")
        .count()
    )

    low = (
        db.query(Ticket)
        .filter(Ticket.priority == "Low")
        .count()
    )

    return {

        "total_tickets": total,

        "open_tickets": open_count,

        "assigned_tickets": assigned_count,

        "resolved_tickets": resolved_count,

        "high_priority": high,

        "medium_priority": medium,

        "low_priority": low,

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

        "high": (
            db.query(Ticket)
            .filter(Ticket.priority == "High")
            .count()
        ),

        "medium": (
            db.query(Ticket)
            .filter(Ticket.priority == "Medium")
            .count()
        ),

        "low": (
            db.query(Ticket)
            .filter(Ticket.priority == "Low")
            .count()
        ),

    }


# ==========================================
# Weekly Ticket Trend
# ==========================================

def get_ticket_trend(db: Session):

    result = (
        db.query(
            func.date(Ticket.created_at),
            func.count(Ticket.id)
        )
        .group_by(func.date(Ticket.created_at))
        .order_by(func.date(Ticket.created_at))
        .all()
    )

    return [

        {

            "date": str(date),

            "tickets": count,

        }

        for date, count in result

    ]
from sqlalchemy import func
from app.models.ticket import Ticket


def get_ticket_trend(db):
    results = (
        db.query(
            func.date(Ticket.created_at).label("date"),
            func.count(Ticket.id).label("count"),
        )
        .group_by(func.date(Ticket.created_at))
        .order_by(func.date(Ticket.created_at))
        .all()
    )

    return [
        {
            "date": str(row.date),
            "tickets": row.count,
        }
        for row in results
    ]