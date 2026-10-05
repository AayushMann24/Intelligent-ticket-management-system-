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