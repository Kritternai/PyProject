"""
Classwork Repository Implementation
"""

from typing import List, Optional
from datetime import datetime
from sqlalchemy import text
from flask import current_app
from ...domain.entities.classwork_task import ClassworkTask, TaskStatus, TaskPriority
from ...domain.entities.classwork_material import ClassworkMaterial, MaterialType
from ...domain.entities.classwork_note import ClassworkNote
from ...domain.interfaces.classwork_repository import (
    ClassworkTaskRepository,
    ClassworkMaterialRepository,
    ClassworkNoteRepository
)

class ClassworkTaskRepositoryImpl(ClassworkTaskRepository):
    """Classwork Task Repository Implementation"""
    
    def __init__(self, db):
        self.db = db
    
    def create_task(self, task: ClassworkTask) -> ClassworkTask:
        """Create a new classwork task"""
        try:
            query = text("""
                INSERT INTO classwork_task (
                    id, user_id, lesson_id, title, description, subject, category,
                    priority, status, due_date, estimated_time, actual_time,
                    created_at, updated_at
                ) VALUES (
                    :id, :user_id, :lesson_id, :title, :description, :subject, :category,
                    :priority, :status, :due_date, :estimated_time, :actual_time,
                    :created_at, :updated_at
                )
            """)
            
            self.db.session.execute(query, {
                'id': task.id,
                'user_id': task.user_id,
                'lesson_id': task.lesson_id,
                'title': task.title,
                'description': task.description,
                'subject': task.subject,
                'category': task.category,
                'priority': task.priority.value,
                'status': task.status.value,
                'due_date': task.due_date.isoformat() if task.due_date else None,
                'estimated_time': task.estimated_time,
                'actual_time': task.actual_time,
                'created_at': task.created_at.isoformat() if task.created_at else None,
                'updated_at': task.updated_at.isoformat() if task.updated_at else None
            })
            
            self.db.session.commit()
            return task
            
        except Exception as e:
            self.db.session.rollback()
            raise e
    
    def get_task_by_id(self, task_id: str, user_id: str) -> Optional[ClassworkTask]:
        """Get task by ID"""
        try:
            query = text("""
                SELECT * FROM classwork_task 
                WHERE id = :task_id AND user_id = :user_id
            """)
            
            result = self.db.session.execute(query, {
                'task_id': task_id,
                'user_id': user_id
            }).fetchone()
            
            if result:
                return self._row_to_task(result)
            return None
            
        except Exception as e:
            raise e
    
    def get_user_tasks(self, user_id: str) -> List[ClassworkTask]:
        """Get all tasks for a user"""
        try:
            query = text("""
                SELECT * FROM classwork_task 
                WHERE user_id = :user_id
                ORDER BY created_at DESC
            """)
            
            result = self.db.session.execute(query, {
                'user_id': user_id
            }).fetchall()
            
            return [self._row_to_task(row) for row in result]
            
        except Exception as e:
            raise e

    def get_tasks_by_lesson(self, lesson_id: str, user_id: str) -> List[ClassworkTask]:
        """Get all tasks for a lesson"""
        try:
            query = text("""
                SELECT * FROM classwork_task 
                WHERE lesson_id = :lesson_id AND user_id = :user_id
                ORDER BY created_at DESC
            """)
            
            result = self.db.session.execute(query, {
                'lesson_id': lesson_id,
                'user_id': user_id
            }).fetchall()
            
            return [self._row_to_task(row) for row in result]
            
        except Exception as e:
            raise e
    
    def get_tasks_by_status(self, status: TaskStatus, user_id: str) -> List[ClassworkTask]:
        """Get tasks by status"""
        try:
            query = text("""
                SELECT * FROM classwork_task 
                WHERE status = :status AND user_id = :user_id
                ORDER BY created_at DESC
            """)
            
            result = self.db.session.execute(query, {
                'status': status.value,
                'user_id': user_id
            }).fetchall()
            
            return [self._row_to_task(row) for row in result]
            
        except Exception as e:
            raise e
    
    def get_tasks_by_priority(self, priority: TaskPriority, user_id: str) -> List[ClassworkTask]:
        """Get tasks by priority"""
        try:
            query = text("""
                SELECT * FROM classwork_task 
                WHERE priority = :priority AND user_id = :user_id
                ORDER BY created_at DESC
            """)
            
            result = self.db.session.execute(query, {
                'priority': priority.value,
                'user_id': user_id
            }).fetchall()
            
            return [self._row_to_task(row) for row in result]
            
        except Exception as e:
            raise e
    
    def get_overdue_tasks(self, user_id: str) -> List[ClassworkTask]:
        """Get overdue tasks"""
        try:
            query = text("""
                SELECT * FROM classwork_task 
                WHERE user_id = :user_id 
                AND due_date < datetime('now') 
                AND status != 'done'
                ORDER BY due_date ASC
            """)
            
            result = self.db.session.execute(query, {'user_id': user_id}).fetchall()
            return [self._row_to_task(row) for row in result]
            
        except Exception as e:
            raise e
    
    def get_due_soon_tasks(self, user_id: str, hours: int = 24) -> List[ClassworkTask]:
        """Get tasks due soon"""
        try:
            query = text("""
                SELECT * FROM classwork_task 
                WHERE user_id = :user_id 
                AND due_date BETWEEN datetime('now') AND datetime('now', '+{} hours')
                AND status != 'done'
                ORDER BY due_date ASC
            """.format(hours))
            
            result = self.db.session.execute(query, {'user_id': user_id}).fetchall()
            return [self._row_to_task(row) for row in result]
            
        except Exception as e:
            raise e
    
    def update_task(self, task: ClassworkTask) -> ClassworkTask:
        """Update task"""
        try:
            query = text("""
                UPDATE classwork_task SET
                    title = :title,
                    description = :description,
                    subject = :subject,
                    category = :category,
                    priority = :priority,
                    status = :status,
                    due_date = :due_date,
                    estimated_time = :estimated_time,
                    actual_time = :actual_time,
                    updated_at = :updated_at
                WHERE id = :id AND user_id = :user_id
            """)
            
            self.db.session.execute(query, {
                'id': task.id,
                'user_id': task.user_id,
                'title': task.title,
                'description': task.description,
                'subject': task.subject,
                'category': task.category,
                'priority': task.priority.value,
                'status': task.status.value,
                'due_date': task.due_date.isoformat() if task.due_date else None,
                'estimated_time': task.estimated_time,
                'actual_time': task.actual_time,
                'updated_at': task.updated_at.isoformat() if task.updated_at else None
            })
            
            self.db.session.commit()
            return task
            
        except Exception as e:
            self.db.session.rollback()
            raise e
    
    def delete_task(self, task_id: str, user_id: str) -> bool:
        """Delete task"""
        try:
            query = text("""
                DELETE FROM classwork_task 
                WHERE id = :task_id AND user_id = :user_id
            """)
            
            result = self.db.session.execute(query, {
                'task_id': task_id,
                'user_id': user_id
            })
            
            self.db.session.commit()
            return result.rowcount > 0
            
        except Exception as e:
            self.db.session.rollback()
            raise e
    
    def search_tasks(self, query: str, user_id: str) -> List[ClassworkTask]:
        """Search tasks"""
        try:
            search_query = text("""
                SELECT * FROM classwork_task 
                WHERE user_id = :user_id 
                AND (title LIKE :query OR description LIKE :query OR subject LIKE :query)
                ORDER BY created_at DESC
            """)
            
            result = self.db.session.execute(search_query, {
                'user_id': user_id,
                'query': f'%{query}%'
            }).fetchall()
            
            return [self._row_to_task(row) for row in result]
            
        except Exception as e:
            raise e
    
    def _row_to_task(self, row) -> ClassworkTask:
        """Convert database row to ClassworkTask"""
        return ClassworkTask(
            id=row.id,
            user_id=row.user_id,
            lesson_id=row.lesson_id,
            title=row.title,
            description=row.description,
            subject=row.subject,
            category=row.category,
            priority=TaskPriority(row.priority),
            status=TaskStatus(row.status),
            due_date=datetime.fromisoformat(row.due_date) if row.due_date else None,
            estimated_time=row.estimated_time,
            actual_time=row.actual_time,
            created_at=datetime.fromisoformat(row.created_at) if row.created_at else None,
            updated_at=datetime.fromisoformat(row.updated_at) if row.updated_at else None
        )

class ClassworkMaterialRepositoryImpl(ClassworkMaterialRepository):
    """Classwork Material Repository Implementation"""
    
    def __init__(self, db):
        self.db = db
    
    def create_material(self, material: ClassworkMaterial) -> ClassworkMaterial:
        """Create a new classwork material"""
        try:
            query = text("""
                INSERT INTO classwork_material (
                    id, user_id, lesson_id, task_id, title, description, file_path,
                    file_type, file_size, subject, category, tags, created_at, updated_at
                ) VALUES (
                    :id, :user_id, :lesson_id, :task_id, :title, :description, :file_path,
                    :file_type, :file_size, :subject, :category, :tags, :created_at, :updated_at
                )
            """)
            
            self.db.session.execute(query, {
                'id': material.id,
                'user_id': material.user_id,
                'lesson_id': material.lesson_id,
                'task_id': material.task_id,
                'title': material.title,
                'description': material.description,
                'file_path': material.file_path,
                'file_type': material.file_type.value if material.file_type else None,
                'file_size': material.file_size,
                'subject': material.subject,
                'category': material.category,
                'tags': ','.join(material.tags) if material.tags else None,
                'created_at': material.created_at.isoformat() if material.created_at else None,
                'updated_at': material.updated_at.isoformat() if material.updated_at else None
            })
            
            self.db.session.commit()
            return material
            
        except Exception as e:
            self.db.session.rollback()
            raise e
    
    def get_materials_by_lesson(self, lesson_id: str, user_id: str) -> List[ClassworkMaterial]:
        """Get all materials for a lesson"""
        try:
            query = text("""
                SELECT * FROM classwork_material 
                WHERE lesson_id = :lesson_id AND user_id = :user_id
                ORDER BY created_at DESC
            """)
            
            result = self.db.session.execute(query, {
                'lesson_id': lesson_id,
                'user_id': user_id
            }).fetchall()
            
            return [self._row_to_material(row) for row in result]
            
        except Exception as e:
            raise e

    def get_material_by_id(self, material_id: str, user_id: str) -> Optional[ClassworkMaterial]:
        """Get material by ID"""
        try:
            query = text("""
                SELECT * FROM classwork_material 
                WHERE id = :material_id AND user_id = :user_id
            """)
            
            result = self.db.session.execute(query, {
                'material_id': material_id,
                'user_id': user_id
            }).fetchone()
            
            if result:
                return self._row_to_material(result)
            return None
            
        except Exception as e:
            raise e
    
    def get_materials_by_task(self, task_id: str, user_id: str) -> List[ClassworkMaterial]:
        """Get materials for a task"""
        try:
            query = text("""
                SELECT * FROM classwork_material 
                WHERE task_id = :task_id AND user_id = :user_id
                ORDER BY created_at DESC
            """)
            
            result = self.db.session.execute(query, {
                'task_id': task_id,
                'user_id': user_id
            }).fetchall()
            
            return [self._row_to_material(row) for row in result]
            
        except Exception as e:
            raise e
    
    def get_materials_by_type(self, material_type: MaterialType, user_id: str) -> List[ClassworkMaterial]:
        """Get materials by type"""
        try:
            query = text("""
                SELECT * FROM classwork_material 
                WHERE file_type = :file_type AND user_id = :user_id
                ORDER BY created_at DESC
            """)
            
            result = self.db.session.execute(query, {
                'file_type': material_type.value,
                'user_id': user_id
            }).fetchall()
            
            return [self._row_to_material(row) for row in result]
            
        except Exception as e:
            raise e
    
    def get_materials_by_subject(self, subject: str, user_id: str) -> List[ClassworkMaterial]:
        """Get materials by subject"""
        try:
            query = text("""
                SELECT * FROM classwork_material 
                WHERE subject = :subject AND user_id = :user_id
                ORDER BY created_at DESC
            """)
            
            result = self.db.session.execute(query, {
                'subject': subject,
                'user_id': user_id
            }).fetchall()
            
            return [self._row_to_material(row) for row in result]
            
        except Exception as e:
            raise e
    
    def update_material(self, material: ClassworkMaterial) -> ClassworkMaterial:
        """Update material"""
        try:
            query = text("""
                UPDATE classwork_material SET
                    title = :title,
                    description = :description,
                    file_path = :file_path,
                    file_type = :file_type,
                    file_size = :file_size,
                    subject = :subject,
                    category = :category,
                    tags = :tags,
                    updated_at = :updated_at
                WHERE id = :id AND user_id = :user_id
            """)
            
            self.db.session.execute(query, {
                'id': material.id,
                'user_id': material.user_id,
                'title': material.title,
                'description': material.description,
                'file_path': material.file_path,
                'file_type': material.file_type.value if material.file_type else None,
                'file_size': material.file_size,
                'subject': material.subject,
                'category': material.category,
                'tags': ','.join(material.tags) if material.tags else None,
                'updated_at': material.updated_at.isoformat() if material.updated_at else None
            })
            
            self.db.session.commit()
            return material
            
        except Exception as e:
            self.db.session.rollback()
            raise e
    
    def delete_material(self, material_id: str, user_id: str) -> bool:
        """Delete material"""
        try:
            query = text("""
                DELETE FROM classwork_material 
                WHERE id = :material_id AND user_id = :user_id
            """)
            
            result = self.db.session.execute(query, {
                'material_id': material_id,
                'user_id': user_id
            })
            
            self.db.session.commit()
            return result.rowcount > 0
            
        except Exception as e:
            self.db.session.rollback()
            raise e
    
    def search_materials(self, query: str, user_id: str) -> List[ClassworkMaterial]:
        """Search materials"""
        try:
            search_query = text("""
                SELECT * FROM classwork_material 
                WHERE user_id = :user_id 
                AND (title LIKE :query OR description LIKE :query OR subject LIKE :query)
                ORDER BY created_at DESC
            """)
            
            result = self.db.session.execute(search_query, {
                'user_id': user_id,
                'query': f'%{query}%'
            }).fetchall()
            
            return [self._row_to_material(row) for row in result]
            
        except Exception as e:
            raise e
    
    def _row_to_material(self, row) -> ClassworkMaterial:
        """Convert database row to ClassworkMaterial"""
        return ClassworkMaterial(
            id=row.id,
            user_id=row.user_id,
            lesson_id=row.lesson_id,
            task_id=row.task_id,
            title=row.title,
            description=row.description,
            file_path=row.file_path,
            file_type=MaterialType(row.file_type) if row.file_type else None,
            file_size=row.file_size,
            subject=row.subject,
            category=row.category,
            tags=row.tags.split(',') if row.tags else [],
            created_at=datetime.fromisoformat(row.created_at) if row.created_at else None,
            updated_at=datetime.fromisoformat(row.updated_at) if row.updated_at else None
        )

class ClassworkNoteRepositoryImpl(ClassworkNoteRepository):
    """Classwork Note Repository Implementation"""
    
    def __init__(self, db):
        self.db = db
    
    def create_note(self, note: ClassworkNote) -> ClassworkNote:
        """Create a new classwork note"""
        try:
            query = text("""
                INSERT INTO classwork_note (
                    id, user_id, lesson_id, task_id, title, content, subject, category, tags, created_at, updated_at
                ) VALUES (
                    :id, :user_id, :lesson_id, :task_id, :title, :content, :subject, :category, :tags, :created_at, :updated_at
                )
            """)
            
            self.db.session.execute(query, {
                'id': note.id,
                'user_id': note.user_id,
                'lesson_id': note.lesson_id,
                'task_id': note.task_id,
                'title': note.title,
                'content': note.content,
                'subject': note.subject,
                'category': note.category,
                'tags': ','.join(note.tags) if note.tags else None,
                'created_at': note.created_at.isoformat() if note.created_at else None,
                'updated_at': note.updated_at.isoformat() if note.updated_at else None
            })
            
            self.db.session.commit()
            return note
            
        except Exception as e:
            self.db.session.rollback()
            raise e
    
    def get_note_by_id(self, note_id: str, user_id: str) -> Optional[ClassworkNote]:
        """Get note by ID"""
        try:
            query = text("""
                SELECT * FROM classwork_note 
                WHERE id = :note_id AND user_id = :user_id
            """)
            
            result = self.db.session.execute(query, {
                'note_id': note_id,
                'user_id': user_id
            }).fetchone()
            
            if result:
                return self._row_to_note(result)
            return None
            
        except Exception as e:
            raise e
    
    def get_notes_by_lesson(self, lesson_id: str, user_id: str) -> List[ClassworkNote]:
        """Get all notes for a lesson"""
        try:
            query = text("""
                SELECT * FROM classwork_note 
                WHERE lesson_id = :lesson_id AND user_id = :user_id
                ORDER BY created_at DESC
            """)
            
            result = self.db.session.execute(query, {
                'lesson_id': lesson_id,
                'user_id': user_id
            }).fetchall()
            
            return [self._row_to_note(row) for row in result]
            
        except Exception as e:
            raise e
    
    def get_notes_by_task(self, task_id: str, user_id: str) -> List[ClassworkNote]:
        """Get notes for a task"""
        try:
            query = text("""
                SELECT * FROM classwork_note 
                WHERE task_id = :task_id AND user_id = :user_id
                ORDER BY created_at DESC
            """)
            
            result = self.db.session.execute(query, {
                'task_id': task_id,
                'user_id': user_id
            }).fetchall()
            
            return [self._row_to_note(row) for row in result]
            
        except Exception as e:
            raise e
    
    def get_notes_by_subject(self, subject: str, user_id: str) -> List[ClassworkNote]:
        """Get notes by subject"""
        try:
            query = text("""
                SELECT * FROM classwork_note 
                WHERE subject = :subject AND user_id = :user_id
                ORDER BY created_at DESC
            """)
            
            result = self.db.session.execute(query, {
                'subject': subject,
                'user_id': user_id
            }).fetchall()
            
            return [self._row_to_note(row) for row in result]
            
        except Exception as e:
            raise e
    
    def update_note(self, note: ClassworkNote) -> ClassworkNote:
        """Update note"""
        try:
            query = text("""
                UPDATE classwork_note SET
                    title = :title,
                    content = :content,
                    subject = :subject,
                    category = :category,
                    tags = :tags,
                    updated_at = :updated_at
                WHERE id = :id AND user_id = :user_id
            """)
            
            self.db.session.execute(query, {
                'id': note.id,
                'user_id': note.user_id,
                'title': note.title,
                'content': note.content,
                'subject': note.subject,
                'category': note.category,
                'tags': ','.join(note.tags) if note.tags else None,
                'updated_at': note.updated_at.isoformat() if note.updated_at else None
            })
            
            self.db.session.commit()
            return note
            
        except Exception as e:
            self.db.session.rollback()
            raise e
    
    def delete_note(self, note_id: str, user_id: str) -> bool:
        """Delete note"""
        try:
            query = text("""
                DELETE FROM classwork_note 
                WHERE id = :note_id AND user_id = :user_id
            """)
            
            result = self.db.session.execute(query, {
                'note_id': note_id,
                'user_id': user_id
            })
            
            self.db.session.commit()
            return result.rowcount > 0
            
        except Exception as e:
            self.db.session.rollback()
            raise e
    
    def search_notes(self, query: str, user_id: str) -> List[ClassworkNote]:
        """Search notes"""
        try:
            search_query = text("""
                SELECT * FROM classwork_note 
                WHERE user_id = :user_id 
                AND (title LIKE :query OR content LIKE :query OR subject LIKE :query)
                ORDER BY created_at DESC
            """)
            
            result = self.db.session.execute(search_query, {
                'user_id': user_id,
                'query': f'%{query}%'
            }).fetchall()
            
            return [self._row_to_note(row) for row in result]
            
        except Exception as e:
            raise e
    
    def _row_to_note(self, row) -> ClassworkNote:
        """Convert database row to ClassworkNote"""
        return ClassworkNote(
            id=row.id,
            user_id=row.user_id,
            lesson_id=row.lesson_id,
            task_id=row.task_id,
            title=row.title,
            content=row.content,
            subject=row.subject,
            category=row.category,
            tags=row.tags.split(',') if row.tags else [],
            created_at=datetime.fromisoformat(row.created_at) if row.created_at else None,
            updated_at=datetime.fromisoformat(row.updated_at) if row.updated_at else None
        )
