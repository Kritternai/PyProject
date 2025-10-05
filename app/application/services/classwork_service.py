"""
Classwork Service - Business Logic
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid
from ...domain.entities.classwork_task import ClassworkTask, TaskStatus, TaskPriority
from ...domain.entities.classwork_material import ClassworkMaterial, MaterialType
from ...domain.entities.classwork_note import ClassworkNote
from ...domain.interfaces.classwork_repository import (
    ClassworkTaskRepository,
    ClassworkMaterialRepository,
    ClassworkNoteRepository
)

class ClassworkTaskService:
    """Classwork Task Service"""
    
    def __init__(self, task_repository: ClassworkTaskRepository):
        self.task_repository = task_repository
    
    def create_task(self, user_id: str, lesson_id: str, title: str, **kwargs) -> ClassworkTask:
        """Create a new classwork task"""
        task = ClassworkTask(
            id=str(uuid.uuid4()),
            user_id=user_id,
            lesson_id=lesson_id,
            title=title,
            description=kwargs.get('description'),
            subject=kwargs.get('subject'),
            category=kwargs.get('category'),
            priority=TaskPriority(kwargs.get('priority', 'medium')),
            status=TaskStatus(kwargs.get('status', 'todo')),
            due_date=datetime.fromisoformat(kwargs['due_date']) if kwargs.get('due_date') else None,
            estimated_time=int(kwargs.get('estimated_time', 0)) if kwargs.get('estimated_time') else 0,
            actual_time=int(kwargs.get('actual_time', 0)) if kwargs.get('actual_time') else 0
        )
        
        return self.task_repository.create_task(task)
    
    def get_task(self, task_id: str, user_id: str) -> Optional[ClassworkTask]:
        """Get task by ID"""
        return self.task_repository.get_task_by_id(task_id, user_id)
    
    def get_dashboard(self, user_id: str, lesson_id: str = None) -> Dict[str, Any]:
        """Get dashboard statistics for a specific lesson or all lessons"""
        try:
            if lesson_id:
                # Get tasks for specific lesson only
                all_tasks = self.task_repository.get_tasks_by_lesson(lesson_id, user_id)
            else:
                # Get all tasks for user
                all_tasks = self.task_repository.get_user_tasks(user_id)
            
            # Calculate statistics
            total_tasks = len(all_tasks)
            completed_tasks = len([t for t in all_tasks if t.status == TaskStatus.DONE])
            in_progress_tasks = len([t for t in all_tasks if t.status == TaskStatus.IN_PROGRESS])
            
            # Calculate overdue tasks
            from datetime import datetime
            now = datetime.now()
            overdue_tasks = len([t for t in all_tasks 
                                if t.due_date and t.due_date < now and t.status != TaskStatus.DONE])
            
            return {
                'total_tasks': total_tasks,
                'completed_tasks': completed_tasks,
                'in_progress_tasks': in_progress_tasks,
                'overdue_tasks': overdue_tasks
            }
        except Exception as e:
            print(f"Error getting dashboard: {e}")
            return {
                'total_tasks': 0,
                'completed_tasks': 0,
                'in_progress_tasks': 0,
                'overdue_tasks': 0
            }

    def get_lesson_tasks(self, lesson_id: str, user_id: str) -> List[ClassworkTask]:
        """Get all tasks for a lesson"""
        return self.task_repository.get_tasks_by_lesson(lesson_id, user_id)
    
    def get_tasks_by_status(self, status: str, user_id: str) -> List[ClassworkTask]:
        """Get tasks by status"""
        return self.task_repository.get_tasks_by_status(TaskStatus(status), user_id)
    
    def get_tasks_by_priority(self, priority: str, user_id: str) -> List[ClassworkTask]:
        """Get tasks by priority"""
        return self.task_repository.get_tasks_by_priority(TaskPriority(priority), user_id)
    
    def get_overdue_tasks(self, user_id: str) -> List[ClassworkTask]:
        """Get overdue tasks"""
        return self.task_repository.get_overdue_tasks(user_id)
    
    def get_due_soon_tasks(self, user_id: str, hours: int = 24) -> List[ClassworkTask]:
        """Get tasks due soon"""
        return self.task_repository.get_due_soon_tasks(user_id, hours)
    
    def update_task(self, task_id: str, user_id: str, **kwargs) -> Optional[ClassworkTask]:
        """Update task"""
        task = self.task_repository.get_task_by_id(task_id, user_id)
        if not task:
            return None
        
        # Update fields
        if 'title' in kwargs:
            task.title = kwargs['title']
        if 'description' in kwargs:
            task.description = kwargs['description']
        if 'subject' in kwargs:
            task.subject = kwargs['subject']
        if 'category' in kwargs:
            task.category = kwargs['category']
        if 'priority' in kwargs:
            task.priority = TaskPriority(kwargs['priority'])
        if 'status' in kwargs:
            task.status = TaskStatus(kwargs['status'])
        if 'due_date' in kwargs:
            task.due_date = datetime.fromisoformat(kwargs['due_date']) if kwargs['due_date'] else None
        if 'estimated_time' in kwargs:
            task.estimated_time = kwargs['estimated_time']
        if 'actual_time' in kwargs:
            task.actual_time = kwargs['actual_time']
        
        task.updated_at = datetime.now()
        return self.task_repository.update_task(task)
    
    def delete_task(self, task_id: str, user_id: str) -> bool:
        """Delete task"""
        return self.task_repository.delete_task(task_id, user_id)
    
    def search_tasks(self, query: str, user_id: str) -> List[ClassworkTask]:
        """Search tasks"""
        return self.task_repository.search_tasks(query, user_id)
    
    def mark_task_complete(self, task_id: str, user_id: str) -> Optional[ClassworkTask]:
        """Mark task as complete"""
        task = self.task_repository.get_task_by_id(task_id, user_id)
        if not task:
            return None
        
        task.update_status(TaskStatus.DONE)
        return self.task_repository.update_task(task)
    
    def add_time_spent(self, task_id: str, user_id: str, minutes: int) -> Optional[ClassworkTask]:
        """Add time spent on task"""
        task = self.task_repository.get_task_by_id(task_id, user_id)
        if not task:
            return None
        
        task.add_time_spent(minutes)
        return self.task_repository.update_task(task)

class ClassworkMaterialService:
    """Classwork Material Service"""
    
    def __init__(self, material_repository: ClassworkMaterialRepository):
        self.material_repository = material_repository
    
    def create_material(self, user_id: str, lesson_id: str, title: str, **kwargs) -> ClassworkMaterial:
        """Create a new classwork material"""
        material = ClassworkMaterial(
            id=str(uuid.uuid4()),
            user_id=user_id,
            lesson_id=lesson_id,
            task_id=kwargs.get('task_id'),
            title=title,
            description=kwargs.get('description'),
            file_path=kwargs.get('file_path'),
            file_type=MaterialType(kwargs['file_type']) if kwargs.get('file_type') else None,
            file_size=kwargs.get('file_size'),
            subject=kwargs.get('subject'),
            category=kwargs.get('category'),
            tags=kwargs.get('tags', [])
        )
        
        return self.material_repository.create_material(material)
    
    def get_lesson_materials(self, lesson_id: str, user_id: str) -> List[ClassworkMaterial]:
        """Get all materials for a lesson"""
        return self.material_repository.get_materials_by_lesson(lesson_id, user_id)

    def get_material(self, material_id: str, user_id: str) -> Optional[ClassworkMaterial]:
        """Get material by ID"""
        return self.material_repository.get_material_by_id(material_id, user_id)
    
    def get_task_materials(self, task_id: str, user_id: str) -> List[ClassworkMaterial]:
        """Get materials for a task"""
        return self.material_repository.get_materials_by_task(task_id, user_id)
    
    def get_materials_by_type(self, material_type: str, user_id: str) -> List[ClassworkMaterial]:
        """Get materials by type"""
        return self.material_repository.get_materials_by_type(MaterialType(material_type), user_id)
    
    def get_materials_by_subject(self, subject: str, user_id: str) -> List[ClassworkMaterial]:
        """Get materials by subject"""
        return self.material_repository.get_materials_by_subject(subject, user_id)
    
    def update_material(self, material_id: str, user_id: str, **kwargs) -> Optional[ClassworkMaterial]:
        """Update material"""
        material = self.material_repository.get_material_by_id(material_id, user_id)
        if not material:
            return None
        
        # Update fields
        if 'title' in kwargs:
            material.title = kwargs['title']
        if 'description' in kwargs:
            material.description = kwargs['description']
        if 'file_path' in kwargs:
            material.file_path = kwargs['file_path']
        if 'file_type' in kwargs:
            material.file_type = MaterialType(kwargs['file_type'])
        if 'file_size' in kwargs:
            material.file_size = kwargs['file_size']
        if 'subject' in kwargs:
            material.subject = kwargs['subject']
        if 'category' in kwargs:
            material.category = kwargs['category']
        if 'tags' in kwargs:
            material.tags = kwargs['tags']
        
        material.updated_at = datetime.now()
        return self.material_repository.update_material(material)
    
    def delete_material(self, material_id: str, user_id: str) -> bool:
        """Delete material"""
        return self.material_repository.delete_material(material_id, user_id)
    
    def search_materials(self, query: str, user_id: str) -> List[ClassworkMaterial]:
        """Search materials"""
        return self.material_repository.search_materials(query, user_id)
    
    def add_tag(self, material_id: str, user_id: str, tag: str) -> Optional[ClassworkMaterial]:
        """Add tag to material"""
        material = self.material_repository.get_material_by_id(material_id, user_id)
        if not material:
            return None
        
        material.add_tag(tag)
        return self.material_repository.update_material(material)
    
    def remove_tag(self, material_id: str, user_id: str, tag: str) -> Optional[ClassworkMaterial]:
        """Remove tag from material"""
        material = self.material_repository.get_material_by_id(material_id, user_id)
        if not material:
            return None
        
        material.remove_tag(tag)
        return self.material_repository.update_material(material)

class ClassworkNoteService:
    """Classwork Note Service"""
    
    def __init__(self, note_repository: ClassworkNoteRepository):
        self.note_repository = note_repository
    
    def create_note(self, user_id: str, lesson_id: str, title: str, **kwargs) -> ClassworkNote:
        """Create a new classwork note"""
        note = ClassworkNote(
            id=kwargs.get('id'),
            user_id=user_id,
            lesson_id=lesson_id,
            task_id=kwargs.get('task_id'),
            title=title,
            content=kwargs.get('content'),
            subject=kwargs.get('subject'),
            category=kwargs.get('category'),
            tags=kwargs.get('tags', [])
        )
        
        return self.note_repository.create_note(note)
    
    def get_note(self, note_id: str, user_id: str) -> Optional[ClassworkNote]:
        """Get note by ID"""
        return self.note_repository.get_note_by_id(note_id, user_id)
    
    def get_lesson_notes(self, lesson_id: str, user_id: str) -> List[ClassworkNote]:
        """Get all notes for a lesson"""
        return self.note_repository.get_notes_by_lesson(lesson_id, user_id)
    
    def get_task_notes(self, task_id: str, user_id: str) -> List[ClassworkNote]:
        """Get notes for a task"""
        return self.note_repository.get_notes_by_task(task_id, user_id)
    
    def get_notes_by_subject(self, subject: str, user_id: str) -> List[ClassworkNote]:
        """Get notes by subject"""
        return self.note_repository.get_notes_by_subject(subject, user_id)
    
    def update_note(self, note_id: str, user_id: str, **kwargs) -> Optional[ClassworkNote]:
        """Update note"""
        note = self.note_repository.get_note_by_id(note_id, user_id)
        if not note:
            return None
        
        # Update fields
        if 'title' in kwargs:
            note.title = kwargs['title']
        if 'content' in kwargs:
            note.content = kwargs['content']
        if 'subject' in kwargs:
            note.subject = kwargs['subject']
        if 'category' in kwargs:
            note.category = kwargs['category']
        if 'tags' in kwargs:
            note.tags = kwargs['tags']
        
        note.updated_at = datetime.now()
        return self.note_repository.update_note(note)
    
    def delete_note(self, note_id: str, user_id: str) -> bool:
        """Delete note"""
        return self.note_repository.delete_note(note_id, user_id)
    
    def search_notes(self, query: str, user_id: str) -> List[ClassworkNote]:
        """Search notes"""
        return self.note_repository.search_notes(query, user_id)
    
    def add_tag(self, note_id: str, user_id: str, tag: str) -> Optional[ClassworkNote]:
        """Add tag to note"""
        note = self.note_repository.get_note_by_id(note_id, user_id)
        if not note:
            return None
        
        note.add_tag(tag)
        return self.note_repository.update_note(note)
    
    def remove_tag(self, note_id: str, user_id: str, tag: str) -> Optional[ClassworkNote]:
        """Remove tag from note"""
        note = self.note_repository.get_note_by_id(note_id, user_id)
        if not note:
            return None
        
        note.remove_tag(tag)
        return self.note_repository.update_note(note)
