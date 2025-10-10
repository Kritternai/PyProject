"""
Task controller following Clean Architecture principles.
Handles HTTP requests and responses for task operations.
"""

from flask import request, jsonify, g
from typing import Dict, Any, Optional
from datetime import datetime
from app.services import TaskService
from app.utils.exceptions import (
    ValidationException,
    NotFoundException,
    BusinessLogicException,
    AuthorizationException
)
from ..middleware import login_required


class TaskController:
    """
    Controller for task-related HTTP operations.
    Handles request/response logic and delegates business logic to services.
    """
    
    def __init__(self):
        """Initialize controller with service dependencies."""
        self._task_service = TaskService()
    
    def create_task(self) -> Dict[str, Any]:
        """
        Create a new task.
        
        Returns:
            JSON response with created task data
        """
        try:
            current_user = g.user
            if not current_user:
                return jsonify({
                    'success': False,
                    'message': 'User not authenticated'
                }), 401
            
            data = request.get_json()
            if not data:
                return jsonify({
                    'success': False,
                    'message': 'Request body is required'
                }), 400
            
            # Validate required fields
            if 'title' not in data or not data['title']:
                return jsonify({
                    'success': False,
                    'message': 'Title is required'
                }), 400
            
            # Parse task type and priority (MVC - use strings directly)
            task_type = data.get('task_type', 'other')
            priority = data.get('priority', 'medium')
            
            # Parse due date
            due_date = None
            if 'due_date' in data and data['due_date']:
                try:
                    due_date = datetime.fromisoformat(data['due_date'].replace('Z', '+00:00'))
                except ValueError:
                    return jsonify({
                        'success': False,
                        'message': 'Invalid due date format'
                    }), 400
            
            # Create task
            task = self._task_service.create_task(
                user_id=current_user.id,
                title=data['title'],
                description=data.get('description'),
                task_type=task_type,
                priority=priority,
                due_date=due_date,
                estimated_duration=data.get('estimated_duration'),
                lesson_id=data.get('lesson_id'),
                section_id=data.get('section_id'),
                tags=data.get('tags'),
                is_reminder_enabled=data.get('is_reminder_enabled', True),
                reminder_time=data.get('reminder_time')
            )
            
            return jsonify({
                'success': True,
                'message': 'Task created successfully',
                'data': task.to_dict()
            }), 201
            
        except ValidationException as e:
            return jsonify({
                'success': False,
                'message': e.message,
                'error_code': e.error_code,
                'details': e.details
            }), 400
            
        except BusinessLogicException as e:
            return jsonify({
                'success': False,
                'message': e.message,
                'error_code': e.error_code,
                'details': e.details
            }), 409
            
        except Exception as e:
            return jsonify({
                'success': False,
                'message': 'Internal server error',
                'error': str(e)
            }), 500
    
    def get_task(self, task_id: str) -> Dict[str, Any]:
        """
        Get task by ID.
        
        Args:
            task_id: Task ID
            
        Returns:
            JSON response with task data
        """
        try:
            current_user = g.user
            if not current_user:
                return jsonify({
                    'success': False,
                    'message': 'User not authenticated'
                }), 401
            
            task = self._task_service.get_task_by_id(task_id, current_user.id)
            if not task:
                return jsonify({
                    'success': False,
                    'message': f'Task with ID {task_id} not found'
                }), 404
            
            return jsonify({
                'success': True,
                'data': task.to_dict()
            }), 200
            
        except Exception as e:
            return jsonify({
                'success': False,
                'message': 'Internal server error',
                'error': str(e)
            }), 500
    
    def get_user_tasks(self) -> Dict[str, Any]:
        """
        Get tasks for current user.
        
        Returns:
            JSON response with tasks list
        """
        try:
            current_user = g.user
            if not current_user:
                return jsonify({
                    'success': False,
                    'message': 'User not authenticated'
                }), 401
            
            # Get pagination parameters
            limit = request.args.get('limit', type=int)
            offset = request.args.get('offset', type=int)
            
            tasks = self._task_service.get_user_tasks(
                user_id=current_user.id,
                limit=limit,
                offset=offset
            )
            
            return jsonify({
                'success': True,
                'data': [task.to_dict() for task in tasks]
            }), 200
            
        except Exception as e:
            return jsonify({
                'success': False,
                'message': 'Internal server error',
                'error': str(e)
            }), 500
    
    def update_task(self, task_id: str) -> Dict[str, Any]:
        """
        Update task.
        
        Args:
            task_id: Task ID to update
            
        Returns:
            JSON response with updated task data
        """
        try:
            current_user = g.user
            if not current_user:
                return jsonify({
                    'success': False,
                    'message': 'User not authenticated'
                }), 401
            
            data = request.get_json()
            if not data:
                return jsonify({
                    'success': False,
                    'message': 'Request body is required'
                }), 400
            
            # Parse enums if provided
            # Task type and priority (MVC - use strings directly)
            task_type = None
            if 'task_type' in data:
                task_type = data['task_type']
            
            priority = None
            if 'priority' in data:
                priority = data['priority']
            
            # Parse due date
            due_date = None
            if 'due_date' in data and data['due_date']:
                try:
                    due_date = datetime.fromisoformat(data['due_date'].replace('Z', '+00:00'))
                except ValueError:
                    return jsonify({
                        'success': False,
                        'message': 'Invalid due date format'
                    }), 400
            
            # Update task
            task = self._task_service.update_task(
                task_id=task_id,
                user_id=current_user.id,
                title=data.get('title'),
                description=data.get('description'),
                task_type=task_type,
                priority=priority,
                due_date=due_date,
                estimated_duration=data.get('estimated_duration'),
                lesson_id=data.get('lesson_id'),
                section_id=data.get('section_id'),
                tags=data.get('tags'),
                is_reminder_enabled=data.get('is_reminder_enabled'),
                reminder_time=data.get('reminder_time')
            )
            
            return jsonify({
                'success': True,
                'message': 'Task updated successfully',
                'data': task.to_dict()
            }), 200
            
        except ValidationException as e:
            return jsonify({
                'success': False,
                'message': e.message,
                'error_code': e.error_code,
                'details': e.details
            }), 400
            
        except NotFoundException as e:
            return jsonify({
                'success': False,
                'message': e.message,
                'error_code': e.error_code
            }), 404
            
        except AuthorizationException as e:
            return jsonify({
                'success': False,
                'message': e.message,
                'error_code': e.error_code
            }), 403
            
        except BusinessLogicException as e:
            return jsonify({
                'success': False,
                'message': e.message,
                'error_code': e.error_code,
                'details': e.details
            }), 409
            
        except Exception as e:
            return jsonify({
                'success': False,
                'message': 'Internal server error',
                'error': str(e)
            }), 500
    
    def delete_task(self, task_id: str) -> Dict[str, Any]:
        """
        Delete task.
        
        Args:
            task_id: Task ID to delete
            
        Returns:
            JSON response
        """
        try:
            current_user = g.user
            if not current_user:
                return jsonify({
                    'success': False,
                    'message': 'User not authenticated'
                }), 401
            
            success = self._task_service.delete_task(task_id, current_user.id)
            
            if success:
                return jsonify({
                    'success': True,
                    'message': 'Task deleted successfully'
                }), 200
            else:
                return jsonify({
                    'success': False,
                    'message': 'Task not found'
                }), 404
            
        except AuthorizationException as e:
            return jsonify({
                'success': False,
                'message': e.message,
                'error_code': e.error_code
            }), 403
            
        except Exception as e:
            return jsonify({
                'success': False,
                'message': 'Internal server error',
                'error': str(e)
            }), 500
    
    def change_task_status(self, task_id: str) -> Dict[str, Any]:
        """
        Change task status.
        
        Args:
            task_id: Task ID
            
        Returns:
            JSON response with updated task data
        """
        try:
            current_user = g.user
            if not current_user:
                return jsonify({
                    'success': False,
                    'message': 'User not authenticated'
                }), 401
            
            data = request.get_json()
            if not data or 'status' not in data:
                return jsonify({
                    'success': False,
                    'message': 'Status is required'
                }), 400
            
            # Status (MVC - use string directly)
            status = data['status']
            task = self._task_service.change_task_status(task_id, current_user.id, status)
            
            return jsonify({
                'success': True,
                'message': 'Task status updated successfully',
                'data': task.to_dict()
            }), 200
            
        except ValidationException as e:
            return jsonify({
                'success': False,
                'message': e.message,
                'error_code': e.error_code,
                'details': e.details
            }), 400
            
        except NotFoundException as e:
            return jsonify({
                'success': False,
                'message': e.message,
                'error_code': e.error_code
            }), 404
            
        except AuthorizationException as e:
            return jsonify({
                'success': False,
                'message': e.message,
                'error_code': e.error_code
            }), 403
            
        except Exception as e:
            return jsonify({
                'success': False,
                'message': 'Internal server error',
                'error': str(e)
            }), 500
    
    def update_task_progress(self, task_id: str) -> Dict[str, Any]:
        """
        Update task progress.
        
        Args:
            task_id: Task ID
            
        Returns:
            JSON response with updated task data
        """
        try:
            current_user = g.user
            if not current_user:
                return jsonify({
                    'success': False,
                    'message': 'User not authenticated'
                }), 401
            
            data = request.get_json()
            if not data or 'percentage' not in data:
                return jsonify({
                    'success': False,
                    'message': 'Percentage is required'
                }), 400
            
            percentage = data['percentage']
            task = self._task_service.update_task_progress(task_id, current_user.id, percentage)
            
            return jsonify({
                'success': True,
                'message': 'Task progress updated successfully',
                'data': task.to_dict()
            }), 200
            
        except ValidationException as e:
            return jsonify({
                'success': False,
                'message': e.message,
                'error_code': e.error_code,
                'details': e.details
            }), 400
            
        except NotFoundException as e:
            return jsonify({
                'success': False,
                'message': e.message,
                'error_code': e.error_code
            }), 404
            
        except AuthorizationException as e:
            return jsonify({
                'success': False,
                'message': e.message,
                'error_code': e.error_code
            }), 403
            
        except Exception as e:
            return jsonify({
                'success': False,
                'message': 'Internal server error',
                'error': str(e)
            }), 500
    
    def add_time_spent(self, task_id: str) -> Dict[str, Any]:
        """
        Add time spent on task.
        
        Args:
            task_id: Task ID
            
        Returns:
            JSON response with updated task data
        """
        try:
            current_user = g.user
            if not current_user:
                return jsonify({
                    'success': False,
                    'message': 'User not authenticated'
                }), 401
            
            data = request.get_json()
            if not data or 'minutes' not in data:
                return jsonify({
                    'success': False,
                    'message': 'Minutes is required'
                }), 400
            
            minutes = data['minutes']
            task = self._task_service.add_time_spent(task_id, current_user.id, minutes)
            
            return jsonify({
                'success': True,
                'message': 'Time spent updated successfully',
                'data': task.to_dict()
            }), 200
            
        except ValidationException as e:
            return jsonify({
                'success': False,
                'message': e.message,
                'error_code': e.error_code,
                'details': e.details
            }), 400
            
        except NotFoundException as e:
            return jsonify({
                'success': False,
                'message': e.message,
                'error_code': e.error_code
            }), 404
            
        except AuthorizationException as e:
            return jsonify({
                'success': False,
                'message': e.message,
                'error_code': e.error_code
            }), 403
            
        except Exception as e:
            return jsonify({
                'success': False,
                'message': 'Internal server error',
                'error': str(e)
            }), 500
    
    def get_overdue_tasks(self) -> Dict[str, Any]:
        """
        Get overdue tasks.
        
        Returns:
            JSON response with overdue tasks
        """
        try:
            current_user = g.user
            if not current_user:
                return jsonify({
                    'success': False,
                    'message': 'User not authenticated'
                }), 401
            
            limit = request.args.get('limit', type=int)
            tasks = self._task_service.get_overdue_tasks(current_user.id, limit=limit)
            
            return jsonify({
                'success': True,
                'data': [task.to_dict() for task in tasks]
            }), 200
            
        except Exception as e:
            return jsonify({
                'success': False,
                'message': 'Internal server error',
                'error': str(e)
            }), 500
    
    def get_due_soon_tasks(self) -> Dict[str, Any]:
        """
        Get tasks due soon.
        
        Returns:
            JSON response with tasks due soon
        """
        try:
            current_user = g.user
            if not current_user:
                return jsonify({
                    'success': False,
                    'message': 'User not authenticated'
                }), 401
            
            hours = request.args.get('hours', 24, type=int)
            limit = request.args.get('limit', type=int)
            tasks = self._task_service.get_due_soon_tasks(current_user.id, hours=hours, limit=limit)
            
            return jsonify({
                'success': True,
                'data': [task.to_dict() for task in tasks]
            }), 200
            
        except Exception as e:
            return jsonify({
                'success': False,
                'message': 'Internal server error',
                'error': str(e)
            }), 500
    
    def get_high_priority_tasks(self) -> Dict[str, Any]:
        """
        Get high priority tasks.
        
        Returns:
            JSON response with high priority tasks
        """
        try:
            current_user = g.user
            if not current_user:
                return jsonify({
                    'success': False,
                    'message': 'User not authenticated'
                }), 401
            
            limit = request.args.get('limit', type=int)
            tasks = self._task_service.get_high_priority_tasks(current_user.id, limit=limit)
            
            return jsonify({
                'success': True,
                'data': [task.to_dict() for task in tasks]
            }), 200
            
        except Exception as e:
            return jsonify({
                'success': False,
                'message': 'Internal server error',
                'error': str(e)
            }), 500
    
    def search_tasks(self) -> Dict[str, Any]:
        """
        Search tasks.
        
        Returns:
            JSON response with matching tasks
        """
        try:
            current_user = g.user
            if not current_user:
                return jsonify({
                    'success': False,
                    'message': 'User not authenticated'
                }), 401
            
            query = request.args.get('q', '')
            if not query:
                return jsonify({
                    'success': False,
                    'message': 'Search query is required'
                }), 400
            
            limit = request.args.get('limit', type=int)
            tasks = self._task_service.search_tasks(current_user.id, query, limit=limit)
            
            return jsonify({
                'success': True,
                'data': [task.to_dict() for task in tasks]
            }), 200
            
        except Exception as e:
            return jsonify({
                'success': False,
                'message': 'Internal server error',
                'error': str(e)
            }), 500
    
    def get_task_statistics(self) -> Dict[str, Any]:
        """
        Get task statistics for current user.
        
        Returns:
            JSON response with task statistics
        """
        try:
            current_user = g.user
            if not current_user:
                return jsonify({
                    'success': False,
                    'message': 'User not authenticated'
                }), 401
            
            statistics = self._task_service.get_task_statistics(current_user.id)
            
            return jsonify({
                'success': True,
                'data': statistics
            }), 200
            
        except Exception as e:
            return jsonify({
                'success': False,
                'message': 'Internal server error',
                'error': str(e)
            }), 500
