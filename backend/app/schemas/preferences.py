from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class PreferencesResponse(BaseModel):
    """Response model for a user's preferences."""

    email_notifications_enabled: bool
    in_app_notifications_enabled: bool
    ai_suggestions_enabled: bool
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class PreferencesUpdate(BaseModel):
    """Partial update model for a user's preferences.

    All fields are optional; only fields explicitly provided in the request
    body are applied. The service additionally filters to an allow-list.
    """

    email_notifications_enabled: Optional[bool] = None
    in_app_notifications_enabled: Optional[bool] = None
    ai_suggestions_enabled: Optional[bool] = None
