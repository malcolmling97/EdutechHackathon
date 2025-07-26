"""
Folder management endpoint tests for EdutechHackathon API.

Tests all folder endpoints according to the API specification:
- GET /folders - List user folders
- POST /folders - Create folder
- GET /folders/{id} - Retrieve folder
- PATCH /folders/{id} - Update metadata
- DELETE /folders/{id} - Delete folder (+ cascade)
"""
import pytest
from fastapi import status
from fastapi.testclient import TestClient


class TestListFolders:
    """Test list folders endpoint."""
    
    def test_list_folders_empty(self, client: TestClient, auth_headers):
        """Test listing folders when user has none."""
        response = client.get("/api/v1/folders", headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert "data" in data
        assert "meta" in data
        assert data["data"] == []
        assert data["meta"]["total"] == 0
        assert data["meta"]["page"] == 1
        assert data["meta"]["limit"] == 20
    
    def test_list_folders_with_data(self, client: TestClient, auth_headers, created_folder):
        """Test listing folders when user has folders."""
        response = client.get("/api/v1/folders", headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert "data" in data
        assert "meta" in data
        assert len(data["data"]) == 1
        assert data["meta"]["total"] == 1
        
        folder = data["data"][0]
        assert folder["id"] == str(created_folder.id)
        assert folder["title"] == created_folder.title
        assert folder["description"] == created_folder.description
        assert "ownerId" in folder
        assert "createdAt" in folder
    
    def test_list_folders_pagination(self, client: TestClient, auth_headers):
        """Test folder listing with pagination parameters."""
        # Create multiple folders first
        for i in range(5):
            folder_data = {
                "title": f"Test Folder {i}",
                "description": f"Description {i}"
            }
            client.post("/api/v1/folders", json=folder_data, headers=auth_headers)
        
        # Test pagination
        response = client.get("/api/v1/folders?page=1&limit=3", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert len(data["data"]) == 3
        assert data["meta"]["page"] == 1
        assert data["meta"]["limit"] == 3
        assert data["meta"]["total"] == 5
        
        # Test second page
        response = client.get("/api/v1/folders?page=2&limit=3", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert len(data["data"]) == 2  # Remaining folders
        assert data["meta"]["page"] == 2
    
    def test_list_folders_search(self, client: TestClient, auth_headers):
        """Test folder search functionality."""
        # Create folders with different titles
        folder_data_1 = {"title": "Biology Notes", "description": "Bio description"}
        folder_data_2 = {"title": "Chemistry Lab", "description": "Chem description"}
        folder_data_3 = {"title": "Physics Problems", "description": "Bio related physics"}
        
        client.post("/api/v1/folders", json=folder_data_1, headers=auth_headers)
        client.post("/api/v1/folders", json=folder_data_2, headers=auth_headers)
        client.post("/api/v1/folders", json=folder_data_3, headers=auth_headers)
        
        # Search for "bio"
        response = client.get("/api/v1/folders?q=bio", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert len(data["data"]) == 2  # Biology Notes and Physics Problems (bio in description)
        
        # Search for "chemistry"
        response = client.get("/api/v1/folders?q=chemistry", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert len(data["data"]) == 1
        assert "Chemistry" in data["data"][0]["title"]
    
    def test_list_folders_no_auth(self, client: TestClient):
        """Test folder listing without authentication."""
        response = client.get("/api/v1/folders")
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        
        data = response.json()
        assert "error" in data
    
    def test_list_folders_invalid_pagination(self, client: TestClient, auth_headers):
        """Test folder listing with invalid pagination parameters."""
        # Invalid page number (0)
        response = client.get("/api/v1/folders?page=0", headers=auth_headers)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        
        # Invalid limit (too high)
        response = client.get("/api/v1/folders?limit=101", headers=auth_headers)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        
        # Invalid limit (0)
        response = client.get("/api/v1/folders?limit=0", headers=auth_headers)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestCreateFolder:
    """Test create folder endpoint."""
    
    def test_create_folder_success(self, client: TestClient, auth_headers, sample_folder_data):
        """Test successful folder creation."""
        response = client.post("/api/v1/folders", json=sample_folder_data, headers=auth_headers)
        
        assert response.status_code == status.HTTP_201_CREATED
        
        data = response.json()
        assert "data" in data
        
        folder = data["data"]
        assert folder["title"] == sample_folder_data["title"]
        assert folder["description"] == sample_folder_data["description"]
        assert "id" in folder
        assert "ownerId" in folder
        assert "createdAt" in folder
    
    def test_create_folder_minimal_data(self, client: TestClient, auth_headers):
        """Test folder creation with minimal required data."""
        folder_data = {"title": "Minimal Folder"}
        
        response = client.post("/api/v1/folders", json=folder_data, headers=auth_headers)
        
        assert response.status_code == status.HTTP_201_CREATED
        
        data = response.json()
        folder = data["data"]
        assert folder["title"] == "Minimal Folder"
        assert folder["description"] is None or folder["description"] == ""
    
    def test_create_folder_with_description(self, client: TestClient, auth_headers):
        """Test folder creation with description."""
        folder_data = {
            "title": "Detailed Folder",
            "description": "This is a detailed description of the folder"
        }
        
        response = client.post("/api/v1/folders", json=folder_data, headers=auth_headers)
        
        assert response.status_code == status.HTTP_201_CREATED
        
        data = response.json()
        folder = data["data"]
        assert folder["title"] == folder_data["title"]
        assert folder["description"] == folder_data["description"]
    
    def test_create_folder_empty_title(self, client: TestClient, auth_headers):
        """Test folder creation with empty title."""
        folder_data = {"title": "", "description": "Description"}
        
        response = client.post("/api/v1/folders", json=folder_data, headers=auth_headers)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        
        data = response.json()
        assert "detail" in data
    
    def test_create_folder_long_title(self, client: TestClient, auth_headers):
        """Test folder creation with title exceeding maximum length."""
        folder_data = {"title": "x" * 256}  # Exceeds 255 character limit
        
        response = client.post("/api/v1/folders", json=folder_data, headers=auth_headers)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_create_folder_long_description(self, client: TestClient, auth_headers):
        """Test folder creation with description exceeding maximum length."""
        folder_data = {
            "title": "Test Folder",
            "description": "x" * 1001  # Exceeds 1000 character limit
        }
        
        response = client.post("/api/v1/folders", json=folder_data, headers=auth_headers)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_create_folder_missing_title(self, client: TestClient, auth_headers):
        """Test folder creation without title."""
        folder_data = {"description": "Description without title"}
        
        response = client.post("/api/v1/folders", json=folder_data, headers=auth_headers)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_create_folder_no_auth(self, client: TestClient, sample_folder_data):
        """Test folder creation without authentication."""
        response = client.post("/api/v1/folders", json=sample_folder_data)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        
        data = response.json()
        assert "error" in data


class TestGetFolder:
    """Test get single folder endpoint."""
    
    def test_get_folder_success(self, client: TestClient, auth_headers, created_folder):
        """Test successful folder retrieval."""
        response = client.get(f"/api/v1/folders/{created_folder.id}", headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert "data" in data
        
        folder = data["data"]
        assert folder["id"] == str(created_folder.id)
        assert folder["title"] == created_folder.title
        assert folder["description"] == created_folder.description
        assert "ownerId" in folder
        assert "createdAt" in folder
    
    def test_get_folder_not_found(self, client: TestClient, auth_headers):
        """Test getting non-existent folder."""
        fake_id = "123e4567-e89b-12d3-a456-426614174000"
        response = client.get(f"/api/v1/folders/{fake_id}", headers=auth_headers)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        
        data = response.json()
        assert "error" in data
    
    def test_get_folder_invalid_id(self, client: TestClient, auth_headers):
        """Test getting folder with invalid ID format."""
        response = client.get("/api/v1/folders/invalid-id", headers=auth_headers)
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_get_folder_no_auth(self, client: TestClient, created_folder):
        """Test folder retrieval without authentication."""
        response = client.get(f"/api/v1/folders/{created_folder.id}")
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        
        data = response.json()
        assert "error" in data
    
    def test_get_folder_other_user(self, client: TestClient, sample_user_data_2, created_folder):
        """Test accessing folder owned by another user."""
        # Register second user
        register_response = client.post("/api/v1/auth/register", json=sample_user_data_2)
        token_2 = register_response.json()["data"]["token"]
        headers_2 = {"Authorization": f"Bearer {token_2}"}
        
        # Try to access first user's folder
        response = client.get(f"/api/v1/folders/{created_folder.id}", headers=headers_2)
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
        
        data = response.json()
        assert "error" in data


class TestUpdateFolder:
    """Test update folder endpoint."""
    
    def test_update_folder_title(self, client: TestClient, auth_headers, created_folder):
        """Test updating folder title."""
        update_data = {"title": "Updated Title"}
        
        response = client.patch(f"/api/v1/folders/{created_folder.id}", 
                              json=update_data, headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        folder = data["data"]
        assert folder["title"] == "Updated Title"
        assert folder["description"] == created_folder.description  # Unchanged
    
    def test_update_folder_description(self, client: TestClient, auth_headers, created_folder):
        """Test updating folder description."""
        update_data = {"description": "Updated description"}
        
        response = client.patch(f"/api/v1/folders/{created_folder.id}", 
                              json=update_data, headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        folder = data["data"]
        assert folder["description"] == "Updated description"
        assert folder["title"] == created_folder.title  # Unchanged
    
    def test_update_folder_both_fields(self, client: TestClient, auth_headers, created_folder):
        """Test updating both title and description."""
        update_data = {
            "title": "New Title",
            "description": "New description"
        }
        
        response = client.patch(f"/api/v1/folders/{created_folder.id}", 
                              json=update_data, headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        folder = data["data"]
        assert folder["title"] == "New Title"
        assert folder["description"] == "New description"
    
    def test_update_folder_empty_title(self, client: TestClient, auth_headers, created_folder):
        """Test updating folder with empty title."""
        update_data = {"title": ""}
        
        response = client.patch(f"/api/v1/folders/{created_folder.id}", 
                              json=update_data, headers=auth_headers)
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_update_folder_not_found(self, client: TestClient, auth_headers):
        """Test updating non-existent folder."""
        fake_id = "123e4567-e89b-12d3-a456-426614174000"
        update_data = {"title": "New Title"}
        
        response = client.patch(f"/api/v1/folders/{fake_id}", 
                              json=update_data, headers=auth_headers)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_update_folder_no_auth(self, client: TestClient, created_folder):
        """Test folder update without authentication."""
        update_data = {"title": "New Title"}
        
        response = client.patch(f"/api/v1/folders/{created_folder.id}", json=update_data)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_update_folder_other_user(self, client: TestClient, sample_user_data_2, created_folder):
        """Test updating folder owned by another user."""
        # Register second user
        register_response = client.post("/api/v1/auth/register", json=sample_user_data_2)
        token_2 = register_response.json()["data"]["token"]
        headers_2 = {"Authorization": f"Bearer {token_2}"}
        
        update_data = {"title": "Hacked Title"}
        
        # Try to update first user's folder
        response = client.patch(f"/api/v1/folders/{created_folder.id}", 
                              json=update_data, headers=headers_2)
        
        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestDeleteFolder:
    """Test delete folder endpoint."""
    
    def test_delete_folder_success(self, client: TestClient, auth_headers, created_folder):
        """Test successful folder deletion."""
        response = client.delete(f"/api/v1/folders/{created_folder.id}", headers=auth_headers)
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert response.content == b""
        
        # Verify folder is deleted
        get_response = client.get(f"/api/v1/folders/{created_folder.id}", headers=auth_headers)
        assert get_response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_delete_folder_not_found(self, client: TestClient, auth_headers):
        """Test deleting non-existent folder."""
        fake_id = "123e4567-e89b-12d3-a456-426614174000"
        
        response = client.delete(f"/api/v1/folders/{fake_id}", headers=auth_headers)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_delete_folder_no_auth(self, client: TestClient, created_folder):
        """Test folder deletion without authentication."""
        response = client.delete(f"/api/v1/folders/{created_folder.id}")
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_delete_folder_other_user(self, client: TestClient, sample_user_data_2, created_folder):
        """Test deleting folder owned by another user."""
        # Register second user
        register_response = client.post("/api/v1/auth/register", json=sample_user_data_2)
        token_2 = register_response.json()["data"]["token"]
        headers_2 = {"Authorization": f"Bearer {token_2}"}
        
        # Try to delete first user's folder
        response = client.delete(f"/api/v1/folders/{created_folder.id}", headers=headers_2)
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_delete_folder_cascade(self, client: TestClient, auth_headers, created_folder, created_space):
        """Test that folder deletion cascades to spaces and files."""
        # Verify space exists first
        space_response = client.get(f"/api/v1/spaces/{created_space.id}", headers=auth_headers)
        assert space_response.status_code == status.HTTP_200_OK
        
        # Delete folder
        response = client.delete(f"/api/v1/folders/{created_folder.id}", headers=auth_headers)
        assert response.status_code == status.HTTP_204_NO_CONTENT
        
        # Verify space is also deleted (cascade)
        # Note: Returns 403 instead of 404 for security (doesn't leak resource existence)
        space_response = client.get(f"/api/v1/spaces/{created_space.id}", headers=auth_headers)
        assert space_response.status_code == status.HTTP_403_FORBIDDEN


class TestFolderOwnership:
    """Test folder ownership and access control."""
    
    def test_user_isolation(self, client: TestClient, sample_user_data, sample_user_data_2):
        """Test that users can only see their own folders."""
        # Register two users
        register_response_1 = client.post("/api/v1/auth/register", json=sample_user_data)
        register_response_2 = client.post("/api/v1/auth/register", json=sample_user_data_2)
        
        token_1 = register_response_1.json()["data"]["token"]
        token_2 = register_response_2.json()["data"]["token"]
        
        headers_1 = {"Authorization": f"Bearer {token_1}"}
        headers_2 = {"Authorization": f"Bearer {token_2}"}
        
        # User 1 creates a folder
        folder_data = {"title": "User 1 Folder"}
        create_response = client.post("/api/v1/folders", json=folder_data, headers=headers_1)
        assert create_response.status_code == status.HTTP_201_CREATED
        
        # User 2 creates a folder
        folder_data_2 = {"title": "User 2 Folder"}
        create_response_2 = client.post("/api/v1/folders", json=folder_data_2, headers=headers_2)
        assert create_response_2.status_code == status.HTTP_201_CREATED
        
        # User 1 should only see their folder
        list_response_1 = client.get("/api/v1/folders", headers=headers_1)
        assert list_response_1.status_code == status.HTTP_200_OK
        
        data_1 = list_response_1.json()
        assert len(data_1["data"]) == 1
        assert data_1["data"][0]["title"] == "User 1 Folder"
        
        # User 2 should only see their folder
        list_response_2 = client.get("/api/v1/folders", headers=headers_2)
        assert list_response_2.status_code == status.HTTP_200_OK
        
        data_2 = list_response_2.json()
        assert len(data_2["data"]) == 1
        assert data_2["data"][0]["title"] == "User 2 Folder" 