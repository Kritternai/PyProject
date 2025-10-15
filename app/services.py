"""
Simple service classes for MVC architecture.
Contains business logic for the application.
"""

# app/services.py

import json
from typing import List, Optional, Dict, Any
from datetime import datetime, date, timedelta
from sqlalchemy import func, or_
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
        from werkzeug.security import check_password_hash
        
        user = self.get_user_by_email(email)
        # Check password hash
        if not check_password_hash(user.password_hash, password):
            raise ValidationException("รหัสผ่านไม่ถูกต้อง")
        return user

    def update_user_profile(self, user_id: int, data: Dict[str, Any]):
        """Update user profile."""
        from app.models.user import UserModel
        from app import db
        
        # Get user
        user = UserModel.query.get(user_id)
        if not user:
            raise NotFoundException("User not found")
        
        # Update fields if provided
        if 'first_name' in data:
            user.first_name = data['first_name'] or None
        if 'last_name' in data:
            user.last_name = data['last_name'] or None
        if 'email' in data and data['email']:
            # Check if email is already taken by another user
            existing_user = UserModel.query.filter(
                UserModel.email == data['email'],
                UserModel.id != user_id
            ).first()
            if existing_user:
                raise BusinessLogicException("This email is already in use")
            user.email = data['email']
        if 'bio' in data:
            user.bio = data['bio'] or None
        
        try:
            db.session.commit()
            return user
        except Exception as e:
            db.session.rollback()
            raise BusinessLogicException(f"Failed to update profile: {str(e)}")


class BaseLessonService:
    def __init__(self):
        from app import db
        self._db = db
        self._model_class = None
    
    def _validate_user_id(self, user_id: str) -> bool:
        if not user_id or not isinstance(user_id, str) or len(user_id.strip()) == 0:
            return False
        return True
    
    def _validate_lesson_id(self, lesson_id: str) -> bool:
        if not lesson_id or not isinstance(lesson_id, str) or len(lesson_id.strip()) == 0:
            return False
        return True
    
    def _validate_title(self, title: str) -> bool:
        if not title or not isinstance(title, str) or len(title.strip()) < 3:
            return False
        return True


class LessonService(BaseLessonService):
    def __init__(self):
        super().__init__()
        from app.models.lesson import LessonModel
        self._model_class = LessonModel
        self._max_title_length = 200
        self._max_description_length = 1000
    
    def _create_lesson_model(self, user_id: str, title: str, **kwargs):
        return self._model_class(
            user_id=user_id,
            title=title.strip(),
            description=kwargs.get('description', '').strip() if kwargs.get('description') else None,
            difficulty_level=kwargs.get('difficulty_level', 'beginner'),
            estimated_duration=kwargs.get('estimated_duration'),
            color_theme=kwargs.get('color_theme', 1),
            source_platform=kwargs.get('source_platform', 'manual'),
            external_id=kwargs.get('external_id'),
            external_url=kwargs.get('external_url'),
            author_name=kwargs.get('author_name'),
            subject=kwargs.get('subject'),
            grade_level=kwargs.get('grade_level')
        )
    
    def _validate_lesson_data(self, user_id: str, title: str, **kwargs):
        if not self._validate_user_id(user_id):
            raise ValueError("Invalid user ID")
        
        if not self._validate_title(title):
            raise ValueError("Title must be at least 3 characters long")
        
        if len(title) > self._max_title_length:
            raise ValueError(f"Title cannot exceed {self._max_title_length} characters")
        
        description = kwargs.get('description', '')
        if description and len(description) > self._max_description_length:
            raise ValueError(f"Description cannot exceed {self._max_description_length} characters")
    
    def _get_lesson_query(self, user_id: str = None, lesson_id: str = None, status: str = None):
        query = self._model_class.query
        
        if user_id:
            query = query.filter_by(user_id=user_id)
        
        if lesson_id:
            query = query.filter_by(id=lesson_id)
        
        if status:
            query = query.filter_by(status=status)
        
        return query
    
    def _commit_changes(self):
        try:
            self._db.session.commit()
        except Exception as e:
            self._db.session.rollback()
            raise e
    
    def create_lesson(self, user_id: str, title: str, **kwargs):
        self._validate_lesson_data(user_id, title, **kwargs)
        
        lesson = self._create_lesson_model(user_id, title, **kwargs)
        self._db.session.add(lesson)
        self._commit_changes()
        
        return lesson
    
    def get_lessons_by_user(self, user_id: str):
        if not self._validate_user_id(user_id):
            raise ValueError("Invalid user ID")
        
        return self._get_lesson_query(user_id=user_id).all()
    
    def get_lesson_by_id(self, lesson_id: str):
        if not self._validate_lesson_id(lesson_id):
            raise ValueError("Invalid lesson ID")
        
        lesson = self._get_lesson_query(lesson_id=lesson_id).first()
        if not lesson:
            raise NotFoundException("Lesson", lesson_id)
        
        return lesson
    
    def get_lessons_count(self, user_id: str) -> int:
        if not self._validate_user_id(user_id):
            return 0
        
        return self._get_lesson_query(user_id=user_id).count()
    
    def get_user_lessons_count(self, user_id: str) -> int:
        return self.get_lessons_count(user_id)
    
    def get_completed_lessons_count(self, user_id: str) -> int:
        if not self._validate_user_id(user_id):
            return 0
        
        return self._get_lesson_query(user_id=user_id, status='completed').count()
    
    def get_lessons_completed_today(self, user_id: str) -> int:
        if not self._validate_user_id(user_id):
            return 0
        
        from datetime import datetime
        
        today = datetime.now().date()
        
        count = self._get_lesson_query(user_id=user_id, status='completed').filter(
            self._db.func.date(self._model_class.updated_at) == today
        ).count()
        
        return count
    
    def get_lesson_statistics(self, user_id: str) -> dict:
        if not self._validate_user_id(user_id):
            return {
                'total_lessons': 0,
                'completed_lessons': 0,
                'in_progress_lessons': 0,
                'not_started_lessons': 0,
                'completed_today': 0
            }
        
        total = self.get_lessons_count(user_id)
        completed = self.get_completed_lessons_count(user_id)
        in_progress = self._get_lesson_query(user_id=user_id, status='in_progress').count()
        not_started = self._get_lesson_query(user_id=user_id, status='not_started').count()
        completed_today = self.get_lessons_completed_today(user_id)
        
        return {
            'total_lessons': total,
            'completed_lessons': completed,
            'in_progress_lessons': in_progress,
            'not_started_lessons': not_started,
            'completed_today': completed_today,
            'completion_rate': (completed / total * 100) if total > 0 else 0
        }
    
    def update_lesson(self, lesson_id: str, user_id: str, **kwargs):
        if not self._validate_lesson_id(lesson_id):
            raise ValueError("Invalid lesson ID")
        
        if not self._validate_user_id(user_id):
            raise ValueError("Invalid user ID")
        
        lesson = self.get_lesson_by_id(lesson_id)
        
        if lesson.user_id != user_id:
            raise PermissionError("Only lesson owner can update lesson")
        
        if 'title' in kwargs:
            if not self._validate_title(kwargs['title']):
                raise ValueError("Invalid title")
            lesson.title = kwargs['title'].strip()
        
        if 'description' in kwargs:
            description = kwargs['description']
            if description and len(description) > self._max_description_length:
                raise ValueError(f"Description cannot exceed {self._max_description_length} characters")
            lesson.description = description.strip() if description else None
        
        for field in ['difficulty_level', 'estimated_duration', 'color_theme', 
                     'author_name', 'subject', 'grade_level', 'status']:
            if field in kwargs:
                setattr(lesson, field, kwargs[field])
        
        self._commit_changes()
        return lesson
    
    def delete_lesson(self, lesson_id: str, user_id: str):
        if not self._validate_lesson_id(lesson_id):
            raise ValueError("Invalid lesson ID")
        
        if not self._validate_user_id(user_id):
            raise ValueError("Invalid user ID")
        
        lesson = self.get_lesson_by_id(lesson_id)
        
        if lesson.user_id != user_id:
            raise PermissionError("Only lesson owner can delete lesson")
        
        self._db.session.delete(lesson)
        self._commit_changes()
        return True
    
    def toggle_favorite(self, lesson_id: str, user_id: str):
        if not self._validate_lesson_id(lesson_id):
            raise ValueError("Invalid lesson ID")
        
        if not self._validate_user_id(user_id):
            raise ValueError("Invalid user ID")
        
        lesson = self.get_lesson_by_id(lesson_id)
        
        if lesson.user_id != user_id:
            raise PermissionError("Only lesson owner can toggle favorite")
        
        lesson.is_favorite = not lesson.is_favorite
        self._commit_changes()
        return lesson


class GoogleClassroomLessonService(LessonService):
    def __init__(self):
        super().__init__()
        self._source_platform = 'google_classroom'
        self._external_api_client = None
    
    def create_lesson(self, user_id: str, title: str, external_id: str = None, **kwargs):
        if not external_id:
            raise ValueError("Google Classroom course ID is required")
        
        kwargs.update({
            'source_platform': self._source_platform,
            'external_id': external_id,
            'external_url': f"https://classroom.google.com/c/{external_id}"
        })
        
        return super().create_lesson(user_id, title, **kwargs)
    
    def sync_with_google_classroom(self, lesson_id: str):
        lesson = self.get_lesson_by_id(lesson_id)
        
        if lesson.source_platform != self._source_platform:
            raise ValueError("Lesson is not a Google Classroom lesson")
        
        return lesson


class MicrosoftTeamsLessonService(LessonService):
    def __init__(self):
        super().__init__()
        self._source_platform = 'microsoft_teams'
        self._external_api_client = None
    
    def create_lesson(self, user_id: str, title: str, external_id: str = None, **kwargs):
        if not external_id:
            raise ValueError("Microsoft Teams team ID is required")
        
        kwargs.update({
            'source_platform': self._source_platform,
            'external_id': external_id,
            'external_url': f"https://teams.microsoft.com/l/team/{external_id}"
        })
        
        return super().create_lesson(user_id, title, **kwargs)
    
    def sync_with_microsoft_teams(self, lesson_id: str):
        lesson = self.get_lesson_by_id(lesson_id)
        
        if lesson.source_platform != self._source_platform:
            raise ValueError("Lesson is not a Microsoft Teams lesson")
        
        return lesson


class LessonServiceFactory:
    @staticmethod
    def create_lesson_service(platform: str = 'manual') -> BaseLessonService:
        if platform == 'manual':
            return LessonService()
        elif platform == 'google_classroom':
            return GoogleClassroomLessonService()
        elif platform == 'microsoft_teams':
            return MicrosoftTeamsLessonService()
        else:
            raise ValueError(f"Unsupported platform: {platform}")
    
    @staticmethod
    def get_service_for_lesson(lesson_model) -> BaseLessonService:
        platform = getattr(lesson_model, 'source_platform', 'manual')
        return LessonServiceFactory.create_lesson_service(platform)


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
    
    def get_user_notes_count(self, user_id: str):
        """Get total number of notes for a user."""
        from app.models.note import NoteModel
        return NoteModel.query.filter_by(user_id=user_id).count()
    
    def get_notes_count_since(self, user_id: str, since_date):
        """Get number of notes created since a specific date."""
        from app.models.note import NoteModel
        return NoteModel.query.filter_by(user_id=user_id)\
            .filter(NoteModel.created_at >= since_date).count()
    
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
            raise NotFoundException("Note", note_id)
        return note
    
    def update_note(self, note_id: str, **kwargs):
        """Update a note with any provided fields."""
        from app.models.note import NoteModel
        from app import db
        import json
        
        note = NoteModel.query.filter_by(id=note_id).first()
        if not note:
            raise NotFoundException("Note", note_id)
        
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
    """Business logic for task management and Pomodoro integrations."""

    VALID_STATUSES = {"pending", "in_progress", "completed"}
    VALID_PRIORITIES = {"low", "medium", "high"}
    VALID_TASK_TYPES = {"focus", "study", "break", "other"}

    # ------------------------------------------------------------------
    # CRUD OPERATIONS
    # ------------------------------------------------------------------
    def create_task(
        self,
        user_id: str,
        title: str,
        description: Optional[str] = None,
        task_type: Optional[str] = None,
        priority: Optional[str] = None,
        due_date: Optional[datetime] = None,
        estimated_duration: Optional[int] = None,
        lesson_id: Optional[str] = None,
        section_id: Optional[str] = None,
        tags: Optional[Any] = None,
        is_reminder_enabled: bool = True,
        reminder_time: Optional[int] = None,
        status: Optional[str] = None
    ):
        """Create a new task for the given user."""
        from app.models.task import TaskModel
        from app import db

        if not user_id:
            raise ValidationException("User ID is required")

        normalized_title = (title or "").strip()
        if not normalized_title:
            raise ValidationException("Task title is required")

        normalized_type = self._normalize_task_type(task_type)
        normalized_priority = self._normalize_priority(priority)
        normalized_status = self._normalize_status(status)

        task = TaskModel(
            user_id=user_id,
            title=normalized_title,
            description=description,
            task_type=normalized_type,
            status=normalized_status,
            priority=normalized_priority,
            due_date=due_date,
            estimated_duration=self._coerce_int(estimated_duration),
            lesson_id=lesson_id,
            section_id=section_id,
            tags=self._serialize_tags(tags),
            is_reminder_enabled=bool(is_reminder_enabled),
            reminder_time=self._coerce_int(reminder_time)
        )

        if normalized_status == "completed":
            task.completed_at = datetime.utcnow()
            task.progress_percentage = 100

        db.session.add(task)
        db.session.commit()

        self._refresh_pomodoro_statistics(user_id, task.created_at.date() if task.created_at else date.today())
        return task
    
    def get_user_tasks_count(self, user_id: str):
        """Get total number of tasks for a user."""
        from app.models.task import TaskModel
        return TaskModel.query.filter_by(user_id=user_id).count()
    
    def get_completed_tasks_count(self, user_id: str):
        """Get number of completed tasks for a user."""
        from app.models.task import TaskModel
        return TaskModel.query.filter_by(user_id=user_id, status='completed').count()

    def get_tasks_by_user(self, user_id: str, limit: Optional[int] = None, offset: Optional[int] = None):
        """Return tasks for user ordered by creation date (desc)."""
        from app.models.task import TaskModel

        query = TaskModel.query.filter_by(user_id=user_id).order_by(TaskModel.created_at.desc())
        if offset:
            query = query.offset(offset)
        if limit:
            query = query.limit(limit)
        return query.all()

    def get_user_tasks(self, user_id: str, limit: Optional[int] = None, offset: Optional[int] = None):
        """Compatibility wrapper used by existing controllers."""
        return self.get_tasks_by_user(user_id, limit=limit, offset=offset)

    def get_task_by_id(self, task_id: str, user_id: Optional[str] = None):
        """Load a task by ID and optional user ownership."""
        from app.models.task import TaskModel

        query = TaskModel.query.filter_by(id=task_id)
        if user_id:
            query = query.filter(TaskModel.user_id == user_id)

        task = query.first()
        if not task:
            raise NotFoundException("Task", task_id)
        return task

    def update_task(
        self,
        task_id: str,
        user_id: str,
        title: Optional[str] = None,
        description: Optional[str] = None,
        task_type: Optional[str] = None,
        priority: Optional[str] = None,
        due_date: Optional[datetime] = None,
        estimated_duration: Optional[int] = None,
        lesson_id: Optional[str] = None,
        section_id: Optional[str] = None,
        tags: Optional[Any] = None,
        is_reminder_enabled: Optional[bool] = None,
        reminder_time: Optional[int] = None
    ):
        """Update mutable fields on an existing task."""
        from app.models.task import TaskModel
        from app import db

        task = self.get_task_by_id(task_id, user_id)

        if title is not None:
            normalized_title = title.strip()
            if not normalized_title:
                raise ValidationException("Task title cannot be empty")
            task.title = normalized_title

        if description is not None:
            task.description = description

        if task_type is not None:
            task.task_type = self._normalize_task_type(task_type)

        if priority is not None:
            task.priority = self._normalize_priority(priority)

        if due_date is not None or due_date is None:
            task.due_date = due_date

        if estimated_duration is not None:
            task.estimated_duration = self._coerce_int(estimated_duration)

        if lesson_id is not None:
            task.lesson_id = lesson_id

        if section_id is not None:
            task.section_id = section_id

        if tags is not None:
            task.tags = self._serialize_tags(tags)

        if is_reminder_enabled is not None:
            task.is_reminder_enabled = bool(is_reminder_enabled)

        if reminder_time is not None:
            task.reminder_time = self._coerce_int(reminder_time)

        db.session.commit()
        self._refresh_pomodoro_statistics(user_id, date.today())
        return task

    def delete_task(self, task_id: str, user_id: str) -> bool:
        """Delete task and refresh statistics."""
        from app.models.task import TaskModel
        from app import db

        task = self.get_task_by_id(task_id, user_id)

        created_date = task.created_at.date() if task.created_at else None
        completed_date = task.completed_at.date() if task.completed_at else None

        db.session.delete(task)
        db.session.commit()

        if created_date:
            self._refresh_pomodoro_statistics(user_id, created_date)
        if completed_date and completed_date != created_date:
            self._refresh_pomodoro_statistics(user_id, completed_date)
        if not created_date and not completed_date:
            self._refresh_pomodoro_statistics(user_id, date.today())
        return True

    # ------------------------------------------------------------------
    # TASK PROGRESS & STATUS
    # ------------------------------------------------------------------
    def change_task_status(self, task_id: str, user_id: str, status: str):
        """Update status while keeping Pomodoro data in sync."""
        from app import db

        task = self.get_task_by_id(task_id, user_id)
        normalized_status = self._normalize_status(status)
        previous_status = task.status
        previous_completed_date = task.completed_at.date() if task.completed_at else None

        task.status = normalized_status
        if normalized_status == "completed":
            task.completed_at = datetime.utcnow()
            task.progress_percentage = 100
        else:
            if previous_status == "completed":
                task.completed_at = None
            if normalized_status == "pending" and task.progress_percentage == 100:
                task.progress_percentage = 0

        db.session.commit()

        new_completed_date = task.completed_at.date() if task.completed_at else None

        if previous_completed_date and previous_completed_date != new_completed_date:
            self._refresh_pomodoro_statistics(user_id, previous_completed_date)
        if new_completed_date:
            self._refresh_pomodoro_statistics(user_id, new_completed_date)
        if not previous_completed_date and not new_completed_date:
            self._refresh_pomodoro_statistics(user_id, date.today())
        return task

    def update_task_progress(self, task_id: str, user_id: str, percentage: int):
        """Set task progress (0-100) and auto-update status when needed."""
        from app import db

        if percentage is None:
            raise ValidationException("Progress percentage is required")

        if not isinstance(percentage, (int, float)):
            raise ValidationException("Progress percentage must be numeric")

        clamped_percentage = max(0, min(int(percentage), 100))

        task = self.get_task_by_id(task_id, user_id)
        previous_completed_date = task.completed_at.date() if task.completed_at else None
        task.progress_percentage = clamped_percentage

        if clamped_percentage >= 100:
            task.status = "completed"
            task.completed_at = datetime.utcnow()
        elif task.status == "completed":
            task.status = "in_progress"
            task.completed_at = None

        db.session.commit()

        new_completed_date = task.completed_at.date() if task.completed_at else None

        if previous_completed_date and previous_completed_date != new_completed_date:
            self._refresh_pomodoro_statistics(user_id, previous_completed_date)
        if new_completed_date:
            self._refresh_pomodoro_statistics(user_id, new_completed_date)
        if not previous_completed_date and not new_completed_date:
            self._refresh_pomodoro_statistics(user_id, date.today())
        return task

    def add_time_spent(self, task_id: str, user_id: str, minutes: int):
        """Increment time spent on a task (in minutes)."""
        from app import db

        if minutes is None:
            raise ValidationException("Minutes value is required")
        if not isinstance(minutes, (int, float)) or minutes < 0:
            raise ValidationException("Minutes must be a non-negative number")

        task = self.get_task_by_id(task_id, user_id)
        task.time_spent = (task.time_spent or 0) + int(minutes)

        db.session.commit()
        return task

    # ------------------------------------------------------------------
    # TASK QUERIES
    # ------------------------------------------------------------------
    def get_overdue_tasks(self, user_id: str, limit: Optional[int] = None):
        """Tasks with due dates in the past and not completed."""
        from app.models.task import TaskModel

        now = datetime.utcnow()
        query = TaskModel.query.filter(
            TaskModel.user_id == user_id,
            TaskModel.due_date.isnot(None),
            TaskModel.due_date < now,
            TaskModel.status != "completed"
        ).order_by(TaskModel.due_date.asc())

        if limit:
            query = query.limit(limit)
        return query.all()

    def get_due_soon_tasks(self, user_id: str, hours: int = 24, limit: Optional[int] = None):
        """Tasks due within the next X hours."""
        from app.models.task import TaskModel

        now = datetime.utcnow()
        window_end = now + timedelta(hours=max(hours, 1))
        query = TaskModel.query.filter(
            TaskModel.user_id == user_id,
            TaskModel.due_date.isnot(None),
            TaskModel.due_date >= now,
            TaskModel.due_date <= window_end,
            TaskModel.status != "completed"
        ).order_by(TaskModel.due_date.asc())

        if limit:
            query = query.limit(limit)
        return query.all()

    def get_high_priority_tasks(self, user_id: str, limit: Optional[int] = None):
        """Return high-priority tasks (optionally limited)."""
        from app.models.task import TaskModel

        query = TaskModel.query.filter(
            TaskModel.user_id == user_id,
            TaskModel.priority == "high",
            TaskModel.status != "completed"
        ).order_by(TaskModel.created_at.desc())

        if limit:
            query = query.limit(limit)
        return query.all()

    def search_tasks(self, user_id: str, query_string: str, limit: Optional[int] = None):
        """Search tasks by title or description substring."""
        from app.models.task import TaskModel

        if not query_string:
            raise ValidationException("Search query is required")

        like_query = f"%{query_string.strip()}%"
        query = TaskModel.query.filter(
            TaskModel.user_id == user_id,
            or_(
                TaskModel.title.ilike(like_query),
                TaskModel.description.ilike(like_query)
            )
        ).order_by(TaskModel.created_at.desc())

        if limit:
            query = query.limit(limit)
        return query.all()

    def get_task_statistics(self, user_id: str) -> Dict[str, Any]:
        """Aggregate task statistics for dashboards."""
        from app.models.task import TaskModel

        total_tasks = TaskModel.query.filter_by(user_id=user_id).count()
        completed_tasks = TaskModel.query.filter(
            TaskModel.user_id == user_id,
            TaskModel.status == "completed"
        ).count()
        in_progress_tasks = TaskModel.query.filter(
            TaskModel.user_id == user_id,
            TaskModel.status == "in_progress"
        ).count()
        pending_tasks = TaskModel.query.filter(
            TaskModel.user_id == user_id,
            TaskModel.status == "pending"
        ).count()

        overdue_tasks = len(self.get_overdue_tasks(user_id))
        high_priority_tasks = TaskModel.query.filter(
            TaskModel.user_id == user_id,
            TaskModel.priority == "high",
            TaskModel.status != "completed"
        ).count()

        today = date.today()
        completed_today = TaskModel.query.filter(
            TaskModel.user_id == user_id,
            TaskModel.status == "completed",
            TaskModel.completed_at.isnot(None),
            func.date(TaskModel.completed_at) == today
        ).count()

        created_today = TaskModel.query.filter(
            TaskModel.user_id == user_id,
            func.date(TaskModel.created_at) == today
        ).count()

        average_progress = 0
        if total_tasks:
            average_progress = round(
                (TaskModel.query.with_entities(func.avg(TaskModel.progress_percentage))
                 .filter(TaskModel.user_id == user_id)
                 .scalar() or 0),
                2
            )

        return {
            'total_tasks': total_tasks,
            'completed_tasks': completed_tasks,
            'in_progress_tasks': in_progress_tasks,
            'pending_tasks': pending_tasks,
            'overdue_tasks': overdue_tasks,
            'high_priority_tasks': high_priority_tasks,
            'tasks_completed_today': completed_today,
            'tasks_created_today': created_today,
            'average_progress_percent': average_progress
        }

    # ------------------------------------------------------------------
    # INTERNAL HELPERS
    # ------------------------------------------------------------------
    def _normalize_status(self, status: Optional[str]) -> str:
        if not status:
            return "pending"
        normalized = status.lower()
        if normalized not in self.VALID_STATUSES:
            raise ValidationException("Invalid task status")
        return normalized

    def _normalize_priority(self, priority: Optional[str]) -> str:
        if not priority:
            return "medium"
        normalized = priority.lower()
        if normalized not in self.VALID_PRIORITIES:
            raise ValidationException("Invalid task priority")
        return normalized

    def _normalize_task_type(self, task_type: Optional[str]) -> str:
        if not task_type:
            return "other"
        normalized = task_type.lower()
        if normalized not in self.VALID_TASK_TYPES:
            return "other"
        return normalized

    def _serialize_tags(self, tags: Optional[Any]) -> Optional[str]:
        if tags is None:
            return None
        if isinstance(tags, str):
            return tags
        try:
            return json.dumps(tags)
        except (TypeError, ValueError):
            raise ValidationException("Tags must be JSON serializable")

    def _coerce_int(self, value: Optional[Any]) -> Optional[int]:
        if value is None:
            return None
        try:
            return int(value)
        except (TypeError, ValueError):
            raise ValidationException("Value must be an integer")

    def _refresh_pomodoro_statistics(self, user_id: str, target_date: Optional[date] = None):
        """Trigger Pomodoro statistics recalculation when task data changes."""
        try:
            session_service = PomodoroSessionService()
            session_service.recalculate_daily_statistics(user_id, target_date)
        except Exception as exc:
            # Avoid breaking the main task flow if statistics update fails
            print(f"[TaskService] Failed to refresh Pomodoro statistics: {exc}")


class PomodoroSessionService:
    """Service layer for Pomodoro session management"""

    def create_session(self, user_id: str, session_type: str, duration: int, task: Optional[str] = None,
                    lesson_id: Optional[str] = None, section_id: Optional[str] = None,
                    mood_before: Optional[str] = None, energy_level: Optional[int] = None,
                    auto_start_next: bool = True, notification_enabled: bool = True,
                    sound_enabled: bool = True, task_id: Optional[str] = None):
        """Create a new Pomodoro session with all optional parameters."""
        from app import db
        try:
            from app.models.pomodoro_session import PomodoroSessionModel

            if not user_id:
                raise ValidationException("User ID is required")

            if session_type not in ['focus', 'short_break', 'long_break']:
                raise ValidationException("Invalid session type")

            if duration <= 0:
                raise ValidationException("Duration must be positive")

            task_title = task.strip() if isinstance(task, str) and task.strip() else None
            resolved_task_id: Optional[str] = None

            if task_id:
                task_service = TaskService()
                try:
                    task_entity = task_service.get_task_by_id(task_id, user_id)
                except NotFoundException as exc:
                    raise ValidationException("Invalid task_id provided") from exc
                resolved_task_id = task_entity.id
                task_title = task_title or task_entity.title

            session = PomodoroSessionModel(
                user_id=user_id,
                session_type=session_type,
                duration=duration,
                start_time=datetime.utcnow(),
                task=task_title,
                task_id=resolved_task_id,
                status='active',
                lesson_id=lesson_id,
                section_id=section_id,
                mood_before=mood_before,
                energy_level=energy_level,
                auto_start_next=auto_start_next,
                notification_enabled=notification_enabled,
                sound_enabled=sound_enabled,
                is_completed=False,
                is_interrupted=False,
                interruption_count=0
            )

            db.session.add(session)
            db.session.commit()

            session_date = session.start_time.date() if session.start_time else date.today()
            self._update_daily_statistics(user_id, session_date)

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
        """Update a session with all possible fields."""
        from app.models.pomodoro_session import PomodoroSessionModel
        from app import db

        session = self.get_session(session_id)
        if not session:
            return None

        # Update timing fields
        if 'actual_duration' in data:
            session.actual_duration = data['actual_duration']
        if 'end_time' in data:
            session.end_time = data['end_time']
        
        # Update status fields
        if 'status' in data:
            session.status = data['status']
            if data['status'] == 'completed':
                session.is_completed = True
                session.is_interrupted = False
            elif data['status'] == 'interrupted':
                session.is_interrupted = True
                session.is_completed = False
            else:
                session.is_completed = False
                session.is_interrupted = False
        
        # Update scoring and feedback
        if 'productivity_score' in data:
            session.productivity_score = data['productivity_score']
        if 'mood_after' in data:
            session.mood_after = data['mood_after']
        if 'focus_score' in data:
            session.focus_score = data['focus_score']
        if 'difficulty_level' in data:
            session.difficulty_level = data['difficulty_level']
        if 'energy_level' in data:
            session.energy_level = data['energy_level']
        if 'notes' in data:
            session.notes = data['notes']

        # Update interruption data
        if 'interruption_count' in data:
            session.interruption_count = data['interruption_count']
        if 'interruption_reasons' in data:
            session.interruption_reasons = data['interruption_reasons']

        # Update settings
        if 'auto_start_next' in data:
            session.auto_start_next = data['auto_start_next']
        if 'notification_enabled' in data:
            session.notification_enabled = data['notification_enabled']
        if 'sound_enabled' in data:
            session.sound_enabled = data['sound_enabled']

        # Update related entities
        if 'lesson_id' in data:
            session.lesson_id = data['lesson_id']
        if 'section_id' in data:
            session.section_id = data['section_id']
        
        task_title_update: Optional[str] = None
        task_service: Optional[TaskService] = None

        if 'task_id' in data:
            incoming_task_id = data['task_id']
            if incoming_task_id:
                task_service = TaskService()
                try:
                    task_entity = task_service.get_task_by_id(incoming_task_id, session.user_id)
                except NotFoundException as exc:
                    raise ValidationException("Invalid task_id provided") from exc
                session.task_id = task_entity.id
                task_title_update = data.get('task') if isinstance(data.get('task'), str) else None
                session.task = (task_title_update or task_entity.title).strip() or task_entity.title
            else:
                session.task_id = None
                task_title_update = data.get('task') if isinstance(data.get('task'), str) else None
                session.task = task_title_update.strip() if task_title_update else None
        elif 'task' in data:
            task_title_update = data['task']
            session.task = task_title_update.strip() if isinstance(task_title_update, str) and task_title_update.strip() else None

        db.session.commit()

        session_date_source = session.end_time or session.start_time or datetime.utcnow()
        self._update_daily_statistics(session.user_id, session_date_source.date())

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
        if status == 'completed':
            session.is_completed = True
            session.is_interrupted = False
        elif status == 'interrupted':
            session.is_interrupted = True
            session.is_completed = False
        else:
            session.is_completed = False
            session.is_interrupted = False
        if session.start_time:
            session.actual_duration = int((session.end_time - session.start_time).total_seconds() / 60)

        db.session.commit()

        session_date_source = session.end_time or session.start_time or datetime.utcnow()
        self._update_daily_statistics(session.user_id, session_date_source.date())
        return session

    def get_active_session(self, user_id: str):
        """Get user's active session if exists"""
        from app.models.pomodoro_session import PomodoroSessionModel
        return PomodoroSessionModel.query.filter_by(
            user_id=user_id,
            status='active'
        ).first()

    def interrupt_session(self, session_id: str):
        """Mark a session as interrupted and increment counter"""
        session = self.get_session(session_id)
        if not session:
            return None

        session.status = 'interrupted'
        session.is_interrupted = True
        session.interruption_count += 1
        
        session.end_time = datetime.utcnow()
        if session.start_time:
            session.actual_duration = int((session.end_time - session.start_time).total_seconds() / 60)

        from app import db
        db.session.commit()

        # Keep interruption statistics in sync
        session_date_source = session.end_time or session.start_time or datetime.utcnow()
        self._update_daily_statistics(session.user_id, session_date_source.date())
        return session

    def delete_session(self, session_id: str) -> bool:
        """Delete a session"""
        from app.models.pomodoro_session import PomodoroSessionModel
        from app import db
        
        session = self.get_session(session_id)
        if not session:
            return False

        session_date_source = (
            session.end_time
            or session.start_time
            or getattr(session, 'created_at', None)
            or datetime.utcnow()
        )

        db.session.delete(session)
        db.session.commit()

        self._update_daily_statistics(session.user_id, session_date_source.date())
        return True

    def recalculate_daily_statistics(self, user_id: str, target_date: Optional[date] = None):
        """Aggregate and persist Pomodoro statistics for the provided date."""
        from app import db
        from app.models.pomodoro_session import PomodoroSessionModel
        from app.models.pomodoro_statistics import PomodoroStatisticsModel
        from app.models.task import TaskModel

        target = target_date or date.today()

        try:
            stats = PomodoroStatisticsModel.query.filter_by(
                user_id=user_id,
                date=target
            ).first()

            if not stats:
                stats = PomodoroStatisticsModel(
                    user_id=user_id,
                    date=target
                )
                db.session.add(stats)

            day_sessions = PomodoroSessionModel.query.filter(
                PomodoroSessionModel.user_id == user_id,
                db.func.date(PomodoroSessionModel.created_at) == target
            ).all()

            total_sessions = len(day_sessions)
            completed_sessions = [s for s in day_sessions if s.is_completed]
            interrupted_sessions = [s for s in day_sessions if s.is_interrupted or s.status == 'interrupted']

            focus_sessions = [s for s in day_sessions if s.session_type == 'focus']
            completed_focus_sessions = [s for s in focus_sessions if s.is_completed]
            short_break_sessions = [s for s in day_sessions if s.session_type == 'short_break']
            long_break_sessions = [s for s in day_sessions if s.session_type == 'long_break']

            def session_minutes(session):
                return int(session.actual_duration or session.duration or 0)

            focus_minutes = sum(session_minutes(s) for s in focus_sessions)
            short_break_minutes = sum(session_minutes(s) for s in short_break_sessions)
            long_break_minutes = sum(session_minutes(s) for s in long_break_sessions)

            total_time_spent = focus_minutes + short_break_minutes + long_break_minutes
            total_productivity_score = sum(
                s.productivity_score or 0 for s in day_sessions if s.productivity_score is not None
            )

            created_task_ids = {
                task_id for (task_id,) in db.session.query(TaskModel.id).filter(
                    TaskModel.user_id == user_id,
                    func.date(TaskModel.created_at) == target
                ).all()
            }

            completed_task_ids = {
                task_id for (task_id,) in db.session.query(TaskModel.id).filter(
                    TaskModel.user_id == user_id,
                    TaskModel.status == 'completed',
                    TaskModel.completed_at.isnot(None),
                    func.date(TaskModel.completed_at) == target
                ).all()
            }

            unique_task_ids = created_task_ids.union(completed_task_ids)

            on_time_sessions = [
                s for s in completed_sessions
                if session_minutes(s) >= int(s.duration or 0)
            ]
            late_sessions = [
                s for s in completed_sessions
                if 0 < int(s.duration or 0) and session_minutes(s) < int(s.duration or 0)
            ]

            stats.total_sessions = total_sessions
            stats.total_completed_sessions = len(completed_sessions)
            stats.total_interrupted_sessions = len(interrupted_sessions)
            stats.total_focus_sessions = len(focus_sessions)
            stats.total_short_break_sessions = len(short_break_sessions)
            stats.total_long_break_sessions = len(long_break_sessions)
            stats.total_focus_time = focus_minutes
            stats.total_break_time = short_break_minutes
            stats.total_long_break_time = long_break_minutes
            stats.total_time_spent = total_time_spent
            stats.total_effective_time = focus_minutes
            stats.total_ineffective_time = max(total_time_spent - focus_minutes, 0)
            stats.total_productivity_score = total_productivity_score
            stats.total_tasks = len(unique_task_ids)
            stats.total_tasks_completed = len(completed_task_ids)
            stats.total_abandoned_sessions = len(interrupted_sessions)
            stats.total_on_time_sessions = len(on_time_sessions)
            stats.total_late_sessions = len(late_sessions)
            stats.average_session_duration = (
                round(total_time_spent / total_sessions, 2) if total_sessions else 0.0
            )
            stats.productivity_score = (
                round(total_productivity_score / len(completed_sessions), 2)
                if completed_sessions else 0.0
            )

            db.session.commit()
            return stats
        except Exception as exc:
            db.session.rollback()
            print(f"[PomodoroSessionService] Error recalculating statistics: {exc}")
            raise

    def _update_daily_statistics(self, user_id: str, target_date: Optional[date] = None) -> None:
        """Aggregate and persist Pomodoro statistics for the provided date."""
        try:
            self.recalculate_daily_statistics(user_id, target_date)
        except Exception as exc:
            print(f"[PomodoroSessionService] Error updating daily statistics: {exc}")
# --- Class ที่เพิ่มเข้ามา ---
class PomodoroService:
    """Service for Pomodoro tracking logic."""

    DEFAULT_DAILY_TARGET = 4  # Default target sessions per day

    def __init__(self):
        self._session_service = PomodoroSessionService()

    def get_pomodoros_count_today(self, user_id: str) -> int:
        """Count focus sessions completed today."""
        return self.get_daily_progress(user_id).get('completed_sessions', 0)

    def get_study_time_today(self, user_id: str, duration_per_session: int = 25) -> int:
        """Estimate study time based on completed sessions today."""
        return self.get_pomodoros_count_today(user_id) * duration_per_session

    def get_total_pomodoros_count(self, user_id: str) -> int:
        """Count total focus sessions for user."""
        from app.models.pomodoro_session import PomodoroSessionModel

        return PomodoroSessionModel.query.filter(
            PomodoroSessionModel.user_id == user_id,
            PomodoroSessionModel.session_type == 'focus'
        ).count()

    def get_stats(self, user_id: str) -> Dict[str, Any]:
        """Return aggregate statistics for dashboard widgets."""
        from app import db
        from app.models.pomodoro_session import PomodoroSessionModel
        from app.models.pomodoro_statistics import PomodoroStatisticsModel
        from app.models.task import TaskModel

        total_sessions = PomodoroSessionModel.query.filter_by(user_id=user_id).count()

        completed_focus_sessions = PomodoroSessionModel.query.filter(
            PomodoroSessionModel.user_id == user_id,
            PomodoroSessionModel.session_type == 'focus',
            PomodoroSessionModel.is_completed.is_(True)
        ).count()

        focus_sessions_total = PomodoroSessionModel.query.filter(
            PomodoroSessionModel.user_id == user_id,
            PomodoroSessionModel.session_type == 'focus'
        ).count()

        interrupted_sessions = PomodoroSessionModel.query.filter(
            PomodoroSessionModel.user_id == user_id,
            PomodoroSessionModel.is_interrupted.is_(True)
        ).count()

        focus_minutes = db.session.query(
            func.coalesce(
                func.sum(
                    func.coalesce(
                        PomodoroSessionModel.actual_duration,
                        PomodoroSessionModel.duration,
                        0
                    )
                ),
                0
            )
        ).filter(
            PomodoroSessionModel.user_id == user_id,
            PomodoroSessionModel.session_type == 'focus'
        ).scalar() or 0

        total_minutes = db.session.query(
            func.coalesce(
                func.sum(
                    func.coalesce(
                        PomodoroSessionModel.actual_duration,
                        PomodoroSessionModel.duration,
                        0
                    )
                ),
                0
            )
        ).filter(
            PomodoroSessionModel.user_id == user_id
        ).scalar() or 0

        total_break_sessions = PomodoroSessionModel.query.filter(
            PomodoroSessionModel.user_id == user_id,
            PomodoroSessionModel.session_type.in_(['short_break', 'long_break'])
        ).count()

        last_session = PomodoroSessionModel.query.filter_by(user_id=user_id).order_by(
            PomodoroSessionModel.created_at.desc()
        ).first()

        active_days = db.session.query(
            func.count(func.distinct(func.date(PomodoroSessionModel.created_at)))
        ).filter(
            PomodoroSessionModel.user_id == user_id
        ).scalar() or 0

        total_tasks_logged_db = TaskModel.query.filter_by(user_id=user_id).count()
        tasks_completed_overall = TaskModel.query.filter(
            TaskModel.user_id == user_id,
            TaskModel.status == 'completed'
        ).count()

        all_stats = PomodoroStatisticsModel.query.filter_by(user_id=user_id).all()
        latest_stats = None
        if all_stats:
            latest_stats = max(all_stats, key=lambda row: row.date)

        total_sessions_aggregated = sum(row.total_sessions for row in all_stats) if all_stats else 0
        completed_sessions_aggregated = sum(row.total_completed_sessions for row in all_stats) if all_stats else 0
        interrupted_sessions_aggregated = sum(row.total_interrupted_sessions for row in all_stats) if all_stats else 0
        abandoned_sessions = sum(row.total_abandoned_sessions for row in all_stats) if all_stats else 0
        on_time_sessions = sum(row.total_on_time_sessions for row in all_stats) if all_stats else 0
        late_sessions = sum(row.total_late_sessions for row in all_stats) if all_stats else 0
        tasks_logged_daily_sum = sum(row.total_tasks for row in all_stats) if all_stats else 0
        tasks_completed_daily_sum = sum(row.total_tasks_completed for row in all_stats) if all_stats else 0
        total_effective_minutes = sum(row.total_effective_time for row in all_stats) if all_stats else 0
        total_ineffective_minutes = sum(row.total_ineffective_time for row in all_stats) if all_stats else 0

        average_productivity_score = round(
            sum(row.productivity_score for row in all_stats) / len(all_stats), 2
        ) if all_stats else 0.0
        average_session_duration = round(
            sum(row.average_session_duration for row in all_stats) / len(all_stats), 2
        ) if all_stats else 0.0

        focus_completion_rate = round(
            (completed_focus_sessions / focus_sessions_total) * 100, 2
        ) if focus_sessions_total else 0.0
        task_completion_rate = round(
            (tasks_completed_overall / total_tasks_logged_db) * 100, 2
        ) if total_tasks_logged_db else 0.0
        overall_completion_rate = round(
            (completed_sessions_aggregated / total_sessions_aggregated) * 100, 2
        ) if total_sessions_aggregated else 0.0

        streak = self._calculate_streak(user_id)

        return {
            'total_sessions': total_sessions,
            'total_pomodoros': completed_focus_sessions,
            'total_focus_minutes': focus_minutes,
            'total_break_minutes': max(total_minutes - focus_minutes, 0),
            'total_tasks_completed': tasks_completed_overall,
            'total_break_sessions': total_break_sessions,
            'interrupted_sessions': interrupted_sessions,
            'active_days': active_days,
            'streak': streak,
            'last_session_at': last_session.created_at.isoformat() if last_session else None,
            'productivity_score': latest_stats.productivity_score if latest_stats else 0.0,
            'total_completed_sessions_overall': completed_sessions_aggregated,
            'total_interrupted_sessions_overall': interrupted_sessions_aggregated,
            'total_sessions_aggregated': total_sessions_aggregated,
            'abandoned_sessions': abandoned_sessions,
            'on_time_sessions': on_time_sessions,
            'late_sessions': late_sessions,
            'total_tasks_logged': total_tasks_logged_db,
            'total_tasks_logged_daily_sum': tasks_logged_daily_sum,
            'total_tasks_completed_daily_sum': tasks_completed_daily_sum,
            'total_tasks_completed_overall': tasks_completed_overall,
            'total_effective_minutes': total_effective_minutes,
            'total_ineffective_minutes': total_ineffective_minutes,
            'average_productivity_score': average_productivity_score,
            'average_session_duration': average_session_duration,
            'focus_completion_rate': focus_completion_rate,
            'task_completion_rate': task_completion_rate,
            'overall_completion_rate': overall_completion_rate,
            'latest_daily_statistics': latest_stats.to_dict() if latest_stats else None
        }

    def get_daily_progress(self, user_id: str, target_date: Optional[date] = None) -> Dict[str, Any]:
        """Return today's progress metrics."""
        target = target_date or date.today()
        stats_record = self._ensure_statistics(user_id, target)

        tasks_completed = stats_record.total_tasks_completed
        total_tasks = stats_record.total_tasks
        break_sessions = stats_record.total_short_break_sessions + stats_record.total_long_break_sessions

        target_sessions = self.DEFAULT_DAILY_TARGET
        goal_percent = (
            min((stats_record.total_completed_sessions / target_sessions) * 100, 100.0)
            if target_sessions else 0.0
        )

        completion_rate = round(
            (stats_record.total_completed_sessions / stats_record.total_sessions) * 100, 2
        ) if stats_record.total_sessions else 0.0
        focus_effectiveness = round(
            (stats_record.total_effective_time / stats_record.total_time_spent) * 100, 2
        ) if stats_record.total_time_spent else 0.0
        task_completion_rate = round(
            (tasks_completed / total_tasks) * 100, 2
        ) if total_tasks else 0.0

        return {
            'date': target.isoformat(),
            'completed_sessions': stats_record.total_completed_sessions,
            'focus_minutes': stats_record.total_focus_time,
            'break_minutes': stats_record.total_break_time + stats_record.total_long_break_time,
            'interrupted_sessions': stats_record.total_interrupted_sessions,
            'tasks_completed': tasks_completed,
            'tasks_logged': total_tasks,
            'break_sessions': break_sessions,
            'target_sessions': target_sessions,
            'goal_completion_percent': round(goal_percent, 2),
            'completion_rate': completion_rate,
            'focus_effectiveness_percent': focus_effectiveness,
            'task_completion_rate': task_completion_rate,
            'on_time_sessions': stats_record.total_on_time_sessions,
            'late_sessions': stats_record.total_late_sessions,
            'abandoned_sessions': stats_record.total_abandoned_sessions
        }

    def generate_productivity_report(
        self,
        user_id: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate productivity report for a date range."""
        from app.models.pomodoro_statistics import PomodoroStatisticsModel

        end = datetime.strptime(end_date, '%Y-%m-%d').date() if end_date else date.today()
        start = datetime.strptime(start_date, '%Y-%m-%d').date() if start_date else end - timedelta(days=6)

        if start > end:
            raise ValidationException("Start date must be before or equal to end date")

        stats_rows = PomodoroStatisticsModel.query.filter(
            PomodoroStatisticsModel.user_id == user_id,
            PomodoroStatisticsModel.date >= start,
            PomodoroStatisticsModel.date <= end
        ).order_by(PomodoroStatisticsModel.date.asc()).all()

        totals = {
            'total_sessions': sum(row.total_sessions for row in stats_rows),
            'total_completed_sessions': sum(row.total_completed_sessions for row in stats_rows),
            'total_interrupted_sessions': sum(row.total_interrupted_sessions for row in stats_rows),
            'total_focus_time': sum(row.total_focus_time for row in stats_rows),
            'total_break_time': sum(row.total_break_time + row.total_long_break_time for row in stats_rows),
            'total_abandoned_sessions': sum(row.total_abandoned_sessions for row in stats_rows),
            'total_on_time_sessions': sum(row.total_on_time_sessions for row in stats_rows),
            'total_late_sessions': sum(row.total_late_sessions for row in stats_rows),
            'total_tasks_logged': sum(row.total_tasks for row in stats_rows),
            'total_tasks_completed': sum(row.total_tasks_completed for row in stats_rows),
            'average_productivity_score': round(
                sum(row.productivity_score for row in stats_rows) / len(stats_rows), 2
            ) if stats_rows else 0.0,
            'average_session_duration': round(
                sum(row.average_session_duration for row in stats_rows) / len(stats_rows), 2
            ) if stats_rows else 0.0,
            'average_focus_effectiveness_percent': round(
                sum(
                    (row.total_effective_time / row.total_time_spent) * 100
                    if row.total_time_spent else 0
                    for row in stats_rows
                ) / len(stats_rows),
                2
            ) if stats_rows else 0.0
        }

        return {
            'start_date': start.isoformat(),
            'end_date': end.isoformat(),
            'daily': [row.to_dict() for row in stats_rows],
            'totals': totals
        }

    def get_session_history(self, user_id: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Return latest Pomodoro sessions."""
        from app.models.pomodoro_session import PomodoroSessionModel

        sessions = PomodoroSessionModel.query.filter_by(user_id=user_id).order_by(
            PomodoroSessionModel.created_at.desc()
        ).limit(limit).all()

        return [session.to_dict() for session in sessions]

    def export_user_data(self, user_id: str) -> Dict[str, Any]:
        """Export full Pomodoro dataset for the user."""
        from app.models.pomodoro_session import PomodoroSessionModel
        from app.models.pomodoro_statistics import PomodoroStatisticsModel

        sessions = PomodoroSessionModel.query.filter_by(user_id=user_id).order_by(
            PomodoroSessionModel.created_at.asc()
        ).all()

        statistics = PomodoroStatisticsModel.query.filter_by(user_id=user_id).order_by(
            PomodoroStatisticsModel.date.asc()
        ).all()

        return {
            'summary': self.get_stats(user_id),
            'sessions': [session.to_dict() for session in sessions],
            'statistics': [stat.to_dict() for stat in statistics]
        }

    def update_daily_statistics(self, user_id: str, target_date: Optional[str] = None) -> Dict[str, Any]:
        """Recalculate daily statistics for provided date (defaults to today)."""
        parsed_date: Optional[date] = None
        if target_date:
            try:
                parsed_date = datetime.strptime(target_date, '%Y-%m-%d').date()
            except ValueError as exc:
                raise ValidationException("Invalid date format. Expected YYYY-MM-DD") from exc

        stats = self._session_service.recalculate_daily_statistics(user_id, parsed_date)
        return stats.to_dict() if stats else {}

    def _calculate_streak(self, user_id: str) -> int:
        """Calculate consecutive days with completed sessions."""
        from app.models.pomodoro_statistics import PomodoroStatisticsModel

        streak = 0
        cursor = date.today()

        while True:
            stats = PomodoroStatisticsModel.query.filter_by(user_id=user_id, date=cursor).first()
            if stats and stats.total_completed_sessions > 0:
                streak += 1
                cursor -= timedelta(days=1)
            else:
                break

        return streak

    def _ensure_statistics(self, user_id: str, target: date):
        """Ensure statistics record exists for given date."""
        from app.models.pomodoro_statistics import PomodoroStatisticsModel

        stats = PomodoroStatisticsModel.query.filter_by(user_id=user_id, date=target).first()
        if not stats:
            stats = self._session_service.recalculate_daily_statistics(user_id, target)
        return stats

    def _get_sessions_for_date(self, user_id: str, target: date):
        """Return list of sessions for given date."""
        from app import db
        from app.models.pomodoro_session import PomodoroSessionModel

        return PomodoroSessionModel.query.filter(
            PomodoroSessionModel.user_id == user_id,
            db.func.date(PomodoroSessionModel.created_at) == target
        ).all()
    
