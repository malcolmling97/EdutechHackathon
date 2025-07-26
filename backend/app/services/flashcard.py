"""
Flashcard service for flashcard management operations.

Handles:
- Flashcard generation with mock AI integration
- Flashcard listing with pagination
- Flashcard retrieval with ownership verification
- Flashcard updates and modifications
- Flashcard shuffling for study sessions
- Flashcard deletion with cascading operations
"""
import uuid
import random
from typing import Optional, List, Tuple, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc
from fastapi import HTTPException, status
from datetime import datetime

from app.models.flashcard import Flashcard
from app.models.space import Space, SpaceType
from app.models.file import File
from app.models.folder import Folder
from app.models.user import User
from app.schemas.flashcard import (
    FlashcardCreate, 
    FlashcardResponse, 
    FlashcardListResponse,
    FlashcardUpdate,
    FlashcardShuffleResponse,
    PaginationMeta,
    CardType,
    DifficultyLevel
)


class MockAIService:
    """Mock AI service for flashcard generation (Backend Developer responsibility)."""
    
    @staticmethod
    def generate_flashcard_cards(file_contents: List[str], params: FlashcardCreate) -> List[Dict[str, Any]]:
        """
        Mock AI service to generate flashcard cards from file content.
        
        In production, this would call OpenAI API for card generation.
        For now, returns mock cards based on parameters.
        """
        cards = []
        difficulties = ["easy", "medium", "hard"]
        topics = ["photosynthesis", "cellular respiration", "chloroplasts", "mitochondria", "enzymes", "metabolism"]
        
        for i in range(params.card_count):
            card_type = params.card_types[i % len(params.card_types)]
            difficulty = difficulties[i % len(difficulties)]
            topic = topics[i % len(topics)]
            
            if card_type == CardType.mcq:
                card = {
                    "id": f"card{i+1}",
                    "front": f"What is the main function of {topic}?",
                    "back": f"The main function of {topic} is to process energy and materials in cells.",
                    "difficulty": difficulty,
                    "tags": [topic, "function", "biology"]
                }
            elif card_type == CardType.tf:
                card = {
                    "id": f"card{i+1}",
                    "front": f"True or False: {topic} is essential for cellular function.",
                    "back": "True",
                    "difficulty": difficulty,
                    "tags": [topic, "true_false", "cellular"]
                }
            else:  # short_answer
                card = {
                    "id": f"card{i+1}",
                    "front": f"Explain the role of {topic} in biological systems.",
                    "back": f"{topic} plays a crucial role in biological systems by facilitating essential cellular processes.",
                    "difficulty": difficulty,
                    "tags": [topic, "explanation", "biology"]
                }
            
            cards.append(card)
        
        return cards


class FlashcardService:
    """Service class for flashcard management operations."""
    
    @staticmethod
    def generate_flashcards(
        db: Session, 
        user: User, 
        space_id: str,
        flashcard_data: FlashcardCreate
    ) -> FlashcardResponse:
        """
        Generate flashcards from file content using mock AI service.
        
        Args:
            db: Database session
            user: Current user
            space_id: Space UUID where flashcards will be created
            flashcard_data: Flashcard generation parameters
            
        Returns:
            FlashcardResponse with generated flashcard data
            
        Raises:
            HTTPException: If space not found, files not found, or permission denied
        """
        # Verify space exists and user owns it
        space = db.query(Space).filter(
            and_(
                Space.id == space_id,
                Space.deleted_at.is_(None)
            )
        ).first()
        
        if not space:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error": {
                        "code": "SPACE_NOT_FOUND",
                        "message": "Space not found or you don't have permission to access it",
                        "details": {"space_id": space_id}
                    }
                }
            )
        
        # Verify user owns the parent folder
        folder = db.query(Folder).filter(
            and_(
                Folder.id == space.folder_id,
                Folder.owner_id == user.id,
                Folder.deleted_at.is_(None)
            )
        ).first()
        
        if not folder:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "error": {
                        "code": "FORBIDDEN",
                        "message": "You don't have permission to access this space",
                        "details": {"space_id": space_id}
                    }
                }
            )
        
        # Verify all files exist and user owns them
        file_ids = [uuid.UUID(file_id) for file_id in flashcard_data.file_ids]
        files = db.query(File).filter(
            and_(
                File.id.in_(file_ids),
                File.deleted_at.is_(None)
            )
        ).all()
        
        if len(files) != len(file_ids):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error": {
                        "code": "FILE_NOT_FOUND",
                        "message": "One or more files not found",
                        "details": {"file_ids": flashcard_data.file_ids}
                    }
                }
            )
        
        # Verify user owns all files (through folder ownership)
        for file in files:
            file_folder = db.query(Folder).filter(
                and_(
                    Folder.id == file.folder_id,
                    Folder.owner_id == user.id,
                    Folder.deleted_at.is_(None)
                )
            ).first()
            
            if not file_folder:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail={
                        "error": {
                            "code": "FORBIDDEN",
                            "message": "You don't have permission to access one or more files",
                            "details": {"file_ids": flashcard_data.file_ids}
                        }
                    }
                )
        
        # Get file contents for AI processing
        file_contents = []
        for file in files:
            if file.text_content:
                file_contents.append(file.text_content)
            else:
                # If no text content, use filename as placeholder
                file_contents.append(f"Content from {file.name}")
        
        # Generate flashcards using mock AI service
        cards = MockAIService.generate_flashcard_cards(file_contents, flashcard_data)
        
        # Create flashcard record
        flashcard = Flashcard(
            id=uuid.uuid4(),
            space_id=space_id,
            title=flashcard_data.title,
            cards=cards,
            file_ids=flashcard_data.file_ids,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        db.add(flashcard)
        db.commit()
        db.refresh(flashcard)
        
        # Convert to response format
        return FlashcardResponse(
            id=flashcard.id,
            space_id=flashcard.space_id,
            title=flashcard.title,
            cards=flashcard.cards,
            created_at=flashcard.created_at,
            updated_at=flashcard.updated_at
        )
    
    @staticmethod
    def list_flashcards(
        db: Session, 
        user: User, 
        space_id: str,
        page: int = 1, 
        limit: int = 20
    ) -> FlashcardListResponse:
        """
        List flashcards in a space with pagination.
        
        Args:
            db: Database session
            user: Current user
            space_id: Space UUID to list flashcards from
            page: Page number (1-based)
            limit: Items per page
            
        Returns:
            FlashcardListResponse with paginated flashcard data
            
        Raises:
            HTTPException: If space not found or permission denied
        """
        # Verify space exists and user owns it
        space = db.query(Space).filter(
            and_(
                Space.id == space_id,
                Space.deleted_at.is_(None)
            )
        ).first()
        
        if not space:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error": {
                        "code": "SPACE_NOT_FOUND",
                        "message": "Space not found or you don't have permission to access it",
                        "details": {"space_id": space_id}
                    }
                }
            )
        
        # Verify user owns the parent folder
        folder = db.query(Folder).filter(
            and_(
                Folder.id == space.folder_id,
                Folder.owner_id == user.id,
                Folder.deleted_at.is_(None)
            )
        ).first()
        
        if not folder:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "error": {
                        "code": "FORBIDDEN",
                        "message": "You don't have permission to access this space",
                        "details": {"space_id": space_id}
                    }
                }
            )
        
        # Query flashcards with pagination
        offset = (page - 1) * limit
        
        flashcards_query = db.query(Flashcard).filter(
            Flashcard.space_id == space_id
        ).order_by(desc(Flashcard.created_at))
        
        total = flashcards_query.count()
        flashcards = flashcards_query.offset(offset).limit(limit).all()
        
        # Convert to response format
        flashcard_responses = []
        for flashcard in flashcards:
            flashcard_responses.append(
                FlashcardResponse(
                    id=flashcard.id,
                    space_id=flashcard.space_id,
                    title=flashcard.title,
                    cards=flashcard.cards,
                    created_at=flashcard.created_at,
                    updated_at=flashcard.updated_at
                )
            )
        
        return FlashcardListResponse(
            data=flashcard_responses,
            meta=PaginationMeta(
                page=page,
                limit=limit,
                total=total
            )
        )
    
    @staticmethod
    def get_flashcard(
        db: Session, 
        user: User, 
        flashcard_id: str
    ) -> FlashcardResponse:
        """
        Get a specific flashcard by ID.
        
        Args:
            db: Database session
            user: Current user
            flashcard_id: Flashcard UUID to retrieve
            
        Returns:
            FlashcardResponse with flashcard data
            
        Raises:
            HTTPException: If flashcard not found or permission denied
        """
        # Get flashcard with space and folder information
        flashcard = db.query(Flashcard).filter(
            Flashcard.id == flashcard_id
        ).first()
        
        if not flashcard:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error": {
                        "code": "FLASHCARD_NOT_FOUND",
                        "message": "Flashcard not found",
                        "details": {"flashcard_id": flashcard_id}
                    }
                }
            )
        
        # Verify user owns the parent folder
        space = db.query(Space).filter(
            and_(
                Space.id == flashcard.space_id,
                Space.deleted_at.is_(None)
            )
        ).first()
        
        if not space:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error": {
                        "code": "FLASHCARD_NOT_FOUND",
                        "message": "Flashcard not found",
                        "details": {"flashcard_id": flashcard_id}
                    }
                }
            )
        
        folder = db.query(Folder).filter(
            and_(
                Folder.id == space.folder_id,
                Folder.owner_id == user.id,
                Folder.deleted_at.is_(None)
            )
        ).first()
        
        if not folder:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "error": {
                        "code": "FORBIDDEN",
                        "message": "You don't have permission to access this flashcard",
                        "details": {"flashcard_id": flashcard_id}
                    }
                }
            )
        
        # Convert to response format
        return FlashcardResponse(
            id=flashcard.id,
            space_id=flashcard.space_id,
            title=flashcard.title,
            cards=flashcard.cards,
            created_at=flashcard.created_at,
            updated_at=flashcard.updated_at
        )
    
    @staticmethod
    def update_flashcard(
        db: Session, 
        user: User, 
        flashcard_id: str,
        update_data: FlashcardUpdate
    ) -> FlashcardResponse:
        """
        Update a flashcard deck or individual cards.
        
        Args:
            db: Database session
            user: Current user
            flashcard_id: Flashcard UUID to update
            update_data: Update data
            
        Returns:
            FlashcardResponse with updated flashcard data
            
        Raises:
            HTTPException: If flashcard not found or permission denied
        """
        # Get flashcard and verify ownership
        flashcard = db.query(Flashcard).filter(
            Flashcard.id == flashcard_id
        ).first()
        
        if not flashcard:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error": {
                        "code": "FLASHCARD_NOT_FOUND",
                        "message": "Flashcard not found",
                        "details": {"flashcard_id": flashcard_id}
                    }
                }
            )
        
        # Verify user owns the parent folder
        space = db.query(Space).filter(
            and_(
                Space.id == flashcard.space_id,
                Space.deleted_at.is_(None)
            )
        ).first()
        
        if not space:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error": {
                        "code": "FLASHCARD_NOT_FOUND",
                        "message": "Flashcard not found",
                        "details": {"flashcard_id": flashcard_id}
                    }
                }
            )
        
        folder = db.query(Folder).filter(
            and_(
                Folder.id == space.folder_id,
                Folder.owner_id == user.id,
                Folder.deleted_at.is_(None)
            )
        ).first()
        
        if not folder:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "error": {
                        "code": "FORBIDDEN",
                        "message": "You don't have permission to access this flashcard",
                        "details": {"flashcard_id": flashcard_id}
                    }
                }
            )
        
        # Update flashcard fields
        if update_data.title is not None:
            flashcard.title = update_data.title
        
        if update_data.cards is not None:
            flashcard.cards = update_data.cards
        
        flashcard.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(flashcard)
        
        # Convert to response format
        return FlashcardResponse(
            id=flashcard.id,
            space_id=flashcard.space_id,
            title=flashcard.title,
            cards=flashcard.cards,
            created_at=flashcard.created_at,
            updated_at=flashcard.updated_at
        )
    
    @staticmethod
    def shuffle_flashcards(
        db: Session, 
        user: User, 
        flashcard_id: str
    ) -> FlashcardShuffleResponse:
        """
        Get a shuffled order of cards for study sessions.
        
        Args:
            db: Database session
            user: Current user
            flashcard_id: Flashcard UUID to shuffle
            
        Returns:
            FlashcardShuffleResponse with shuffled card order
            
        Raises:
            HTTPException: If flashcard not found or permission denied
        """
        # Get flashcard and verify ownership
        flashcard = db.query(Flashcard).filter(
            Flashcard.id == flashcard_id
        ).first()
        
        if not flashcard:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error": {
                        "code": "FLASHCARD_NOT_FOUND",
                        "message": "Flashcard not found",
                        "details": {"flashcard_id": flashcard_id}
                    }
                }
            )
        
        # Verify user owns the parent folder
        space = db.query(Space).filter(
            and_(
                Space.id == flashcard.space_id,
                Space.deleted_at.is_(None)
            )
        ).first()
        
        if not space:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error": {
                        "code": "FLASHCARD_NOT_FOUND",
                        "message": "Flashcard not found",
                        "details": {"flashcard_id": flashcard_id}
                    }
                }
            )
        
        folder = db.query(Folder).filter(
            and_(
                Folder.id == space.folder_id,
                Folder.owner_id == user.id,
                Folder.deleted_at.is_(None)
            )
        ).first()
        
        if not folder:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "error": {
                        "code": "FORBIDDEN",
                        "message": "You don't have permission to access this flashcard",
                        "details": {"flashcard_id": flashcard_id}
                    }
                }
            )
        
        # Extract card IDs and shuffle them
        card_ids = [card["id"] for card in flashcard.cards]
        shuffled_card_ids = card_ids.copy()
        random.shuffle(shuffled_card_ids)
        
        # Generate session ID
        session_id = str(uuid.uuid4())
        
        return FlashcardShuffleResponse(
            card_order=shuffled_card_ids,
            session_id=session_id,
            created_at=datetime.utcnow()
        )
    
    @staticmethod
    def delete_flashcard(
        db: Session, 
        user: User, 
        flashcard_id: str
    ) -> None:
        """
        Delete a flashcard deck.
        
        Args:
            db: Database session
            user: Current user
            flashcard_id: Flashcard UUID to delete
            
        Raises:
            HTTPException: If flashcard not found or permission denied
        """
        # Get flashcard and verify ownership
        flashcard = db.query(Flashcard).filter(
            Flashcard.id == flashcard_id
        ).first()
        
        if not flashcard:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error": {
                        "code": "FLASHCARD_NOT_FOUND",
                        "message": "Flashcard not found",
                        "details": {"flashcard_id": flashcard_id}
                    }
                }
            )
        
        # Verify user owns the parent folder
        space = db.query(Space).filter(
            and_(
                Space.id == flashcard.space_id,
                Space.deleted_at.is_(None)
            )
        ).first()
        
        if not space:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error": {
                        "code": "FLASHCARD_NOT_FOUND",
                        "message": "Flashcard not found",
                        "details": {"flashcard_id": flashcard_id}
                    }
                }
            )
        
        folder = db.query(Folder).filter(
            and_(
                Folder.id == space.folder_id,
                Folder.owner_id == user.id,
                Folder.deleted_at.is_(None)
            )
        ).first()
        
        if not folder:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "error": {
                        "code": "FORBIDDEN",
                        "message": "You don't have permission to access this flashcard",
                        "details": {"flashcard_id": flashcard_id}
                    }
                }
            )
        
        # Delete the flashcard
        db.delete(flashcard)
        db.commit() 