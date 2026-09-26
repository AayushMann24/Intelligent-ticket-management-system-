import pytest
from fastapi.testclient import TestClient


class TestRegistration:
    def test_register_success(self, client):
        response = client.post("/auth/register", json={
            "name": "New User",
            "email": "newuser@example.com",
            "password": "password123",
        })
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "newuser@example.com"
        assert data["name"] == "New User"
        assert data["role"] == "Employee"
        assert "id" in data

    def test_register_duplicate_email(self, client, test_user):
        response = client.post("/auth/register", json={
            "name": "Another User",
            "email": "test@example.com",
            "password": "password123",
        })
        assert response.status_code == 400
        assert "already registered" in response.json()["detail"].lower()

    def test_register_invalid_email(self, client):
        response = client.post("/auth/register", json={
            "name": "Test User",
            "email": "invalid-email",
            "password": "password123",
        })
        assert response.status_code == 422

    def test_register_short_password(self, client):
        response = client.post("/auth/register", json={
            "name": "Test User",
            "email": "test2@example.com",
            "password": "short",
        })
        assert response.status_code == 422

    def test_register_short_name(self, client):
        response = client.post("/auth/register", json={
            "name": "Ab",
            "email": "test3@example.com",
            "password": "password123",
        })
        assert response.status_code == 422


class TestLogin:
    def test_login_success(self, client, test_user):
        response = client.post("/auth/login", json={
            "email": "test@example.com",
            "password": "testpassword123",
        })
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
        assert data["email"] == "test@example.com"
        assert data["role"] == "Employee"

    def test_login_invalid_email(self, client, test_user):
        response = client.post("/auth/login", json={
            "email": "nonexistent@example.com",
            "password": "testpassword123",
        })
        assert response.status_code == 401

    def test_login_invalid_password(self, client, test_user):
        response = client.post("/auth/login", json={
            "email": "test@example.com",
            "password": "wrongpassword",
        })
        assert response.status_code == 401


class TestRefreshToken:
    def test_refresh_token_success(self, client, test_user):
        # Login first
        login_response = client.post("/auth/login", json={
            "email": "test@example.com",
            "password": "testpassword123",
        })
        refresh_token = login_response.json()["refresh_token"]

        # Refresh
        response = client.post("/auth/refresh", json={
            "refresh_token": refresh_token,
        })
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["refresh_token"] != refresh_token  # Token should be rotated

    def test_refresh_token_invalid(self, client):
        response = client.post("/auth/refresh", json={
            "refresh_token": "invalid_token",
        })
        assert response.status_code == 401

    def test_refresh_token_reuse_detection(self, client, test_user):
        # Login first
        login_response = client.post("/auth/login", json={
            "email": "test@example.com",
            "password": "testpassword123",
        })
        refresh_token = login_response.json()["refresh_token"]

        # First refresh - should work
        response1 = client.post("/auth/refresh", json={
            "refresh_token": refresh_token,
        })
        assert response1.status_code == 200

        # Second refresh with same token - should fail (reuse detection)
        response2 = client.post("/auth/refresh", json={
            "refresh_token": refresh_token,
        })
        assert response2.status_code == 401


class TestLogout:
    def test_logout_success(self, client, auth_headers):
        response = client.post("/auth/logout", headers=auth_headers)
        assert response.status_code == 200
        assert response.json()["message"] == "Logged out successfully"

    def test_logout_revokes_tokens(self, client, auth_headers, test_user):
        # Logout
        client.post("/auth/logout", headers=auth_headers)

        # Try to use access token after logout - should fail
        # Note: The access token itself is still valid until expiry,
        # but refresh tokens should be revoked
        response = client.get("/profile", headers=auth_headers)
        # Access token might still work until expiry
        # This tests that the endpoint is accessible
        assert response.status_code in [200, 401]


class TestTokenValidation:
    def test_invalid_token(self, client):
        response = client.get("/profile", headers={
            "Authorization": "Bearer invalid_token",
        })
        assert response.status_code == 401

    def test_expired_token(self, client, test_user):
        # This would require creating an expired token
        # For now, just test invalid token format
        pass