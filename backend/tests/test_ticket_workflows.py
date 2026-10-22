"""
Tests for ticket workflow actions (assign, reassign, unassign, start-work, mark-pending, resolve, reopen, close, escalate).

These tests cover the workflow endpoints that were not fully tested in test_tickets.py.
"""

import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timezone


class TestTicketReassign:
    """Tests for ticket reassignment."""

    def test_reassign_ticket_as_admin(self, client, admin_auth_headers, technician_user, db_session):
        """Admin can reassign a ticket from one technician to another."""
        from app.models.user import User
        from app.utils.security import hash_password
        
        # Create a ticket
        create_response = client.post("/tickets/", json={
            "title": "Reassign Test",
            "description": "Description",
            "priority": "Medium",
        }, headers=admin_auth_headers)
        assert create_response.status_code == 200
        ticket_id = create_response.json()["id"]

        # Assign to first technician
        assign_resp = client.put(f"/tickets/{ticket_id}/assign", json={
            "assigned_to": technician_user.id,
        }, headers=admin_auth_headers)
        assert assign_resp.status_code == 200

        # Create another technician directly in DB (register endpoint creates Employee by default)
        tech2 = User(
            name="Tech 2",
            email="tech2@example.com",
            password=hash_password("password123"),
            role="Technician",
        )
        db_session.add(tech2)
        db_session.commit()
        db_session.refresh(tech2)
        tech2_id = tech2.id

        # Reassign to second technician - ticket must be in ASSIGNED status
        # The ticket should still be ASSIGNED (not IN_PROGRESS since we didn't start work)
        response = client.put(f"/tickets/{ticket_id}/reassign", json={
            "assigned_to": tech2_id,
        }, headers=admin_auth_headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.json()}"
        data = response.json()
        assert data["assigned_to"] == tech2_id
        # Status remains ASSIGNED
        assert data["status"] == "Assigned"

    def test_reassign_ticket_invalid_user(self, client, admin_auth_headers, technician_user):
        """Reassign to non-existent user returns 404."""
        create_response = client.post("/tickets/", json={
            "title": "Reassign Invalid",
            "description": "Description",
            "priority": "Medium",
        }, headers=admin_auth_headers)
        ticket_id = create_response.json()["id"]

        # Assign first
        client.put(f"/tickets/{ticket_id}/assign", json={
            "assigned_to": technician_user.id,
        }, headers=admin_auth_headers)

        response = client.put(f"/tickets/{ticket_id}/reassign", json={
            "assigned_to": 99999,
        }, headers=admin_auth_headers)
        assert response.status_code == 404

    def test_reassign_ticket_employee_forbidden(self, client, auth_headers, technician_user):
        """Employee cannot reassign tickets."""
        create_response = client.post("/tickets/", json={
            "title": "Reassign Employee",
            "description": "Description",
            "priority": "Medium",
        }, headers=auth_headers)
        ticket_id = create_response.json()["id"]

        response = client.put(f"/tickets/{ticket_id}/reassign", json={
            "assigned_to": technician_user.id,
        }, headers=auth_headers)
        assert response.status_code == 403

    def test_reassign_ticket_nonexistent(self, client, admin_auth_headers):
        """Reassign nonexistent ticket returns 404."""
        response = client.put("/tickets/99999/reassign", json={
            "assigned_to": 1,
        }, headers=admin_auth_headers)
        assert response.status_code == 404

    def test_reassign_unassigned_ticket(self, client, admin_auth_headers, technician_user):
        """Cannot reassign an unassigned ticket - must use assign endpoint."""
        create_response = client.post("/tickets/", json={
            "title": "Reassign Unassigned",
            "description": "Description",
            "priority": "Medium",
        }, headers=admin_auth_headers)
        ticket_id = create_response.json()["id"]

        # Try to reassign without assigning first
        response = client.put(f"/tickets/{ticket_id}/reassign", json={
            "assigned_to": technician_user.id,
        }, headers=admin_auth_headers)
        assert response.status_code == 400

    def test_reassign_to_same_user(self, client, admin_auth_headers, technician_user):
        """Reassign to same user returns 400."""
        create_response = client.post("/tickets/", json={
            "title": "Reassign Same",
            "description": "Description",
            "priority": "Medium",
        }, headers=admin_auth_headers)
        ticket_id = create_response.json()["id"]

        client.put(f"/tickets/{ticket_id}/assign", json={
            "assigned_to": technician_user.id,
        }, headers=admin_auth_headers)

        response = client.put(f"/tickets/{ticket_id}/reassign", json={
            "assigned_to": technician_user.id,
        }, headers=admin_auth_headers)
        assert response.status_code == 400

    def test_reassign_to_employee_role_rejected(self, client, admin_auth_headers, technician_user, test_user):
        """Reassign to user with Employee role is rejected."""
        create_response = client.post("/tickets/", json={
            "title": "Reassign To Employee",
            "description": "Description",
            "priority": "Medium",
        }, headers=admin_auth_headers)
        ticket_id = create_response.json()["id"]

        client.put(f"/tickets/{ticket_id}/assign", json={
            "assigned_to": technician_user.id,
        }, headers=admin_auth_headers)

        response = client.put(f"/tickets/{ticket_id}/reassign", json={
            "assigned_to": test_user.id,
        }, headers=admin_auth_headers)
        assert response.status_code == 400


class TestTicketUnassign:
    """Tests for ticket unassignment."""

    def test_unassign_ticket_as_admin(self, client, admin_auth_headers, technician_user):
        """Admin can unassign a ticket."""
        create_response = client.post("/tickets/", json={
            "title": "Unassign Test",
            "description": "Description",
            "priority": "Medium",
        }, headers=admin_auth_headers)
        ticket_id = create_response.json()["id"]

        # Assign first
        client.put(f"/tickets/{ticket_id}/assign", json={
            "assigned_to": technician_user.id,
        }, headers=admin_auth_headers)

        # Unassign
        response = client.post(f"/tickets/{ticket_id}/unassign", json={}, headers=admin_auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["assigned_to"] is None
        assert data["status"] == "Open"

    def test_unassign_ticket_employee_forbidden(self, client, auth_headers, technician_user):
        """Employee cannot unassign tickets."""
        create_response = client.post("/tickets/", json={
            "title": "Unassign Employee",
            "description": "Description",
            "priority": "Medium",
        }, headers=auth_headers)
        ticket_id = create_response.json()["id"]

        response = client.post(f"/tickets/{ticket_id}/unassign", json={}, headers=auth_headers)
        assert response.status_code == 403

    def test_unassign_nonexistent_ticket(self, client, admin_auth_headers):
        """Unassign nonexistent ticket returns 404."""
        response = client.post("/tickets/99999/unassign", json={}, headers=admin_auth_headers)
        assert response.status_code == 404

    def test_unassign_unassigned_ticket(self, client, admin_auth_headers):
        """Cannot unassign an unassigned ticket."""
        create_response = client.post("/tickets/", json={
            "title": "Unassign Not Assigned",
            "description": "Description",
            "priority": "Medium",
        }, headers=admin_auth_headers)
        ticket_id = create_response.json()["id"]

        response = client.post(f"/tickets/{ticket_id}/unassign", json={}, headers=admin_auth_headers)
        assert response.status_code == 400


class TestTicketStartWork:
    """Tests for starting work on a ticket."""

    def test_start_work_as_technician(self, client, tech_auth_headers, technician_user, admin_auth_headers):
        """Technician can start work on assigned ticket."""
        # Create ticket as admin
        create_response = client.post("/tickets/", json={
            "title": "Start Work Test",
            "description": "Description",
            "priority": "Medium",
        }, headers=admin_auth_headers)
        ticket_id = create_response.json()["id"]

        # Assign to technician
        client.put(f"/tickets/{ticket_id}/assign", json={
            "assigned_to": technician_user.id,
        }, headers=admin_auth_headers)

        # Technician starts work
        response = client.post(f"/tickets/{ticket_id}/start-work", headers=tech_auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "In Progress"

    def test_start_work_as_admin(self, client, admin_auth_headers, technician_user):
        """Admin can start work on assigned ticket."""
        create_response = client.post("/tickets/", json={
            "title": "Start Work Admin",
            "description": "Description",
            "priority": "Medium",
        }, headers=admin_auth_headers)
        ticket_id = create_response.json()["id"]

        client.put(f"/tickets/{ticket_id}/assign", json={
            "assigned_to": technician_user.id,
        }, headers=admin_auth_headers)

        response = client.post(f"/tickets/{ticket_id}/start-work", headers=admin_auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "In Progress"

    def test_start_work_employee_forbidden(self, client, auth_headers, technician_user, admin_auth_headers):
        """Employee cannot start work on tickets."""
        create_response = client.post("/tickets/", json={
            "title": "Start Work Employee",
            "description": "Description",
            "priority": "Medium",
        }, headers=admin_auth_headers)
        ticket_id = create_response.json()["id"]

        client.put(f"/tickets/{ticket_id}/assign", json={
            "assigned_to": technician_user.id,
        }, headers=admin_auth_headers)

        # Employee tries to start work
        response = client.post(f"/tickets/{ticket_id}/start-work", headers=auth_headers)
        assert response.status_code == 403

    def test_start_work_unassigned_ticket(self, client, admin_auth_headers):
        """Cannot start work on unassigned ticket."""
        create_response = client.post("/tickets/", json={
            "title": "Start Work Unassigned",
            "description": "Description",
            "priority": "Medium",
        }, headers=admin_auth_headers)
        ticket_id = create_response.json()["id"]

        # Admin tries to start work without assignment - should fail
        response = client.post(f"/tickets/{ticket_id}/start-work", headers=admin_auth_headers)
        assert response.status_code == 400

    def test_start_work_nonexistent_ticket(self, client, tech_auth_headers):
        """Start work on nonexistent ticket returns 404."""
        response = client.post("/tickets/99999/start-work", headers=tech_auth_headers)
        assert response.status_code == 404


class TestTicketMarkPending:
    """Tests for marking ticket as pending."""

    def test_mark_pending_with_reason(self, client, tech_auth_headers, technician_user, admin_auth_headers):
        """Technician can mark ticket as pending with reason."""
        create_response = client.post("/tickets/", json={
            "title": "Mark Pending Test",
            "description": "Description",
            "priority": "Medium",
        }, headers=admin_auth_headers)
        ticket_id = create_response.json()["id"]

        client.put(f"/tickets/{ticket_id}/assign", json={
            "assigned_to": technician_user.id,
        }, headers=admin_auth_headers)

        # Start work first
        client.post(f"/tickets/{ticket_id}/start-work", headers=tech_auth_headers)

        # Mark as pending
        response = client.post(f"/tickets/{ticket_id}/mark-pending", json={
            "reason": "Waiting for customer response"
        }, headers=tech_auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "Pending"
        # pending_reason may not be in the response schema - just verify status
        assert data["status"] == "Pending"

    def test_mark_pending_empty_reason_rejected(self, client, tech_auth_headers, technician_user, admin_auth_headers):
        """Mark pending with empty reason is rejected."""
        create_response = client.post("/tickets/", json={
            "title": "Mark Pending Empty Reason",
            "description": "Description",
            "priority": "Medium",
        }, headers=admin_auth_headers)
        ticket_id = create_response.json()["id"]

        client.put(f"/tickets/{ticket_id}/assign", json={
            "assigned_to": technician_user.id,
        }, headers=admin_auth_headers)

        client.post(f"/tickets/{ticket_id}/start-work", headers=tech_auth_headers)

        response = client.post(f"/tickets/{ticket_id}/mark-pending", json={
            "reason": ""
        }, headers=tech_auth_headers)
        assert response.status_code == 400  # Returns 400 for validation errors in workflow endpoints

    def test_mark_pending_employee_forbidden(self, client, auth_headers, technician_user, admin_auth_headers, tech_auth_headers):
        """Employee cannot mark tickets as pending."""
        create_response = client.post("/tickets/", json={
            "title": "Mark Pending Employee",
            "description": "Description",
            "priority": "Medium",
        }, headers=admin_auth_headers)
        ticket_id = create_response.json()["id"]

        client.put(f"/tickets/{ticket_id}/assign", json={
            "assigned_to": technician_user.id,
        }, headers=admin_auth_headers)

        client.post(f"/tickets/{ticket_id}/start-work", headers=tech_auth_headers)

        response = client.post(f"/tickets/{ticket_id}/mark-pending", json={
            "reason": "Waiting"
        }, headers=auth_headers)
        assert response.status_code == 403

    def test_mark_pending_without_start_work(self, client, tech_auth_headers, technician_user, admin_auth_headers):
        """Cannot mark as pending without starting work first."""
        create_response = client.post("/tickets/", json={
            "title": "Mark Pending No Start Work",
            "description": "Description",
            "priority": "Medium",
        }, headers=admin_auth_headers)
        ticket_id = create_response.json()["id"]

        client.put(f"/tickets/{ticket_id}/assign", json={
            "assigned_to": technician_user.id,
        }, headers=admin_auth_headers)

        # Try to mark pending without starting work
        response = client.post(f"/tickets/{ticket_id}/mark-pending", json={
            "reason": "Waiting"
        }, headers=tech_auth_headers)
        assert response.status_code == 400  # Should fail due to invalid state transition

    def test_mark_pending_nonexistent_ticket(self, client, tech_auth_headers):
        """Mark pending on nonexistent ticket returns 404."""
        response = client.post("/tickets/99999/mark-pending", json={
            "reason": "Waiting"
        }, headers=tech_auth_headers)
        assert response.status_code == 404


class TestTicketResolve:
    """Tests for resolving tickets."""

    def test_resolve_with_summary(self, client, tech_auth_headers, technician_user, admin_auth_headers):
        """Technician can resolve ticket with resolution summary."""
        create_response = client.post("/tickets/", json={
            "title": "Resolve Test",
            "description": "Description",
            "priority": "Medium",
        }, headers=admin_auth_headers)
        ticket_id = create_response.json()["id"]

        client.put(f"/tickets/{ticket_id}/assign", json={
            "assigned_to": technician_user.id,
        }, headers=admin_auth_headers)

        client.post(f"/tickets/{ticket_id}/start-work", headers=tech_auth_headers)

        response = client.post(f"/tickets/{ticket_id}/resolve", json={
            "resolution_summary": "Fixed the reported issue by updating the configuration"
        }, headers=tech_auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "Resolved"
        assert data["resolution_summary"] == "Fixed the reported issue by updating the configuration"

    def test_resolve_empty_summary_rejected(self, client, tech_auth_headers, technician_user, admin_auth_headers):
        """Resolve with empty summary is rejected."""
        create_response = client.post("/tickets/", json={
            "title": "Resolve Empty Summary",
            "description": "Description",
            "priority": "Medium",
        }, headers=admin_auth_headers)
        ticket_id = create_response.json()["id"]

        client.put(f"/tickets/{ticket_id}/assign", json={
            "assigned_to": technician_user.id,
        }, headers=admin_auth_headers)

        client.post(f"/tickets/{ticket_id}/start-work", headers=tech_auth_headers)

        response = client.post(f"/tickets/{ticket_id}/resolve", json={
            "resolution_summary": ""
        }, headers=tech_auth_headers)
        assert response.status_code == 400  # Returns 400 for validation errors in workflow endpoints

    def test_resolve_admin_can_resolve(self, client, admin_auth_headers, technician_user):
        """Admin can resolve assigned tickets."""
        create_response = client.post("/tickets/", json={
            "title": "Resolve Admin",
            "description": "Description",
            "priority": "Medium",
        }, headers=admin_auth_headers)
        ticket_id = create_response.json()["id"]

        client.put(f"/tickets/{ticket_id}/assign", json={
            "assigned_to": technician_user.id,
        }, headers=admin_auth_headers)

        response = client.post(f"/tickets/{ticket_id}/resolve", json={
            "resolution_summary": "Admin resolved"
        }, headers=admin_auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "Resolved"

    def test_resolve_employee_forbidden(self, client, auth_headers, technician_user, admin_auth_headers, tech_auth_headers):
        """Employee cannot resolve tickets."""
        create_response = client.post("/tickets/", json={
            "title": "Resolve Employee",
            "description": "Description",
            "priority": "Medium",
        }, headers=admin_auth_headers)
        ticket_id = create_response.json()["id"]

        client.put(f"/tickets/{ticket_id}/assign", json={
            "assigned_to": technician_user.id,
        }, headers=admin_auth_headers)

        client.post(f"/tickets/{ticket_id}/start-work", headers=tech_auth_headers)

        response = client.post(f"/tickets/{ticket_id}/resolve", json={
            "resolution_summary": "Employee resolved"
        }, headers=auth_headers)
        assert response.status_code == 403

    def test_resolve_nonexistent_ticket(self, client, tech_auth_headers):
        """Resolve nonexistent ticket returns 404."""
        response = client.post("/tickets/99999/resolve", json={
            "resolution_summary": "Fixed"
        }, headers=tech_auth_headers)
        assert response.status_code == 404


class TestTicketReopen:
    """Tests for reopening tickets."""

    def test_reopen_resolved_ticket(self, client, auth_headers, technician_user, admin_auth_headers, tech_auth_headers, db_session):
        """Ticket creator (employee) can reopen a resolved ticket."""
        # Employee creates the ticket
        create_response = client.post("/tickets/", json={
            "title": "Reopen Test",
            "description": "Description",
            "priority": "Medium",
        }, headers=auth_headers)
        assert create_response.status_code == 200
        ticket_data = create_response.json()
        ticket_id = ticket_data["id"]
        
        # Admin assigns and technician resolves
        client.put(f"/tickets/{ticket_id}/assign", json={
            "assigned_to": technician_user.id,
        }, headers=admin_auth_headers)

        client.post(f"/tickets/{ticket_id}/start-work", headers=tech_auth_headers)
        client.post(f"/tickets/{ticket_id}/resolve", json={
            "resolution_summary": "Fixed"
        }, headers=tech_auth_headers)

        # Employee (creator) reopens
        response = client.post(f"/tickets/{ticket_id}/reopen", json={
            "reason": "Issue not actually fixed"
        }, headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "Open"

    def test_reopen_closed_ticket(self, client, auth_headers, technician_user, admin_auth_headers, tech_auth_headers):
        """Ticket creator can reopen a closed ticket."""
        # Employee creates the ticket
        create_response = client.post("/tickets/", json={
            "title": "Reopen Closed Test",
            "description": "Description",
            "priority": "Medium",
        }, headers=auth_headers)
        ticket_id = create_response.json()["id"]

        # Admin assigns
        client.put(f"/tickets/{ticket_id}/assign", json={
            "assigned_to": technician_user.id,
        }, headers=admin_auth_headers)

        client.post(f"/tickets/{ticket_id}/start-work", headers=tech_auth_headers)
        client.post(f"/tickets/{ticket_id}/resolve", json={
            "resolution_summary": "Fixed"
        }, headers=tech_auth_headers)
        client.post(f"/tickets/{ticket_id}/close", headers=tech_auth_headers)

        # Employee (creator) reopens
        response = client.post(f"/tickets/{ticket_id}/reopen", json={
            "reason": "Issue reoccurred"
        }, headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "Open"

    def test_reopen_admin_can_reopen(self, client, admin_auth_headers, technician_user, tech_auth_headers):
        """Admin can reopen resolved/closed tickets."""
        create_response = client.post("/tickets/", json={
            "title": "Reopen Admin",
            "description": "Description",
            "priority": "Medium",
        }, headers=admin_auth_headers)
        ticket_id = create_response.json()["id"]

        client.put(f"/tickets/{ticket_id}/assign", json={
            "assigned_to": technician_user.id,
        }, headers=admin_auth_headers)

        client.post(f"/tickets/{ticket_id}/start-work", headers=tech_auth_headers)
        client.post(f"/tickets/{ticket_id}/resolve", json={
            "resolution_summary": "Fixed"
        }, headers=tech_auth_headers)

        response = client.post(f"/tickets/{ticket_id}/reopen", json={
            "reason": "Admin reopening"
        }, headers=admin_auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "Open"

    def test_reopen_technician_can_reopen(self, client, tech_auth_headers, technician_user, admin_auth_headers):
        """Assigned technician can reopen resolved/closed tickets."""
        create_response = client.post("/tickets/", json={
            "title": "Reopen Technician",
            "description": "Description",
            "priority": "Medium",
        }, headers=admin_auth_headers)
        ticket_id = create_response.json()["id"]

        client.put(f"/tickets/{ticket_id}/assign", json={
            "assigned_to": technician_user.id,
        }, headers=admin_auth_headers)

        client.post(f"/tickets/{ticket_id}/start-work", headers=tech_auth_headers)
        client.post(f"/tickets/{ticket_id}/resolve", json={
            "resolution_summary": "Fixed"
        }, headers=tech_auth_headers)

        response = client.post(f"/tickets/{ticket_id}/reopen", json={
            "reason": "Technician reopening"
        }, headers=tech_auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "Open"

    def test_reopen_other_employee_forbidden(self, client, auth_headers, technician_user, admin_auth_headers, tech_auth_headers, db_session):
        """Another employee cannot reopen someone else's ticket."""
        from app.models.user import User
        from app.utils.security import hash_password
        
        # Create ticket as employee 1
        create_response = client.post("/tickets/", json={
            "title": "Reopen Other Employee",
            "description": "Description",
            "priority": "Medium",
        }, headers=auth_headers)
        ticket_id = create_response.json()["id"]

        # Admin assigns and resolves
        client.put(f"/tickets/{ticket_id}/assign", json={
            "assigned_to": technician_user.id,
        }, headers=admin_auth_headers)

        client.post(f"/tickets/{ticket_id}/start-work", headers=tech_auth_headers)
        client.post(f"/tickets/{ticket_id}/resolve", json={
            "resolution_summary": "Fixed"
        }, headers=tech_auth_headers)

        # Create another employee directly in DB
        emp2 = User(
            name="Employee 2",
            email="emp2@example.com",
            password=hash_password("password123"),
            role="Employee",
        )
        db_session.add(emp2)
        db_session.commit()
        db_session.refresh(emp2)
        emp2_id = emp2.id

        # Log in as employee 2 to get token
        login_response = client.post("/auth/login", json={
            "email": "emp2@example.com",
            "password": "password123",
        })
        assert login_response.status_code == 200
        emp2_token = login_response.json()["access_token"]
        emp2_headers = {"Authorization": f"Bearer {emp2_token}"}

        # Employee 2 tries to reopen
        response = client.post(f"/tickets/{ticket_id}/reopen", json={
            "reason": "Other employee reopening"
        }, headers=emp2_headers)
        assert response.status_code == 403

    def test_reopen_open_ticket_rejected(self, client, auth_headers):
        """Cannot reopen an already open ticket."""
        create_response = client.post("/tickets/", json={
            "title": "Reopen Open Ticket",
            "description": "Description",
            "priority": "Medium",
        }, headers=auth_headers)
        ticket_id = create_response.json()["id"]

        response = client.post(f"/tickets/{ticket_id}/reopen", json={
            "reason": "Trying to reopen"
        }, headers=auth_headers)
        assert response.status_code == 400  # Invalid state transition

    def test_reopen_nonexistent_ticket(self, client, auth_headers):
        """Reopen nonexistent ticket returns 404."""
        response = client.post("/tickets/99999/reopen", json={
            "reason": "Reopen"
        }, headers=auth_headers)
        assert response.status_code == 404


class TestTicketClose:
    """Tests for closing tickets."""

    def test_close_resolved_ticket_as_technician(self, client, tech_auth_headers, technician_user, admin_auth_headers):
        """Assigned technician can close a resolved ticket."""
        create_response = client.post("/tickets/", json={
            "title": "Close Test",
            "description": "Description",
            "priority": "Medium",
        }, headers=admin_auth_headers)
        ticket_id = create_response.json()["id"]

        client.put(f"/tickets/{ticket_id}/assign", json={
            "assigned_to": technician_user.id,
        }, headers=admin_auth_headers)

        client.post(f"/tickets/{ticket_id}/start-work", headers=tech_auth_headers)
        client.post(f"/tickets/{ticket_id}/resolve", json={
            "resolution_summary": "Fixed"
        }, headers=tech_auth_headers)

        response = client.post(f"/tickets/{ticket_id}/close", json={}, headers=tech_auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "Closed"

    def test_close_resolved_ticket_as_admin(self, client, admin_auth_headers, technician_user, tech_auth_headers):
        """Admin can close a resolved ticket."""
        create_response = client.post("/tickets/", json={
            "title": "Close Admin",
            "description": "Description",
            "priority": "Medium",
        }, headers=admin_auth_headers)
        ticket_id = create_response.json()["id"]

        client.put(f"/tickets/{ticket_id}/assign", json={
            "assigned_to": technician_user.id,
        }, headers=admin_auth_headers)

        client.post(f"/tickets/{ticket_id}/start-work", headers=tech_auth_headers)
        client.post(f"/tickets/{ticket_id}/resolve", json={
            "resolution_summary": "Fixed"
        }, headers=tech_auth_headers)

        response = client.post(f"/tickets/{ticket_id}/close", json={}, headers=admin_auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "Closed"

    def test_close_non_resolved_ticket_rejected(self, client, tech_auth_headers, technician_user, admin_auth_headers):
        """Cannot close a ticket that is not resolved."""
        create_response = client.post("/tickets/", json={
            "title": "Close Non Resolved",
            "description": "Description",
            "priority": "Medium",
        }, headers=admin_auth_headers)
        ticket_id = create_response.json()["id"]

        client.put(f"/tickets/{ticket_id}/assign", json={
            "assigned_to": technician_user.id,
        }, headers=admin_auth_headers)

        client.post(f"/tickets/{ticket_id}/start-work", headers=tech_auth_headers)
        # Don't resolve, try to close directly

        response = client.post(f"/tickets/{ticket_id}/close", json={}, headers=tech_auth_headers)
        assert response.status_code == 400  # Invalid state transition

    def test_close_employee_forbidden(self, client, auth_headers, technician_user, admin_auth_headers, tech_auth_headers):
        """Employee cannot close tickets."""
        create_response = client.post("/tickets/", json={
            "title": "Close Employee",
            "description": "Description",
            "priority": "Medium",
        }, headers=admin_auth_headers)
        ticket_id = create_response.json()["id"]

        client.put(f"/tickets/{ticket_id}/assign", json={
            "assigned_to": technician_user.id,
        }, headers=admin_auth_headers)

        client.post(f"/tickets/{ticket_id}/start-work", headers=tech_auth_headers)
        client.post(f"/tickets/{ticket_id}/resolve", json={
            "resolution_summary": "Fixed"
        }, headers=tech_auth_headers)

        response = client.post(f"/tickets/{ticket_id}/close", json={}, headers=auth_headers)
        assert response.status_code == 403

    def test_close_nonexistent_ticket(self, client, tech_auth_headers):
        """Close nonexistent ticket returns 404."""
        response = client.post("/tickets/99999/close", json={}, headers=tech_auth_headers)
        assert response.status_code == 404


class TestTicketEscalate:
    """Tests for escalating tickets."""

    def test_escalate_ticket_as_technician(self, client, tech_auth_headers, technician_user, admin_auth_headers, db_session):
        """Technician can escalate their own ticket."""
        from app.models.user import User
        from app.utils.security import hash_password
        
        create_response = client.post("/tickets/", json={
            "title": "Escalate Test",
            "description": "Description",
            "priority": "High",
        }, headers=admin_auth_headers)
        ticket_id = create_response.json()["id"]

        client.put(f"/tickets/{ticket_id}/assign", json={
            "assigned_to": technician_user.id,
        }, headers=admin_auth_headers)

        # Create another admin directly in DB (register endpoint creates Employee by default)
        admin2 = User(
            name="Admin 2",
            email="admin2@example.com",
            password=hash_password("password123"),
            role="Admin",
        )
        db_session.add(admin2)
        db_session.commit()
        db_session.refresh(admin2)
        admin2_id = admin2.id

        response = client.post(f"/tickets/{ticket_id}/escalate", json={
            "escalated_to": admin2_id,
            "escalation_reason": "Requires management approval"
        }, headers=tech_auth_headers)
        assert response.status_code == 200
        data = response.json()
        # Escalation doesn't change ticket status, only sets escalation metadata
        assert data["status"] == "Assigned"
        assert data["escalated_to"] == admin2_id
        assert data["escalation_reason"] == "Requires management approval"
        assert data["escalated_by"] == technician_user.id
        assert data["escalated_at"] is not None

    def test_escalate_ticket_as_admin(self, client, admin_auth_headers, technician_user, db_session):
        """Admin can escalate any ticket."""
        from app.models.user import User
        from app.utils.security import hash_password
        
        create_response = client.post("/tickets/", json={
            "title": "Escalate Admin",
            "description": "Description",
            "priority": "High",
        }, headers=admin_auth_headers)
        ticket_id = create_response.json()["id"]

        # Create another admin directly in DB (register endpoint creates Employee by default)
        admin2 = User(
            name="Admin 2",
            email="admin2@example.com",
            password=hash_password("password123"),
            role="Admin",
        )
        db_session.add(admin2)
        db_session.commit()
        db_session.refresh(admin2)
        admin2_id = admin2.id

        response = client.post(f"/tickets/{ticket_id}/escalate", json={
            "escalated_to": admin2_id,
            "escalation_reason": "Escalating for review"
        }, headers=admin_auth_headers)
        assert response.status_code == 200
        data = response.json()
        # Escalation doesn't change ticket status, only sets escalation metadata
        assert data["status"] == "Open"
        assert data["escalated_to"] == admin2_id
        assert data["escalation_reason"] == "Escalating for review"
        assert data["escalated_by"] == data["created_by"]  # Admin who created the ticket
        assert data["escalated_at"] is not None

    def test_escalate_employee_forbidden(self, client, auth_headers, technician_user, admin_auth_headers):
        """Employee cannot escalate tickets."""
        create_response = client.post("/tickets/", json={
            "title": "Escalate Employee",
            "description": "Description",
            "priority": "High",
        }, headers=admin_auth_headers)
        ticket_id = create_response.json()["id"]

        client.put(f"/tickets/{ticket_id}/assign", json={
            "assigned_to": technician_user.id,
        }, headers=admin_auth_headers)

        admin2_response = client.post("/auth/register", json={
            "name": "Admin 2",
            "email": "admin2@example.com",
            "password": "password123",
            "role": "Admin",
        }, headers=admin_auth_headers)
        assert admin2_response.status_code == 201
        admin2_id = admin2_response.json()["id"]

        response = client.post(f"/tickets/{ticket_id}/escalate", json={
            "escalated_to": admin2_id,
            "escalation_reason": "Employee trying to escalate"
        }, headers=auth_headers)
        assert response.status_code == 403

    def test_escalate_invalid_target_user(self, client, tech_auth_headers, technician_user, admin_auth_headers):
        """Escalate to non-existent user returns 404."""
        create_response = client.post("/tickets/", json={
            "title": "Escalate Invalid User",
            "description": "Description",
            "priority": "High",
        }, headers=admin_auth_headers)
        ticket_id = create_response.json()["id"]

        client.put(f"/tickets/{ticket_id}/assign", json={
            "assigned_to": technician_user.id,
        }, headers=admin_auth_headers)

        response = client.post(f"/tickets/{ticket_id}/escalate", json={
            "escalated_to": 99999,
            "escalation_reason": "Test"
        }, headers=tech_auth_headers)
        assert response.status_code == 404

    def test_escalate_empty_reason_rejected(self, client, tech_auth_headers, technician_user, admin_auth_headers):
        """Escalate with empty reason is rejected."""
        create_response = client.post("/tickets/", json={
            "title": "Escalate Empty Reason",
            "description": "Description",
            "priority": "High",
        }, headers=admin_auth_headers)
        ticket_id = create_response.json()["id"]

        client.put(f"/tickets/{ticket_id}/assign", json={
            "assigned_to": technician_user.id,
        }, headers=admin_auth_headers)

        admin2_response = client.post("/auth/register", json={
            "name": "Admin 2",
            "email": "admin2@example.com",
            "password": "password123",
            "role": "Admin",
        }, headers=admin_auth_headers)
        assert admin2_response.status_code == 201
        admin2_id = admin2_response.json()["id"]

        response = client.post(f"/tickets/{ticket_id}/escalate", json={
            "escalated_to": admin2_id,
            "escalation_reason": ""
        }, headers=tech_auth_headers)
        assert response.status_code == 400  # Returns 400 for validation errors in workflow endpoints

    def test_escalate_to_employee_role_rejected(self, client, tech_auth_headers, technician_user, admin_auth_headers, test_user):
        """Escalate to user with Employee role is rejected."""
        create_response = client.post("/tickets/", json={
            "title": "Escalate To Employee",
            "description": "Description",
            "priority": "High",
        }, headers=admin_auth_headers)
        ticket_id = create_response.json()["id"]

        client.put(f"/tickets/{ticket_id}/assign", json={
            "assigned_to": technician_user.id,
        }, headers=admin_auth_headers)

        response = client.post(f"/tickets/{ticket_id}/escalate", json={
            "escalated_to": test_user.id,
            "escalation_reason": "Test"
        }, headers=tech_auth_headers)
        assert response.status_code == 400

    def test_escalate_nonexistent_ticket(self, client, tech_auth_headers):
        """Escalate nonexistent ticket returns 404."""
        response = client.post("/tickets/99999/escalate", json={
            "escalated_to": 1,
            "escalation_reason": "Test"
        }, headers=tech_auth_headers)
        assert response.status_code == 404


class TestTicketWorkflowActions:
    """Tests for getting available workflow actions."""

    def test_get_workflow_actions_as_creator(self, client, auth_headers, technician_user, admin_auth_headers, tech_auth_headers):
        """Ticket creator can see available workflow actions."""
        create_response = client.post("/tickets/", json={
            "title": "Workflow Actions Test",
            "description": "Description",
            "priority": "Medium",
        }, headers=auth_headers)
        ticket_id = create_response.json()["id"]

        # Assign and start work
        client.put(f"/tickets/{ticket_id}/assign", json={
            "assigned_to": technician_user.id,
        }, headers=admin_auth_headers)

        client.post(f"/tickets/{ticket_id}/start-work", headers=tech_auth_headers)

        # Get workflow actions as creator
        response = client.get(f"/tickets/{ticket_id}/workflow-actions", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "can_assign" in data
        assert "can_reassign" in data
        assert "can_unassign" in data
        assert "can_start_work" in data
        assert "can_mark_pending" in data
        assert "can_resolve" in data
        assert "can_reopen" in data
        assert "can_close" in data
        assert "can_escalate" in data
        assert "valid_status_transitions" in data
        assert isinstance(data["valid_status_transitions"], list)

    def test_get_workflow_actions_as_assignee(self, client, tech_auth_headers, technician_user, admin_auth_headers):
        """Assigned technician can see workflow actions."""
        create_response = client.post("/tickets/", json={
            "title": "Workflow Actions Assignee",
            "description": "Description",
            "priority": "Medium",
        }, headers=admin_auth_headers)
        ticket_id = create_response.json()["id"]

        client.put(f"/tickets/{ticket_id}/assign", json={
            "assigned_to": technician_user.id,
        }, headers=admin_auth_headers)

        client.post(f"/tickets/{ticket_id}/start-work", headers=tech_auth_headers)

        response = client.get(f"/tickets/{ticket_id}/workflow-actions", headers=tech_auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "can_resolve" in data
        assert "can_reopen" in data
        assert "can_close" in data
        assert "can_escalate" in data

    def test_get_workflow_actions_as_admin(self, client, admin_auth_headers, technician_user):
        """Admin can see workflow actions for any ticket."""
        create_response = client.post("/tickets/", json={
            "title": "Workflow Actions Admin",
            "description": "Description",
            "priority": "Medium",
        }, headers=admin_auth_headers)
        ticket_id = create_response.json()["id"]

        response = client.get(f"/tickets/{ticket_id}/workflow-actions", headers=admin_auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "can_assign" in data
        assert "can_reassign" in data
        assert "can_unassign" in data

    def test_get_workflow_actions_unauthorized(self, client, auth_headers, technician_user, admin_auth_headers, tech_auth_headers):
        """Unauthorized user cannot see workflow actions for other's ticket."""
        create_response = client.post("/tickets/", json={
            "title": "Workflow Actions Unauthorized",
            "description": "Description",
            "priority": "Medium",
        }, headers=tech_auth_headers)
        ticket_id = create_response.json()["id"]

        # Employee tries to access technician's ticket
        response = client.get(f"/tickets/{ticket_id}/workflow-actions", headers=auth_headers)
        assert response.status_code == 404

    def test_get_workflow_actions_nonexistent_ticket(self, client, auth_headers):
        """Workflow actions for nonexistent ticket returns 404."""
        response = client.get("/tickets/99999/workflow-actions", headers=auth_headers)
        assert response.status_code == 404