"""
Authentication endpoint tests for EdutechHackathon API.

Tests all authentication endpoints according to the API specification:
- POST /auth/register - User registration
- POST /auth/login - User login  
- GET /auth/profile - Get current user profile
- POST /auth/logout - User logout
"""
import pytest
from fastapi import status
from fastapi.testclient import TestClient


class TestUserRegistration:
    """Test user registration endpoint."""
    
    def test_successful_registration(self, client: TestClient, sample_user_data):
        """Test successful user registration with valid data."""
        response = client.post("/api/v1/auth/register", json=sample_user_data)
        
        assert response.status_code == status.HTTP_201_CREATED
        
        data = response.json()
        assert "data" in data
        assert "user" in data["data"]
        assert "token" in data["data"]
        
        user = data["data"]["user"]
        assert user["email"] == sample_user_data["email"]
        assert user["name"] == sample_user_data["name"]
        assert "id" in user
        assert "created_at" in user
        assert "password" not in user  # Password should not be returned
        
        # Token should be a non-empty string
        assert isinstance(data["data"]["token"], str)
        assert len(data["data"]["token"]) > 0
    
    def test_duplicate_email_registration(self, client: TestClient, sample_user_data):
        """Test registration with email that already exists."""
        # First registration should succeed
        response1 = client.post("/api/v1/auth/register", json=sample_user_data)
        assert response1.status_code == status.HTTP_201_CREATED
        
        # Second registration with same email should fail
        response2 = client.post("/api/v1/auth/register", json=sample_user_data)
        assert response2.status_code == status.HTTP_400_BAD_REQUEST
        
        data = response2.json()
        assert "error" in data
        assert data["error"]["code"] == "EMAIL_ALREADY_EXISTS"
    
    def test_invalid_email_format(self, client: TestClient, sample_user_data):
        """Test registration with invalid email format."""
        invalid_data = sample_user_data.copy()
        invalid_data["email"] = "invalid-email"
        
        response = client.post("/api/v1/auth/register", json=invalid_data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        
        data = response.json()
        assert "detail" in data
        # FastAPI validation error for invalid email
        assert any("email" in str(error).lower() for error in data["detail"])
    
    def test_short_password(self, client: TestClient, sample_user_data):
        """Test registration with password shorter than 8 characters."""
        invalid_data = sample_user_data.copy()
        invalid_data["password"] = "1234567"  # 7 characters
        
        response = client.post("/api/v1/auth/register", json=invalid_data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        
        data = response.json()
        assert "detail" in data
        # Should mention password length requirement
        assert any("password" in str(error).lower() for error in data["detail"])
    
    def test_empty_name(self, client: TestClient, sample_user_data):
        """Test registration with empty name."""
        invalid_data = sample_user_data.copy()
        invalid_data["name"] = ""
        
        response = client.post("/api/v1/auth/register", json=invalid_data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        
        data = response.json()
        assert "detail" in data
        # Should mention name requirement
        assert any("name" in str(error).lower() for error in data["detail"])
    
    def test_missing_fields(self, client: TestClient):
        """Test registration with missing required fields."""
        # Missing email
        response = client.post("/api/v1/auth/register", json={
            "password": "password123",
            "name": "Test User"
        })
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        
        # Missing password
        response = client.post("/api/v1/auth/register", json={
            "email": "test@example.com",
            "name": "Test User"
        })
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        
        # Missing name
        response = client.post("/api/v1/auth/register", json={
            "email": "test@example.com",
            "password": "password123"
        })
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestUserLogin:
    """Test user login endpoint."""
    
    def test_successful_login(self, client: TestClient, created_user, sample_user_data):
        """Test successful login with valid credentials."""
        login_data = {
            "email": sample_user_data["email"],
            "password": sample_user_data["password"]
        }
        
        response = client.post("/api/v1/auth/login", json=login_data)
        
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert "data" in data
        assert "user" in data["data"]
        assert "token" in data["data"]
        
        user = data["data"]["user"]
        assert user["email"] == sample_user_data["email"]
        assert user["name"] == sample_user_data["name"]
        assert user["id"] == str(created_user.id)
        
        # Token should be a non-empty string
        assert isinstance(data["data"]["token"], str)
        assert len(data["data"]["token"]) > 0
    
    def test_invalid_email(self, client: TestClient, sample_user_data):
        """Test login with non-existent email."""
        login_data = {
            "email": "nonexistent@example.com",
            "password": sample_user_data["password"]
        }
        
        response = client.post("/api/v1/auth/login", json=login_data)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        
        data = response.json()
        assert "error" in data
        assert data["error"]["code"] == "INVALID_CREDENTIALS"
    
    def test_invalid_password(self, client: TestClient, created_user, sample_user_data):
        """Test login with incorrect password."""
        login_data = {
            "email": sample_user_data["email"],
            "password": "wrongpassword"
        }
        
        response = client.post("/api/v1/auth/login", json=login_data)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        
        data = response.json()
        assert "error" in data
        assert data["error"]["code"] == "INVALID_CREDENTIALS"
    
    def test_malformed_email(self, client: TestClient, sample_user_data):
        """Test login with malformed email."""
        login_data = {
            "email": "invalid-email",
            "password": sample_user_data["password"]
        }
        
        response = client.post("/api/v1/auth/login", json=login_data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_missing_credentials(self, client: TestClient):
        """Test login with missing email or password."""
        # Missing password
        response = client.post("/api/v1/auth/login", json={
            "email": "test@example.com"
        })
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        
        # Missing email
        response = client.post("/api/v1/auth/login", json={
            "password": "password123"
        })
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestUserProfile:
    """Test user profile endpoint."""
    
    def test_get_profile_success(self, client: TestClient, created_user, auth_headers, sample_user_data):
        """Test successful profile retrieval with valid token."""
        response = client.get("/api/v1/auth/profile", headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert "data" in data
        assert "user" in data["data"]
        
        user = data["data"]["user"]
        assert user["id"] == str(created_user.id)
        assert user["email"] == sample_user_data["email"]
        assert user["name"] == sample_user_data["name"]
        assert "created_at" in user
        assert "password" not in user  # Password should not be returned
    
    def test_get_profile_no_token(self, client: TestClient):
        """Test profile access without authentication token."""
        response = client.get("/api/v1/auth/profile")
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        
        data = response.json()
        assert "error" in data
    
    def test_get_profile_invalid_token(self, client: TestClient):
        """Test profile access with invalid token."""
        invalid_headers = {"Authorization": "Bearer invalid-token"}
        response = client.get("/api/v1/auth/profile", headers=invalid_headers)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        
        data = response.json()
        assert "error" in data
    
    def test_get_profile_malformed_header(self, client: TestClient):
        """Test profile access with malformed authorization header."""
        # Missing Bearer prefix
        invalid_headers = {"Authorization": "invalid-token"}
        response = client.get("/api/v1/auth/profile", headers=invalid_headers)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        
        # Empty authorization header
        invalid_headers = {"Authorization": ""}
        response = client.get("/api/v1/auth/profile", headers=invalid_headers)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestUserLogout:
    """Test user logout endpoint."""
    
    def test_successful_logout(self, client: TestClient, auth_headers):
        """Test successful logout with valid token."""
        response = client.post("/api/v1/auth/logout", headers=auth_headers)
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert response.content == b""  # No content for 204
    
    def test_logout_no_token(self, client: TestClient):
        """Test logout without authentication token."""
        response = client.post("/api/v1/auth/logout")
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        
        data = response.json()
        assert "error" in data
    
    def test_logout_invalid_token(self, client: TestClient):
        """Test logout with invalid token."""
        invalid_headers = {"Authorization": "Bearer invalid-token"}
        response = client.post("/api/v1/auth/logout", headers=invalid_headers)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        
        data = response.json()
        assert "error" in data
    
    def test_token_blacklisted_after_logout(self, client: TestClient, auth_headers):
        """Test that token is blacklisted after logout."""
        # First, verify profile access works
        response = client.get("/api/v1/auth/profile", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        
        # Logout
        response = client.post("/api/v1/auth/logout", headers=auth_headers)
        assert response.status_code == status.HTTP_204_NO_CONTENT
        
        # Try to access profile again with same token (should fail)
        response = client.get("/api/v1/auth/profile", headers=auth_headers)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestAuthenticationFlow:
    """Test complete authentication flows."""
    
    def test_complete_auth_flow(self, client: TestClient, sample_user_data):
        """Test complete authentication flow: register -> login -> profile -> logout."""
        # Register
        register_response = client.post("/api/v1/auth/register", json=sample_user_data)
        assert register_response.status_code == status.HTTP_201_CREATED
        
        register_token = register_response.json()["data"]["token"]
        register_headers = {"Authorization": f"Bearer {register_token}"}
        
        # Get profile with registration token
        profile_response = client.get("/api/v1/auth/profile", headers=register_headers)
        assert profile_response.status_code == status.HTTP_200_OK
        
        # Login
        login_data = {
            "email": sample_user_data["email"],
            "password": sample_user_data["password"]
        }
        login_response = client.post("/api/v1/auth/login", json=login_data)
        assert login_response.status_code == status.HTTP_200_OK
        
        login_token = login_response.json()["data"]["token"]
        login_headers = {"Authorization": f"Bearer {login_token}"}
        
        # Get profile with login token
        profile_response = client.get("/api/v1/auth/profile", headers=login_headers)
        assert profile_response.status_code == status.HTTP_200_OK
        
        # Logout
        logout_response = client.post("/api/v1/auth/logout", headers=login_headers)
        assert logout_response.status_code == status.HTTP_204_NO_CONTENT
        
        # Verify token is invalidated
        profile_response = client.get("/api/v1/auth/profile", headers=login_headers)
        assert profile_response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_multiple_user_isolation(self, client: TestClient, sample_user_data, sample_user_data_2):
        """Test that multiple users are properly isolated."""
        # Register two users
        register_response_1 = client.post("/api/v1/auth/register", json=sample_user_data)
        register_response_2 = client.post("/api/v1/auth/register", json=sample_user_data_2)
        
        assert register_response_1.status_code == status.HTTP_201_CREATED
        assert register_response_2.status_code == status.HTTP_201_CREATED
        
        token_1 = register_response_1.json()["data"]["token"]
        token_2 = register_response_2.json()["data"]["token"]
        
        headers_1 = {"Authorization": f"Bearer {token_1}"}
        headers_2 = {"Authorization": f"Bearer {token_2}"}
        
        # Each user should see their own profile
        profile_1 = client.get("/api/v1/auth/profile", headers=headers_1)
        profile_2 = client.get("/api/v1/auth/profile", headers=headers_2)
        
        assert profile_1.status_code == status.HTTP_200_OK
        assert profile_2.status_code == status.HTTP_200_OK
        
        user_1_data = profile_1.json()["data"]["user"]
        user_2_data = profile_2.json()["data"]["user"]
        
        assert user_1_data["email"] == sample_user_data["email"]
        assert user_2_data["email"] == sample_user_data_2["email"]
        assert user_1_data["id"] != user_2_data["id"] 