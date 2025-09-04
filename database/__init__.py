# Database Package for Smart Learning Hub
from .config import DatabaseConfig
from .manager import DatabaseManager, get_db_manager, init_database, close_database
from .models import *

__all__ = [
    'DatabaseConfig',
    'DatabaseManager', 
    'get_db_manager',
    'init_database',
    'close_database',
    # Models
    'BaseModel',
    'User',
    'Lesson',
    'LessonSection',
    'Note',
    'Task',
    'Files',
    'Tag',
    'TagRelationship',
    'LessonTag',
    'ExternalIntegration',
    'ExternalData',
    'ProgressTracking',
    'PomodoroSession',
    'Reminder',
    'Report',
    'ActivityLog'
]
