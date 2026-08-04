from langchain_core.tools import tool

from app.database.connection import SessionLocal

from app.services.dashboard_service import (
    get_dashboard_summary,
    get_recent_tickets,
    get_priority_summary,
    get_ticket_trend,
)


# ==========================================
# Dashboard Summary
# ==========================================

@tool
def dashboard_summary_tool():
    """
    Returns the dashboard summary.
    """

    db = SessionLocal()

    try:
        return get_dashboard_summary(db)

    finally:
        db.close()


# ==========================================
# Recent Tickets
# ==========================================

@tool
def recent_tickets_tool():
    """
    Returns the five most recent tickets.
    """

    db = SessionLocal()

    try:

        tickets = get_recent_tickets(db)

        return [
            {
                "id": t.id,
                "title": t.title,
                "status": t.status,
                "priority": t.priority,
            }
            for t in tickets
        ]

    finally:
        db.close()


# ==========================================
# Priority Summary
# ==========================================

@tool
def priority_summary_tool():
    """
    Returns ticket count by priority.
    """

    db = SessionLocal()

    try:
        return get_priority_summary(db)

    finally:
        db.close()