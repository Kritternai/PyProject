from app import db
from app.core.lesson import Lesson, LessonSection
from app.core.lesson_manager import LessonManager
from datetime import datetime

class NoteSectionManager:
    def __init__(self, db_session, lesson_manager):
        self.db_session = db_session
        self.lesson_manager = lesson_manager

    def get_all_user_notes(self, user_id):
        return self.db_session.session.query(LessonSection).join(Lesson).filter(
            Lesson.user_id == user_id,
            LessonSection.type == 'note'
        ).order_by(LessonSection.created_at.desc()).all()

    def get_user_note_by_id(self, note_id, user_id):
        return self.db_session.session.query(LessonSection).join(Lesson).filter(
            LessonSection.id == note_id,
            LessonSection.type == 'note',
            Lesson.user_id == user_id
        ).first()

    def create_user_note(self, user_id, title, content, tags=None, status=None, image_path=None, file_url=None, external_link=None):
        # Find or create the "General Notes" lesson for the user
        general_notes_lesson = Lesson.query.filter_by(user_id=user_id, title="General Notes").first()
        if not general_notes_lesson:
            general_notes_lesson = self.lesson_manager.add_lesson(user_id, "General Notes", "A place for your general notes.")

        if not general_notes_lesson:
            return None # Could not create general notes lesson

        return self.lesson_manager.add_section(
            lesson_id=general_notes_lesson.id,
            title=title,
            body=content,
            type='note',
            tags=tags,
            status=status,
            image_path=image_path,
            file_url=file_url,
            external_link=external_link
        )

    def update_user_note(self, note_id, user_id, title, content, tags=None, status=None, image_path=None, file_url=None, external_link=None):
        note_section = self.get_user_note_by_id(note_id, user_id)
        if note_section:
            return self.lesson_manager.update_section(
                section_id=note_id,
                title=title,
                body=content,
                type='note', # Ensure type remains note
                tags=tags,
                status=status,
                image_path=image_path,
                file_url=file_url,
                external_link=external_link
            )
        return None

    def delete_user_note(self, note_id, user_id):
        note_section = self.get_user_note_by_id(note_id, user_id)
        if note_section:
            return self.lesson_manager.delete_section(note_id)
        return False
