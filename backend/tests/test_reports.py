"""
Tests for Reports API (Phase 2E - Checkpoint 3)
"""

import pytest
from datetime import datetime, timezone, timedelta
from sqlalchemy.orm import Session
from fastapi.testclient import TestClient

from app.models.ticket import Ticket
from app.models.user import User
from app.models.escalation import EscalationRecord, EscalationEventType
from app.services.report_service import (
    generate_ticket_report_rows,
    get_ticket_report_summary,
    generate_sla_report_rows,
    get_sla_report_summary,
    generate_sla_breach_report_rows,
    generate_escalation_report_rows,
    get_escalation_report_summary,
    generate_technician_report_rows,
    get_technician_report_summary,
    _generate_csv_stream,
    TICKET_REPORT_HEADERS,
    SLA_REPORT_HEADERS,
    SLA_BREACH_REPORT_HEADERS,
    ESCALATION_REPORT_HEADERS,
    TECHNICIAN_REPORT_HEADERS,
)


class TestReportService:
    """Tests for report service functions."""

    def test_generate_ticket_report_rows(self, db_session: Session, admin_user: User, test_user: User):
        """Test ticket report row generation."""
        # Create test tickets
        tickets = [
            Ticket(
                title="Test Ticket 1",
                description="Description 1",
                priority="High",
                status="Open",
                ticket_type="INCIDENT",
                category="Network",
                created_by=test_user.id,
                assigned_to=admin_user.id,
            ),
            Ticket(
                title="Test Ticket 2",
                description="Description 2",
                priority="Critical",
                status="Resolved",
                ticket_type="PROBLEM",
                category="Hardware",
                created_by=test_user.id,
                resolved_by=admin_user.id,
                resolved_at=datetime.now(timezone.utc),
            ),
        ]
        for t in tickets:
            db_session.add(t)
        db_session.commit()

        # Generate rows
        rows = list(generate_ticket_report_rows(db_session))
        assert len(rows) == 2

        # Check first row structure
        row = rows[0]
        assert len(row) == len(TICKET_REPORT_HEADERS)
        assert row[0] in [t.id for t in tickets]  # Ticket ID
        assert row[3] in ["High", "Critical"]  # Priority

    def test_ticket_report_summary(self, db_session: Session, test_user: User):
        """Test ticket report summary generation."""
        tickets = [
            Ticket(title="T1", description="D1", priority="High", status="Open", ticket_type="INCIDENT", category="Net", created_by=test_user.id),
            Ticket(title="T2", description="D2", priority="High", status="Open", ticket_type="INCIDENT", category="Net", created_by=test_user.id),
            Ticket(title="T3", description="D3", priority="Medium", status="Resolved", ticket_type="PROBLEM", category="HW", created_by=test_user.id),
        ]
        for t in tickets:
            db_session.add(t)
        db_session.commit()

        summary = get_ticket_report_summary(db_session)
        assert summary["total_tickets"] == 3
        assert summary["by_status"]["Open"] == 2
        assert summary["by_status"]["Resolved"] == 1
        assert summary["by_priority"]["High"] == 2
        assert summary["by_priority"]["Medium"] == 1
        assert summary["by_ticket_type"]["INCIDENT"] == 2
        assert summary["by_ticket_type"]["PROBLEM"] == 1

    def test_ticket_report_with_filters(self, db_session: Session, test_user: User):
        """Test ticket report with date and priority filters."""
        now = datetime.now(timezone.utc)
        old_date = now - timedelta(days=10)

        tickets = [
            Ticket(title="Recent High", description="D", priority="High", status="Open", ticket_type="INCIDENT", category="A", created_by=test_user.id, created_at=now),
            Ticket(title="Recent Low", description="D", priority="Low", status="Open", ticket_type="INCIDENT", category="A", created_by=test_user.id, created_at=now),
            Ticket(title="Old High", description="D", priority="High", status="Open", ticket_type="INCIDENT", category="A", created_by=test_user.id, created_at=old_date),
        ]
        for t in tickets:
            db_session.add(t)
        db_session.commit()

        # Filter by recent date
        rows = list(generate_ticket_report_rows(db_session, start_date=now - timedelta(days=5)))
        assert len(rows) == 2

        # Filter by priority
        rows = list(generate_ticket_report_rows(db_session, priority="High"))
        assert len(rows) == 2

    def test_generate_sla_report_rows(self, db_session: Session, test_user: User, admin_user: User):
        """Test SLA report row generation."""
        now = datetime.now(timezone.utc)

        # Create SLA policy
        from app.models.ticket import SLAPolicy
        sla_policy = SLAPolicy(
            name="Test SLA",
            priority="High",
            response_time_minutes=60,
            resolution_time_minutes=240,
            is_active=True,
        )
        db_session.add(sla_policy)
        db_session.commit()

        ticket = Ticket(
            title="SLA Ticket",
            description="D",
            priority="High",
            status="Open",
            ticket_type="INCIDENT",
            created_by=test_user.id,
            sla_policy_id=sla_policy.id,
            sla_response_deadline=now + timedelta(hours=1),
            sla_resolution_deadline=now + timedelta(hours=4),
        )
        db_session.add(ticket)
        db_session.commit()

        rows = list(generate_sla_report_rows(db_session))
        assert len(rows) == 1
        assert len(rows[0]) == len(SLA_REPORT_HEADERS)

    def test_sla_report_summary(self, db_session: Session, test_user: User):
        """Test SLA report summary generation."""
        from app.models.ticket import SLAPolicy
        sla_policy = SLAPolicy(name="SLA1", priority="High", response_time_minutes=60, resolution_time_minutes=240, is_active=True)
        db_session.add(sla_policy)
        db_session.commit()

        now = datetime.now(timezone.utc)
        tickets = [
            Ticket(title="T1", description="D", priority="High", status="Open", ticket_type="INCIDENT", created_by=test_user.id,
                   sla_policy_id=sla_policy.id, sla_response_deadline=now + timedelta(hours=1), sla_resolution_deadline=now + timedelta(hours=4),
                   sla_response_met_at=now, sla_resolution_met_at=now),
            Ticket(title="T2", description="D", priority="High", status="Open", ticket_type="INCIDENT", created_by=test_user.id,
                   sla_policy_id=sla_policy.id, sla_response_deadline=now + timedelta(hours=1), sla_resolution_deadline=now + timedelta(hours=4),
                   sla_response_breached=True),
            Ticket(title="T3", description="D", priority="Medium", status="Open", ticket_type="INCIDENT", created_by=test_user.id,
                   sla_policy_id=sla_policy.id, sla_response_deadline=now + timedelta(hours=1), sla_resolution_deadline=now + timedelta(hours=4)),
        ]
        for t in tickets:
            db_session.add(t)
        db_session.commit()

        summary = get_sla_report_summary(db_session)
        assert summary["response_sla"]["total"] == 3
        assert summary["response_sla"]["met"] == 1
        assert summary["response_sla"]["breached"] == 1
        assert summary["response_sla"]["pending"] == 1

    def test_sla_breach_report_rows(self, db_session: Session, test_user: User):
        """Test SLA breach report row generation."""
        from app.models.ticket import SLAPolicy
        sla_policy = SLAPolicy(name="SLA1", priority="High", response_time_minutes=60, resolution_time_minutes=240, is_active=True)
        db_session.add(sla_policy)
        db_session.commit()

        now = datetime.now(timezone.utc)
        tickets = [
            Ticket(title="Response Breach", description="D", priority="High", status="Open", ticket_type="INCIDENT", created_by=test_user.id,
                   sla_policy_id=sla_policy.id, sla_response_breached=True),
            Ticket(title="Resolution Breach", description="D", priority="High", status="Open", ticket_type="INCIDENT", created_by=test_user.id,
                   sla_policy_id=sla_policy.id, sla_resolution_breached=True),
            Ticket(title="Both Breach", description="D", priority="High", status="Open", ticket_type="INCIDENT", created_by=test_user.id,
                   sla_policy_id=sla_policy.id, sla_response_breached=True, sla_resolution_breached=True),
            Ticket(title="No Breach", description="D", priority="High", status="Open", ticket_type="INCIDENT", created_by=test_user.id,
                   sla_policy_id=sla_policy.id),
        ]
        for t in tickets:
            db_session.add(t)
        db_session.commit()

        rows = list(generate_sla_breach_report_rows(db_session))
        assert len(rows) == 3  # Only breached tickets

        # Test filter by breach type
        rows = list(generate_sla_breach_report_rows(db_session, breach_type="response"))
        assert len(rows) == 2  # Response Breach + Both Breach

    def test_generate_escalation_report_rows(self, db_session: Session, test_user: User, admin_user: User, technician_user: User):
        """Test escalation report row generation."""
        ticket = Ticket(
            title="Escalated Ticket",
            description="D",
            priority="Critical",
            status="Open",
            ticket_type="INCIDENT",
            category="Network",
            created_by=test_user.id,
            assigned_to=technician_user.id,
        )
        db_session.add(ticket)
        db_session.commit()

        esc = EscalationRecord(
            ticket_id=ticket.id,
            event_type=EscalationEventType.RESPONSE_BREACH,
            recipient_id=admin_user.id,
            notification_created=True,
            email_sent=True,
        )
        db_session.add(esc)
        db_session.commit()

        rows = list(generate_escalation_report_rows(db_session))
        assert len(rows) == 1
        assert len(rows[0]) == len(ESCALATION_REPORT_HEADERS)

    def test_escalation_report_summary(self, db_session: Session, test_user: User, admin_user: User):
        """Test escalation report summary generation."""
        ticket = Ticket(title="T", description="D", priority="Critical", status="Open", ticket_type="INCIDENT", created_by=test_user.id)
        db_session.add(ticket)
        db_session.commit()

        esc1 = EscalationRecord(ticket_id=ticket.id, event_type=EscalationEventType.RESPONSE_BREACH, recipient_id=admin_user.id)
        esc2 = EscalationRecord(ticket_id=ticket.id, event_type=EscalationEventType.RESOLUTION_BREACH, recipient_id=admin_user.id)
        db_session.add_all([esc1, esc2])
        db_session.commit()

        summary = get_escalation_report_summary(db_session)
        assert summary["total_escalations"] == 2
        assert summary["by_event_type"]["RESPONSE_BREACH"] == 1
        assert summary["by_event_type"]["RESOLUTION_BREACH"] == 1
        assert summary["by_priority"]["Critical"] == 2
        assert summary["by_recipient_role"]["Admin"] == 2

    def test_generate_technician_report_rows(self, db_session: Session, admin_user: User, technician_user: User, test_user: User):
        """Test technician report row generation."""
        tickets = [
            Ticket(title="T1", description="D", priority="High", status="Open", ticket_type="INCIDENT", created_by=test_user.id, assigned_to=technician_user.id),
            Ticket(title="T2", description="D", priority="High", status="Resolved", ticket_type="INCIDENT", created_by=test_user.id, resolved_by=technician_user.id, resolved_at=datetime.now(timezone.utc)),
        ]
        for t in tickets:
            db_session.add(t)
        db_session.commit()

        # Generate rows - may include other technicians from other tests
        rows = list(generate_technician_report_rows(db_session))
        assert len(rows) >= 2  # At least admin + technician from fixtures

        # Check that our technician has the right data
        tech_row = next(r for r in rows if r[2] == technician_user.email)
        assert tech_row[5] >= 1  # Open Assigned Tickets
        assert tech_row[6] >= 1  # Tickets Resolved

    def test_technician_report_summary(self, db_session: Session, admin_user: User, technician_user: User, test_user: User):
        """Test technician report summary generation."""
        tickets = [
            Ticket(title="T1", description="D", priority="High", status="Open", ticket_type="INCIDENT", created_by=test_user.id, assigned_to=technician_user.id),
            Ticket(title="T2", description="D", priority="High", status="Resolved", ticket_type="INCIDENT", created_by=test_user.id, resolved_by=technician_user.id, resolved_at=datetime.now(timezone.utc)),
        ]
        for t in tickets:
            db_session.add(t)
        db_session.commit()

        summary = get_technician_report_summary(db_session)
        assert summary["total_technicians"] >= 2  # At least admin + technician from fixtures
        assert summary["total_assigned"] >= 1
        assert summary["total_resolved"] >= 1

    def test_csv_generation(self):
        """Test CSV stream generation."""
        headers = ["A", "B", "C"]
        def row_gen():
            yield [1, 2, 3]
            yield ["a", "b,c", "d"]  # Test comma escaping
            yield ["x", "y\nz", 'w"z']  # Test newline and quote escaping

        output = list(_generate_csv_stream(headers, row_gen()))
        assert len(output) == 4  # Header + 3 rows

        # Check header
        assert "A,B,C" in output[0]

        # Check escaping
        csv_content = "".join(output)
        assert '"b,c"' in csv_content  # Comma escaped
        assert '"y\nz"' in csv_content  # Newline escaped
        # Quote escaping: w"z -> """w""""z""" in CSV (cell is quoted, internal quotes doubled)
        assert '"""w""""z"""' in csv_content


class TestReportsAPI:
    """Tests for Reports API endpoints."""

    def test_list_reports_admin(self, client: TestClient, admin_auth_headers):
        """Test listing reports as admin."""
        response = client.get("/reports/", headers=admin_auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "reports" in data
        report_types = [r["type"] for r in data["reports"]]
        assert "tickets" in report_types
        assert "sla" in report_types
        assert "sla_breaches" in report_types
        assert "escalations" in report_types
        assert "technicians" in report_types

    def test_list_reports_technician_forbidden(self, client: TestClient, tech_auth_headers):
        """Test listing reports as technician (forbidden)."""
        response = client.get("/reports/", headers=tech_auth_headers)
        assert response.status_code == 403

    def test_list_reports_employee_forbidden(self, client: TestClient, auth_headers):
        """Test listing reports as employee (forbidden)."""
        response = client.get("/reports/", headers=auth_headers)
        assert response.status_code == 403

    def test_tickets_report_json_admin(self, client: TestClient, admin_auth_headers, db_session: Session, test_user: User):
        """Test ticket report JSON as admin."""
        ticket = Ticket(title="T1", description="D", priority="High", status="Open", ticket_type="INCIDENT", created_by=test_user.id)
        db_session.add(ticket)
        db_session.commit()

        response = client.get("/reports/tickets", headers=admin_auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["report_type"] == "tickets"
        assert "summary" in data
        assert data["summary"]["total_tickets"] == 1

    def test_tickets_report_csv_admin(self, client: TestClient, admin_auth_headers, db_session: Session, test_user: User):
        """Test ticket report CSV export as admin."""
        ticket = Ticket(title="T1", description="D", priority="High", status="Open", ticket_type="INCIDENT", created_by=test_user.id)
        db_session.add(ticket)
        db_session.commit()

        response = client.get("/reports/tickets/export", headers=admin_auth_headers)
        assert response.status_code == 200
        assert response.headers["content-type"] == "text/csv; charset=utf-8"
        assert "attachment; filename=" in response.headers["content-disposition"]
        content = response.content.decode("utf-8")
        assert "Ticket ID" in content
        assert "T1" in content

    def test_sla_report_json_admin(self, client: TestClient, admin_auth_headers, db_session: Session, test_user: User):
        """Test SLA report JSON as admin."""
        from app.models.ticket import SLAPolicy
        sla_policy = SLAPolicy(name="SLA1", priority="High", response_time_minutes=60, resolution_time_minutes=240, is_active=True)
        db_session.add(sla_policy)
        Ticket(title="T1", description="D", priority="High", status="Open", ticket_type="INCIDENT", created_by=test_user.id,
               sla_policy_id=sla_policy.id)
        db_session.commit()

        response = client.get("/reports/sla", headers=admin_auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["report_type"] == "sla"
        assert "summary" in data

    def test_sla_report_csv_admin(self, client: TestClient, admin_auth_headers, db_session: Session, test_user: User):
        """Test SLA report CSV export as admin."""
        from app.models.ticket import SLAPolicy
        sla_policy = SLAPolicy(name="SLA1", priority="High", response_time_minutes=60, resolution_time_minutes=240, is_active=True)
        db_session.add(sla_policy)
        Ticket(title="T1", description="D", priority="High", status="Open", ticket_type="INCIDENT", created_by=test_user.id,
               sla_policy_id=sla_policy.id)
        db_session.commit()

        response = client.get("/reports/sla/export", headers=admin_auth_headers)
        assert response.status_code == 200
        assert response.headers["content-type"] == "text/csv; charset=utf-8"
        content = response.content.decode("utf-8")
        assert "Ticket ID" in content

    def test_sla_breaches_report_csv_admin(self, client: TestClient, admin_auth_headers, db_session: Session, test_user: User):
        """Test SLA breach report CSV export as admin."""
        from app.models.ticket import SLAPolicy
        sla_policy = SLAPolicy(name="SLA1", priority="High", response_time_minutes=60, resolution_time_minutes=240, is_active=True)
        db_session.add(sla_policy)
        Ticket(title="T1", description="D", priority="High", status="Open", ticket_type="INCIDENT", created_by=test_user.id,
               sla_policy_id=sla_policy.id, sla_response_breached=True)
        db_session.commit()

        response = client.get("/reports/sla/breaches/export", headers=admin_auth_headers)
        assert response.status_code == 200
        content = response.content.decode("utf-8")
        assert "Breach Types" in content

    def test_escalations_report_json_admin(self, client: TestClient, admin_auth_headers, db_session: Session, test_user: User, admin_user: User):
        """Test escalation report JSON as admin."""
        ticket = Ticket(title="T", description="D", priority="Critical", status="Open", ticket_type="INCIDENT", created_by=test_user.id)
        db_session.add(ticket)
        db_session.commit()

        esc = EscalationRecord(ticket_id=ticket.id, event_type=EscalationEventType.RESPONSE_BREACH, recipient_id=admin_user.id)
        db_session.add(esc)
        db_session.commit()

        response = client.get("/reports/escalations", headers=admin_auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["report_type"] == "escalations"
        assert data["summary"]["total_escalations"] == 1

    def test_escalations_report_csv_admin(self, client: TestClient, admin_auth_headers, db_session: Session, test_user: User, admin_user: User):
        """Test escalation report CSV export as admin."""
        ticket = Ticket(title="T", description="D", priority="Critical", status="Open", ticket_type="INCIDENT", created_by=test_user.id)
        db_session.add(ticket)
        db_session.commit()

        esc = EscalationRecord(ticket_id=ticket.id, event_type=EscalationEventType.RESPONSE_BREACH, recipient_id=admin_user.id)
        db_session.add(esc)
        db_session.commit()

        response = client.get("/reports/escalations/export", headers=admin_auth_headers)
        assert response.status_code == 200
        content = response.content.decode("utf-8")
        assert "Escalation ID" in content

    def test_technicians_report_json_admin(self, client: TestClient, admin_auth_headers, db_session: Session, test_user: User, technician_user: User):
        """Test technician report JSON as admin."""
        ticket = Ticket(title="T1", description="D", priority="High", status="Open", ticket_type="INCIDENT", created_by=test_user.id, assigned_to=technician_user.id)
        db_session.add(ticket)
        db_session.commit()

        response = client.get("/reports/technicians", headers=admin_auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["report_type"] == "technicians"
        assert data["summary"]["total_technicians"] >= 1

    def test_technicians_report_csv_admin(self, client: TestClient, admin_auth_headers, db_session: Session, test_user: User, technician_user: User):
        """Test technician report CSV export as admin."""
        ticket = Ticket(title="T1", description="D", priority="High", status="Open", ticket_type="INCIDENT", created_by=test_user.id, assigned_to=technician_user.id)
        db_session.add(ticket)
        db_session.commit()

        response = client.get("/reports/technicians/export", headers=admin_auth_headers)
        assert response.status_code == 200
        content = response.content.decode("utf-8")
        assert "Technician ID" in content

    def test_tickets_report_with_filters(self, client: TestClient, admin_auth_headers, db_session: Session, test_user: User):
        """Test ticket report with various filters."""
        now = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        old = (datetime.now(timezone.utc) - timedelta(days=10)).strftime("%Y-%m-%d")

        ticket1 = Ticket(title="Recent High", description="D", priority="High", status="Open", ticket_type="INCIDENT", category="A", created_by=test_user.id)
        ticket2 = Ticket(title="Recent Low", description="D", priority="Low", status="Open", ticket_type="INCIDENT", category="A", created_by=test_user.id)
        db_session.add(ticket1)
        db_session.add(ticket2)
        db_session.commit()

        # Filter by priority
        response = client.get(f"/reports/tickets?priority=High", headers=admin_auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["summary"]["total_tickets"] == 1

        # Filter by date
        response = client.get(f"/reports/tickets?start_date={old}&end_date={now}", headers=admin_auth_headers)
        assert response.status_code == 200

    def test_reports_unauthenticated(self, client: TestClient):
        """Test reports endpoints without authentication."""
        response = client.get("/reports/tickets")
        assert response.status_code in [401, 403]

    def test_reports_csv_empty_result(self, client: TestClient, admin_auth_headers):
        """Test CSV export with empty results."""
        response = client.get("/reports/tickets/export", headers=admin_auth_headers)
        assert response.status_code == 200
        content = response.content.decode("utf-8")
        # Should have headers even with no data
        assert "Ticket ID" in content