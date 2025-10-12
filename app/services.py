"""
Simple service classes for MVC architecture.
Contains business logic for the application.
"""

import json
from typing import List, Optional, Dict, Any
from datetime import datetime
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
            raise NotFoundException("User not found")
        return user
    
    def get_user_by_email(self, email: str):
        """Get user by email."""
        from app.models.user import UserModel
        
        user = UserModel.query.filter_by(email=email).first()
        if not user:
            raise NotFoundException("User not found")
        return user
    
    def authenticate_user(self, email: str, password: str):
        """Authenticate user."""
        user = self.get_user_by_email(email)
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
    
    def create_note(self, user_id: str, lesson_id: str, title: str, content: str):
        """Create a new note."""
        from app.models.note import NoteModel
        from app import db
        
        note = NoteModel(
            user_id=user_id,
            lesson_id=lesson_id,
            title=title,
            content=content
        )
        
        db.session.add(note)
        db.session.commit()
        return note
    
    def get_notes_by_user(self, user_id: str):
        """Get all notes for a user."""
        from app.models.note import NoteModel
        return NoteModel.query.filter_by(user_id=user_id).all()
    
    def get_notes_by_lesson(self, lesson_id: str):
        """Get all notes for a lesson."""
        from app.models.note import NoteModel
        return NoteModel.query.filter_by(lesson_id=lesson_id).all()
    
    def get_note_by_id(self, note_id: str):
        """Get a specific note by ID."""
        from app.models.note import NoteModel
        
        note = NoteModel.query.filter_by(id=note_id).first()
        if not note:
            raise NotFoundException("Note not found")
        return note
    
    def update_note(self, note_id: str, title: str = None, content: str = None):
        """Update a note."""
        from app.models.note import NoteModel
        from app import db
        
        note = NoteModel.query.filter_by(id=note_id).first()
        if not note:
            raise NotFoundException("Note not found")
        
        if title is not None:
            note.title = title
        if content is not None:
            note.content = content
        
        db.session.commit()
        return note
    
    def get_user_notes(self, user_id: str):
        """Get all notes for a user (alias for get_notes_by_user)."""
        return self.get_notes_by_user(user_id)
    
    def delete_note(self, note_id: str):
        """Delete a note."""
        from app.models.note import NoteModel
        from app import db
        
        note = NoteModel.query.filter_by(id=note_id).first()
        if not note:
            raise NotFoundException("Note not found")
        
        db.session.delete(note)
        db.session.commit()
        return True


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


class PomodoroSessionService:
    """Service layer for Pomodoro session management"""

    def create_session(self, user_id: str, session_type: str, duration: int, task: Optional[str] = None):
        """Create a new Pomodoro session"""
        from app import db
        try:
            from app.models.pomodoro_session import PomodoroSessionModel
            
            if not user_id:
                raise ValidationException("User ID is required")
            
            if session_type not in ['focus', 'short_break', 'long_break']:
                raise ValidationException("Invalid session type")
            
            if duration <= 0:
                raise ValidationException("Duration must be positive")

            session = PomodoroSessionModel(
                user_id=user_id,
                session_type=session_type,
                duration=duration,
                start_time=datetime.utcnow(),
                task=task,
                status='active'
            )

            db.session.add(session)
            db.session.commit()
            
            return session
        except Exception as e:
            db.session.rollback()
            print(f"Error creating session: {str(e)}")
            raise

    def get_session(self, session_id: str):
        """Get a specific session by ID"""
        from app.models.pomodoro_session import PomodoroSessionModel
        return PomodoroSessionModel.query.get(session_id)

    def get_user_sessions(self, user_id: str):
        """Get all sessions for a user"""
        from app.models.pomodoro_session import PomodoroSessionModel
        return PomodoroSessionModel.query.filter_by(user_id=user_id).all()

    def update_session(self, session_id: str, data: Dict):
        """Update a session"""
        from app.models.pomodoro_session import PomodoroSessionModel
        from app.models.task import TaskModel
        from app import db
        
        session = self.get_session(session_id)
        if not session:
            return None

        # Update allowed fields
        if 'actual_duration' in data:
            session.actual_duration = data['actual_duration']
        if 'end_time' in data:
            session.end_time = data['end_time']
        if 'status' in data:
            session.status = data['status']
        if 'productivity_score' in data:
            session.productivity_score = data['productivity_score']

        # Handle task update
        if 'task' in data:
            task_name = data['task']
            if task_name:
                # Try to find existing task first
                task_obj = TaskModel.query.filter_by(user_id=session.user_id, title=task_name).first()
                if not task_obj:
                    # Create new task if it doesn't exist
                    task_obj = TaskModel(
                        user_id=session.user_id,
                        title=task_name
                    )
                    db.session.add(task_obj)
                    db.session.flush()  # Flush to get the task ID
                
                session.task_id = task_obj.id
            else:
                session.task_id = None

        db.session.commit()
        return session

    def end_session(self, session_id: str, status: str = 'completed'):
        """End a Pomodoro session"""
        from app.models.pomodoro_session import PomodoroSessionModel
        from app import db
        
        session = self.get_session(session_id)
        if not session:
            return None

        session.end_time = datetime.utcnow()
        session.status = status
        if session.start_time:
            session.actual_duration = int((session.end_time - session.start_time).total_seconds() / 60)

        db.session.commit()
        return session

    def get_active_session(self, user_id: str):
        """Get user's active session if exists"""
        from app.models.pomodoro_session import PomodoroSessionModel
        return PomodoroSessionModel.query.filter_by(
            user_id=user_id,
            status='active'
        ).first()

    def interrupt_session(self, session_id: str):
        """Mark a session as interrupted"""
        return self.end_session(session_id, status='interrupted')

    def delete_session(self, session_id: str) -> bool:
        """Delete a session"""
        from app.models.pomodoro_session import PomodoroSessionModel
        from app import db
        
        session = self.get_session(session_id)
        if not session:
            return False

        db.session.delete(session)
        db.session.commit()
        return True
