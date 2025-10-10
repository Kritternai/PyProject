"""
Note controller following Clean Architecture principles.
Handles HTTP requests and responses for note operations.
"""

from flask import request, jsonify, g
from typing import Dict, Any, Optional
from app.services import NoteService
from app.utils.exceptions import (
    ValidationException,
    NotFoundException,
    BusinessLogicException,
    AuthorizationException
)
from ..middleware import login_required


class NoteController:
    """
    Controller for note-related HTTP operations.
    Handles request/response logic and delegates business logic to services.
    """
    
    def __init__(self):
        """Initialize controller with service dependencies."""
        self._note_service = NoteService()
    
    def create_note(self) -> Dict[str, Any]:
        """
        Create a new note.
        
        Returns:
            JSON response with created note data
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
            required_fields = ['title', 'content']
            for field in required_fields:
                if field not in data or not data[field]:
                    return jsonify({
                        'success': False,
                        'message': f'{field} is required'
                    }), 400
            
            # Parse note type (MVC - use string directly)
            note_type = data.get('note_type', 'text')
            
            # Create note
            note = self._note_service.create_note(
                user_id=current_user.id,
                title=data['title'],
                content=data['content'],
                note_type=note_type,
                lesson_id=data.get('lesson_id'),
                section_id=data.get('section_id'),
                tags=data.get('tags'),
                is_public=data.get('is_public', False)
            )
            
            return jsonify({
                'success': True,
                'message': 'Note created successfully',
                'data': note.to_dict()
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
    
    def get_note(self, note_id: str) -> Dict[str, Any]:
        """
        Get note by ID.
        
        Args:
            note_id: Note ID
            
        Returns:
            JSON response with note data
        """
        try:
            current_user = g.user
            if not current_user:
                return jsonify({
                    'success': False,
                    'message': 'User not authenticated'
                }), 401
            
            note = self._note_service.get_note_by_id(note_id, current_user.id)
            if not note:
                return jsonify({
                    'success': False,
                    'message': f'Note with ID {note_id} not found'
                }), 404
            
            # Increment view count
            self._note_service.increment_view_count(note_id)
            
            return jsonify({
                'success': True,
                'data': note.to_dict()
            }), 200
            
        except Exception as e:
            return jsonify({
                'success': False,
                'message': 'Internal server error',
                'error': str(e)
            }), 500
    
    def get_user_notes(self) -> Dict[str, Any]:
        """
        Get notes for current user.
        
        Returns:
            JSON response with notes list
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
            
            notes = self._note_service.get_user_notes(
                user_id=current_user.id,
                limit=limit,
                offset=offset
            )
            
            return jsonify({
                'success': True,
                'data': [note.to_dict() for note in notes]
            }), 200
            
        except Exception as e:
            return jsonify({
                'success': False,
                'message': 'Internal server error',
                'error': str(e)
            }), 500
    
    def update_note(self, note_id: str) -> Dict[str, Any]:
        """
        Update note.
        
        Args:
            note_id: Note ID to update
            
        Returns:
            JSON response with updated note data
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
            
            # Parse enum if provided
            # Note type (MVC - use string directly)
            note_type = None
            if 'note_type' in data:
                note_type = data['note_type']
            
            # Update note
            note = self._note_service.update_note(
                note_id=note_id,
                user_id=current_user.id,
                title=data.get('title'),
                content=data.get('content'),
                note_type=note_type,
                lesson_id=data.get('lesson_id'),
                section_id=data.get('section_id'),
                tags=data.get('tags'),
                is_public=data.get('is_public')
            )
            
            return jsonify({
                'success': True,
                'message': 'Note updated successfully',
                'data': note.to_dict()
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
    
    def delete_note(self, note_id: str) -> Dict[str, Any]:
        """
        Delete note.
        
        Args:
            note_id: Note ID to delete
            
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
            
            success = self._note_service.delete_note(note_id, current_user.id)
            
            if success:
                return jsonify({
                    'success': True,
                    'message': 'Note deleted successfully'
                }), 200
            else:
                return jsonify({
                    'success': False,
                    'message': 'Note not found'
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
    
    def get_notes_by_lesson(self, lesson_id: str) -> Dict[str, Any]:
        """
        Get notes for a specific lesson.
        
        Args:
            lesson_id: Lesson ID
            
        Returns:
            JSON response with notes list
        """
        try:
            current_user = g.user
            if not current_user:
                return jsonify({
                    'success': False,
                    'message': 'User not authenticated'
                }), 401
            
            limit = request.args.get('limit', type=int)
            notes = self._note_service.get_notes_by_lesson(lesson_id, current_user.id, limit=limit)
            
            return jsonify({
                'success': True,
                'data': [note.to_dict() for note in notes]
            }), 200
            
        except Exception as e:
            return jsonify({
                'success': False,
                'message': 'Internal server error',
                'error': str(e)
            }), 500
    
    def get_notes_by_section(self, section_id: str) -> Dict[str, Any]:
        """
        Get notes for a specific section.
        
        Args:
            section_id: Section ID
            
        Returns:
            JSON response with notes list
        """
        try:
            current_user = g.user
            if not current_user:
                return jsonify({
                    'success': False,
                    'message': 'User not authenticated'
                }), 401
            
            limit = request.args.get('limit', type=int)
            notes = self._note_service.get_notes_by_section(section_id, current_user.id, limit=limit)
            
            return jsonify({
                'success': True,
                'data': [note.to_dict() for note in notes]
            }), 200
            
        except Exception as e:
            return jsonify({
                'success': False,
                'message': 'Internal server error',
                'error': str(e)
            }), 500
    
    def search_notes(self) -> Dict[str, Any]:
        """
        Search notes.
        
        Returns:
            JSON response with matching notes
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
            notes = self._note_service.search_notes(current_user.id, query, limit=limit)
            
            return jsonify({
                'success': True,
                'data': [note.to_dict() for note in notes]
            }), 200
            
        except Exception as e:
            return jsonify({
                'success': False,
                'message': 'Internal server error',
                'error': str(e)
            }), 500
    
    def search_notes_by_tags(self) -> Dict[str, Any]:
        """
        Search notes by tags.
        
        Returns:
            JSON response with matching notes
        """
        try:
            current_user = g.user
            if not current_user:
                return jsonify({
                    'success': False,
                    'message': 'User not authenticated'
                }), 401
            
            tags = request.args.getlist('tags')
            if not tags:
                return jsonify({
                    'success': False,
                    'message': 'Tags are required'
                }), 400
            
            limit = request.args.get('limit', type=int)
            notes = self._note_service.search_notes_by_tags(current_user.id, tags, limit=limit)
            
            return jsonify({
                'success': True,
                'data': [note.to_dict() for note in notes]
            }), 200
            
        except Exception as e:
            return jsonify({
                'success': False,
                'message': 'Internal server error',
                'error': str(e)
            }), 500
    
    def get_public_notes(self) -> Dict[str, Any]:
        """
        Get public notes.
        
        Returns:
            JSON response with public notes
        """
        try:
            limit = request.args.get('limit', type=int)
            offset = request.args.get('offset', type=int)
            notes = self._note_service.get_public_notes(limit=limit, offset=offset)
            
            return jsonify({
                'success': True,
                'data': [note.to_dict() for note in notes]
            }), 200
            
        except Exception as e:
            return jsonify({
                'success': False,
                'message': 'Internal server error',
                'error': str(e)
            }), 500
    
    def toggle_public_status(self, note_id: str) -> Dict[str, Any]:
        """
        Toggle note public status.
        
        Args:
            note_id: Note ID
            
        Returns:
            JSON response with updated note data
        """
        try:
            current_user = g.user
            if not current_user:
                return jsonify({
                    'success': False,
                    'message': 'User not authenticated'
                }), 401
            
            note = self._note_service.toggle_public_status(note_id, current_user.id)
            
            return jsonify({
                'success': True,
                'message': 'Note public status updated successfully',
                'data': note.to_dict()
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
    
    def add_tag(self, note_id: str) -> Dict[str, Any]:
        """
        Add tag to note.
        
        Args:
            note_id: Note ID
            
        Returns:
            JSON response with updated note data
        """
        try:
            current_user = g.user
            if not current_user:
                return jsonify({
                    'success': False,
                    'message': 'User not authenticated'
                }), 401
            
            data = request.get_json()
            if not data or 'tag' not in data:
                return jsonify({
                    'success': False,
                    'message': 'Tag is required'
                }), 400
            
            tag = data['tag']
            note = self._note_service.add_tag(note_id, current_user.id, tag)
            
            return jsonify({
                'success': True,
                'message': 'Tag added successfully',
                'data': note.to_dict()
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
    
    def remove_tag(self, note_id: str) -> Dict[str, Any]:
        """
        Remove tag from note.
        
        Args:
            note_id: Note ID
            
        Returns:
            JSON response with updated note data
        """
        try:
            current_user = g.user
            if not current_user:
                return jsonify({
                    'success': False,
                    'message': 'User not authenticated'
                }), 401
            
            data = request.get_json()
            if not data or 'tag' not in data:
                return jsonify({
                    'success': False,
                    'message': 'Tag is required'
                }), 400
            
            tag = data['tag']
            note = self._note_service.remove_tag(note_id, current_user.id, tag)
            
            return jsonify({
                'success': True,
                'message': 'Tag removed successfully',
                'data': note.to_dict()
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
    
    def get_note_statistics(self) -> Dict[str, Any]:
        """
        Get note statistics for current user.
        
        Returns:
            JSON response with note statistics
        """
        try:
            current_user = g.user
            if not current_user:
                return jsonify({
                    'success': False,
                    'message': 'User not authenticated'
                }), 401
            
            statistics = self._note_service.get_note_statistics(current_user.id)
            
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
    
    def get_recent_notes(self) -> Dict[str, Any]:
        """
        Get recent notes for current user.
        
        Returns:
            JSON response with recent notes
        """
        try:
            current_user = g.user
            if not current_user:
                return jsonify({
                    'success': False,
                    'message': 'User not authenticated'
                }), 401
            
            limit = request.args.get('limit', 10, type=int)
            notes = self._note_service.get_recent_notes(current_user.id, limit=limit)
            
            return jsonify({
                'success': True,
                'data': [note.to_dict() for note in notes]
            }), 200
            
        except Exception as e:
            return jsonify({
                'success': False,
                'message': 'Internal server error',
                'error': str(e)
            }), 500
    
    def get_most_viewed_notes(self) -> Dict[str, Any]:
        """
        Get most viewed notes for current user.
        
        Returns:
            JSON response with most viewed notes
        """
        try:
            current_user = g.user
            if not current_user:
                return jsonify({
                    'success': False,
                    'message': 'User not authenticated'
                }), 401
            
            limit = request.args.get('limit', 10, type=int)
            notes = self._note_service.get_most_viewed_notes(current_user.id, limit=limit)
            
            return jsonify({
                'success': True,
                'data': [note.to_dict() for note in notes]
            }), 200
            
        except Exception as e:
            return jsonify({
                'success': False,
                'message': 'Internal server error',
                'error': str(e)
            }), 500
    
    def get_all_user_tags(self) -> Dict[str, Any]:
        """
        Get all unique tags for current user.
        
        Returns:
            JSON response with tags list
        """
        try:
            current_user = g.user
            if not current_user:
                return jsonify({
                    'success': False,
                    'message': 'User not authenticated'
                }), 401
            
            tags = self._note_service.get_all_user_tags(current_user.id)
            
            return jsonify({
                'success': True,
                'data': tags
            }), 200
            
        except Exception as e:
            return jsonify({
                'success': False,
                'message': 'Internal server error',
                'error': str(e)
            }), 500
