"""
Flashcard management endpoint tests for EdutechHackathon API.

Tests all flashcard endpoints according to the API specification:
- POST /spaces/{spaceId}/flashcards - Generate flashcards from selected files + params
- GET /spaces/{spaceId}/flashcards - List flashcards
- GET /flashcards/{id} - Flashcard detail
- PATCH /flashcards/{id} - Update flashcard deck or individual cards
- DELETE /flashcards/{id} - Delete flashcard deck
- POST /flashcards/{id}/shuffle - Get shuffled card order for study session
"""
import pytest
from fastapi import status
from fastapi.testclient import TestClient
import uuid


class TestGenerateFlashcards:
    """Test flashcard generation endpoint."""
    
    def test_generate_flashcards_success(self, client: TestClient, auth_headers, created_space, uploaded_files):
        """Test successful flashcard generation."""
        flashcard_data = {
            "title": "Biology Terms Set 1",
            "fileIds": [str(uploaded_files[0].id), str(uploaded_files[1].id)],
            "cardCount": 20,
            "cardTypes": ["mcq", "tf"],
            "difficulty": "medium"
        }
        
        response = client.post(
            f"/api/v1/spaces/{created_space.id}/flashcards",
            json=flashcard_data,
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_201_CREATED
        
        data = response.json()
        assert "data" in data
        flashcard = data["data"]
        
        assert "id" in flashcard
        assert flashcard["spaceId"] == str(created_space.id)
        assert flashcard["title"] == "Biology Terms Set 1"
        assert "cards" in flashcard
        assert len(flashcard["cards"]) == 20  # Mock AI service should generate 20 cards
        assert "createdAt" in flashcard
        assert "updatedAt" in flashcard
        
        # Verify card structure
        for card in flashcard["cards"]:
            assert "id" in card
            assert "front" in card
            assert "back" in card
            assert "difficulty" in card
            assert card["difficulty"] in ["easy", "medium", "hard"]
            assert "tags" in card
            assert isinstance(card["tags"], list)
    
    def test_generate_flashcards_with_minimal_data(self, client: TestClient, auth_headers, created_space, uploaded_files):
        """Test flashcard generation with minimal required fields."""
        flashcard_data = {
            "title": "Simple Flashcards",
            "fileIds": [str(uploaded_files[0].id)]
        }
        
        response = client.post(
            f"/api/v1/spaces/{created_space.id}/flashcards",
            json=flashcard_data,
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_201_CREATED
        
        data = response.json()
        flashcard = data["data"]
        
        assert flashcard["title"] == "Simple Flashcards"
        assert len(flashcard["cards"]) == 20  # Default card count
    
    def test_generate_flashcards_invalid_space(self, client: TestClient, auth_headers, uploaded_files):
        """Test flashcard generation with invalid space ID."""
        flashcard_data = {
            "title": "Test Flashcards",
            "fileIds": [str(uploaded_files[0].id)]
        }
        
        invalid_space_id = str(uuid.uuid4())
        response = client.post(
            f"/api/v1/spaces/{invalid_space_id}/flashcards",
            json=flashcard_data,
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        
        error = response.json()
        assert "error" in error
        assert error["error"]["code"] == "SPACE_NOT_FOUND"
    
    def test_generate_flashcards_invalid_files(self, client: TestClient, auth_headers, created_space):
        """Test flashcard generation with non-existent file IDs."""
        flashcard_data = {
            "title": "Test Flashcards",
            "fileIds": [str(uuid.uuid4())]
        }
        
        response = client.post(
            f"/api/v1/spaces/{created_space.id}/flashcards",
            json=flashcard_data,
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        
        error = response.json()
        assert "error" in error
        assert error["error"]["code"] == "FILE_NOT_FOUND"
    
    def test_generate_flashcards_files_not_owned(self, client: TestClient, auth_headers, created_space, other_user_files):
        """Test flashcard generation with files not owned by user."""
        flashcard_data = {
            "title": "Test Flashcards",
            "fileIds": [str(other_user_files[0].id)]
        }
        
        response = client.post(
            f"/api/v1/spaces/{created_space.id}/flashcards",
            json=flashcard_data,
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
        
        error = response.json()
        assert "error" in error
        assert error["error"]["code"] == "FORBIDDEN"
    
    def test_generate_flashcards_validation_errors(self, client: TestClient, auth_headers, created_space):
        """Test flashcard generation with various validation errors."""
        # Empty title
        flashcard_data = {
            "title": "",
            "fileIds": [str(uuid.uuid4())]
        }
        
        response = client.post(
            f"/api/v1/spaces/{created_space.id}/flashcards",
            json=flashcard_data,
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        
        # No file IDs
        flashcard_data = {
            "title": "Test Flashcards",
            "fileIds": []
        }
        
        response = client.post(
            f"/api/v1/spaces/{created_space.id}/flashcards",
            json=flashcard_data,
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        
        # Invalid card count
        flashcard_data = {
            "title": "Test Flashcards",
            "fileIds": [str(uuid.uuid4())],
            "cardCount": 0
        }
        
        response = client.post(
            f"/api/v1/spaces/{created_space.id}/flashcards",
            json=flashcard_data,
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_generate_flashcards_unauthorized(self, client: TestClient, created_space, uploaded_files):
        """Test flashcard generation without authentication."""
        flashcard_data = {
            "title": "Test Flashcards",
            "fileIds": [str(uploaded_files[0].id)]
        }
        
        response = client.post(
            f"/api/v1/spaces/{created_space.id}/flashcards",
            json=flashcard_data
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestListFlashcards:
    """Test list flashcards endpoint."""
    
    def test_list_flashcards_empty(self, client: TestClient, auth_headers, created_space):
        """Test listing flashcards when space has none."""
        response = client.get(f"/api/v1/spaces/{created_space.id}/flashcards", headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert "data" in data
        assert "meta" in data
        assert data["data"] == []
        assert data["meta"]["total"] == 0
        assert data["meta"]["page"] == 1
        assert data["meta"]["limit"] == 20
    
    def test_list_flashcards_with_data(self, client: TestClient, auth_headers, created_space_flashcards, created_flashcards):
        """Test listing flashcards when space has flashcards."""
        response = client.get(f"/api/v1/spaces/{created_space_flashcards.id}/flashcards", headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert "data" in data
        assert "meta" in data
        assert len(data["data"]) == 1
        assert data["meta"]["total"] == 1
        
        flashcard = data["data"][0]
        assert flashcard["id"] == str(created_flashcards.id)
        assert flashcard["spaceId"] == str(created_space_flashcards.id)
        assert flashcard["title"] == created_flashcards.title
        assert "cards" in flashcard
        assert "createdAt" in flashcard
        assert "updatedAt" in flashcard
    
    def test_list_flashcards_pagination(self, client: TestClient, auth_headers, created_space, uploaded_files):
        """Test flashcard listing with pagination."""
        # Create multiple flashcards
        for i in range(5):
            flashcard_data = {
                "title": f"Flashcards {i}",
                "fileIds": [str(uploaded_files[0].id)]
            }
            client.post(f"/api/v1/spaces/{created_space.id}/flashcards", json=flashcard_data, headers=auth_headers)
        
        # Test pagination
        response = client.get(f"/api/v1/spaces/{created_space.id}/flashcards?page=1&limit=3", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert len(data["data"]) == 3
        assert data["meta"]["page"] == 1
        assert data["meta"]["limit"] == 3
        assert data["meta"]["total"] == 5
        
        # Test second page
        response = client.get(f"/api/v1/spaces/{created_space.id}/flashcards?page=2&limit=3", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert len(data["data"]) == 2
        assert data["meta"]["page"] == 2
    
    def test_list_flashcards_invalid_space(self, client: TestClient, auth_headers):
        """Test listing flashcards with invalid space ID."""
        invalid_space_id = str(uuid.uuid4())
        response = client.get(f"/api/v1/spaces/{invalid_space_id}/flashcards", headers=auth_headers)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        
        error = response.json()
        assert "error" in error
        assert error["error"]["code"] == "SPACE_NOT_FOUND"
    
    def test_list_flashcards_unauthorized(self, client: TestClient, created_space):
        """Test listing flashcards without authentication."""
        response = client.get(f"/api/v1/spaces/{created_space.id}/flashcards")
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestGetFlashcardDetail:
    """Test get flashcard detail endpoint."""
    
    def test_get_flashcard_success(self, client: TestClient, auth_headers, created_flashcards):
        """Test successful flashcard retrieval."""
        response = client.get(f"/api/v1/flashcards/{created_flashcards.id}", headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert "data" in data
        flashcard = data["data"]
        
        assert flashcard["id"] == str(created_flashcards.id)
        assert flashcard["title"] == created_flashcards.title
        assert "cards" in flashcard
        assert "createdAt" in flashcard
        assert "updatedAt" in flashcard
    
    def test_get_flashcard_invalid_id(self, client: TestClient, auth_headers):
        """Test getting flashcard with invalid ID."""
        invalid_flashcard_id = str(uuid.uuid4())
        response = client.get(f"/api/v1/flashcards/{invalid_flashcard_id}", headers=auth_headers)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        
        error = response.json()
        assert "error" in error
        assert error["error"]["code"] == "FLASHCARD_NOT_FOUND"
    
    def test_get_flashcard_not_owned(self, client: TestClient, auth_headers, other_user_flashcards):
        """Test getting flashcard not owned by user."""
        response = client.get(f"/api/v1/flashcards/{other_user_flashcards.id}", headers=auth_headers)
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
        
        error = response.json()
        assert "error" in error
        assert error["error"]["code"] == "FORBIDDEN"
    
    def test_get_flashcard_unauthorized(self, client: TestClient, created_flashcards):
        """Test getting flashcard without authentication."""
        response = client.get(f"/api/v1/flashcards/{created_flashcards.id}")
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestUpdateFlashcard:
    """Test update flashcard endpoint."""
    
    def test_update_flashcard_title_success(self, client: TestClient, auth_headers, created_flashcards):
        """Test successful flashcard title update."""
        update_data = {
            "title": "Updated Biology Terms"
        }
        
        response = client.patch(
            f"/api/v1/flashcards/{created_flashcards.id}",
            json=update_data,
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert "data" in data
        flashcard = data["data"]
        
        assert flashcard["title"] == "Updated Biology Terms"
        assert "updatedAt" in flashcard
    
    def test_update_flashcard_cards_success(self, client: TestClient, auth_headers, created_flashcards):
        """Test successful flashcard cards update."""
        update_data = {
            "cards": [
                {
                    "id": "card1",
                    "front": "What is chlorophyll?",
                    "back": "A green pigment found in plants",
                    "difficulty": "easy",
                    "tags": ["photosynthesis", "pigments"]
                },
                {
                    "id": "card2",
                    "front": "Where does photosynthesis occur?",
                    "back": "In the chloroplasts",
                    "difficulty": "medium",
                    "tags": ["photosynthesis", "chloroplasts"]
                }
            ]
        }
        
        response = client.patch(
            f"/api/v1/flashcards/{created_flashcards.id}",
            json=update_data,
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        flashcard = data["data"]
        
        assert len(flashcard["cards"]) == 2
        assert flashcard["cards"][0]["front"] == "What is chlorophyll?"
        assert flashcard["cards"][1]["front"] == "Where does photosynthesis occur?"
    
    def test_update_flashcard_invalid_id(self, client: TestClient, auth_headers):
        """Test updating flashcard with invalid ID."""
        update_data = {"title": "Updated Title"}
        invalid_flashcard_id = str(uuid.uuid4())
        
        response = client.patch(
            f"/api/v1/flashcards/{invalid_flashcard_id}",
            json=update_data,
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        
        error = response.json()
        assert "error" in error
        assert error["error"]["code"] == "FLASHCARD_NOT_FOUND"
    
    def test_update_flashcard_not_owned(self, client: TestClient, auth_headers, other_user_flashcards):
        """Test updating flashcard not owned by user."""
        update_data = {"title": "Updated Title"}
        
        response = client.patch(
            f"/api/v1/flashcards/{other_user_flashcards.id}",
            json=update_data,
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
        
        error = response.json()
        assert "error" in error
        assert error["error"]["code"] == "FORBIDDEN"
    
    def test_update_flashcard_validation_errors(self, client: TestClient, auth_headers, created_flashcards):
        """Test flashcard update with validation errors."""
        # Empty title
        update_data = {"title": ""}
        
        response = client.patch(
            f"/api/v1/flashcards/{created_flashcards.id}",
            json=update_data,
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_update_flashcard_unauthorized(self, client: TestClient, created_flashcards):
        """Test updating flashcard without authentication."""
        update_data = {"title": "Updated Title"}
        
        response = client.patch(
            f"/api/v1/flashcards/{created_flashcards.id}",
            json=update_data
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestShuffleFlashcards:
    """Test flashcard shuffle endpoint."""
    
    def test_shuffle_flashcards_success(self, client: TestClient, auth_headers, created_flashcards):
        """Test successful flashcard shuffling."""
        response = client.post(
            f"/api/v1/flashcards/{created_flashcards.id}/shuffle",
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert "data" in data
        shuffled = data["data"]
        
        assert "cardOrder" in shuffled
        assert len(shuffled["cardOrder"]) == len(created_flashcards.cards)
        assert "sessionId" in shuffled
        assert "createdAt" in shuffled
        
        # Verify all original card IDs are present
        original_card_ids = {card["id"] for card in created_flashcards.cards}
        shuffled_card_ids = set(shuffled["cardOrder"])
        assert original_card_ids == shuffled_card_ids
    
    def test_shuffle_flashcards_invalid_id(self, client: TestClient, auth_headers):
        """Test shuffling flashcard with invalid ID."""
        invalid_flashcard_id = str(uuid.uuid4())
        
        response = client.post(
            f"/api/v1/flashcards/{invalid_flashcard_id}/shuffle",
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        
        error = response.json()
        assert "error" in error
        assert error["error"]["code"] == "FLASHCARD_NOT_FOUND"
    
    def test_shuffle_flashcards_not_owned(self, client: TestClient, auth_headers, other_user_flashcards):
        """Test shuffling flashcard not owned by user."""
        response = client.post(
            f"/api/v1/flashcards/{other_user_flashcards.id}/shuffle",
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
        
        error = response.json()
        assert "error" in error
        assert error["error"]["code"] == "FORBIDDEN"
    
    def test_shuffle_flashcards_unauthorized(self, client: TestClient, created_flashcards):
        """Test shuffling flashcard without authentication."""
        response = client.post(f"/api/v1/flashcards/{created_flashcards.id}/shuffle")
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestDeleteFlashcard:
    """Test delete flashcard endpoint."""
    
    def test_delete_flashcard_success(self, client: TestClient, auth_headers, created_flashcards):
        """Test successful flashcard deletion."""
        response = client.delete(f"/api/v1/flashcards/{created_flashcards.id}", headers=auth_headers)
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
        
        # Verify flashcard is deleted
        response = client.get(f"/api/v1/flashcards/{created_flashcards.id}", headers=auth_headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_delete_flashcard_invalid_id(self, client: TestClient, auth_headers):
        """Test deleting flashcard with invalid ID."""
        invalid_flashcard_id = str(uuid.uuid4())
        response = client.delete(f"/api/v1/flashcards/{invalid_flashcard_id}", headers=auth_headers)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        
        error = response.json()
        assert "error" in error
        assert error["error"]["code"] == "FLASHCARD_NOT_FOUND"
    
    def test_delete_flashcard_not_owned(self, client: TestClient, auth_headers, other_user_flashcards):
        """Test deleting flashcard not owned by user."""
        response = client.delete(f"/api/v1/flashcards/{other_user_flashcards.id}", headers=auth_headers)
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
        
        error = response.json()
        assert "error" in error
        assert error["error"]["code"] == "FORBIDDEN"
    
    def test_delete_flashcard_unauthorized(self, client: TestClient, created_flashcards):
        """Test deleting flashcard without authentication."""
        response = client.delete(f"/api/v1/flashcards/{created_flashcards.id}")
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED 