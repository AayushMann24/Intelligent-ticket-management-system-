from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Index
from sqlalchemy.orm import relationship

from app.database.connection import Base


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id = Column(Integer, primary_key=True, index=True)
    
    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )
    
    token_hash = Column(
        String,
        nullable=False,
        unique=True,
        index=True,
    )
    
    # For rotation: the new token that replaced this one
    replaced_by_token_hash = Column(
        String,
        nullable=True,
        index=True,
    )
    
    # Track if token has been revoked/rotated
    is_revoked = Column(
        Boolean,
        default=False,
        nullable=False,
        index=True,
    )
    
    # Track if token was reused (potential theft)
    is_reused = Column(
        Boolean,
        default=False,
        nullable=False,
    )
    
    expires_at = Column(
        DateTime(timezone=True),
        nullable=False,
        index=True,
    )
    
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    
    # Relationship to user
    user = relationship("User")
    
    __table_args__ = (
        Index("ix_refresh_tokens_user_revoked", "user_id", "is_revoked"),
        Index("ix_refresh_tokens_expires_revoked", "expires_at", "is_revoked"),
    )