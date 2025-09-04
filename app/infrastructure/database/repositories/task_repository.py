"""
Task repository implementation using SQLAlchemy.
Infrastructure layer implementation of TaskRepository interface.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from app.domain.entities.task import Task, TaskStatus, TaskPriority, TaskType
from app.domain.interfaces.repositories.task_repository import TaskRepository
from ..models.task_model import TaskModel
from app import db
from app.shared.exceptions import ValidationException


class TaskRepositoryImpl(TaskRepository):
    """
    SQLAlchemy implementation of TaskRepository interface.
    Handles all database operations for Task entity.
    """
    
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
        try:
            task_model = TaskModel.from_domain_entity(task)
            db.session.add(task_model)
            db.session.commit()
            return task_model.to_domain_entity()
        except Exception as e:
            db.session.rollback()
            raise ValidationException(f"Failed to create task: {str(e)}")
    
    def get_by_id(self, task_id: str) -> Optional[Task]:
        """
        Get task by ID.
        
        Args:
            task_id: Task ID to search for
            
        Returns:
            Task entity if found, None otherwise
        """
        task_model = TaskModel.query.filter_by(id=task_id).first()
        return task_model.to_domain_entity() if task_model else None
    
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
        query = TaskModel.query.filter_by(user_id=user_id).order_by(TaskModel.created_at.desc())
        
        if offset:
            query = query.offset(offset)
        
        if limit:
            query = query.limit(limit)
        
        task_models = query.all()
        return [task_model.to_domain_entity() for task_model in task_models]
    
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
        try:
            task_model = TaskModel.query.filter_by(id=task.id).first()
            if not task_model:
                from ...shared.exceptions import NotFoundException
                raise NotFoundException("Task", task.id)
            
            # Update fields
            task_model.user_id = task.user_id
            task_model.title = task.title
            task_model.description = task.description
            task_model.task_type = task.task_type.value
            task_model.status = task.status.value
            task_model.priority = task.priority.value
            task_model.due_date = task.due_date
            task_model.estimated_duration = task.estimated_duration
            task_model.lesson_id = task.lesson_id
            task_model.section_id = task.section_id
            task_model.tags = json.dumps(task.tags) if task.tags else None
            task_model.is_reminder_enabled = task.is_reminder_enabled
            task_model.reminder_time = task.reminder_time
            task_model.progress_percentage = task.progress_percentage
            task_model.time_spent = task.time_spent
            task_model.completed_at = task.completed_at
            task_model.updated_at = task.updated_at
            
            db.session.commit()
            return task_model.to_domain_entity()
        except Exception as e:
            db.session.rollback()
            if "NotFoundException" in str(type(e)):
                raise
            raise ValidationException(f"Failed to update task: {str(e)}")
    
    def delete(self, task_id: str) -> bool:
        """
        Delete task by ID.
        
        Args:
            task_id: Task ID to delete
            
        Returns:
            True if deleted, False if not found
        """
        try:
            task_model = TaskModel.query.filter_by(id=task_id).first()
            if not task_model:
                return False
            
            db.session.delete(task_model)
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            raise ValidationException(f"Failed to delete task: {str(e)}")
    
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
        query = TaskModel.query.filter_by(
            user_id=user_id,
            status=status.value
        ).order_by(TaskModel.created_at.desc())
        
        if limit:
            query = query.limit(limit)
        
        task_models = query.all()
        return [task_model.to_domain_entity() for task_model in task_models]
    
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
        query = TaskModel.query.filter_by(
            user_id=user_id,
            priority=priority.value
        ).order_by(TaskModel.created_at.desc())
        
        if limit:
            query = query.limit(limit)
        
        task_models = query.all()
        return [task_model.to_domain_entity() for task_model in task_models]
    
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
        query = TaskModel.query.filter_by(
            user_id=user_id,
            task_type=task_type.value
        ).order_by(TaskModel.created_at.desc())
        
        if limit:
            query = query.limit(limit)
        
        task_models = query.all()
        return [task_model.to_domain_entity() for task_model in task_models]
    
    def get_by_lesson_id(self, lesson_id: str, limit: Optional[int] = None) -> List[Task]:
        """
        Get tasks by lesson ID.
        
        Args:
            lesson_id: Lesson ID to filter by
            limit: Maximum number of results
            
        Returns:
            List of task entities for the lesson
        """
        query = TaskModel.query.filter_by(lesson_id=lesson_id).order_by(TaskModel.created_at.desc())
        
        if limit:
            query = query.limit(limit)
        
        task_models = query.all()
        return [task_model.to_domain_entity() for task_model in task_models]
    
    def get_by_section_id(self, section_id: str, limit: Optional[int] = None) -> List[Task]:
        """
        Get tasks by section ID.
        
        Args:
            section_id: Section ID to filter by
            limit: Maximum number of results
            
        Returns:
            List of task entities for the section
        """
        query = TaskModel.query.filter_by(section_id=section_id).order_by(TaskModel.created_at.desc())
        
        if limit:
            query = query.limit(limit)
        
        task_models = query.all()
        return [task_model.to_domain_entity() for task_model in task_models]
    
    def get_overdue_tasks(self, user_id: str, limit: Optional[int] = None) -> List[Task]:
        """
        Get overdue tasks.
        
        Args:
            user_id: User ID to filter by
            limit: Maximum number of results
            
        Returns:
            List of overdue task entities
        """
        now = datetime.utcnow()
        query = TaskModel.query.filter(
            db.and_(
                TaskModel.user_id == user_id,
                TaskModel.due_date < now,
                TaskModel.status != TaskStatus.COMPLETED.value
            )
        ).order_by(TaskModel.due_date.asc())
        
        if limit:
            query = query.limit(limit)
        
        task_models = query.all()
        return [task_model.to_domain_entity() for task_model in task_models]
    
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
        now = datetime.utcnow()
        threshold = now + timedelta(hours=hours)
        
        query = TaskModel.query.filter(
            db.and_(
                TaskModel.user_id == user_id,
                TaskModel.due_date >= now,
                TaskModel.due_date <= threshold,
                TaskModel.status != TaskStatus.COMPLETED.value
            )
        ).order_by(TaskModel.due_date.asc())
        
        if limit:
            query = query.limit(limit)
        
        task_models = query.all()
        return [task_model.to_domain_entity() for task_model in task_models]
    
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
        query = TaskModel.query.filter_by(user_id=user_id)
        
        if start_date:
            start_dt = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
            query = query.filter(TaskModel.due_date >= start_dt)
        
        if end_date:
            end_dt = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
            query = query.filter(TaskModel.due_date <= end_dt)
        
        query = query.order_by(TaskModel.due_date.asc())
        
        if limit:
            query = query.limit(limit)
        
        task_models = query.all()
        return [task_model.to_domain_entity() for task_model in task_models]
    
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
        search_query = TaskModel.query.filter(
            db.and_(
                TaskModel.user_id == user_id,
                db.or_(
                    TaskModel.title.contains(query),
                    TaskModel.description.contains(query)
                )
            )
        ).order_by(TaskModel.created_at.desc())
        
        if limit:
            search_query = search_query.limit(limit)
        
        task_models = search_query.all()
        return [task_model.to_domain_entity() for task_model in task_models]
    
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
        query = TaskModel.query.filter_by(user_id=user_id)
        
        # Filter by tags (simplified - checks if any tag is contained in the tags JSON)
        for tag in tags:
            query = query.filter(TaskModel.tags.contains(tag))
        
        query = query.order_by(TaskModel.created_at.desc())
        
        if limit:
            query = query.limit(limit)
        
        task_models = query.all()
        return [task_model.to_domain_entity() for task_model in task_models]
    
    def get_high_priority_tasks(self, user_id: str, limit: Optional[int] = None) -> List[Task]:
        """
        Get high priority tasks (high and urgent).
        
        Args:
            user_id: User ID to filter by
            limit: Maximum number of results
            
        Returns:
            List of high priority task entities
        """
        query = TaskModel.query.filter(
            db.and_(
                TaskModel.user_id == user_id,
                db.or_(
                    TaskModel.priority == TaskPriority.HIGH.value,
                    TaskModel.priority == TaskPriority.URGENT.value
                )
            )
        ).order_by(TaskModel.created_at.desc())
        
        if limit:
            query = query.limit(limit)
        
        task_models = query.all()
        return [task_model.to_domain_entity() for task_model in task_models]
    
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
        query = TaskModel.query.filter_by(
            user_id=user_id,
            is_reminder_enabled=reminder_enabled
        ).order_by(TaskModel.created_at.desc())
        
        if limit:
            query = query.limit(limit)
        
        task_models = query.all()
        return [task_model.to_domain_entity() for task_model in task_models]
    
    def get_task_statistics(self, user_id: str) -> Dict[str, Any]:
        """
        Get task statistics for user.
        
        Args:
            user_id: User ID
            
        Returns:
            Dictionary with task statistics
        """
        total_tasks = TaskModel.query.filter_by(user_id=user_id).count()
        
        # Count by status
        status_counts = db.session.query(
            TaskModel.status,
            db.func.count(TaskModel.id)
        ).filter_by(user_id=user_id).group_by(TaskModel.status).all()
        
        # Count by priority
        priority_counts = db.session.query(
            TaskModel.priority,
            db.func.count(TaskModel.id)
        ).filter_by(user_id=user_id).group_by(TaskModel.priority).all()
        
        # Count by type
        type_counts = db.session.query(
            TaskModel.task_type,
            db.func.count(TaskModel.id)
        ).filter_by(user_id=user_id).group_by(TaskModel.task_type).all()
        
        # Count overdue tasks
        now = datetime.utcnow()
        overdue_count = TaskModel.query.filter(
            db.and_(
                TaskModel.user_id == user_id,
                TaskModel.due_date < now,
                TaskModel.status != TaskStatus.COMPLETED.value
            )
        ).count()
        
        # Count due soon tasks (next 24 hours)
        threshold = now + timedelta(hours=24)
        due_soon_count = TaskModel.query.filter(
            db.and_(
                TaskModel.user_id == user_id,
                TaskModel.due_date >= now,
                TaskModel.due_date <= threshold,
                TaskModel.status != TaskStatus.COMPLETED.value
            )
        ).count()
        
        # Total time spent
        total_time = db.session.query(
            db.func.sum(TaskModel.time_spent)
        ).filter_by(user_id=user_id).scalar() or 0
        
        return {
            'total_tasks': total_tasks,
            'status_counts': dict(status_counts),
            'priority_counts': dict(priority_counts),
            'type_counts': dict(type_counts),
            'overdue_count': overdue_count,
            'due_soon_count': due_soon_count,
            'total_time_spent': total_time
        }
    
    def count_by_user(self, user_id: str) -> int:
        """
        Count tasks by user.
        
        Args:
            user_id: User ID
            
        Returns:
            Total count of tasks for user
        """
        return TaskModel.query.filter_by(user_id=user_id).count()
    
    def get_recent_tasks(self, user_id: str, limit: int = 10) -> List[Task]:
        """
        Get recent tasks for user.
        
        Args:
            user_id: User ID
            limit: Maximum number of results
            
        Returns:
            List of recent task entities
        """
        task_models = TaskModel.query.filter_by(
            user_id=user_id
        ).order_by(TaskModel.updated_at.desc()).limit(limit).all()
        
        return [task_model.to_domain_entity() for task_model in task_models]
    
    def get_completed_tasks(self, user_id: str, limit: Optional[int] = None) -> List[Task]:
        """
        Get completed tasks for user.
        
        Args:
            user_id: User ID
            limit: Maximum number of results
            
        Returns:
            List of completed task entities
        """
        query = TaskModel.query.filter_by(
            user_id=user_id,
            status=TaskStatus.COMPLETED.value
        ).order_by(TaskModel.completed_at.desc())
        
        if limit:
            query = query.limit(limit)
        
        task_models = query.all()
        return [task_model.to_domain_entity() for task_model in task_models]
    
    def get_tasks_sorted_by_priority(self, user_id: str, limit: Optional[int] = None) -> List[Task]:
        """
        Get tasks sorted by priority score.
        
        Args:
            user_id: User ID
            limit: Maximum number of results
            
        Returns:
            List of task entities sorted by priority
        """
        # This is a simplified implementation
        # In a real application, you might want to implement custom sorting logic
        query = TaskModel.query.filter_by(user_id=user_id).order_by(
            TaskModel.priority.desc(),
            TaskModel.due_date.asc()
        )
        
        if limit:
            query = query.limit(limit)
        
        task_models = query.all()
        tasks = [task_model.to_domain_entity() for task_model in task_models]
        
        # Sort by priority score (domain logic)
        return sorted(tasks, key=lambda t: t.get_priority_score(), reverse=True)
    
    def get_all_user_tags(self, user_id: str) -> List[str]:
        """
        Get all unique tags for user.
        
        Args:
            user_id: User ID
            
        Returns:
            List of unique tags
        """
        # This is a simplified implementation
        # In a real application, you might want to use a separate tags table
        tasks = TaskModel.query.filter_by(user_id=user_id).all()
        all_tags = set()
        
        for task in tasks:
            if task.tags:
                try:
                    tags = json.loads(task.tags)
                    all_tags.update(tags)
                except (json.JSONDecodeError, TypeError):
                    continue
        
        return sorted(list(all_tags))
