"""
Authentication tests for Strands GUI backend.
"""
import pytest
from httpx import AsyncClient

from app.core.security import verify_password, get_password_hash, create_access_token, decode_token
from app.models.user import User


class TestPasswordHashing:
    """Tests for password hashing utilities."""

    @pytest.mark.unit
    def test_password_hash_and_verify(self):
        """Test password hashing and verification."""
        password = "mysecretpassword123"
        hashed = get_password_hash(password)

        assert hashed != password
        assert verify_password(password, hashed)
        assert not verify_password("wrongpassword", hashed)

    @pytest.mark.unit
    def test_different_passwords_different_hashes(self):
        """Test that different passwords produce different hashes."""
        hash1 = get_password_hash("password1")
        hash2 = get_password_hash("password2")
        assert hash1 != hash2


class TestTokens:
    """Tests for JWT token utilities."""

    @pytest.mark.unit
    def test_create_and_decode_token(self):
        """Test token creation and decoding."""
        user_id = "123"
        token = create_access_token(data={"sub": user_id})

        assert token is not None
        assert isinstance(token, str)

        payload = decode_token(token)
        assert payload is not None
        assert payload.get("sub") == user_id

    @pytest.mark.unit
    def test_decode_invalid_token(self):
        """Test decoding an invalid token returns None."""
        result = decode_token("invalid.token.here")
        assert result is None

    @pytest.mark.unit
    def test_decode_empty_token(self):
        """Test decoding an empty token returns None."""
        result = decode_token("")
        assert result is None


class TestAuthEndpoints:
    """Tests for authentication API endpoints."""

    @pytest.mark.integration
    async def test_register_new_user(self, client: AsyncClient):
        """Test user registration."""
        response = await client.post(
            "/api/auth/register",
            json={
                "email": "newuser@example.com",
                "password": "securepassword123",
                "full_name": "New User",
            },
        )

        assert response.status_code == 201
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["user"]["email"] == "newuser@example.com"
        assert data["user"]["full_name"] == "New User"
        assert data["user"]["is_active"] is True

    @pytest.mark.integration
    async def test_register_duplicate_email(self, client: AsyncClient, test_user: User):
        """Test registration with existing email fails."""
        response = await client.post(
            "/api/auth/register",
            json={
                "email": test_user.email,
                "password": "anotherpassword123",
                "full_name": "Another User",
            },
        )

        assert response.status_code == 400
        assert "already registered" in response.json()["detail"].lower()

    @pytest.mark.integration
    async def test_register_short_password(self, client: AsyncClient):
        """Test registration with short password fails."""
        response = await client.post(
            "/api/auth/register",
            json={
                "email": "short@example.com",
                "password": "short",
                "full_name": "Short Password User",
            },
        )

        assert response.status_code == 422  # Validation error

    @pytest.mark.integration
    async def test_register_invalid_email(self, client: AsyncClient):
        """Test registration with invalid email fails."""
        response = await client.post(
            "/api/auth/register",
            json={
                "email": "notanemail",
                "password": "validpassword123",
                "full_name": "Invalid Email User",
            },
        )

        assert response.status_code == 422  # Validation error

    @pytest.mark.integration
    async def test_login_success(self, client: AsyncClient, db_session):
        """Test successful login."""
        # First register a user
        register_response = await client.post(
            "/api/auth/register",
            json={
                "email": "logintest@example.com",
                "password": "testpassword123",
                "full_name": "Login Test",
            },
        )
        assert register_response.status_code == 201

        # Then login
        response = await client.post(
            "/api/auth/login",
            json={
                "email": "logintest@example.com",
                "password": "testpassword123",
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["user"]["email"] == "logintest@example.com"

    @pytest.mark.integration
    async def test_login_wrong_password(self, client: AsyncClient, test_user: User):
        """Test login with wrong password fails."""
        response = await client.post(
            "/api/auth/login",
            json={
                "email": test_user.email,
                "password": "wrongpassword",
            },
        )

        assert response.status_code == 401
        assert "invalid" in response.json()["detail"].lower()

    @pytest.mark.integration
    async def test_login_nonexistent_user(self, client: AsyncClient):
        """Test login with non-existent user fails."""
        response = await client.post(
            "/api/auth/login",
            json={
                "email": "nonexistent@example.com",
                "password": "anypassword123",
            },
        )

        assert response.status_code == 401

    @pytest.mark.integration
    async def test_get_current_user(self, authenticated_client: AsyncClient, test_user: User):
        """Test getting current user info."""
        response = await authenticated_client.get("/api/auth/me")

        assert response.status_code == 200
        data = response.json()
        assert data["email"] == test_user.email
        assert data["id"] == test_user.id

    @pytest.mark.integration
    async def test_get_current_user_unauthorized(self, client: AsyncClient):
        """Test getting current user without auth fails."""
        response = await client.get("/api/auth/me")

        assert response.status_code == 403  # No Authorization header

    @pytest.mark.integration
    async def test_get_current_user_invalid_token(self, client: AsyncClient):
        """Test getting current user with invalid token fails."""
        client.headers["Authorization"] = "Bearer invalidtoken"
        response = await client.get("/api/auth/me")

        assert response.status_code == 401

    @pytest.mark.integration
    async def test_update_current_user(self, authenticated_client: AsyncClient, test_user: User):
        """Test updating current user info."""
        response = await authenticated_client.put(
            "/api/auth/me",
            json={"full_name": "Updated Name"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["full_name"] == "Updated Name"
        assert data["email"] == test_user.email  # Email unchanged


class TestTokenAuthentication:
    """Tests for token-based authentication flow."""

    @pytest.mark.integration
    async def test_full_auth_flow(self, client: AsyncClient):
        """Test complete authentication flow: register -> login -> access protected resource."""
        # Register
        register_response = await client.post(
            "/api/auth/register",
            json={
                "email": "flowtest@example.com",
                "password": "flowpassword123",
                "full_name": "Flow Test",
            },
        )
        assert register_response.status_code == 201
        token = register_response.json()["access_token"]

        # Access protected resource with token
        client.headers["Authorization"] = f"Bearer {token}"
        me_response = await client.get("/api/auth/me")
        assert me_response.status_code == 200
        assert me_response.json()["email"] == "flowtest@example.com"

        # Login with same credentials
        login_response = await client.post(
            "/api/auth/login",
            json={
                "email": "flowtest@example.com",
                "password": "flowpassword123",
            },
        )
        assert login_response.status_code == 200
        new_token = login_response.json()["access_token"]

        # Access with new token
        client.headers["Authorization"] = f"Bearer {new_token}"
        me_response2 = await client.get("/api/auth/me")
        assert me_response2.status_code == 200
