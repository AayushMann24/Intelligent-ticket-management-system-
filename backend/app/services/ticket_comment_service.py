from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy.orm import Session, joinedload
from fastapi import HTTPException, status

from app.models.ticket_comment import TicketComment, HistoryEventType
from app.models.ticket import Ticket
from app.models.user import User
from app.schemas.ticket_comment import (
    TicketCommentCreate,
    TicketCommentUpdate,
    TicketCommentResponse,
    TicketCommentListResponse,
)
from app.services.ticket_utils import (
    _base_ticket_query,
    _can_view_ticket,
    _can_view_ticket_comments,
    _can_view_internal_notes,
    _can_create_comment,
    _can_create_internal_note,
    _can_delete_comment,
)
from app.services.sla_service import mark_response_sla_met

# ==========================================
# Base query with soft delete filter
# ==========================================
def _base_comment_query(db: Session):
    """Base query that excludes soft-deleted comments."""
    return db.query(TicketComment).filter(TicketComment.is_deleted == False)


def _base_history_query(db: Session):
    """Base query for history (no soft delete)."""
    return db.query(TicketComment).filter(TicketComment.is_deleted == False)


# ==========================================
# Authorization Helpers
# ==========================================
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


def _can_delete_comment(user_id: int, user_role: str, comment: TicketComment, ticket: Ticket) -> bool:
    """Check if user can delete a comment."""
    # Admin can delete any comment
    if user_role == "Admin":
        return True
    # Author can delete their own comment
    if comment.author_id == user_id:
        return True
    return False


# ==========================================
# Comment CRUD
# ==========================================
def create_comment(
    db: Session,
    ticket_id: int,
    comment_data: TicketCommentCreate,
    user_id: int,
    user_role: str,
) -> TicketComment:
    # Get ticket and check authorization
    ticket = _base_ticket_query(db).filter(Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    if not _can_create_comment(user_id, user_role, ticket):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to comment on this ticket"
        )

    # Check internal note permission
    if comment_data.is_internal and not _can_create_internal_note(user_id, user_role):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to create internal notes"
        )

    new_comment = TicketComment(
        ticket_id=ticket_id,
        author_id=user_id,
        body=comment_data.body,
        is_internal=comment_data.is_internal,
    )

    db.add(new_comment)
    db.commit()
    db.refresh(new_comment)

    # Mark response SLA as met when technician/admin responds (first response)
    if user_role in ["Admin", "Technician"]:
        mark_response_sla_met(db, ticket)

    return new_comment


def get_comments(
    db: Session,
    ticket_id: int,
    user_id: int,
    user_role: str,
    page: int = 1,
    page_size: int = 20,
    include_internal: bool = False,
) -> TicketCommentListResponse:
    # Get ticket and check authorization
    ticket = _base_ticket_query(db).filter(Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    if not _can_view_ticket_comments(user_id, user_role, ticket):
        raise HTTPException(
            status_code=404,
            detail="Ticket not found"
        )

    query = _base_comment_query(db).filter(TicketComment.ticket_id == ticket_id)

    # Filter internal notes based on permission
    if not include_internal or not _can_view_internal_notes(user_id, user_role, ticket):
        query = query.filter(TicketComment.is_internal == False)

    # Get total count
    total = query.count()

    # Apply ordering and pagination
    query = query.order_by(TicketComment.created_at.desc())
    offset = (page - 1) * page_size
    comments = query.offset(offset).limit(page_size).all()

    total_pages = (total + page_size - 1) // page_size

    # Build response with author names
    author_ids = {c.author_id for c in comments}
    authors = db.query(User).filter(User.id.in_(author_ids)).all() if author_ids else []
    author_map = {a.id: a.name for a in authors}

    return TicketCommentListResponse(
        items=[
            TicketCommentResponse(
                id=c.id,
                ticket_id=c.ticket_id,
                author_id=c.author_id,
                author_name=author_map.get(c.author_id),
                body=c.body,
                is_internal=c.is_internal,
                created_at=c.created_at,
                updated_at=c.updated_at,
            )
            for c in comments
        ],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


def get_comment_by_id(
    db: Session,
    comment_id: int,
    user_id: int,
    user_role: str,
) -> TicketComment:
    comment = (
        _base_comment_query(db)
        .filter(TicketComment.id == comment_id)
        .first()
    )

    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")

    # Check ticket access
    ticket = _base_ticket_query(db).filter(Ticket.id == comment.ticket_id).first()
    if not ticket or not _can_view_ticket_comments(user_id, user_role, ticket):
        raise HTTPException(status_code=404, detail="Comment not found")

    # Check internal note visibility
    if comment.is_internal and not _can_view_internal_notes(user_id, user_role, ticket):
        raise HTTPException(status_code=404, detail="Comment not found")

    return comment


def update_comment(
    db: Session,
    comment_id: int,
    comment_data: TicketCommentUpdate,
    user_id: int,
    user_role: str,
) -> TicketComment:
    comment = get_comment_by_id(db, comment_id, user_id, user_role)

    # Check delete/update permission
    if not _can_delete_comment(user_id, user_role, comment, None):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this comment"
        )

    # Check internal note permission for updates
    if comment_data.is_internal is not None and comment_data.is_internal:
        if not _can_create_internal_note(user_id, user_role):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to create internal notes"
            )

    if comment_data.body is not None:
        comment.body = comment_data.body
    if comment_data.is_internal is not None:
        comment.is_internal = comment_data.is_internal

    comment.updated_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(comment)

    return comment


def delete_comment(
    db: Session,
    comment_id: int,
    user_id: int,
    user_role: str,
):
    comment = get_comment_by_id(db, comment_id, user_id, user_role)

    if not _can_delete_comment(user_id, user_role, comment, None):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this comment"
        )

    comment.is_deleted = True
    comment.updated_at = datetime.now(timezone.utc)

    db.commit()

    return {"message": "Comment deleted successfully"}


# Need to import datetime at the top
from datetime import datetime, timezone