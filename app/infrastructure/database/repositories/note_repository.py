"""
Note repository implementation using SQLAlchemy.
Infrastructure layer implementation of NoteRepository interface.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from app.domain.entities.note import Note, NoteType
from app.domain.interfaces.repositories.note_repository import NoteRepository
from ..models.note_model import NoteModel
from app import db
from app.shared.exceptions import ValidationException


class NoteRepositoryImpl(NoteRepository):
    """
    SQLAlchemy implementation of NoteRepository interface.
    Handles all database operations for Note entity.
    """
    
    def create(self, note: Note) -> Note:
        """
        Create a new note.
        
        Args:
            note: Note entity to create
            
        Returns:
            Created note entity
            
        Raises:
            ValidationException: If note data is invalid
        """
        try:
            note_model = NoteModel.from_domain_entity(note)
            db.session.add(note_model)
            db.session.commit()
            return note_model.to_domain_entity()
        except Exception as e:
            db.session.rollback()
            raise ValidationException(f"Failed to create note: {str(e)}")
    
    def get_by_id(self, note_id: str) -> Optional[Note]:
        """
        Get note by ID.
        
        Args:
            note_id: Note ID to search for
            
        Returns:
            Note entity if found, None otherwise
        """
        note_model = NoteModel.query.filter_by(id=note_id).first()
        return note_model.to_domain_entity() if note_model else None
    
    def get_by_user_id(self, user_id: str, limit: Optional[int] = None, offset: Optional[int] = None) -> List[Note]:
        """
        Get notes by user ID.
        
        Args:
            user_id: User ID to search for
            limit: Maximum number of notes to return
            offset: Number of notes to skip
            
        Returns:
            List of note entities
        """
        query = NoteModel.query.filter_by(user_id=user_id).order_by(NoteModel.created_at.desc())
        
        if offset:
            query = query.offset(offset)
        
        if limit:
            query = query.limit(limit)
        
        note_models = query.all()
        return [note_model.to_domain_entity() for note_model in note_models]
    
    def update(self, note: Note) -> Note:
        """
        Update existing note.
        
        Args:
            note: Note entity to update
            
        Returns:
            Updated note entity
            
        Raises:
            NotFoundException: If note doesn't exist
            ValidationException: If note data is invalid
        """
        try:
            note_model = NoteModel.query.filter_by(id=note.id).first()
            if not note_model:
                from ...shared.exceptions import NotFoundException
                raise NotFoundException("Note", note.id)
            
            # Update fields
            note_model.user_id = note.user_id
            note_model.title = note.title
            note_model.content = note.content
            note_model.note_type = note.note_type.value
            note_model.lesson_id = note.lesson_id
            note_model.section_id = note.section_id
            note_model.tags = json.dumps(note.tags) if note.tags else None
            note_model.is_public = note.is_public
            note_model.view_count = note.view_count
            note_model.word_count = note.word_count
            note_model.updated_at = note.updated_at
            
            db.session.commit()
            return note_model.to_domain_entity()
        except Exception as e:
            db.session.rollback()
            if "NotFoundException" in str(type(e)):
                raise
            raise ValidationException(f"Failed to update note: {str(e)}")
    
    def delete(self, note_id: str) -> bool:
        """
        Delete note by ID.
        
        Args:
            note_id: Note ID to delete
            
        Returns:
            True if deleted, False if not found
        """
        try:
            note_model = NoteModel.query.filter_by(id=note_id).first()
            if not note_model:
                return False
            
            db.session.delete(note_model)
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            raise ValidationException(f"Failed to delete note: {str(e)}")
    
    def get_by_lesson_id(self, lesson_id: str, limit: Optional[int] = None) -> List[Note]:
        """
        Get notes by lesson ID.
        
        Args:
            lesson_id: Lesson ID to filter by
            limit: Maximum number of results
            
        Returns:
            List of note entities for the lesson
        """
        query = NoteModel.query.filter_by(lesson_id=lesson_id).order_by(NoteModel.created_at.desc())
        
        if limit:
            query = query.limit(limit)
        
        note_models = query.all()
        return [note_model.to_domain_entity() for note_model in note_models]
    
    def get_by_section_id(self, section_id: str, limit: Optional[int] = None) -> List[Note]:
        """
        Get notes by section ID.
        
        Args:
            section_id: Section ID to filter by
            limit: Maximum number of results
            
        Returns:
            List of note entities for the section
        """
        query = NoteModel.query.filter_by(section_id=section_id).order_by(NoteModel.created_at.desc())
        
        if limit:
            query = query.limit(limit)
        
        note_models = query.all()
        return [note_model.to_domain_entity() for note_model in note_models]
    
    def get_by_note_type(self, user_id: str, note_type: NoteType, limit: Optional[int] = None) -> List[Note]:
        """
        Get notes by type.
        
        Args:
            user_id: User ID to filter by
            note_type: Note type to filter by
            limit: Maximum number of results
            
        Returns:
            List of note entities with specified type
        """
        query = NoteModel.query.filter_by(
            user_id=user_id,
            note_type=note_type.value
        ).order_by(NoteModel.created_at.desc())
        
        if limit:
            query = query.limit(limit)
        
        note_models = query.all()
        return [note_model.to_domain_entity() for note_model in note_models]
    
    def get_public_notes(self, limit: Optional[int] = None, offset: Optional[int] = None) -> List[Note]:
        """
        Get public notes.
        
        Args:
            limit: Maximum number of results
            offset: Number of notes to skip
            
        Returns:
            List of public note entities
        """
        query = NoteModel.query.filter_by(is_public=True).order_by(NoteModel.created_at.desc())
        
        if offset:
            query = query.offset(offset)
        
        if limit:
            query = query.limit(limit)
        
        note_models = query.all()
        return [note_model.to_domain_entity() for note_model in note_models]
    
    def search(self, user_id: str, query: str, limit: Optional[int] = None) -> List[Note]:
        """
        Search notes by query.
        
        Args:
            user_id: User ID to filter by
            query: Search query
            limit: Maximum number of results
            
        Returns:
            List of matching note entities
        """
        search_query = NoteModel.query.filter(
            db.and_(
                NoteModel.user_id == user_id,
                db.or_(
                    NoteModel.title.contains(query),
                    NoteModel.content.contains(query)
                )
            )
        ).order_by(NoteModel.created_at.desc())
        
        if limit:
            search_query = search_query.limit(limit)
        
        note_models = search_query.all()
        return [note_model.to_domain_entity() for note_model in note_models]
    
    def search_by_tags(self, user_id: str, tags: List[str], limit: Optional[int] = None) -> List[Note]:
        """
        Search notes by tags.
        
        Args:
            user_id: User ID to filter by
            tags: List of tags to search for
            limit: Maximum number of results
            
        Returns:
            List of note entities with matching tags
        """
        # This is a simplified implementation
        # In a real application, you might want to use a more sophisticated tag search
        query = NoteModel.query.filter_by(user_id=user_id)
        
        # Filter by tags (simplified - checks if any tag is contained in the tags JSON)
        for tag in tags:
            query = query.filter(NoteModel.tags.contains(tag))
        
        query = query.order_by(NoteModel.created_at.desc())
        
        if limit:
            query = query.limit(limit)
        
        note_models = query.all()
        return [note_model.to_domain_entity() for note_model in note_models]
    
    def get_notes_by_date_range(
        self,
        user_id: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        limit: Optional[int] = None
    ) -> List[Note]:
        """
        Get notes by date range.
        
        Args:
            user_id: User ID to filter by
            start_date: Start date (ISO format)
            end_date: End date (ISO format)
            limit: Maximum number of results
            
        Returns:
            List of note entities in date range
        """
        query = NoteModel.query.filter_by(user_id=user_id)
        
        if start_date:
            start_dt = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
            query = query.filter(NoteModel.created_at >= start_dt)
        
        if end_date:
            end_dt = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
            query = query.filter(NoteModel.created_at <= end_dt)
        
        query = query.order_by(NoteModel.created_at.desc())
        
        if limit:
            query = query.limit(limit)
        
        note_models = query.all()
        return [note_model.to_domain_entity() for note_model in note_models]
    
    def get_note_statistics(self, user_id: str) -> Dict[str, Any]:
        """
        Get note statistics for user.
        
        Args:
            user_id: User ID
            
        Returns:
            Dictionary with note statistics
        """
        total_notes = NoteModel.query.filter_by(user_id=user_id).count()
        
        # Count by type
        type_counts = db.session.query(
            NoteModel.note_type,
            db.func.count(NoteModel.id)
        ).filter_by(user_id=user_id).group_by(NoteModel.note_type).all()
        
        # Count public notes
        public_count = NoteModel.query.filter_by(
            user_id=user_id,
            is_public=True
        ).count()
        
        # Total views
        total_views = db.session.query(
            db.func.sum(NoteModel.view_count)
        ).filter_by(user_id=user_id).scalar() or 0
        
        # Total words
        total_words = db.session.query(
            db.func.sum(NoteModel.word_count)
        ).filter_by(user_id=user_id).scalar() or 0
        
        return {
            'total_notes': total_notes,
            'type_counts': dict(type_counts),
            'public_count': public_count,
            'total_views': total_views,
            'total_words': total_words
        }
    
    def count_by_user(self, user_id: str) -> int:
        """
        Count notes by user.
        
        Args:
            user_id: User ID
            
        Returns:
            Total count of notes for user
        """
        return NoteModel.query.filter_by(user_id=user_id).count()
    
    def get_recent_notes(self, user_id: str, limit: int = 10) -> List[Note]:
        """
        Get recent notes for user.
        
        Args:
            user_id: User ID
            limit: Maximum number of results
            
        Returns:
            List of recent note entities
        """
        note_models = NoteModel.query.filter_by(
            user_id=user_id
        ).order_by(NoteModel.updated_at.desc()).limit(limit).all()
        
        return [note_model.to_domain_entity() for note_model in note_models]
    
    def get_most_viewed_notes(self, user_id: str, limit: int = 10) -> List[Note]:
        """
        Get most viewed notes for user.
        
        Args:
            user_id: User ID
            limit: Maximum number of results
            
        Returns:
            List of most viewed note entities
        """
        note_models = NoteModel.query.filter_by(
            user_id=user_id
        ).order_by(NoteModel.view_count.desc()).limit(limit).all()
        
        return [note_model.to_domain_entity() for note_model in note_models]
    
    def get_all_tags(self, user_id: str) -> List[str]:
        """
        Get all unique tags for user.
        
        Args:
            user_id: User ID
            
        Returns:
            List of unique tags
        """
        # This is a simplified implementation
        # In a real application, you might want to use a separate tags table
        notes = NoteModel.query.filter_by(user_id=user_id).all()
        all_tags = set()
        
        for note in notes:
            if note.tags:
                try:
                    tags = json.loads(note.tags)
                    all_tags.update(tags)
                except (json.JSONDecodeError, TypeError):
                    continue
        
        return sorted(list(all_tags))
