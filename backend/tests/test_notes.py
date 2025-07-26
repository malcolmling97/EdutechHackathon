"""
Notes management endpoint tests for EdutechHackathon API.

Tests all notes endpoints according to the API specification:
- POST /spaces/{spaceId}/notes - Generate notes
- GET /spaces/{spaceId}/notes - List notes  
- GET /notes/{id} - Retrieve note
- PATCH /notes/{id} - Update content
- DELETE /notes/{id} - Delete note
"""
import pytest
from fastapi import status
from fastapi.testclient import TestClient


class TestGenerateNotes:
    """Test notes generation endpoint."""
    
    def test_generate_notes_success(self, client: TestClient, auth_headers, created_space_notes, created_file):
        """Test successful notes generation from files."""
        notes_data = {
            "file_ids": [str(created_file.id)],
            "format": "markdown"
        }
        
        response = client.post(
            f"/api/v1/spaces/{created_space_notes.id}/notes",
            json=notes_data,
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_201_CREATED
        
        data = response.json()
        assert "data" in data
        
        note = data["data"]
        assert "id" in note
        assert note["spaceId"] == str(created_space_notes.id)
        assert note["format"] == "markdown"
        assert "content" in note
        assert len(note["content"]) > 0  # Should have generated content
        assert "createdAt" in note
        assert "updatedAt" in note
    
    def test_generate_notes_multiple_files(self, client: TestClient, auth_headers, created_space_notes, created_file, created_file_2):
        """Test notes generation from multiple files."""
        notes_data = {
            "file_ids": [str(created_file.id), str(created_file_2.id)],
            "format": "bullet"
        }
        
        response = client.post(
            f"/api/v1/spaces/{created_space_notes.id}/notes",
            json=notes_data,
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_201_CREATED
        
        data = response.json()
        note = data["data"]
        assert note["format"] == "bullet"
        assert len(note["content"]) > 0
    
    def test_generate_notes_invalid_space_type(self, client: TestClient, auth_headers, created_space, created_file):
        """Test notes generation fails for wrong space type."""
        notes_data = {
            "file_ids": [str(created_file.id)],
            "format": "markdown"
        }
        
        response = client.post(
            f"/api/v1/spaces/{created_space.id}/notes",
            json=notes_data,
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        
        data = response.json()
        assert "error" in data
        assert data["error"]["code"] == "INVALID_SPACE_TYPE"
    
    def test_generate_notes_no_files(self, client: TestClient, auth_headers, created_space_notes):
        """Test notes generation fails without files."""
        notes_data = {
            "file_ids": [],
            "format": "markdown"
        }
        
        response = client.post(
            f"/api/v1/spaces/{created_space_notes.id}/notes",
            json=notes_data,
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_generate_notes_nonexistent_files(self, client: TestClient, auth_headers, created_space_notes):
        """Test notes generation fails with nonexistent files."""
        notes_data = {
            "file_ids": ["00000000-0000-0000-0000-000000000000"],
            "format": "markdown"
        }
        
        response = client.post(
            f"/api/v1/spaces/{created_space_notes.id}/notes",
            json=notes_data,
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        
        data = response.json()
        assert "error" in data
        assert data["error"]["code"] == "FILE_NOT_FOUND"
    
    def test_generate_notes_unauthorized_files(self, client: TestClient, auth_headers, created_space_notes, created_file_other_user):
        """Test notes generation fails with files from other users."""
        notes_data = {
            "file_ids": [str(created_file_other_user.id)],
            "format": "markdown"
        }
        
        response = client.post(
            f"/api/v1/spaces/{created_space_notes.id}/notes",
            json=notes_data,
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
        
        data = response.json()
        assert "error" in data
        assert data["error"]["code"] == "FORBIDDEN"
    
    def test_generate_notes_invalid_format(self, client: TestClient, auth_headers, created_space_notes, created_file):
        """Test notes generation with invalid format."""
        notes_data = {
            "file_ids": [str(created_file.id)],
            "format": "invalid_format"
        }
        
        response = client.post(
            f"/api/v1/spaces/{created_space_notes.id}/notes",
            json=notes_data,
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_generate_notes_nonexistent_space(self, client: TestClient, auth_headers, created_file):
        """Test notes generation fails with nonexistent space."""
        notes_data = {
            "file_ids": [str(created_file.id)],
            "format": "markdown"
        }
        
        response = client.post(
            "/api/v1/spaces/00000000-0000-0000-0000-000000000000/notes",
            json=notes_data,
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_generate_notes_unauthorized_space(self, client: TestClient, auth_headers, created_space_notes_other_user, created_file):
        """Test notes generation fails with unauthorized space."""
        notes_data = {
            "file_ids": [str(created_file.id)],
            "format": "markdown"
        }
        
        response = client.post(
            f"/api/v1/spaces/{created_space_notes_other_user.id}/notes",
            json=notes_data,
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_generate_notes_unauthenticated(self, client: TestClient, created_space_notes, created_file):
        """Test notes generation fails without authentication."""
        notes_data = {
            "file_ids": [str(created_file.id)],
            "format": "markdown"
        }
        
        response = client.post(
            f"/api/v1/spaces/{created_space_notes.id}/notes",
            json=notes_data
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestListNotes:
    """Test list notes endpoint."""
    
    def test_list_notes_empty(self, client: TestClient, auth_headers, created_space_notes):
        """Test listing notes when space has none."""
        response = client.get(f"/api/v1/spaces/{created_space_notes.id}/notes", headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert "data" in data
        assert "meta" in data
        assert data["data"] == []
        assert data["meta"]["total"] == 0
        assert data["meta"]["page"] == 1
        assert data["meta"]["limit"] == 20
    
    def test_list_notes_with_data(self, client: TestClient, auth_headers, created_space_notes, created_note):
        """Test listing notes when space has notes."""
        response = client.get(f"/api/v1/spaces/{created_space_notes.id}/notes", headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert "data" in data
        assert "meta" in data
        assert len(data["data"]) == 1
        assert data["meta"]["total"] == 1
        
        note = data["data"][0]
        assert note["id"] == str(created_note.id)
        assert note["spaceId"] == str(created_space_notes.id)
        assert note["format"] == created_note.format.value
        assert note["content"] == created_note.content
        assert "createdAt" in note
        assert "updatedAt" in note
    
    def test_list_notes_pagination(self, client: TestClient, auth_headers, created_space_notes, created_file):
        """Test notes listing with pagination."""
        # Create multiple notes
        for i in range(5):
            notes_data = {
                "file_ids": [str(created_file.id)],
                "format": "markdown"
            }
            client.post(f"/api/v1/spaces/{created_space_notes.id}/notes", json=notes_data, headers=auth_headers)
        
        # Test pagination
        response = client.get(f"/api/v1/spaces/{created_space_notes.id}/notes?page=1&limit=3", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert len(data["data"]) == 3
        assert data["meta"]["page"] == 1
        assert data["meta"]["limit"] == 3
        assert data["meta"]["total"] == 5
        
        # Test second page
        response = client.get(f"/api/v1/spaces/{created_space_notes.id}/notes?page=2&limit=3", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert len(data["data"]) == 2
        assert data["meta"]["page"] == 2
        assert data["meta"]["limit"] == 3
        assert data["meta"]["total"] == 5
    
    def test_list_notes_invalid_space_type(self, client: TestClient, auth_headers, created_space):
        """Test listing notes fails for wrong space type."""
        response = client.get(f"/api/v1/spaces/{created_space.id}/notes", headers=auth_headers)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        
        data = response.json()
        assert "error" in data
        assert data["error"]["code"] == "INVALID_SPACE_TYPE"
    
    def test_list_notes_nonexistent_space(self, client: TestClient, auth_headers):
        """Test listing notes fails with nonexistent space."""
        response = client.get("/api/v1/spaces/00000000-0000-0000-0000-000000000000/notes", headers=auth_headers)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_list_notes_unauthorized_space(self, client: TestClient, auth_headers, created_space_notes_other_user):
        """Test listing notes fails with unauthorized space."""
        response = client.get(f"/api/v1/spaces/{created_space_notes_other_user.id}/notes", headers=auth_headers)
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_list_notes_unauthenticated(self, client: TestClient, created_space_notes):
        """Test listing notes fails without authentication."""
        response = client.get(f"/api/v1/spaces/{created_space_notes.id}/notes")
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestGetNote:
    """Test get note endpoint."""
    
    def test_get_note_success(self, client: TestClient, auth_headers, created_note):
        """Test successful note retrieval."""
        response = client.get(f"/api/v1/notes/{created_note.id}", headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert "data" in data
        
        note = data["data"]
        assert note["id"] == str(created_note.id)
        assert note["spaceId"] == str(created_note.space_id)
        assert note["format"] == created_note.format.value
        assert note["content"] == created_note.content
        assert "createdAt" in note
        assert "updatedAt" in note
    
    def test_get_note_nonexistent(self, client: TestClient, auth_headers):
        """Test getting nonexistent note."""
        response = client.get("/api/v1/notes/00000000-0000-0000-0000-000000000000", headers=auth_headers)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        
        data = response.json()
        assert "error" in data
        assert data["error"]["code"] == "NOTE_NOT_FOUND"
    
    def test_get_note_unauthorized(self, client: TestClient, auth_headers, created_note_other_user):
        """Test getting note from another user fails."""
        response = client.get(f"/api/v1/notes/{created_note_other_user.id}", headers=auth_headers)
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
        
        data = response.json()
        assert "error" in data
        assert data["error"]["code"] == "FORBIDDEN"
    
    def test_get_note_unauthenticated(self, client: TestClient, created_note):
        """Test getting note fails without authentication."""
        response = client.get(f"/api/v1/notes/{created_note.id}")
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_get_note_invalid_uuid(self, client: TestClient, auth_headers):
        """Test getting note with invalid UUID."""
        response = client.get("/api/v1/notes/invalid-uuid", headers=auth_headers)
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestUpdateNote:
    """Test update note endpoint."""
    
    def test_update_note_success(self, client: TestClient, auth_headers, created_note):
        """Test successful note update."""
        update_data = {
            "content": "# Updated Content\n\nThis is the updated note content."
        }
        
        response = client.patch(f"/api/v1/notes/{created_note.id}", json=update_data, headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert "data" in data
        
        note = data["data"]
        assert note["id"] == str(created_note.id)
        assert note["content"] == update_data["content"]
        assert "updatedAt" in note
    
    def test_update_note_empty_content(self, client: TestClient, auth_headers, created_note):
        """Test updating note with empty content fails."""
        update_data = {
            "content": ""
        }
        
        response = client.patch(f"/api/v1/notes/{created_note.id}", json=update_data, headers=auth_headers)
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_update_note_whitespace_only(self, client: TestClient, auth_headers, created_note):
        """Test updating note with whitespace-only content fails."""
        update_data = {
            "content": "   \n\t  "
        }
        
        response = client.patch(f"/api/v1/notes/{created_note.id}", json=update_data, headers=auth_headers)
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_update_note_nonexistent(self, client: TestClient, auth_headers):
        """Test updating nonexistent note."""
        update_data = {
            "content": "Updated content"
        }
        
        response = client.patch("/api/v1/notes/00000000-0000-0000-0000-000000000000", json=update_data, headers=auth_headers)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_update_note_unauthorized(self, client: TestClient, auth_headers, created_note_other_user):
        """Test updating note from another user fails."""
        update_data = {
            "content": "Malicious update"
        }
        
        response = client.patch(f"/api/v1/notes/{created_note_other_user.id}", json=update_data, headers=auth_headers)
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_update_note_unauthenticated(self, client: TestClient, created_note):
        """Test updating note fails without authentication."""
        update_data = {
            "content": "Updated content"
        }
        
        response = client.patch(f"/api/v1/notes/{created_note.id}", json=update_data)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_update_note_no_changes(self, client: TestClient, auth_headers, created_note):
        """Test updating note with no changes."""
        update_data = {}
        
        response = client.patch(f"/api/v1/notes/{created_note.id}", json=update_data, headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        note = data["data"]
        assert note["content"] == created_note.content  # No change


class TestDeleteNote:
    """Test delete note endpoint."""
    
    def test_delete_note_success(self, client: TestClient, auth_headers, created_note):
        """Test successful note deletion."""
        response = client.delete(f"/api/v1/notes/{created_note.id}", headers=auth_headers)
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
        
        # Verify note is deleted
        get_response = client.get(f"/api/v1/notes/{created_note.id}", headers=auth_headers)
        assert get_response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_delete_note_nonexistent(self, client: TestClient, auth_headers):
        """Test deleting nonexistent note."""
        response = client.delete("/api/v1/notes/00000000-0000-0000-0000-000000000000", headers=auth_headers)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_delete_note_unauthorized(self, client: TestClient, auth_headers, created_note_other_user):
        """Test deleting note from another user fails."""
        response = client.delete(f"/api/v1/notes/{created_note_other_user.id}", headers=auth_headers)
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_delete_note_unauthenticated(self, client: TestClient, created_note):
        """Test deleting note fails without authentication."""
        response = client.delete(f"/api/v1/notes/{created_note.id}")
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_delete_note_invalid_uuid(self, client: TestClient, auth_headers):
        """Test deleting note with invalid UUID."""
        response = client.delete("/api/v1/notes/invalid-uuid", headers=auth_headers)
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestNotesIntegration:
    """Test notes integration scenarios."""
    
    def test_full_notes_workflow(self, client: TestClient, auth_headers, created_space_notes, created_file):
        """Test complete notes workflow: create, list, get, update, delete."""
        # 1. Create notes
        notes_data = {
            "file_ids": [str(created_file.id)],
            "format": "markdown"
        }
        
        create_response = client.post(
            f"/api/v1/spaces/{created_space_notes.id}/notes",
            json=notes_data,
            headers=auth_headers
        )
        assert create_response.status_code == status.HTTP_201_CREATED
        note_id = create_response.json()["data"]["id"]
        
        # 2. List notes (should find 1)
        list_response = client.get(f"/api/v1/spaces/{created_space_notes.id}/notes", headers=auth_headers)
        assert list_response.status_code == status.HTTP_200_OK
        assert len(list_response.json()["data"]) == 1
        
        # 3. Get specific note
        get_response = client.get(f"/api/v1/notes/{note_id}", headers=auth_headers)
        assert get_response.status_code == status.HTTP_200_OK
        
        # 4. Update note
        update_data = {"content": "# Updated Notes\n\nUpdated content"}
        update_response = client.patch(f"/api/v1/notes/{note_id}", json=update_data, headers=auth_headers)
        assert update_response.status_code == status.HTTP_200_OK
        assert update_response.json()["data"]["content"] == update_data["content"]
        
        # 5. Delete note
        delete_response = client.delete(f"/api/v1/notes/{note_id}", headers=auth_headers)
        assert delete_response.status_code == status.HTTP_204_NO_CONTENT
        
        # 6. Verify deletion
        final_list_response = client.get(f"/api/v1/spaces/{created_space_notes.id}/notes", headers=auth_headers)
        assert final_list_response.status_code == status.HTTP_200_OK
        assert len(final_list_response.json()["data"]) == 0
    
    def test_notes_space_deletion_cascade(self, client: TestClient, auth_headers, created_space_notes, created_note):
        """Test that deleting a space cascades to delete all notes."""
        # Verify note exists
        get_response = client.get(f"/api/v1/notes/{created_note.id}", headers=auth_headers)
        assert get_response.status_code == status.HTTP_200_OK
        
        # Delete the space
        delete_space_response = client.delete(f"/api/v1/spaces/{created_space_notes.id}", headers=auth_headers)
        assert delete_space_response.status_code == status.HTTP_204_NO_CONTENT
        
        # Verify note is also deleted (cascade)
        get_after_delete_response = client.get(f"/api/v1/notes/{created_note.id}", headers=auth_headers)
        assert get_after_delete_response.status_code == status.HTTP_404_NOT_FOUND 