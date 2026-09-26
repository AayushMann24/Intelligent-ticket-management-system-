from datetime import datetime
from enum import Enum
from typing import Optional, List
from pydantic import BaseModel, ConfigDict


class HistoryEventType(str, Enum):
    TICKET_CREATED = "TICKET_CREATED"
    STATUS_CHANGED = "STATUS_CHANGED"
    PRIORITY_CHANGED = "PRIORITY_CHANGED"
    ASSIGNED = "ASSIGNED"
    UNASSIGNED = "UNASSIGNED"
    CATEGORY_CHANGED = "CATEGORY_CHANGED"
    SUBCATEGORY_CHANGED = "SUBCATEGORY_CHANGED"
    TITLE_CHANGED = "TITLE_CHANGED"
    DESCRIPTION_CHANGED = "DESCRIPTION_CHANGED"
    COMMENT_ADDED = "COMMENT_ADDED"
    INTERNAL_NOTE_ADDED = "INTERNAL_NOTE_ADDED"
    ATTACHMENT_ADDED = "ATTACHMENT_ADDED"
    ATTACHMENT_REMOVED = "ATTACHMENT_REMOVED"
    TICKET_REOPENED = "TICKET_REOPENED"
    TICKET_RESOLVED = "TICKET_RESOLVED"
    TICKET_CLOSED = "TICKET_CLOSED"
    TICKET_REOPENED_AFTER_CLOSURE = "TICKET_REOPENED_AFTER_CLOSURE"
    PRIORITY_REASON_CHANGED = "PRIORITY_REASON_CHANGED"
    ASSIGNMENT_REASON_CHANGED = "ASSIGNMENT_REASON_CHANGED"


# ================================
# TicketComment Schemas
# ================================
class TicketCommentCreate(BaseModel):
    body: str
    is_internal: bool = False


class TicketCommentUpdate(BaseModel):
    body: Optional[str] = None
    is_internal: Optional[bool] = None


class TicketCommentResponse(BaseModel):
    id: int
    ticket_id: int
    author_id: int
    author_name: Optional[str] = None
    body: str
    is_internal: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TicketCommentListResponse(BaseModel):
    items: List["TicketCommentResponse"]
    total: int
    page: int
    page_size: int
    total_pages: int


# ================================
# TicketHistory Schemas
# ================================
class TicketHistoryResponse(BaseModel):
    id: int
    ticket_id: int
    actor_id: int
    actor_name: Optional[str] = None
    event_type: str
    old_value: Optional[str] = None
    new_value: Optional[str] = None
    metadata_json: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TicketHistoryListResponse(BaseModel):
    items: List["TicketHistoryResponse"]
    total: int
    page: int
    page_size: int
    total_pages: int


# ================================
# TicketAttachment Schemas
# ================================
class TicketAttachmentCreate(BaseModel):
    ticket_id: int
    original_filename: str
    stored_filename: str
    content_type: str
    file_size: int


class TicketAttachmentResponse(BaseModel):
    id: int
    ticket_id: int
    uploaded_by: int
    uploader_name: Optional[str] = None
    original_filename: str
    stored_filename: str
    content_type: str
    file_size: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TicketAttachmentListResponse(BaseModel):
    items: List["TicketAttachmentResponse"]
    total: int
    page: int
    page_size: int
    total_pages: int


# ================================
# Timeline Schema (Combined view)
# ================================
class TimelineItemType(str, Enum):
    HISTORY = "HISTORY"
    COMMENT = "COMMENT"
    INTERNAL_NOTE = "INTERNAL_NOTE"
    ATTACHMENT = "ATTACHMENT"


class TimelineItem(BaseModel):
    type: TimelineItemType
    id: int
    actor_id: int
    actor_name: Optional[str] = None
    timestamp: datetime
    # For history events
    event_type: Optional[str] = None
    old_value: Optional[str] = None
    new_value: Optional[str] = None
    # For comments
    body: Optional[str] = None
    is_internal: Optional[bool] = None
    # For attachments
    filename: Optional[str] = None
    file_size: Optional[int] = None
    content_type: Optional[str] = None


class TimelineResponse(BaseModel):
    items: List[TimelineItem]
    total: int
    page: int
    page_size: int
    total_pages: int


# Need to add these at the bottom since they reference each other
from typing import List, Optional