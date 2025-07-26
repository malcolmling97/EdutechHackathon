"""
Study Guides management endpoint tests for EdutechHackathon API.

Tests all study guides endpoints according to the API specification:
- POST /spaces/{spaceId}/studyguides - Create study guide
- GET /spaces/{spaceId}/studyguides - List study guides
- GET /studyguides/{id} - Retrieve study guide
- PATCH /studyguides/{id} - Update study guide
- DELETE /studyguides/{id} - Delete study guide
- POST /studyguides/{id}/sessions/{sessionId}/complete - Mark session complete
"""
import pytest
from datetime import datetime, timedelta
from fastapi import status
from fastapi.testclient import TestClient


class TestCreateStudyGuide:
    """Test study guide creation endpoint."""
    
    def test_create_study_guide_success(self, client: TestClient, auth_headers, created_space_studyguide, created_file):
        """Test successful study guide creation."""
        study_guide_data = {
            "title": "Final Exam Study Plan",
            "deadline": (datetime.utcnow() + timedelta(days=14)).isoformat() + "Z",
            "preferences": {
                "dailyStudyHours": 2,
                "preferredTimes": ["morning", "evening"],
                "breakInterval": 25,
                "studyMethods": ["reading", "flashcards", "practice"]
            },
            "file_ids": [str(created_file.id)],
            "topics": ["photosynthesis", "cellular respiration"]
        }
        
        response = client.post(
            f"/api/v1/spaces/{created_space_studyguide.id}/studyguides",
            json=study_guide_data,
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_201_CREATED
        
        data = response.json()
        assert "data" in data
        
        study_guide = data["data"]
        assert "id" in study_guide
        assert study_guide["spaceId"] == str(created_space_studyguide.id)
        assert study_guide["title"] == "Final Exam Study Plan"
        assert "deadline" in study_guide
        assert "totalStudyHours" in study_guide
        assert "schedule" in study_guide
        assert isinstance(study_guide["schedule"], list)
        assert "preferences" in study_guide
        assert "progress" in study_guide
        assert "createdAt" in study_guide
        assert "updatedAt" in study_guide
        
        # Verify preferences
        prefs = study_guide["preferences"]
        assert prefs["dailyStudyHours"] == 2
        assert prefs["preferredTimes"] == ["morning", "evening"]
        assert prefs["breakInterval"] == 25
        assert prefs["studyMethods"] == ["reading", "flashcards", "practice"]
        
        # Verify progress
        progress = study_guide["progress"]
        assert progress["completedHours"] == 0
        assert progress["completedSessions"] == 0
        assert progress["totalSessions"] > 0
    
    def test_create_study_guide_multiple_files(self, client: TestClient, auth_headers, created_space_studyguide, created_file, created_file_2):
        """Test study guide creation with multiple files."""
        study_guide_data = {
            "title": "Comprehensive Study Plan",
            "deadline": (datetime.utcnow() + timedelta(days=30)).isoformat() + "Z",
            "preferences": {
                "dailyStudyHours": 3,
                "preferredTimes": ["morning"],
                "breakInterval": 30,
                "studyMethods": ["reading", "practice"]
            },
            "file_ids": [str(created_file.id), str(created_file_2.id)],
            "topics": ["biology", "chemistry"]
        }
        
        response = client.post(
            f"/api/v1/spaces/{created_space_studyguide.id}/studyguides",
            json=study_guide_data,
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_201_CREATED
        
        data = response.json()
        study_guide = data["data"]
        assert len(study_guide["schedule"]) > 0
    
    def test_create_study_guide_invalid_space_type(self, client: TestClient, auth_headers, created_space, created_file):
        """Test study guide creation fails for wrong space type."""
        study_guide_data = {
            "title": "Study Plan",
            "deadline": (datetime.utcnow() + timedelta(days=7)).isoformat() + "Z",
            "preferences": {
                "dailyStudyHours": 2,
                "preferredTimes": ["morning"],
                "breakInterval": 25,
                "studyMethods": ["reading"]
            },
            "file_ids": [str(created_file.id)],
            "topics": ["topic1"]
        }
        
        response = client.post(
            f"/api/v1/spaces/{created_space.id}/studyguides",
            json=study_guide_data,
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        
        data = response.json()
        assert "error" in data
        assert data["error"]["code"] == "INVALID_SPACE_TYPE"
    
    def test_create_study_guide_no_files(self, client: TestClient, auth_headers, created_space_studyguide):
        """Test study guide creation fails without files."""
        study_guide_data = {
            "title": "Study Plan",
            "deadline": (datetime.utcnow() + timedelta(days=7)).isoformat() + "Z",
            "preferences": {
                "dailyStudyHours": 2,
                "preferredTimes": ["morning"],
                "breakInterval": 25,
                "studyMethods": ["reading"]
            },
            "file_ids": [],
            "topics": ["topic1"]
        }
        
        response = client.post(
            f"/api/v1/spaces/{created_space_studyguide.id}/studyguides",
            json=study_guide_data,
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_create_study_guide_nonexistent_files(self, client: TestClient, auth_headers, created_space_studyguide):
        """Test study guide creation fails with nonexistent files."""
        import uuid
        nonexistent_file_id = str(uuid.uuid4())
        
        study_guide_data = {
            "title": "Study Plan",
            "deadline": (datetime.utcnow() + timedelta(days=7)).isoformat() + "Z",
            "preferences": {
                "dailyStudyHours": 2,
                "preferredTimes": ["morning"],
                "breakInterval": 25,
                "studyMethods": ["reading"]
            },
            "file_ids": [nonexistent_file_id],
            "topics": ["topic1"]
        }
        
        response = client.post(
            f"/api/v1/spaces/{created_space_studyguide.id}/studyguides",
            json=study_guide_data,
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_create_study_guide_unauthorized_files(self, client: TestClient, auth_headers, created_space_studyguide, created_file_other_user):
        """Test study guide creation fails with unauthorized files."""
        study_guide_data = {
            "title": "Study Plan",
            "deadline": (datetime.utcnow() + timedelta(days=7)).isoformat() + "Z",
            "preferences": {
                "dailyStudyHours": 2,
                "preferredTimes": ["morning"],
                "breakInterval": 25,
                "studyMethods": ["reading"]
            },
            "file_ids": [str(created_file_other_user.id)],
            "topics": ["topic1"]
        }
        
        response = client.post(
            f"/api/v1/spaces/{created_space_studyguide.id}/studyguides",
            json=study_guide_data,
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_create_study_guide_past_deadline(self, client: TestClient, auth_headers, created_space_studyguide, created_file):
        """Test study guide creation fails with past deadline."""
        study_guide_data = {
            "title": "Study Plan",
            "deadline": (datetime.utcnow() - timedelta(days=1)).isoformat() + "Z",
            "preferences": {
                "dailyStudyHours": 2,
                "preferredTimes": ["morning"],
                "breakInterval": 25,
                "studyMethods": ["reading"]
            },
            "file_ids": [str(created_file.id)],
            "topics": ["topic1"]
        }
        
        response = client.post(
            f"/api/v1/spaces/{created_space_studyguide.id}/studyguides",
            json=study_guide_data,
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        
        data = response.json()
        assert "error" in data
        assert data["error"]["code"] == "INVALID_DEADLINE"
    
    def test_create_study_guide_invalid_preferences(self, client: TestClient, auth_headers, created_space_studyguide, created_file):
        """Test study guide creation fails with invalid preferences."""
        study_guide_data = {
            "title": "Study Plan",
            "deadline": (datetime.utcnow() + timedelta(days=7)).isoformat() + "Z",
            "preferences": {
                "dailyStudyHours": 0,  # Invalid: must be > 0
                "preferredTimes": ["morning"],
                "breakInterval": 25,
                "studyMethods": ["reading"]
            },
            "file_ids": [str(created_file.id)],
            "topics": ["topic1"]
        }
        
        response = client.post(
            f"/api/v1/spaces/{created_space_studyguide.id}/studyguides",
            json=study_guide_data,
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_create_study_guide_nonexistent_space(self, client: TestClient, auth_headers, created_file):
        """Test study guide creation fails with nonexistent space."""
        import uuid
        nonexistent_space_id = str(uuid.uuid4())
        
        study_guide_data = {
            "title": "Study Plan",
            "deadline": (datetime.utcnow() + timedelta(days=7)).isoformat() + "Z",
            "preferences": {
                "dailyStudyHours": 2,
                "preferredTimes": ["morning"],
                "breakInterval": 25,
                "studyMethods": ["reading"]
            },
            "file_ids": [str(created_file.id)],
            "topics": ["topic1"]
        }
        
        response = client.post(
            f"/api/v1/spaces/{nonexistent_space_id}/studyguides",
            json=study_guide_data,
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_create_study_guide_unauthorized_space(self, client: TestClient, auth_headers, created_space_studyguide_other_user, created_file):
        """Test study guide creation fails with unauthorized space."""
        study_guide_data = {
            "title": "Study Plan",
            "deadline": (datetime.utcnow() + timedelta(days=7)).isoformat() + "Z",
            "preferences": {
                "dailyStudyHours": 2,
                "preferredTimes": ["morning"],
                "breakInterval": 25,
                "studyMethods": ["reading"]
            },
            "file_ids": [str(created_file.id)],
            "topics": ["topic1"]
        }
        
        response = client.post(
            f"/api/v1/spaces/{created_space_studyguide_other_user.id}/studyguides",
            json=study_guide_data,
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_create_study_guide_unauthenticated(self, client: TestClient, created_space_studyguide, created_file):
        """Test study guide creation fails without authentication."""
        study_guide_data = {
            "title": "Study Plan",
            "deadline": (datetime.utcnow() + timedelta(days=7)).isoformat() + "Z",
            "preferences": {
                "dailyStudyHours": 2,
                "preferredTimes": ["morning"],
                "breakInterval": 25,
                "studyMethods": ["reading"]
            },
            "file_ids": [str(created_file.id)],
            "topics": ["topic1"]
        }
        
        response = client.post(
            f"/api/v1/spaces/{created_space_studyguide.id}/studyguides",
            json=study_guide_data
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestListStudyGuides:
    """Test study guides listing endpoint."""
    
    def test_list_study_guides_empty(self, client: TestClient, auth_headers, created_space_studyguide):
        """Test listing study guides when none exist."""
        response = client.get(
            f"/api/v1/spaces/{created_space_studyguide.id}/studyguides",
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert "data" in data
        assert "meta" in data
        assert data["data"] == []
        assert data["meta"]["page"] == 1
        assert data["meta"]["limit"] == 20
        assert data["meta"]["total"] == 0
    
    def test_list_study_guides_with_data(self, client: TestClient, auth_headers, created_space_studyguide, created_study_guide):
        """Test listing study guides with existing data."""
        response = client.get(
            f"/api/v1/spaces/{created_space_studyguide.id}/studyguides",
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert "data" in data
        assert "meta" in data
        assert len(data["data"]) == 1
        assert data["meta"]["total"] == 1
        
        study_guide = data["data"][0]
        assert study_guide["id"] == str(created_study_guide.id)
        assert study_guide["spaceId"] == str(created_space_studyguide.id)
        assert "title" in study_guide
        assert "deadline" in study_guide
        assert "schedule" in study_guide
        assert "preferences" in study_guide
        assert "progress" in study_guide
    
    def test_list_study_guides_pagination(self, client: TestClient, auth_headers, created_space_studyguide, created_file):
        """Test study guides listing with pagination."""
        # Create multiple study guides
        for i in range(25):
            study_guide_data = {
                "title": f"Study Plan {i+1}",
                "deadline": (datetime.utcnow() + timedelta(days=7)).isoformat() + "Z",
                "preferences": {
                    "dailyStudyHours": 2,
                    "preferredTimes": ["morning"],
                    "breakInterval": 25,
                    "studyMethods": ["reading"]
                },
                "file_ids": [str(created_file.id)],
                "topics": [f"topic{i}"]
            }
            
            client.post(
                f"/api/v1/spaces/{created_space_studyguide.id}/studyguides",
                json=study_guide_data,
                headers=auth_headers
            )
        
        # Test first page
        response = client.get(
            f"/api/v1/spaces/{created_space_studyguide.id}/studyguides?page=1&limit=10",
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert len(data["data"]) == 10
        assert data["meta"]["page"] == 1
        assert data["meta"]["limit"] == 10
        assert data["meta"]["total"] == 25
        
        # Test second page
        response = client.get(
            f"/api/v1/spaces/{created_space_studyguide.id}/studyguides?page=2&limit=10",
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert len(data["data"]) == 10
        assert data["meta"]["page"] == 2
    
    def test_list_study_guides_invalid_space_type(self, client: TestClient, auth_headers, created_space):
        """Test listing study guides fails for wrong space type."""
        response = client.get(
            f"/api/v1/spaces/{created_space.id}/studyguides",
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        
        data = response.json()
        assert "error" in data
        assert data["error"]["code"] == "INVALID_SPACE_TYPE"
    
    def test_list_study_guides_nonexistent_space(self, client: TestClient, auth_headers):
        """Test listing study guides fails for nonexistent space."""
        import uuid
        nonexistent_space_id = str(uuid.uuid4())
        
        response = client.get(
            f"/api/v1/spaces/{nonexistent_space_id}/studyguides",
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_list_study_guides_unauthorized_space(self, client: TestClient, auth_headers, created_space_studyguide_other_user):
        """Test listing study guides fails for unauthorized space."""
        response = client.get(
            f"/api/v1/spaces/{created_space_studyguide_other_user.id}/studyguides",
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_list_study_guides_unauthenticated(self, client: TestClient, created_space_studyguide):
        """Test listing study guides fails without authentication."""
        response = client.get(
            f"/api/v1/spaces/{created_space_studyguide.id}/studyguides"
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestGetStudyGuide:
    """Test study guide retrieval endpoint."""
    
    def test_get_study_guide_success(self, client: TestClient, auth_headers, created_study_guide):
        """Test successful study guide retrieval."""
        response = client.get(
            f"/api/v1/studyguides/{created_study_guide.id}",
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert "data" in data
        
        study_guide = data["data"]
        assert study_guide["id"] == str(created_study_guide.id)
        assert "title" in study_guide
        assert "deadline" in study_guide
        assert "totalStudyHours" in study_guide
        assert "schedule" in study_guide
        assert "preferences" in study_guide
        assert "progress" in study_guide
        assert "createdAt" in study_guide
        assert "updatedAt" in study_guide
    
    def test_get_study_guide_nonexistent(self, client: TestClient, auth_headers):
        """Test study guide retrieval fails for nonexistent study guide."""
        import uuid
        nonexistent_id = str(uuid.uuid4())
        
        response = client.get(
            f"/api/v1/studyguides/{nonexistent_id}",
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_get_study_guide_unauthorized(self, client: TestClient, auth_headers, created_study_guide_other_user):
        """Test study guide retrieval fails for unauthorized study guide."""
        response = client.get(
            f"/api/v1/studyguides/{created_study_guide_other_user.id}",
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_get_study_guide_unauthenticated(self, client: TestClient, created_study_guide):
        """Test study guide retrieval fails without authentication."""
        response = client.get(
            f"/api/v1/studyguides/{created_study_guide.id}"
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_get_study_guide_invalid_uuid(self, client: TestClient, auth_headers):
        """Test study guide retrieval fails with invalid UUID."""
        response = client.get(
            "/api/v1/studyguides/invalid-uuid",
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestUpdateStudyGuide:
    """Test study guide update endpoint."""
    
    def test_update_study_guide_success(self, client: TestClient, auth_headers, created_study_guide):
        """Test successful study guide update."""
        update_data = {
            "title": "Updated Study Plan",
            "preferences": {
                "dailyStudyHours": 3,
                "preferredTimes": ["evening"],
                "breakInterval": 30,
                "studyMethods": ["reading", "practice"]
            }
        }
        
        response = client.patch(
            f"/api/v1/studyguides/{created_study_guide.id}",
            json=update_data,
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        study_guide = data["data"]
        assert study_guide["title"] == "Updated Study Plan"
        assert study_guide["preferences"]["dailyStudyHours"] == 3
        assert study_guide["preferences"]["preferredTimes"] == ["evening"]
    
    def test_update_study_guide_partial(self, client: TestClient, auth_headers, created_study_guide):
        """Test partial study guide update."""
        original_title = created_study_guide.title
        
        update_data = {
            "preferences": {
                "dailyStudyHours": 4
            }
        }
        
        response = client.patch(
            f"/api/v1/studyguides/{created_study_guide.id}",
            json=update_data,
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        study_guide = data["data"]
        assert study_guide["title"] == original_title  # Should remain unchanged
        assert study_guide["preferences"]["dailyStudyHours"] == 4
    
    def test_update_study_guide_nonexistent(self, client: TestClient, auth_headers):
        """Test study guide update fails for nonexistent study guide."""
        import uuid
        nonexistent_id = str(uuid.uuid4())
        
        update_data = {
            "title": "Updated Title"
        }
        
        response = client.patch(
            f"/api/v1/studyguides/{nonexistent_id}",
            json=update_data,
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_update_study_guide_unauthorized(self, client: TestClient, auth_headers, created_study_guide_other_user):
        """Test study guide update fails for unauthorized study guide."""
        update_data = {
            "title": "Updated Title"
        }
        
        response = client.patch(
            f"/api/v1/studyguides/{created_study_guide_other_user.id}",
            json=update_data,
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_update_study_guide_unauthenticated(self, client: TestClient, created_study_guide):
        """Test study guide update fails without authentication."""
        update_data = {
            "title": "Updated Title"
        }
        
        response = client.patch(
            f"/api/v1/studyguides/{created_study_guide.id}",
            json=update_data
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_update_study_guide_invalid_preferences(self, client: TestClient, auth_headers, created_study_guide):
        """Test study guide update fails with invalid preferences."""
        update_data = {
            "preferences": {
                "dailyStudyHours": -1  # Invalid: must be > 0
            }
        }
        
        response = client.patch(
            f"/api/v1/studyguides/{created_study_guide.id}",
            json=update_data,
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestDeleteStudyGuide:
    """Test study guide deletion endpoint."""
    
    def test_delete_study_guide_success(self, client: TestClient, auth_headers, created_study_guide):
        """Test successful study guide deletion."""
        response = client.delete(
            f"/api/v1/studyguides/{created_study_guide.id}",
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
        
        # Verify it's actually deleted
        get_response = client.get(
            f"/api/v1/studyguides/{created_study_guide.id}",
            headers=auth_headers
        )
        
        assert get_response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_delete_study_guide_nonexistent(self, client: TestClient, auth_headers):
        """Test study guide deletion fails for nonexistent study guide."""
        import uuid
        nonexistent_id = str(uuid.uuid4())
        
        response = client.delete(
            f"/api/v1/studyguides/{nonexistent_id}",
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_delete_study_guide_unauthorized(self, client: TestClient, auth_headers, created_study_guide_other_user):
        """Test study guide deletion fails for unauthorized study guide."""
        response = client.delete(
            f"/api/v1/studyguides/{created_study_guide_other_user.id}",
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_delete_study_guide_unauthenticated(self, client: TestClient, created_study_guide):
        """Test study guide deletion fails without authentication."""
        response = client.delete(
            f"/api/v1/studyguides/{created_study_guide.id}"
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_delete_study_guide_invalid_uuid(self, client: TestClient, auth_headers):
        """Test study guide deletion fails with invalid UUID."""
        response = client.delete(
            "/api/v1/studyguides/invalid-uuid",
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestCompleteStudySession:
    """Test study session completion endpoint."""
    
    def test_complete_study_session_success(self, client: TestClient, auth_headers, created_study_guide):
        """Test successful study session completion."""
        # Get the first session ID from the study guide
        session_id = created_study_guide.schedule[0]["id"] if created_study_guide.schedule else "session1"
        
        response = client.post(
            f"/api/v1/studyguides/{created_study_guide.id}/sessions/{session_id}/complete",
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert "data" in data
        
        study_guide = data["data"]
        assert study_guide["progress"]["completedSessions"] > 0
    
    def test_complete_study_session_nonexistent_study_guide(self, client: TestClient, auth_headers):
        """Test session completion fails for nonexistent study guide."""
        import uuid
        nonexistent_id = str(uuid.uuid4())
        
        response = client.post(
            f"/api/v1/studyguides/{nonexistent_id}/sessions/session1/complete",
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_complete_study_session_nonexistent_session(self, client: TestClient, auth_headers, created_study_guide):
        """Test session completion fails for nonexistent session."""
        response = client.post(
            f"/api/v1/studyguides/{created_study_guide.id}/sessions/nonexistent-session/complete",
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_complete_study_session_unauthorized(self, client: TestClient, auth_headers, created_study_guide_other_user):
        """Test session completion fails for unauthorized study guide."""
        response = client.post(
            f"/api/v1/studyguides/{created_study_guide_other_user.id}/sessions/session1/complete",
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_complete_study_session_unauthenticated(self, client: TestClient, created_study_guide):
        """Test session completion fails without authentication."""
        response = client.post(
            f"/api/v1/studyguides/{created_study_guide.id}/sessions/session1/complete"
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestStudyGuidesIntegration:
    """Integration tests for study guides workflow."""
    
    def test_full_study_guides_workflow(self, client: TestClient, auth_headers, created_space_studyguide, created_file):
        """Test complete study guides workflow."""
        # 1. Create study guide
        study_guide_data = {
            "title": "Integration Test Study Plan",
            "deadline": (datetime.utcnow() + timedelta(days=7)).isoformat() + "Z",
            "preferences": {
                "dailyStudyHours": 2,
                "preferredTimes": ["morning"],
                "breakInterval": 25,
                "studyMethods": ["reading"]
            },
            "file_ids": [str(created_file.id)],
            "topics": ["integration", "testing"]
        }
        
        create_response = client.post(
            f"/api/v1/spaces/{created_space_studyguide.id}/studyguides",
            json=study_guide_data,
            headers=auth_headers
        )
        
        assert create_response.status_code == status.HTTP_201_CREATED
        
        study_guide_id = create_response.json()["data"]["id"]
        
        # 2. List study guides
        list_response = client.get(
            f"/api/v1/spaces/{created_space_studyguide.id}/studyguides",
            headers=auth_headers
        )
        
        assert list_response.status_code == status.HTTP_200_OK
        assert len(list_response.json()["data"]) == 1
        
        # 3. Get specific study guide
        get_response = client.get(
            f"/api/v1/studyguides/{study_guide_id}",
            headers=auth_headers
        )
        
        assert get_response.status_code == status.HTTP_200_OK
        
        # 4. Update study guide
        update_data = {
            "title": "Updated Integration Test Study Plan"
        }
        
        update_response = client.patch(
            f"/api/v1/studyguides/{study_guide_id}",
            json=update_data,
            headers=auth_headers
        )
        
        assert update_response.status_code == status.HTTP_200_OK
        assert update_response.json()["data"]["title"] == "Updated Integration Test Study Plan"
        
        # 5. Complete a study session
        session_id = update_response.json()["data"]["schedule"][0]["id"] if update_response.json()["data"]["schedule"] else "session1"
        
        complete_response = client.post(
            f"/api/v1/studyguides/{study_guide_id}/sessions/{session_id}/complete",
            headers=auth_headers
        )
        
        assert complete_response.status_code == status.HTTP_200_OK
        
        # 6. Delete study guide
        delete_response = client.delete(
            f"/api/v1/studyguides/{study_guide_id}",
            headers=auth_headers
        )
        
        assert delete_response.status_code == status.HTTP_204_NO_CONTENT
        
        # 7. Verify deletion
        verify_response = client.get(
            f"/api/v1/studyguides/{study_guide_id}",
            headers=auth_headers
        )
        
        assert verify_response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_study_guides_space_deletion_cascade(self, client: TestClient, auth_headers, created_space_studyguide, created_study_guide):
        """Test that study guides are deleted when their space is deleted."""
        study_guide_id = str(created_study_guide.id)
        
        # Verify study guide exists
        get_response = client.get(
            f"/api/v1/studyguides/{study_guide_id}",
            headers=auth_headers
        )
        
        assert get_response.status_code == status.HTTP_200_OK
        
        # Delete the space
        delete_space_response = client.delete(
            f"/api/v1/spaces/{created_space_studyguide.id}",
            headers=auth_headers
        )
        
        assert delete_space_response.status_code == status.HTTP_204_NO_CONTENT
        
        # Verify study guide is also deleted
        verify_response = client.get(
            f"/api/v1/studyguides/{study_guide_id}",
            headers=auth_headers
        )
        
        assert verify_response.status_code == status.HTTP_404_NOT_FOUND 