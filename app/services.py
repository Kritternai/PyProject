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
        from werkzeug.security import generate_password_hash
        
        # Validate input
        if not email or not password:
            raise ValidationException("Email and password are required")
        
        if len(password) < 8:
            raise ValidationException("Password must be at least 8 characters long")
        
        # Check if user already exists
        if UserModel.query.filter_by(email=email).first():
            raise BusinessLogicException("อีเมลนี้มีผู้ใช้แล้ว")
        
        if UserModel.query.filter_by(username=username).first():
            raise BusinessLogicException("ชื่อผู้ใช้นี้มีคนใช้แล้ว")
        
        # Hash password
        password_hash = generate_password_hash(password)
        
        # Create new user
        user = UserModel(
            username=username,
            email=email,
            password_hash=password_hash,
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
        from werkzeug.security import check_password_hash
        
        user = self.get_user_by_email(email)
        # Check password hash
        if not check_password_hash(user.password_hash, password):
            raise ValidationException("รหัสผ่านไม่ถูกต้อง")
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
        
    # --- โค้ดใหม่ที่เพิ่มเข้ามาใน LessonService ---
    def get_lessons_count(self, user_id: str):
        """นับ lessons ทั้งหมด"""
        from app.models.lesson import LessonModel
        return LessonModel.query.filter_by(user_id=user_id).count()

    def get_lessons_completed_today(self, user_id: str):
        """นับ lessons ที่เสร็จวันนี้"""
        from app.models.lesson import LessonModel
        from datetime import datetime
        from app import db
        
        today = datetime.now().date()
        
        count = LessonModel.query.filter(
            LessonModel.user_id == user_id,
            LessonModel.status == 'completed',
            db.func.date(LessonModel.updated_at) == today
        ).count()
        
        return count
    # --- จบโค้ดที่เพิ่ม ---


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

    # --- โค้ดใหม่ที่เพิ่มเข้ามาใน NoteService ---
    def get_notes_count_today(self, user_id: str):
        """นับ notes ที่สร้างวันนี้"""
        from datetime import datetime
        from app.models.note import NoteModel
        from app import db

        today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        
        count = NoteModel.query.filter(
            NoteModel.user_id == user_id,
            NoteModel.created_at >= today_start
        ).count()
        
        return count

    def get_total_notes_count(self, user_id: str):
        """นับ notes ทั้งหมด"""
        from app.models.note import NoteModel
        return NoteModel.query.filter_by(user_id=user_id).count()
    # --- จบโค้ดที่เพิ่ม ---


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

# --- Class ที่เพิ่มเข้ามา ---
class PomodoroService:
    """Service for Pomodoro tracking logic."""
    
    def get_pomodoros_count_today(self, user_id: str):
        """นับ pomodoro ที่ทำวันนี้"""
        from datetime import date
        from app.models.pomodoro import PomodoroSessionModel
        from app import db

        today = date.today()
        
        count = PomodoroSessionModel.query.filter(
            PomodoroSessionModel.user_id == user_id,
            db.func.date(PomodoroSessionModel.created_at) == today
        ).count()
        
        return count
    
    def get_study_time_today(self, user_id: str, duration_per_session: int = 25):
        """คำนวณเวลาเรียนวันนี้ (นาที)"""
        count = self.get_pomodoros_count_today(user_id)
        return count * duration_per_session

    def get_total_pomodoros_count(self, user_id: str):
        """นับ pomodoros ทั้งหมด"""
        from app.models.pomodoro import PomodoroSessionModel
        return PomodoroSessionModel.query.filter_by(user_id=user_id).count()
    