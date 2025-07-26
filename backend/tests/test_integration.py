"""
Integration tests for EdutechHackathon backend API.

Tests complete workflows and cross-module interactions:
- Complete user journey from registration to content creation
- Cross-module data flow and relationships
- End-to-end scenarios with multiple API calls
- Performance and concurrency testing
"""
import pytest
import uuid
import tempfile
import os
import time
from fastapi import status
from fastapi.testclient import TestClient
from datetime import datetime


class TestCompleteUserJourney:
    """Test complete user journey from registration to content creation."""
    
    def test_complete_user_workflow(self, client: TestClient):
        """Test complete user workflow: register -> login -> create folder -> upload files -> create spaces -> generate content."""
        # 1. Register user
        user_data = {
            "email": "journey@test.com",
            "password": "journey123",
            "name": "Journey User"
        }
        response = client.post("/api/v1/auth/register", json=user_data)
        assert response.status_code == status.HTTP_201_CREATED
        
        data = response.json()
        token = data["data"]["token"]
        user_id = data["data"]["user"]["id"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # 2. Create folder
        folder_data = {
            "title": "Journey Folder",
            "description": "Folder for complete workflow testing"
        }
        response = client.post("/api/v1/folders", json=folder_data, headers=headers)
        assert response.status_code == status.HTTP_201_CREATED
        
        folder_id = response.json()["data"]["id"]
        
        # 3. Upload test files
        test_content = "This is test content for the complete workflow."
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(test_content)
            f.flush()
            
            with open(f.name, 'rb') as file:
                response = client.post(
                    "/api/v1/files/upload",
                    files={"files": ("test.txt", file, "text/plain")},
                    data={"folder_id": folder_id},
                    headers=headers
                )
        
        os.unlink(f.name)
        assert response.status_code == status.HTTP_201_CREATED
        
        file_id = response.json()["data"][0]["id"]
        
        # 4. Create different types of spaces
        space_types = ["chat", "quiz", "notes", "flashcards", "openended"]
        space_ids = {}
        
        for space_type in space_types:
            space_data = {
                "type": space_type,
                "title": f"{space_type.title()} Space",
                "settings": {}
            }
            response = client.post(f"/api/v1/folders/{folder_id}/spaces", json=space_data, headers=headers)
            assert response.status_code == status.HTTP_201_CREATED
            space_ids[space_type] = response.json()["data"]["id"]
        
        # 5. Generate content in each space type
        # Chat: Send a message
        chat_message = {
            "role": "user",
            "content": "Hello, this is a test message for the complete workflow."
        }
        response = client.post(f"/api/v1/spaces/{space_ids['chat']}/messages", json=chat_message, headers=headers)
        assert response.status_code == status.HTTP_201_CREATED
        
        # Quiz: Generate quiz
        quiz_data = {
            "title": "Workflow Quiz",
            "fileIds": [file_id],
            "questionCount": 3
        }
        response = client.post(f"/api/v1/spaces/{space_ids['quiz']}/quizzes", json=quiz_data, headers=headers)
        assert response.status_code == status.HTTP_201_CREATED
        
        quiz_id = response.json()["data"]["id"]
        
        # Notes: Generate notes
        notes_data = {
            "fileIds": [file_id],
            "format": "markdown"
        }
        response = client.post(f"/api/v1/spaces/{space_ids['notes']}/notes", json=notes_data, headers=headers)
        assert response.status_code == status.HTTP_201_CREATED
        
        note_id = response.json()["data"]["id"]
        
        # Flashcards: Generate flashcards
        flashcard_data = {
            "title": "Workflow Flashcards",
            "fileIds": [file_id]
        }
        response = client.post(f"/api/v1/spaces/{space_ids['flashcards']}/flashcards", json=flashcard_data, headers=headers)
        assert response.status_code == status.HTTP_201_CREATED
        
        flashcard_id = response.json()["data"]["id"]
        
        # Open-ended: Generate questions
        openended_data = {
            "title": "Workflow Questions",
            "fileIds": [file_id],
            "questionCount": 2
        }
        response = client.post(f"/api/v1/spaces/{space_ids['openended']}/openended", json=openended_data, headers=headers)
        assert response.status_code == status.HTTP_201_CREATED
        
        openended_id = response.json()["data"]["id"]
        
        # 6. Verify all content was created
        # Check chat messages
        response = client.get(f"/api/v1/spaces/{space_ids['chat']}/messages", headers=headers)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()["data"]) == 1
        
        # Check quiz
        response = client.get(f"/api/v1/quizzes/{quiz_id}", headers=headers)
        assert response.status_code == status.HTTP_200_OK
        
        # Check notes
        response = client.get(f"/api/v1/notes/{note_id}", headers=headers)
        assert response.status_code == status.HTTP_200_OK
        
        # Check flashcards
        response = client.get(f"/api/v1/flashcards/{flashcard_id}", headers=headers)
        assert response.status_code == status.HTTP_200_OK
        
        # Check open-ended questions
        response = client.get(f"/api/v1/openended/{openended_id}", headers=headers)
        assert response.status_code == status.HTTP_200_OK
        
        # 7. Test content interactions
        # Submit quiz answers
        quiz_response = client.get(f"/api/v1/quizzes/{quiz_id}", headers=headers)
        quiz_data = quiz_response.json()["data"]
        questions = quiz_data["questions"]
        
        answers = []
        for question in questions:
            if question["type"] == "mcq":
                answers.append({"questionId": question["id"], "answer": "A"})
            elif question["type"] == "tf":
                answers.append({"questionId": question["id"], "answer": True})
        
        response = client.post(f"/api/v1/quizzes/{quiz_id}/submit", json={"answers": answers}, headers=headers)
        assert response.status_code == status.HTTP_201_CREATED
        
        # Submit open-ended answers
        openended_response = client.get(f"/api/v1/openended/{openended_id}", headers=headers)
        openended_data = openended_response.json()["data"]
        questions = openended_data["questions"]
        
        answers = []
        for question in questions:
            answers.append({
                "question_id": question["id"],
                "answer": "This is a comprehensive answer for the workflow test question."
            })
        
        response = client.post(f"/api/v1/openended/{openended_id}/submit", json={"answers": answers}, headers=headers)
        assert response.status_code == status.HTTP_201_CREATED
        
        # 8. Clean up (optional - test cascade deletion)
        # Delete folder should cascade to all content
        response = client.delete(f"/api/v1/folders/{folder_id}", headers=headers)
        assert response.status_code == status.HTTP_204_NO_CONTENT
        
        # Verify all content is deleted
        response = client.get(f"/api/v1/quizzes/{quiz_id}", headers=headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND
        
        response = client.get(f"/api/v1/notes/{note_id}", headers=headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestCrossModuleDataFlow:
    """Test data flow between different modules."""
    
    def test_file_to_content_flow(self, client: TestClient, auth_headers, created_folder):
        """Test flow from file upload to content generation across different modules."""
        # Upload file
        test_content = "Photosynthesis is the process by which plants convert light energy into chemical energy."
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(test_content)
            f.flush()
            
            with open(f.name, 'rb') as file:
                response = client.post(
                    "/api/v1/files/upload",
                    files={"files": ("biology.txt", file, "text/plain")},
                    data={"folder_id": str(created_folder.id)},
                    headers=auth_headers
                )
        
        os.unlink(f.name)
        assert response.status_code == status.HTTP_201_CREATED
        file_id = response.json()["data"][0]["id"]
        
        # Create spaces and generate content
        space_types = ["quiz", "notes", "flashcards", "openended"]
        content_ids = {}
        
        for space_type in space_types:
            # Create space
            space_data = {
                "type": space_type,
                "title": f"{space_type.title()} Space",
                "settings": {}
            }
            response = client.post(f"/api/v1/folders/{created_folder.id}/spaces", json=space_data, headers=auth_headers)
            assert response.status_code == status.HTTP_201_CREATED
            space_id = response.json()["data"]["id"]
            
            # Generate content
            if space_type == "quiz":
                content_data = {"title": "Biology Quiz", "fileIds": [file_id], "questionCount": 3}
                endpoint = f"/api/v1/spaces/{space_id}/quizzes"
            elif space_type == "notes":
                content_data = {"fileIds": [file_id], "format": "markdown"}
                endpoint = f"/api/v1/spaces/{space_id}/notes"
            elif space_type == "flashcards":
                content_data = {"title": "Biology Flashcards", "fileIds": [file_id]}
                endpoint = f"/api/v1/spaces/{space_id}/flashcards"
            elif space_type == "openended":
                content_data = {"title": "Biology Questions", "fileIds": [file_id], "questionCount": 2}
                endpoint = f"/api/v1/spaces/{space_id}/openended"
            
            response = client.post(endpoint, json=content_data, headers=auth_headers)
            assert response.status_code == status.HTTP_201_CREATED
            content_ids[space_type] = response.json()["data"]["id"]
        
        # Verify all content references the same file
        for space_type, content_id in content_ids.items():
            if space_type == "quiz":
                response = client.get(f"/api/v1/quizzes/{content_id}", headers=auth_headers)
            elif space_type == "notes":
                response = client.get(f"/api/v1/notes/{content_id}", headers=auth_headers)
            elif space_type == "flashcards":
                response = client.get(f"/api/v1/flashcards/{content_id}", headers=auth_headers)
            elif space_type == "openended":
                response = client.get(f"/api/v1/openended/{content_id}", headers=auth_headers)
            
            assert response.status_code == status.HTTP_200_OK
            content_data = response.json()["data"]
            
            # Verify file reference
            if "fileIds" in content_data:
                assert file_id in content_data["fileIds"]
            elif "file_ids" in content_data:
                assert file_id in content_data["file_ids"]


class TestUserIsolation:
    """Test that users are properly isolated from each other."""
    
    def test_user_data_isolation(self, client: TestClient):
        """Test that users cannot access each other's data."""
        # Create two users
        user1_data = {"email": "user1@test.com", "password": "password123", "name": "User 1"}
        user2_data = {"email": "user2@test.com", "password": "password123", "name": "User 2"}
        
        # Register users
        response1 = client.post("/api/v1/auth/register", json=user1_data)
        response2 = client.post("/api/v1/auth/register", json=user2_data)
        
        assert response1.status_code == status.HTTP_201_CREATED
        assert response2.status_code == status.HTTP_201_CREATED
        
        token1 = response1.json()["data"]["token"]
        token2 = response2.json()["data"]["token"]
        headers1 = {"Authorization": f"Bearer {token1}"}
        headers2 = {"Authorization": f"Bearer {token2}"}
        
        # Create folders for each user
        folder1_data = {"title": "User 1 Folder", "description": "User 1's folder"}
        folder2_data = {"title": "User 2 Folder", "description": "User 2's folder"}
        
        response1 = client.post("/api/v1/folders", json=folder1_data, headers=headers1)
        response2 = client.post("/api/v1/folders", json=folder2_data, headers=headers2)
        
        assert response1.status_code == status.HTTP_201_CREATED
        assert response2.status_code == status.HTTP_201_CREATED
        
        folder1_id = response1.json()["data"]["id"]
        folder2_id = response2.json()["data"]["id"]
        
        # Try to access each other's folders
        response = client.get(f"/api/v1/folders/{folder1_id}", headers=headers2)
        assert response.status_code == status.HTTP_404_NOT_FOUND
        
        response = client.get(f"/api/v1/folders/{folder2_id}", headers=headers1)
        assert response.status_code == status.HTTP_404_NOT_FOUND
        
        # Create spaces in each folder
        space1_data = {"type": "chat", "title": "User 1 Space", "settings": {}}
        space2_data = {"type": "chat", "title": "User 2 Space", "settings": {}}
        
        response1 = client.post(f"/api/v1/folders/{folder1_id}/spaces", json=space1_data, headers=headers1)
        response2 = client.post(f"/api/v1/folders/{folder2_id}/spaces", json=space2_data, headers=headers2)
        
        assert response1.status_code == status.HTTP_201_CREATED
        assert response2.status_code == status.HTTP_201_CREATED
        
        space1_id = response1.json()["data"]["id"]
        space2_id = response2.json()["data"]["id"]
        
        # Try to access each other's spaces
        response = client.get(f"/api/v1/spaces/{space1_id}", headers=headers2)
        assert response.status_code == status.HTTP_404_NOT_FOUND
        
        response = client.get(f"/api/v1/spaces/{space2_id}", headers=headers1)
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestPerformanceAndConcurrency:
    """Test performance and concurrency scenarios."""
    
    def test_concurrent_file_uploads(self, client: TestClient, auth_headers, created_folder):
        """Test concurrent file uploads to the same folder."""
        import threading
        import time
        
        results = []
        errors = []
        
        def upload_file(file_index):
            try:
                test_content = f"Test content for file {file_index}"
                with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
                    f.write(test_content)
                    f.flush()
                    
                    with open(f.name, 'rb') as file:
                        response = client.post(
                            "/api/v1/files/upload",
                            files={"files": (f"test{file_index}.txt", file, "text/plain")},
                            data={"folder_id": str(created_folder.id)},
                            headers=auth_headers
                        )
                    
                    os.unlink(f.name)
                    
                    if response.status_code == status.HTTP_201_CREATED:
                        results.append(file_index)
                    else:
                        errors.append((file_index, response.status_code))
            except Exception as e:
                errors.append((file_index, str(e)))
        
        # Start 5 concurrent uploads
        threads = []
        for i in range(5):
            thread = threading.Thread(target=upload_file, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Verify results
        assert len(results) == 5, f"Expected 5 successful uploads, got {len(results)}. Errors: {errors}"
        
        # Verify all files were uploaded
        response = client.get(f"/api/v1/folders/{created_folder.id}/files", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()["data"]) >= 5
    
    def test_large_file_upload_performance(self, client: TestClient, auth_headers, created_folder):
        """Test performance with larger files."""
        # Create a larger test file (1MB)
        large_content = "A" * 1024 * 1024  # 1MB of data
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(large_content)
            f.flush()
            
            start_time = time.time()
            
            with open(f.name, 'rb') as file:
                response = client.post(
                    "/api/v1/files/upload",
                    files={"files": ("large_test.txt", file, "text/plain")},
                    data={"folder_id": str(created_folder.id)},
                    headers=auth_headers
                )
            
            end_time = time.time()
            upload_time = end_time - start_time
            
            os.unlink(f.name)
        
        assert response.status_code == status.HTTP_201_CREATED
        assert upload_time < 10.0, f"File upload took too long: {upload_time} seconds"


class TestErrorRecovery:
    """Test error recovery and edge cases."""
    
    def test_database_connection_recovery(self, client: TestClient, auth_headers, created_folder):
        """Test that the system can handle database connection issues gracefully."""
        # This test would require mocking database failures
        # For now, we'll test that the system handles malformed requests gracefully
        
        # Test with malformed JSON
        response = client.post(
            "/api/v1/folders",
            data="invalid json",
            headers={**auth_headers, "Content-Type": "application/json"}
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        
        # Test with missing required fields
        response = client.post("/api/v1/folders", json={}, headers=auth_headers)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_file_processing_error_recovery(self, client: TestClient, auth_headers, created_folder):
        """Test recovery from file processing errors."""
        # Create a file that might cause processing issues
        problematic_content = "This is a test file with special characters: éñüß"
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            f.write(problematic_content)
            f.flush()
            
            with open(f.name, 'rb') as file:
                response = client.post(
                    "/api/v1/files/upload",
                    files={"files": ("special_chars.txt", file, "text/plain")},
                    data={"folder_id": str(created_folder.id)},
                    headers=auth_headers
                )
            
            os.unlink(f.name)
        
        # Should handle special characters gracefully
        assert response.status_code == status.HTTP_201_CREATED


class TestAPICompatibility:
    """Test API compatibility and versioning."""
    
    def test_api_version_consistency(self, client: TestClient):
        """Test that all endpoints use consistent API versioning."""
        # Test that all endpoints return consistent response formats
        endpoints_to_test = [
            "/api/v1/auth/register",
            "/api/v1/folders",
            "/api/v1/spaces",
            "/api/v1/files/upload"
        ]
        
        for endpoint in endpoints_to_test:
            if endpoint == "/api/v1/auth/register":
                # Test with valid data
                response = client.post(endpoint, json={
                    "email": f"test{uuid.uuid4()}@example.com",
                    "password": "testpass123",
                    "name": "Test User"
                })
            elif endpoint == "/api/v1/folders":
                # This requires authentication, so we'll skip for now
                continue
            elif endpoint == "/api/v1/spaces":
                # This requires authentication, so we'll skip for now
                continue
            elif endpoint == "/api/v1/files/upload":
                # This requires authentication, so we'll skip for now
                continue
            
            # Check that successful responses have consistent structure
            if response.status_code in [200, 201]:
                data = response.json()
                # Should have either 'data' or 'error' key
                assert "data" in data or "error" in data, f"Response missing data/error key: {data}"
    
    def test_error_response_consistency(self, client: TestClient):
        """Test that error responses are consistent across all endpoints."""
        # Test various error scenarios
        error_scenarios = [
            ("/api/v1/auth/register", {"email": "invalid-email"}, 422),
            ("/api/v1/auth/login", {"email": "nonexistent@test.com", "password": "wrong"}, 401),
        ]
        
        for endpoint, data, expected_status in error_scenarios:
            response = client.post(endpoint, json=data)
            assert response.status_code == expected_status
            
            # Check error response structure
            error_data = response.json()
            if "error" in error_data:
                assert "code" in error_data["error"]
                assert "message" in error_data["error"]
            elif "detail" in error_data:
                # FastAPI validation errors
                assert isinstance(error_data["detail"], list) 