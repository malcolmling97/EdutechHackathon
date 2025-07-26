"""
Quiz management endpoint tests for EdutechHackathon API.

Tests all quiz endpoints according to the API specification:
- POST /spaces/{spaceId}/quizzes - Generate quiz from selected files + params
- GET /spaces/{spaceId}/quizzes - List quizzes  
- GET /quizzes/{id} - Quiz detail
- POST /quizzes/{id}/submit - Grade answers
- DELETE /quizzes/{id} - Delete quiz
"""
import pytest
from fastapi import status
from fastapi.testclient import TestClient
import uuid


class TestGenerateQuiz:
    """Test quiz generation endpoint."""
    
    def test_generate_quiz_success(self, client: TestClient, auth_headers, created_space, uploaded_files):
        """Test successful quiz generation."""
        quiz_data = {
            "title": "Chapter 3 Quiz",
            "fileIds": [str(uploaded_files[0].id), str(uploaded_files[1].id)],
            "questionCount": 10,
            "questionTypes": ["mcq", "tf"],
            "difficulty": "medium"
        }
        
        response = client.post(
            f"/api/v1/spaces/{created_space.id}/quizzes",
            json=quiz_data,
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_201_CREATED
        
        data = response.json()
        assert "data" in data
        quiz = data["data"]
        
        assert "id" in quiz
        assert quiz["spaceId"] == str(created_space.id)
        assert quiz["title"] == "Chapter 3 Quiz"
        assert "questions" in quiz
        assert len(quiz["questions"]) == 10  # Mock AI service should generate 10 questions
        assert "createdAt" in quiz
        
        # Verify question structure
        for question in quiz["questions"]:
            assert "id" in question
            assert "type" in question
            assert question["type"] in ["mcq", "tf"]
            assert "prompt" in question
            if question["type"] == "mcq":
                assert "choices" in question
                assert len(question["choices"]) == 4
            assert "answer" in question
    
    def test_generate_quiz_with_minimal_data(self, client: TestClient, auth_headers, created_space, uploaded_files):
        """Test quiz generation with minimal required fields."""
        quiz_data = {
            "title": "Simple Quiz",
            "fileIds": [str(uploaded_files[0].id)]
        }
        
        response = client.post(
            f"/api/v1/spaces/{created_space.id}/quizzes",
            json=quiz_data,
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_201_CREATED
        
        data = response.json()
        quiz = data["data"]
        
        assert quiz["title"] == "Simple Quiz"
        assert len(quiz["questions"]) == 10  # Default question count
    
    def test_generate_quiz_invalid_space(self, client: TestClient, auth_headers, uploaded_files):
        """Test quiz generation with invalid space ID."""
        quiz_data = {
            "title": "Test Quiz",
            "fileIds": [str(uploaded_files[0].id)]
        }
        
        invalid_space_id = str(uuid.uuid4())
        response = client.post(
            f"/api/v1/spaces/{invalid_space_id}/quizzes",
            json=quiz_data,
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        
        error = response.json()
        assert "error" in error
        assert error["error"]["code"] == "SPACE_NOT_FOUND"
    
    def test_generate_quiz_invalid_files(self, client: TestClient, auth_headers, created_space):
        """Test quiz generation with non-existent file IDs."""
        quiz_data = {
            "title": "Test Quiz",
            "fileIds": [str(uuid.uuid4())]
        }
        
        response = client.post(
            f"/api/v1/spaces/{created_space.id}/quizzes",
            json=quiz_data,
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        
        error = response.json()
        assert "error" in error
        assert error["error"]["code"] == "FILE_NOT_FOUND"
    
    def test_generate_quiz_files_not_owned(self, client: TestClient, auth_headers, created_space, other_user_files):
        """Test quiz generation with files not owned by user."""
        quiz_data = {
            "title": "Test Quiz",
            "fileIds": [str(other_user_files[0].id)]
        }
        
        response = client.post(
            f"/api/v1/spaces/{created_space.id}/quizzes",
            json=quiz_data,
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
        
        error = response.json()
        assert "error" in error
        assert error["error"]["code"] == "FORBIDDEN"
    
    def test_generate_quiz_validation_errors(self, client: TestClient, auth_headers, created_space):
        """Test quiz generation with various validation errors."""
        # Empty title
        quiz_data = {
            "title": "",
            "fileIds": [str(uuid.uuid4())]
        }
        
        response = client.post(
            f"/api/v1/spaces/{created_space.id}/quizzes",
            json=quiz_data,
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        
        # No file IDs
        quiz_data = {
            "title": "Test Quiz",
            "fileIds": []
        }
        
        response = client.post(
            f"/api/v1/spaces/{created_space.id}/quizzes",
            json=quiz_data,
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        
        # Invalid question count
        quiz_data = {
            "title": "Test Quiz",
            "fileIds": [str(uuid.uuid4())],
            "questionCount": 0
        }
        
        response = client.post(
            f"/api/v1/spaces/{created_space.id}/quizzes",
            json=quiz_data,
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_generate_quiz_unauthorized(self, client: TestClient, created_space, uploaded_files):
        """Test quiz generation without authentication."""
        quiz_data = {
            "title": "Test Quiz",
            "fileIds": [str(uploaded_files[0].id)]
        }
        
        response = client.post(
            f"/api/v1/spaces/{created_space.id}/quizzes",
            json=quiz_data
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestListQuizzes:
    """Test list quizzes endpoint."""
    
    def test_list_quizzes_empty(self, client: TestClient, auth_headers, created_space):
        """Test listing quizzes when space has none."""
        response = client.get(f"/api/v1/spaces/{created_space.id}/quizzes", headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert "data" in data
        assert "meta" in data
        assert data["data"] == []
        assert data["meta"]["total"] == 0
        assert data["meta"]["page"] == 1
        assert data["meta"]["limit"] == 20
    
    def test_list_quizzes_with_data(self, client: TestClient, auth_headers, created_space, created_quiz):
        """Test listing quizzes when space has quizzes."""
        response = client.get(f"/api/v1/spaces/{created_space.id}/quizzes", headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert "data" in data
        assert "meta" in data
        assert len(data["data"]) == 1
        assert data["meta"]["total"] == 1
        
        quiz = data["data"][0]
        assert quiz["id"] == str(created_quiz.id)
        assert quiz["spaceId"] == str(created_space.id)
        assert quiz["title"] == created_quiz.title
        assert "questions" in quiz
        assert "createdAt" in quiz
    
    def test_list_quizzes_pagination(self, client: TestClient, auth_headers, created_space, uploaded_files):
        """Test quiz listing with pagination."""
        # Create multiple quizzes
        for i in range(5):
            quiz_data = {
                "title": f"Quiz {i}",
                "fileIds": [str(uploaded_files[0].id)]
            }
            client.post(f"/api/v1/spaces/{created_space.id}/quizzes", json=quiz_data, headers=auth_headers)
        
        # Test pagination
        response = client.get(f"/api/v1/spaces/{created_space.id}/quizzes?page=1&limit=3", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert len(data["data"]) == 3
        assert data["meta"]["page"] == 1
        assert data["meta"]["limit"] == 3
        assert data["meta"]["total"] == 5
        
        # Test second page
        response = client.get(f"/api/v1/spaces/{created_space.id}/quizzes?page=2&limit=3", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert len(data["data"]) == 2
        assert data["meta"]["page"] == 2
    
    def test_list_quizzes_invalid_space(self, client: TestClient, auth_headers):
        """Test listing quizzes with invalid space ID."""
        invalid_space_id = str(uuid.uuid4())
        response = client.get(f"/api/v1/spaces/{invalid_space_id}/quizzes", headers=auth_headers)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        
        error = response.json()
        assert "error" in error
        assert error["error"]["code"] == "SPACE_NOT_FOUND"
    
    def test_list_quizzes_unauthorized(self, client: TestClient, created_space):
        """Test listing quizzes without authentication."""
        response = client.get(f"/api/v1/spaces/{created_space.id}/quizzes")
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestGetQuizDetail:
    """Test get quiz detail endpoint."""
    
    def test_get_quiz_success(self, client: TestClient, auth_headers, created_quiz):
        """Test successful quiz retrieval."""
        response = client.get(f"/api/v1/quizzes/{created_quiz.id}", headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert "data" in data
        quiz = data["data"]
        
        assert quiz["id"] == str(created_quiz.id)
        assert quiz["title"] == created_quiz.title
        assert "questions" in quiz
        assert "createdAt" in quiz
    
    def test_get_quiz_invalid_id(self, client: TestClient, auth_headers):
        """Test getting quiz with invalid ID."""
        invalid_quiz_id = str(uuid.uuid4())
        response = client.get(f"/api/v1/quizzes/{invalid_quiz_id}", headers=auth_headers)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        
        error = response.json()
        assert "error" in error
        assert error["error"]["code"] == "QUIZ_NOT_FOUND"
    
    def test_get_quiz_not_owned(self, client: TestClient, auth_headers, other_user_quiz):
        """Test getting quiz not owned by user."""
        response = client.get(f"/api/v1/quizzes/{other_user_quiz.id}", headers=auth_headers)
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
        
        error = response.json()
        assert "error" in error
        assert error["error"]["code"] == "FORBIDDEN"
    
    def test_get_quiz_unauthorized(self, client: TestClient, created_quiz):
        """Test getting quiz without authentication."""
        response = client.get(f"/api/v1/quizzes/{created_quiz.id}")
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestSubmitQuizAnswers:
    """Test quiz answer submission endpoint."""
    
    def test_submit_quiz_answers_success(self, client: TestClient, auth_headers, created_quiz):
        """Test successful quiz answer submission."""
        submission_data = {
            "answers": [
                {"questionId": "q1", "answer": "A"},
                {"questionId": "q2", "answer": 1}
            ]
        }
        
        response = client.post(
            f"/api/v1/quizzes/{created_quiz.id}/submit",
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
        assert result["totalQuestions"] == len(created_quiz.questions)
        assert 0 <= result["score"] <= result["totalQuestions"]
    
    def test_submit_quiz_answers_partial(self, client: TestClient, auth_headers, created_quiz):
        """Test quiz submission with partial answers."""
        submission_data = {
            "answers": [
                {"questionId": "q1", "answer": "A"}
                # Missing answers for other questions
            ]
        }
        
        response = client.post(
            f"/api/v1/quizzes/{created_quiz.id}/submit",
            json=submission_data,
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_201_CREATED
        
        data = response.json()
        result = data["data"]
        
        # Should accept partial submissions
        assert "score" in result
        assert "feedback" in result
    
    def test_submit_quiz_answers_invalid_quiz(self, client: TestClient, auth_headers):
        """Test quiz submission with invalid quiz ID."""
        submission_data = {
            "answers": [
                {"questionId": "q1", "answer": "A"}
            ]
        }
        
        invalid_quiz_id = str(uuid.uuid4())
        response = client.post(
            f"/api/v1/quizzes/{invalid_quiz_id}/submit",
            json=submission_data,
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        
        error = response.json()
        assert "error" in error
        assert error["error"]["code"] == "QUIZ_NOT_FOUND"
    
    def test_submit_quiz_answers_validation_errors(self, client: TestClient, auth_headers, created_quiz):
        """Test quiz submission with validation errors."""
        # Empty answers
        submission_data = {
            "answers": []
        }
        
        response = client.post(
            f"/api/v1/quizzes/{created_quiz.id}/submit",
            json=submission_data,
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        
        # Missing questionId
        submission_data = {
            "answers": [
                {"answer": "A"}
            ]
        }
        
        response = client.post(
            f"/api/v1/quizzes/{created_quiz.id}/submit",
            json=submission_data,
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_submit_quiz_answers_not_owned(self, client: TestClient, auth_headers, other_user_quiz):
        """Test quiz submission for quiz not owned by user."""
        submission_data = {
            "answers": [
                {"questionId": "q1", "answer": "A"}
            ]
        }
        
        response = client.post(
            f"/api/v1/quizzes/{other_user_quiz.id}/submit",
            json=submission_data,
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
        
        error = response.json()
        assert "error" in error
        assert error["error"]["code"] == "FORBIDDEN"
    
    def test_submit_quiz_answers_unauthorized(self, client: TestClient, created_quiz):
        """Test quiz submission without authentication."""
        submission_data = {
            "answers": [
                {"questionId": "q1", "answer": "A"}
            ]
        }
        
        response = client.post(
            f"/api/v1/quizzes/{created_quiz.id}/submit",
            json=submission_data
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestDeleteQuiz:
    """Test delete quiz endpoint."""
    
    def test_delete_quiz_success(self, client: TestClient, auth_headers, created_quiz):
        """Test successful quiz deletion."""
        response = client.delete(f"/api/v1/quizzes/{created_quiz.id}", headers=auth_headers)
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
        
        # Verify quiz is deleted
        response = client.get(f"/api/v1/quizzes/{created_quiz.id}", headers=auth_headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_delete_quiz_invalid_id(self, client: TestClient, auth_headers):
        """Test deleting quiz with invalid ID."""
        invalid_quiz_id = str(uuid.uuid4())
        response = client.delete(f"/api/v1/quizzes/{invalid_quiz_id}", headers=auth_headers)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        
        error = response.json()
        assert "error" in error
        assert error["error"]["code"] == "QUIZ_NOT_FOUND"
    
    def test_delete_quiz_not_owned(self, client: TestClient, auth_headers, other_user_quiz):
        """Test deleting quiz not owned by user."""
        response = client.delete(f"/api/v1/quizzes/{other_user_quiz.id}", headers=auth_headers)
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
        
        error = response.json()
        assert "error" in error
        assert error["error"]["code"] == "FORBIDDEN"
    
    def test_delete_quiz_unauthorized(self, client: TestClient, created_quiz):
        """Test deleting quiz without authentication."""
        response = client.delete(f"/api/v1/quizzes/{created_quiz.id}")
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_delete_quiz_cascade_submissions(self, client: TestClient, auth_headers, created_quiz):
        """Test that deleting quiz also deletes submissions."""
        # Submit answers first
        submission_data = {
            "answers": [
                {"questionId": "q1", "answer": "A"}
            ]
        }
        
        submit_response = client.post(
            f"/api/v1/quizzes/{created_quiz.id}/submit",
            json=submission_data,
            headers=auth_headers
        )
        assert submit_response.status_code == status.HTTP_201_CREATED
        
        # Delete quiz
        response = client.delete(f"/api/v1/quizzes/{created_quiz.id}", headers=auth_headers)
        assert response.status_code == status.HTTP_204_NO_CONTENT
        
        # Verify quiz and submissions are gone
        response = client.get(f"/api/v1/quizzes/{created_quiz.id}", headers=auth_headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND 