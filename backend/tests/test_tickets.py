import pytest
from fastapi.testclient import TestClient


class TestTicketCreation:
    def test_create_ticket_success(self, client, auth_headers, test_user):
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
        assert data["created_by"] == test_user.id
        assert "id" in data

    def test_create_ticket_unauthorized(self, client):
        response = client.post("/tickets/", json={
            "title": "Test Ticket",
            "description": "This is a test ticket",
            "priority": "Medium",
        })
        assert response.status_code == 401

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
    def test_create_comment_success(self, client, auth_headers, test_user):
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
        assert data["author_id"] == test_user.id

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
    def _create_ticket(self, client, headers, title="Attachment Test"):
        response = client.post("/tickets/", json={
            "title": title,
            "description": "Description",
            "priority": "Medium",
        }, headers=headers)
        assert response.status_code == 200
        return response.json()["id"]

    # ------------------------------------------------------------------
    # Upload
    # ------------------------------------------------------------------
    def test_upload_attachment_success(self, client, auth_headers, isolate_upload_dir):
        ticket_id = self._create_ticket(client, auth_headers)

        files = {"file": ("test.txt", b"Hello World", "text/plain")}
        response = client.post(f"/tickets/{ticket_id}/attachments", files=files, headers=auth_headers)

        assert response.status_code == 201
        data = response.json()
        assert data["original_filename"] == "test.txt"
        assert data["content_type"] == "text/plain"
        assert data["file_size"] == 11
        assert data["ticket_id"] == ticket_id
        # Stored filename must never be exposed to clients.
        assert "stored_filename" not in data
        # A physical file was written to the isolated upload dir.
        assert len(list(isolate_upload_dir.iterdir())) == 1

    def test_upload_attachment_unauthorized(self, client, auth_headers, tech_auth_headers):
        ticket_id = self._create_ticket(client, tech_auth_headers)

        # Employee tries to upload to technician's ticket
        files = {"file": ("test.txt", b"Hello", "text/plain")}
        response = client.post(f"/tickets/{ticket_id}/attachments", files=files, headers=auth_headers)
        assert response.status_code == 403

    def test_upload_to_nonexistent_ticket(self, client, auth_headers):
        files = {"file": ("test.txt", b"Hello", "text/plain")}
        response = client.post("/tickets/999999/attachments", files=files, headers=auth_headers)
        assert response.status_code == 404

    def test_upload_invalid_file_type(self, client, auth_headers):
        ticket_id = self._create_ticket(client, auth_headers, "Invalid Type Test")

        # Executable content type is not in the allow-list
        files = {"file": ("test.exe", b"MZ...", "application/x-msdownload")}
        response = client.post(f"/tickets/{ticket_id}/attachments", files=files, headers=auth_headers)
        assert response.status_code == 415

    def test_upload_unsupported_extension(self, client, auth_headers):
        ticket_id = self._create_ticket(client, auth_headers, "Unsupported Extension Test")

        # Extension is not allow-listed even though the content type is
        files = {"file": ("script.sh", b"echo hi", "text/plain")}
        response = client.post(f"/tickets/{ticket_id}/attachments", files=files, headers=auth_headers)
        assert response.status_code == 415

    def test_upload_extension_content_type_mismatch(self, client, auth_headers):
        ticket_id = self._create_ticket(client, auth_headers, "Mismatch Test")

        # Declares a .txt extension but claims to be a PNG
        files = {"file": ("photo.txt", b"not really an image", "image/png")}
        response = client.post(f"/tickets/{ticket_id}/attachments", files=files, headers=auth_headers)
        assert response.status_code == 415

    def test_upload_svg_rejected(self, client, auth_headers):
        ticket_id = self._create_ticket(client, auth_headers, "SVG Test")

        files = {"file": ("logo.svg", b"<svg></svg>", "image/svg+xml")}
        response = client.post(f"/tickets/{ticket_id}/attachments", files=files, headers=auth_headers)
        assert response.status_code == 415

    def test_upload_empty_file(self, client, auth_headers):
        ticket_id = self._create_ticket(client, auth_headers, "Empty File Test")

        files = {"file": ("empty.txt", b"", "text/plain")}
        response = client.post(f"/tickets/{ticket_id}/attachments", files=files, headers=auth_headers)
        assert response.status_code == 400

    def test_upload_oversized_file(self, client, auth_headers):
        from app.config import settings

        ticket_id = self._create_ticket(client, auth_headers, "Oversized Test")

        oversized = b"0" * (settings.max_upload_size_mb * 1024 * 1024 + 1)
        files = {"file": ("big.txt", oversized, "text/plain")}
        response = client.post(f"/tickets/{ticket_id}/attachments", files=files, headers=auth_headers)
        assert response.status_code == 413

    # ------------------------------------------------------------------
    # List
    # ------------------------------------------------------------------
    def test_list_attachments_success(self, client, auth_headers):
        ticket_id = self._create_ticket(client, auth_headers, "List Test")

        client.post(
            f"/tickets/{ticket_id}/attachments",
            files={"file": ("a.txt", b"aaa", "text/plain")},
            headers=auth_headers,
        )
        client.post(
            f"/tickets/{ticket_id}/attachments",
            files={"file": ("b.txt", b"bbb", "text/plain")},
            headers=auth_headers,
        )

        response = client.get(f"/tickets/{ticket_id}/attachments", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 2
        assert len(data["items"]) == 2
        for item in data["items"]:
            assert "stored_filename" not in item

    def test_list_attachments_unauthorized(self, client, auth_headers, tech_auth_headers):
        ticket_id = self._create_ticket(client, tech_auth_headers, "List Unauthorized Test")
        client.post(
            f"/tickets/{ticket_id}/attachments",
            files={"file": ("a.txt", b"aaa", "text/plain")},
            headers=tech_auth_headers,
        )

        response = client.get(f"/tickets/{ticket_id}/attachments", headers=auth_headers)
        assert response.status_code == 403

    # ------------------------------------------------------------------
    # Get / Download
    # ------------------------------------------------------------------
    def test_download_attachment(self, client, auth_headers):
        ticket_id = self._create_ticket(client, auth_headers, "Download Test")

        upload_response = client.post(
            f"/tickets/{ticket_id}/attachments",
            files={"file": ("test.txt", b"Hello World", "text/plain")},
            headers=auth_headers,
        )
        attachment_id = upload_response.json()["id"]

        response = client.get(
            f"/tickets/{ticket_id}/attachments/{attachment_id}/download",
            headers=auth_headers,
        )
        assert response.status_code == 200
        assert response.headers["content-type"].startswith("text/plain")
        assert response.content == b"Hello World"

    def test_get_attachment_mismatched_ticket_id(self, client, auth_headers):
        ticket_a = self._create_ticket(client, auth_headers, "Ticket A")
        ticket_b = self._create_ticket(client, auth_headers, "Ticket B")

        upload_response = client.post(
            f"/tickets/{ticket_a}/attachments",
            files={"file": ("test.txt", b"Hello", "text/plain")},
            headers=auth_headers,
        )
        attachment_id = upload_response.json()["id"]

        response = client.get(
            f"/tickets/{ticket_b}/attachments/{attachment_id}",
            headers=auth_headers,
        )
        assert response.status_code == 404

    def test_download_mismatched_ticket_id(self, client, auth_headers):
        ticket_a = self._create_ticket(client, auth_headers, "Ticket A")
        ticket_b = self._create_ticket(client, auth_headers, "Ticket B")

        upload_response = client.post(
            f"/tickets/{ticket_a}/attachments",
            files={"file": ("test.txt", b"Hello", "text/plain")},
            headers=auth_headers,
        )
        attachment_id = upload_response.json()["id"]

        response = client.get(
            f"/tickets/{ticket_b}/attachments/{attachment_id}/download",
            headers=auth_headers,
        )
        assert response.status_code == 404

    def test_download_attachment_unauthorized(self, client, auth_headers, tech_auth_headers):
        ticket_id = self._create_ticket(client, tech_auth_headers, "Download Unauthorized Test")

        upload_response = client.post(
            f"/tickets/{ticket_id}/attachments",
            files={"file": ("test.txt", b"Hello", "text/plain")},
            headers=tech_auth_headers,
        )
        attachment_id = upload_response.json()["id"]

        response = client.get(
            f"/tickets/{ticket_id}/attachments/{attachment_id}/download",
            headers=auth_headers,
        )
        assert response.status_code == 404

    def test_download_missing_physical_file(self, client, auth_headers, isolate_upload_dir):
        ticket_id = self._create_ticket(client, auth_headers, "Missing File Test")

        upload_response = client.post(
            f"/tickets/{ticket_id}/attachments",
            files={"file": ("test.txt", b"Hello", "text/plain")},
            headers=auth_headers,
        )
        attachment_id = upload_response.json()["id"]

        # Simulate a file that vanished from disk
        for stored_file in isolate_upload_dir.iterdir():
            stored_file.unlink()

        response = client.get(
            f"/tickets/{ticket_id}/attachments/{attachment_id}/download",
            headers=auth_headers,
        )
        assert response.status_code == 404

    # ------------------------------------------------------------------
    # Delete
    # ------------------------------------------------------------------
    def test_delete_attachment(self, client, auth_headers):
        ticket_id = self._create_ticket(client, auth_headers, "Delete Attachment Test")

        upload_response = client.post(
            f"/tickets/{ticket_id}/attachments",
            files={"file": ("test.txt", b"Hello", "text/plain")},
            headers=auth_headers,
        )
        attachment_id = upload_response.json()["id"]

        response = client.delete(
            f"/tickets/{ticket_id}/attachments/{attachment_id}",
            headers=auth_headers,
        )
        assert response.status_code == 200
        assert response.json()["message"] == "Attachment deleted successfully"

        # Soft-deleted attachment is no longer downloadable
        download_response = client.get(
            f"/tickets/{ticket_id}/attachments/{attachment_id}/download",
            headers=auth_headers,
        )
        assert download_response.status_code == 404

    def test_delete_mismatched_ticket_id(self, client, auth_headers):
        ticket_a = self._create_ticket(client, auth_headers, "Ticket A")
        ticket_b = self._create_ticket(client, auth_headers, "Ticket B")

        upload_response = client.post(
            f"/tickets/{ticket_a}/attachments",
            files={"file": ("test.txt", b"Hello", "text/plain")},
            headers=auth_headers,
        )
        attachment_id = upload_response.json()["id"]

        response = client.delete(
            f"/tickets/{ticket_b}/attachments/{attachment_id}",
            headers=auth_headers,
        )
        assert response.status_code == 404

        # Original attachment is untouched
        assert client.get(
            f"/tickets/{ticket_a}/attachments/{attachment_id}",
            headers=auth_headers,
        ).status_code == 200

    def test_delete_attachment_non_uploader_denied(self, client, auth_headers, admin_auth_headers):
        # Employee creates the ticket, Admin uploads, Employee cannot delete.
        ticket_id = self._create_ticket(client, auth_headers, "Non Uploader Delete Test")

        upload_response = client.post(
            f"/tickets/{ticket_id}/attachments",
            files={"file": ("admin.txt", b"Hello", "text/plain")},
            headers=admin_auth_headers,
        )
        attachment_id = upload_response.json()["id"]

        response = client.delete(
            f"/tickets/{ticket_id}/attachments/{attachment_id}",
            headers=auth_headers,
        )
        assert response.status_code == 403

    def test_deleted_attachment_excluded_from_listing(self, client, auth_headers):
        ticket_id = self._create_ticket(client, auth_headers, "Listing Exclusion Test")

        first = client.post(
            f"/tickets/{ticket_id}/attachments",
            files={"file": ("keep.txt", b"keep", "text/plain")},
            headers=auth_headers,
        ).json()
        second = client.post(
            f"/tickets/{ticket_id}/attachments",
            files={"file": ("remove.txt", b"remove", "text/plain")},
            headers=auth_headers,
        ).json()

        client.delete(
            f"/tickets/{ticket_id}/attachments/{second['id']}",
            headers=auth_headers,
        )

        response = client.get(f"/tickets/{ticket_id}/attachments", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert [item["id"] for item in data["items"]] == [first["id"]]

    def test_delete_removes_physical_file(self, client, auth_headers, isolate_upload_dir):
        ticket_id = self._create_ticket(client, auth_headers, "Physical Removal Test")

        attachment_id = client.post(
            f"/tickets/{ticket_id}/attachments",
            files={"file": ("test.txt", b"Hello", "text/plain")},
            headers=auth_headers,
        ).json()["id"]

        assert len(list(isolate_upload_dir.iterdir())) == 1

        response = client.delete(
            f"/tickets/{ticket_id}/attachments/{attachment_id}",
            headers=auth_headers,
        )
        assert response.status_code == 200
        assert list(isolate_upload_dir.iterdir()) == []

    def test_delete_attachment_missing_file_is_safe(self, client, auth_headers, isolate_upload_dir):
        ticket_id = self._create_ticket(client, auth_headers, "Delete Missing File Test")

        attachment_id = client.post(
            f"/tickets/{ticket_id}/attachments",
            files={"file": ("test.txt", b"Hello", "text/plain")},
            headers=auth_headers,
        ).json()["id"]

        # Remove the file first so the delete handler hits an already-missing file.
        for stored_file in isolate_upload_dir.iterdir():
            stored_file.unlink()

        response = client.delete(
            f"/tickets/{ticket_id}/attachments/{attachment_id}",
            headers=auth_headers,
        )
        assert response.status_code == 200
        assert response.json()["message"] == "Attachment deleted successfully"


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


class TestTicketWorkflowHistoryPersistence:
    """Regression tests for ticket workflow audit integrity (Milestone 4C).

    Every workflow operation must persist the ticket state change together with
    the corresponding ``TicketHistory`` events in the same transaction, so the
    event cannot be lost when no unrelated downstream service commits later.
    The assertions below read the events back through the history/timeline
    endpoints (i.e. from persisted rows), not from in-memory objects.
    """

    def _create_ticket(self, client, headers, title="Workflow History Ticket"):
        response = client.post("/tickets/", json={
            "title": title,
            "description": "Description",
            "priority": "Medium",
        }, headers=headers)
        assert response.status_code == 200
        return response.json()["id"]

    def _history(self, client, ticket_id, headers):
        response = client.get(
            f"/tickets/{ticket_id}/history?page=1&page_size=100",
            headers=headers,
        )
        assert response.status_code == 200
        return response.json()["items"]

    def _events(self, client, ticket_id, headers, event_type):
        return [
            item for item in self._history(client, ticket_id, headers)
            if item["event_type"] == event_type
        ]

    def _timeline_events(self, client, ticket_id, headers, event_type):
        response = client.get(
            f"/tickets/{ticket_id}/timeline?page=1&page_size=200",
            headers=headers,
        )
        assert response.status_code == 200
        return [
            item for item in response.json()["items"]
            if item.get("event_type") == event_type
        ]

    # ------------------------------------------------------------------
    # Assignment
    # ------------------------------------------------------------------
    def test_assign_persists_assigned_and_status_change(
        self, client, auth_headers, admin_auth_headers, technician_user, db_session
    ):
        ticket_id = self._create_ticket(client, auth_headers)

        response = client.put(f"/tickets/{ticket_id}/assign", json={
            "assigned_to": technician_user.id,
        }, headers=admin_auth_headers)
        assert response.status_code == 200
        assert response.json()["status"] == "Assigned"
        assert response.json()["assigned_to"] == technician_user.id

        # Exactly one ASSIGNED event with the correct transition values.
        assigned = self._events(client, ticket_id, admin_auth_headers, "ASSIGNED")
        assert len(assigned) == 1
        assert assigned[0]["old_value"] == "Unassigned"
        assert assigned[0]["new_value"] == str(technician_user.id)

        # The dead STATUS_CHANGED branch is now a real, single Open -> Assigned event.
        transitions = self._events(client, ticket_id, admin_auth_headers, "STATUS_CHANGED")
        assert len(transitions) == 1
        assert transitions[0]["old_value"] == "Open"
        assert transitions[0]["new_value"] == "Assigned"

        # The event is also visible on the timeline.
        timeline_assigned = self._timeline_events(
            client, ticket_id, admin_auth_headers, "ASSIGNED"
        )
        assert len(timeline_assigned) == 1
        assert timeline_assigned[0]["new_value"] == str(technician_user.id)

        # And the rows are genuinely persisted in the database.
        from app.models.ticket_comment import TicketHistory, HistoryEventType
        persisted = db_session.query(TicketHistory).filter(
            TicketHistory.ticket_id == ticket_id,
        ).all()
        assert sum(
            1 for e in persisted if e.event_type == HistoryEventType.ASSIGNED
        ) == 1
        assert sum(
            1 for e in persisted if e.event_type == HistoryEventType.STATUS_CHANGED
        ) == 1

    def test_reassign_persists_previous_and_new_assignee(
        self, client, auth_headers, admin_auth_headers, technician_user, db_session
    ):
        from uuid import uuid4

        from app.models.user import User
        from app.utils.security import hash_password

        second_tech = User(
            name="Second Tech",
            email=f"reassign-target-{uuid4().hex}@example.com",
            password=hash_password("techpassword123"),
            role="Technician",
        )
        db_session.add(second_tech)
        db_session.commit()
        db_session.refresh(second_tech)

        ticket_id = self._create_ticket(client, auth_headers)
        client.put(f"/tickets/{ticket_id}/assign", json={
            "assigned_to": technician_user.id,
        }, headers=admin_auth_headers)

        response = client.put(f"/tickets/{ticket_id}/reassign", json={
            "assigned_to": second_tech.id,
        }, headers=admin_auth_headers)
        assert response.status_code == 200
        assert response.json()["assigned_to"] == second_tech.id

        reassigned = self._events(client, ticket_id, admin_auth_headers, "REASSIGNED")
        assert len(reassigned) == 1
        assert reassigned[0]["old_value"] == str(technician_user.id)
        assert reassigned[0]["new_value"] == str(second_tech.id)

    def test_unassign_persists_unassigned_and_status_transition(
        self, client, auth_headers, admin_auth_headers, technician_user
    ):
        ticket_id = self._create_ticket(client, auth_headers)
        client.put(f"/tickets/{ticket_id}/assign", json={
            "assigned_to": technician_user.id,
        }, headers=admin_auth_headers)

        response = client.post(
            f"/tickets/{ticket_id}/unassign", json={}, headers=admin_auth_headers
        )
        assert response.status_code == 200
        assert response.json()["status"] == "Open"
        assert response.json()["assigned_to"] is None

        unassigned = self._events(client, ticket_id, admin_auth_headers, "UNASSIGNED")
        assert len(unassigned) == 1
        assert unassigned[0]["old_value"] == str(technician_user.id)
        assert unassigned[0]["new_value"] == "Unassigned"

        # The status transition must reflect the real prior status, not compare
        # the already-mutated value against itself.
        transitions = [
            e for e in self._events(client, ticket_id, admin_auth_headers, "STATUS_CHANGED")
            if e["old_value"] == "Assigned"
        ]
        assert len(transitions) == 1
        assert transitions[0]["new_value"] == "Open"

    # ------------------------------------------------------------------
    # Status transitions
    # ------------------------------------------------------------------
    def _assigned_ticket(self, client, auth_headers, admin_auth_headers, technician_user):
        ticket_id = self._create_ticket(client, auth_headers)
        assign = client.put(f"/tickets/{ticket_id}/assign", json={
            "assigned_to": technician_user.id,
        }, headers=admin_auth_headers)
        assert assign.status_code == 200
        return ticket_id

    def test_start_work_persists_status_change(
        self, client, auth_headers, admin_auth_headers, tech_auth_headers, technician_user
    ):
        ticket_id = self._assigned_ticket(
            client, auth_headers, admin_auth_headers, technician_user
        )

        response = client.post(
            f"/tickets/{ticket_id}/start-work", headers=tech_auth_headers
        )
        assert response.status_code == 200
        assert response.json()["status"] == "In Progress"

        transitions = self._events(client, ticket_id, admin_auth_headers, "STATUS_CHANGED")
        assert any(
            e["old_value"] == "Assigned" and e["new_value"] == "In Progress"
            for e in transitions
        )

    def test_mark_pending_persists_status_change(
        self, client, auth_headers, admin_auth_headers, tech_auth_headers, technician_user
    ):
        ticket_id = self._assigned_ticket(
            client, auth_headers, admin_auth_headers, technician_user
        )
        client.post(f"/tickets/{ticket_id}/start-work", headers=tech_auth_headers)

        response = client.post(
            f"/tickets/{ticket_id}/mark-pending",
            json={"reason": "Waiting for customer response"},
            headers=tech_auth_headers
        )
        assert response.status_code == 200
        assert response.json()["status"] == "Pending"

        transitions = self._events(client, ticket_id, admin_auth_headers, "STATUS_CHANGED")
        assert any(
            e["old_value"] == "In Progress" and e["new_value"] == "Pending"
            for e in transitions
        )

    def test_resolve_persists_status_and_resolution_history(
        self, client, auth_headers, admin_auth_headers, tech_auth_headers, technician_user
    ):
        ticket_id = self._assigned_ticket(
            client, auth_headers, admin_auth_headers, technician_user
        )
        client.post(f"/tickets/{ticket_id}/start-work", headers=tech_auth_headers)

        response = client.post(f"/tickets/{ticket_id}/resolve", json={
            "resolution_summary": "Fixed the leak",
        }, headers=tech_auth_headers)
        assert response.status_code == 200
        assert response.json()["status"] == "Resolved"

        transitions = self._events(client, ticket_id, admin_auth_headers, "STATUS_CHANGED")
        assert any(
            e["old_value"] == "In Progress" and e["new_value"] == "Resolved"
            for e in transitions
        )

        resolved = self._events(client, ticket_id, admin_auth_headers, "TICKET_RESOLVED")
        assert len(resolved) == 1
        assert resolved[0]["new_value"] == "Resolved: Fixed the leak"

        timeline_resolved = self._timeline_events(
            client, ticket_id, admin_auth_headers, "TICKET_RESOLVED"
        )
        assert len(timeline_resolved) == 1

    def test_reopen_persists_history(
        self, client, auth_headers, admin_auth_headers, tech_auth_headers, technician_user
    ):
        ticket_id = self._assigned_ticket(
            client, auth_headers, admin_auth_headers, technician_user
        )
        client.post(f"/tickets/{ticket_id}/start-work", headers=tech_auth_headers)
        client.post(f"/tickets/{ticket_id}/resolve", json={
            "resolution_summary": "Fixed",
        }, headers=tech_auth_headers)

        response = client.post(f"/tickets/{ticket_id}/reopen", json={
            "reason": "Issue returned",
        }, headers=admin_auth_headers)
        assert response.status_code == 200
        assert response.json()["status"] == "Open"

        reopened = self._events(client, ticket_id, admin_auth_headers, "TICKET_REOPENED")
        assert len(reopened) == 1
        assert reopened[0]["new_value"] == "Reopened: Issue returned"

        transitions = [
            e for e in self._events(client, ticket_id, admin_auth_headers, "STATUS_CHANGED")
            if e["old_value"] == "Resolved"
        ]
        assert len(transitions) == 1
        assert transitions[0]["new_value"] == "Open"

    def test_close_persists_history(
        self, client, auth_headers, admin_auth_headers, tech_auth_headers, technician_user
    ):
        ticket_id = self._assigned_ticket(
            client, auth_headers, admin_auth_headers, technician_user
        )
        client.post(f"/tickets/{ticket_id}/start-work", headers=tech_auth_headers)
        client.post(f"/tickets/{ticket_id}/resolve", json={
            "resolution_summary": "Fixed",
        }, headers=tech_auth_headers)

        response = client.post(
            f"/tickets/{ticket_id}/close", json={}, headers=tech_auth_headers
        )
        assert response.status_code == 200
        assert response.json()["status"] == "Closed"

        closed = self._events(client, ticket_id, admin_auth_headers, "TICKET_CLOSED")
        assert len(closed) == 1
        assert closed[0]["new_value"] == "Ticket closed"

        transitions = [
            e for e in self._events(client, ticket_id, admin_auth_headers, "STATUS_CHANGED")
            if e["old_value"] == "Resolved"
        ]
        assert len(transitions) == 1
        assert transitions[0]["new_value"] == "Closed"

    # ------------------------------------------------------------------
    # Legacy status update
    # ------------------------------------------------------------------
    def test_legacy_status_update_persists_history(
        self, client, auth_headers, admin_auth_headers
    ):
        ticket_id = self._create_ticket(client, auth_headers)

        response = client.patch(f"/tickets/{ticket_id}/status", json={
            "status": "Assigned",
        }, headers=admin_auth_headers)
        assert response.status_code == 200
        assert response.json()["status"] == "Assigned"

        transitions = self._events(client, ticket_id, admin_auth_headers, "STATUS_CHANGED")
        assert len(transitions) == 1
        assert transitions[0]["old_value"] == "Open"
        assert transitions[0]["new_value"] == "Assigned"

    # ------------------------------------------------------------------
    # Escalation
    # ------------------------------------------------------------------
    def test_escalation_history_persists_when_notifications_disabled(
        self, client, auth_headers, admin_auth_headers, technician_user, db_session
    ):
        from app.services.preferences_service import update_preferences

        # Disable the escalation target's in-app notifications. Notification
        # creation will early-return, so the history event must be persisted by
        # the escalation operation itself.
        update_preferences(
            db_session,
            technician_user.id,
            {"in_app_notifications_enabled": False},
        )

        ticket_id = self._create_ticket(client, auth_headers)

        response = client.post(f"/tickets/{ticket_id}/escalate", json={
            "escalated_to": technician_user.id,
            "escalation_reason": "Needs senior attention",
        }, headers=admin_auth_headers)
        assert response.status_code == 200

        escalated = self._events(client, ticket_id, admin_auth_headers, "ESCALATED")
        assert len(escalated) == 1
        assert escalated[0]["new_value"] == (
            f"Escalated to {technician_user.name}: Needs senior attention"
        )