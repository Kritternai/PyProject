"""
Classwork Repository Interfaces
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import datetime
from ..entities.classwork_task import ClassworkTask, TaskStatus, TaskPriority
from ..entities.classwork_material import ClassworkMaterial, MaterialType
from ..entities.classwork_note import ClassworkNote

class ClassworkTaskRepository(ABC):
    """Classwork Task Repository Interface"""
    
    @abstractmethod
    def create_task(self, task: ClassworkTask) -> ClassworkTask:
        """Create a new classwork task"""
        pass
    
    @abstractmethod
    def get_task_by_id(self, task_id: str, user_id: str) -> Optional[ClassworkTask]:
        """Get task by ID"""
        pass
    
    @abstractmethod
    def get_tasks_by_lesson(self, lesson_id: str, user_id: str) -> List[ClassworkTask]:
        """Get all tasks for a lesson"""
        pass
    
    @abstractmethod
    def get_tasks_by_status(self, status: TaskStatus, user_id: str) -> List[ClassworkTask]:
        """Get tasks by status"""
        pass
    
    @abstractmethod
    def get_tasks_by_priority(self, priority: TaskPriority, user_id: str) -> List[ClassworkTask]:
        """Get tasks by priority"""
        pass
    
    @abstractmethod
    def get_overdue_tasks(self, user_id: str) -> List[ClassworkTask]:
        """Get overdue tasks"""
        pass
    
    @abstractmethod
    def get_due_soon_tasks(self, user_id: str, hours: int = 24) -> List[ClassworkTask]:
        """Get tasks due soon"""
        pass
    
    @abstractmethod
    def update_task(self, task: ClassworkTask) -> ClassworkTask:
        """Update task"""
        pass
    
    @abstractmethod
    def delete_task(self, task_id: str, user_id: str) -> bool:
        """Delete task"""
        pass
    
    @abstractmethod
    def search_tasks(self, query: str, user_id: str) -> List[ClassworkTask]:
        """Search tasks"""
        pass

class ClassworkMaterialRepository(ABC):
    """Classwork Material Repository Interface"""
    
    @abstractmethod
    def create_material(self, material: ClassworkMaterial) -> ClassworkMaterial:
        """Create a new classwork material"""
        pass
    
    @abstractmethod
    def get_material_by_id(self, material_id: str, user_id: str) -> Optional[ClassworkMaterial]:
        """Get material by ID"""
        pass
    
    @abstractmethod
    def get_materials_by_lesson(self, lesson_id: str, user_id: str) -> List[ClassworkMaterial]:
        """Get all materials for a lesson"""
        pass
    
    @abstractmethod
    def get_materials_by_task(self, task_id: str, user_id: str) -> List[ClassworkMaterial]:
        """Get materials for a task"""
        pass
    
    @abstractmethod
    def get_materials_by_type(self, material_type: MaterialType, user_id: str) -> List[ClassworkMaterial]:
        """Get materials by type"""
        pass
    
    @abstractmethod
    def get_materials_by_subject(self, subject: str, user_id: str) -> List[ClassworkMaterial]:
        """Get materials by subject"""
        pass
    
    @abstractmethod
    def update_material(self, material: ClassworkMaterial) -> ClassworkMaterial:
        """Update material"""
        pass
    
    @abstractmethod
    def delete_material(self, material_id: str, user_id: str) -> bool:
        """Delete material"""
        pass
    
    @abstractmethod
    def search_materials(self, query: str, user_id: str) -> List[ClassworkMaterial]:
        """Search materials"""
        pass

class ClassworkNoteRepository(ABC):
    """Classwork Note Repository Interface"""
    
    @abstractmethod
    def create_note(self, note: ClassworkNote) -> ClassworkNote:
        """Create a new classwork note"""
        pass
    
    @abstractmethod
    def get_note_by_id(self, note_id: str, user_id: str) -> Optional[ClassworkNote]:
        """Get note by ID"""
        pass
    
    @abstractmethod
    def get_notes_by_lesson(self, lesson_id: str, user_id: str) -> List[ClassworkNote]:
        """Get all notes for a lesson"""
        pass
    
    @abstractmethod
    def get_notes_by_task(self, task_id: str, user_id: str) -> List[ClassworkNote]:
        """Get notes for a task"""
        pass
    
    @abstractmethod
    def get_notes_by_subject(self, subject: str, user_id: str) -> List[ClassworkNote]:
        """Get notes by subject"""
        pass
    
    @abstractmethod
    def update_note(self, note: ClassworkNote) -> ClassworkNote:
        """Update note"""
        pass
    
    @abstractmethod
    def delete_note(self, note_id: str, user_id: str) -> bool:
        """Delete note"""
        pass
    
    @abstractmethod
    def search_notes(self, query: str, user_id: str) -> List[ClassworkNote]:
        """Search notes"""
        pass
