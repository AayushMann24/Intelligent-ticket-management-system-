"""Conversation Service.

Handles database operations for conversations and messages.
"""

from datetime import datetime, timezone
from typing import Optional, List

from sqlalchemy.orm import Session

from app.models.conversation import Conversation, Message
from app.models.user import User


async def create_conversation(db: Session, title: str, owner_id: int) -> Conversation:
    """Create a new conversation for the given owner."""
    conversation = Conversation(
        title=title,
        owner_id=owner_id,
    )
    db.add(conversation)
    db.flush()
    db.refresh(conversation)
    return conversation


async def get_conversations(db: Session, owner_id: int) -> List[Conversation]:
    """Get all conversations for a given owner."""
    from sqlalchemy import select
    result = await db.execute(
        select(Conversation).filter(Conversation.owner_id == owner_id).order_by(
            Conversation.updated_at.desc()
        )
    )
    return result.scalars().all()


async def get_conversation(db: Session, conversation_id: int, owner_id: int) -> Optional[Conversation]:
    """Get a conversation by ID, verifying ownership."""
    from sqlalchemy import select
    result = await db.execute(
        select(Conversation).filter(
            Conversation.id == conversation_id,
            Conversation.owner_id == owner_id,
        )
    )
    return result.scalar_one_or_none()


async def update_conversation(db: Session, conversation_id: int, new_title: str, owner_id: int) -> Optional[Conversation]:
    """Update a conversation title, verifying ownership."""
    conversation = await get_conversation(db, conversation_id, owner_id)
    if not conversation:
        return None
    conversation.title = new_title
    conversation.updated_at = datetime.now(timezone.utc)
    db.flush()
    db.refresh(conversation)
    return conversation


async def delete_conversation(db: Session, conversation_id: int, owner_id: int) -> bool:
    """Delete (archive) a conversation, verifying ownership."""
    conversation = await get_conversation(db, conversation_id, owner_id)
    if not conversation:
        return False
    conversation.archived = True
    conversation.updated_at = datetime.now(timezone.utc)
    db.flush()
    db.refresh(conversation)
    return True


async def add_message(
    db: Session,
    conversation_id: int,
    role: str,
    content: str,
) -> Message:
    """Add a message to a conversation."""
    message = Message(
        conversation_id=conversation_id,
        role=role,
        content=content,
    )
    db.add(message)
    db.flush()
    db.refresh(message)
    return message


async def get_messages(db: Session, conversation_id: int) -> List[Message]:
    """Get all messages for a conversation, ordered by creation time."""
    from sqlalchemy import select
    result = await db.execute(
        select(Message).filter(
            Message.conversation_id == conversation_id
        ).order_by(Message.id.asc())
    )
    return result.scalars().all()