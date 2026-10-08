from datetime import datetime, timezone
from sqlalchemy import (
    Column,
    Integer,
    Text,
    DateTime,
    ForeignKey,
    Index,
    ARRAY,
    Float,
)
from sqlalchemy.orm import relationship
from pgvector.sqlalchemy import Vector

from app.database.connection import Base


class KnowledgeChunk(Base):
    __tablename__ = "knowledge_chunks"

    id = Column(Integer, primary_key=True, index=True)

    article_id = Column(
        Integer,
        ForeignKey("knowledge_articles.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    chunk_index = Column(Integer, nullable=False)

    content = Column(Text, nullable=False)

    embedding = Column(Vector(768), nullable=True)

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

    # Relationships
    article = relationship(
        "KnowledgeArticle",
        foreign_keys=[article_id],
        back_populates="chunks",
    )

    __table_args__ = (
        Index("ix_knowledge_chunks_article_idx", "article_id", "chunk_index"),
        Index("ix_knowledge_chunks_created", "created_at"),
    )