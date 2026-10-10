"""Conversation schemas for API requests and responses."""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class ConversationCreate(BaseModel):
    """Request to create a new conversation."""
    title: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Conversation title",
    )


class ConversationTitleUpdate(BaseModel):
    """Request to update a conversation title."""
    title: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="New conversation title",
    )


class ConversationResponse(BaseModel):
    """Response for conversation data."""
    id: int
    title: str
    owner_id: int
    archived: bool
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True,
    }


class MessageCreate(BaseModel):
    """Request to create a new message."""
    role: str = Field(
        ...,
        description="Message role (user or assistant)",
    )
    content: str = Field(
        ...,
        min_length=1,
        max_length=5000,
        description="Message content",
    )


class MessageResponse(BaseModel):
    """Response for message data."""
    id: int
    conversation_id: int
    role: str
    content: str
    created_at: datetime
    citation_metadata: Optional[dict] = None

    model_config = {
        "from_attributes": True,
    }