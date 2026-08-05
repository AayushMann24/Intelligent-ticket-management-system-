from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.user import User
from app.models.ticket import Ticket


def get_technician_workload(db: Session):
    """
    Returns all technicians with their
    specialization and current workload.
    """

    result = (
        db.query(
            User.id,
            User.name,
            User.specialization,
            func.count(Ticket.id).label("workload"),
        )
        .outerjoin(
            Ticket,
            User.id == Ticket.assigned_to,
        )
        .filter(
            User.role == "Technician"
        )
        .group_by(
            User.id,
            User.name,
            User.specialization,
        )
        .all()
    )

    technicians = []

    for row in result:

        technicians.append(
            {
                "id": row.id,
                "name": row.name,
                "specialization": row.specialization,
                "workload": row.workload,
            }
        )

    return technicians