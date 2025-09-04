"""
Task domain entity following Domain-Driven Design principles.
Pure business object with no external dependencies.
"""

import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum
from ..interfaces.entity import Entity


class TaskStatus(Enum):
    """Task status enumeration."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    ON_HOLD = "on_hold"


class TaskPriority(Enum):
    """Task priority enumeration."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class TaskType(Enum):
    """Task type enumeration."""
    STUDY = "study"
    ASSIGNMENT = "assignment"
    PROJECT = "project"
    EXAM = "exam"
    READING = "reading"
    PRACTICE = "practice"
    REVIEW = "review"
    OTHER = "other"


class Task(Entity):
    """
    Task domain entity representing a task in the system.
    Contains business logic and validation rules.
    """
    
    def __init__(
        self,
        user_id: str,
        title: str,
        description: Optional[str] = None,
        task_type: TaskType = TaskType.OTHER,
        status: TaskStatus = TaskStatus.PENDING,
        priority: TaskPriority = TaskPriority.MEDIUM,
        due_date: Optional[datetime] = None,
        estimated_duration: Optional[int] = None,
        lesson_id: Optional[str] = None,
        section_id: Optional[str] = None,
        tags: Optional[List[str]] = None,
        is_reminder_enabled: bool = True,
        reminder_time: Optional[int] = None,
        task_id: Optional[str] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None
    ):
        """
        Initialize task entity.
        
        Args:
            user_id: ID of the user who owns this task
            title: Task title
            description: Task description
            task_type: Type of task
            status: Task status
            priority: Task priority
            due_date: Due date for the task
            estimated_duration: Estimated duration in minutes
            lesson_id: Associated lesson ID
            section_id: Associated section ID
            tags: List of tags
            is_reminder_enabled: Whether reminder is enabled
            reminder_time: Reminder time in minutes before due date
            task_id: Task ID (auto-generated if not provided)
            created_at: Creation timestamp
            updated_at: Last update timestamp
        """
        self._id = task_id or str(uuid.uuid4())
        self._user_id = user_id
        self._title = title
        self._description = description
        self._task_type = task_type
        self._status = status
        self._priority = priority
        self._due_date = due_date
        self._estimated_duration = estimated_duration
        self._lesson_id = lesson_id
        self._section_id = section_id
        self._tags = tags or []
        self._is_reminder_enabled = is_reminder_enabled
        self._reminder_time = reminder_time
        
        # Progress tracking
        self._progress_percentage = 0
        self._time_spent = 0  # minutes
        self._completed_at = None
        
        # Timestamps
        self._created_at = created_at or datetime.utcnow()
        self._updated_at = updated_at or datetime.utcnow()
        
        # Validate business rules
        self._validate()
    
    def _validate(self) -> None:
        """Validate task business rules."""
        if not self._user_id or len(self._user_id.strip()) == 0:
            raise ValueError("User ID cannot be empty")
        
        if not self._title or len(self._title.strip()) == 0:
            raise ValueError("Title cannot be empty")
        
        if len(self._title) > 200:
            raise ValueError("Title must be no more than 200 characters long")
        
        if self._description and len(self._description) > 2000:
            raise ValueError("Description must be no more than 2000 characters long")
        
        if self._estimated_duration is not None and self._estimated_duration < 0:
            raise ValueError("Estimated duration cannot be negative")
        
        if self._time_spent < 0:
            raise ValueError("Time spent cannot be negative")
        
        if self._progress_percentage < 0 or self._progress_percentage > 100:
            raise ValueError("Progress percentage must be between 0 and 100")
        
        if self._tags and len(self._tags) > 15:
            raise ValueError("Cannot have more than 15 tags")
        
        for tag in self._tags:
            if len(tag) > 50:
                raise ValueError("Tag must be no more than 50 characters long")
        
        if self._reminder_time is not None and self._reminder_time < 0:
            raise ValueError("Reminder time cannot be negative")
    
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
    def task_type(self) -> TaskType:
        return self._task_type
    
    @property
    def status(self) -> TaskStatus:
        return self._status
    
    @property
    def priority(self) -> TaskPriority:
        return self._priority
    
    @property
    def due_date(self) -> Optional[datetime]:
        return self._due_date
    
    @property
    def estimated_duration(self) -> Optional[int]:
        return self._estimated_duration
    
    @property
    def lesson_id(self) -> Optional[str]:
        return self._lesson_id
    
    @property
    def section_id(self) -> Optional[str]:
        return self._section_id
    
    @property
    def tags(self) -> List[str]:
        return self._tags.copy()
    
    @property
    def is_reminder_enabled(self) -> bool:
        return self._is_reminder_enabled
    
    @property
    def reminder_time(self) -> Optional[int]:
        return self._reminder_time
    
    @property
    def progress_percentage(self) -> int:
        return self._progress_percentage
    
    @property
    def time_spent(self) -> int:
        return self._time_spent
    
    @property
    def completed_at(self) -> Optional[datetime]:
        return self._completed_at
    
    @property
    def created_at(self) -> datetime:
        return self._created_at
    
    @property
    def updated_at(self) -> datetime:
        return self._updated_at
    
    # Business methods
    def update_title(self, title: str) -> None:
        """
        Update task title.
        
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
        Update task description.
        
        Args:
            description: New description
        """
        if description and len(description) > 2000:
            raise ValueError("Description must be no more than 2000 characters long")
        
        self._description = description
        self._updated_at = datetime.utcnow()
    
    def change_status(self, status: TaskStatus) -> None:
        """
        Change task status.
        
        Args:
            status: New status
        """
        self._status = status
        self._updated_at = datetime.utcnow()
        
        # Auto-update progress and completion time
        if status == TaskStatus.COMPLETED:
            self._progress_percentage = 100
            self._completed_at = datetime.utcnow()
        elif status == TaskStatus.PENDING:
            self._progress_percentage = 0
            self._completed_at = None
        elif status == TaskStatus.IN_PROGRESS and self._progress_percentage == 0:
            self._progress_percentage = 10  # Start with 10% when beginning
    
    def change_priority(self, priority: TaskPriority) -> None:
        """
        Change task priority.
        
        Args:
            priority: New priority
        """
        self._priority = priority
        self._updated_at = datetime.utcnow()
    
    def change_task_type(self, task_type: TaskType) -> None:
        """
        Change task type.
        
        Args:
            task_type: New task type
        """
        self._task_type = task_type
        self._updated_at = datetime.utcnow()
    
    def set_due_date(self, due_date: Optional[datetime]) -> None:
        """
        Set due date.
        
        Args:
            due_date: New due date
        """
        self._due_date = due_date
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
    
    def set_lesson_association(self, lesson_id: Optional[str]) -> None:
        """
        Set lesson association.
        
        Args:
            lesson_id: Lesson ID to associate with
        """
        self._lesson_id = lesson_id
        self._updated_at = datetime.utcnow()
    
    def set_section_association(self, section_id: Optional[str]) -> None:
        """
        Set section association.
        
        Args:
            section_id: Section ID to associate with
        """
        self._section_id = section_id
        self._updated_at = datetime.utcnow()
    
    def add_tag(self, tag: str) -> None:
        """
        Add a tag to the task.
        
        Args:
            tag: Tag to add
            
        Raises:
            ValueError: If tag is invalid or limit exceeded
        """
        if not tag or len(tag.strip()) == 0:
            raise ValueError("Tag cannot be empty")
        
        if len(tag) > 50:
            raise ValueError("Tag must be no more than 50 characters long")
        
        if len(self._tags) >= 15:
            raise ValueError("Cannot have more than 15 tags")
        
        tag = tag.strip().lower()
        if tag not in self._tags:
            self._tags.append(tag)
            self._updated_at = datetime.utcnow()
    
    def remove_tag(self, tag: str) -> None:
        """
        Remove a tag from the task.
        
        Args:
            tag: Tag to remove
        """
        tag = tag.strip().lower()
        if tag in self._tags:
            self._tags.remove(tag)
            self._updated_at = datetime.utcnow()
    
    def set_tags(self, tags: List[str]) -> None:
        """
        Set all tags for the task.
        
        Args:
            tags: List of tags
            
        Raises:
            ValueError: If tags are invalid
        """
        if len(tags) > 15:
            raise ValueError("Cannot have more than 15 tags")
        
        for tag in tags:
            if not tag or len(tag.strip()) == 0:
                raise ValueError("Tag cannot be empty")
            if len(tag) > 50:
                raise ValueError("Tag must be no more than 50 characters long")
        
        self._tags = [tag.strip().lower() for tag in tags]
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
            self._status = TaskStatus.COMPLETED
            self._completed_at = datetime.utcnow()
        elif percentage > 0:
            self._status = TaskStatus.IN_PROGRESS
        else:
            self._status = TaskStatus.PENDING
    
    def add_time_spent(self, minutes: int) -> None:
        """
        Add time spent on task.
        
        Args:
            minutes: Minutes to add
        """
        if minutes < 0:
            raise ValueError("Time spent cannot be negative")
        
        self._time_spent += minutes
        self._updated_at = datetime.utcnow()
    
    def toggle_reminder(self) -> None:
        """Toggle reminder status."""
        self._is_reminder_enabled = not self._is_reminder_enabled
        self._updated_at = datetime.utcnow()
    
    def set_reminder(self, is_enabled: bool, reminder_time: Optional[int] = None) -> None:
        """
        Set reminder configuration.
        
        Args:
            is_enabled: Whether reminder is enabled
            reminder_time: Reminder time in minutes before due date
        """
        self._is_reminder_enabled = is_enabled
        if reminder_time is not None and reminder_time < 0:
            raise ValueError("Reminder time cannot be negative")
        self._reminder_time = reminder_time
        self._updated_at = datetime.utcnow()
    
    def is_overdue(self) -> bool:
        """
        Check if task is overdue.
        
        Returns:
            True if task is overdue, False otherwise
        """
        if not self._due_date or self._status == TaskStatus.COMPLETED:
            return False
        
        return datetime.utcnow() > self._due_date
    
    def is_due_soon(self, hours: int = 24) -> bool:
        """
        Check if task is due soon.
        
        Args:
            hours: Hours threshold for "due soon"
            
        Returns:
            True if task is due within the specified hours, False otherwise
        """
        if not self._due_date or self._status == TaskStatus.COMPLETED:
            return False
        
        from datetime import timedelta
        threshold = datetime.utcnow() + timedelta(hours=hours)
        return self._due_date <= threshold
    
    def get_remaining_time(self) -> Optional[int]:
        """
        Get remaining time until due date in minutes.
        
        Returns:
            Remaining time in minutes, or None if no due date
        """
        if not self._due_date:
            return None
        
        now = datetime.utcnow()
        if now >= self._due_date:
            return 0
        
        delta = self._due_date - now
        return int(delta.total_seconds() / 60)
    
    def get_priority_score(self) -> int:
        """
        Get priority score for sorting (higher = more urgent).
        
        Returns:
            Priority score
        """
        priority_scores = {
            TaskPriority.LOW: 1,
            TaskPriority.MEDIUM: 2,
            TaskPriority.HIGH: 3,
            TaskPriority.URGENT: 4
        }
        
        score = priority_scores.get(self._priority, 2)
        
        # Boost score for overdue tasks
        if self.is_overdue():
            score += 2
        elif self.is_due_soon(24):
            score += 1
        
        return score
    
    def has_tag(self, tag: str) -> bool:
        """
        Check if task has a specific tag.
        
        Args:
            tag: Tag to check
            
        Returns:
            True if task has the tag, False otherwise
        """
        return tag.strip().lower() in self._tags
    
    def get_tags_string(self) -> str:
        """
        Get tags as comma-separated string.
        
        Returns:
            Comma-separated tags string
        """
        return ", ".join(self._tags)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert task to dictionary representation."""
        return {
            'id': self._id,
            'user_id': self._user_id,
            'title': self._title,
            'description': self._description,
            'task_type': self._task_type.value,
            'status': self._status.value,
            'priority': self._priority.value,
            'due_date': self._due_date.isoformat() if self._due_date else None,
            'estimated_duration': self._estimated_duration,
            'lesson_id': self._lesson_id,
            'section_id': self._section_id,
            'tags': self._tags,
            'is_reminder_enabled': self._is_reminder_enabled,
            'reminder_time': self._reminder_time,
            'progress_percentage': self._progress_percentage,
            'time_spent': self._time_spent,
            'completed_at': self._completed_at.isoformat() if self._completed_at else None,
            'created_at': self._created_at.isoformat(),
            'updated_at': self._updated_at.isoformat(),
            'is_overdue': self.is_overdue(),
            'is_due_soon': self.is_due_soon(),
            'remaining_time': self.get_remaining_time(),
            'priority_score': self.get_priority_score()
        }
    
    def __str__(self) -> str:
        return f"Task({self._title}, {self._status.value}, {self._priority.value})"
    
    def __repr__(self) -> str:
        return f"Task(id='{self._id}', title='{self._title}', status='{self._status.value}')"
