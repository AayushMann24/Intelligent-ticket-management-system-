from sqlalchemy.orm import Session
from app.models.ticket import Ticket


def get_recent_activity(db: Session):
    tickets = (
        db.query(Ticket)
        .order_by(Ticket.created_at.desc())
        .limit(10)
        .all()
    )

    activity = []

    for ticket in tickets:
        activity.append(
            {
                "message": f"Ticket '{ticket.title}' was created",
                "time": ticket.created_at.strftime("%d %b %Y %I:%M %p"),
            }
        )

    return activity