"""
Lesson domain entity following Domain-Driven Design principles.
Pure business object with no external dependencies.
"""

import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum
from ..interfaces.entity import Entity


class LessonStatus(Enum):
    """Lesson status enumeration."""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class DifficultyLevel(Enum):
    """Difficulty level enumeration."""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


class SourcePlatform(Enum):
    """Source platform enumeration."""
    MANUAL = "manual"
    GOOGLE_CLASSROOM = "google_classroom"
    MS_TEAMS = "ms_teams"
    CANVAS = "canvas"


class Lesson(Entity):
    """
    Lesson domain entity representing a lesson in the system.
    Contains business logic and validation rules.
    """
    
    def __init__(
        self,
        user_id: str,
        title: str,
        description: Optional[str] = None,
        status: LessonStatus = LessonStatus.NOT_STARTED,
        difficulty_level: DifficultyLevel = DifficultyLevel.BEGINNER,
        estimated_duration: Optional[int] = None,
        color_theme: int = 1,
        is_favorite: bool = False,
        source_platform: SourcePlatform = SourcePlatform.MANUAL,
        external_id: Optional[str] = None,
        external_url: Optional[str] = None,
        author_name: Optional[str] = None,
        subject: Optional[str] = None,
        grade_level: Optional[str] = None,
        lesson_id: Optional[str] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None
    ):
        """
        Initialize lesson entity.
        
        Args:
            user_id: ID of the user who owns this lesson
            title: Lesson title
            description: Lesson description
            status: Lesson status
            difficulty_level: Difficulty level
            estimated_duration: Estimated duration in minutes
            color_theme: Color theme (1-6)
            is_favorite: Whether lesson is marked as favorite
            source_platform: Source platform
            external_id: External platform ID
            external_url: External platform URL
            author_name: Author name
            subject: Subject
            grade_level: Grade level
            lesson_id: Lesson ID (auto-generated if not provided)
            created_at: Creation timestamp
            updated_at: Last update timestamp
        """
        self._id = lesson_id or str(uuid.uuid4())
        self._user_id = user_id
        self._title = title
        self._description = description
        self._status = status
        self._difficulty_level = difficulty_level
        self._estimated_duration = estimated_duration
        self._color_theme = color_theme
        self._is_favorite = is_favorite
        self._source_platform = source_platform
        self._external_id = external_id
        self._external_url = external_url
        self._author_name = author_name
        self._subject = subject
        self._grade_level = grade_level
        
        # Statistics
        self._progress_percentage = 0
        self._total_sections = 0
        self._completed_sections = 0
        self._total_time_spent = 0
        
        # Timestamps
        self._created_at = created_at or datetime.utcnow()
        self._updated_at = updated_at or datetime.utcnow()
        
        # Validate business rules
        self._validate()
    
    def _validate(self) -> None:
        """Validate lesson business rules."""
        if not self._user_id or len(self._user_id.strip()) == 0:
            raise ValueError("User ID cannot be empty")
        
        if not self._title or len(self._title.strip()) == 0:
            raise ValueError("Title cannot be empty")
        
        if len(self._title) > 200:
            raise ValueError("Title must be no more than 200 characters long")
        
        if self._description and len(self._description) > 5000:
            raise ValueError("Description must be no more than 5000 characters long")
        
        if self._color_theme < 1 or self._color_theme > 6:
            raise ValueError("Color theme must be between 1 and 6")
        
        if self._estimated_duration is not None and self._estimated_duration < 0:
            raise ValueError("Estimated duration cannot be negative")
        
        if self._progress_percentage < 0 or self._progress_percentage > 100:
            raise ValueError("Progress percentage must be between 0 and 100")
    
    # Properties
    @property
    def id(self) -> str:
        return self._id
    
    @property
    def user_id(self) -> str:
        return self._user_id
    
    @property
    def title(self) -> str:
        return self._title
    
    @property
    def description(self) -> Optional[str]:
        return self._description
    
    @property
    def status(self) -> LessonStatus:
        return self._status
    
    @property
    def difficulty_level(self) -> DifficultyLevel:
        return self._difficulty_level
    
    @property
    def estimated_duration(self) -> Optional[int]:
        return self._estimated_duration
    
    @property
    def color_theme(self) -> int:
        return self._color_theme
    
    @property
    def is_favorite(self) -> bool:
        return self._is_favorite
    
    @property
    def source_platform(self) -> SourcePlatform:
        return self._source_platform
    
    @property
    def external_id(self) -> Optional[str]:
        return self._external_id
    
    @property
    def external_url(self) -> Optional[str]:
        return self._external_url
    
    @property
    def author_name(self) -> Optional[str]:
        return self._author_name
    
    @property
    def subject(self) -> Optional[str]:
        return self._subject
    
    @property
    def grade_level(self) -> Optional[str]:
        return self._grade_level
    
    @property
    def progress_percentage(self) -> int:
        return self._progress_percentage
    
    @property
    def total_sections(self) -> int:
        return self._total_sections
    
    @property
    def completed_sections(self) -> int:
        return self._completed_sections
    
    @property
    def total_time_spent(self) -> int:
        return self._total_time_spent
    
    @property
    def created_at(self) -> datetime:
        return self._created_at
    
    @property
    def updated_at(self) -> datetime:
        return self._updated_at
    
    # Business methods
    def update_title(self, title: str) -> None:
        """
        Update lesson title.
        
        Args:
            title: New title
            
        Raises:
            ValueError: If title is invalid
        """
        if not title or len(title.strip()) == 0:
            raise ValueError("Title cannot be empty")
        
        if len(title) > 200:
            raise ValueError("Title must be no more than 200 characters long")
        
        self._title = title
        self._updated_at = datetime.utcnow()
    
    def update_description(self, description: Optional[str]) -> None:
        """
        Update lesson description.
        
        Args:
            description: New description
        """
        if description and len(description) > 5000:
            raise ValueError("Description must be no more than 5000 characters long")
        
        self._description = description
        self._updated_at = datetime.utcnow()
    
    def change_status(self, status: LessonStatus) -> None:
        """
        Change lesson status.
        
        Args:
            status: New status
        """
        self._status = status
        self._updated_at = datetime.utcnow()
        
        # Auto-update progress when status changes
        if status == LessonStatus.COMPLETED:
            self._progress_percentage = 100
        elif status == LessonStatus.NOT_STARTED:
            self._progress_percentage = 0
    
    def update_difficulty_level(self, difficulty_level: DifficultyLevel) -> None:
        """
        Update difficulty level.
        
        Args:
            difficulty_level: New difficulty level
        """
        self._difficulty_level = difficulty_level
        self._updated_at = datetime.utcnow()
    
    def update_estimated_duration(self, duration: Optional[int]) -> None:
        """
        Update estimated duration.
        
        Args:
            duration: New estimated duration in minutes
        """
        if duration is not None and duration < 0:
            raise ValueError("Estimated duration cannot be negative")
        
        self._estimated_duration = duration
        self._updated_at = datetime.utcnow()
    
    def toggle_favorite(self) -> None:
        """Toggle favorite status."""
        self._is_favorite = not self._is_favorite
        self._updated_at = datetime.utcnow()
    
    def set_favorite(self, is_favorite: bool) -> None:
        """
        Set favorite status.
        
        Args:
            is_favorite: Whether lesson is favorite
        """
        self._is_favorite = is_favorite
        self._updated_at = datetime.utcnow()
    
    def update_progress(self, percentage: int) -> None:
        """
        Update progress percentage.
        
        Args:
            percentage: Progress percentage (0-100)
        """
        if percentage < 0 or percentage > 100:
            raise ValueError("Progress percentage must be between 0 and 100")
        
        self._progress_percentage = percentage
        self._updated_at = datetime.utcnow()
        
        # Auto-update status based on progress
        if percentage == 100:
            self._status = LessonStatus.COMPLETED
        elif percentage > 0:
            self._status = LessonStatus.IN_PROGRESS
        else:
            self._status = LessonStatus.NOT_STARTED
    
    def add_time_spent(self, minutes: int) -> None:
        """
        Add time spent on lesson.
        
        Args:
            minutes: Minutes to add
        """
        if minutes < 0:
            raise ValueError("Time spent cannot be negative")
        
        self._total_time_spent += minutes
        self._updated_at = datetime.utcnow()
    
    def update_section_counts(self, total: int, completed: int) -> None:
        """
        Update section counts.
        
        Args:
            total: Total number of sections
            completed: Number of completed sections
        """
        if total < 0 or completed < 0:
            raise ValueError("Section counts cannot be negative")
        
        if completed > total:
            raise ValueError("Completed sections cannot exceed total sections")
        
        self._total_sections = total
        self._completed_sections = completed
        self._updated_at = datetime.utcnow()
        
        # Auto-update progress based on section completion
        if total > 0:
            self._progress_percentage = int((completed / total) * 100)
    
    def is_completed(self) -> bool:
        """Check if lesson is completed."""
        return self._status == LessonStatus.COMPLETED
    
    def is_in_progress(self) -> bool:
        """Check if lesson is in progress."""
        return self._status == LessonStatus.IN_PROGRESS
    
    def is_archived(self) -> bool:
        """Check if lesson is archived."""
        return self._status == LessonStatus.ARCHIVED
    
    def get_progress_ratio(self) -> float:
        """Get progress as ratio (0.0 to 1.0)."""
        return self._progress_percentage / 100.0
    
    def get_completion_ratio(self) -> float:
        """Get completion ratio based on sections (0.0 to 1.0)."""
        if self._total_sections == 0:
            return 0.0
        return self._completed_sections / self._total_sections
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert lesson to dictionary representation."""
        return {
            'id': self._id,
            'user_id': self._user_id,
            'title': self._title,
            'description': self._description,
            'status': self._status.value,
            'difficulty_level': self._difficulty_level.value,
            'estimated_duration': self._estimated_duration,
            'color_theme': self._color_theme,
            'is_favorite': self._is_favorite,
            'source_platform': self._source_platform.value,
            'external_id': self._external_id,
            'external_url': self._external_url,
            'author_name': self._author_name,
            'subject': self._subject,
            'grade_level': self._grade_level,
            'progress_percentage': self._progress_percentage,
            'total_sections': self._total_sections,
            'completed_sections': self._completed_sections,
            'total_time_spent': self._total_time_spent,
            'created_at': self._created_at.isoformat(),
            'updated_at': self._updated_at.isoformat()
        }
    
    def __str__(self) -> str:
        return f"Lesson({self._title}, {self._status.value})"
    
    def __repr__(self) -> str:
        return f"Lesson(id='{self._id}', title='{self._title}', status='{self._status.value}')"
