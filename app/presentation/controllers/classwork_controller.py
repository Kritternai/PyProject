"""
Classwork Controller - HTTP Request Handling
"""

from typing import Dict, Any, List
from flask import request, jsonify, g, session
from ...application.services.classwork_service import (
    ClassworkTaskService,
    ClassworkMaterialService,
    ClassworkNoteService
)

class ClassworkTaskController:
    """Classwork Task Controller"""
    
    def __init__(self, task_service: ClassworkTaskService):
        self.task_service = task_service
    
    def create_task(self) -> Dict[str, Any]:
        """Create a new classwork task"""
        try:
            data = request.get_json()
            # Use default user for now
            user_id = '1'  # Default test user
            
            task = self.task_service.create_task(
                user_id=user_id,
                lesson_id=data['lesson_id'],
                title=data['title'],
                description=data.get('description'),
                subject=data.get('subject'),
                category=data.get('category'),
                priority=data.get('priority', 'medium'),
                status=data.get('status', 'todo'),
                due_date=data.get('due_date'),
                estimated_time=data.get('estimated_time', 0),
                actual_time=data.get('actual_time', 0)
            )
            
            return jsonify({
                'success': True,
                'message': 'Task created successfully',
                'task': task.to_dict()
            }), 201
            
        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'Error creating task: {str(e)}'
            }), 500
    
    def get_task(self, task_id: str) -> Dict[str, Any]:
        """Get task by ID"""
        try:
            user_id = session.get('user_id')
            if not user_id:
                return jsonify({'success': False, 'message': 'Please login first'}), 401
            task = self.task_service.get_task(task_id, user_id)
            
            if not task:
                return jsonify({
                    'success': False,
                    'message': 'Task not found'
                }), 404
            
            return jsonify({
                'success': True,
                'task': task.to_dict()
            })
            
        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'Error getting task: {str(e)}'
            }), 500
    
    def get_dashboard(self, lesson_id: str = None) -> Dict[str, Any]:
        """Get classwork dashboard for a specific lesson or all lessons"""
        try:
            # Use default user for now
            user_id = '1'  # Default test user
            
            # Get dashboard stats
            dashboard = self.task_service.get_dashboard(user_id, lesson_id)
            
            return jsonify({
                'success': True,
                'dashboard': dashboard
            })
            
        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'Error getting dashboard: {str(e)}'
            }), 500

    def get_lesson_tasks(self, lesson_id: str) -> Dict[str, Any]:
        """Get all tasks for a lesson"""
        try:
            # Use default user for now
            user_id = '1'  # Default test user
            tasks = self.task_service.get_lesson_tasks(lesson_id, user_id)
            
            return jsonify({
                'success': True,
                'tasks': [task.to_dict() for task in tasks]
            })
            
        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'Error getting tasks: {str(e)}'
            }), 500
    
    def update_task(self, task_id: str) -> Dict[str, Any]:
        """Update task"""
        try:
            data = request.get_json()
            user_id = g.user.id
            
            task = self.task_service.update_task(
                task_id=task_id,
                user_id=user_id,
                **data
            )
            
            if not task:
                return jsonify({
                    'success': False,
                    'message': 'Task not found'
                }), 404
            
            return jsonify({
                'success': True,
                'message': 'Task updated successfully',
                'task': task.to_dict()
            })
            
        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'Error updating task: {str(e)}'
            }), 500
    
    def delete_task(self, task_id: str) -> Dict[str, Any]:
        """Delete task"""
        try:
            user_id = g.user.id
            success = self.task_service.delete_task(task_id, user_id)
            
            if not success:
                return jsonify({
                    'success': False,
                    'message': 'Task not found'
                }), 404
            
            return jsonify({
                'success': True,
                'message': 'Task deleted successfully'
            })
            
        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'Error deleting task: {str(e)}'
            }), 500
    
    def mark_task_complete(self, task_id: str) -> Dict[str, Any]:
        """Mark task as complete"""
        try:
            user_id = g.user.id
            task = self.task_service.mark_task_complete(task_id, user_id)
            
            if not task:
                return jsonify({
                    'success': False,
                    'message': 'Task not found'
                }), 404
            
            return jsonify({
                'success': True,
                'message': 'Task marked as complete',
                'task': task.to_dict()
            })
            
        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'Error marking task complete: {str(e)}'
            }), 500
    
    def search_tasks(self) -> Dict[str, Any]:
        """Search tasks"""
        try:
            query = request.args.get('q', '')
            user_id = g.user.id
            tasks = self.task_service.search_tasks(query, user_id)
            
            return jsonify({
                'success': True,
                'tasks': [task.to_dict() for task in tasks]
            })
            
        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'Error searching tasks: {str(e)}'
            }), 500

class ClassworkMaterialController:
    """Classwork Material Controller"""
    
    def __init__(self, material_service: ClassworkMaterialService):
        self.material_service = material_service
    
    def create_material(self) -> Dict[str, Any]:
        """Create a new classwork material"""
        try:
            # Handle file upload
            if request.files:
                file = request.files.get('file')
                title = request.form.get('title')
                description = request.form.get('description')
                subject = request.form.get('subject')
                category = request.form.get('category')
                tags = request.form.get('tags', '').split(',') if request.form.get('tags') else []
                lesson_id = request.form.get('lesson_id')
                
                # Save file
                import os
                import uuid
                from werkzeug.utils import secure_filename
                
                if file and file.filename:
                    filename = secure_filename(file.filename)
                    unique_filename = f"{uuid.uuid4()}_{filename}"
                    upload_path = os.path.join('app', 'static', 'uploads', 'classwork')
                    os.makedirs(upload_path, exist_ok=True)
                    file_path = os.path.join(upload_path, unique_filename)
                    file.save(file_path)
                    
                    # Get file info
                    file_size = os.path.getsize(file_path)
                    file_extension = filename.split('.')[-1].lower()
                    
                    # Determine file type
                    file_type = 'document'
                    if file_extension in ['jpg', 'jpeg', 'png', 'gif']:
                        file_type = 'image'
                    elif file_extension in ['mp4', 'avi', 'mov']:
                        file_type = 'video'
                    elif file_extension in ['mp3', 'wav']:
                        file_type = 'audio'
                    elif file_extension in ['ppt', 'pptx']:
                        file_type = 'presentation'
                    elif file_extension in ['xls', 'xlsx']:
                        file_type = 'spreadsheet'
                    
                    data = {
                        'title': title,
                        'description': description,
                        'file_path': f'/static/uploads/classwork/{unique_filename}',
                        'file_type': file_type,
                        'file_size': file_size,
                        'subject': subject,
                        'category': category,
                        'tags': tags,
                        'lesson_id': lesson_id
                    }
                else:
                    return jsonify({'success': False, 'message': 'No file provided'}), 400
            else:
                data = request.get_json()
            
            # Use default user for now
            user_id = '1'  # Default test user
            
            material = self.material_service.create_material(
                user_id=user_id,
                lesson_id=data['lesson_id'],
                title=data['title'],
                description=data.get('description'),
                file_path=data.get('file_path'),
                file_type=data.get('file_type'),
                file_size=data.get('file_size'),
                subject=data.get('subject'),
                category=data.get('category'),
                tags=data.get('tags', []),
                task_id=data.get('task_id')
            )
            
            return jsonify({
                'success': True,
                'message': 'Material created successfully',
                'material': material.to_dict()
            }), 201
            
        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'Error creating material: {str(e)}'
            }), 500
    
    def get_lesson_materials(self, lesson_id: str) -> Dict[str, Any]:
        """Get all materials for a lesson"""
        try:
            # Use default user for now
            user_id = '1'  # Default test user
            materials = self.material_service.get_lesson_materials(lesson_id, user_id)
            
            return jsonify({
                'success': True,
                'materials': [material.to_dict() for material in materials]
            })
            
        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'Error getting materials: {str(e)}'
            }), 500

    def get_material(self, material_id: str) -> Dict[str, Any]:
        """Get material by ID"""
        try:
            user_id = session.get('user_id')
            if not user_id:
                return jsonify({'success': False, 'message': 'Please login first'}), 401
            material = self.material_service.get_material(material_id, user_id)
            
            if not material:
                return jsonify({
                    'success': False,
                    'message': 'Material not found'
                }), 404
            
            return jsonify({
                'success': True,
                'material': material.to_dict()
            })
            
        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'Error getting material: {str(e)}'
            }), 500
    
    
    def update_material(self, material_id: str) -> Dict[str, Any]:
        """Update material"""
        try:
            data = request.get_json()
            user_id = g.user.id
            
            material = self.material_service.update_material(
                material_id=material_id,
                user_id=user_id,
                **data
            )
            
            if not material:
                return jsonify({
                    'success': False,
                    'message': 'Material not found'
                }), 404
            
            return jsonify({
                'success': True,
                'message': 'Material updated successfully',
                'material': material.to_dict()
            })
            
        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'Error updating material: {str(e)}'
            }), 500
    
    def delete_material(self, material_id: str) -> Dict[str, Any]:
        """Delete material"""
        try:
            user_id = g.user.id
            success = self.material_service.delete_material(material_id, user_id)
            
            if not success:
                return jsonify({
                    'success': False,
                    'message': 'Material not found'
                }), 404
            
            return jsonify({
                'success': True,
                'message': 'Material deleted successfully'
            })
            
        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'Error deleting material: {str(e)}'
            }), 500
    
    def search_materials(self) -> Dict[str, Any]:
        """Search materials"""
        try:
            query = request.args.get('q', '')
            user_id = g.user.id
            materials = self.material_service.search_materials(query, user_id)
            
            return jsonify({
                'success': True,
                'materials': [material.to_dict() for material in materials]
            })
            
        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'Error searching materials: {str(e)}'
            }), 500

class ClassworkNoteController:
    """Classwork Note Controller"""
    
    def __init__(self, note_service: ClassworkNoteService):
        self.note_service = note_service
    
    def create_note(self) -> Dict[str, Any]:
        """Create a new classwork note"""
        try:
            data = request.get_json()
            user_id = g.user.id
            
            note = self.note_service.create_note(
                user_id=user_id,
                lesson_id=data['lesson_id'],
                title=data['title'],
                content=data.get('content'),
                subject=data.get('subject'),
                category=data.get('category'),
                tags=data.get('tags', []),
                task_id=data.get('task_id')
            )
            
            return jsonify({
                'success': True,
                'message': 'Note created successfully',
                'note': note.to_dict()
            }), 201
            
        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'Error creating note: {str(e)}'
            }), 500
    
    def get_note(self, note_id: str) -> Dict[str, Any]:
        """Get note by ID"""
        try:
            user_id = g.user.id
            note = self.note_service.get_note(note_id, user_id)
            
            if not note:
                return jsonify({
                    'success': False,
                    'message': 'Note not found'
                }), 404
            
            return jsonify({
                'success': True,
                'note': note.to_dict()
            })
            
        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'Error getting note: {str(e)}'
            }), 500
    
    def get_lesson_notes(self, lesson_id: str) -> Dict[str, Any]:
        """Get all notes for a lesson"""
        try:
            user_id = g.user.id
            notes = self.note_service.get_lesson_notes(lesson_id, user_id)
            
            return jsonify({
                'success': True,
                'notes': [note.to_dict() for note in notes]
            })
            
        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'Error getting notes: {str(e)}'
            }), 500
    
    def update_note(self, note_id: str) -> Dict[str, Any]:
        """Update note"""
        try:
            data = request.get_json()
            user_id = g.user.id
            
            note = self.note_service.update_note(
                note_id=note_id,
                user_id=user_id,
                **data
            )
            
            if not note:
                return jsonify({
                    'success': False,
                    'message': 'Note not found'
                }), 404
            
            return jsonify({
                'success': True,
                'message': 'Note updated successfully',
                'note': note.to_dict()
            })
            
        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'Error updating note: {str(e)}'
            }), 500
    
    def delete_note(self, note_id: str) -> Dict[str, Any]:
        """Delete note"""
        try:
            user_id = g.user.id
            success = self.note_service.delete_note(note_id, user_id)
            
            if not success:
                return jsonify({
                    'success': False,
                    'message': 'Note not found'
                }), 404
            
            return jsonify({
                'success': True,
                'message': 'Note deleted successfully'
            })
            
        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'Error deleting note: {str(e)}'
            }), 500
    
    def search_notes(self) -> Dict[str, Any]:
        """Search notes"""
        try:
            query = request.args.get('q', '')
            user_id = g.user.id
            notes = self.note_service.search_notes(query, user_id)
            
            return jsonify({
                'success': True,
                'notes': [note.to_dict() for note in notes]
            })
            
        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'Error searching notes: {str(e)}'
            }), 500
