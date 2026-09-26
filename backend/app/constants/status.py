from enum import Enum


class TicketStatus(str, Enum):
    OPEN = "Open"
    ASSIGNED = "Assigned"
    IN_PROGRESS = "In Progress"
    PENDING = "Pending"
    RESOLVED = "Resolved"
    CLOSED = "Closed"


# For backwards compatibility
TICKET_STATUS = [status.value for status in TicketStatus]