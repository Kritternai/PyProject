"""
Task repository interface following Repository pattern.
Defines contract for task data access operations.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from ...entities.task import Task, TaskStatus, TaskPriority, TaskType


class TaskRepository(ABC):
    """
    Abstract repository interface for Task entity.
    Defines all data access operations for tasks.
    """
    
    @abstractmethod
    def create(self, task: Task) -> Task:
        """
        Create a new task.
        
        Args:
            task: Task entity to create
            
        Returns:
            Created task entity
            
        Raises:
            ValidationException: If task data is invalid
        """
        pass
    
    @abstractmethod
    def get_by_id(self, task_id: str) -> Optional[Task]:
        """
        Get task by ID.
        
        Args:
            task_id: Task ID to search for
            
        Returns:
            Task entity if found, None otherwise
        """
        pass
    
    @abstractmethod
    def get_by_user_id(self, user_id: str, limit: Optional[int] = None, offset: Optional[int] = None) -> List[Task]:
        """
        Get tasks by user ID.
        
        Args:
            user_id: User ID to search for
            limit: Maximum number of tasks to return
            offset: Number of tasks to skip
            
        Returns:
            List of task entities
        """
        pass
    
    @abstractmethod
    def update(self, task: Task) -> Task:
        """
        Update existing task.
        
        Args:
            task: Task entity to update
            
        Returns:
            Updated task entity
            
        Raises:
            NotFoundException: If task doesn't exist
            ValidationException: If task data is invalid
        """
        pass
    
    @abstractmethod
    def delete(self, task_id: str) -> bool:
        """
        Delete task by ID.
        
        Args:
            task_id: Task ID to delete
            
        Returns:
            True if deleted, False if not found
        """
        pass
    
    @abstractmethod
    def get_by_status(self, user_id: str, status: TaskStatus, limit: Optional[int] = None) -> List[Task]:
        """
        Get tasks by status.
        
        Args:
            user_id: User ID to filter by
            status: Task status to filter by
            limit: Maximum number of results
            
        Returns:
            List of task entities with specified status
        """
        pass
    
    @abstractmethod
    def get_by_priority(self, user_id: str, priority: TaskPriority, limit: Optional[int] = None) -> List[Task]:
        """
        Get tasks by priority.
        
        Args:
            user_id: User ID to filter by
            priority: Task priority to filter by
            limit: Maximum number of results
            
        Returns:
            List of task entities with specified priority
        """
        pass
    
    @abstractmethod
    def get_by_task_type(self, user_id: str, task_type: TaskType, limit: Optional[int] = None) -> List[Task]:
        """
        Get tasks by type.
        
        Args:
            user_id: User ID to filter by
            task_type: Task type to filter by
            limit: Maximum number of results
            
        Returns:
            List of task entities with specified type
        """
        pass
    
    @abstractmethod
    def get_by_lesson_id(self, lesson_id: str, limit: Optional[int] = None) -> List[Task]:
        """
        Get tasks by lesson ID.
        
        Args:
            lesson_id: Lesson ID to filter by
            limit: Maximum number of results
            
        Returns:
            List of task entities for the lesson
        """
        pass
    
    @abstractmethod
    def get_by_section_id(self, section_id: str, limit: Optional[int] = None) -> List[Task]:
        """
        Get tasks by section ID.
        
        Args:
            section_id: Section ID to filter by
            limit: Maximum number of results
            
        Returns:
            List of task entities for the section
        """
        pass
    
    @abstractmethod
    def get_overdue_tasks(self, user_id: str, limit: Optional[int] = None) -> List[Task]:
        """
        Get overdue tasks.
        
        Args:
            user_id: User ID to filter by
            limit: Maximum number of results
            
        Returns:
            List of overdue task entities
        """
        pass
    
    @abstractmethod
    def get_due_soon_tasks(self, user_id: str, hours: int = 24, limit: Optional[int] = None) -> List[Task]:
        """
        Get tasks due soon.
        
        Args:
            user_id: User ID to filter by
            hours: Hours threshold for "due soon"
            limit: Maximum number of results
            
        Returns:
            List of tasks due soon
        """
        pass
    
    @abstractmethod
    def get_tasks_by_date_range(
        self,
        user_id: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        limit: Optional[int] = None
    ) -> List[Task]:
        """
        Get tasks by date range.
        
        Args:
            user_id: User ID to filter by
            start_date: Start date (ISO format)
            end_date: End date (ISO format)
            limit: Maximum number of results
            
        Returns:
            List of task entities in date range
        """
        pass
    
    @abstractmethod
    def search(self, user_id: str, query: str, limit: Optional[int] = None) -> List[Task]:
        """
        Search tasks by query.
        
        Args:
            user_id: User ID to filter by
            query: Search query
            limit: Maximum number of results
            
        Returns:
            List of matching task entities
        """
        pass
    
    @abstractmethod
    def search_by_tags(self, user_id: str, tags: List[str], limit: Optional[int] = None) -> List[Task]:
        """
        Search tasks by tags.
        
        Args:
            user_id: User ID to filter by
            tags: List of tags to search for
            limit: Maximum number of results
            
        Returns:
            List of task entities with matching tags
        """
        pass
    
    @abstractmethod
    def get_high_priority_tasks(self, user_id: str, limit: Optional[int] = None) -> List[Task]:
        """
        Get high priority tasks (high and urgent).
        
        Args:
            user_id: User ID to filter by
            limit: Maximum number of results
            
        Returns:
            List of high priority task entities
        """
        pass
    
    @abstractmethod
    def get_tasks_by_reminder_status(self, user_id: str, reminder_enabled: bool, limit: Optional[int] = None) -> List[Task]:
        """
        Get tasks by reminder status.
        
        Args:
            user_id: User ID to filter by
            reminder_enabled: Whether reminder is enabled
            limit: Maximum number of results
            
        Returns:
            List of task entities with specified reminder status
        """
        pass
    
    @abstractmethod
    def get_task_statistics(self, user_id: str) -> Dict[str, Any]:
        """
        Get task statistics for user.
        
        Args:
            user_id: User ID
            
        Returns:
            Dictionary with task statistics
        """
        pass
    
    @abstractmethod
    def count_by_user(self, user_id: str) -> int:
        """
        Count tasks by user.
        
        Args:
            user_id: User ID
            
        Returns:
            Total count of tasks for user
        """
        pass
    
    @abstractmethod
    def get_recent_tasks(self, user_id: str, limit: int = 10) -> List[Task]:
        """
        Get recent tasks for user.
        
        Args:
            user_id: User ID
            limit: Maximum number of results
            
        Returns:
            List of recent task entities
        """
        pass
    
    @abstractmethod
    def get_completed_tasks(self, user_id: str, limit: Optional[int] = None) -> List[Task]:
        """
        Get completed tasks for user.
        
        Args:
            user_id: User ID
            limit: Maximum number of results
            
        Returns:
            List of completed task entities
        """
        pass
    
    @abstractmethod
    def get_tasks_sorted_by_priority(self, user_id: str, limit: Optional[int] = None) -> List[Task]:
        """
        Get tasks sorted by priority score.
        
        Args:
            user_id: User ID
            limit: Maximum number of results
            
        Returns:
            List of task entities sorted by priority
        """
        pass
    
    @abstractmethod
    def get_all_user_tags(self, user_id: str) -> List[str]:
        """
        Get all unique tags for user.
        
        Args:
            user_id: User ID
            
        Returns:
            List of unique tags
        """
        pass
