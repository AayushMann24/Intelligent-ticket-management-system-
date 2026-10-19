"""Tests for user preferences and password change (Functional Settings backend)."""
import asyncio
import inspect

import pytest

from app.config import settings
from app.dependencies.rate_limit import rate_limit_dependency
from app.models.escalation import EscalationEventType, EscalationRecord
from app.models.notification import Notification, NotificationType
from app.models.ticket import Ticket
from app.models.user import User
from app.models.user_preferences import UserPreferences
from app.services import email_provider as email_provider_module
from app.services.email_provider import (
    EmailMessage,
    EmailProvider,
    EmailResult,
    MockEmailProvider,
    set_email_provider,
)
from app.services.escalation_service import (
    create_escalation_notification,
    create_escalation_rule,
    process_escalation,
    send_escalation_email,
)
from app.services.notification_service import create_notification
from app.utils.rate_limiter import rate_limiter
from app.utils.security import hash_password


# ==================================================
# Helpers
# ==================================================

@pytest.fixture(autouse=True)
def _isolate_email_provider():
    """Keep the global email provider from leaking between tests."""
    original = email_provider_module._email_provider
    email_provider_module._email_provider = None
    yield
    email_provider_module._email_provider = original


def _set_preferences(db_session, user, *, in_app=None, email=None):
    """Persist an explicit preferences row for a user (True/False values only)."""
    preferences = UserPreferences(user_id=user.id)
    if in_app is not None:
        preferences.in_app_notifications_enabled = in_app
    if email is not None:
        preferences.email_notifications_enabled = email
    db_session.add(preferences)
    db_session.commit()
    return preferences


def _make_escalation_ticket(db_session, user, priority="Critical"):
    ticket = Ticket(
        title=f"{priority} preference enforcement ticket",
        description="Ticket used for notification preference tests",
        priority=priority,
        status="Open",
        ticket_type="INCIDENT",
        created_by=user.id,
    )
    db_session.add(ticket)
    db_session.commit()
    db_session.refresh(ticket)
    return ticket


def _make_rule(db_session, name, event_type=EscalationEventType.RESPONSE_BREACH, priority="Critical", **kwargs):
    return create_escalation_rule(
        db=db_session,
        name=name,
        event_type=event_type,
        priority=priority,
        target_role="Admin",
        **kwargs,
    )


class _FailingProvider(EmailProvider):
    async def send(self, message: EmailMessage) -> EmailResult:
        return EmailResult(success=False, error="smtp unavailable")



# ==================================================
# Preferences
# ==================================================
class TestPreferences:
    def test_get_creates_defaults(self, client, auth_headers):
        response = client.get("/users/me/preferences", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["email_notifications_enabled"] is True
        assert data["in_app_notifications_enabled"] is True
        assert data["ai_suggestions_enabled"] is True

    def test_get_only_creates_one_row(self, client, auth_headers, db_session, test_user):
        from app.models.user_preferences import UserPreferences

        client.get("/users/me/preferences", headers=auth_headers)
        client.get("/users/me/preferences", headers=auth_headers)

        count = (
            db_session.query(UserPreferences)
            .filter(UserPreferences.user_id == test_user.id)
            .count()
        )
        assert count == 1

    def test_put_persists_changes(self, client, auth_headers):
        response = client.put(
            "/users/me/preferences",
            headers=auth_headers,
            json={"email_notifications_enabled": False},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["email_notifications_enabled"] is False
        # Untouched fields retain defaults
        assert data["in_app_notifications_enabled"] is True
        assert data["ai_suggestions_enabled"] is True

        # Persisted across requests
        get_response = client.get("/users/me/preferences", headers=auth_headers)
        assert get_response.json()["email_notifications_enabled"] is False

    def test_put_partial_update_multiple_fields(self, client, auth_headers):
        response = client.put(
            "/users/me/preferences",
            headers=auth_headers,
            json={
                "in_app_notifications_enabled": False,
                "ai_suggestions_enabled": False,
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["email_notifications_enabled"] is True
        assert data["in_app_notifications_enabled"] is False
        assert data["ai_suggestions_enabled"] is False

    def test_put_invalid_value_rejected(self, client, auth_headers):
        response = client.put(
            "/users/me/preferences",
            headers=auth_headers,
            json={"email_notifications_enabled": "not-a-boolean"},
        )

        assert response.status_code == 422

    def test_put_ignores_unknown_fields(self, client, auth_headers):
        response = client.put(
            "/users/me/preferences",
            headers=auth_headers,
            json={"is_admin": True, "email_notifications_enabled": False},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["email_notifications_enabled"] is False
        assert "is_admin" not in data

    def test_get_requires_authentication(self, client):
        response = client.get("/users/me/preferences")
        assert response.status_code == 401

    def test_put_requires_authentication(self, client):
        response = client.put(
            "/users/me/preferences",
            json={"email_notifications_enabled": False},
        )
        assert response.status_code == 401

    def test_preferences_are_isolated_per_user(self, client, auth_headers, db_session):
        from app.models.user import User

        other = User(
            name="Other User",
            email="other@example.com",
            password=hash_password("otherpassword123"),
            role="Employee",
        )
        db_session.add(other)
        db_session.commit()

        # Current user disables email notifications
        client.put(
            "/users/me/preferences",
            headers=auth_headers,
            json={"email_notifications_enabled": False},
        )

        # A different user still sees their own defaults
        login = client.post(
            "/auth/login",
            json={"email": "other@example.com", "password": "otherpassword123"},
        )
        other_headers = {"Authorization": f"Bearer {login.json()['access_token']}"}

        response = client.get("/users/me/preferences", headers=other_headers)
        assert response.status_code == 200
        assert response.json()["email_notifications_enabled"] is True


class TestPreferencesCSRF:
    def test_put_without_csrf_header_is_rejected(self, client, test_user):
        login = client.post(
            "/auth/login",
            json={"email": "test@example.com", "password": "testpassword123"},
        )
        assert login.status_code == 200

        # Cookie auth is now active; omit the CSRF header
        response = client.put(
            "/users/me/preferences",
            json={"email_notifications_enabled": False},
        )
        assert response.status_code == 403

    def test_put_with_csrf_header_succeeds(self, client, test_user):
        login = client.post(
            "/auth/login",
            json={"email": "test@example.com", "password": "testpassword123"},
        )
        assert login.status_code == 200

        csrf_token = client.cookies.get(settings.csrf_cookie_name)
        assert csrf_token

        response = client.put(
            "/users/me/preferences",
            json={"email_notifications_enabled": False},
            headers={settings.csrf_header_name: csrf_token},
        )
        assert response.status_code == 200
        assert response.json()["email_notifications_enabled"] is False


# ==================================================
# Password Change
# ==================================================
class TestPasswordChange:
    def test_change_password_success_and_reauthenticate(self, client, auth_headers, test_user):
        response = client.put(
            "/users/me/password",
            headers=auth_headers,
            json={
                "current_password": "testpassword123",
                "new_password": "newpassword456",
            },
        )

        assert response.status_code == 200
        assert "message" in response.json()

        # Old password no longer works
        old_login = client.post(
            "/auth/login",
            json={"email": test_user.email, "password": "testpassword123"},
        )
        assert old_login.status_code == 401

        # New password works
        new_login = client.post(
            "/auth/login",
            json={"email": test_user.email, "password": "newpassword456"},
        )
        assert new_login.status_code == 200

    def test_change_password_wrong_current_password(self, client, auth_headers, test_user):
        response = client.put(
            "/users/me/password",
            headers=auth_headers,
            json={
                "current_password": "wrongpassword",
                "new_password": "newpassword456",
            },
        )

        assert response.status_code == 400

        # Original password still valid
        login = client.post(
            "/auth/login",
            json={"email": test_user.email, "password": "testpassword123"},
        )
        assert login.status_code == 200

    def test_change_password_too_short(self, client, auth_headers):
        response = client.put(
            "/users/me/password",
            headers=auth_headers,
            json={
                "current_password": "testpassword123",
                "new_password": "short",
            },
        )
        assert response.status_code == 422

    def test_change_password_requires_authentication(self, client):
        response = client.put(
            "/users/me/password",
            json={
                "current_password": "testpassword123",
                "new_password": "newpassword456",
            },
        )
        assert response.status_code == 401

    def test_change_password_requires_csrf(self, client, test_user):
        login = client.post(
            "/auth/login",
            json={"email": "test@example.com", "password": "testpassword123"},
        )
        assert login.status_code == 200

        response = client.put(
            "/users/me/password",
            json={
                "current_password": "testpassword123",
                "new_password": "newpassword456",
            },
        )
        assert response.status_code == 403

    def test_change_password_revokes_refresh_tokens(self, client, test_user):
        login = client.post(
            "/auth/login",
            json={"email": "test@example.com", "password": "testpassword123"},
        )
        assert login.status_code == 200
        tokens = login.json()

        response = client.put(
            "/users/me/password",
            headers={"Authorization": f"Bearer {tokens['access_token']}"},
            json={
                "current_password": "testpassword123",
                "new_password": "newpassword456",
            },
        )
        assert response.status_code == 200

        # The previously issued refresh token is now revoked
        refresh = client.post(
            "/auth/refresh",
            json={"refresh_token": tokens["refresh_token"]},
        )
        assert refresh.status_code == 401


class TestPasswordChangeRateLimit:
    @pytest.fixture(autouse=True)
    def enable_rate_limiting(self):
        original_enabled = settings.rate_limit_enabled
        settings.rate_limit_enabled = True
        yield
        settings.rate_limit_enabled = original_enabled
        asyncio.run(rate_limiter.reset_all())

    def test_excessive_attempts_are_rate_limited(self, client, auth_headers):
        # The generic dependency binds its limit at import time; read it so the
        # test stays correct if the default is retuned.
        limit = inspect.signature(rate_limit_dependency).parameters["max_requests"].default

        payload = {"current_password": "wrongpassword", "new_password": "newpassword456"}

        statuses = []
        for _ in range(limit + 1):
            response = client.put(
                "/users/me/password",
                headers=auth_headers,
                json=payload,
            )
            statuses.append(response.status_code)

        assert statuses[-1] == 429
        assert all(code != 429 for code in statuses[:limit])


# ==================================================
# In-app notification preference enforcement
# ==================================================
class TestInAppNotificationPreference:
    def test_default_enabled_creates_notification(self, db_session, admin_user):
        notification = create_notification(
            db=db_session,
            recipient_id=admin_user.id,
            notification_type=NotificationType.TICKET_ASSIGNED,
            title="Ticket Assigned",
            message="Ticket #1 has been assigned to you.",
        )

        assert notification is not None
        assert notification.id is not None

    def test_enabled_preference_creates_notification(self, db_session, admin_user):
        _set_preferences(db_session, admin_user, in_app=True)

        notification = create_notification(
            db=db_session,
            recipient_id=admin_user.id,
            notification_type=NotificationType.TICKET_ASSIGNED,
            title="Ticket Assigned",
            message="Ticket #1 has been assigned to you.",
        )

        assert notification is not None

    def test_disabled_preference_suppresses_notification(self, db_session, admin_user):
        _set_preferences(db_session, admin_user, in_app=False)

        notification = create_notification(
            db=db_session,
            recipient_id=admin_user.id,
            notification_type=NotificationType.TICKET_ASSIGNED,
            title="Ticket Assigned",
            message="Ticket #1 has been assigned to you.",
        )

        assert notification is None
        count = (
            db_session.query(Notification)
            .filter(Notification.recipient_id == admin_user.id)
            .count()
        )
        assert count == 0

    def test_disabled_preference_suppresses_escalation_notification(self, db_session, admin_user):
        ticket = _make_escalation_ticket(db_session, admin_user)
        rule = _make_rule(db_session, "Pref Suppress Notify Rule", notify_enabled=True)
        _set_preferences(db_session, admin_user, in_app=False)

        notification_id = create_escalation_notification(
            db_session,
            ticket,
            admin_user,
            EscalationEventType.RESPONSE_BREACH,
            rule,
        )

        assert notification_id is None
        count = (
            db_session.query(Notification)
            .filter(Notification.recipient_id == admin_user.id)
            .count()
        )
        assert count == 0

    def test_enabled_preference_keeps_escalation_notification(self, db_session, admin_user):
        ticket = _make_escalation_ticket(db_session, admin_user)
        rule = _make_rule(db_session, "Pref Allow Notify Rule", notify_enabled=True)
        _set_preferences(db_session, admin_user, in_app=True)

        notification_id = create_escalation_notification(
            db_session,
            ticket,
            admin_user,
            EscalationEventType.RESPONSE_BREACH,
            rule,
        )

        assert notification_id is not None


# ==================================================
# Escalation email preference enforcement
# ==================================================
class TestEscalationEmailPreference:
    def test_default_enabled_delivers_email(self, db_session, admin_user):
        provider = MockEmailProvider()
        set_email_provider(provider)
        ticket = _make_escalation_ticket(db_session, admin_user)
        rule = _make_rule(db_session, "Pref Email Default Rule", email_enabled=True)

        result = asyncio.run(
            send_escalation_email(
                ticket, admin_user, EscalationEventType.RESPONSE_BREACH, rule, db=db_session
            )
        )

        assert result.success is True
        assert len(provider.sent_emails) == 1

    def test_enabled_preference_delivers_email(self, db_session, admin_user):
        provider = MockEmailProvider()
        set_email_provider(provider)
        ticket = _make_escalation_ticket(db_session, admin_user)
        rule = _make_rule(db_session, "Pref Email Enabled Rule", email_enabled=True)
        _set_preferences(db_session, admin_user, email=True)

        result = asyncio.run(
            send_escalation_email(
                ticket, admin_user, EscalationEventType.RESPONSE_BREACH, rule, db=db_session
            )
        )

        assert result.success is True
        assert len(provider.sent_emails) == 1

    def test_disabled_preference_suppresses_email(self, db_session, admin_user):
        provider = MockEmailProvider()
        set_email_provider(provider)
        ticket = _make_escalation_ticket(db_session, admin_user)
        rule = _make_rule(db_session, "Pref Email Disabled Rule", email_enabled=True)
        _set_preferences(db_session, admin_user, email=False)

        result = asyncio.run(
            send_escalation_email(
                ticket, admin_user, EscalationEventType.RESPONSE_BREACH, rule, db=db_session
            )
        )

        assert result.success is False
        assert "disabled" in result.error.lower()
        assert provider.sent_emails == []

    def test_rule_disabled_overrides_recipient_preference(self, db_session, admin_user):
        provider = MockEmailProvider()
        set_email_provider(provider)
        ticket = _make_escalation_ticket(db_session, admin_user)
        rule = _make_rule(db_session, "Pref Email Rule Off Rule", email_enabled=False)
        _set_preferences(db_session, admin_user, email=True)

        result = asyncio.run(
            send_escalation_email(
                ticket, admin_user, EscalationEventType.RESPONSE_BREACH, rule, db=db_session
            )
        )

        assert result.success is False
        assert "rule" in result.error.lower()
        assert provider.sent_emails == []


# ==================================================
# End-to-end escalation preference enforcement
# ==================================================
class TestEscalationPreferenceIntegration:
    def test_escalation_skips_email_when_preference_disabled(self, db_session, admin_user):
        provider = MockEmailProvider()
        set_email_provider(provider)
        ticket = _make_escalation_ticket(db_session, admin_user)
        _set_preferences(db_session, admin_user, email=False)

        result = asyncio.run(
            process_escalation(db_session, ticket, EscalationEventType.RESPONSE_BREACH)
        )

        assert result is True
        record = (
            db_session.query(EscalationRecord)
            .filter(EscalationRecord.ticket_id == ticket.id)
            .first()
        )
        assert record is not None
        assert record.email_sent is False
        assert record.email_error is not None
        assert "disabled" in record.email_error.lower()
        assert provider.sent_emails == []
        # In-app notifications remain enabled by default.
        assert record.notification_created is True
        assert record.history_recorded is True

    def test_escalation_skips_notification_when_preference_disabled(self, db_session, admin_user):
        provider = MockEmailProvider()
        set_email_provider(provider)
        ticket = _make_escalation_ticket(db_session, admin_user)
        _set_preferences(db_session, admin_user, in_app=False)

        result = asyncio.run(
            process_escalation(db_session, ticket, EscalationEventType.RESPONSE_BREACH)
        )

        assert result is True
        record = (
            db_session.query(EscalationRecord)
            .filter(EscalationRecord.ticket_id == ticket.id)
            .first()
        )
        assert record is not None
        assert record.notification_created is False
        assert record.notification_id is None
        assert (
            db_session.query(Notification)
            .filter(Notification.recipient_id == admin_user.id)
            .count()
            == 0
        )
        # Email remains enabled by default and is delivered.
        assert record.email_sent is True
        assert len(provider.sent_emails) == 1

    def test_escalation_continues_when_email_delivery_fails(self, db_session, admin_user):
        set_email_provider(_FailingProvider())
        ticket = _make_escalation_ticket(db_session, admin_user)

        result = asyncio.run(
            process_escalation(db_session, ticket, EscalationEventType.RESPONSE_BREACH)
        )

        assert result is True
        record = (
            db_session.query(EscalationRecord)
            .filter(EscalationRecord.ticket_id == ticket.id)
            .first()
        )
        assert record is not None
        assert record.email_sent is False
        assert record.email_error is not None
        assert "smtp unavailable" in record.email_error
        assert record.history_recorded is True
        db_session.refresh(ticket)
        assert ticket.escalated_to is not None
