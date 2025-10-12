"""
Simple service classes for MVC architecture.
Contains business logic for the application.
"""
# app/services.py
from typing import List, Optional, Dict, Any
from app.utils.exceptions import (
    ValidationException,
    NotFoundException,
    BusinessLogicException
)


class UserService:
    """Simple user service for business logic."""
    
    def create_user(self, username: str, email: str, password: str, 
                   first_name: str = None, last_name: str = None, role: str = 'student'):
        """Create a new user."""
        from app.models.user import UserModel
        from app import db
        
        # Check if user already exists
        if UserModel.query.filter_by(email=email).first():
            raise BusinessLogicException("Email already exists")
        
        if UserModel.query.filter_by(username=username).first():
            raise BusinessLogicException("Username already exists")
        
        # Create new user
        user = UserModel(
            username=username,
            email=email,
            password_hash=password,  # Should be hashed in real implementation
            first_name=first_name,
            last_name=last_name,
            role=role
        )
        
        db.session.add(user)
        db.session.commit()
        return user
    
    def get_user_by_id(self, user_id: str):
        """Get user by ID."""
        from app.models.user import UserModel
        
        user = UserModel.query.filter_by(id=user_id).first()
        if not user:
            return None  # Return None instead of raising exception
        return user
    
    def get_user_by_email(self, email: str):
        """Get user by email."""
        from app.models.user import UserModel
        
        user = UserModel.query.filter_by(email=email).first()
        if not user:
            return None  # Return None instead of raising exception
        return user
    
    def authenticate_user(self, email: str, password: str):
        """Authenticate user."""
        user = self.get_user_by_email(email)
        if not user:
            raise ValidationException("User not found")
        # In real implementation, check password hash
        if user.password_hash != password:
            raise ValidationException("Invalid password")
        return user


class LessonService:
    """Simple lesson service for business logic."""
    
    def create_lesson(self, user_id: str, title: str, description: str = None):
        """Create a new lesson."""
        from app.models.lesson import LessonModel
        from app import db
        
        lesson = LessonModel(
            user_id=user_id,
            title=title,
            description=description
        )
        
        db.session.add(lesson)
        db.session.commit()
        return lesson
    
    def get_lessons_by_user(self, user_id: str):
        """Get all lessons for a user."""
        from app.models.lesson import LessonModel
        return LessonModel.query.filter_by(user_id=user_id).all()
    
    def get_lesson_by_id(self, lesson_id: str):
        """Get lesson by ID."""
        from app.models.lesson import LessonModel
        
        lesson = LessonModel.query.filter_by(id=lesson_id).first()
        if not lesson:
            raise NotFoundException("Lesson not found")
        return lesson


class NoteService:
    """Simple note service for business logic."""
    
    def create_note(self, user_id: str, title: str, content: str, lesson_id: str = None, **kwargs):
        """Create a new note (standalone or linked to lesson)."""
        from app.models.note import NoteModel
        from app import db
        import json
        
        note = NoteModel(
            user_id=user_id,
            lesson_id=lesson_id,  # Optional: None for standalone notes
            title=title,
            content=content
        )
        
        # Set additional fields if provided
        if 'note_type' in kwargs and kwargs['note_type'] is not None:
            note.note_type = kwargs['note_type']
        if 'is_public' in kwargs and kwargs['is_public'] is not None:
            note.is_public = kwargs['is_public']
        if 'status' in kwargs and kwargs['status'] is not None:
            note.status = kwargs['status']
        if 'external_link' in kwargs and kwargs['external_link'] is not None:
            note.external_link = kwargs['external_link']
        
        # Handle tags (convert list to JSON string)
        if 'tags' in kwargs and kwargs['tags'] is not None:
            if isinstance(kwargs['tags'], list):
                note.tags = json.dumps(kwargs['tags'])
            elif isinstance(kwargs['tags'], str):
                note.tags = kwargs['tags']
            else:
                note.tags = None
        
        db.session.add(note)
        db.session.commit()
        return note
    
    def get_notes_by_user(self, user_id: str):
        """Get all notes for a user."""
        from app.models.note import NoteModel
        return NoteModel.query.filter_by(user_id=user_id).all()
    
    def get_notes_by_lesson(self, lesson_id: str):
        """Get all notes for a lesson (optional feature)."""
        from app.models.note import NoteModel
        return NoteModel.query.filter_by(lesson_id=lesson_id).all()
    
    def get_standalone_notes(self, user_id: str):
        """Get all standalone notes (not linked to any lesson) for a user."""
        from app.models.note import NoteModel
        return NoteModel.query.filter_by(user_id=user_id, lesson_id=None).all()
    
    def get_note_by_id(self, note_id: str):
        """Get a specific note by ID."""
        from app.models.note import NoteModel
        
        note = NoteModel.query.filter_by(id=note_id).first()
        if not note:
            raise NotFoundException("Note not found")
        return note
    
    def update_note(self, note_id: str, **kwargs):
        """Update a note with any provided fields."""
        from app.models.note import NoteModel
        from app import db
        import json
        
        note = NoteModel.query.filter_by(id=note_id).first()
        if not note:
            raise NotFoundException("Note not found")
        
        # Update basic fields
        if 'title' in kwargs and kwargs['title'] is not None:
            note.title = kwargs['title']
        if 'content' in kwargs and kwargs['content'] is not None:
            note.content = kwargs['content']
        if 'note_type' in kwargs and kwargs['note_type'] is not None:
            note.note_type = kwargs['note_type']
        if 'is_public' in kwargs and kwargs['is_public'] is not None:
            note.is_public = kwargs['is_public']
        if 'status' in kwargs and kwargs['status'] is not None:
            note.status = kwargs['status']
        if 'external_link' in kwargs and kwargs['external_link'] is not None:
            note.external_link = kwargs['external_link']
        
        # Handle tags (convert list to JSON string)
        if 'tags' in kwargs and kwargs['tags'] is not None:
            if isinstance(kwargs['tags'], list):
                note.tags = json.dumps(kwargs['tags'])
            elif isinstance(kwargs['tags'], str):
                note.tags = kwargs['tags']
            else:
                note.tags = None
        
        db.session.commit()
        return note
    
    def get_user_notes(self, user_id: str):
        """Get all notes for a user (alias for get_notes_by_user)."""
        return self.get_notes_by_user(user_id)
    
    def delete_note(self, note_id: str, user_id: str = None):
        """Delete a note."""
        from app.models.note import NoteModel
        from app import db
        
        # Build query
        if user_id:
            note = NoteModel.query.filter_by(id=note_id, user_id=user_id).first()
        else:
            note = NoteModel.query.filter_by(id=note_id).first()
        
        if not note:
            return False
        
        db.session.delete(note)
        db.session.commit()
        return True
    
    def get_public_notes(self, limit=None, offset=None):
        """Get all public notes."""
        from app.models.note import NoteModel
        
        query = NoteModel.query.filter_by(is_public=True)
        
        if offset:
            query = query.offset(offset)
        if limit:
            query = query.limit(limit)
        
        return query.all()
    
    def get_notes_by_section(self, section_id: str):
        """Get notes for a specific section."""
        from app.models.note import NoteModel
        # For now, return empty list as section integration is not implemented
        return []
    
    def search_notes_by_tags(self, tags: list, user_id: str = None):
        """Search notes by tags."""
        from app.models.note import NoteModel
        import json
        
        # Build query
        query = NoteModel.query
        if user_id:
            query = query.filter_by(user_id=user_id)
        
        # Search for notes containing any of the tags
        notes = []
        for note in query.all():
            if note.tags:
                try:
                    note_tags = json.loads(note.tags) if isinstance(note.tags, str) else note.tags
                    if any(tag in note_tags for tag in tags):
                        notes.append(note)
                except (json.JSONDecodeError, TypeError):
                    # Handle malformed JSON
                    if any(tag in str(note.tags) for tag in tags):
                        notes.append(note)
        
        return notes
    
    def get_note_statistics(self, user_id: str = None):
        """Get note statistics."""
        from app.models.note import NoteModel
        
        query = NoteModel.query
        if user_id:
            query = query.filter_by(user_id=user_id)
        
        notes = query.all()
        
        stats = {
            'total': len(notes),
            'completed': len([n for n in notes if n.status == 'completed']),
            'pending': len([n for n in notes if n.status == 'pending']),
            'in_progress': len([n for n in notes if n.status == 'in-progress']),
            'public': len([n for n in notes if n.is_public]),
            'private': len([n for n in notes if not n.is_public])
        }
        
        return stats
    
    def get_recent_notes(self, user_id: str = None, limit: int = 10):
        """Get recent notes."""
        from app.models.note import NoteModel
        
        query = NoteModel.query
        if user_id:
            query = query.filter_by(user_id=user_id)
        
        return query.order_by(NoteModel.created_at.desc()).limit(limit).all()


class TaskService:
    """Simple task service for business logic."""
    
    def create_task(self, user_id: str, title: str, description: str = None):
        """Create a new task."""
        from app.models.task import TaskModel
        from app import db
        
        task = TaskModel(
            user_id=user_id,
            title=title,
            description=description
        )
        
        db.session.add(task)
        db.session.commit()
        return task
    
    def get_tasks_by_user(self, user_id: str):
        """Get all tasks for a user."""
        from app.models.task import TaskModel
        return TaskModel.query.filter_by(user_id=user_id).all()
    
    def get_task_by_id(self, task_id: str):
        """Get task by ID."""
        from app.models.task import TaskModel
        
        task = TaskModel.query.filter_by(id=task_id).first()
        if not task:
            raise NotFoundException("Task not found")
        return task
