from datetime import datetime, timezone

from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Boolean,
    DateTime,
    ForeignKey,
    Index,
    JSON,
)

from sqlalchemy.orm import relationship

from app.database.connection import Base


class Conversation(Base):
    __tablename__ = "conversations"

    # =====================================================
    # Primary Information
    # =====================================================

    id = Column(Integer, primary_key=True, index=True)

    title = Column(String, nullable=False)

    # =====================================================
    # Owner Information
    # =====================================================

    owner_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )

    # =====================================================
    # State
    # =====================================================

    archived = Column(
        Boolean,
        default=False,
        nullable=False,
        index=True,
    )

    # =====================================================
    # Timestamps
    # =====================================================

    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # =====================================================
    # Relationships
    # =====================================================

    owner = relationship(
        "User",
        foreign_keys="Conversation.owner_id",
        back_populates="conversations",
    )

    messages = relationship(
        "Message",
        back_populates="conversation",
        cascade="all, delete-orphan",
        lazy="select",
    )

    __table_args__ = (
        Index("ix_conversations_owner_archived", "owner_id", "archived"),
    )


class Message(Base):
    __tablename__ = "messages"

    # =====================================================
    # Primary Information
    # =====================================================

    id = Column(Integer, primary_key=True, index=True)

    conversation_id = Column(
        Integer,
        ForeignKey("conversations.id"),
        nullable=False,
        index=True,
    )

    role = Column(
        String,
        nullable=False,
    )

    content = Column(
        Text,
        nullable=False,
    )

    # =====================================================
    # Citation/Response Metadata
    # =====================================================

    citation_metadata = Column(
        JSON,
        nullable=True,
    )

    # =====================================================
    # Timestamps
    # =====================================================

    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # =====================================================
    # Relationships
    # =====================================================

    conversation = relationship(
        "Conversation",
        foreign_keys="Message.conversation_id",
        back_populates="messages",
    )

    __table_args__ = (
        Index("ix_messages_conversation_order", "conversation_id", "id"),
    )