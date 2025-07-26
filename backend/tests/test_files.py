"""
File management endpoint tests for EdutechHackathon API.

Tests all file endpoints according to the API specification:
- POST /files/upload - Upload one or many files (multipart)
- GET /folders/{folderId}/files - List files in folder
- GET /files/{id} - File metadata
- GET /files/{id}/content - Raw or extracted text
- DELETE /files/{id} - Delete file
"""
import pytest
import tempfile
import os
from fastapi import status
from fastapi.testclient import TestClient


class TestFileUpload:
    """Test file upload endpoint."""
    
    def test_upload_single_file_success(self, client: TestClient, auth_headers, created_folder, temp_test_file):
        """Test successful single file upload."""
        with open(temp_test_file, 'rb') as f:
            files = {"files": (os.path.basename(temp_test_file), f, "text/plain")}
            data = {"folder_id": str(created_folder.id)}
            
            response = client.post("/api/v1/files/upload", 
                                 files=files, data=data, headers=auth_headers)
        
        assert response.status_code == status.HTTP_201_CREATED
        
        response_data = response.json()
        assert "data" in response_data
        assert len(response_data["data"]) == 1
        
        file_data = response_data["data"][0]
        assert file_data["folder_id"] == str(created_folder.id)
        assert file_data["name"] == os.path.basename(temp_test_file)
        assert file_data["mime_type"] == "text/plain"
        assert file_data["size"] > 0
        assert "id" in file_data
        assert "created_at" in file_data
    
    def test_upload_multiple_files_success(self, client: TestClient, auth_headers, created_folder):
        """Test successful multiple file upload."""
        # Create multiple test files
        test_files = []
        for i in range(3):
            with tempfile.NamedTemporaryFile(delete=False, suffix=f"_test_{i}.txt") as f:
                f.write(f"Test content for file {i}".encode())
                test_files.append(f.name)
        
        try:
            files = []
            for test_file in test_files:
                with open(test_file, 'rb') as f:
                    content = f.read()
                files.append(("files", (os.path.basename(test_file), content, "text/plain")))
            
            data = {"folder_id": str(created_folder.id)}
            
            response = client.post("/api/v1/files/upload", 
                                 files=files, data=data, headers=auth_headers)
            
            assert response.status_code == status.HTTP_201_CREATED
            
            response_data = response.json()
            assert len(response_data["data"]) == 3
            
            for file_data in response_data["data"]:
                assert file_data["folder_id"] == str(created_folder.id)
                assert "id" in file_data
                assert "name" in file_data
                assert file_data["mime_type"] == "text/plain"
        
        finally:
            # Cleanup
            for test_file in test_files:
                os.unlink(test_file)
    
    def test_upload_file_invalid_folder(self, client: TestClient, auth_headers, temp_test_file):
        """Test file upload to non-existent folder."""
        fake_id = "123e4567-e89b-12d3-a456-426614174000"
        
        with open(temp_test_file, 'rb') as f:
            files = {"files": (os.path.basename(temp_test_file), f, "text/plain")}
            data = {"folder_id": fake_id}
            
            response = client.post("/api/v1/files/upload", 
                                 files=files, data=data, headers=auth_headers)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        
        response_data = response.json()
        assert "error" in response_data
    
    def test_upload_file_no_auth(self, client: TestClient, created_folder, temp_test_file):
        """Test file upload without authentication."""
        with open(temp_test_file, 'rb') as f:
            files = {"files": (os.path.basename(temp_test_file), f, "text/plain")}
            data = {"folder_id": str(created_folder.id)}
            
            response = client.post("/api/v1/files/upload", files=files, data=data)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        
        response_data = response.json()
        assert "error" in response_data
    
    def test_upload_file_other_user_folder(self, client: TestClient, sample_user_2_data, created_folder, temp_test_file):
        """Test file upload to folder owned by another user."""
        # Register second user
        register_response = client.post("/api/v1/auth/register", json=sample_user_2_data)
        token_2 = register_response.json()["data"]["token"]
        headers_2 = {"Authorization": f"Bearer {token_2}"}
        
        with open(temp_test_file, 'rb') as f:
            files = {"files": (os.path.basename(temp_test_file), f, "text/plain")}
            data = {"folder_id": str(created_folder.id)}
            
            response = client.post("/api/v1/files/upload", 
                                 files=files, data=data, headers=headers_2)
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
        
        response_data = response.json()
        assert "error" in response_data
    
    def test_upload_file_too_large(self, client: TestClient, auth_headers, created_folder):
        """Test file upload that exceeds size limit."""
        # Create a large file (simulate > 25MB)
        large_content = b"x" * (26 * 1024 * 1024)  # 26MB
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as f:
            f.write(large_content)
            large_file = f.name
        
        try:
            files = {"files": (os.path.basename(large_file), large_content, "text/plain")}
            data = {"folder_id": str(created_folder.id)}
            
            response = client.post("/api/v1/files/upload", 
                                 files=files, data=data, headers=auth_headers)
            
            # Should return 413 for file too large
            assert response.status_code == status.HTTP_413_REQUEST_ENTITY_TOO_LARGE
            
            response_data = response.json()
            assert "error" in response_data
            assert response_data["error"]["code"] == "FILE_TOO_LARGE"
        
        finally:
            os.unlink(large_file)
    
    def test_upload_unsupported_file_type(self, client: TestClient, auth_headers, created_folder):
        """Test upload of unsupported file type."""
        # Create an executable file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".exe") as f:
            f.write(b"fake executable content")
            exe_file = f.name
        
        try:
            with open(exe_file, 'rb') as f:
                files = {"files": (os.path.basename(exe_file), f, "application/x-executable")}
                data = {"folder_id": str(created_folder.id)}
                
                response = client.post("/api/v1/files/upload", 
                                     files=files, data=data, headers=auth_headers)
            
            # Should return 415 for unsupported media type
            assert response.status_code == status.HTTP_415_UNSUPPORTED_MEDIA_TYPE
            
            response_data = response.json()
            assert "error" in response_data
            assert response_data["error"]["code"] == "UNSUPPORTED_FORMAT"
        
        finally:
            os.unlink(exe_file)
    
    def test_upload_no_files(self, client: TestClient, auth_headers, created_folder):
        """Test upload request with no files."""
        data = {"folder_id": str(created_folder.id)}
        
        response = client.post("/api/v1/files/upload", data=data, headers=auth_headers)
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_upload_missing_folder_id(self, client: TestClient, auth_headers, temp_test_file):
        """Test upload request with missing folder_id."""
        with open(temp_test_file, 'rb') as f:
            files = {"files": (os.path.basename(temp_test_file), f, "text/plain")}
            
            response = client.post("/api/v1/files/upload", files=files, headers=auth_headers)
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestListFiles:
    """Test list files endpoint."""
    
    def test_list_files_empty(self, client: TestClient, auth_headers, created_folder):
        """Test listing files when folder has none."""
        response = client.get(f"/api/v1/folders/{created_folder.id}/files", headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert "data" in data
        assert "meta" in data
        assert data["data"] == []
        assert data["meta"]["total"] == 0
        assert data["meta"]["page"] == 1
        assert data["meta"]["limit"] == 20
    
    def test_list_files_with_data(self, client: TestClient, auth_headers, created_folder, temp_test_file):
        """Test listing files when folder has files."""
        # First upload a file
        with open(temp_test_file, 'rb') as f:
            files = {"files": (os.path.basename(temp_test_file), f, "text/plain")}
            data = {"folder_id": str(created_folder.id)}
            
            upload_response = client.post("/api/v1/files/upload", 
                                        files=files, data=data, headers=auth_headers)
        
        assert upload_response.status_code == status.HTTP_201_CREATED
        uploaded_file = upload_response.json()["data"][0]
        
        # Now list files
        response = client.get(f"/api/v1/folders/{created_folder.id}/files", headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert "data" in data
        assert "meta" in data
        assert len(data["data"]) == 1
        assert data["meta"]["total"] == 1
        
        file_data = data["data"][0]
        assert file_data["id"] == uploaded_file["id"]
        assert file_data["name"] == uploaded_file["name"]
        assert file_data["folder_id"] == str(created_folder.id)
        assert "size" in file_data
        assert "mime_type" in file_data
        assert "created_at" in file_data
    
    def test_list_files_pagination(self, client: TestClient, auth_headers, created_folder):
        """Test file listing with pagination."""
        # Upload multiple files
        for i in range(5):
            with tempfile.NamedTemporaryFile(delete=False, suffix=f"_test_{i}.txt") as f:
                f.write(f"Test content {i}".encode())
                
                with open(f.name, 'rb') as upload_f:
                    files = {"files": (os.path.basename(f.name), upload_f, "text/plain")}
                    data = {"folder_id": str(created_folder.id)}
                    
                    client.post("/api/v1/files/upload", 
                              files=files, data=data, headers=auth_headers)
                
                os.unlink(f.name)
        
        # Test pagination
        response = client.get(f"/api/v1/folders/{created_folder.id}/files?page=1&limit=3", 
                            headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert len(data["data"]) == 3
        assert data["meta"]["page"] == 1
        assert data["meta"]["limit"] == 3
        assert data["meta"]["total"] == 5
        
        # Test second page
        response = client.get(f"/api/v1/folders/{created_folder.id}/files?page=2&limit=3", 
                            headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert len(data["data"]) == 2  # Remaining files
        assert data["meta"]["page"] == 2
    
    def test_list_files_invalid_folder(self, client: TestClient, auth_headers):
        """Test listing files for non-existent folder."""
        fake_id = "123e4567-e89b-12d3-a456-426614174000"
        response = client.get(f"/api/v1/folders/{fake_id}/files", headers=auth_headers)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        
        data = response.json()
        assert "error" in data
    
    def test_list_files_no_auth(self, client: TestClient, created_folder):
        """Test listing files without authentication."""
        response = client.get(f"/api/v1/folders/{created_folder.id}/files")
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        
        data = response.json()
        assert "error" in data
    
    def test_list_files_other_user_folder(self, client: TestClient, sample_user_2_data, created_folder):
        """Test listing files for folder owned by another user."""
        # Register second user
        register_response = client.post("/api/v1/auth/register", json=sample_user_2_data)
        token_2 = register_response.json()["data"]["token"]
        headers_2 = {"Authorization": f"Bearer {token_2}"}
        
        # Try to list files in first user's folder
        response = client.get(f"/api/v1/folders/{created_folder.id}/files", headers=headers_2)
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
        
        data = response.json()
        assert "error" in data


class TestGetFileMetadata:
    """Test get file metadata endpoint."""
    
    def test_get_file_metadata_success(self, client: TestClient, auth_headers, created_folder, temp_test_file):
        """Test successful file metadata retrieval."""
        # First upload a file
        with open(temp_test_file, 'rb') as f:
            files = {"files": (os.path.basename(temp_test_file), f, "text/plain")}
            data = {"folder_id": str(created_folder.id)}
            
            upload_response = client.post("/api/v1/files/upload", 
                                        files=files, data=data, headers=auth_headers)
        
        uploaded_file = upload_response.json()["data"][0]
        file_id = uploaded_file["id"]
        
        # Get file metadata
        response = client.get(f"/api/v1/files/{file_id}", headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert "data" in data
        
        file_data = data["data"]
        assert file_data["id"] == file_id
        assert file_data["name"] == uploaded_file["name"]
        assert file_data["folder_id"] == str(created_folder.id)
        assert file_data["mime_type"] == "text/plain"
        assert file_data["size"] > 0
        assert "created_at" in file_data
    
    def test_get_file_metadata_not_found(self, client: TestClient, auth_headers):
        """Test getting metadata for non-existent file."""
        fake_id = "123e4567-e89b-12d3-a456-426614174000"
        response = client.get(f"/api/v1/files/{fake_id}", headers=auth_headers)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        
        data = response.json()
        assert "error" in data
    
    def test_get_file_metadata_invalid_id(self, client: TestClient, auth_headers):
        """Test getting file metadata with invalid ID format."""
        response = client.get("/api/v1/files/invalid-id", headers=auth_headers)
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_get_file_metadata_no_auth(self, client: TestClient, created_folder, temp_test_file):
        """Test file metadata retrieval without authentication."""
        # First upload a file (as authenticated user)
        # Register a user first
        user_data = {"email": "test@example.com", "password": "password123", "name": "Test User"}
        register_response = client.post("/api/v1/auth/register", json=user_data)
        token = register_response.json()["data"]["token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Create folder
        folder_data = {"title": "Test Folder"}
        folder_response = client.post("/api/v1/folders", json=folder_data, headers=headers)
        folder_id = folder_response.json()["data"]["id"]
        
        # Upload file
        with open(temp_test_file, 'rb') as f:
            files = {"files": (os.path.basename(temp_test_file), f, "text/plain")}
            data = {"folder_id": folder_id}
            
            upload_response = client.post("/api/v1/files/upload", 
                                        files=files, data=data, headers=headers)
        
        file_id = upload_response.json()["data"][0]["id"]
        
        # Try to get metadata without auth
        response = client.get(f"/api/v1/files/{file_id}")
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        
        data = response.json()
        assert "error" in data
    
    def test_get_file_metadata_other_user(self, client: TestClient, sample_user_2_data, created_folder, temp_test_file, auth_headers):
        """Test accessing file metadata owned by another user."""
        # Upload file as first user
        with open(temp_test_file, 'rb') as f:
            files = {"files": (os.path.basename(temp_test_file), f, "text/plain")}
            data = {"folder_id": str(created_folder.id)}
            
            upload_response = client.post("/api/v1/files/upload", 
                                        files=files, data=data, headers=auth_headers)
        
        file_id = upload_response.json()["data"][0]["id"]
        
        # Register second user
        register_response = client.post("/api/v1/auth/register", json=sample_user_2_data)
        token_2 = register_response.json()["data"]["token"]
        headers_2 = {"Authorization": f"Bearer {token_2}"}
        
        # Try to access first user's file
        response = client.get(f"/api/v1/files/{file_id}", headers=headers_2)
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
        
        data = response.json()
        assert "error" in data


class TestGetFileContent:
    """Test get file content endpoint."""
    
    def test_get_file_content_success(self, client: TestClient, auth_headers, created_folder, temp_test_file):
        """Test successful file content retrieval."""
        # First upload a file
        with open(temp_test_file, 'rb') as f:
            original_content = f.read()
            f.seek(0)
            files = {"files": (os.path.basename(temp_test_file), f, "text/plain")}
            data = {"folder_id": str(created_folder.id)}
            
            upload_response = client.post("/api/v1/files/upload", 
                                        files=files, data=data, headers=auth_headers)
        
        file_id = upload_response.json()["data"][0]["id"]
        
        # Get file content
        response = client.get(f"/api/v1/files/{file_id}/content", headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert "data" in data
        assert "content" in data["data"]
        assert "mime_type" in data["data"]
        
        # Content should match original (for text files, it might be extracted text)
        assert data["data"]["mime_type"] == "text/plain"
        # For text files, content should contain the original text
        assert original_content.decode() in data["data"]["content"] or data["data"]["content"] == original_content.decode()
    
    def test_get_file_content_not_found(self, client: TestClient, auth_headers):
        """Test getting content for non-existent file."""
        fake_id = "123e4567-e89b-12d3-a456-426614174000"
        response = client.get(f"/api/v1/files/{fake_id}/content", headers=auth_headers)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        
        data = response.json()
        assert "error" in data
    
    def test_get_file_content_no_auth(self, client: TestClient, created_folder, temp_test_file):
        """Test file content retrieval without authentication."""
        # First create and upload a file (need a user for this)
        user_data = {"email": "test@example.com", "password": "password123", "name": "Test User"}
        register_response = client.post("/api/v1/auth/register", json=user_data)
        token = register_response.json()["data"]["token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Create folder
        folder_data = {"title": "Test Folder"}
        folder_response = client.post("/api/v1/folders", json=folder_data, headers=headers)
        folder_id = folder_response.json()["data"]["id"]
        
        # Upload file
        with open(temp_test_file, 'rb') as f:
            files = {"files": (os.path.basename(temp_test_file), f, "text/plain")}
            data = {"folder_id": folder_id}
            
            upload_response = client.post("/api/v1/files/upload", 
                                        files=files, data=data, headers=headers)
        
        file_id = upload_response.json()["data"][0]["id"]
        
        # Try to get content without auth
        response = client.get(f"/api/v1/files/{file_id}/content")
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        
        data = response.json()
        assert "error" in data


class TestDeleteFile:
    """Test delete file endpoint."""
    
    def test_delete_file_success(self, client: TestClient, auth_headers, created_folder, temp_test_file):
        """Test successful file deletion."""
        # First upload a file
        with open(temp_test_file, 'rb') as f:
            files = {"files": (os.path.basename(temp_test_file), f, "text/plain")}
            data = {"folder_id": str(created_folder.id)}
            
            upload_response = client.post("/api/v1/files/upload", 
                                        files=files, data=data, headers=auth_headers)
        
        file_id = upload_response.json()["data"][0]["id"]
        
        # Delete file
        response = client.delete(f"/api/v1/files/{file_id}", headers=auth_headers)
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert response.content == b""
        
        # Verify file is deleted
        get_response = client.get(f"/api/v1/files/{file_id}", headers=auth_headers)
        assert get_response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_delete_file_soft_delete(self, client: TestClient, auth_headers, created_folder, temp_test_file):
        """Test soft delete (default behavior)."""
        # Upload file
        with open(temp_test_file, 'rb') as f:
            files = {"files": (os.path.basename(temp_test_file), f, "text/plain")}
            data = {"folder_id": str(created_folder.id)}
            
            upload_response = client.post("/api/v1/files/upload", 
                                        files=files, data=data, headers=auth_headers)
        
        file_id = upload_response.json()["data"][0]["id"]
        
        # Soft delete (force=false is default)
        response = client.delete(f"/api/v1/files/{file_id}?force=false", headers=auth_headers)
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
        
        # File should not be accessible
        get_response = client.get(f"/api/v1/files/{file_id}", headers=auth_headers)
        assert get_response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_delete_file_hard_delete(self, client: TestClient, auth_headers, created_folder, temp_test_file):
        """Test hard delete (force=true)."""
        # Upload file
        with open(temp_test_file, 'rb') as f:
            files = {"files": (os.path.basename(temp_test_file), f, "text/plain")}
            data = {"folder_id": str(created_folder.id)}
            
            upload_response = client.post("/api/v1/files/upload", 
                                        files=files, data=data, headers=auth_headers)
        
        file_id = upload_response.json()["data"][0]["id"]
        
        # Hard delete
        response = client.delete(f"/api/v1/files/{file_id}?force=true", headers=auth_headers)
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
        
        # File should not be accessible
        get_response = client.get(f"/api/v1/files/{file_id}", headers=auth_headers)
        assert get_response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_delete_file_not_found(self, client: TestClient, auth_headers):
        """Test deleting non-existent file."""
        fake_id = "123e4567-e89b-12d3-a456-426614174000"
        
        response = client.delete(f"/api/v1/files/{fake_id}", headers=auth_headers)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_delete_file_no_auth(self, client: TestClient, created_folder, temp_test_file):
        """Test file deletion without authentication."""
        # First create and upload a file (need a user for this)
        user_data = {"email": "test@example.com", "password": "password123", "name": "Test User"}
        register_response = client.post("/api/v1/auth/register", json=user_data)
        token = register_response.json()["data"]["token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Create folder
        folder_data = {"title": "Test Folder"}
        folder_response = client.post("/api/v1/folders", json=folder_data, headers=headers)
        folder_id = folder_response.json()["data"]["id"]
        
        # Upload file
        with open(temp_test_file, 'rb') as f:
            files = {"files": (os.path.basename(temp_test_file), f, "text/plain")}
            data = {"folder_id": folder_id}
            
            upload_response = client.post("/api/v1/files/upload", 
                                        files=files, data=data, headers=headers)
        
        file_id = upload_response.json()["data"][0]["id"]
        
        # Try to delete without auth
        response = client.delete(f"/api/v1/files/{file_id}")
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        
        data = response.json()
        assert "error" in data
    
    def test_delete_file_other_user(self, client: TestClient, sample_user_2_data, created_folder, temp_test_file, auth_headers):
        """Test deleting file owned by another user."""
        # Upload file as first user
        with open(temp_test_file, 'rb') as f:
            files = {"files": (os.path.basename(temp_test_file), f, "text/plain")}
            data = {"folder_id": str(created_folder.id)}
            
            upload_response = client.post("/api/v1/files/upload", 
                                        files=files, data=data, headers=auth_headers)
        
        file_id = upload_response.json()["data"][0]["id"]
        
        # Register second user
        register_response = client.post("/api/v1/auth/register", json=sample_user_2_data)
        token_2 = register_response.json()["data"]["token"]
        headers_2 = {"Authorization": f"Bearer {token_2}"}
        
        # Try to delete first user's file
        response = client.delete(f"/api/v1/files/{file_id}", headers=headers_2)
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
        
        data = response.json()
        assert "error" in data


class TestFileOwnership:
    """Test file ownership and access control."""
    
    def test_file_belongs_to_correct_folder(self, client: TestClient, auth_headers, temp_test_file):
        """Test that files are properly associated with folders."""
        # Create two folders
        folder1_data = {"title": "Folder 1"}
        folder2_data = {"title": "Folder 2"}
        
        folder1_response = client.post("/api/v1/folders", json=folder1_data, headers=auth_headers)
        folder2_response = client.post("/api/v1/folders", json=folder2_data, headers=auth_headers)
        
        folder1_id = folder1_response.json()["data"]["id"]
        folder2_id = folder2_response.json()["data"]["id"]
        
        # Upload file to folder 1
        with open(temp_test_file, 'rb') as f:
            files = {"files": (os.path.basename(temp_test_file), f, "text/plain")}
            data = {"folder_id": folder1_id}
            
            upload_response = client.post("/api/v1/files/upload", 
                                        files=files, data=data, headers=auth_headers)
        
        file_id = upload_response.json()["data"][0]["id"]
        
        # File should appear in folder 1 list
        list_response1 = client.get(f"/api/v1/folders/{folder1_id}/files", headers=auth_headers)
        assert len(list_response1.json()["data"]) == 1
        
        # File should not appear in folder 2 list
        list_response2 = client.get(f"/api/v1/folders/{folder2_id}/files", headers=auth_headers)
        assert len(list_response2.json()["data"]) == 0
        
        # File details should show correct folder_id
        file_response = client.get(f"/api/v1/files/{file_id}", headers=auth_headers)
        assert file_response.json()["data"]["folder_id"] == folder1_id
    
    def test_user_isolation_files(self, client: TestClient, sample_user_data, sample_user_2_data, temp_test_file):
        """Test that users can only see files in their own folders."""
        # Register two users
        register_response_1 = client.post("/api/v1/auth/register", json=sample_user_data)
        register_response_2 = client.post("/api/v1/auth/register", json=sample_user_2_data)
        
        token_1 = register_response_1.json()["data"]["token"]
        token_2 = register_response_2.json()["data"]["token"]
        
        headers_1 = {"Authorization": f"Bearer {token_1}"}
        headers_2 = {"Authorization": f"Bearer {token_2}"}
        
        # User 1 creates folder and uploads file
        folder_data = {"title": "User 1 Folder"}
        folder_response = client.post("/api/v1/folders", json=folder_data, headers=headers_1)
        folder_id = folder_response.json()["data"]["id"]
        
        with open(temp_test_file, 'rb') as f:
            files = {"files": (os.path.basename(temp_test_file), f, "text/plain")}
            data = {"folder_id": folder_id}
            
            upload_response = client.post("/api/v1/files/upload", 
                                        files=files, data=data, headers=headers_1)
        
        file_id = upload_response.json()["data"][0]["id"]
        
        # User 2 should not be able to access user 1's file
        get_response = client.get(f"/api/v1/files/{file_id}", headers=headers_2)
        assert get_response.status_code == status.HTTP_403_FORBIDDEN
        
        # User 2 should not be able to list files in user 1's folder
        list_response = client.get(f"/api/v1/folders/{folder_id}/files", headers=headers_2)
        assert list_response.status_code == status.HTTP_403_FORBIDDEN 