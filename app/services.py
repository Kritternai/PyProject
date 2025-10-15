"""
Simple service classes for MVC architecture.
Contains business logic for the application.
"""

# app/services.py

import json
from typing import List, Optional, Dict, Any
from datetime import datetime
from app.db_instance import db as database
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
        from app.database_utils import get_db
        from werkzeug.security import generate_password_hash
        
        db = get_db()
        
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
        
        database.session.add(user)
        database.session.commit()
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


class LessonService:
    """Simple lesson service for business logic."""
    
    def create_lesson(self, user_id: str, title: str, description: str = None):
        """Create a new lesson."""
        from app.models.lesson import LessonModel
        
        lesson = LessonModel(
            user_id=user_id,
            title=title,
            description=description
        )
        
        database.session.add(lesson)
        database.session.commit()
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
        
        today = datetime.now().date()
        
        count = LessonModel.query.filter(
            LessonModel.user_id == user_id,
            LessonModel.status == 'completed',
            database.func.date(LessonModel.updated_at) == today
        ).count()
        
        return count
    # --- จบโค้ดที่เพิ่ม ---


class NoteService:
    """Simple note service for business logic."""
    
    def create_note(self, user_id: str, title: str, content: str, lesson_id: str = None, **kwargs):
        """Create a new note (standalone or linked to lesson)."""
        from app.models.note import NoteModel
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
        
        database.session.add(note)
        database.session.commit()
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
        
        database.session.commit()
        return note
    
    def get_user_notes(self, user_id: str):
        """Get all notes for a user (alias for get_notes_by_user)."""
        return self.get_notes_by_user(user_id)
    
    def delete_note(self, note_id: str, user_id: str = None):
        """Delete a note."""
        from app.models.note import NoteModel
        
        # Build query
        if user_id:
            note = NoteModel.query.filter_by(id=note_id, user_id=user_id).first()
        else:
            note = NoteModel.query.filter_by(id=note_id).first()
        
        if not note:
            return False
        
        database.session.delete(note)
        database.session.commit()
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
        
        task = TaskModel(
            user_id=user_id,
            title=title,
            description=description
        )
        
        database.session.add(task)
        database.session.commit()
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

    def create_session(self, user_id: str, session_type: str, duration: int, task: Optional[str] = None, 
                    lesson_id: Optional[str] = None, section_id: Optional[str] = None,
                    mood_before: Optional[str] = None, energy_level: Optional[int] = None,
                    auto_start_next: bool = True, notification_enabled: bool = True,
                    sound_enabled: bool = True):
        """Create a new Pomodoro session with all optional parameters"""
        from app.db_instance import db as database
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

            database.session.add(session)
            database.session.commit()
            
            return session
        except Exception as e:
            database.session.rollback()
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
        """Update a session with all possible fields"""
        from app.models.pomodoro_session import PomodoroSessionModel
        from app.models.task import TaskModel
        from app.db_instance import db as database
        
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
            elif data['status'] == 'interrupted':
                session.is_interrupted = True
        
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
                    database.session.add(task_obj)
                    database.session.flush()  # Flush to get the task ID
                
                session.task_id = task_obj.id
                session.task = task_name
            else:
                session.task_id = None
                session.task = None

        database.session.commit()
        return session

    def end_session(self, session_id: str, status: str = 'completed'):
        """End a Pomodoro session"""
        from app.models.pomodoro_session import PomodoroSessionModel
        from app.db_instance import db as database
        
        session = self.get_session(session_id)
        if not session:
            return None

        session.end_time = datetime.utcnow()
        session.status = status
        if session.start_time:
            session.actual_duration = int((session.end_time - session.start_time).total_seconds() / 60)
        
        # Mark as completed if status is completed
        if status == 'completed':
            session.is_completed = True
        elif status == 'interrupted':
            session.is_interrupted = True

        database.session.commit()
        
        # Update statistics after ending session using comprehensive service
        self._update_daily_statistics(session.user_id)
        
        # Also update using the wrapper service for additional functionality
        try:
            stats_wrapper = PomodoroStatisticsServiceWrapper()
            session_data = {
                'user_id': session.user_id,
                'created_at': session.created_at,
                'session_type': session.session_type,
                'status': session.status,
                'is_completed': session.is_completed,
                'is_interrupted': session.is_interrupted,
                'actual_duration': session.actual_duration
            }
            stats_wrapper.create_or_update_statistics_from_session(session_data)
        except Exception as e:
            print(f"⚠️ Error with statistics wrapper: {str(e)}")
        
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

        from app.db_instance import db as database
        database.session.commit()
        return session

    def _update_daily_statistics(self, user_id: str):
        """Update daily statistics after session completion using PomodoroStatisticsService"""
        try:
            from app.services.pomodoro_statistics_service import PomodoroStatisticsService
            from datetime import date
            
            # Use the dedicated statistics service for proper calculation
            stats_service = PomodoroStatisticsService()
            today = date.today()
            
            # Update or create daily statistics with full calculation
            updated_stats = stats_service.update_or_create_daily_statistics(user_id, today)
            
            print(f"✅ Daily statistics updated for user {user_id}")
            print(f"   - Total sessions: {updated_stats.get('total_sessions', 0)}")
            print(f"   - Completed sessions: {updated_stats.get('total_completed_sessions', 0)}")
            print(f"   - Focus time: {updated_stats.get('total_focus_time', 0)} minutes")
            print(f"   - Productivity score: {updated_stats.get('productivity_score', 0):.1f}")
            
            return updated_stats
            
        except Exception as e:
            print(f"⚠️ Error updating daily statistics: {str(e)}")
            # Don't rollback here as the session was already committed
            return None

    def delete_session(self, session_id: str) -> bool:
        """Delete a session"""
        from app.models.pomodoro_session import PomodoroSessionModel
        from app.db_instance import db as database
        
        session = self.get_session(session_id)
        if not session:
            return False

        user_id = session.user_id
        session_date = session.created_at.date() if session.created_at else None
        
        database.session.delete(session)
        database.session.commit()
        
        # Recalculate statistics for the day after deletion
        if session_date:
            try:
                stats_wrapper = PomodoroStatisticsServiceWrapper()
                stats_wrapper.update_daily_statistics(user_id, session_date)
                print(f"✅ Statistics recalculated after session deletion")
            except Exception as e:
                print(f"⚠️ Error recalculating statistics after deletion: {str(e)}")
        
        return True
    
    def get_session_statistics(self, user_id: str, session_id: str = None):
        """Get statistics for a specific session or user sessions"""
        if session_id:
            session = self.get_session(session_id)
            if not session:
                return None
            
            return {
                'session_id': session.id,
                'duration': session.duration,
                'actual_duration': session.actual_duration,
                'productivity_score': session.productivity_score,
                'focus_score': session.focus_score,
                'interruption_count': session.interruption_count,
                'is_completed': session.is_completed,
                'is_interrupted': session.is_interrupted,
                'efficiency_ratio': (session.actual_duration / session.duration * 100) if session.duration and session.actual_duration else 0
            }
        else:
            # Get overall user statistics using wrapper
            try:
                stats_wrapper = PomodoroStatisticsServiceWrapper()
                return stats_wrapper.get_user_dashboard_stats(user_id)
            except Exception as e:
                print(f"⚠️ Error getting user statistics: {str(e)}")
                return None
    
    def bulk_update_statistics(self, user_id: str, start_date=None, end_date=None):
        """Recalculate statistics for a date range"""
        try:
            from datetime import date, timedelta
            from app.models.pomodoro_session import PomodoroSessionModel
            from app.db_instance import db as database
            
            if not start_date:
                # Get first session date
                first_session = PomodoroSessionModel.query.filter_by(user_id=user_id).order_by(PomodoroSessionModel.created_at.asc()).first()
                start_date = first_session.created_at.date() if first_session else date.today()
            
            if not end_date:
                end_date = date.today()
            
            # Convert string dates if needed
            if isinstance(start_date, str):
                start_date = date.fromisoformat(start_date)
            if isinstance(end_date, str):
                end_date = date.fromisoformat(end_date)
            
            stats_wrapper = PomodoroStatisticsServiceWrapper()
            updated_dates = []
            
            current_date = start_date
            while current_date <= end_date:
                # Check if there are sessions for this date
                sessions_exist = PomodoroSessionModel.query.filter(
                    PomodoroSessionModel.user_id == user_id,
                    database.func.date(PomodoroSessionModel.created_at) == current_date
                ).first()
                
                if sessions_exist:
                    stats_wrapper.update_daily_statistics(user_id, current_date)
                    updated_dates.append(current_date.isoformat())
                
                current_date += timedelta(days=1)
            
            return {
                'success': True,
                'message': f'Updated statistics for {len(updated_dates)} dates',
                'updated_dates': updated_dates
            }
            
        except Exception as e:
            print(f"⚠️ Error in bulk statistics update: {str(e)}")
            return {
                'success': False,
                'message': str(e),
                'updated_dates': []
            }
# --- Class ที่เพิ่มเข้ามา ---
class PomodoroService:
    """Service for Pomodoro tracking logic."""
    
    def get_pomodoros_count_today(self, user_id: str):
        """นับ pomodoro ที่ทำวันนี้"""
        from datetime import date
        from app.models.pomodoro_session import PomodoroSessionModel
        from app.db_instance import db as database

        today = date.today()
        
        count = PomodoroSessionModel.query.filter(
            PomodoroSessionModel.user_id == user_id,
            database.func.date(PomodoroSessionModel.created_at) == today
        ).count()
        
        return count
    
    def get_study_time_today(self, user_id: str, duration_per_session: int = 25):
        """คำนวณเวลาเรียนวันนี้ (นาที)"""
        count = self.get_pomodoros_count_today(user_id)
        return count * duration_per_session

    def get_total_pomodoros_count(self, user_id: str):
        """นับ pomodoros ทั้งหมด"""
        from app.models.pomodoro_session import PomodoroSessionModel
        return PomodoroSessionModel.query.filter_by(user_id=user_id).count()


class PomodoroStatisticsServiceWrapper:
    """Wrapper service for Pomodoro Statistics to integrate with main services.py"""
    
    def __init__(self):
        """Initialize with the full statistics service"""
        from app.services.pomodoro_statistics_service import PomodoroStatisticsService
        self._stats_service = PomodoroStatisticsService()
    
    def get_daily_statistics(self, user_id: str, target_date=None):
        """Get daily statistics for a user"""
        from datetime import date
        if target_date is None:
            target_date = date.today()
        elif isinstance(target_date, str):
            target_date = date.fromisoformat(target_date)
        
        return self._stats_service.get_daily_statistics(user_id, target_date)
    
    def update_daily_statistics(self, user_id: str, target_date=None):
        """Update or create daily statistics"""
        from datetime import date
        if target_date is None:
            target_date = date.today()
        elif isinstance(target_date, str):
            target_date = date.fromisoformat(target_date)
        
        return self._stats_service.update_or_create_daily_statistics(user_id, target_date)
    
    def get_weekly_statistics(self, user_id: str, start_date=None):
        """Get weekly statistics"""
        return self._stats_service.get_weekly_statistics(user_id, start_date)
    
    def get_monthly_statistics(self, user_id: str, year=None, month=None):
        """Get monthly statistics"""
        return self._stats_service.get_monthly_statistics(user_id, year, month)
    
    def get_productivity_trends(self, user_id: str, days: int = 7):
        """Get productivity trends"""
        return self._stats_service.get_productivity_trends(user_id, days)
    
    def get_statistics_summary(self, user_id: str):
        """Get comprehensive statistics summary"""
        return self._stats_service.get_statistics_summary(user_id)
    
    def recalculate_all_statistics(self, user_id: str):
        """Recalculate all statistics for a user"""
        return self._stats_service.recalculate_all_statistics(user_id)
    
    def calculate_daily_statistics(self, user_id: str, target_date=None):
        """Calculate statistics from session data"""
        from datetime import date
        if target_date is None:
            target_date = date.today()
        elif isinstance(target_date, str):
            target_date = date.fromisoformat(target_date)
        
        return self._stats_service.calculate_daily_statistics(user_id, target_date)
    
    def get_user_dashboard_stats(self, user_id: str):
        """Get dashboard statistics for UI display"""
        try:
            summary = self.get_statistics_summary(user_id)
            trends = self.get_productivity_trends(user_id, 7)
            
            # Format for dashboard
            dashboard_stats = {
                'today': {
                    'sessions_completed': summary.get('today', {}).get('total_completed_sessions', 0),
                    'focus_time': summary.get('today', {}).get('total_focus_time', 0),
                    'productivity_score': summary.get('today', {}).get('productivity_score', 0),
                    'interruptions': summary.get('today', {}).get('total_interrupted_sessions', 0),
                },
                'week': {
                    'total_focus_time': summary.get('this_week', {}).get('total_focus_time', 0),
                    'total_sessions': summary.get('this_week', {}).get('total_sessions', 0),
                    'average_productivity': summary.get('this_week', {}).get('average_productivity', 0),
                },
                'trends': {
                    'trend_direction': trends.get('trend', 'neutral'),
                    'completion_rate': trends.get('completion_rate', 0),
                    'data_points': trends.get('data_points', [])[:7]  # Last 7 days
                },
                'last_updated': summary.get('last_updated')
            }
            
            return dashboard_stats
            
        except Exception as e:
            print(f"⚠️ Error getting dashboard stats: {str(e)}")
            return {
                'today': {'sessions_completed': 0, 'focus_time': 0, 'productivity_score': 0, 'interruptions': 0},
                'week': {'total_focus_time': 0, 'total_sessions': 0, 'average_productivity': 0},
                'trends': {'trend_direction': 'neutral', 'completion_rate': 0, 'data_points': []},
                'last_updated': None
            }
    
    def create_or_update_statistics_from_session(self, session_data: dict):
        """Update statistics when a session is completed/interrupted"""
        try:
            if not session_data.get('user_id'):
                return None
            
            from datetime import date, datetime
            
            # Get the date from session
            if session_data.get('created_at'):
                if isinstance(session_data['created_at'], str):
                    session_date = datetime.fromisoformat(session_data['created_at'].replace('Z', '+00:00')).date()
                else:
                    session_date = session_data['created_at'].date()
            else:
                session_date = date.today()
            
            # Update statistics for that date
            updated_stats = self.update_daily_statistics(session_data['user_id'], session_date)
            
            print(f"✅ Statistics updated for session on {session_date}")
            return updated_stats
            
        except Exception as e:
            print(f"⚠️ Error updating statistics from session: {str(e)}")
            return None

    def _update_daily_statistics(self, user_id: str):
        """Update daily statistics after session completion using PomodoroStatisticsService"""
        try:
            from app.services.pomodoro_statistics_service import PomodoroStatisticsService
            from datetime import date
            
            # Use the dedicated statistics service for proper calculation
            stats_service = PomodoroStatisticsService()
            today = date.today()
            
            # Update or create daily statistics with full calculation
            updated_stats = stats_service.update_or_create_daily_statistics(user_id, today)
            
            print(f"✅ Daily statistics updated for user {user_id}")
            print(f"   - Total sessions: {updated_stats.get('total_sessions', 0)}")
            print(f"   - Completed sessions: {updated_stats.get('total_completed_sessions', 0)}")
            print(f"   - Focus time: {updated_stats.get('total_focus_time', 0)} minutes")
            print(f"   - Productivity score: {updated_stats.get('productivity_score', 0):.1f}")
            
            return updated_stats
            
        except Exception as e:
            print(f"⚠️ Error updating daily statistics: {str(e)}")
            # Don't rollback here as the session was already committed
            return None


# End of services.py
