"""
Lesson controller following Clean Architecture principles.
Handles HTTP requests and responses for lesson operations.
"""

from flask import request, jsonify
from typing import Dict, Any, Optional
from app.domain.interfaces.services.lesson_service import LessonService
from app.domain.entities.lesson import LessonStatus, DifficultyLevel, SourcePlatform
from app.shared.exceptions import (
    ValidationException,
    NotFoundException,
    BusinessLogicException,
    AuthorizationException
)
from ..middleware.auth_middleware import login_required, get_current_user
from app.infrastructure.di.container import get_service


class LessonController:
    """
    Controller for lesson-related HTTP operations.
    Handles request/response logic and delegates business logic to services.
    """
    
    def __init__(self):
        """Initialize controller with service dependencies."""
        self._lesson_service: LessonService = get_service(LessonService)
    
    def create_lesson(self) -> Dict[str, Any]:
        """
        Create a new lesson.
        
        Returns:
            JSON response with created lesson data
        """
        try:
            current_user = get_current_user()
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
            
            # Parse enums
            difficulty_level = DifficultyLevel(data.get('difficulty_level', 'beginner'))
            source_platform = SourcePlatform(data.get('source_platform', 'manual'))
            
            # Create lesson
            lesson = self._lesson_service.create_lesson(
                user_id=current_user.id,
                title=data['title'],
                description=data.get('description'),
                difficulty_level=difficulty_level,
                estimated_duration=data.get('estimated_duration'),
                color_theme=data.get('color_theme', 1),
                source_platform=source_platform,
                external_id=data.get('external_id'),
                external_url=data.get('external_url'),
                author_name=data.get('author_name'),
                subject=data.get('subject'),
                grade_level=data.get('grade_level')
            )
            
            return jsonify({
                'success': True,
                'message': 'Lesson created successfully',
                'data': lesson.to_dict()
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
    
    def get_lesson(self, lesson_id: str) -> Dict[str, Any]:
        """
        Get lesson by ID.
        
        Args:
            lesson_id: Lesson ID
            
        Returns:
            JSON response with lesson data
        """
        try:
            current_user = get_current_user()
            if not current_user:
                return jsonify({
                    'success': False,
                    'message': 'User not authenticated'
                }), 401
            
            lesson = self._lesson_service.get_lesson_by_id(lesson_id, current_user.id)
            if not lesson:
                return jsonify({
                    'success': False,
                    'message': f'Lesson with ID {lesson_id} not found'
                }), 404
            
            return jsonify({
                'success': True,
                'data': lesson.to_dict()
            }), 200
            
        except Exception as e:
            return jsonify({
                'success': False,
                'message': 'Internal server error',
                'error': str(e)
            }), 500
    
    def get_user_lessons(self) -> Dict[str, Any]:
        """
        Get lessons for current user.
        
        Returns:
            JSON response with lessons list
        """
        try:
            current_user = get_current_user()
            if not current_user:
                return jsonify({
                    'success': False,
                    'message': 'User not authenticated'
                }), 401
            
            # Get pagination parameters
            limit = request.args.get('limit', type=int)
            offset = request.args.get('offset', type=int)
            
            lessons = self._lesson_service.get_user_lessons(
                user_id=current_user.id,
                limit=limit,
                offset=offset
            )
            
            return jsonify({
                'success': True,
                'data': [lesson.to_dict() for lesson in lessons]
            }), 200
            
        except Exception as e:
            return jsonify({
                'success': False,
                'message': 'Internal server error',
                'error': str(e)
            }), 500
    
    def update_lesson(self, lesson_id: str) -> Dict[str, Any]:
        """
        Update lesson.
        
        Args:
            lesson_id: Lesson ID to update
            
        Returns:
            JSON response with updated lesson data
        """
        try:
            current_user = get_current_user()
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
            difficulty_level = None
            if 'difficulty_level' in data:
                difficulty_level = DifficultyLevel(data['difficulty_level'])
            
            # Update lesson
            lesson = self._lesson_service.update_lesson(
                lesson_id=lesson_id,
                user_id=current_user.id,
                title=data.get('title'),
                description=data.get('description'),
                difficulty_level=difficulty_level,
                estimated_duration=data.get('estimated_duration'),
                color_theme=data.get('color_theme'),
                author_name=data.get('author_name'),
                subject=data.get('subject'),
                grade_level=data.get('grade_level')
            )
            
            return jsonify({
                'success': True,
                'message': 'Lesson updated successfully',
                'data': lesson.to_dict()
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
    
    def delete_lesson(self, lesson_id: str) -> Dict[str, Any]:
        """
        Delete lesson.
        
        Args:
            lesson_id: Lesson ID to delete
            
        Returns:
            JSON response
        """
        try:
            current_user = get_current_user()
            if not current_user:
                return jsonify({
                    'success': False,
                    'message': 'User not authenticated'
                }), 401
            
            success = self._lesson_service.delete_lesson(lesson_id, current_user.id)
            
            if success:
                return jsonify({
                    'success': True,
                    'message': 'Lesson deleted successfully'
                }), 200
            else:
                return jsonify({
                    'success': False,
                    'message': 'Lesson not found'
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
    
    def change_lesson_status(self, lesson_id: str) -> Dict[str, Any]:
        """
        Change lesson status.
        
        Args:
            lesson_id: Lesson ID
            
        Returns:
            JSON response with updated lesson data
        """
        try:
            current_user = get_current_user()
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
            
            status = LessonStatus(data['status'])
            lesson = self._lesson_service.change_lesson_status(lesson_id, current_user.id, status)
            
            return jsonify({
                'success': True,
                'message': 'Lesson status updated successfully',
                'data': lesson.to_dict()
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
    
    def update_lesson_progress(self, lesson_id: str) -> Dict[str, Any]:
        """
        Update lesson progress.
        
        Args:
            lesson_id: Lesson ID
            
        Returns:
            JSON response with updated lesson data
        """
        try:
            current_user = get_current_user()
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
            lesson = self._lesson_service.update_lesson_progress(lesson_id, current_user.id, percentage)
            
            return jsonify({
                'success': True,
                'message': 'Lesson progress updated successfully',
                'data': lesson.to_dict()
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
    
    def toggle_favorite(self, lesson_id: str) -> Dict[str, Any]:
        """
        Toggle lesson favorite status.
        
        Args:
            lesson_id: Lesson ID
            
        Returns:
            JSON response with updated lesson data
        """
        try:
            current_user = get_current_user()
            if not current_user:
                return jsonify({
                    'success': False,
                    'message': 'User not authenticated'
                }), 401
            
            lesson = self._lesson_service.toggle_favorite(lesson_id, current_user.id)
            
            return jsonify({
                'success': True,
                'message': 'Lesson favorite status updated successfully',
                'data': lesson.to_dict()
            }), 200
            
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
    
    def search_lessons(self) -> Dict[str, Any]:
        """
        Search lessons.
        
        Returns:
            JSON response with matching lessons
        """
        try:
            current_user = get_current_user()
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
            lessons = self._lesson_service.search_lessons(current_user.id, query, limit=limit)
            
            return jsonify({
                'success': True,
                'data': [lesson.to_dict() for lesson in lessons]
            }), 200
            
        except Exception as e:
            return jsonify({
                'success': False,
                'message': 'Internal server error',
                'error': str(e)
            }), 500
    
    def get_lesson_statistics(self) -> Dict[str, Any]:
        """
        Get lesson statistics for current user.
        
        Returns:
            JSON response with lesson statistics
        """
        try:
            current_user = get_current_user()
            if not current_user:
                return jsonify({
                    'success': False,
                    'message': 'User not authenticated'
                }), 401
            
            statistics = self._lesson_service.get_lesson_statistics(current_user.id)
            
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
