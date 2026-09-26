from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy.orm import Session, joinedload
from fastapi import HTTPException, status

from app.models.ticket_comment import TicketHistory, HistoryEventType
from app.models.ticket import Ticket
from app.models.user import User
from app.schemas.ticket_comment import (
    TicketHistoryResponse,
    TicketHistoryListResponse,
    TimelineItem,
    TimelineItemType,
    TimelineResponse,
)
from app.services.ticket_utils import (
    _base_ticket_query,
    _can_view_ticket,
    _can_view_ticket_history,
)


# ==========================================
# Base query
# ==========================================
def _base_history_query(db: Session):
    """Base query for history (no soft delete - history is immutable)."""
    return db.query(TicketHistory)


# ==========================================
# Authorization Helpers
# ==========================================
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


# ==========================================
# History Recording
# ==========================================
def record_history(
    db: Session,
    ticket_id: int,
    actor_id: int,
    event_type: HistoryEventType,
    old_value: Optional[str] = None,
    new_value: Optional[str] = None,
    metadata_json: Optional[str] = None,
) -> None:
    """Record a history event. Should be called from service layer when ticket changes."""
    # Don't record if values haven't actually changed
    if old_value == new_value:
        return

    history = TicketHistory(
        ticket_id=ticket_id,
        actor_id=actor_id,
        event_type=event_type,
        old_value=old_value,
        new_value=new_value,
        metadata_json=None,  # Could be used for complex metadata in future
    )

    db.add(history)
    # Note: Don't commit here - let the calling function commit as part of its transaction


def record_multiple_history(
    db: Session,
    ticket_id: int,
    actor_id: int,
    events: List[tuple],
) -> None:
    """Record multiple history events at once."""
    for event_type, old_value, new_value in events:
        if old_value != new_value:
            record_history(db, ticket_id, actor_id, event_type, old_value, new_value)


# ==========================================
# History Retrieval
# ==========================================
def get_ticket_history(
    db: Session,
    ticket_id: int,
    user_id: int,
    user_role: str,
    page: int = 1,
    page_size: int = 20,
) -> "TicketHistoryListResponse":
    from app.schemas.ticket_comment import TicketHistoryResponse, TicketHistoryListResponse

    # Get ticket and check authorization
    ticket = (
        db.query(Ticket)
        .filter(Ticket.id == ticket_id, Ticket.is_deleted == False)
        .first()
    )
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    if not _can_view_ticket_history(user_id, user_role, ticket):
        raise HTTPException(
            status_code=404,
            detail="Ticket not found"
        )

    query = (
        db.query(TicketHistory)
        .filter(TicketHistory.ticket_id == ticket_id)
        .options(joinedload(TicketHistory.actor))
    )

    total = query.count()

    query = query.order_by(TicketHistory.created_at.desc())
    offset = (page - 1) * page_size
    history = query.offset(offset).limit(page_size).all()

    total_pages = (total + page_size - 1) // page_size

    return TicketHistoryListResponse(
        items=[
            TicketHistoryResponse(
                id=h.id,
                ticket_id=h.ticket_id,
                actor_id=h.actor_id,
                actor_name=h.actor.name if h.actor else None,
                event_type=h.event_type.value,
                old_value=h.old_value,
                new_value=h.new_value,
                metadata_json=h.metadata_json,
                created_at=h.created_at,
            )
            for h in history
        ],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


def get_ticket_timeline(
    db: Session,
    ticket_id: int,
    user_id: int,
    user_role: str,
    page: int = 1,
    page_size: int = 50,
) -> "TimelineResponse":
    from app.models.ticket_comment import TicketComment
    from app.schemas.ticket_comment import (
        TimelineItem,
        TimelineItemType,
        TimelineResponse,
    )
    from app.services.ticket_utils import _base_ticket_query, _can_view_ticket

    # Get ticket and check authorization
    ticket = (
        db.query(Ticket)
        .filter(Ticket.id == ticket_id, Ticket.is_deleted == False)
        .first()
    )
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    if not _can_view_ticket(user_id, user_role, ticket):
        raise HTTPException(
            status_code=404,
            detail="Ticket not found"
        )

    timeline_items = []

    # Get history events
    history_query = (
        db.query(TicketHistory)
        .filter(TicketHistory.ticket_id == ticket_id)
        .options(joinedload(TicketHistory.actor))
        .order_by(TicketHistory.created_at.desc())
    )
    history_events = history_query.all()

    for h in history_events:
        timeline_items.append(
            TimelineItem(
                type=TimelineItemType.HISTORY,
                id=h.id,
                actor_id=h.actor_id,
                actor_name=h.actor.name if h.actor else None,
                timestamp=h.created_at,
                event_type=h.event_type.value,
                old_value=h.old_value,
                new_value=h.new_value,
            )
        )

    # Get comments (including internal if user can see them)
    from app.services.ticket_comment_service import _can_view_internal_notes
    from app.services.ticket_utils import _base_ticket_query as base_ticket_query

    ticket_obj = base_ticket_query(db).filter(Ticket.id == ticket_id).first()
    can_see_internal = _can_view_internal_notes(user_id, user_role, ticket_obj)

    comment_query = (
        db.query(TicketComment)
        .filter(TicketComment.ticket_id == ticket_id, TicketComment.is_deleted == False)
        .options(joinedload(TicketComment.author))
    )

    if not can_see_internal:
        comment_query = comment_query.filter(TicketComment.is_internal == False)

    comments = comment_query.order_by(TicketComment.created_at.desc()).all()

    for c in comments:
        item_type = TimelineItemType.INTERNAL_NOTE if c.is_internal else TimelineItemType.COMMENT
        timeline_items.append(
            TimelineItem(
                type=item_type,
                id=c.id,
                actor_id=c.author_id,
                actor_name=c.author.name if c.author else None,
                timestamp=c.created_at,
                body=c.body,
                is_internal=c.is_internal,
            )
        )

    # Get attachments
    from app.models.ticket_comment import TicketAttachment
    attachments = (
        db.query(TicketAttachment)
        .filter(TicketAttachment.ticket_id == ticket_id, TicketAttachment.is_deleted == False)
        .options(joinedload(TicketAttachment.uploader))
        .order_by(TicketAttachment.created_at.desc())
        .all()
    )

    for a in attachments:
        timeline_items.append(
            TimelineItem(
                type=TimelineItemType.ATTACHMENT,
                id=a.id,
                actor_id=a.uploaded_by,
                actor_name=a.uploader.name if a.uploader else None,
                timestamp=a.created_at,
                filename=a.original_filename,
                file_size=a.file_size,
                content_type=a.content_type,
            )
        )

    # Sort all items by timestamp (newest first)
    timeline_items.sort(key=lambda x: x.timestamp, reverse=True)

    # Apply pagination
    total = len(timeline_items)
    offset = (page - 1) * page_size
    paginated_items = timeline_items[offset:offset + page_size]
    total_pages = (total + page_size - 1) // page_size

    return TimelineResponse(
        items=paginated_items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


# Need to import at the top
from typing import List, Optional
from app.models.ticket import Ticket
from app.models.ticket_comment import TicketComment, TicketHistory, HistoryEventType, TicketAttachment