"""
Space management endpoint tests for EdutechHackathon API.

Tests all space endpoints according to the API specification:
- GET /folders/{folderId}/spaces - List spaces in folder  
- POST /folders/{folderId}/spaces - Create space
- GET /spaces/{id} - Retrieve space
- PATCH /spaces/{id} - Rename / update settings
- DELETE /spaces/{id} - Delete space
"""
import pytest
from fastapi import status
from fastapi.testclient import TestClient


class TestListSpaces:
    """Test list spaces endpoint."""
    
    def test_list_spaces_empty(self, client: TestClient, auth_headers, created_folder):
        """Test listing spaces when folder has none."""
        response = client.get(f"/api/v1/folders/{created_folder.id}/spaces", headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert "data" in data
        assert "meta" in data
        assert data["data"] == []
        assert data["meta"]["total"] == 0
        assert data["meta"]["page"] == 1
        assert data["meta"]["limit"] == 20
    
    def test_list_spaces_with_data(self, client: TestClient, auth_headers, created_folder, created_space):
        """Test listing spaces when folder has spaces."""
        response = client.get(f"/api/v1/folders/{created_folder.id}/spaces", headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert "data" in data
        assert "meta" in data
        assert len(data["data"]) == 1
        assert data["meta"]["total"] == 1
        
        space = data["data"][0]
        assert space["id"] == str(created_space.id)
        assert space["type"] == created_space.type.value
        assert space["title"] == created_space.title
        assert space["folderId"] == str(created_folder.id)
        assert "settings" in space
        assert "createdAt" in space
    
    def test_list_spaces_type_filter(self, client: TestClient, auth_headers, created_folder):
        """Test listing spaces with type filter."""
        # Create different types of spaces
        chat_space = {"type": "chat", "title": "Chat Space"}
        quiz_space = {"type": "quiz", "title": "Quiz Space"}
        notes_space = {"type": "notes", "title": "Notes Space"}
        
        client.post(f"/api/v1/folders/{created_folder.id}/spaces", json=chat_space, headers=auth_headers)
        client.post(f"/api/v1/folders/{created_folder.id}/spaces", json=quiz_space, headers=auth_headers)
        client.post(f"/api/v1/folders/{created_folder.id}/spaces", json=notes_space, headers=auth_headers)
        
        # Filter by chat type
        response = client.get(f"/api/v1/folders/{created_folder.id}/spaces?type=chat", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert len(data["data"]) == 1
        assert data["data"][0]["type"] == "chat"
        
        # Filter by quiz type
        response = client.get(f"/api/v1/folders/{created_folder.id}/spaces?type=quiz", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert len(data["data"]) == 1
        assert data["data"][0]["type"] == "quiz"
        
        # No filter should return all
        response = client.get(f"/api/v1/folders/{created_folder.id}/spaces", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert len(data["data"]) == 3
    
    def test_list_spaces_pagination(self, client: TestClient, auth_headers, created_folder):
        """Test space listing with pagination."""
        # Create multiple spaces
        for i in range(5):
            space_data = {"type": "chat", "title": f"Chat Space {i}"}
            client.post(f"/api/v1/folders/{created_folder.id}/spaces", json=space_data, headers=auth_headers)
        
        # Test pagination
        response = client.get(f"/api/v1/folders/{created_folder.id}/spaces?page=1&limit=3", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert len(data["data"]) == 3
        assert data["meta"]["page"] == 1
        assert data["meta"]["limit"] == 3
        assert data["meta"]["total"] == 5
        
        # Test second page
        response = client.get(f"/api/v1/folders/{created_folder.id}/spaces?page=2&limit=3", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert len(data["data"]) == 2  # Remaining spaces
        assert data["meta"]["page"] == 2
    
    def test_list_spaces_invalid_folder(self, client: TestClient, auth_headers):
        """Test listing spaces for non-existent folder."""
        fake_id = "123e4567-e89b-12d3-a456-426614174000"
        response = client.get(f"/api/v1/folders/{fake_id}/spaces", headers=auth_headers)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        
        data = response.json()
        assert "error" in data
    
    def test_list_spaces_no_auth(self, client: TestClient, created_folder):
        """Test listing spaces without authentication."""
        response = client.get(f"/api/v1/folders/{created_folder.id}/spaces")
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        
        data = response.json()
        assert "error" in data
    
    def test_list_spaces_other_user_folder(self, client: TestClient, sample_user_data_2, created_folder):
        """Test listing spaces for folder owned by another user."""
        # Register second user
        register_response = client.post("/api/v1/auth/register", json=sample_user_data_2)
        token_2 = register_response.json()["data"]["token"]
        headers_2 = {"Authorization": f"Bearer {token_2}"}
        
        # Try to list spaces in first user's folder
        response = client.get(f"/api/v1/folders/{created_folder.id}/spaces", headers=headers_2)
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
        
        data = response.json()
        assert "error" in data


class TestCreateSpace:
    """Test create space endpoint."""
    
    def test_create_space_chat(self, client: TestClient, auth_headers, created_folder):
        """Test creating a chat space."""
        space_data = {
            "type": "chat",
            "title": "My Chat Space",
            "settings": {"theme": "dark"}
        }
        
        response = client.post(f"/api/v1/folders/{created_folder.id}/spaces", 
                             json=space_data, headers=auth_headers)
        
        assert response.status_code == status.HTTP_201_CREATED
        
        data = response.json()
        assert "data" in data
        
        space = data["data"]
        assert space["type"] == "chat"
        assert space["title"] == "My Chat Space"
        assert space["folderId"] == str(created_folder.id)
        assert space["settings"]["theme"] == "dark"
        assert "id" in space
        assert "createdAt" in space
    
    def test_create_space_quiz(self, client: TestClient, auth_headers, created_folder):
        """Test creating a quiz space."""
        space_data = {
            "type": "quiz",
            "title": "Biology Quiz Space"
        }
        
        response = client.post(f"/api/v1/folders/{created_folder.id}/spaces", 
                             json=space_data, headers=auth_headers)
        
        assert response.status_code == status.HTTP_201_CREATED
        
        data = response.json()
        space = data["data"]
        assert space["type"] == "quiz"
        assert space["title"] == "Biology Quiz Space"
        assert space["settings"] == {} or space["settings"] is None
    
    def test_create_space_notes(self, client: TestClient, auth_headers, created_folder):
        """Test creating a notes space."""
        space_data = {
            "type": "notes",
            "title": "Study Notes Space"
        }
        
        response = client.post(f"/api/v1/folders/{created_folder.id}/spaces", 
                             json=space_data, headers=auth_headers)
        
        assert response.status_code == status.HTTP_201_CREATED
        
        data = response.json()
        space = data["data"]
        assert space["type"] == "notes"
        assert space["title"] == "Study Notes Space"
    
    def test_create_space_all_types(self, client: TestClient, auth_headers, created_folder):
        """Test creating all supported space types."""
        space_types = ["chat", "quiz", "notes", "openended", "flashcards", "studyguide"]
        
        for space_type in space_types:
            space_data = {
                "type": space_type,
                "title": f"Test {space_type.title()} Space"
            }
            
            response = client.post(f"/api/v1/folders/{created_folder.id}/spaces", 
                                 json=space_data, headers=auth_headers)
            
            assert response.status_code == status.HTTP_201_CREATED
            
            data = response.json()
            assert data["data"]["type"] == space_type
    
    def test_create_space_invalid_type(self, client: TestClient, auth_headers, created_folder):
        """Test creating space with invalid type."""
        space_data = {
            "type": "invalid_type",
            "title": "Invalid Space"
        }
        
        response = client.post(f"/api/v1/folders/{created_folder.id}/spaces", 
                             json=space_data, headers=auth_headers)
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_create_space_empty_title(self, client: TestClient, auth_headers, created_folder):
        """Test creating space with empty title."""
        space_data = {
            "type": "chat",
            "title": ""
        }
        
        response = client.post(f"/api/v1/folders/{created_folder.id}/spaces", 
                             json=space_data, headers=auth_headers)
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_create_space_long_title(self, client: TestClient, auth_headers, created_folder):
        """Test creating space with title exceeding maximum length."""
        space_data = {
            "type": "chat",
            "title": "x" * 256  # Exceeds 255 character limit
        }
        
        response = client.post(f"/api/v1/folders/{created_folder.id}/spaces", 
                             json=space_data, headers=auth_headers)
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_create_space_missing_required_fields(self, client: TestClient, auth_headers, created_folder):
        """Test creating space with missing required fields."""
        # Missing type
        response = client.post(f"/api/v1/folders/{created_folder.id}/spaces", 
                             json={"title": "Test Space"}, headers=auth_headers)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        
        # Missing title
        response = client.post(f"/api/v1/folders/{created_folder.id}/spaces", 
                             json={"type": "chat"}, headers=auth_headers)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_create_space_invalid_folder(self, client: TestClient, auth_headers):
        """Test creating space in non-existent folder."""
        fake_id = "123e4567-e89b-12d3-a456-426614174000"
        space_data = {"type": "chat", "title": "Test Space"}
        
        response = client.post(f"/api/v1/folders/{fake_id}/spaces", 
                             json=space_data, headers=auth_headers)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_create_space_no_auth(self, client: TestClient, created_folder, sample_space_data):
        """Test creating space without authentication."""
        response = client.post(f"/api/v1/folders/{created_folder.id}/spaces", json=sample_space_data)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_create_space_other_user_folder(self, client: TestClient, sample_user_data_2, created_folder):
        """Test creating space in folder owned by another user."""
        # Register second user
        register_response = client.post("/api/v1/auth/register", json=sample_user_data_2)
        token_2 = register_response.json()["data"]["token"]
        headers_2 = {"Authorization": f"Bearer {token_2}"}
        
        space_data = {"type": "chat", "title": "Unauthorized Space"}
        
        # Try to create space in first user's folder
        response = client.post(f"/api/v1/folders/{created_folder.id}/spaces", 
                             json=space_data, headers=headers_2)
        
        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestGetSpace:
    """Test get single space endpoint."""
    
    def test_get_space_success(self, client: TestClient, auth_headers, created_space):
        """Test successful space retrieval."""
        response = client.get(f"/api/v1/spaces/{created_space.id}", headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert "data" in data
        
        space = data["data"]
        assert space["id"] == str(created_space.id)
        assert space["type"] == created_space.type.value
        assert space["title"] == created_space.title
        assert space["folderId"] == str(created_space.folder_id)
        assert "settings" in space
        assert "createdAt" in space
    
    def test_get_space_not_found(self, client: TestClient, auth_headers):
        """Test getting non-existent space."""
        fake_id = "123e4567-e89b-12d3-a456-426614174000"
        response = client.get(f"/api/v1/spaces/{fake_id}", headers=auth_headers)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        
        data = response.json()
        assert "error" in data
    
    def test_get_space_invalid_id(self, client: TestClient, auth_headers):
        """Test getting space with invalid ID format."""
        response = client.get("/api/v1/spaces/invalid-id", headers=auth_headers)
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_get_space_no_auth(self, client: TestClient, created_space):
        """Test space retrieval without authentication."""
        response = client.get(f"/api/v1/spaces/{created_space.id}")
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        
        data = response.json()
        assert "error" in data
    
    def test_get_space_other_user(self, client: TestClient, sample_user_data_2, created_space):
        """Test accessing space owned by another user."""
        # Register second user
        register_response = client.post("/api/v1/auth/register", json=sample_user_data_2)
        token_2 = register_response.json()["data"]["token"]
        headers_2 = {"Authorization": f"Bearer {token_2}"}
        
        # Try to access first user's space
        response = client.get(f"/api/v1/spaces/{created_space.id}", headers=headers_2)
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
        
        data = response.json()
        assert "error" in data


class TestUpdateSpace:
    """Test update space endpoint."""
    
    def test_update_space_title(self, client: TestClient, auth_headers, created_space):
        """Test updating space title."""
        update_data = {"title": "Updated Space Title"}
        
        response = client.patch(f"/api/v1/spaces/{created_space.id}", 
                              json=update_data, headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        space = data["data"]
        assert space["title"] == "Updated Space Title"
        assert space["type"] == created_space.type.value  # Unchanged
    
    def test_update_space_settings(self, client: TestClient, auth_headers, created_space):
        """Test updating space settings."""
        update_data = {"settings": {"theme": "light", "notifications": True}}
        
        response = client.patch(f"/api/v1/spaces/{created_space.id}", 
                              json=update_data, headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        space = data["data"]
        assert space["settings"]["theme"] == "light"
        assert space["settings"]["notifications"] is True
        assert space["title"] == created_space.title  # Unchanged
    
    def test_update_space_both_fields(self, client: TestClient, auth_headers, created_space):
        """Test updating both title and settings."""
        update_data = {
            "title": "New Title",
            "settings": {"mode": "advanced"}
        }
        
        response = client.patch(f"/api/v1/spaces/{created_space.id}", 
                              json=update_data, headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        space = data["data"]
        assert space["title"] == "New Title"
        assert space["settings"]["mode"] == "advanced"
    
    def test_update_space_empty_title(self, client: TestClient, auth_headers, created_space):
        """Test updating space with empty title."""
        update_data = {"title": ""}
        
        response = client.patch(f"/api/v1/spaces/{created_space.id}", 
                              json=update_data, headers=auth_headers)
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_update_space_not_found(self, client: TestClient, auth_headers):
        """Test updating non-existent space."""
        fake_id = "123e4567-e89b-12d3-a456-426614174000"
        update_data = {"title": "New Title"}
        
        response = client.patch(f"/api/v1/spaces/{fake_id}", 
                              json=update_data, headers=auth_headers)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_update_space_no_auth(self, client: TestClient, created_space):
        """Test space update without authentication."""
        update_data = {"title": "New Title"}
        
        response = client.patch(f"/api/v1/spaces/{created_space.id}", json=update_data)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_update_space_other_user(self, client: TestClient, sample_user_data_2, created_space):
        """Test updating space owned by another user."""
        # Register second user
        register_response = client.post("/api/v1/auth/register", json=sample_user_data_2)
        token_2 = register_response.json()["data"]["token"]
        headers_2 = {"Authorization": f"Bearer {token_2}"}
        
        update_data = {"title": "Hacked Title"}
        
        # Try to update first user's space
        response = client.patch(f"/api/v1/spaces/{created_space.id}", 
                              json=update_data, headers=headers_2)
        
        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestDeleteSpace:
    """Test delete space endpoint."""
    
    def test_delete_space_success(self, client: TestClient, auth_headers, created_space):
        """Test successful space deletion."""
        response = client.delete(f"/api/v1/spaces/{created_space.id}", headers=auth_headers)
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert response.content == b""
        
        # Verify space is deleted
        get_response = client.get(f"/api/v1/spaces/{created_space.id}", headers=auth_headers)
        assert get_response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_delete_space_not_found(self, client: TestClient, auth_headers):
        """Test deleting non-existent space."""
        fake_id = "123e4567-e89b-12d3-a456-426614174000"
        
        response = client.delete(f"/api/v1/spaces/{fake_id}", headers=auth_headers)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_delete_space_no_auth(self, client: TestClient, created_space):
        """Test space deletion without authentication."""
        response = client.delete(f"/api/v1/spaces/{created_space.id}")
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_delete_space_other_user(self, client: TestClient, sample_user_data_2, created_space):
        """Test deleting space owned by another user."""
        # Register second user
        register_response = client.post("/api/v1/auth/register", json=sample_user_data_2)
        token_2 = register_response.json()["data"]["token"]
        headers_2 = {"Authorization": f"Bearer {token_2}"}
        
        # Try to delete first user's space
        response = client.delete(f"/api/v1/spaces/{created_space.id}", headers=headers_2)
        
        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestSpaceOwnership:
    """Test space ownership and access control."""
    
    def test_space_belongs_to_correct_folder(self, client: TestClient, auth_headers, created_user):
        """Test that spaces are properly associated with folders."""
        # Create two folders
        folder1_data = {"title": "Folder 1"}
        folder2_data = {"title": "Folder 2"}
        
        folder1_response = client.post("/api/v1/folders", json=folder1_data, headers=auth_headers)
        folder2_response = client.post("/api/v1/folders", json=folder2_data, headers=auth_headers)
        
        folder1_id = folder1_response.json()["data"]["id"]
        folder2_id = folder2_response.json()["data"]["id"]
        
        # Create space in folder 1
        space_data = {"type": "chat", "title": "Space in Folder 1"}
        space_response = client.post(f"/api/v1/folders/{folder1_id}/spaces", 
                                   json=space_data, headers=auth_headers)
        space_id = space_response.json()["data"]["id"]
        
        # Space should appear in folder 1 list
        list_response1 = client.get(f"/api/v1/folders/{folder1_id}/spaces", headers=auth_headers)
        assert len(list_response1.json()["data"]) == 1
        
        # Space should not appear in folder 2 list
        list_response2 = client.get(f"/api/v1/folders/{folder2_id}/spaces", headers=auth_headers)
        assert len(list_response2.json()["data"]) == 0
        
        # Space details should show correct folder_id
        space_response = client.get(f"/api/v1/spaces/{space_id}", headers=auth_headers)
        assert space_response.json()["data"]["folderId"] == folder1_id
    
    def test_user_isolation_spaces(self, client: TestClient, sample_user_data, sample_user_data_2):
        """Test that users can only see spaces in their own folders."""
        # Register two users
        register_response_1 = client.post("/api/v1/auth/register", json=sample_user_data)
        register_response_2 = client.post("/api/v1/auth/register", json=sample_user_data_2)
        
        token_1 = register_response_1.json()["data"]["token"]
        token_2 = register_response_2.json()["data"]["token"]
        
        headers_1 = {"Authorization": f"Bearer {token_1}"}
        headers_2 = {"Authorization": f"Bearer {token_2}"}
        
        # User 1 creates folder and space
        folder_data = {"title": "User 1 Folder"}
        folder_response = client.post("/api/v1/folders", json=folder_data, headers=headers_1)
        folder_id = folder_response.json()["data"]["id"]
        
        space_data = {"type": "chat", "title": "User 1 Space"}
        space_response = client.post(f"/api/v1/folders/{folder_id}/spaces", 
                                   json=space_data, headers=headers_1)
        space_id = space_response.json()["data"]["id"]
        
        # User 2 should not be able to access user 1's space
        get_response = client.get(f"/api/v1/spaces/{space_id}", headers=headers_2)
        assert get_response.status_code == status.HTTP_403_FORBIDDEN
        
        # User 2 should not be able to list spaces in user 1's folder
        list_response = client.get(f"/api/v1/folders/{folder_id}/spaces", headers=headers_2)
        assert list_response.status_code == status.HTTP_403_FORBIDDEN 