from app import db
from app.core.note import Note
from datetime import datetime

class NoteManager:
    def __init__(self):
        pass # db session is now handled by db.session directly

    def get_all_user_notes(self, user_id):
        return Note.query.filter_by(user_id=user_id).order_by(Note.created_at.desc()).all()

    def get_user_note_by_id(self, note_id, user_id):
        return Note.query.filter_by(id=note_id, user_id=user_id).first()

    def create_user_note(self, user_id, title, body, tags=None, status=None, image_path=None, file_url=None, external_link=None):
        new_note = Note(
            user_id=user_id,
            title=title,
            body=body,
            tags=tags,
            status=status,
            image_path=image_path,
            file_url=file_url,
            external_link=external_link
        )
        db.session.add(new_note)
        db.session.commit()
        return new_note

    def update_user_note(self, note_id, user_id, title, body, tags=None, status=None, image_path=None, file_url=None, external_link=None):
        note = self.get_user_note_by_id(note_id, user_id)
        if note:
            note.title = title
            note.body = body
            note.tags = tags
            note.status = status
            note.image_path = image_path
            note.file_url = file_url
            note.external_link = external_link
            db.session.commit()
        return note

    def delete_user_note(self, note_id, user_id):
        note = self.get_user_note_by_id(note_id, user_id)
        if note:
            db.session.delete(note)
            db.session.commit()
            return True
        return False
