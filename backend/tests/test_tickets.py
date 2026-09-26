import pytest
from fastapi.testclient import TestClient


class TestTicketCreation:
    def test_create_ticket_success(self, client, auth_headers):
        response = client.post("/tickets/", json={
            "title": "Test Ticket",
            "description": "This is a test ticket",
            "priority": "Medium",
        }, headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Test Ticket"
        assert data["description"] == "This is a test ticket"
        assert data["priority"] == "Medium"
        assert data["status"] == "Open"
        assert data["created_by"] == 1  # test_user id
        assert "id" in data

    def test_create_ticket_unauthorized(self, client):
        response = client.post("/tickets/", json={
            "title": "Test Ticket",
            "description": "This is a test ticket",
            "priority": "Medium",
        })
        assert response.status_code == 403

    def test_create_ticket_high_priority(self, client, auth_headers):
        response = client.post("/tickets/", json={
            "title": "Urgent Issue",
            "description": "Critical bug",
            "priority": "High",
        }, headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["priority"] == "High"


class TestTicketListing:
    def test_get_tickets_as_employee(self, client, auth_headers):
        response = client.get("/tickets/", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert "page" in data
        assert "page_size" in data
        assert "total_pages" in data

    def test_get_tickets_pagination(self, client, auth_headers):
        response = client.get("/tickets/?page=1&page_size=5", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["page"] == 1
        assert data["page_size"] == 5

    def test_get_tickets_filter_status(self, client, auth_headers):
        response = client.get("/tickets/?status=Open", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        for ticket in data["items"]:
            assert ticket["status"] == "Open"

    def test_get_tickets_filter_priority(self, client, auth_headers):
        response = client.get("/tickets/?priority=High", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        for ticket in data["items"]:
            assert ticket["priority"] == "High"

    def test_get_tickets_search(self, client, auth_headers):
        response = client.get("/tickets/?search=Test", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()


class TestTicketDetail:
    def test_get_ticket_by_id(self, client, auth_headers):
        # Create a ticket first
        create_response = client.post("/tickets/", json={
            "title": "Detail Test",
            "description": "Test description",
            "priority": "Medium",
        }, headers=auth_headers)
        ticket_id = create_response.json()["id"]

        # Get ticket by ID
        response = client.get(f"/tickets/{ticket_id}", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == ticket_id
        assert data["title"] == "Detail Test"

    def test_get_nonexistent_ticket(self, client, auth_headers):
        response = client.get("/tickets/99999", headers=auth_headers)
        assert response.status_code == 404


class TestTicketUpdate:
    def test_update_own_ticket(self, client, auth_headers, test_user):
        # Create a ticket
        create_response = client.post("/tickets/", json={
            "title": "Original Title",
            "description": "Original description",
            "priority": "Medium",
        }, headers=auth_headers)
        ticket_id = create_response.json()["id"]

        # Update the ticket
        response = client.put(f"/tickets/{ticket_id}", json={
            "title": "Updated Title",
            "description": "Updated description",
            "priority": "High",
            "status": "Open",
            "assigned_to": None,
        }, headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Updated Title"
        assert data["priority"] == "High"

    def test_partial_update_ticket(self, client, auth_headers):
        # Create a ticket
        create_response = client.post("/tickets/", json={
            "title": "Partial Update Test",
            "description": "Description",
            "priority": "Medium",
        }, headers=auth_headers)
        ticket_id = create_response.json()["id"]

        # Partial update - only title
        response = client.put(f"/tickets/{ticket_id}", json={
            "title": "New Title Only",
            "description": "Description",
            "priority": "Medium",
            "status": "Open",
            "assigned_to": None,
        }, headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "New Title Only"


class TestTicketDelete:
    def test_delete_own_ticket_as_admin(self, client, admin_auth_headers):
        # Create a ticket as admin
        create_response = client.post("/tickets/", json={
            "title": "Admin Ticket",
            "description": "Description",
            "priority": "Medium",
        }, headers=admin_auth_headers)
        ticket_id = create_response.json()["id"]

        # Delete as admin
        response = client.delete(f"/tickets/{ticket_id}", headers=admin_auth_headers)
        assert response.status_code == 200
        assert response.json()["message"] == "Ticket deleted successfully"

    def test_cannot_delete_ticket_as_employee(self, client, auth_headers):
        # Create a ticket as employee
        create_response = client.post("/tickets/", json={
            "title": "Employee Ticket",
            "description": "Description",
            "priority": "Medium",
        }, headers=auth_headers)
        ticket_id = create_response.json()["id"]

        # Try to delete as employee (should fail - only admin can delete)
        response = client.delete(f"/tickets/{ticket_id}", headers=auth_headers)
        assert response.status_code == 403


class TestTicketAssignment:
    def test_assign_ticket_as_admin(self, client, admin_auth_headers, technician_user):
        # Create a ticket
        create_response = client.post("/tickets/", json={
            "title": "Assignment Test",
            "description": "Description",
            "priority": "Medium",
        }, headers=admin_auth_headers)
        ticket_id = create_response.json()["id"]

        # Assign to technician
        response = client.put(f"/tickets/{ticket_id}/assign", json={
            "assigned_to": technician_user.id,
        }, headers=admin_auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["assigned_to"] == technician_user.id
        assert data["status"] == "Assigned"

    def test_assign_ticket_invalid_user(self, client, admin_auth_headers):
        create_response = client.post("/tickets/", json={
            "title": "Assignment Test",
            "description": "Description",
            "priority": "Medium",
        }, headers=admin_auth_headers)
        ticket_id = create_response.json()["id"]

        response = client.put(f"/tickets/{ticket_id}/assign", json={
            "assigned_to": 99999,
        }, headers=admin_auth_headers)
        assert response.status_code == 404


class TestTicketStatus:
    def test_update_status_as_technician(self, client, tech_auth_headers, technician_user, admin_auth_headers):
        # Create ticket as admin
        create_response = client.post("/tickets/", json={
            "title": "Status Test",
            "description": "Description",
            "priority": "Medium",
        }, headers=admin_auth_headers)
        ticket_id = create_response.json()["id"]

        # Assign to technician
        client.put(f"/tickets/{ticket_id}/assign", json={
            "assigned_to": technician_user.id,
        }, headers=admin_auth_headers)

        # Update status as technician
        response = client.patch(f"/tickets/{ticket_id}/status", json={
            "status": "In Progress",
        }, headers=tech_auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "In Progress"

    def test_update_status_invalid(self, client, tech_auth_headers):
        response = client.patch("/tickets/1/status", json={
            "status": "InvalidStatus",
        }, headers=tech_auth_headers)
        assert response.status_code == 422


class TestTicketAuthorization:
    def test_employee_cannot_access_other_users_ticket(self, client, auth_headers, technician_user, admin_auth_headers):
        # Create ticket as technician
        tech_response = client.post("/auth/login", json={
            "email": "tech@example.com",
            "password": "techpassword123",
        })
        tech_token = tech_response.json()["access_token"]
        tech_headers = {"Authorization": f"Bearer {tech_token}"}

        create_response = client.post("/tickets/", json={
            "title": "Tech Ticket",
            "description": "Description",
            "priority": "Medium",
        }, headers=tech_headers)
        ticket_id = create_response.json()["id"]

        # Employee tries to access technician's ticket
        response = client.get(f"/tickets/{ticket_id}", headers=auth_headers)
        assert response.status_code == 404  # Should not see other users' tickets

    def test_employee_cannot_update_other_users_ticket(self, client, auth_headers, technician_user, admin_auth_headers):
        # Create ticket as technician
        tech_response = client.post("/auth/login", json={
            "email": "tech@example.com",
            "password": "techpassword123",
        })
        tech_token = tech_response.json()["access_token"]
        tech_headers = {"Authorization": f"Bearer {tech_token}"}

        create_response = client.post("/tickets/", json={
            "title": "Tech Ticket",
            "description": "Description",
            "priority": "Medium",
        }, headers=tech_headers)
        ticket_id = create_response.json()["id"]

        # Employee tries to update technician's ticket
        response = client.put(f"/tickets/{ticket_id}", json={
            "title": "Hacked",
            "description": "Description",
            "priority": "Medium",
            "status": "Open",
            "assigned_to": None,
        }, headers=auth_headers)
        assert response.status_code == 403


class TestTicketComments:
    def test_create_comment_success(self, client, auth_headers):
        # Create a ticket first
        create_response = client.post("/tickets/", json={
            "title": "Comment Test",
            "description": "Test description",
            "priority": "Medium",
        }, headers=auth_headers)
        ticket_id = create_response.json()["id"]

        # Add a comment
        response = client.post(f"/tickets/{ticket_id}/comments", json={
            "body": "This is a test comment",
            "is_internal": False,
        }, headers=auth_headers)
        assert response.status_code == 201
        data = response.json()
        assert data["body"] == "This is a test comment"
        assert data["is_internal"] == False
        assert data["author_id"] == 1

    def test_create_internal_note_as_technician(self, client, tech_auth_headers, technician_user, admin_auth_headers):
        # Create ticket as admin
        create_response = client.post("/tickets/", json={
            "title": "Internal Note Test",
            "description": "Description",
            "priority": "Medium",
        }, headers=admin_auth_headers)
        ticket_id = create_response.json()["id"]

        # Assign ticket to technician first
        client.put(f"/tickets/{ticket_id}/assign", json={
            "assigned_to": technician_user.id,
        }, headers=admin_auth_headers)

        # Technician adds internal note
        response = client.post(f"/tickets/{ticket_id}/comments", json={
            "body": "Internal investigation note",
            "is_internal": True,
        }, headers=tech_auth_headers)
        assert response.status_code == 201
        data = response.json()
        assert data["is_internal"] == True

    def test_employee_cannot_create_internal_note(self, client, auth_headers):
        # Create a ticket
        create_response = client.post("/tickets/", json={
            "title": "Internal Note Test",
            "description": "Description",
            "priority": "Medium",
        }, headers=auth_headers)
        ticket_id = create_response.json()["id"]

        # Employee tries to add internal note
        response = client.post(f"/tickets/{ticket_id}/comments", json={
            "body": "Internal note attempt",
            "is_internal": True,
        }, headers=auth_headers)
        assert response.status_code == 403

    def test_get_comments_pagination(self, client, auth_headers):
        create_response = client.post("/tickets/", json={
            "title": "Pagination Test",
            "description": "Description",
            "priority": "Medium",
        }, headers=auth_headers)
        ticket_id = create_response.json()["id"]

        # Add multiple comments
        for i in range(5):
            client.post(f"/tickets/{ticket_id}/comments", json={
                "body": f"Comment {i}",
                "is_internal": False,
            }, headers=auth_headers)

        # Test pagination
        response = client.get(f"/tickets/{ticket_id}/comments?page=1&page_size=2", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["page"] == 1
        assert data["page_size"] == 2
        assert len(data["items"]) == 2
        assert data["total"] == 5

    def test_get_comments_unauthorized(self, client, auth_headers, technician_user, admin_auth_headers):
        # Create ticket as technician
        tech_response = client.post("/auth/login", json={
            "email": "tech@example.com",
            "password": "techpassword123",
        })
        tech_token = tech_response.json()["access_token"]
        tech_headers = {"Authorization": f"Bearer {tech_token}"}

        create_response = client.post("/tickets/", json={
            "title": "Tech Comment Test",
            "description": "Description",
            "priority": "Medium",
        }, headers=tech_headers)
        ticket_id = create_response.json()["id"]

        # Employee tries to access technician's ticket comments
        response = client.get(f"/tickets/{ticket_id}/comments", headers=auth_headers)
        assert response.status_code == 404

    def test_employee_cannot_see_internal_notes(self, client, auth_headers, technician_user, admin_auth_headers):
        # Create ticket as technician
        tech_response = client.post("/auth/login", json={
            "email": "tech@example.com",
            "password": "techpassword123",
        })
        tech_token = tech_response.json()["access_token"]
        tech_headers = {"Authorization": f"Bearer {tech_token}"}

        create_response = client.post("/tickets/", json={
            "title": "Internal Note Test",
            "description": "Description",
            "priority": "Medium",
        }, headers=tech_headers)
        ticket_id = create_response.json()["id"]

        # Technician adds internal note
        client.post(f"/tickets/{ticket_id}/comments", json={
            "body": "Internal note",
            "is_internal": True,
        }, headers=tech_headers)

        # Employee tries to get comments with internal=true
        response = client.get(f"/tickets/{ticket_id}/comments?include_internal=true", headers=auth_headers)
        assert response.status_code == 404  # Should not see internal notes

        # Employee gets comments without internal
        response = client.get(f"/tickets/{ticket_id}/comments", headers=auth_headers)
        assert response.status_code == 404  # Can't access other user's ticket at all


class TestTicketHistory:
    def test_get_ticket_history(self, client, auth_headers):
        create_response = client.post("/tickets/", json={
            "title": "History Test",
            "description": "Description",
            "priority": "Medium",
        }, headers=auth_headers)
        ticket_id = create_response.json()["id"]

        # Get history
        response = client.get(f"/tickets/{ticket_id}/history", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        # Should have at least TICKET_CREATED event
        assert len(data["items"]) >= 1

    def test_history_pagination(self, client, auth_headers):
        create_response = client.post("/tickets/", json={
            "title": "History Pagination",
            "description": "Description",
            "priority": "Medium",
        }, headers=auth_headers)
        ticket_id = create_response.json()["id"]

        # Update status multiple times to generate history
        client.patch(f"/tickets/{create_response.json()['id']}/status", json={"status": "Assigned"}, headers=auth_headers)
        client.patch(f"/tickets/{create_response.json()['id']}/status", json={"status": "In Progress"}, headers=auth_headers)

        response = client.get(f"/tickets/{create_response.json()['id']}/history?page=1&page_size=1", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["page"] == 1
        assert data["page_size"] == 1
        assert len(data["items"]) == 1

    def test_history_unauthorized(self, client, auth_headers, technician_user, admin_auth_headers):
        # Create ticket as technician
        tech_response = client.post("/auth/login", json={
            "email": "tech@example.com",
            "password": "techpassword123",
        })
        tech_token = tech_response.json()["access_token"]
        tech_headers = {"Authorization": f"Bearer {tech_token}"}

        create_response = client.post("/tickets/", json={
            "title": "Tech History Test",
            "description": "Description",
            "priority": "Medium",
        }, headers=tech_headers)
        ticket_id = create_response.json()["id"]

        # Employee tries to access technician's ticket history
        response = client.get(f"/tickets/{ticket_id}/history", headers=auth_headers)
        assert response.status_code == 404


class TestTicketTimeline:
    def test_get_timeline(self, client, auth_headers):
        create_response = client.post("/tickets/", json={
            "title": "Timeline Test",
            "description": "Description",
            "priority": "Medium",
        }, headers=auth_headers)
        ticket_id = create_response.json()["id"]

        response = client.get(f"/tickets/{ticket_id}/timeline", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert len(data["items"]) >= 1  # At least ticket creation

    def test_timeline_includes_comments(self, client, auth_headers):
        create_response = client.post("/tickets/", json={
            "title": "Timeline Comments",
            "description": "Description",
            "priority": "Medium",
        }, headers=auth_headers)
        ticket_id = create_response.json()["id"]

        # Add a comment
        client.post(f"/tickets/{ticket_id}/comments", json={
            "body": "Test comment for timeline",
            "is_internal": False,
        }, headers=auth_headers)

        response = client.get(f"/tickets/{ticket_id}/timeline", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        # Should have ticket creation + comment
        assert len(data["items"]) >= 2

    def test_timeline_unauthorized(self, client, auth_headers, technician_user, admin_auth_headers):
        tech_response = client.post("/auth/login", json={
            "email": "tech@example.com",
            "password": "techpassword123",
        })
        tech_token = tech_response.json()["access_token"]
        tech_headers = {"Authorization": f"Bearer {tech_token}"}

        create_response = client.post("/tickets/", json={
            "title": "Timeline Unauthorized",
            "description": "Description",
            "priority": "Medium",
        }, headers=tech_headers)
        ticket_id = create_response.json()["id"]

        response = client.get(f"/tickets/{ticket_id}/timeline", headers=auth_headers)
        assert response.status_code == 404


class TestTicketAttachments:
    def test_upload_attachment_success(self, client, auth_headers):
        create_response = client.post("/tickets/", json={
            "title": "Attachment Test",
            "description": "Description",
            "priority": "Medium",
        }, headers=auth_headers)
        ticket_id = create_response.json()["id"]

        # Create a simple text file
        files = {"file": ("test.txt", b"Hello World", "text/plain")}
        response = client.post(f"/tickets/{ticket_id}/attachments", files=files, headers=auth_headers)
        assert response.status_code == 201
        data = response.json()
        assert data["original_filename"] == "test.txt"
        assert data["content_type"] == "text/plain"
        assert data["file_size"] == 11

    def test_upload_attachment_unauthorized(self, client, auth_headers, technician_user, admin_auth_headers):
        tech_response = client.post("/auth/login", json={
            "email": "tech@example.com",
            "password": "techpassword123",
        })
        tech_token = tech_response.json()["access_token"]
        tech_headers = {"Authorization": f"Bearer {tech_token}"}

        create_response = client.post("/tickets/", json={
            "title": "Attachment Test",
            "description": "Description",
            "priority": "Medium",
        }, headers=tech_headers)
        ticket_id = create_response.json()["id"]

        # Employee tries to upload to technician's ticket
        files = {"file": ("test.txt", b"Hello", "text/plain")}
        response = client.post(f"/tickets/{ticket_id}/attachments", files=files, headers=auth_headers)
        assert response.status_code == 403

    def test_upload_invalid_file_type(self, client, auth_headers):
        create_response = client.post("/tickets/", json={
            "title": "Invalid Type Test",
            "description": "Description",
            "priority": "Medium",
        }, headers=auth_headers)
        ticket_id = create_response.json()["id"]

        # Try to upload an executable
        files = {"file": ("test.exe", b"MZ...", "application/x-msdownload")}
        response = client.post(f"/tickets/{ticket_id}/attachments", files=files, headers=auth_headers)
        assert response.status_code == 415

    def test_download_attachment(self, client, auth_headers):
        create_response = client.post("/tickets/", json={
            "title": "Download Test",
            "description": "Description",
            "priority": "Medium",
        }, headers=auth_headers)
        ticket_id = create_response.json()["id"]

        # Upload a file
        files = {"file": ("test.txt", b"Hello World", "text/plain")}
        upload_response = client.post(f"/tickets/{ticket_id}/attachments", files=files, headers=auth_headers)
        attachment_id = upload_response.json()["id"]

        # Download the file
        response = client.get(f"/tickets/{ticket_id}/attachments/{attachment_id}/download", headers=auth_headers)
        assert response.status_code == 200
        assert response.headers["content-type"].startswith("text/plain")
        assert response.content == b"Hello World"

    def test_delete_attachment(self, client, auth_headers):
        create_response = client.post("/tickets/", json={
            "title": "Delete Attachment Test",
            "description": "Description",
            "priority": "Medium",
        }, headers=auth_headers)
        ticket_id = create_response.json()["id"]

        # Upload a file
        files = {"file": ("test.txt", b"Hello", "text/plain")}
        upload_response = client.post(f"/tickets/{ticket_id}/attachments", files=files, headers=auth_headers)
        attachment_id = upload_response.json()["id"]

        # Delete the attachment
        response = client.delete(f"/tickets/{ticket_id}/attachments/{attachment_id}", headers=auth_headers)
        assert response.status_code == 200
        assert response.json()["message"] == "Attachment deleted successfully"

        # Try to download deleted attachment
        download_response = client.get(f"/tickets/{ticket_id}/attachments/{attachment_id}/download", headers=auth_headers)
        assert download_response.status_code == 404


class TestSLABreach:
    """Tests for SLA breach detection (Phase 2C-2)."""

    def test_response_deadline_not_reached_no_breach(self, client, auth_headers, admin_auth_headers, db_session):
        """Test that no breach is created when response deadline not reached."""
        # Create an SLA policy with 60 min response time
        from app.services.sla_service import create_sla_policy
        policy = create_sla_policy(
            db=db_session,
            name="Test Response SLA",
            priority="High",
            response_time_minutes=60,
            resolution_time_minutes=240,
        )

        # Create ticket as employee (High priority matches policy)
        response = client.post("/tickets/", json={
            "title": "SLA Test - No Breach",
            "description": "Test ticket for SLA breach detection",
            "priority": "High",
        }, headers=auth_headers)
        assert response.status_code == 200
        ticket_id = response.json()["id"]

        # Check SLA info - should have deadline but not breached
        sla_response = client.get(f"/sla/tickets/{ticket_id}", headers=auth_headers)
        assert sla_response.status_code == 200
        sla_data = sla_response.json()
        assert sla_data["has_sla"] is True
        assert sla_data["response_status"] == "RESPONSE_PENDING"
        assert sla_data["response_breached"] is False

    def test_resolution_deadline_not_reached_no_breach(self, client, auth_headers, admin_auth_headers, db_session):
        """Test that no breach is created when resolution deadline not reached."""
        from app.services.sla_service import create_sla_policy
        policy = create_sla_policy(
            db=db_session,
            name="Test Resolution SLA",
            priority="Critical",
            response_time_minutes=30,
            resolution_time_minutes=120,
        )

        response = client.post("/tickets/", json={
            "title": "SLA Test - Resolution No Breach",
            "description": "Test ticket for resolution SLA",
            "priority": "Critical",
        }, headers=auth_headers)
        assert response.status_code == 200
        ticket_id = response.json()["id"]

        sla_response = client.get(f"/sla/tickets/{ticket_id}", headers=auth_headers)
        assert sla_response.status_code == 200
        sla_data = sla_response.json()
        assert sla_data["has_sla"] is True
        assert sla_data["resolution_status"] == "RESOLUTION_PENDING"
        assert sla_data["resolution_breached"] is False

    def test_response_already_met_no_breach(self, client, auth_headers, admin_auth_headers, db_session, technician_user):
        """Test that no response breach is created when response already met."""
        from app.services.sla_service import create_sla_policy
        policy = create_sla_policy(
            db=db_session,
            name="Test Response Met",
            priority="High",
            response_time_minutes=60,
            resolution_time_minutes=240,
        )

        response = client.post("/tickets/", json={
            "title": "SLA Test - Response Met",
            "description": "Test ticket for SLA",
            "priority": "High",
        }, headers=auth_headers)
        assert response.status_code == 200
        ticket_id = response.json()["id"]

        # Assign ticket to technician first
        admin_response = client.post("/auth/login", json={
            "email": "admin@example.com",
            "password": "adminpassword123",
        })
        admin_token = admin_response.json()["access_token"]
        admin_headers = {"Authorization": f"Bearer {admin_token}"}
        
        assign_response = client.put(f"/tickets/{ticket_id}/assign", json={
            "assigned_to": technician_user.id
        }, headers=admin_headers)
        assert assign_response.status_code == 200

        # Technician starts work - marks response SLA as met
        tech_response = client.post("/auth/login", json={
            "email": "tech@example.com",
            "password": "techpassword123",
        })
        tech_token = tech_response.json()["access_token"]
        tech_headers = {"Authorization": f"Bearer {tech_token}"}

        start_response = client.post(f"/tickets/{ticket_id}/start-work", headers=tech_headers)
        assert start_response.status_code == 200

        # Check SLA - response should be met
        sla_response = client.get(f"/sla/tickets/{ticket_id}", headers=auth_headers)
        sla_data = sla_response.json()
        assert sla_data["response_status"] == "RESPONSE_MET"
        assert sla_data["response_breached"] is False

    def test_resolution_already_completed_no_breach(self, client, auth_headers, admin_auth_headers, db_session, technician_user):
        """Test that no resolution breach is created when already resolved."""
        from app.services.sla_service import create_sla_policy
        policy = create_sla_policy(
            db=db_session,
            name="Test Resolution Completed",
            priority="High",
            response_time_minutes=60,
            resolution_time_minutes=240,
        )

        response = client.post("/tickets/", json={
            "title": "SLA Test - Resolution Completed",
            "description": "Test ticket for SLA",
            "priority": "High",
        }, headers=auth_headers)
        assert response.status_code == 200
        ticket_id = response.json()["id"]

        # Assign ticket to technician first
        admin_response = client.post("/auth/login", json={
            "email": "admin@example.com",
            "password": "adminpassword123",
        })
        admin_token = admin_response.json()["access_token"]
        admin_headers = {"Authorization": f"Bearer {admin_token}"}
        
        assign_response = client.put(f"/tickets/{ticket_id}/assign", json={
            "assigned_to": technician_user.id
        }, headers=admin_headers)
        assert assign_response.status_code == 200

        tech_response = client.post("/auth/login", json={
            "email": "tech@example.com",
            "password": "techpassword123",
        })
        tech_token = tech_response.json()["access_token"]
        tech_headers = {"Authorization": f"Bearer {tech_token}"}

        # Start work and resolve
        client.post(f"/tickets/{ticket_id}/start-work", headers=tech_headers)
        resolve_response = client.post(f"/tickets/{ticket_id}/resolve", json={
            "resolution_summary": "Fixed the issue"
        }, headers=tech_headers)
        assert resolve_response.status_code == 200

        # Check SLA - resolution should be met
        sla_response = client.get(f"/sla/tickets/{ticket_id}", headers=auth_headers)
        sla_data = sla_response.json()
        assert sla_data["resolution_status"] == "RESOLUTION_MET"
        assert sla_data["resolution_breached"] is False

    def test_existing_response_breach_no_duplicate(self, client, auth_headers, admin_auth_headers, db_session):
        """Test that running breach check twice creates only one history event."""
        from app.services.sla_service import create_sla_policy
        from app.services.sla_breach_service import check_all_sla_breaches
        from app.models.ticket_comment import TicketHistory, HistoryEventType

        policy = create_sla_policy(
            db=db_session,
            name="Test Duplicate Breach",
            priority="High",
            response_time_minutes=1,  # 1 minute - will be breached almost immediately
            resolution_time_minutes=240,
        )

        response = client.post("/tickets/", json={
            "title": "SLA Test - Duplicate Breach",
            "description": "Test ticket for duplicate breach check",
            "priority": "High",
        }, headers=auth_headers)
        assert response.status_code == 200
        ticket_id = response.json()["id"]

        # Manually set deadline to past to simulate breach
        from datetime import datetime, timezone, timedelta
        from app.models.ticket import Ticket
        ticket = db_session.query(Ticket).filter(Ticket.id == ticket_id).first()
        ticket.sla_response_deadline = datetime.now(timezone.utc) - timedelta(minutes=5)
        db_session.commit()

        # Run breach check first time
        result1 = check_all_sla_breaches(db_session)
        assert result1["response_breaches_processed"] == 1

        # Run breach check second time
        result2 = check_all_sla_breaches(db_session)
        assert result2["response_breaches_processed"] == 0

        # Verify only one history event
        history_count = db_session.query(TicketHistory).filter(
            TicketHistory.ticket_id == ticket_id,
            TicketHistory.event_type == HistoryEventType.SLA_RESPONSE_BREACHED,
        ).count()
        assert history_count == 1

    def test_existing_resolution_breach_no_duplicate(self, client, auth_headers, admin_auth_headers, db_session):
        """Test that running resolution breach check twice creates only one history event."""
        from app.services.sla_service import create_sla_policy
        from app.services.sla_breach_service import check_all_sla_breaches
        from app.models.ticket_comment import TicketHistory, HistoryEventType

        policy = create_sla_policy(
            db=db_session,
            name="Test Duplicate Resolution Breach",
            priority="Critical",
            response_time_minutes=30,
            resolution_time_minutes=1,
        )

        response = client.post("/tickets/", json={
            "title": "SLA Test - Duplicate Resolution Breach",
            "description": "Test ticket for duplicate breach check",
            "priority": "Critical",
        }, headers=auth_headers)
        assert response.status_code == 200
        ticket_id = response.json()["id"]

        # Manually set resolution deadline to past
        from datetime import datetime, timezone, timedelta
        from app.models.ticket import Ticket
        ticket = db_session.query(Ticket).filter(Ticket.id == ticket_id).first()
        ticket.sla_resolution_deadline = datetime.now(timezone.utc) - timedelta(minutes=5)
        db_session.commit()

        # Run breach check first time
        result1 = check_all_sla_breaches(db_session)
        assert result1["resolution_breaches_processed"] == 1

        # Run breach check second time
        result2 = check_all_sla_breaches(db_session)
        assert result2["resolution_breaches_processed"] == 0

        # Verify only one history event
        history_count = db_session.query(TicketHistory).filter(
            TicketHistory.ticket_id == ticket_id,
            TicketHistory.event_type == HistoryEventType.SLA_RESOLUTION_BREACHED,
        ).count()
        assert history_count == 1

    def test_multiple_candidates_processed(self, client, auth_headers, admin_auth_headers, db_session):
        """Test that multiple candidate tickets are processed correctly."""
        from app.services.sla_service import create_sla_policy
        from app.services.sla_breach_service import check_all_sla_breaches

        policy = create_sla_policy(
            db=db_session,
            name="Test Multiple Breaches",
            priority="High",
            response_time_minutes=1,
            resolution_time_minutes=240,
        )

        # Create 3 tickets with past response deadlines
        ticket_ids = []
        for i in range(3):
            response = client.post("/tickets/", json={
                "title": f"Multi Breach Test {i}",
                "description": f"Test ticket {i}",
                "priority": "High",
            }, headers=auth_headers)
            assert response.status_code == 200
            ticket_ids.append(response.json()["id"])

        # Set deadlines to past
        from datetime import datetime, timezone, timedelta
        from app.models.ticket import Ticket
        for tid in ticket_ids:
            ticket = db_session.query(Ticket).filter(Ticket.id == tid).first()
            ticket.sla_response_deadline = datetime.now(timezone.utc) - timedelta(minutes=5)
        db_session.commit()

        result = check_all_sla_breaches(db_session)
        assert result["response_candidates"] == 3
        assert result["response_breaches_processed"] == 3

    def test_resolved_ticket_excluded_from_response_breach(self, client, auth_headers, admin_auth_headers, db_session, technician_user):
        """Test that resolved tickets are excluded from response breach detection."""
        from app.services.sla_service import create_sla_policy
        from app.services.sla_breach_service import check_all_sla_breaches

        policy = create_sla_policy(
            db=db_session,
            name="Test Resolved Exclusion",
            priority="High",
            response_time_minutes=1,
            resolution_time_minutes=240,
        )

        response = client.post("/tickets/", json={
            "title": "SLA Test - Resolved Exclusion",
            "description": "Test ticket",
            "priority": "High",
        }, headers=auth_headers)
        assert response.status_code == 200
        ticket_id = response.json()["id"]

        # Assign ticket to technician
        admin_response = client.post("/auth/login", json={
            "email": "admin@example.com",
            "password": "adminpassword123",
        })
        admin_token = admin_response.json()["access_token"]
        admin_headers = {"Authorization": f"Bearer {admin_token}"}
        
        assign_response = client.put(f"/tickets/{ticket_id}/assign", json={
            "assigned_to": technician_user.id
        }, headers=admin_headers)
        assert assign_response.status_code == 200

        tech_response = client.post("/auth/login", json={
            "email": "tech@example.com",
            "password": "techpassword123",
        })
        tech_token = tech_response.json()["access_token"]
        tech_headers = {"Authorization": f"Bearer {tech_token}"}

        # Resolve the ticket
        client.post(f"/tickets/{ticket_id}/start-work", headers=tech_headers)
        client.post(f"/tickets/{ticket_id}/resolve", json={
            "resolution_summary": "Fixed"
        }, headers=tech_headers)

        # Set deadline to past
        from datetime import datetime, timezone, timedelta
        from app.models.ticket import Ticket
        ticket = db_session.query(Ticket).filter(Ticket.id == ticket_id).first()
        ticket.sla_response_deadline = datetime.now(timezone.utc) - timedelta(minutes=5)
        db_session.commit()

        result = check_all_sla_breaches(db_session)
        # Should not process breach for resolved ticket
        assert result["response_breaches_processed"] == 0

    def test_closed_ticket_excluded_from_resolution_breach(self, client, auth_headers, admin_auth_headers, db_session, technician_user):
        """Test that closed tickets are excluded from resolution breach detection."""
        from app.services.sla_service import create_sla_policy
        from app.services.sla_breach_service import check_all_sla_breaches

        policy = create_sla_policy(
            db=db_session,
            name="Test Closed Exclusion",
            priority="Critical",
            response_time_minutes=30,
            resolution_time_minutes=1,
        )

        response = client.post("/tickets/", json={
            "title": "SLA Test - Closed Exclusion",
            "description": "Test ticket",
            "priority": "Critical",
        }, headers=auth_headers)
        assert response.status_code == 200
        ticket_id = response.json()["id"]

        # Assign ticket to technician
        admin_response = client.post("/auth/login", json={
            "email": "admin@example.com",
            "password": "adminpassword123",
        })
        admin_token = admin_response.json()["access_token"]
        admin_headers = {"Authorization": f"Bearer {admin_token}"}
        
        assign_response = client.put(f"/tickets/{ticket_id}/assign", json={
            "assigned_to": technician_user.id
        }, headers=admin_headers)
        assert assign_response.status_code == 200

        tech_response = client.post("/auth/login", json={
            "email": "tech@example.com",
            "password": "techpassword123",
        })
        tech_token = tech_response.json()["access_token"]
        tech_headers = {"Authorization": f"Bearer {tech_token}"}

        # Resolve and close the ticket
        client.post(f"/tickets/{ticket_id}/start-work", headers=tech_headers)
        client.post(f"/tickets/{ticket_id}/resolve", json={
            "resolution_summary": "Fixed"
        }, headers=tech_headers)
        client.post(f"/tickets/{ticket_id}/close", headers=tech_headers)

        # Set deadline to past
        from datetime import datetime, timezone, timedelta
        from app.models.ticket import Ticket
        ticket = db_session.query(Ticket).filter(Ticket.id == ticket_id).first()
        ticket.sla_resolution_deadline = datetime.now(timezone.utc) - timedelta(minutes=5)
        db_session.commit()

        result = check_all_sla_breaches(db_session)
        # Should not process breach for closed ticket
        assert result["resolution_breaches_processed"] == 0