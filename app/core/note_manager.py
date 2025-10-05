from app import db
from app.core.note import Note

class NoteManager:
    # Method to create a new note
    def add_note(self, user_id, title, content, tags=None, status=None, external_link=None, lesson_id=None, section_id=None, is_public=False):
        try:
            new_note = Note(
                user_id=user_id,
                title=title,
                content=content,
                tags=tags,
                status=status,
                external_link=external_link,
                lesson_id=lesson_id,
                section_id=section_id,
                is_public=is_public
            )
            db.session.add(new_note)
            db.session.commit()
            return new_note
        except Exception as e:
            db.session.rollback()
            print(f"Error adding note: {e}")
            return None

    # Methods to manage notes
    def get_note_by_id(self, note_id):
        return Note.query.get(note_id)

    # Method to get notes by user ID
    def get_notes_by_user(self, user_id):
        return Note.query.filter_by(user_id=user_id).order_by(Note.created_at.desc()).all()

    # Method to update notes
    def update_note(self, note_id, title, content, tags=None, status=None, external_link=None, lesson_id=None, section_id=None, is_public=None):
        note = self.get_note_by_id(note_id)
        if note:
            note.title = title
            note.content = content
            note.tags = tags
            if status is not None:
                note.status = status
            if external_link is not None:
                note.external_link = external_link
            if lesson_id is not None:
                note.lesson_id = lesson_id
            if section_id is not None:
                note.section_id = section_id
            if is_public is not None:
                note.is_public = is_public
            try:
                db.session.commit()
                return True
            except Exception as e:
                db.session.rollback()
                print(f"Error updating note: {e}")
                return False
        return False

    # Method to delete a note
    def delete_note(self, note_id):
        note = self.get_note_by_id(note_id)
        if note:
            try:
                db.session.delete(note)
                db.session.commit()
                return True
            except Exception as e:
                db.session.rollback()
                print(f"Error deleting note: {e}")
                return False
        return False
