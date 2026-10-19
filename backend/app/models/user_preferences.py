from datetime import datetime, timezone

from sqlalchemy import Column, Integer, Boolean, DateTime, ForeignKey

from app.database.connection import Base


class UserPreferences(Base):
    """Per-user notification and feature preferences.

    One-to-one with ``users`` (enforced by the unique ``user_id`` foreign key).
    Rows are created lazily on first access via the preferences service so that
    existing users do not require a backfill.
    """

    __tablename__ = "user_preferences"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )

    email_notifications_enabled = Column(
        Boolean,
        nullable=False,
        default=True,
    )

    in_app_notifications_enabled = Column(
        Boolean,
        nullable=False,
        default=True,
    )

    ai_suggestions_enabled = Column(
        Boolean,
        nullable=False,
        default=True,
    )

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
