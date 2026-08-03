from sqlalchemy.orm import Session

from app.models.ticket import Ticket


def get_dashboard_summary(db: Session):

    total = db.query(Ticket).count()

    open_tickets = (
        db.query(Ticket)
        .filter(Ticket.status == "Open")
        .count()
    )

    in_progress = (
        db.query(Ticket)
        .filter(Ticket.status == "In Progress")
        .count()
    )

    resolved = (
        db.query(Ticket)
        .filter(Ticket.status == "Resolved")
        .count()
    )

    return {
        "total_tickets": total,
        "open_tickets": open_tickets,
        "in_progress_tickets": in_progress,
        "resolved_tickets": resolved,
    }
def get_recent_tickets(db: Session):

    recent_tickets = (
        db.query(Ticket)
        .order_by(Ticket.id.desc())
        .limit(5)
        .all()
    )

    return recent_tickets

def get_priority_summary(db: Session):

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
        "high": high,
        "medium": medium,
        "low": low
    }