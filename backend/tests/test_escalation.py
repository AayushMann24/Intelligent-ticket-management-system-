"""
Focused tests for the escalation administration milestone (Phase 2D-4).

Coverage:
  * Authorization (Admin-only rule management and record inspection)
  * Rule CRUD via the API
  * Rule precedence / specificity matching
  * Idempotency (duplicate rule names and repeated escalation processing)
  * Migration seeding (presence, idempotency, reversibility)
  * SMTP provider success/failure (mocked - never sends real email)
  * Regression: email transport failures do not block escalation
"""

import asyncio
import importlib.util
import pathlib
import smtplib
from datetime import datetime, timezone
from unittest.mock import patch

import pytest

from app.config import settings
from app.models.escalation import EscalationEventType, EscalationRecord, EscalationRule
from app.models.ticket import Ticket
from app.models.user import User
from app.services import email_provider as email_provider_module
from app.services.email_provider import (
    EmailMessage,
    EmailProvider,
    EmailResult,
    MockEmailProvider,
    SMTPEmailProvider,
    build_email_provider,
    set_email_provider,
    get_email_provider,
)
from app.services.escalation_service import (
    create_escalation_rule,
    get_best_matching_rule,
    get_delivery_status,
    process_escalation,
)


# ======================================================
# Test isolation
# ======================================================

@pytest.fixture(autouse=True)
def _reset_email_provider():
    """Ensure each test starts from a clean, config-driven email provider."""
    original = email_provider_module._email_provider
    email_provider_module._email_provider = None
    yield
    email_provider_module._email_provider = original


def _load_migration_module():
    """Load the Phase 2D-4 migration module by path (it is not a package)."""
    path = (
        pathlib.Path(__file__).resolve().parents[1]
        / "alembic"
        / "versions"
        / "phase2d4_escalation_defaults.py"
    )
    spec = importlib.util.spec_from_file_location("phase2d4_escalation_defaults", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _make_ticket(db_session, admin_user, priority="Critical"):
    ticket = Ticket(
        title=f"{priority} escalation ticket",
        description="Test ticket for escalation",
        priority=priority,
        status="Open",
        ticket_type="INCIDENT",
        created_by=admin_user.id,
        sla_response_deadline=datetime.now(timezone.utc),
    )
    db_session.add(ticket)
    db_session.commit()
    db_session.refresh(ticket)
    return ticket


# ======================================================
# Authorization
# ======================================================

class TestEscalationAuthorization:
    def test_list_rules_requires_authentication(self, client):
        assert client.get("/escalations/rules").status_code == 401

    def test_employee_cannot_list_rules(self, client, auth_headers):
        assert client.get("/escalations/rules", headers=auth_headers).status_code == 403

    def test_technician_cannot_list_rules(self, client, tech_auth_headers):
        assert client.get("/escalations/rules", headers=tech_auth_headers).status_code == 403

    def test_employee_cannot_create_rule(self, client, auth_headers):
        response = client.post(
            "/escalations/rules",
            headers=auth_headers,
            json={
                "name": "Employee Attempt",
                "event_type": "RESPONSE_BREACH",
                "priority": "High",
            },
        )
        assert response.status_code == 403

    def test_technician_cannot_update_rule(self, client, tech_auth_headers, admin_auth_headers):
        created = client.post(
            "/escalations/rules",
            headers=admin_auth_headers,
            json={"name": "Authz Rule", "event_type": "RESPONSE_BREACH", "priority": "High"},
        )
        rule_id = created.json()["id"]
        response = client.put(
            f"/escalations/rules/{rule_id}",
            headers=tech_auth_headers,
            json={"name": "Nope"},
        )
        assert response.status_code == 403

    def test_employee_cannot_list_records(self, client, auth_headers):
        assert client.get("/escalations/records", headers=auth_headers).status_code == 403

    def test_unauthenticated_cannot_list_records(self, client):
        assert client.get("/escalations/records").status_code == 401


# ======================================================
# Rule CRUD
# ======================================================

class TestEscalationRuleCRUD:
    def test_create_rule(self, client, admin_auth_headers):
        response = client.post(
            "/escalations/rules",
            headers=admin_auth_headers,
            json={
                "name": "CRUD Create Rule",
                "description": "A rule created through the API",
                "event_type": "RESPONSE_BREACH",
                "priority": "Medium",
                "target_role": "Technician",
                "notify_enabled": True,
                "email_enabled": False,
            },
        )
        assert response.status_code == 201
        body = response.json()
        assert body["name"] == "CRUD Create Rule"
        assert body["event_type"] == "RESPONSE_BREACH"
        assert body["priority"] == "Medium"
        assert body["target_role"] == "Technician"
        assert body["email_enabled"] is False
        assert body["is_active"] is True
        assert body["precedence"] == 2

    def test_create_rule_duplicate_name_rejected(self, client, admin_auth_headers):
        payload = {
            "name": "CRUD Duplicate Rule",
            "event_type": "RESPONSE_BREACH",
            "priority": "High",
        }
        assert client.post("/escalations/rules", headers=admin_auth_headers, json=payload).status_code == 201
        duplicate = client.post("/escalations/rules", headers=admin_auth_headers, json=payload)
        assert duplicate.status_code == 400

    def test_create_rule_invalid_priority_rejected(self, client, admin_auth_headers):
        response = client.post(
            "/escalations/rules",
            headers=admin_auth_headers,
            json={"name": "Bad Priority", "event_type": "RESPONSE_BREACH", "priority": "Urgent"},
        )
        assert response.status_code == 422

    def test_get_rule_by_id(self, client, admin_auth_headers):
        created = client.post(
            "/escalations/rules",
            headers=admin_auth_headers,
            json={"name": "CRUD Get Rule", "event_type": "RESOLUTION_BREACH", "priority": "High"},
        ).json()
        response = client.get(f"/escalations/rules/{created['id']}", headers=admin_auth_headers)
        assert response.status_code == 200
        assert response.json()["id"] == created["id"]

    def test_get_missing_rule_returns_404(self, client, admin_auth_headers):
        assert client.get("/escalations/rules/999999", headers=admin_auth_headers).status_code == 404

    def test_list_rules_with_filter(self, client, admin_auth_headers):
        client.post(
            "/escalations/rules",
            headers=admin_auth_headers,
            json={"name": "CRUD Filter Rule", "event_type": "RESPONSE_BREACH", "priority": "Low"},
        )
        response = client.get("/escalations/rules?priority=Low", headers=admin_auth_headers)
        assert response.status_code == 200
        names = [r["name"] for r in response.json()["items"]]
        assert "CRUD Filter Rule" in names
        assert all(r["priority"] == "Low" for r in response.json()["items"])

    def test_update_rule(self, client, admin_auth_headers):
        created = client.post(
            "/escalations/rules",
            headers=admin_auth_headers,
            json={"name": "CRUD Update Rule", "event_type": "RESPONSE_BREACH", "priority": "Medium"},
        ).json()

        response = client.put(
            f"/escalations/rules/{created['id']}",
            headers=admin_auth_headers,
            json={"name": "CRUD Update Rule v2", "ticket_type": "INCIDENT"},
        )
        assert response.status_code == 200
        body = response.json()
        assert body["name"] == "CRUD Update Rule v2"
        assert body["ticket_type"] == "INCIDENT"
        # Precedence recomputed: event_type + priority + ticket_type
        assert body["precedence"] == 3

    def test_update_rule_duplicate_name_rejected(self, client, admin_auth_headers):
        client.post(
            "/escalations/rules",
            headers=admin_auth_headers,
            json={"name": "CRUD Name A", "event_type": "RESPONSE_BREACH", "priority": "Medium"},
        )
        second = client.post(
            "/escalations/rules",
            headers=admin_auth_headers,
            json={"name": "CRUD Name B", "event_type": "RESPONSE_BREACH", "priority": "Medium"},
        ).json()

        response = client.put(
            f"/escalations/rules/{second['id']}", headers=admin_auth_headers, json={"name": "CRUD Name A"}
        )
        assert response.status_code == 400

    def test_deactivate_rule(self, client, admin_auth_headers):
        created = client.post(
            "/escalations/rules",
            headers=admin_auth_headers,
            json={"name": "CRUD Deactivate Rule", "event_type": "RESOLUTION_BREACH", "priority": "High"},
        ).json()

        response = client.delete(f"/escalations/rules/{created['id']}", headers=admin_auth_headers)
        assert response.status_code == 200
        assert response.json()["is_active"] is False

        fetched = client.get(f"/escalations/rules/{created['id']}", headers=admin_auth_headers)
        assert fetched.status_code == 200
        assert fetched.json()["is_active"] is False

    def test_deactivate_missing_rule_returns_404(self, client, admin_auth_headers):
        assert client.delete("/escalations/rules/999999", headers=admin_auth_headers).status_code == 404


# ======================================================
# Precedence / specificity
# ======================================================

class TestEscalationRulePrecedence:
    def test_more_specific_rule_wins(self, db_session):
        create_escalation_rule(
            db=db_session,
            name="Prec Medium Generic",
            event_type=EscalationEventType.RESPONSE_BREACH,
            priority="Medium",
            target_role="Admin",
        )
        create_escalation_rule(
            db=db_session,
            name="Prec Medium Incident",
            event_type=EscalationEventType.RESPONSE_BREACH,
            priority="Medium",
            target_role="Technician",
            ticket_type="INCIDENT",
        )
        create_escalation_rule(
            db=db_session,
            name="Prec Medium Incident Database",
            event_type=EscalationEventType.RESPONSE_BREACH,
            priority="Medium",
            target_role="Admin",
            ticket_type="INCIDENT",
            category="Database",
        )

        best = get_best_matching_rule(
            db_session,
            EscalationEventType.RESPONSE_BREACH,
            priority="Medium",
            ticket_type="INCIDENT",
            category="Database",
        )
        assert best is not None
        assert best.name == "Prec Medium Incident Database"

        best = get_best_matching_rule(
            db_session,
            EscalationEventType.RESPONSE_BREACH,
            priority="Medium",
            ticket_type="INCIDENT",
            category="Network",
        )
        assert best is not None
        assert best.name == "Prec Medium Incident"

    def test_low_priority_has_no_default_rule(self, db_session):
        # No default rules exist for Low priority; higher priorities do not match.
        best = get_best_matching_rule(
            db_session,
            EscalationEventType.RESPONSE_BREACH,
            priority="Low",
            ticket_type="INCIDENT",
        )
        assert best is None

    def test_disabled_rule_is_not_matched(self, db_session):
        create_escalation_rule(
            db=db_session,
            name="Prec Disabled",
            event_type=EscalationEventType.RESOLUTION_BREACH,
            priority="Low",
            target_role="Admin",
            is_active=False,
        )
        best = get_best_matching_rule(
            db_session, EscalationEventType.RESOLUTION_BREACH, priority="Low"
        )
        assert best is None


# ======================================================
# Records API / delivery status
# ======================================================

class TestEscalationRecordsAPI:
    @pytest.mark.parametrize(
        "email_sent,email_error,expected",
        [
            (True, None, "delivered"),
            (False, "smtp down", "failed"),
            (False, None, "not_attempted"),
        ],
    )
    def test_delivery_status_derivation(self, db_session, email_sent, email_error, expected):
        record = EscalationRecord(
            ticket_id=1,
            event_type=EscalationEventType.RESPONSE_BREACH,
            email_sent=email_sent,
            email_error=email_error,
        )
        assert get_delivery_status(record) == expected

    def test_list_and_get_records(self, client, admin_auth_headers, db_session, admin_user):
        ticket = _make_ticket(db_session, admin_user)
        record = EscalationRecord(
            ticket_id=ticket.id,
            event_type=EscalationEventType.RESPONSE_BREACH,
            recipient_id=admin_user.id,
            notification_created=True,
            history_recorded=True,
            email_sent=False,
            email_error="smtp unavailable",
        )
        db_session.add(record)
        db_session.commit()
        db_session.refresh(record)

        listing = client.get("/escalations/records", headers=admin_auth_headers)
        assert listing.status_code == 200
        items = [i for i in listing.json()["items"] if i["id"] == record.id]
        assert len(items) == 1
        assert items[0]["delivery_status"] == "failed"
        assert items[0]["ticket_title"] == ticket.title
        assert items[0]["recipient_name"] == admin_user.name

        single = client.get(f"/escalations/records/{record.id}", headers=admin_auth_headers)
        assert single.status_code == 200
        assert single.json()["delivery_status"] == "failed"

    def test_records_filter_by_ticket(self, client, admin_auth_headers, db_session, admin_user):
        ticket = _make_ticket(db_session, admin_user)
        record = EscalationRecord(
            ticket_id=ticket.id,
            event_type=EscalationEventType.RESOLUTION_BREACH,
            recipient_id=admin_user.id,
            email_sent=True,
        )
        db_session.add(record)
        db_session.commit()

        response = client.get(
            f"/escalations/records?ticket_id={ticket.id}", headers=admin_auth_headers
        )
        assert response.status_code == 200
        assert response.json()["total"] == 1
        assert response.json()["items"][0]["delivery_status"] == "delivered"

    def test_get_missing_record_returns_404(self, client, admin_auth_headers):
        assert client.get("/escalations/records/999999", headers=admin_auth_headers).status_code == 404

    def test_default_rules_are_listed(self, client, admin_auth_headers):
        response = client.get("/escalations/rules?page_size=100", headers=admin_auth_headers)
        assert response.status_code == 200
        names = {r["name"] for r in response.json()["items"]}
        assert "Default: Critical Response SLA Breach" in names
        assert "Default: High Resolution SLA Breach" in names


# ======================================================
# Migration seeding
# ======================================================

class TestMigrationSeeding:
    def test_default_rules_seeded_once(self, db_session):
        module = _load_migration_module()
        names = [r["name"] for r in module.DEFAULT_RULES]

        found = (
            db_session.query(EscalationRule)
            .filter(EscalationRule.name.in_(names))
            .all()
        )
        assert len(found) == len(names)
        assert all(rule.is_active for rule in found)
        assert all(rule.precedence == 2 for rule in found)

    def test_seed_helper_is_idempotent(self, db_session):
        module = _load_migration_module()
        bind = db_session.connection()

        before = db_session.query(EscalationRule).count()
        inserted = module._seed_default_rules(bind)
        assert inserted == 0  # already applied by the migration
        assert db_session.query(EscalationRule).count() == before

        module._seed_default_rules(bind)
        assert db_session.query(EscalationRule).count() == before

    def test_seed_helper_is_reversible(self, db_session):
        module = _load_migration_module()
        bind = db_session.connection()
        names = [r["name"] for r in module.DEFAULT_RULES]

        deleted = module._remove_default_rules(bind)
        assert deleted == len(names)
        assert (
            db_session.query(EscalationRule)
            .filter(EscalationRule.name.in_(names))
            .count()
            == 0
        )

        module._seed_default_rules(bind)
        assert (
            db_session.query(EscalationRule)
            .filter(EscalationRule.name.in_(names))
            .count()
            == len(names)
        )


# ======================================================
# SMTP provider (mocked - no real email)
# ======================================================

class TestSMTPProvider:
    def test_smtp_send_success(self):
        provider = SMTPEmailProvider(
            host="smtp.example.com",
            port=587,
            username="smtp-user",
            password="smtp-secret",
            use_tls=True,
        )
        with patch("app.services.email_provider.smtplib.SMTP") as mock_smtp:
            instance = mock_smtp.return_value
            result = asyncio.run(
                provider.send(
                    EmailMessage(to="dest@example.com", subject="Hello", body_text="Body")
                )
            )

        assert result.success is True
        assert result.message_id
        mock_smtp.assert_called_once()
        instance.starttls.assert_called_once()
        instance.login.assert_called_once_with("smtp-user", "smtp-secret")
        instance.send_message.assert_called_once()
        # Connection must be closed after sending.
        instance.quit.assert_called_once()

    def test_smtp_send_failure_records_error_without_password(self):
        provider = SMTPEmailProvider(
            host="smtp.example.com",
            port=587,
            username="smtp-user",
            password="super-secret-password",
        )
        with patch("app.services.email_provider.smtplib.SMTP") as mock_smtp:
            instance = mock_smtp.return_value
            instance.send_message.side_effect = smtplib.SMTPException("relay refused")
            result = asyncio.run(
                provider.send(
                    EmailMessage(to="dest@example.com", subject="Hello", body_text="Body")
                )
            )

        assert result.success is False
        assert "relay refused" in result.error
        # Credentials must never leak into the surfaced error.
        assert "super-secret-password" not in result.error

    def test_smtp_without_host_is_not_configured(self):
        provider = SMTPEmailProvider(host=None)
        result = asyncio.run(
            provider.send(EmailMessage(to="dest@example.com", subject="Hi", body_text="Body"))
        )
        assert result.success is False
        assert "not configured" in result.error.lower()

    def test_build_email_provider_defaults_to_mock(self, monkeypatch):
        monkeypatch.setattr(settings, "email_provider", "mock")
        provider = build_email_provider()
        assert isinstance(provider, MockEmailProvider)

    def test_build_email_provider_smtp(self, monkeypatch):
        monkeypatch.setattr(settings, "email_provider", "smtp")
        monkeypatch.setattr(settings, "smtp_host", "smtp.example.com")
        monkeypatch.setattr(settings, "smtp_port", 2525)
        monkeypatch.setattr(settings, "smtp_username", "user")
        monkeypatch.setattr(settings, "smtp_password", "pass")
        monkeypatch.setattr(settings, "smtp_use_tls", True)
        monkeypatch.setattr(settings, "smtp_use_ssl", False)

        provider = build_email_provider()
        assert isinstance(provider, SMTPEmailProvider)
        assert provider.host == "smtp.example.com"
        assert provider.port == 2525

    def test_get_email_provider_uses_configuration(self, monkeypatch):
        monkeypatch.setattr(settings, "email_provider", "console")
        assert get_email_provider().__class__.__name__ == "ConsoleEmailProvider"


# ======================================================
# Regression: email failure never blocks escalation
# ======================================================

class _FailingProvider(EmailProvider):
    async def send(self, message: EmailMessage) -> EmailResult:
        return EmailResult(success=False, error="smtp unavailable")


class _RaisingProvider(EmailProvider):
    async def send(self, message: EmailMessage) -> EmailResult:
        raise RuntimeError("smtp exploded")


class TestEscalationEmailFailureRegression:
    @pytest.mark.parametrize(
        "provider_cls,expected_error",
        [(_FailingProvider, "smtp unavailable"), (_RaisingProvider, "smtp exploded")],
    )
    def test_escalation_continues_when_email_fails(
        self, db_session, admin_user, provider_cls, expected_error
    ):
        set_email_provider(provider_cls())

        ticket = _make_ticket(db_session, admin_user, priority="Critical")
        result = asyncio.run(
            process_escalation(db_session, ticket, EscalationEventType.RESPONSE_BREACH)
        )

        assert result is True
        record = (
            db_session.query(EscalationRecord)
            .filter(
                EscalationRecord.ticket_id == ticket.id,
                EscalationRecord.event_type == EscalationEventType.RESPONSE_BREACH,
            )
            .first()
        )
        assert record is not None
        assert record.email_sent is False
        assert record.email_error is not None
        assert expected_error in record.email_error
        assert record.history_recorded is True
        # Escalation workflow still updated the ticket.
        db_session.refresh(ticket)
        assert ticket.escalated_to is not None

    def test_default_rule_escalation_is_idempotent(self, db_session, admin_user):
        ticket = _make_ticket(db_session, admin_user, priority="High")

        first = asyncio.run(
            process_escalation(db_session, ticket, EscalationEventType.RESPONSE_BREACH)
        )
        second = asyncio.run(
            process_escalation(db_session, ticket, EscalationEventType.RESPONSE_BREACH)
        )

        assert first is True
        assert second is True
        records = (
            db_session.query(EscalationRecord)
            .filter(
                EscalationRecord.ticket_id == ticket.id,
                EscalationRecord.event_type == EscalationEventType.RESPONSE_BREACH,
            )
            .all()
        )
        assert len(records) == 1
        assert records[0].rule_id is not None
