from typing import Any, Dict

from sqlalchemy.orm import Session

from app.models.user_preferences import UserPreferences


# Only these fields may ever be written through the preferences API.
# This guards against accidental mass-assignment if the request schema changes.
ALLOWED_UPDATE_FIELDS = {
    "email_notifications_enabled",
    "in_app_notifications_enabled",
    "ai_suggestions_enabled",
}


def get_or_create_preferences(db: Session, user_id: int) -> UserPreferences:
    """Return the preferences row for a user, creating defaults on first access."""
    preferences = (
        db.query(UserPreferences)
        .filter(UserPreferences.user_id == user_id)
        .first()
    )

    if preferences is None:
        preferences = UserPreferences(user_id=user_id)
        db.add(preferences)
        db.commit()
        db.refresh(preferences)

    return preferences


def update_preferences(
    db: Session,
    user_id: int,
    updates: Dict[str, Any],
) -> UserPreferences:
    """Apply only explicitly allowed, non-null preference fields for a user."""
    preferences = get_or_create_preferences(db, user_id)

    for field, value in updates.items():
        if field in ALLOWED_UPDATE_FIELDS and value is not None:
            setattr(preferences, field, value)

    db.commit()
    db.refresh(preferences)
    return preferences


# ==========================================
# Preference Checks (read-only, no side effects)
# ==========================================

def is_in_app_notifications_enabled(db: Session, user_id: int) -> bool:
    """Return whether in-app notifications are enabled for a user.

    Users without a preferences row are treated as enabled (the documented
    default). This read never creates a row, so notification production stays
    free of write side effects.
    """
    value = (
        db.query(UserPreferences.in_app_notifications_enabled)
        .filter(UserPreferences.user_id == user_id)
        .scalar()
    )
    return True if value is None else bool(value)


def is_email_notifications_enabled(db: Session, user_id: int) -> bool:
    """Return whether email notifications are enabled for a user.

    Users without a preferences row are treated as enabled (the documented
    default).
    """
    value = (
        db.query(UserPreferences.email_notifications_enabled)
        .filter(UserPreferences.user_id == user_id)
        .scalar()
    )
    return True if value is None else bool(value)
