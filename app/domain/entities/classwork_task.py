"""
Classwork Task Entity
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List
from enum import Enum

class TaskPriority(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class TaskStatus(Enum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    DONE = "done"
    CANCELLED = "cancelled"

@dataclass
class ClassworkTask:
    """Classwork Task Entity"""
    
    id: str
    user_id: str
    lesson_id: str
    title: str
    description: Optional[str] = None
    subject: Optional[str] = None
    category: Optional[str] = None
    priority: TaskPriority = TaskPriority.MEDIUM
    status: TaskStatus = TaskStatus.TODO
    due_date: Optional[datetime] = None
    estimated_time: int = 0  # in minutes
    actual_time: int = 0  # in minutes
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.updated_at is None:
            self.updated_at = datetime.now()
    
    def is_overdue(self) -> bool:
        """Check if task is overdue"""
        if self.due_date is None:
            return False
        return datetime.now() > self.due_date and self.status != TaskStatus.DONE
    
    def is_due_soon(self, hours: int = 24) -> bool:
        """Check if task is due within specified hours"""
        if self.due_date is None:
            return False
        time_diff = self.due_date - datetime.now()
        return 0 < time_diff.total_seconds() <= hours * 3600
    
    def get_progress_percentage(self) -> float:
        """Get progress percentage based on actual time vs estimated time"""
        if self.estimated_time == 0:
            return 0.0
        return min(100.0, (self.actual_time / self.estimated_time) * 100.0)
    
    def update_status(self, new_status: TaskStatus):
        """Update task status"""
        self.status = new_status
        self.updated_at = datetime.now()
        
        if new_status == TaskStatus.DONE:
            self.actual_time = self.estimated_time  # Assume completed when marked as done
    
    def add_time_spent(self, minutes: int):
        """Add time spent on task"""
        self.actual_time += minutes
        self.updated_at = datetime.now()
    
    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'lesson_id': self.lesson_id,
            'title': self.title,
            'description': self.description,
            'subject': self.subject,
            'category': self.category,
            'priority': self.priority.value,
            'status': self.status.value,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'estimated_time': self.estimated_time,
            'actual_time': self.actual_time,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'is_overdue': self.is_overdue(),
            'is_due_soon': self.is_due_soon(),
            'progress_percentage': self.get_progress_percentage()
        }
