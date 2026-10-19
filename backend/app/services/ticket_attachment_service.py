import uuid
from pathlib import Path
from typing import Union

from fastapi import HTTPException, status, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.models.ticket_comment import TicketAttachment
from app.models.ticket import Ticket
from app.models.user import User
from app.schemas.ticket_comment import (
    TicketAttachmentResponse,
    TicketAttachmentListResponse,
)
from app.services.ticket_utils import (
    _base_ticket_query,
    _can_upload_attachment,
    _can_view_attachment,
    _can_delete_attachment,
)
from app.config import settings


# ==========================================
# Configuration
# ==========================================

# File storage directory (outside source code)
STORAGE_DIR = Path(settings.upload_dir if hasattr(settings, "upload_dir") else "./uploads")
STORAGE_DIR.mkdir(parents=True, exist_ok=True)

# Allowed file types mapped by extension. Content type and extension must agree,
# which prevents a file being stored with a misleading extension. SVG is
# intentionally excluded because it can carry active content.
ALLOWED_EXTENSIONS: dict[str, set[str]] = {
    ".pdf": {"application/pdf"},
    ".jpg": {"image/jpeg"},
    ".jpeg": {"image/jpeg"},
    ".png": {"image/png"},
    ".gif": {"image/gif"},
    ".webp": {"image/webp"},
    ".txt": {"text/plain"},
    ".doc": {"application/msword"},
    ".docx": {
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    },
    ".xls": {"application/vnd.ms-excel"},
    ".xlsx": {
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    },
    ".zip": {"application/zip", "application/x-zip-compressed"},
}

ALLOWED_CONTENT_TYPES: set[str] = set().union(*ALLOWED_EXTENSIONS.values())

# Max file size, configurable via settings (defaults to 10 MB).
MAX_FILE_SIZE = settings.max_upload_size_mb * 1024 * 1024


# ==========================================
# Base query
# ==========================================
def _base_attachment_query(db: Session):
    """Base query that excludes soft-deleted attachments."""
    return db.query(TicketAttachment).filter(TicketAttachment.is_deleted == False)


# ==========================================
# File Validation
# ==========================================
def validate_file(file: UploadFile) -> int:
    """Validate an uploaded file and return its size in bytes.

    Rejects unsupported content types, unknown/missing extensions, and
    extension/content-type mismatches. SVG is not part of the allow-list.
    """
    content_type = (file.content_type or "").lower()

    if content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"File type not allowed. Allowed types: {', '.join(sorted(ALLOWED_CONTENT_TYPES))}",
        )

    filename = file.filename or ""
    extension = Path(filename).suffix.lower()

    if not extension:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="File must have a supported extension",
        )

    allowed_for_extension = ALLOWED_EXTENSIONS.get(extension)
    if not allowed_for_extension:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"File extension '{extension}' is not allowed",
        )

    if content_type not in allowed_for_extension:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="File extension does not match its content type",
        )

    # Determine size without reading the whole file into memory.
    file.file.seek(0, 2)  # Seek to end
    file_size = file.file.tell()
    file.file.seek(0)  # Reset to beginning

    if file_size == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File is empty",
        )

    if file_size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File size exceeds maximum allowed size of {settings.max_upload_size_mb} MB",
        )

    return file_size


def generate_stored_filename(original_filename: str) -> str:
    """Generate a unique stored filename, keeping only the original extension."""
    extension = Path(original_filename).suffix.lower()
    return f"{uuid.uuid4().hex}{extension}"


def _storage_path(stored_filename: str) -> Path:
    """Resolve a stored filename inside STORAGE_DIR, guarding against traversal."""
    base = STORAGE_DIR.resolve()
    resolved = (base / stored_filename).resolve()
    if resolved != base and base not in resolved.parents:
        raise HTTPException(status_code=404, detail="File not found")
    return resolved


def _remove_stored_file(stored_filename: str) -> None:
    """Best-effort removal of a stored file.

    A deleted attachment must not fail because the physical file is already
    gone or the filesystem is unavailable: the logical (soft) deletion has
    already been committed by the time this runs.
    """
    try:
        file_path = _storage_path(stored_filename)
        if file_path.exists():
            file_path.unlink()
    except (OSError, HTTPException):
        pass


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
            detail="Not authorized to upload attachments to this ticket",
        )

    # Validate file (raises on unsupported type, mismatch, empty, or oversized)
    file_size = validate_file(file)

    # Generate stored filename and persist to disk
    stored_filename = generate_stored_filename(file.filename or "")
    file_path = _storage_path(stored_filename)
    content = file.file.read()
    file_path.write_bytes(content)

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
) -> TicketAttachmentListResponse:
    # Get ticket and check authorization
    ticket = _base_ticket_query(db).filter(Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    if not _can_view_attachment(user_id, user_role, ticket):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view attachments for this ticket",
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
    ticket_id: Union[int, None] = None,
) -> TicketAttachment:
    attachment = (
        _base_attachment_query(db)
        .filter(TicketAttachment.id == attachment_id)
        .first()
    )

    if not attachment:
        raise HTTPException(status_code=404, detail="Attachment not found")

    # The attachment must belong to the ticket referenced in the URL. Return 404
    # rather than 403 so a mismatch does not leak whether the resource exists.
    if ticket_id is not None and attachment.ticket_id != ticket_id:
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
    ticket_id: Union[int, None] = None,
):
    attachment = get_attachment_by_id(
        db, attachment_id, user_id, user_role, ticket_id=ticket_id
    )

    file_path = _storage_path(attachment.stored_filename)
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found on disk")

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
    ticket_id: Union[int, None] = None,
):
    attachment = get_attachment_by_id(
        db, attachment_id, user_id, user_role, ticket_id=ticket_id
    )

    if not _can_delete_attachment(user_id, user_role, attachment, None):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this attachment",
        )

    # Soft delete (preserve the existing convention), then remove the file.
    attachment.is_deleted = True
    db.commit()

    _remove_stored_file(attachment.stored_filename)

    return {"message": "Attachment deleted successfully"}
