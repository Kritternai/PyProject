"""
Task service implementation following Service Layer pattern.
Implements business logic for task operations.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from app.domain.entities.task import Task, TaskStatus, TaskPriority, TaskType
from app.domain.interfaces.services.task_service import TaskService
from app.domain.interfaces.repositories.task_repository import TaskRepository
from app.shared.exceptions import (
    ValidationException,
    NotFoundException,
    BusinessLogicException,
    AuthorizationException
)


class TaskServiceImpl(TaskService):
    """
    Implementation of TaskService interface.
    Contains business logic for task operations.
    """
    
    def __init__(self, task_repository: TaskRepository):
        """
        Initialize task service with repository dependency.
        
        Args:
            task_repository: Task repository implementation
        """
        self._task_repository = task_repository
    
    def create_task(
        self,
        user_id: str,
        title: str,
        description: Optional[str] = None,
        task_type: TaskType = TaskType.OTHER,
        priority: TaskPriority = TaskPriority.MEDIUM,
        due_date: Optional[datetime] = None,
        estimated_duration: Optional[int] = None,
        lesson_id: Optional[str] = None,
        section_id: Optional[str] = None,
        tags: Optional[List[str]] = None,
        is_reminder_enabled: bool = True,
        reminder_time: Optional[int] = None
    ) -> Task:
        """
        Create a new task with business validation.
        
        Args:
            user_id: ID of the user creating the task
            title: Task title
            description: Task description
            task_type: Type of task
            priority: Task priority
            due_date: Due date for the task
            estimated_duration: Estimated duration in minutes
            lesson_id: Associated lesson ID
            section_id: Associated section ID
            tags: List of tags
            is_reminder_enabled: Whether reminder is enabled
            reminder_time: Reminder time in minutes before due date
            
        Returns:
            Created task entity
            
        Raises:
            ValidationException: If task data is invalid
            BusinessLogicException: If business rules are violated
        """
        # Business validation
        if tags and len(tags) > 15:
            raise BusinessLogicException(
                "Cannot have more than 15 tags",
                rule="tag_limit"
            )
        
        if due_date and due_date < datetime.utcnow():
            raise BusinessLogicException(
                "Due date cannot be in the past",
                rule="future_due_date"
            )
        
        # Create task entity
        task = Task(
            user_id=user_id,
            title=title,
            description=description,
            task_type=task_type,
            priority=priority,
            due_date=due_date,
            estimated_duration=estimated_duration,
            lesson_id=lesson_id,
            section_id=section_id,
            tags=tags or [],
            is_reminder_enabled=is_reminder_enabled,
            reminder_time=reminder_time
        )
        
        # Save to repository
        return self._task_repository.create(task)
    
    def get_task_by_id(self, task_id: str, user_id: str) -> Optional[Task]:
        """
        Get task by ID with user authorization.
        
        Args:
            task_id: Task ID to search for
            user_id: User ID for authorization
            
        Returns:
            Task entity if found and authorized, None otherwise
        """
        task = self._task_repository.get_by_id(task_id)
        if task and task.user_id == user_id:
            return task
        return None
    
    def get_user_tasks(
        self,
        user_id: str,
        limit: Optional[int] = None,
        offset: Optional[int] = None
    ) -> List[Task]:
        """
        Get tasks for a user.
        
        Args:
            user_id: User ID
            limit: Maximum number of tasks
            offset: Number of tasks to skip
            
        Returns:
            List of task entities
        """
        return self._task_repository.get_by_user_id(user_id, limit=limit, offset=offset)
    
    def update_task(
        self,
        task_id: str,
        user_id: str,
        title: Optional[str] = None,
        description: Optional[str] = None,
        task_type: Optional[TaskType] = None,
        priority: Optional[TaskPriority] = None,
        due_date: Optional[datetime] = None,
        estimated_duration: Optional[int] = None,
        lesson_id: Optional[str] = None,
        section_id: Optional[str] = None,
        tags: Optional[List[str]] = None,
        is_reminder_enabled: Optional[bool] = None,
        reminder_time: Optional[int] = None
    ) -> Task:
        """
        Update task with business validation.
        
        Args:
            task_id: Task ID to update
            user_id: User ID for authorization
            title: New title
            description: New description
            task_type: New task type
            priority: New priority
            due_date: New due date
            estimated_duration: New estimated duration
            lesson_id: New lesson ID
            section_id: New section ID
            tags: New tags
            is_reminder_enabled: New reminder status
            reminder_time: New reminder time
            
        Returns:
            Updated task entity
            
        Raises:
            NotFoundException: If task doesn't exist
            ValidationException: If data is invalid
            AuthorizationException: If user not authorized
        """
        task = self._task_repository.get_by_id(task_id)
        if not task:
            raise NotFoundException("Task", task_id)
        
        if task.user_id != user_id:
            raise AuthorizationException("You can only update your own tasks")
        
        # Business validation for due date
        if due_date and due_date < datetime.utcnow():
            raise BusinessLogicException(
                "Due date cannot be in the past",
                rule="future_due_date"
            )
        
        # Update fields
        if title is not None:
            task.update_title(title)
        
        if description is not None:
            task.update_description(description)
        
        if task_type is not None:
            task.change_task_type(task_type)
        
        if priority is not None:
            task.change_priority(priority)
        
        if due_date is not None:
            task.set_due_date(due_date)
        
        if estimated_duration is not None:
            task.update_estimated_duration(estimated_duration)
        
        if lesson_id is not None:
            task.set_lesson_association(lesson_id)
        
        if section_id is not None:
            task.set_section_association(section_id)
        
        if tags is not None:
            task.set_tags(tags)
        
        if is_reminder_enabled is not None or reminder_time is not None:
            task.set_reminder(is_reminder_enabled or task.is_reminder_enabled, reminder_time)
        
        return self._task_repository.update(task)
    
    def delete_task(self, task_id: str, user_id: str) -> bool:
        """
        Delete task with user authorization.
        
        Args:
            task_id: Task ID to delete
            user_id: User ID for authorization
            
        Returns:
            True if deleted, False if not found
            
        Raises:
            AuthorizationException: If user not authorized
        """
        task = self._task_repository.get_by_id(task_id)
        if task and task.user_id != user_id:
            raise AuthorizationException("You can only delete your own tasks")
        
        return self._task_repository.delete(task_id)
    
    def change_task_status(self, task_id: str, user_id: str, status: TaskStatus) -> Task:
        """
        Change task status.
        
        Args:
            task_id: Task ID
            user_id: User ID for authorization
            status: New status
            
        Returns:
            Updated task entity
            
        Raises:
            NotFoundException: If task doesn't exist
            AuthorizationException: If user not authorized
        """
        task = self._task_repository.get_by_id(task_id)
        if not task:
            raise NotFoundException("Task", task_id)
        
        if task.user_id != user_id:
            raise AuthorizationException("You can only update your own tasks")
        
        task.change_status(status)
        return self._task_repository.update(task)
    
    def update_task_progress(self, task_id: str, user_id: str, percentage: int) -> Task:
        """
        Update task progress.
        
        Args:
            task_id: Task ID
            user_id: User ID for authorization
            percentage: Progress percentage (0-100)
            
        Returns:
            Updated task entity
            
        Raises:
            NotFoundException: If task doesn't exist
            ValidationException: If percentage is invalid
            AuthorizationException: If user not authorized
        """
        task = self._task_repository.get_by_id(task_id)
        if not task:
            raise NotFoundException("Task", task_id)
        
        if task.user_id != user_id:
            raise AuthorizationException("You can only update your own tasks")
        
        task.update_progress(percentage)
        return self._task_repository.update(task)
    
    def add_time_spent(self, task_id: str, user_id: str, minutes: int) -> Task:
        """
        Add time spent on task.
        
        Args:
            task_id: Task ID
            user_id: User ID for authorization
            minutes: Minutes to add
            
        Returns:
            Updated task entity
            
        Raises:
            NotFoundException: If task doesn't exist
            ValidationException: If minutes is invalid
            AuthorizationException: If user not authorized
        """
        task = self._task_repository.get_by_id(task_id)
        if not task:
            raise NotFoundException("Task", task_id)
        
        if task.user_id != user_id:
            raise AuthorizationException("You can only update your own tasks")
        
        task.add_time_spent(minutes)
        return self._task_repository.update(task)
    
    def get_tasks_by_status(
        self,
        user_id: str,
        status: TaskStatus,
        limit: Optional[int] = None
    ) -> List[Task]:
        """
        Get tasks by status.
        
        Args:
            user_id: User ID
            status: Task status
            limit: Maximum number of results
            
        Returns:
            List of task entities with specified status
        """
        return self._task_repository.get_by_status(user_id, status, limit=limit)
    
    def get_tasks_by_priority(
        self,
        user_id: str,
        priority: TaskPriority,
        limit: Optional[int] = None
    ) -> List[Task]:
        """
        Get tasks by priority.
        
        Args:
            user_id: User ID
            priority: Task priority
            limit: Maximum number of results
            
        Returns:
            List of task entities with specified priority
        """
        return self._task_repository.get_by_priority(user_id, priority, limit=limit)
    
    def get_tasks_by_type(
        self,
        user_id: str,
        task_type: TaskType,
        limit: Optional[int] = None
    ) -> List[Task]:
        """
        Get tasks by type.
        
        Args:
            user_id: User ID
            task_type: Task type
            limit: Maximum number of results
            
        Returns:
            List of task entities with specified type
        """
        return self._task_repository.get_by_task_type(user_id, task_type, limit=limit)
    
    def get_tasks_by_lesson(self, lesson_id: str, user_id: str, limit: Optional[int] = None) -> List[Task]:
        """
        Get tasks for a specific lesson.
        
        Args:
            lesson_id: Lesson ID
            user_id: User ID for authorization
            limit: Maximum number of results
            
        Returns:
            List of task entities for the lesson
        """
        tasks = self._task_repository.get_by_lesson_id(lesson_id, limit=limit)
        # Filter by user authorization
        return [task for task in tasks if task.user_id == user_id]
    
    def get_tasks_by_section(self, section_id: str, user_id: str, limit: Optional[int] = None) -> List[Task]:
        """
        Get tasks for a specific section.
        
        Args:
            section_id: Section ID
            user_id: User ID for authorization
            limit: Maximum number of results
            
        Returns:
            List of task entities for the section
        """
        tasks = self._task_repository.get_by_section_id(section_id, limit=limit)
        # Filter by user authorization
        return [task for task in tasks if task.user_id == user_id]
    
    def get_overdue_tasks(self, user_id: str, limit: Optional[int] = None) -> List[Task]:
        """
        Get overdue tasks.
        
        Args:
            user_id: User ID
            limit: Maximum number of results
            
        Returns:
            List of overdue task entities
        """
        return self._task_repository.get_overdue_tasks(user_id, limit=limit)
    
    def get_due_soon_tasks(self, user_id: str, hours: int = 24, limit: Optional[int] = None) -> List[Task]:
        """
        Get tasks due soon.
        
        Args:
            user_id: User ID
            hours: Hours threshold for "due soon"
            limit: Maximum number of results
            
        Returns:
            List of tasks due soon
        """
        return self._task_repository.get_due_soon_tasks(user_id, hours=hours, limit=limit)
    
    def get_high_priority_tasks(self, user_id: str, limit: Optional[int] = None) -> List[Task]:
        """
        Get high priority tasks.
        
        Args:
            user_id: User ID
            limit: Maximum number of results
            
        Returns:
            List of high priority task entities
        """
        return self._task_repository.get_high_priority_tasks(user_id, limit=limit)
    
    def search_tasks(
        self,
        user_id: str,
        query: str,
        limit: Optional[int] = None
    ) -> List[Task]:
        """
        Search tasks by query.
        
        Args:
            user_id: User ID
            query: Search query
            limit: Maximum number of results
            
        Returns:
            List of matching task entities
        """
        return self._task_repository.search(user_id, query, limit=limit)
    
    def search_tasks_by_tags(
        self,
        user_id: str,
        tags: List[str],
        limit: Optional[int] = None
    ) -> List[Task]:
        """
        Search tasks by tags.
        
        Args:
            user_id: User ID
            tags: List of tags to search for
            limit: Maximum number of results
            
        Returns:
            List of task entities with matching tags
        """
        return self._task_repository.search_by_tags(user_id, tags, limit=limit)
    
    def get_tasks_sorted_by_priority(self, user_id: str, limit: Optional[int] = None) -> List[Task]:
        """
        Get tasks sorted by priority score.
        
        Args:
            user_id: User ID
            limit: Maximum number of results
            
        Returns:
            List of task entities sorted by priority
        """
        return self._task_repository.get_tasks_sorted_by_priority(user_id, limit=limit)
    
    def toggle_reminder(self, task_id: str, user_id: str) -> Task:
        """
        Toggle task reminder status.
        
        Args:
            task_id: Task ID
            user_id: User ID for authorization
            
        Returns:
            Updated task entity
            
        Raises:
            NotFoundException: If task doesn't exist
            AuthorizationException: If user not authorized
        """
        task = self._task_repository.get_by_id(task_id)
        if not task:
            raise NotFoundException("Task", task_id)
        
        if task.user_id != user_id:
            raise AuthorizationException("You can only update your own tasks")
        
        task.toggle_reminder()
        return self._task_repository.update(task)
    
    def set_reminder(self, task_id: str, user_id: str, is_enabled: bool, reminder_time: Optional[int] = None) -> Task:
        """
        Set task reminder configuration.
        
        Args:
            task_id: Task ID
            user_id: User ID for authorization
            is_enabled: Whether reminder is enabled
            reminder_time: Reminder time in minutes before due date
            
        Returns:
            Updated task entity
            
        Raises:
            NotFoundException: If task doesn't exist
            ValidationException: If reminder time is invalid
            AuthorizationException: If user not authorized
        """
        task = self._task_repository.get_by_id(task_id)
        if not task:
            raise NotFoundException("Task", task_id)
        
        if task.user_id != user_id:
            raise AuthorizationException("You can only update your own tasks")
        
        task.set_reminder(is_enabled, reminder_time)
        return self._task_repository.update(task)
    
    def add_tag(self, task_id: str, user_id: str, tag: str) -> Task:
        """
        Add tag to task.
        
        Args:
            task_id: Task ID
            user_id: User ID for authorization
            tag: Tag to add
            
        Returns:
            Updated task entity
            
        Raises:
            NotFoundException: If task doesn't exist
            ValidationException: If tag is invalid
            AuthorizationException: If user not authorized
        """
        task = self._task_repository.get_by_id(task_id)
        if not task:
            raise NotFoundException("Task", task_id)
        
        if task.user_id != user_id:
            raise AuthorizationException("You can only update your own tasks")
        
        task.add_tag(tag)
        return self._task_repository.update(task)
    
    def remove_tag(self, task_id: str, user_id: str, tag: str) -> Task:
        """
        Remove tag from task.
        
        Args:
            task_id: Task ID
            user_id: User ID for authorization
            tag: Tag to remove
            
        Returns:
            Updated task entity
            
        Raises:
            NotFoundException: If task doesn't exist
            AuthorizationException: If user not authorized
        """
        task = self._task_repository.get_by_id(task_id)
        if not task:
            raise NotFoundException("Task", task_id)
        
        if task.user_id != user_id:
            raise AuthorizationException("You can only update your own tasks")
        
        task.remove_tag(tag)
        return self._task_repository.update(task)
    
    def get_task_statistics(self, user_id: str) -> Dict[str, Any]:
        """
        Get task statistics for user.
        
        Args:
            user_id: User ID
            
        Returns:
            Dictionary with task statistics
        """
        return self._task_repository.get_task_statistics(user_id)
    
    def get_recent_tasks(self, user_id: str, limit: int = 10) -> List[Task]:
        """
        Get recent tasks for user.
        
        Args:
            user_id: User ID
            limit: Maximum number of results
            
        Returns:
            List of recent task entities
        """
        return self._task_repository.get_recent_tasks(user_id, limit=limit)
    
    def get_completed_tasks(self, user_id: str, limit: Optional[int] = None) -> List[Task]:
        """
        Get completed tasks for user.
        
        Args:
            user_id: User ID
            limit: Maximum number of results
            
        Returns:
            List of completed task entities
        """
        return self._task_repository.get_completed_tasks(user_id, limit=limit)
    
    def get_all_user_tags(self, user_id: str) -> List[str]:
        """
        Get all unique tags for user.
        
        Args:
            user_id: User ID
            
        Returns:
            List of unique tags
        """
        return self._task_repository.get_all_user_tags(user_id)
