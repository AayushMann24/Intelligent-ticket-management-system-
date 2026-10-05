import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.notification import Notification, NotificationType
from app.models.user import User
from app.models.ticket import Ticket
from app.services.notification_service import (
    create_notification,
    get_notifications_for_user,
    get_unread_count,
    mark_notification_as_read,
    mark_all_notifications_as_read,
)
from app.utils.security import hash_password


class TestNotificationModel:
    """Tests for Notification model."""

    def test_notification_creation(self, db_session):
        """Test creating a notification directly via model."""
        # Create a test user
        user = User(
            name="Test User",
            email="notify_test@example.com",
            password=hash_password("password123"),
            role="Employee",
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        # Create notification
        notification = Notification(
            recipient_id=user.id,
            notification_type=NotificationType.TICKET_ASSIGNED,
            title="Test Notification",
            message="This is a test notification",
            ticket_id=None,
        )
        db_session.add(notification)
        db_session.commit()
        db_session.refresh(notification)

        assert notification.id is not None
        assert notification.recipient_id == user.id
        assert notification.notification_type == NotificationType.TICKET_ASSIGNED
        assert notification.title == "Test Notification"
        assert notification.message == "This is a test notification"
        assert notification.is_read is False
        assert notification.read_at is None
        assert notification.created_at is not None

    def test_notification_enum_values(self):
        """Test that all expected notification types exist."""
        expected_types = [
            "TICKET_ASSIGNED",
            "TICKET_REASSIGNED",
            "SLA_RESPONSE_WARNING",
            "SLA_RESPONSE_BREACHED",
            "SLA_RESOLUTION_WARNING",
            "SLA_RESOLUTION_BREACHED",
            "TICKET_ESCALATED",
            "SYSTEM",
        ]
        for expected in expected_types:
            assert hasattr(NotificationType, expected)
            assert getattr(NotificationType, expected).value == expected

    def test_notification_with_ticket(self, db_session):
        """Test notification linked to a ticket."""
        # Create users
        user1 = User(
            name="User 1",
            email="user1_notify@example.com",
            password=hash_password("password123"),
            role="Employee",
        )
        user2 = User(
            name="User 2",
            email="user2_notify@example.com",
            password=hash_password("password123"),
            role="Technician",
        )
        db_session.add_all([user1, user2])
        db_session.commit()
        db_session.refresh(user1)
        db_session.refresh(user2)

        # Create ticket
        ticket = Ticket(
            title="Test Ticket",
            description="Test description",
            priority="Medium",
            status="Open",
            created_by=user1.id,
        )
        db_session.add(ticket)
        db_session.commit()
        db_session.refresh(ticket)

        # Create notification linked to ticket
        notification = Notification(
            recipient_id=user2.id,
            notification_type=NotificationType.TICKET_ASSIGNED,
            title="Ticket Assigned",
            message=f"Ticket #{ticket.id} assigned to you",
            ticket_id=ticket.id,
        )
        db_session.add(notification)
        db_session.commit()
        db_session.refresh(notification)

        assert notification.ticket_id == ticket.id
        assert notification.ticket is not None
        assert notification.ticket.id == ticket.id


class TestNotificationService:
    """Tests for NotificationService."""

    def test_create_notification_success(self, db_session):
        """Test creating a notification via service."""
        user = User(
            name="Service Test User",
            email="service_test@example.com",
            password=hash_password("password123"),
            role="Employee",
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        notification = create_notification(
            db=db_session,
            recipient_id=user.id,
            notification_type=NotificationType.TICKET_ASSIGNED,
            title="Test Title",
            message="Test message",
            ticket_id=None,
        )

        assert notification.id is not None
        assert notification.title == "Test Title"
        assert notification.message == "Test message"
        assert notification.is_read is False

    def test_create_notification_invalid_recipient(self, db_session):
        """Test creating notification for non-existent user raises error."""
        from fastapi import HTTPException

        with pytest.raises(HTTPException) as exc_info:
            create_notification(
                db=db_session,
                recipient_id=99999,
                notification_type=NotificationType.TICKET_ASSIGNED,
                title="Test",
                message="Test",
            )
        assert exc_info.value.status_code == 404

    def test_get_notifications_for_user(self, db_session):
        """Test retrieving notifications for a user."""
        user = User(
            name="List Test User",
            email="list_test@example.com",
            password=hash_password("password123"),
            role="Employee",
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        # Create multiple notifications
        for i in range(5):
            create_notification(
                db=db_session,
                recipient_id=user.id,
                notification_type=NotificationType.TICKET_ASSIGNED,
                title=f"Notification {i}",
                message=f"Message {i}",
            )

        # Create notification for another user (should not appear)
        other_user = User(
            name="Other User",
            email="other_list@example.com",
            password=hash_password("password123"),
            role="Employee",
        )
        db_session.add(other_user)
        db_session.commit()
        db_session.refresh(other_user)

        create_notification(
            db=db_session,
            recipient_id=other_user.id,
            notification_type=NotificationType.TICKET_ASSIGNED,
            title="Other's Notification",
            message="Should not appear",
        )

        # Get notifications for user
        result = get_notifications_for_user(
            db=db_session,
            user_id=user.id,
            page=1,
            page_size=10,
        )

        assert result.total == 5
        assert len(result.items) == 5
        assert result.page == 1
        assert result.page_size == 10
        assert result.total_pages == 1

    def test_get_notifications_unread_only(self, db_session):
        """Test filtering unread notifications."""
        user = User(
            name="Unread Test User",
            email="unread_test@example.com",
            password=hash_password("password123"),
            role="Employee",
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        # Create 3 unread notifications
        for i in range(3):
            create_notification(
                db=db_session,
                recipient_id=user.id,
                notification_type=NotificationType.TICKET_ASSIGNED,
                title=f"Unread {i}",
                message="Unread message",
            )

        # Create 2 read notifications
        for i in range(2):
            notif = create_notification(
                db=db_session,
                recipient_id=user.id,
                notification_type=NotificationType.TICKET_ASSIGNED,
                title=f"Read {i}",
                message="Read message",
            )
            mark_notification_as_read(db=db_session, notification_id=notif.id, user_id=user.id)

        # Get unread only
        result = get_notifications_for_user(
            db=db_session,
            user_id=user.id,
            page=1,
            page_size=10,
            unread_only=True,
        )

        assert result.total == 3
        assert all(not n.is_read for n in result.items)

    def test_get_notifications_filter_by_type(self, db_session):
        """Test filtering notifications by type."""
        user = User(
            name="Filter Test User",
            email="filter_test@example.com",
            password=hash_password("password123"),
            role="Employee",
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        create_notification(
            db=db_session,
            recipient_id=user.id,
            notification_type=NotificationType.TICKET_ASSIGNED,
            title="Assigned",
            message="Assigned message",
        )
        create_notification(
            db=db_session,
            recipient_id=user.id,
            notification_type=NotificationType.TICKET_ESCALATED,
            title="Escalated",
            message="Escalated message",
        )
        create_notification(
            db=db_session,
            recipient_id=user.id,
            notification_type=NotificationType.SLA_RESPONSE_BREACHED,
            title="Breached",
            message="Breached message",
        )

        # Filter by TICKET_ASSIGNED
        result = get_notifications_for_user(
            db=db_session,
            user_id=user.id,
            page=1,
            page_size=10,
            notification_type=NotificationType.TICKET_ASSIGNED,
        )

        assert result.total == 1
        assert result.items[0].notification_type == "TICKET_ASSIGNED"

    def test_get_unread_count(self, db_session):
        """Test getting unread count."""
        user = User(
            name="Count Test User",
            email="count_test@example.com",
            password=hash_password("password123"),
            role="Employee",
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        # Initially 0
        count = get_unread_count(db=db_session, user_id=user.id)
        assert count.unread_count == 0

        # Add 3 notifications
        for i in range(3):
            create_notification(
                db=db_session,
                recipient_id=user.id,
                notification_type=NotificationType.TICKET_ASSIGNED,
                title=f"Notification {i}",
                message="Test",
            )

        count = get_unread_count(db=db_session, user_id=user.id)
        assert count.unread_count == 3

        # Mark one as read
        notif = create_notification(
            db=db_session,
            recipient_id=user.id,
            notification_type=NotificationType.TICKET_ASSIGNED,
            title="To be read",
            message="Test",
        )
        mark_notification_as_read(db=db_session, notification_id=notif.id, user_id=user.id)

        count = get_unread_count(db=db_session, user_id=user.id)
        assert count.unread_count == 3  # Still 3 because we added then marked one

    def test_mark_notification_as_read(self, db_session):
        """Test marking a notification as read."""
        user = User(
            name="Read Test User",
            email="read_test@example.com",
            password=hash_password("password123"),
            role="Employee",
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        notification = create_notification(
            db=db_session,
            recipient_id=user.id,
            notification_type=NotificationType.TICKET_ASSIGNED,
            title="To Read",
            message="Test message",
        )

        assert notification.is_read is False
        assert notification.read_at is None

        # Mark as read
        updated = mark_notification_as_read(
            db=db_session,
            notification_id=notification.id,
            user_id=user.id,
        )

        assert updated.is_read is True
        assert updated.read_at is not None

        # Mark again (idempotent)
        updated2 = mark_notification_as_read(
            db=db_session,
            notification_id=notification.id,
            user_id=user.id,
        )
        assert updated2.is_read is True

    def test_mark_notification_as_read_unauthorized(self, db_session):
        """Test that users cannot mark other users' notifications as read."""
        user1 = User(
            name="User 1",
            email="user1_read@example.com",
            password=hash_password("password123"),
            role="Employee",
        )
        user2 = User(
            name="User 2",
            email="user2_read@example.com",
            password=hash_password("password123"),
            role="Employee",
        )
        db_session.add_all([user1, user2])
        db_session.commit()
        db_session.refresh(user1)
        db_session.refresh(user2)

        notification = create_notification(
            db=db_session,
            recipient_id=user1.id,
            notification_type=NotificationType.TICKET_ASSIGNED,
            title="User 1's notification",
            message="Test",
        )

        from fastapi import HTTPException
        with pytest.raises(HTTPException) as exc_info:
            mark_notification_as_read(
                db=db_session,
                notification_id=notification.id,
                user_id=user2.id,
            )
        assert exc_info.value.status_code == 403

    def test_mark_notification_not_found(self, db_session):
        """Test marking non-existent notification."""
        user = User(
            name="Not Found Test",
            email="notfound_test@example.com",
            password=hash_password("password123"),
            role="Employee",
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        result = mark_notification_as_read(
            db=db_session,
            notification_id=99999,
            user_id=user.id,
        )
        assert result is None

    def test_mark_all_as_read(self, db_session):
        """Test marking all notifications as read."""
        user = User(
            name="Mark All Test",
            email="markall_test@example.com",
            password=hash_password("password123"),
            role="Employee",
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        # Create 5 unread notifications
        for i in range(5):
            create_notification(
                db=db_session,
                recipient_id=user.id,
                notification_type=NotificationType.TICKET_ASSIGNED,
                title=f"Notification {i}",
                message="Test",
            )

        count = get_unread_count(db=db_session, user_id=user.id)
        assert count.unread_count == 5

        # Mark all as read
        marked = mark_all_notifications_as_read(db=db_session, user_id=user.id)
        assert marked == 5

        count = get_unread_count(db=db_session, user_id=user.id)
        assert count.unread_count == 0

        # Call again (idempotent)
        marked = mark_all_notifications_as_read(db=db_session, user_id=user.id)
        assert marked == 0


class TestNotificationAPI:
    """Tests for Notification API endpoints."""

    def test_list_notifications_authenticated(self, client, auth_headers, test_user, db_session):
        """Test listing notifications as authenticated user."""
        # Create some notifications via service layer (which works)
        from app.services.notification_service import create_notification
        for i in range(3):
            create_notification(
                db=db_session,
                recipient_id=test_user.id,
                notification_type=NotificationType.TICKET_ASSIGNED,
                title=f"Notification {i}",
                message=f"Message {i}",
            )

        response = client.get("/notifications/", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 3
        assert len(data["items"]) == 3
        assert data["page"] == 1

    def test_list_notifications_unauthenticated(self, client):
        """Test listing notifications without authentication."""
        response = client.get("/notifications/")
        assert response.status_code == 401

    def test_list_notifications_pagination(self, client, auth_headers, test_user, db_session):
        """Test notification pagination."""
        from app.services.notification_service import create_notification
        for i in range(15):
            create_notification(
                db=db_session,
                recipient_id=test_user.id,
                notification_type=NotificationType.TICKET_ASSIGNED,
                title=f"Notification {i}",
                message=f"Message {i}",
            )

        # Page 1
        response = client.get("/notifications/?page=1&page_size=5", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 15
        assert data["page"] == 1
        assert data["page_size"] == 5
        assert len(data["items"]) == 5
        assert data["total_pages"] == 3

        # Page 2
        response = client.get("/notifications/?page=2&page_size=5", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["page"] == 2
        assert len(data["items"]) == 5

    def test_list_notifications_unread_only(self, client, auth_headers, test_user, db_session):
        """Test filtering unread notifications via API."""
        from app.services.notification_service import create_notification, mark_notification_as_read
        # Create unread
        for i in range(3):
            create_notification(
                db=db_session,
                recipient_id=test_user.id,
                notification_type=NotificationType.TICKET_ASSIGNED,
                title=f"Unread {i}",
                message="Unread",
            )
        # Create read
        for i in range(2):
            notif = create_notification(
                db=db_session,
                recipient_id=test_user.id,
                notification_type=NotificationType.TICKET_ASSIGNED,
                title=f"Read {i}",
                message="Read",
            )
            mark_notification_as_read(db=db_session, notification_id=notif.id, user_id=test_user.id)

        response = client.get("/notifications/?unread_only=true", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 3
        assert all(not item["is_read"] for item in data["items"])

    def test_list_notifications_filter_by_type(self, client, auth_headers, test_user, db_session):
        """Test filtering notifications by type via API."""
        from app.services.notification_service import create_notification
        create_notification(
            db=db_session,
            recipient_id=test_user.id,
            notification_type=NotificationType.TICKET_ASSIGNED,
            title="Assigned",
            message="Assigned",
        )
        create_notification(
            db=db_session,
            recipient_id=test_user.id,
            notification_type=NotificationType.TICKET_ESCALATED,
            title="Escalated",
            message="Escalated",
        )

        response = client.get("/notifications/?notification_type=TICKET_ASSIGNED", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["items"][0]["notification_type"] == "TICKET_ASSIGNED"

    def test_unread_count(self, client, auth_headers, test_user, db_session):
        """Test getting unread count."""
        from app.services.notification_service import create_notification
        for i in range(4):
            create_notification(
                db=db_session,
                recipient_id=test_user.id,
                notification_type=NotificationType.TICKET_ASSIGNED,
                title=f"Notification {i}",
                message="Test",
            )

        response = client.get("/notifications/unread-count", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["unread_count"] == 4

    def test_unread_count_unauthenticated(self, client):
        """Test unread count without authentication."""
        response = client.get("/notifications/unread-count")
        assert response.status_code == 401

    def test_mark_notification_as_read(self, client, auth_headers, test_user, db_session):
        """Test marking a notification as read."""
        from app.services.notification_service import create_notification
        notif = create_notification(
            db=db_session,
            recipient_id=test_user.id,
            notification_type=NotificationType.TICKET_ASSIGNED,
            title="To Read",
            message="Test",
        )

        response = client.patch(f"/notifications/{notif.id}/read", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["is_read"] is True
        assert data["read_at"] is not None

    def test_mark_notification_as_read_unauthorized(self, client, auth_headers, test_user, technician_user, db_session):
        """Test that users cannot mark other users' notifications as read."""
        from app.services.notification_service import create_notification
        notif = create_notification(
            db=db_session,
            recipient_id=technician_user.id,
            notification_type=NotificationType.TICKET_ASSIGNED,
            title="Tech's notification",
            message="Test",
        )

        response = client.patch(f"/notifications/{notif.id}/read", headers=auth_headers)
        assert response.status_code == 403

    def test_mark_notification_not_found(self, client, auth_headers):
        """Test marking non-existent notification."""
        response = client.patch("/notifications/99999/read", headers=auth_headers)
        assert response.status_code == 404

    def test_mark_all_as_read(self, client, auth_headers, test_user, db_session):
        """Test marking all notifications as read."""
        from app.services.notification_service import create_notification
        for i in range(5):
            create_notification(
                db=db_session,
                recipient_id=test_user.id,
                notification_type=NotificationType.TICKET_ASSIGNED,
                title=f"Notification {i}",
                message="Test",
            )

        # Check unread count before
        response = client.get("/notifications/unread-count", headers=auth_headers)
        assert response.json()["unread_count"] == 5

        # Mark all as read
        response = client.post("/notifications/mark-all-read", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["marked_count"] == 5

        # Check unread count after
        response = client.get("/notifications/unread-count", headers=auth_headers)
        assert response.json()["unread_count"] == 0


class TestNotificationIntegration:
    """Integration tests for notifications with ticket workflow."""

    def test_ticket_assignment_creates_notification(self, client, admin_auth_headers, technician_user, auth_headers):
        """Test that assigning a ticket creates a notification for the assignee."""
        # Create ticket as employee
        response = client.post("/tickets/", json={
            "title": "Assignment Test",
            "description": "Test ticket for assignment notification",
            "priority": "Medium",
        }, headers=auth_headers)
        assert response.status_code == 200
        ticket_id = response.json()["id"]

        # Assign ticket to technician as admin
        response = client.put(f"/tickets/{ticket_id}/assign", json={
            "assigned_to": technician_user.id
        }, headers=admin_auth_headers)
        assert response.status_code == 200

        # Check technician's notifications
        tech_response = client.post("/auth/login", json={
            "email": "tech@example.com",
            "password": "techpassword123",
        })
        tech_token = tech_response.json()["access_token"]
        tech_headers = {"Authorization": f"Bearer {tech_token}"}

        response = client.get("/notifications/", headers=tech_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 1
        assigned_notifs = [n for n in data["items"] if n["notification_type"] == "TICKET_ASSIGNED"]
        assert len(assigned_notifs) >= 1
        assert assigned_notifs[0]["ticket_id"] == ticket_id

    

    def test_sla_response_breach_creates_notification(self, client, auth_headers, admin_auth_headers, db_session):
        """Test that SLA response breach creates notification."""
        from app.services.sla_service import create_sla_policy
        from app.services.sla_breach_service import process_response_breach
        from datetime import datetime, timezone, timedelta

        # Create SLA policy with 1 minute response time
        policy = create_sla_policy(
            db=db_session,
            name="Test Response Breach",
            priority="High",
            response_time_minutes=1,
            resolution_time_minutes=240,
        )

        # Create ticket as employee
        response = client.post("/tickets/", json={
            "title": "SLA Breach Test",
            "description": "Test ticket for SLA response breach",
            "priority": "High",
        }, headers=auth_headers)
        assert response.status_code == 200
        ticket_id = response.json()["id"]

        # Get ticket and set deadline to past
        from app.models.ticket import Ticket
        ticket = db_session.query(Ticket).filter(Ticket.id == ticket_id).first()
        ticket.sla_response_deadline = datetime.now(timezone.utc) - timedelta(minutes=5)
        db_session.commit()

        # Process breach
        result = process_response_breach(db_session, ticket)
        assert result is True

        # Check notifications for ticket creator
        response = client.get("/notifications/", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        breach_notifs = [n for n in data["items"] if n["notification_type"] == "SLA_RESPONSE_BREACHED"]
        assert len(breach_notifs) >= 1
        assert breach_notifs[0]["ticket_id"] == ticket_id

    def test_sla_resolution_breach_creates_notification(self, client, auth_headers, admin_auth_headers, db_session, technician_user):
        """Test that SLA resolution breach creates notification."""
        from app.services.sla_service import create_sla_policy
        from app.services.sla_breach_service import process_resolution_breach
        from datetime import datetime, timezone, timedelta

        # Create SLA policy with 1 minute resolution time
        policy = create_sla_policy(
            db=db_session,
            name="Test Resolution Breach",
            priority="Critical",
            response_time_minutes=30,
            resolution_time_minutes=1,
        )

        # Create ticket as employee
        response = client.post("/tickets/", json={
            "title": "Resolution Breach Test",
            "description": "Test ticket for SLA resolution breach",
            "priority": "Critical",
        }, headers=auth_headers)
        assert response.status_code == 200
        ticket_id = response.json()["id"]

        # Assign to technician
        client.put(f"/tickets/{ticket_id}/assign", json={
            "assigned_to": technician_user.id
        }, headers=admin_auth_headers)

        # Get ticket and set resolution deadline to past
        from app.models.ticket import Ticket
        ticket = db_session.query(Ticket).filter(Ticket.id == ticket_id).first()
        ticket.sla_resolution_deadline = datetime.now(timezone.utc) - timedelta(minutes=5)
        db_session.commit()

        # Process breach
        result = process_resolution_breach(db_session, ticket)
        assert result is True

        # Check notifications for assigned technician
        tech_response = client.post("/auth/login", json={
            "email": "tech@example.com",
            "password": "techpassword123",
        })
        tech_token = tech_response.json()["access_token"]
        tech_headers = {"Authorization": f"Bearer {tech_token}"}

        response = client.get("/notifications/", headers=tech_headers)
        assert response.status_code == 200
        data = response.json()
        breach_notifs = [n for n in data["items"] if n["notification_type"] == "SLA_RESOLUTION_BREACHED"]
        assert len(breach_notifs) >= 1
        assert breach_notifs[0]["ticket_id"] == ticket_id

    def test_duplicate_sla_breach_does_not_create_duplicate_notifications(self, client, auth_headers, admin_auth_headers, db_session):
        """Test that running breach check twice doesn't create duplicate notifications."""
        from app.services.sla_service import create_sla_policy
        from app.services.sla_breach_service import process_response_breach
        from datetime import datetime, timezone, timedelta

        # Create SLA policy
        policy = create_sla_policy(
            db=db_session,
            name="Test Duplicate Breach Notif",
            priority="High",
            response_time_minutes=1,
            resolution_time_minutes=240,
        )

        # Create ticket
        response = client.post("/tickets/", json={
            "title": "Duplicate Breach Test",
            "description": "Test duplicate breach notifications",
            "priority": "High",
        }, headers=auth_headers)
        assert response.status_code == 200
        ticket_id = response.json()["id"]

        # Set deadline to past
        from app.models.ticket import Ticket
        ticket = db_session.query(Ticket).filter(Ticket.id == ticket_id).first()
        ticket.sla_response_deadline = datetime.now(timezone.utc) - timedelta(minutes=5)
        db_session.commit()

        # Process breach first time
        result1 = process_response_breach(db_session, ticket)
        assert result1 is True

        # Process breach second time (should be idempotent)
        result2 = process_response_breach(db_session, ticket)
        assert result2 is False

        # Check notifications - should only have one breach notification
        response = client.get("/notifications/", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        breach_notifs = [n for n in data["items"] if n["notification_type"] == "SLA_RESPONSE_BREACHED"]
        assert len(breach_notifs) == 1


class TestEscalationService:
    """Tests for Escalation Service (Phase 2D-3B)."""

    def test_create_escalation_rule(self, db_session):
        """Test creating an escalation rule."""
        from app.services.escalation_service import (
            create_escalation_rule,
            get_escalation_rule,
            EscalationEventType,
        )
        
        rule = create_escalation_rule(
            db=db_session,
            name="Critical Response Breach Escalation",
            event_type=EscalationEventType.RESPONSE_BREACH,
            priority="Critical",
            target_role="Admin",
            description="Escalate critical response breaches to Admin",
            notify_enabled=True,
            email_enabled=True,
        )
        
        assert rule.id is not None
        assert rule.name == "Critical Response Breach Escalation"
        assert rule.event_type == EscalationEventType.RESPONSE_BREACH
        assert rule.priority == "Critical"
        assert rule.target_role == "Admin"
        assert rule.notify_enabled is True
        assert rule.email_enabled is True
        assert rule.is_active is True
        assert rule.precedence == 2  # event_type + priority

    def test_create_escalation_rule_with_ticket_type(self, db_session):
        """Test creating an escalation rule with ticket_type increases precedence."""
        from app.services.escalation_service import (
            create_escalation_rule,
            EscalationEventType,
        )
        
        rule = create_escalation_rule(
            db=db_session,
            name="Critical Incident Response Breach",
            event_type=EscalationEventType.RESPONSE_BREACH,
            priority="Critical",
            target_role="Technician",
            ticket_type="INCIDENT",
            category="Network",
        )
        
        assert rule.ticket_type == "INCIDENT"
        assert rule.category == "Network"
        assert rule.precedence == 4  # event_type + priority + ticket_type + category

    def test_get_escalation_rule(self, db_session):
        """Test retrieving an escalation rule by ID."""
        from app.services.escalation_service import (
            create_escalation_rule,
            get_escalation_rule,
            get_escalation_rule_by_name,
            EscalationEventType,
        )
        
        rule = create_escalation_rule(
            db=db_session,
            name="Test Rule",
            event_type=EscalationEventType.RESOLUTION_BREACH,
            priority="High",
            target_role="Technician",
        )
        
        retrieved = get_escalation_rule(db_session, rule.id)
        assert retrieved is not None
        assert retrieved.id == rule.id
        assert retrieved.name == "Test Rule"
        
        by_name = get_escalation_rule_by_name(db_session, "Test Rule")
        assert by_name is not None
        assert by_name.id == rule.id

    def test_list_escalation_rules(self, db_session):
        """Test listing escalation rules with pagination."""
        from app.services.escalation_service import (
            create_escalation_rule,
            list_escalation_rules,
            EscalationEventType,
        )
        
        for i in range(5):
            create_escalation_rule(
                db=db_session,
                name=f"Rule {i}",
                event_type=EscalationEventType.RESPONSE_BREACH,
                priority="High",
                target_role="Admin",
            )
        
        result = list_escalation_rules(db_session, page=1, page_size=3)
        assert result["total"] == 5
        assert len(result["items"]) == 3
        assert result["page"] == 1
        assert result["page_size"] == 3
        assert result["total_pages"] == 2
        
        # Test filtering by event_type
        result = list_escalation_rules(db_session, event_type=EscalationEventType.RESPONSE_BREACH)
        assert result["total"] == 5
        
        # Test filtering by priority
        result = list_escalation_rules(db_session, priority="High")
        assert result["total"] == 5

    def test_update_escalation_rule(self, db_session):
        """Test updating an escalation rule."""
        from app.services.escalation_service import (
            create_escalation_rule,
            update_escalation_rule,
            EscalationEventType,
        )
        
        rule = create_escalation_rule(
            db=db_session,
            name="Original Name",
            event_type=EscalationEventType.RESPONSE_BREACH,
            priority="Critical",
            target_role="Admin",
            is_active=True,
        )
        
        updated = update_escalation_rule(
            db=db_session,
            rule_id=rule.id,
            name="Updated Name",
            target_role="Technician",
            is_active=False,
        )
        
        assert updated.name == "Updated Name"
        assert updated.target_role == "Technician"
        assert updated.is_active is False

    def test_delete_escalation_rule(self, db_session):
        """Test soft deleting an escalation rule."""
        from app.services.escalation_service import (
            create_escalation_rule,
            delete_escalation_rule,
            get_escalation_rule,
            EscalationEventType,
        )
        
        rule = create_escalation_rule(
            db=db_session,
            name="To Delete",
            event_type=EscalationEventType.RESOLUTION_BREACH,
            priority="Medium",
            target_role="Admin",
        )
        
        result = delete_escalation_rule(db_session, rule.id)
        assert result is True
        
        retrieved = get_escalation_rule(db_session, rule.id)
        assert retrieved.is_active is False

    def test_rule_matching_specificity(self, db_session):
        """Test that more specific rules take precedence over generic ones."""
        from app.services.escalation_service import (
            create_escalation_rule,
            get_best_matching_rule,
            EscalationEventType,
        )
        
        # Generic rule for High priority
        create_escalation_rule(
            db=db_session,
            name="Generic High Priority Response Breach",
            event_type=EscalationEventType.RESPONSE_BREACH,
            priority="High",
            target_role="Admin",
        )
        db_session.commit()
        
        # Generic rule for Medium priority
        create_escalation_rule(
            db=db_session,
            name="Generic Medium Priority Response Breach",
            event_type=EscalationEventType.RESPONSE_BREACH,
            priority="Medium",
            target_role="Admin",
        )
        db_session.commit()
        
        # Specific rule for High priority INCIDENT type (priority + ticket_type)
        create_escalation_rule(
            db=db_session,
            name="High Priority Incident Response Breach",
            event_type=EscalationEventType.RESPONSE_BREACH,
            priority="High",
            target_role="Technician",
            ticket_type="INCIDENT",
        )
        db_session.commit()
        
        # Even more specific with category (priority + ticket_type + category)
        create_escalation_rule(
            db=db_session,
            name="High Priority Network Incident Response Breach",
            event_type=EscalationEventType.RESPONSE_BREACH,
            priority="High",
            target_role="Admin",
            ticket_type="INCIDENT",
            category="Network",
        )
        db_session.commit()
        
        # Test matching - should get the most specific rule
        rule = get_best_matching_rule(
            db=db_session,
            event_type=EscalationEventType.RESPONSE_BREACH,
            priority="High",
            ticket_type="INCIDENT",
            category="Network",
        )
        assert rule is not None, "Should match the most specific rule (Network category)"
        assert rule.name == "High Priority Network Incident Response Breach"
        
        # Test without category - should get INCIDENT-specific rule
        rule = get_best_matching_rule(
            db=db_session,
            event_type=EscalationEventType.RESPONSE_BREACH,
            priority="High",
            ticket_type="INCIDENT",
            category="Database",
        )
        assert rule is not None, "Should match INCIDENT-specific rule"
        assert rule.name == "High Priority Incident Response Breach"
        
        # Test with different priority (Medium) - should get Medium generic rule
        rule = get_best_matching_rule(
            db=db_session,
            event_type=EscalationEventType.RESPONSE_BREACH,
            priority="Medium",
            ticket_type="INCIDENT",
        )
        assert rule is not None, "Should match generic rule for Medium priority"
        assert rule.name == "Generic Medium Priority Response Breach"
        
        # Test no matching rule (Low priority has no rules)
        rule = get_best_matching_rule(
            db=db_session,
            event_type=EscalationEventType.RESPONSE_BREACH,
            priority="Low",
        )
        assert rule is None

    def test_disabled_rule_not_matched(self, db_session):
        """Test that disabled rules are not matched."""
        from app.services.escalation_service import (
            create_escalation_rule,
            get_best_matching_rule,
            EscalationEventType,
        )
        
        create_escalation_rule(
            db=db_session,
            name="Disabled Rule",
            event_type=EscalationEventType.RESPONSE_BREACH,
            priority="Critical",
            target_role="Admin",
            is_active=False,
        )
        
        rule = get_best_matching_rule(
            db=db_session,
            event_type=EscalationEventType.RESPONSE_BREACH,
            priority="Critical",
        )
        assert rule is None

    def test_resolve_escalation_recipient_admin(self, db_session):
        """Test recipient resolution for Admin target role."""
        from app.services.escalation_service import (
            create_escalation_rule,
            resolve_escalation_recipient,
            EscalationEventType,
        )
        from app.models.ticket import Ticket
        from app.models.user import User
        from app.utils.security import hash_password
        
        # Create Admin user
        admin = User(
            name="Admin User",
            email="admin_escalation@example.com",
            password=hash_password("password123"),
            role="Admin",
        )
        db_session.add(admin)
        
        # Create Technician user
        tech = User(
            name="Tech User",
            email="tech_escalation@example.com",
            password=hash_password("password123"),
            role="Technician",
        )
        db_session.add(tech)
        db_session.commit()
        
        # Create rule targeting Admin
        rule = create_escalation_rule(
            db=db_session,
            name="Admin Escalation",
            event_type=EscalationEventType.RESPONSE_BREACH,
            priority="Critical",
            target_role="Admin",
        )
        
        # Create a test ticket
        ticket = Ticket(
            title="Test Ticket",
            description="Test",
            priority="Critical",
            status="Open",
            ticket_type="INCIDENT",
            created_by=tech.id,
        )
        db_session.add(ticket)
        db_session.commit()
        
        recipient = resolve_escalation_recipient(db_session, ticket, rule)
        assert recipient is not None
        assert recipient.role == "Admin"
        assert recipient.id == admin.id

    def test_resolve_escalation_recipient_technician_fallback(self, db_session):
        """Test fallback to Admin when no Technician available."""
        from app.services.escalation_service import (
            create_escalation_rule,
            resolve_escalation_recipient,
            EscalationEventType,
        )
        from app.models.ticket import Ticket
        from app.models.user import User
        from app.utils.security import hash_password
        
        # First, ensure no Technician exists in this test's transaction
        # Delete any existing technicians (from other tests that might have leaked)
        db_session.query(User).filter(User.role == "Technician").delete()
        db_session.commit()
        
        # Create only Admin user (no Technician)
        admin = User(
            name="Admin Only",
            email="admin_only@example.com",
            password=hash_password("password123"),
            role="Admin",
        )
        db_session.add(admin)
        db_session.commit()
        
        # Verify no technician exists
        tech_count = db_session.query(User).filter(User.role == "Technician").count()
        assert tech_count == 0, "No technician should exist for fallback test"
        
        # Create rule targeting Technician
        rule = create_escalation_rule(
            db=db_session,
            name="Tech Escalation",
            event_type=EscalationEventType.RESPONSE_BREACH,
            priority="High",
            target_role="Technician",
        )
        
        # Create a test ticket
        ticket = Ticket(
            title="Test Ticket",
            description="Test",
            priority="High",
            status="Open",
            ticket_type="INCIDENT",
            created_by=admin.id,
        )
        db_session.add(ticket)
        db_session.commit()
        
        # Should fall back to Admin
        recipient = resolve_escalation_recipient(db_session, ticket, rule)
        assert recipient is not None
        assert recipient.role == "Admin"
        assert recipient.id == admin.id

    def test_resolve_escalation_recipient_no_users(self, db_session):
        """Test recipient resolution when no users exist."""
        from app.services.escalation_service import (
            create_escalation_rule,
            resolve_escalation_recipient,
            EscalationEventType,
        )
        from app.models.ticket import Ticket
        from app.models.user import User
        
        # Ensure no users exist
        db_session.query(User).delete()
        db_session.commit()
        
        rule = create_escalation_rule(
            db=db_session,
            name="No Recipient Rule",
            event_type=EscalationEventType.RESPONSE_BREACH,
            priority="Critical",
            target_role="Admin",
        )
        
        # Create a mock ticket object without saving to DB (no FK issues)
        ticket = Ticket(
            title="Test Ticket",
            description="Test",
            priority="Critical",
            status="Open",
            ticket_type="INCIDENT",
        )
        # Don't add to session - just use as object for recipient resolution
        
        recipient = resolve_escalation_recipient(db_session, ticket, rule)
        assert recipient is None

    def test_check_escalation_exists(self, db_session):
        """Test idempotency check for existing escalation records."""
        from app.services.escalation_service import (
            create_escalation_rule,
            check_escalation_exists,
            EscalationEventType,
        )
        from app.models.ticket import Ticket
        from app.models.user import User
        from app.utils.security import hash_password
        
        # Create users and rule
        admin = User(
            name="Admin",
            email="admin_check@example.com",
            password=hash_password("password123"),
            role="Admin",
        )
        db_session.add(admin)
        
        rule = create_escalation_rule(
            db=db_session,
            name="Check Rule",
            event_type=EscalationEventType.RESPONSE_BREACH,
            priority="High",
            target_role="Admin",
        )
        
        ticket = Ticket(
            title="Test Ticket",
            description="Test",
            priority="High",
            status="Open",
            ticket_type="INCIDENT",
            created_by=admin.id,
        )
        db_session.add(ticket)
        db_session.commit()
        
        # No escalation record yet
        existing = check_escalation_exists(db_session, ticket.id, EscalationEventType.RESPONSE_BREACH, rule.id)
        assert existing is None
        
        # Create escalation record
        from app.models.escalation import EscalationRecord
        record = EscalationRecord(
            ticket_id=ticket.id,
            event_type=EscalationEventType.RESPONSE_BREACH,
            rule_id=rule.id,
            recipient_id=admin.id,
        )
        db_session.add(record)
        db_session.commit()
        
        # Now should find it
        existing = check_escalation_exists(db_session, ticket.id, EscalationEventType.RESPONSE_BREACH, rule.id)
        assert existing is not None
        assert existing.id == record.id
        assert existing.ticket_id == ticket.id
        assert existing.event_type == EscalationEventType.RESPONSE_BREACH
        assert existing.rule_id == rule.id

    def test_create_escalation_notification(self, db_session):
        """Test creating escalation notification."""
        from app.services.escalation_service import (
            create_escalation_rule,
            create_escalation_notification,
            EscalationEventType,
        )
        from app.models.ticket import Ticket
        from app.models.user import User
        from app.utils.security import hash_password
        from app.models.notification import Notification
        
        admin = User(
            name="Admin Notify",
            email="admin_notify@example.com",
            password=hash_password("password123"),
            role="Admin",
        )
        tech = User(
            name="Tech Notify",
            email="tech_notify@example.com",
            password=hash_password("password123"),
            role="Technician",
        )
        db_session.add_all([admin, tech])
        
        rule = create_escalation_rule(
            db=db_session,
            name="Notify Rule",
            event_type=EscalationEventType.RESOLUTION_BREACH,
            priority="Critical",
            target_role="Admin",
            notify_enabled=True,
        )
        
        ticket = Ticket(
            title="Resolution Breach Ticket",
            description="Test",
            priority="Critical",
            status="Open",
            ticket_type="INCIDENT",
            created_by=tech.id,
            assigned_to=tech.id,
        )
        db_session.add(ticket)
        db_session.commit()
        
        notification_id = create_escalation_notification(db_session, ticket, admin, EscalationEventType.RESOLUTION_BREACH, rule)
        assert notification_id is not None
        
        # Verify notification was created
        notification = db_session.query(Notification).filter(Notification.id == notification_id).first()
        assert notification is not None
        assert notification.recipient_id == admin.id
        assert notification.notification_type.value == "TICKET_ESCALATED"
        assert "Resolution" in notification.title
        assert "escalated" in notification.message.lower()
        assert notification.ticket_id == ticket.id

    def test_escalation_notification_disabled(self, db_session):
        """Test that notification is not created when disabled in rule."""
        from app.services.escalation_service import (
            create_escalation_rule,
            create_escalation_notification,
            EscalationEventType,
        )
        from app.models.ticket import Ticket
        from app.models.user import User
        from app.utils.security import hash_password
        
        admin = User(
            name="Admin No Notify",
            email="admin_nonotify@example.com",
            password=hash_password("password123"),
            role="Admin",
        )
        db_session.add(admin)
        
        rule = create_escalation_rule(
            db=db_session,
            name="No Notify Rule",
            event_type=EscalationEventType.RESPONSE_BREACH,
            priority="High",
            target_role="Admin",
            notify_enabled=False,
        )
        
        ticket = Ticket(
            title="Test",
            description="Test",
            priority="High",
            status="Open",
            ticket_type="INCIDENT",
            created_by=admin.id,
        )
        db_session.add(ticket)
        db_session.commit()
        
        notification_id = create_escalation_notification(db_session, ticket, admin, EscalationEventType.RESPONSE_BREACH, rule)
        assert notification_id is None

    def test_build_escalation_email(self, db_session):
        """Test building escalation email content."""
        from app.services.escalation_service import (
            create_escalation_rule,
            build_escalation_email,
            EscalationEventType,
        )
        from app.models.ticket import Ticket
        from app.models.user import User
        from app.utils.security import hash_password
        from datetime import datetime, timezone
        
        admin = User(
            name="Admin Email",
            email="admin_email@example.com",
            password=hash_password("password123"),
            role="Admin",
        )
        tech = User(
            name="Tech Email",
            email="tech_email@example.com",
            password=hash_password("password123"),
            role="Technician",
        )
        db_session.add_all([admin, tech])
        
        rule = create_escalation_rule(
            db=db_session,
            name="Email Rule",
            event_type=EscalationEventType.RESPONSE_BREACH,
            priority="Critical",
            target_role="Admin",
            email_enabled=True,
        )
        
        ticket = Ticket(
            title="Email Test Ticket",
            description="Test description",
            priority="Critical",
            status="Open",
            ticket_type="INCIDENT",
            category="Network",
            created_by=tech.id,
            assigned_to=tech.id,
            sla_response_deadline=datetime.now(timezone.utc),
        )
        db_session.add(ticket)
        db_session.commit()
        
        subject, body = build_escalation_email(ticket, admin, EscalationEventType.RESPONSE_BREACH, rule)
        
        assert "Escalation" in subject
        assert "Response" in subject
        assert str(ticket.id) in subject
        assert ticket.title in subject
        
        assert "Email Test Ticket" in body
        assert "Critical" in body
        assert "INCIDENT" in body
        assert "Network" in body
        assert "Tech Email" in body
        assert "admin_email@example.com" in body
        assert "Response" in body
        assert rule.name in body

    def test_escalation_email_disabled(self, db_session):
        """Test email not sent when disabled in rule."""
        from app.services.escalation_service import (
            create_escalation_rule,
            send_escalation_email,
            EscalationEventType,
        )
        from app.models.ticket import Ticket
        from app.models.user import User
        from app.utils.security import hash_password
        
        admin = User(
            name="Admin No Email",
            email="admin_noemail@example.com",
            password=hash_password("password123"),
            role="Admin",
        )
        db_session.add(admin)
        
        rule = create_escalation_rule(
            db=db_session,
            name="No Email Rule",
            event_type=EscalationEventType.RESPONSE_BREACH,
            priority="High",
            target_role="Admin",
            email_enabled=False,
        )
        
        ticket = Ticket(
            title="Test",
            description="Test",
            priority="High",
            status="Open",
            ticket_type="INCIDENT",
            created_by=admin.id,
        )
        db_session.add(ticket)
        db_session.commit()
        
        import asyncio
        result = asyncio.run(send_escalation_email(ticket, admin, EscalationEventType.RESPONSE_BREACH, rule))
        assert result.success is False
        assert "disabled" in result.error.lower() or "email_enabled" in result.error.lower()

    def test_record_escalation_history(self, db_session):
        """Test recording escalation history event."""
        from app.services.escalation_service import (
            create_escalation_rule,
            record_escalation_history,
            EscalationEventType,
        )
        from app.models.ticket import Ticket
        from app.models.user import User
        from app.models.ticket_comment import TicketHistory, HistoryEventType
        from app.utils.security import hash_password
        
        admin = User(
            name="Admin History",
            email="admin_history@example.com",
            password=hash_password("password123"),
            role="Admin",
        )
        system = User(
            name="ITMS System",
            email="system@itms.local",
            password="",
            role="Admin",
        )
        tech = User(
            name="Tech History",
            email="tech_history@example.com",
            password=hash_password("password123"),
            role="Technician",
        )
        db_session.add_all([admin, system, tech])
        db_session.commit()
        
        rule = create_escalation_rule(
            db=db_session,
            name="History Rule",
            event_type=EscalationEventType.RESOLUTION_BREACH,
            priority="Critical",
            target_role="Admin",
        )
        
        ticket = Ticket(
            title="History Test",
            description="Test",
            priority="Critical",
            status="Open",
            ticket_type="INCIDENT",
            created_by=tech.id,
            assigned_to=tech.id,
        )
        db_session.add(ticket)
        db_session.commit()
        
        record_escalation_history(db_session, ticket, admin, EscalationEventType.RESOLUTION_BREACH, rule, system)
        db_session.commit()
        
        # Verify history was recorded
        history = db_session.query(TicketHistory).filter(
            TicketHistory.ticket_id == ticket.id,
            TicketHistory.event_type == HistoryEventType.ESCALATED,
        ).first()
        
        assert history is not None
        assert history.actor_id == system.id
        assert "Resolution" in history.new_value
        assert "escalated" in history.new_value.lower()
        assert admin.name in history.new_value
        assert rule.name in history.new_value

    def test_process_escalation_full_flow(self, db_session):
        """Test full escalation processing flow."""
        from app.services.escalation_service import (
            create_escalation_rule,
            process_escalation,
            EscalationEventType,
        )
        from app.models.escalation import EscalationRecord
        from app.models.notification import Notification
        from app.models.ticket import Ticket
        from app.models.user import User
        from app.utils.security import hash_password
        from app.models.ticket_comment import TicketHistory, HistoryEventType
        from datetime import datetime, timezone
        
        # Create users
        admin = User(
            name="Admin Full Flow",
            email="admin_fullflow@example.com",
            password=hash_password("password123"),
            role="Admin",
        )
        tech = User(
            name="Tech Full Flow",
            email="tech_fullflow@example.com",
            password=hash_password("password123"),
            role="Technician",
        )
        db_session.add_all([admin, tech])
        
        # Create rule
        rule = create_escalation_rule(
            db=db_session,
            name="Full Flow Rule",
            event_type=EscalationEventType.RESPONSE_BREACH,
            priority="Critical",
            target_role="Admin",
            notify_enabled=True,
            email_enabled=True,
        )
        
        # Create ticket with SLA (no policy needed for escalation test)
        ticket = Ticket(
            title="Full Flow Ticket",
            description="Test ticket for full escalation flow",
            priority="Critical",
            status="Open",
            ticket_type="INCIDENT",
            category="Network",
            created_by=tech.id,
            assigned_to=tech.id,
            sla_response_deadline=datetime.now(timezone.utc),
        )
        db_session.add(ticket)
        db_session.commit()
        
        import asyncio
        result = asyncio.run(process_escalation(db_session, ticket, EscalationEventType.RESPONSE_BREACH))
        assert result is True
        
        # Verify escalation record created
        record = db_session.query(EscalationRecord).filter(
            EscalationRecord.ticket_id == ticket.id,
            EscalationRecord.event_type == EscalationEventType.RESPONSE_BREACH,
        ).first()
        
        assert record is not None
        assert record.rule_id == rule.id
        assert record.recipient_id == admin.id
        assert record.notification_created is True
        assert record.notification_id is not None
        assert record.history_recorded is True
        
        # Verify notification created
        notification = db_session.query(Notification).filter(
            Notification.id == record.notification_id
        ).first()
        assert notification is not None
        assert notification.recipient_id == admin.id
        
        # Verify history recorded
        history = db_session.query(TicketHistory).filter(
            TicketHistory.ticket_id == ticket.id,
            TicketHistory.event_type == HistoryEventType.ESCALATED,
        ).first()
        assert history is not None
        
        # Verify ticket escalation fields updated
        db_session.refresh(ticket)
        assert ticket.escalated_to == admin.id
        assert ticket.escalation_reason is not None
        assert "Response" in ticket.escalation_reason

    def test_process_escalation_idempotent(self, db_session):
        """Test that repeated escalation processing creates no duplicates."""
        from app.services.escalation_service import (
            create_escalation_rule,
            process_escalation,
            EscalationEventType,
        )
        from app.models.escalation import EscalationRecord
        from app.models.notification import Notification, NotificationType
        from app.models.ticket import Ticket
        from app.models.user import User
        from app.models.ticket_comment import TicketHistory, HistoryEventType
        from app.utils.security import hash_password
        from datetime import datetime, timezone
        
        admin = User(
            name="Admin Idempotent",
            email="admin_idempotent@example.com",
            password=hash_password("password123"),
            role="Admin",
        )
        tech = User(
            name="Tech Idempotent",
            email="tech_idempotent@example.com",
            password=hash_password("password123"),
            role="Technician",
        )
        db_session.add_all([admin, tech])
        
        rule = create_escalation_rule(
            db=db_session,
            name="Idempotent Rule",
            event_type=EscalationEventType.RESPONSE_BREACH,
            priority="High",
            target_role="Admin",
            notify_enabled=True,
            email_enabled=True,
        )
        
        ticket = Ticket(
            title="Idempotent Test",
            description="Test",
            priority="High",
            status="Open",
            ticket_type="INCIDENT",
            created_by=tech.id,
            assigned_to=tech.id,
            sla_response_deadline=datetime.now(timezone.utc),
        )
        db_session.add(ticket)
        db_session.commit()
        
        import asyncio
        # First execution
        result1 = asyncio.run(process_escalation(db_session, ticket, EscalationEventType.RESPONSE_BREACH))
        assert result1 is True
        
        # Second execution - should return True but not create duplicates
        result2 = asyncio.run(process_escalation(db_session, ticket, EscalationEventType.RESPONSE_BREACH))
        assert result2 is True
        
        # Third execution
        result3 = asyncio.run(process_escalation(db_session, ticket, EscalationEventType.RESPONSE_BREACH))
        assert result3 is True
        
        # Verify only one escalation record
        records = db_session.query(EscalationRecord).filter(
            EscalationRecord.ticket_id == ticket.id,
            EscalationRecord.event_type == EscalationEventType.RESPONSE_BREACH,
        ).all()
        assert len(records) == 1
        
        # Verify only one notification
        notifications = db_session.query(Notification).filter(
            Notification.ticket_id == ticket.id,
            Notification.notification_type == NotificationType.TICKET_ESCALATED,
            Notification.recipient_id == admin.id,
        ).all()
        assert len(notifications) == 1
        
        # Verify only one history event
        histories = db_session.query(TicketHistory).filter(
            TicketHistory.ticket_id == ticket.id,
            TicketHistory.event_type == HistoryEventType.ESCALATED,
        ).all()
        assert len(histories) == 1

    def test_process_escalation_no_matching_rule(self, db_session):
        """Test that no escalation occurs when no rule matches."""
        from app.services.escalation_service import (
            process_escalation,
            EscalationEventType,
        )
        from app.models.ticket import Ticket
        from app.models.user import User
        from app.utils.security import hash_password
        from datetime import datetime, timezone
        
        tech = User(
            name="Tech No Rule",
            email="tech_norule@example.com",
            password=hash_password("password123"),
            role="Technician",
        )
        db_session.add(tech)
        db_session.commit()
        
        # No rules created
        
        ticket = Ticket(
            title="No Rule Ticket",
            description="Test",
            priority="Low",  # No rule for Low priority
            status="Open",
            ticket_type="INCIDENT",
            created_by=tech.id,
            sla_response_deadline=datetime.now(timezone.utc),
        )
        db_session.add(ticket)
        db_session.commit()
        
        import asyncio
        result = asyncio.run(process_escalation(db_session, ticket, EscalationEventType.RESPONSE_BREACH))
        assert result is False
        
        # Verify no escalation record created
        from app.models.escalation import EscalationRecord
        records = db_session.query(EscalationRecord).filter(
            EscalationRecord.ticket_id == ticket.id,
        ).all()
        assert len(records) == 0

    def test_escalation_idempotency_persists(self, db_session):
        """Test that idempotency is enforced by database unique constraint."""
        from app.services.escalation_service import (
            create_escalation_rule,
            process_escalation,
            EscalationEventType,
        )
        from app.models.escalation import EscalationRecord
        from app.models.notification import Notification, NotificationType
        from app.models.ticket import Ticket
        from app.models.user import User
        from app.utils.security import hash_password
        from datetime import datetime, timezone
        from sqlalchemy.exc import IntegrityError
        
        # Create users
        admin = User(
            name="Admin Persist",
            email="admin_persist@example.com",
            password=hash_password("password123"),
            role="Admin",
        )
        tech = User(
            name="Tech Persist",
            email="tech_persist@example.com",
            password=hash_password("password123"),
            role="Technician",
        )
        db_session.add_all([admin, tech])
        
        rule = create_escalation_rule(
            db=db_session,
            name="Persist Rule",
            event_type=EscalationEventType.RESPONSE_BREACH,
            priority="Critical",
            target_role="Admin",
            notify_enabled=True,
            email_enabled=True,
        )
        
        ticket = Ticket(
            title="Persist Ticket",
            description="Test",
            priority="Critical",
            status="Open",
            ticket_type="INCIDENT",
            created_by=tech.id,
            assigned_to=tech.id,
            sla_response_deadline=datetime.now(timezone.utc),
        )
        db_session.add(ticket)
        db_session.commit()
        
        import asyncio
        # First escalation - should succeed
        result1 = asyncio.run(process_escalation(db_session, ticket, EscalationEventType.RESPONSE_BREACH))
        assert result1 is True
        
        # Second escalation - should return True (idempotent) but not create duplicates
        result2 = asyncio.run(process_escalation(db_session, ticket, EscalationEventType.RESPONSE_BREACH))
        assert result2 is True
        
        # Third escalation
        result3 = asyncio.run(process_escalation(db_session, ticket, EscalationEventType.RESPONSE_BREACH))
        assert result3 is True
        
        # Verify only one escalation record exists (enforced by unique constraint)
        records = db_session.query(EscalationRecord).filter(
            EscalationRecord.ticket_id == ticket.id,
            EscalationRecord.event_type == EscalationEventType.RESPONSE_BREACH,
        ).all()
        assert len(records) == 1
        
        # Verify only one notification
        notifications = db_session.query(Notification).filter(
            Notification.ticket_id == ticket.id,
            Notification.notification_type == NotificationType.TICKET_ESCALATED,
            Notification.recipient_id == admin.id,
        ).all()
        assert len(notifications) == 1
        
        # Verify unique constraint prevents manual duplicate insert
        duplicate_record = EscalationRecord(
            ticket_id=ticket.id,
            event_type=EscalationEventType.RESPONSE_BREACH,
            rule_id=rule.id,
            recipient_id=admin.id,
        )
        db_session.add(duplicate_record)
        try:
            db_session.commit()
            assert False, "Should have raised IntegrityError for duplicate escalation record"
        except IntegrityError:
            db_session.rollback()
            # Expected - unique constraint prevents duplicates
            pass
        
        # Verify only one record still exists
        records = db_session.query(EscalationRecord).filter(
            EscalationRecord.ticket_id == ticket.id,
            EscalationRecord.event_type == EscalationEventType.RESPONSE_BREACH,
        ).all()
        assert len(records) == 1

    def test_concurrent_escalation_protection(self, db_session):
        """Test that unique constraint prevents concurrent duplicate escalations."""
        from app.services.escalation_service import (
            create_escalation_rule,
            EscalationEventType,
        )
        from app.models.escalation import EscalationRecord
        from app.models.ticket import Ticket
        from app.models.user import User
        from app.utils.security import hash_password
        from datetime import datetime, timezone
        from sqlalchemy.exc import IntegrityError
        
        admin = User(
            name="Admin Concurrent",
            email="admin_concurrent@example.com",
            password=hash_password("password123"),
            role="Admin",
        )
        db_session.add(admin)
        
        rule = create_escalation_rule(
            db=db_session,
            name="Concurrent Rule",
            event_type=EscalationEventType.RESPONSE_BREACH,
            priority="High",
            target_role="Admin",
        )
        
        ticket = Ticket(
            title="Concurrent Ticket",
            description="Test",
            priority="High",
            status="Open",
            ticket_type="INCIDENT",
            created_by=admin.id,
            sla_response_deadline=datetime.now(timezone.utc),
        )
        db_session.add(ticket)
        db_session.commit()
        
        # Try to create two escalation records for same ticket/event/rule
        record1 = EscalationRecord(
            ticket_id=ticket.id,
            event_type=EscalationEventType.RESPONSE_BREACH,
            rule_id=rule.id,
            recipient_id=admin.id,
        )
        db_session.add(record1)
        db_session.commit()
        
        # Second insert should fail due to unique constraint
        record2 = EscalationRecord(
            ticket_id=ticket.id,
            event_type=EscalationEventType.RESPONSE_BREACH,
            rule_id=rule.id,
            recipient_id=admin.id,
        )
        db_session.add(record2)
        
        try:
            db_session.commit()
            assert False, "Should have raised IntegrityError"
        except IntegrityError:
            db_session.rollback()
            # Expected - unique constraint prevents duplicates
            pass
        
        # Verify only one record exists
        records = db_session.query(EscalationRecord).filter(
            EscalationRecord.ticket_id == ticket.id,
            EscalationRecord.event_type == EscalationEventType.RESPONSE_BREACH,
        ).all()
        assert len(records) == 1