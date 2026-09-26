from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.ticket import Ticket
from app.models.user import User


def _base_ticket_query(db: Session):
    """Base query that excludes soft-deleted tickets."""
    return db.query(Ticket).filter(Ticket.is_deleted == False)


def _base_user_query(db: Session):
    """Base query that excludes soft-deleted users."""
    return db.query(User).filter(User.is_deleted == False)


def _can_view_ticket(user_id: int, user_role: str, ticket: Ticket) -> bool:
    """Check if user can view a ticket."""
    # Admin can view any ticket
    if user_role == "Admin":
        return True
    # Creator can view their own ticket
    if ticket.created_by == user_id:
        return True
    # Assignee can view their assigned ticket
    if ticket.assigned_to == user_id:
        return True
    return False


def _can_modify_ticket(user_id: int, user_role: str, ticket: Ticket) -> bool:
    """Check if user can modify a ticket."""
    # Admin can modify any ticket
    if user_role == "Admin":
        return True
    # Creator can modify their own ticket
    if ticket.created_by == user_id:
        return True
    # Assignee can modify their assigned ticket
    if ticket.assigned_to == user_id:
        return True
    return False


def _can_delete_ticket(user_id: int, user_role: str, ticket: Ticket) -> bool:
    """Check if user can delete a ticket."""
    # Only Admin can delete tickets
    if user_role == "Admin":
        return True
    return False


def _can_view_ticket_history(user_id: int, user_role: str, ticket: Ticket) -> bool:
    """Check if user can view ticket history."""
    # Admin can view all history
    if user_role == "Admin":
        return True
    # Creator can view their ticket's history
    if ticket.created_by == user_id:
        return True
    # Assignee can view their ticket's history
    if ticket.assigned_to == user_id:
        return True
    return False


def _can_view_ticket_comments(user_id: int, user_role: str, ticket: Ticket) -> bool:
    """Check if user can view ticket comments (including internal)."""
    # Admin can view all
    if user_role == "Admin":
        return True
    # Creator can view all comments
    if ticket.created_by == user_id:
        return True
    # Assignee can view all comments
    if ticket.assigned_to == user_id:
        return True
    return False


def _can_view_internal_notes(user_id: int, user_role: str, ticket: Ticket) -> bool:
    """Check if user can view internal notes."""
    # Only Admin and Technician can view internal notes
    if user_role in ["Admin", "Technician"]:
        # But they must have access to the ticket
        return _can_view_ticket_comments(user_id, user_role, ticket)
    return False


def _can_create_comment(user_id: int, user_role: str, ticket: Ticket) -> bool:
    """Check if user can create a comment on this ticket."""
    return _can_view_ticket_comments(user_id, user_role, ticket)


def _can_create_internal_note(user_id: int, user_role: str) -> bool:
    """Check if user can create an internal note."""
    return user_role in ["Admin", "Technician"]


def _can_delete_comment(user_id: int, user_role: str, comment, ticket) -> bool:
    """Check if user can delete a comment."""
    # Admin can delete any comment
    if user_role == "Admin":
        return True
    # Author can delete their own comment
    if comment.author_id == user_id:
        return True
    return False


def _can_upload_attachment(user_id: int, user_role: str, ticket) -> bool:
    """Check if user can upload attachments to this ticket."""
    # Admin can upload to any ticket
    if user_role == "Admin":
        return True
    # Creator can upload
    if ticket.created_by == user_id:
        return True
    # Assignee can upload
    if ticket.assigned_to == user_id:
        return True
    return False


def _can_view_attachment(user_id: int, user_role: str, ticket) -> bool:
    """Check if user can view/download attachments."""
    return (
        user_role == "Admin" or
        ticket.created_by == user_id or
        ticket.assigned_to == user_id
    )


def _can_delete_attachment(user_id: int, user_role: str, attachment, ticket) -> bool:
    """Check if user can delete an attachment."""
    # Admin can delete any
    if user_role == "Admin":
        return True
    # Uploader can delete their own
    if attachment.uploaded_by == user_id:
        return True
    return False


def _can_upload_attachment(user_id: int, user_role: str, ticket) -> bool:
    """Check if user can upload attachments to this ticket."""
    # Admin can upload to any ticket
    if user_role == "Admin":
        return True
    # Creator can upload
    if ticket.created_by == user_id:
        return True
    # Assignee can upload
    if ticket.assigned_to == user_id:
        return True
    return False