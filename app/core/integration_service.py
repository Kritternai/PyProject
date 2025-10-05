from app import db
from app.core.lesson import Lesson, LessonSection
from app.core.note import Note
from app.core.files import Files
import uuid
from datetime import datetime

class IntegrationService:
    """Service for managing integration between Lessons, Notes, and Files"""
    
    @staticmethod
    def create_note_from_lesson_section(lesson_id, section_id, user_id):
        """Create a Note from a LessonSection"""
        section = LessonSection.query.get(section_id)
        if not section or section.lesson_id != lesson_id:
            return None
            
        # Create note from section
        note = Note(
            id=str(uuid.uuid4()),
            user_id=user_id,
            lesson_id=lesson_id,
            section_id=section_id,
            title=section.title,
            content=section.content or '',
            tags=section.tags,
            status=section.status,
            external_link=section.external_link
        )
        
        db.session.add(note)
        
        # Copy files from section to note
        for file_record in section.files:
            new_file = Files(
                id=str(uuid.uuid4()),
                user_id=user_id,
                note_id=note.id,
                lesson_id=lesson_id,
                section_id=section_id,
                file_name=file_record.file_name,
                file_path=file_record.file_path,
                file_type=file_record.file_type,
                file_size=file_record.file_size,
                mime_type=file_record.mime_type,
                external_url=file_record.external_url,
                is_public=file_record.is_public
            )
            db.session.add(new_file)
        
        db.session.commit()
        return note
    
    @staticmethod
    def create_lesson_section_from_note(note_id, lesson_id, user_id):
        """Create a LessonSection from a Note"""
        note = Note.query.get(note_id)
        if not note or note.user_id != user_id:
            return None
            
        # Create section from note
        section = LessonSection(
            id=str(uuid.uuid4()),
            lesson_id=lesson_id,
            title=note.title,
            content=note.content,
            section_type='note',
            tags=note.tags,
            status=note.status
        )
        
        db.session.add(section)
        
        # Copy files from note to section
        for file_record in note.files:
            new_file = Files(
                id=str(uuid.uuid4()),
                user_id=user_id,
                lesson_id=lesson_id,
                section_id=section.id,
                note_id=note_id,
                file_name=file_record.file_name,
                file_path=file_record.file_path,
                file_type=file_record.file_type,
                file_size=file_record.file_size,
                mime_type=file_record.mime_type,
                external_url=file_record.external_url,
                is_public=file_record.is_public
            )
            db.session.add(new_file)
        
        db.session.commit()
        return section
    
    @staticmethod
    def sync_files_between_entities(source_entity_type, source_entity_id, target_entity_type, target_entity_id, user_id):
        """Sync files between different entities (Lesson, Note, Section)"""
        # Get source files
        source_files = Files.query.filter_by(
            user_id=user_id,
            **{f"{source_entity_type}_id": source_entity_id}
        ).all()
        
        # Create copies in target entity
        for file_record in source_files:
            new_file = Files(
                id=str(uuid.uuid4()),
                user_id=user_id,
                file_name=file_record.file_name,
                file_path=file_record.file_path,
                file_type=file_record.file_type,
                file_size=file_record.file_size,
                mime_type=file_record.mime_type,
                external_url=file_record.external_url,
                is_public=file_record.is_public,
                **{f"{target_entity_type}_id": target_entity_id}
            )
            db.session.add(new_file)
        
        db.session.commit()
        return len(source_files)
    
    @staticmethod
    def get_lesson_summary(lesson_id, user_id):
        """Get comprehensive summary of a lesson including notes and files"""
        lesson = Lesson.query.filter_by(id=lesson_id, user_id=user_id).first()
        if not lesson:
            return None
            
        return {
            'lesson': lesson,
            'notes': lesson.notes,
            'files': lesson.files,
            'sections': lesson.sections,
            'note_count': lesson.note_count,
            'file_count': lesson.file_count,
            'section_count': len(lesson.sections)
        }
    
    @staticmethod
    def get_user_integrated_data(user_id):
        """Get all integrated data for a user"""
        lessons = Lesson.query.filter_by(user_id=user_id).all()
        notes = Note.query.filter_by(user_id=user_id).all()
        files = Files.query.filter_by(user_id=user_id).all()
        
        return {
            'lessons': lessons,
            'notes': notes,
            'files': files,
            'total_lessons': len(lessons),
            'total_notes': len(notes),
            'total_files': len(files)
        } 