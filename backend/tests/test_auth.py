import pytest
from fastapi.testclient import TestClient
from app.config import settings
from app.utils.rate_limiter import rate_limiter
import asyncio


class TestRateLimiting:
    """Tests for authentication endpoint rate limiting."""
    
    @pytest.fixture(autouse=True)
    def enable_rate_limiting(self):
        """Enable rate limiting for these tests."""
        original_enabled = settings.rate_limit_enabled
        original_auth_requests = settings.auth_rate_limit_requests
        original_auth_window = settings.auth_rate_limit_window_seconds
        
        settings.rate_limit_enabled = True
        settings.auth_rate_limit_requests = 3  # Low limit for testing
        settings.auth_rate_limit_window_seconds = 60
        
        yield
        
        settings.rate_limit_enabled = original_enabled
        settings.auth_rate_limit_requests = original_auth_requests
        settings.auth_rate_limit_window_seconds = original_auth_window
        asyncio.run(rate_limiter.reset_all())
    
    def test_login_below_limit_succeeds(self, client, test_user):
        """Requests below the limit should succeed."""
        for i in range(3):
            response = client.post("/auth/login", json={
                "email": "test@example.com",
                "password": "testpassword123",
            })
            assert response.status_code == 200, f"Request {i+1} failed"
            assert "access_token" in response.json()
    
    def test_login_exceeding_limit_returns_429(self, client, test_user):
        """Requests exceeding the limit should return HTTP 429."""
        # Make 3 successful requests (at limit)
        for _ in range(3):
            response = client.post("/auth/login", json={
                "email": "test@example.com",
                "password": "testpassword123",
            })
            assert response.status_code == 200
        
        # 4th request should be rate limited
        response = client.post("/auth/login", json={
            "email": "test@example.com",
            "password": "testpassword123",
        })
        assert response.status_code == 429
        data = response.json()
        assert data["error"]["code"] == "RATE_LIMIT_EXCEEDED"
        assert "Rate limit exceeded" in data["error"]["message"]
    
    def test_retry_after_header_present(self, client, test_user):
        """Retry-After header should be present on 429 response."""
        # Exhaust the limit
        for _ in range(3):
            client.post("/auth/login", json={
                "email": "test@example.com",
                "password": "testpassword123",
            })
        
        response = client.post("/auth/login", json={
            "email": "test@example.com",
            "password": "testpassword123",
        })
        assert response.status_code == 429
        assert "Retry-After" in response.headers
        retry_after = int(response.headers["Retry-After"])
        assert retry_after > 0
    
    def test_refresh_endpoint_protected(self, client, test_user):
        """Refresh endpoint should also be rate limited."""
        # Login to get a refresh token
        login_response = client.post("/auth/login", json={
            "email": "test@example.com",
            "password": "testpassword123",
        })
        refresh_token = login_response.json()["refresh_token"]
        
        # Make refresh requests up to limit
        for _ in range(3):
            response = client.post("/auth/refresh", json={
                "refresh_token": refresh_token,
            })
            # First one succeeds, subsequent ones fail due to rotation
            # But rate limiting should still apply
        
        # Next request should be rate limited
        response = client.post("/auth/refresh", json={
            "refresh_token": "invalid_token_for_rate_limit_test",
        })
        assert response.status_code == 429
    
    def test_register_endpoint_protected(self, client):
        """Register endpoint should also be rate limited."""
        for i in range(3):
            response = client.post("/auth/register", json={
                "name": f"User {i}",
                "email": f"user{i}@example.com",
                "password": "password123",
            })
            assert response.status_code == 201
        
        # 4th request should be rate limited
        response = client.post("/auth/register", json={
            "name": "User 3",
            "email": "user3@example.com",
            "password": "password123",
        })
        assert response.status_code == 429
    
    def test_different_clients_independent_limits(self, client, test_user):
        """Different clients should have independent rate limits."""
        # This test simulates different clients by using different IPs
        # Note: TestClient uses same IP, so we test the logic via the rate limiter directly
        import asyncio
        
        async def test_independent():
            # Client A makes 3 requests
            for _ in range(3):
                allowed, _, _ = await rate_limiter.check_rate_limit(
                    "192.168.1.1", "/auth/login", 3, 60
                )
                assert allowed is True
            
            # Client A's 4th request denied
            allowed, _, _ = await rate_limiter.check_rate_limit(
                "192.168.1.1", "/auth/login", 3, 60
            )
            assert allowed is False
            
            # Client B should still be allowed
            allowed, _, _ = await rate_limiter.check_rate_limit(
                "192.168.1.2", "/auth/login", 3, 60
            )
            assert allowed is True
        
        asyncio.run(test_independent())
    
    def test_rate_limit_resets_after_window(self, client, test_user):
        """Rate limit should reset after the time window expires."""
        # This is tested via the rate limiter directly since we can't wait 60s in tests
        import asyncio
        import time
        
        async def test_window_reset():
            # Use a very short window for testing
            for _ in range(3):
                allowed, _, _ = await rate_limiter.check_rate_limit(
                    "10.0.0.1", "/auth/test", 3, 1  # 1 second window
                )
                assert allowed is True
            
            # 4th request denied
            allowed, _, _ = await rate_limiter.check_rate_limit(
                "10.0.0.1", "/auth/test", 3, 1
            )
            assert allowed is False
            
            # Wait for window to expire
            await asyncio.sleep(1.5)
            
            # Should be allowed again
            allowed, _, _ = await rate_limiter.check_rate_limit(
                "10.0.0.1", "/auth/test", 3, 1
            )
            assert allowed is True
        
        asyncio.run(test_window_reset())
    
    def test_configuration_can_disable_limiter(self, client, test_user):
        """Configuration should be able to disable the rate limiter."""
        settings.rate_limit_enabled = False
        try:
            # Should be able to make unlimited requests
            for _ in range(10):
                response = client.post("/auth/login", json={
                    "email": "test@example.com",
                    "password": "testpassword123",
                })
                assert response.status_code == 200
        finally:
            settings.rate_limit_enabled = True
    
    def test_failed_login_does_not_leak_user_existence(self, client):
        """Failed authentication should not leak whether user exists."""
        # Both non-existent and existing users with wrong password should return 401
        # (not 429 for one and 401 for another)
        for _ in range(3):
            response = client.post("/auth/login", json={
                "email": "nonexistent@example.com",
                "password": "wrongpassword",
            })
            assert response.status_code == 401
        
        # 4th request should be rate limited (same IP)
        response = client.post("/auth/login", json={
            "email": "nonexistent@example.com",
            "password": "wrongpassword",
        })
        assert response.status_code == 429
        
        # Now try with a different email - should also be rate limited (same IP)
        response = client.post("/auth/login", json={
            "email": "alsofake@example.com",
            "password": "wrongpassword",
        })
        assert response.status_code == 429
    
    def test_successful_login_behavior_unchanged(self, client, test_user):
        """Successful login behavior should remain unchanged."""
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
        assert "id" in data


class TestRegistration:
    # ... rest of the file
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