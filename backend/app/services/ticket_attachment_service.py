import os
import uuid
from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy.orm import Session, joinedload
from fastapi import HTTPException, status, UploadFile
from pathlib import Path

from app.models.ticket_comment import TicketAttachment
from app.models.ticket import Ticket
from app.models.user import User
from app.schemas.ticket_comment import (
    TicketAttachmentResponse,
    TicketAttachmentListResponse,
)
from app.services.ticket_utils import (
    _base_ticket_query,
    _can_view_ticket,
    _can_upload_attachment,
    _can_view_attachment,
    _can_delete_attachment,
)
from app.config import settings


# ==========================================
# Configuration
# ==========================================

# File storage directory (outside source code)
STORAGE_DIR = Path(settings.upload_dir if hasattr(settings, 'upload_dir') else "./uploads")
STORAGE_DIR.mkdir(parents=True, exist_ok=True)

# Allowed file types
ALLOWED_CONTENT_TYPES = {
    "application/pdf",
    "image/jpeg",
    "image/png",
    "image/gif",
    "image/webp",
    "text/plain",
    "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/vnd.ms-excel",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "application/zip",
    "application/x-zip-compressed",
}

# Max file size (10 MB)
MAX_FILE_SIZE = 10 * 1024 * 1024


# ==========================================
# Base query
# ==========================================
def _base_attachment_query(db: Session):
    """Base query that excludes soft-deleted attachments."""
    return db.query(TicketAttachment).filter(TicketAttachment.is_deleted == False)


# ==========================================
# Authorization Helpers
# ==========================================
def _can_upload_attachment(user_id: int, user_role: str, ticket: Ticket) -> bool:
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


def _can_view_attachment(user_id: int, user_role: str, ticket: Ticket) -> bool:
    """Check if user can view/download attachments."""
    return (
        user_role == "Admin" or
        ticket.created_by == user_id or
        ticket.assigned_to == user_id
    )


def _can_delete_attachment(user_id: int, user_role: str, attachment: TicketAttachment, ticket: Ticket) -> bool:
    """Check if user can delete an attachment."""
    # Admin can delete any
    if user_role == "Admin":
        return True
    # Uploader can delete their own
    if attachment.uploaded_by == user_id:
        return True
    return False


# ==========================================
# File Validation
# ==========================================
def validate_file(file: UploadFile) -> None:
    """Validate uploaded file."""
    # Check content type
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"File type not allowed. Allowed types: {', '.join(ALLOWED_CONTENT_TYPES)}"
        )

    # Check file size (read to check)
    file.file.seek(0, 2)  # Seek to end
    file_size = file.file.tell()
    file.file.seek(0)  # Reset to beginning

    if file_size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File size exceeds maximum allowed size of {MAX_FILE_SIZE // (1024*1024)} MB"
        )


def generate_stored_filename(original_filename: str) -> str:
    """Generate a unique stored filename."""
    ext = Path(original_filename).suffix
    unique_name = f"{uuid.uuid4().hex}{ext}"
    return unique_name


# ==========================================
# Attachment CRUD
# ==========================================
def upload_attachment(
    db: Session,
    ticket_id: int,
    file: UploadFile,
    user_id: int,
    user_role: str,
) -> TicketAttachment:
    # Get ticket and check authorization
    ticket = _base_ticket_query(db).filter(Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    if not _can_upload_attachment(user_id, user_role, ticket):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to upload attachments to this ticket"
        )

    # Validate file
    validate_file(file)

    # Generate stored filename
    stored_filename = generate_stored_filename(file.filename)

    # Save file to disk
    file_path = STORAGE_DIR / stored_filename
    content = file.file.read()
    file_path.write_bytes(content)
    file_size = len(content)

    # Create attachment record
    attachment = TicketAttachment(
        ticket_id=ticket_id,
        uploaded_by=user_id,
        original_filename=file.filename,
        stored_filename=stored_filename,
        content_type=file.content_type,
        file_size=file_size,
    )

    db.add(attachment)
    db.commit()
    db.refresh(attachment)

    return attachment


def get_attachments(
    db: Session,
    ticket_id: int,
    user_id: int,
    user_role: str,
    page: int = 1,
    page_size: int = 20,
) -> "TicketAttachmentListResponse":
    from app.schemas.ticket_comment import TicketAttachmentResponse, TicketAttachmentListResponse

    # Get ticket and check authorization
    ticket = _base_ticket_query(db).filter(Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    if not _can_view_attachment(user_id, user_role, ticket):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view attachments for this ticket"
        )

    query = _base_attachment_query(db).filter(TicketAttachment.ticket_id == ticket_id)

    total = query.count()

    query = query.order_by(TicketAttachment.created_at.desc())
    offset = (page - 1) * page_size
    attachments = query.offset(offset).limit(page_size).all()

    total_pages = (total + page_size - 1) // page_size

    # Build response with uploader names
    uploader_ids = {a.uploaded_by for a in attachments}
    uploaders = db.query(User).filter(User.id.in_(uploader_ids)).all() if uploader_ids else []
    uploader_map = {u.id: u.name for u in uploaders}

    return TicketAttachmentListResponse(
        items=[
            TicketAttachmentResponse(
                id=a.id,
                ticket_id=a.ticket_id,
                uploaded_by=a.uploaded_by,
                uploader_name=uploader_map.get(a.uploaded_by),
                original_filename=a.original_filename,
                stored_filename=a.stored_filename,
                content_type=a.content_type,
                file_size=a.file_size,
                created_at=a.created_at,
            )
            for a in attachments
        ],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


def get_attachment_by_id(
    db: Session,
    attachment_id: int,
    user_id: int,
    user_role: str,
) -> TicketAttachment:
    attachment = (
        _base_attachment_query(db)
        .filter(TicketAttachment.id == attachment_id)
        .first()
    )

    if not attachment:
        raise HTTPException(status_code=404, detail="Attachment not found")

    # Check ticket access
    ticket = _base_ticket_query(db).filter(Ticket.id == attachment.ticket_id).first()
    if not ticket or not _can_view_attachment(user_id, user_role, ticket):
        raise HTTPException(status_code=404, detail="Attachment not found")

    return attachment


def download_attachment(
    db: Session,
    attachment_id: int,
    user_id: int,
    user_role: str,
):
    attachment = get_attachment_by_id(db, attachment_id, user_id, user_role)

    file_path = STORAGE_DIR / attachment.stored_filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found on disk")

    from fastapi.responses import FileResponse
    return FileResponse(
        path=file_path,
        filename=attachment.original_filename,
        media_type=attachment.content_type,
    )


def delete_attachment(
    db: Session,
    attachment_id: int,
    user_id: int,
    user_role: str,
):
    attachment = get_attachment_by_id(db, attachment_id, user_id, user_role)

    if not _can_delete_attachment(user_id, user_role, attachment, None):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this attachment"
        )

    # Soft delete
    attachment.is_deleted = True
    db.commit()

    return {"message": "Attachment deleted successfully"}


# Need to import at the top
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional
from app.models.ticket import Ticket
from app.models.user import User
from app.models.ticket_comment import TicketAttachment