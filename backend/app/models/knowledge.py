from datetime import datetime, timezone
from enum import Enum as PyEnum

from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    Boolean,
    ForeignKey,
    Index,
    Enum,
)
from sqlalchemy.orm import relationship

from app.database.connection import Base


class ArticleStatus(str, PyEnum):
    DRAFT = "DRAFT"
    PUBLISHED = "PUBLISHED"
    ARCHIVED = "ARCHIVED"


class ArticleCategory(str, PyEnum):
    HARDWARE = "Hardware"
    SOFTWARE = "Software"
    NETWORK = "Network"
    SECURITY = "Security"
    ACCOUNT = "Account"
    TROUBLESHOOTING = "Troubleshooting"
    PROCEDURES = "Procedures"
    OTHER = "Other"


class KnowledgeArticle(Base):
    __tablename__ = "knowledge_articles"

    id = Column(Integer, primary_key=True, index=True)

    title = Column(String(255), nullable=False)

    slug = Column(String(255), unique=True, nullable=False, index=True)

    summary = Column(Text, nullable=False)

    content = Column(Text, nullable=False)

    category = Column(
        Enum(ArticleCategory, name="article_category_enum", native_enum=False),
        nullable=False,
        default=ArticleCategory.OTHER,
        index=True,
    )

    status = Column(
        Enum(ArticleStatus, name="article_status_enum", native_enum=False),
        nullable=False,
        default=ArticleStatus.DRAFT,
        index=True,
    )

    author_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )

    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True,
    )

    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    published_at = Column(
        DateTime(timezone=True),
        nullable=True,
        index=True,
    )

    is_deleted = Column(
        Boolean,
        default=False,
        nullable=False,
        index=True,
    )

    # Relationships
    author = relationship(
        "User",
        foreign_keys=[author_id],
        back_populates="knowledge_articles",
    )

    __table_args__ = (
        Index("ix_knowledge_status_category", "status", "category"),
        Index("ix_knowledge_deleted_created", "is_deleted", "created_at"),
        Index("ix_knowledge_published_created", "status", "published_at"),
    )


# Add to User model: knowledge_articles relationship
# This is added here to avoid circular imports