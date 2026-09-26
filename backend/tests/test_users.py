import pytest
from fastapi.testclient import TestClient


class TestUserEndpoints:
    def test_get_current_user(self, client, auth_headers, test_user):
        response = client.get("/users/me", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_user.id
        assert data["email"] == test_user.email
        assert data["name"] == test_user.name

    def test_get_users_as_admin(self, client, admin_auth_headers):
        response = client.get("/users/", headers=admin_auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data

    def test_get_users_as_non_admin(self, client, auth_headers):
        response = client.get("/users/", headers=auth_headers)
        assert response.status_code == 403

    def test_get_user_by_id(self, client, admin_auth_headers, test_user):
        response = client.get(f"/users/{test_user.id}", headers=admin_auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_user.id
        assert data["email"] == test_user.email

    def test_get_nonexistent_user(self, client, admin_auth_headers):
        response = client.get("/users/99999", headers=admin_auth_headers)
        assert response.status_code == 404

    def test_update_user_role_as_admin(self, client, admin_auth_headers, test_user):
        response = client.put(f"/users/{test_user.id}/role", json={
            "role": "Technician",
        }, headers=admin_auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["role"] == "Technician"

    def test_update_user_role_invalid(self, client, admin_auth_headers, test_user):
        response = client.put(f"/users/{test_user.id}/role", json={
            "role": "InvalidRole",
        }, headers=admin_auth_headers)
        assert response.status_code == 422

    def test_update_user_role_as_non_admin(self, client, auth_headers, test_user):
        response = client.put(f"/users/{test_user.id}/role", json={
            "role": "Admin",
        }, headers=auth_headers)
        assert response.status_code == 403


class TestUserPagination:
    def test_get_users_pagination(self, client, admin_auth_headers):
        response = client.get("/users/?page=1&page_size=5", headers=admin_auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["page"] == 1
        assert data["page_size"] == 5
        assert "total" in data
        assert "total_pages" in data

    def test_get_users_search(self, client, admin_auth_headers):
        response = client.get("/users/?search=test", headers=admin_auth_headers)
        assert response.status_code == 200

    def test_get_users_filter_role(self, client, admin_auth_headers):
        response = client.get("/users/?role=Admin", headers=admin_auth_headers)
        assert response.status_code == 200
        data = response.json()
        for user in data["items"]:
            assert user["role"] == "Admin"