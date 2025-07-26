"""
Open-ended Questions management endpoint tests for EdutechHackathon API.

Tests all open-ended question endpoints according to the API specification:
- POST /openended/generate - Generate open-ended questions
- GET /openended/list - List open-ended question sets
- GET /openended/{id} - Retrieve question set
- POST /openended/{id}/submit - Submit answers for AI grading
- GET /openended/{id}/answers - Get user's submitted answers and grades
- DELETE /openended/{id} - Delete question set
"""
import pytest
from fastapi import status
from fastapi.testclient import TestClient
import uuid


class TestGenerateOpenEndedQuestions:
    """Test open-ended question generation endpoint."""
    
    def test_generate_openended_success(self, client: TestClient, auth_headers, created_space, uploaded_files):
        """Test successful open-ended question generation."""
        openended_data = {
            "spaceId": str(created_space.id),
            "title": "Photosynthesis Essay Questions",
            "fileIds": [str(uploaded_files[0].id), str(uploaded_files[1].id)],
            "questionCount": 3,
            "difficulty": "medium",
            "maxWords": 500,
            "topics": ["light reactions", "calvin cycle", "chloroplast structure"]
        }
        
        response = client.post(
            "/api/v1/openended/generate",
            json=openended_data,
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_201_CREATED
        
        data = response.json()
        assert "data" in data
        openended = data["data"]
        
        assert "id" in openended
        assert openended["spaceId"] == str(created_space.id)
        assert openended["title"] == "Photosynthesis Essay Questions"
        assert "questions" in openended
        assert len(openended["questions"]) == 3  # Mock AI service should generate 3 questions
        assert "createdAt" in openended
        
        # Verify question structure
        for question in openended["questions"]:
            assert "id" in question
            assert "prompt" in question
            assert "maxWords" in question
            assert question["maxWords"] == 500
            assert "rubric" in question
            assert "criteria" in question["rubric"]
            assert len(question["rubric"]["criteria"]) > 0
            
            # Verify rubric criteria structure
            for criterion in question["rubric"]["criteria"]:
                assert "name" in criterion
                assert "weight" in criterion
                assert "description" in criterion
                assert 0 < criterion["weight"] <= 1
    
    def test_generate_openended_with_minimal_data(self, client: TestClient, auth_headers, created_space, uploaded_files):
        """Test open-ended question generation with minimal required fields."""
        openended_data = {
            "spaceId": str(created_space.id),
            "title": "Simple Essay Questions",
            "fileIds": [str(uploaded_files[0].id)]
        }
        
        response = client.post(
            "/api/v1/openended/generate",
            json=openended_data,
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_201_CREATED
        
        data = response.json()
        openended = data["data"]
        
        assert openended["title"] == "Simple Essay Questions"
        assert len(openended["questions"]) == 10  # Default question count
    
    def test_generate_openended_invalid_space(self, client: TestClient, auth_headers, uploaded_files):
        """Test open-ended question generation with invalid space ID."""
        openended_data = {
            "spaceId": str(uuid.uuid4()),  # Non-existent space
            "title": "Test Essay Questions",
            "fileIds": [str(uploaded_files[0].id)]
        }
        
        response = client.post(
            "/api/v1/openended/generate",
            json=openended_data,
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        data = response.json()
        assert "error" in data
    
    def test_generate_openended_files_not_owned(self, client: TestClient, auth_headers, created_space, other_user_files):
        """Test open-ended question generation with files not owned by user."""
        openended_data = {
            "spaceId": str(created_space.id),
            "title": "Test Essay Questions",
            "fileIds": [str(other_user_files[0].id)]
        }
        
        response = client.post(
            "/api/v1/openended/generate",
            json=openended_data,
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_generate_openended_validation_errors(self, client: TestClient, auth_headers, created_space):
        """Test open-ended question generation with validation errors."""
        # Test empty title
        openended_data = {
            "spaceId": str(created_space.id),
            "title": "",
            "fileIds": ["invalid-uuid"]
        }
        
        response = client.post(
            "/api/v1/openended/generate",
            json=openended_data,
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_generate_openended_unauthorized(self, client: TestClient, created_space, uploaded_files):
        """Test open-ended question generation without authentication."""
        openended_data = {
            "spaceId": str(created_space.id),
            "title": "Test Essay Questions",
            "fileIds": [str(uploaded_files[0].id)]
        }
        
        response = client.post(
            "/api/v1/openended/generate",
            json=openended_data
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestListOpenEndedQuestions:
    """Test open-ended question listing endpoint."""
    
    def test_list_openended_empty(self, client: TestClient, auth_headers, created_space):
        """Test listing open-ended questions when none exist."""
        response = client.get(
            f"/api/v1/openended/list?space_id={created_space.id}",
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert "data" in data
        assert "meta" in data
        assert len(data["data"]) == 0
        assert data["meta"]["total"] == 0
    
    def test_list_openended_with_data(self, client: TestClient, auth_headers, created_space, created_openended_in_space):
        """Test listing open-ended questions with existing data."""
        response = client.get(
            f"/api/v1/openended/list?space_id={created_space.id}",
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert "data" in data
        assert "meta" in data
        assert len(data["data"]) == 1
        assert data["meta"]["total"] == 1
        
        openended = data["data"][0]
        assert openended["id"] == str(created_openended_in_space.id)
        assert openended["title"] == created_openended_in_space.title
    
    def test_list_openended_pagination(self, client: TestClient, auth_headers, created_space_openended, uploaded_files):
        """Test open-ended question listing with pagination."""
        # Create multiple open-ended question sets
        for i in range(25):
            openended_data = {
                "spaceId": str(created_space_openended.id),
                "title": f"Essay Questions Set {i+1}",
                "fileIds": [str(uploaded_files[0].id)]
            }
            
            client.post(
                "/api/v1/openended/generate",
                json=openended_data,
                headers=auth_headers
            )
        
        # Test first page
        response = client.get(
            f"/api/v1/openended/list?space_id={created_space_openended.id}&page=1&limit=10",
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert len(data["data"]) == 10
        assert data["meta"]["page"] == 1
        assert data["meta"]["limit"] == 10
        assert data["meta"]["total"] >= 25
    
    def test_list_openended_invalid_space(self, client: TestClient, auth_headers):
        """Test listing open-ended questions with invalid space ID."""
        response = client.get(
            "/api/v1/openended/list?space_id=invalid-uuid",
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_list_openended_unauthorized(self, client: TestClient, created_space):
        """Test listing open-ended questions without authentication."""
        response = client.get(f"/api/v1/openended/list?space_id={created_space.id}")
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestGetOpenEndedDetail:
    """Test open-ended question detail retrieval endpoint."""
    
    def test_get_openended_success(self, client: TestClient, auth_headers, created_openended):
        """Test successful open-ended question retrieval."""
        response = client.get(
            f"/api/v1/openended/{created_openended.id}",
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert "data" in data
        openended = data["data"]
        
        assert openended["id"] == str(created_openended.id)
        assert openended["title"] == created_openended.title
        assert "questions" in openended
    
    def test_get_openended_invalid_id(self, client: TestClient, auth_headers):
        """Test open-ended question retrieval with invalid ID."""
        response = client.get(
            "/api/v1/openended/invalid-uuid",
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_get_openended_not_owned(self, client: TestClient, auth_headers, other_user_openended):
        """Test retrieval of open-ended question set not owned by user."""
        response = client.get(
            f"/api/v1/openended/{other_user_openended.id}",
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_get_openended_unauthorized(self, client: TestClient, created_openended):
        """Test open-ended question retrieval without authentication."""
        response = client.get(f"/api/v1/openended/{created_openended.id}")
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestSubmitOpenEndedAnswers:
    """Test open-ended answer submission endpoint."""
    
    def test_submit_openended_answers_success(self, client: TestClient, auth_headers, created_openended):
        """Test successful open-ended answer submission."""
        submission_data = {
            "answers": [
                {
                    "questionId": created_openended.questions[0]["id"],
                    "answer": "This is a detailed answer to the open-ended question. It provides comprehensive explanation of the topic with relevant examples and demonstrates understanding of the subject matter."
                },
                {
                    "questionId": created_openended.questions[1]["id"],
                    "answer": "Another detailed answer that addresses the second question thoroughly."
                }
            ]
        }
        
        response = client.post(
            f"/api/v1/openended/{created_openended.id}/submit",
            json=submission_data,
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_201_CREATED
        
        data = response.json()
        assert "data" in data
        result = data["data"]
        
        assert "score" in result
        assert "totalQuestions" in result
        assert "feedback" in result
        assert "submittedAt" in result
        
        # Verify feedback structure
        assert len(result["feedback"]) == 2
        for feedback in result["feedback"]:
            assert "questionId" in feedback
            assert "userAnswer" in feedback
            assert "correctAnswer" in feedback
            assert "isCorrect" in feedback
            assert "feedback" in feedback
    
    def test_submit_openended_answers_partial(self, client: TestClient, auth_headers, created_openended):
        """Test partial open-ended answer submission."""
        submission_data = {
            "answers": [
                {
                    "questionId": created_openended.questions[0]["id"],
                    "answer": "Partial answer to only one question."
                }
            ]
        }
        
        response = client.post(
            f"/api/v1/openended/{created_openended.id}/submit",
            json=submission_data,
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_201_CREATED
        
        data = response.json()
        result = data["data"]
        assert len(result["feedback"]) == 1
    
    def test_submit_openended_answers_invalid_question(self, client: TestClient, auth_headers, created_openended):
        """Test submission with invalid question ID."""
        submission_data = {
            "answers": [
                {
                    "questionId": "invalid-question-id",
                    "answer": "Some answer text."
                }
            ]
        }
        
        response = client.post(
            f"/api/v1/openended/{created_openended.id}/submit",
            json=submission_data,
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_submit_openended_answers_validation_errors(self, client: TestClient, auth_headers, created_openended):
        """Test submission with validation errors."""
        # Test empty answers
        submission_data = {
            "answers": []
        }
        
        response = client.post(
            f"/api/v1/openended/{created_openended.id}/submit",
            json=submission_data,
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_submit_openended_answers_not_owned(self, client: TestClient, auth_headers, other_user_openended):
        """Test submission for open-ended question set not owned by user."""
        submission_data = {
            "answers": [
                {
                    "questionId": other_user_openended.questions[0]["id"],
                    "answer": "Some answer text."
                }
            ]
        }
        
        response = client.post(
            f"/api/v1/openended/{other_user_openended.id}/submit",
            json=submission_data,
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_submit_openended_answers_unauthorized(self, client: TestClient, created_openended):
        """Test open-ended answer submission without authentication."""
        submission_data = {
            "answers": [
                {
                    "questionId": created_openended.questions[0]["id"],
                    "answer": "Unauthorized submission attempt."
                }
            ]
        }
        
        response = client.post(
            f"/api/v1/openended/{created_openended.id}/submit",
            json=submission_data
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestGetOpenEndedAnswers:
    """Test open-ended answer retrieval endpoint."""
    
    def test_get_openended_answers_success(self, client: TestClient, auth_headers, created_openended):
        """Test successful open-ended answer retrieval."""
        # First submit some answers
        submission_data = {
            "answers": [
                {
                    "questionId": created_openended.questions[0]["id"],
                    "answer": "Test answer for grading."
                }
            ]
        }
        
        client.post(
            f"/api/v1/openended/{created_openended.id}/submit",
            json=submission_data,
            headers=auth_headers
        )
        
        # Then retrieve answers
        response = client.get(
            f"/api/v1/openended/{created_openended.id}/answers",
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert "data" in data
        answers = data["data"]
        
        assert len(answers) == 1
        answer = answers[0]
        
        assert "id" in answer
        assert "questionId" in answer
        assert "userId" in answer
        assert "answer" in answer
        assert "wordCount" in answer
        assert "grade" in answer
        assert "submittedAt" in answer
    
    def test_get_openended_answers_empty(self, client: TestClient, auth_headers, created_openended):
        """Test retrieval when no answers have been submitted."""
        response = client.get(
            f"/api/v1/openended/{created_openended.id}/answers",
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert "data" in data
        assert len(data["data"]) == 0
    
    def test_get_openended_answers_invalid_id(self, client: TestClient, auth_headers):
        """Test answer retrieval with invalid ID."""
        response = client.get(
            "/api/v1/openended/invalid-uuid/answers",
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_get_openended_answers_not_owned(self, client: TestClient, auth_headers, other_user_openended):
        """Test retrieval for open-ended question set not owned by user."""
        response = client.get(
            f"/api/v1/openended/{other_user_openended.id}/answers",
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_get_openended_answers_unauthorized(self, client: TestClient, created_openended):
        """Test open-ended answer retrieval without authentication."""
        response = client.get(f"/api/v1/openended/{created_openended.id}/answers")
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestDeleteOpenEnded:
    """Test open-ended question deletion endpoint."""
    
    def test_delete_openended_success(self, client: TestClient, auth_headers, created_openended):
        """Test successful open-ended question deletion."""
        response = client.delete(
            f"/api/v1/openended/{created_openended.id}",
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
        
        # Verify deletion
        get_response = client.get(
            f"/api/v1/openended/{created_openended.id}",
            headers=auth_headers
        )
        
        assert get_response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_delete_openended_invalid_id(self, client: TestClient, auth_headers):
        """Test deletion with invalid ID."""
        response = client.delete(
            "/api/v1/openended/invalid-uuid",
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_delete_openended_not_owned(self, client: TestClient, auth_headers, other_user_openended):
        """Test deletion of open-ended question set not owned by user."""
        response = client.delete(
            f"/api/v1/openended/{other_user_openended.id}",
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_delete_openended_unauthorized(self, client: TestClient, created_openended):
        """Test open-ended question deletion without authentication."""
        response = client.delete(f"/api/v1/openended/{created_openended.id}")
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_delete_openended_cascade_answers(self, client: TestClient, auth_headers, created_openended):
        """Test that deleting open-ended questions also deletes associated answers."""
        # First submit some answers
        submission_data = {
            "answers": [
                {
                    "questionId": created_openended.questions[0]["id"],
                    "answer": "Test answer for cascade deletion."
                }
            ]
        }
        
        client.post(
            f"/api/v1/openended/{created_openended.id}/submit",
            json=submission_data,
            headers=auth_headers
        )
        
        # Delete the open-ended question set
        response = client.delete(
            f"/api/v1/openended/{created_openended.id}",
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
        
        # Verify that answers are also deleted (should return 404)
        answers_response = client.get(
            f"/api/v1/openended/{created_openended.id}/answers",
            headers=auth_headers
        )
        
        assert answers_response.status_code == status.HTTP_404_NOT_FOUND 