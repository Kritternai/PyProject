from app import db
from app.core.note import Note
from datetime import datetime

class NoteManager:
    def __init__(self, db_session):
        self.db_session = db_session

    def get_all_notes_by_user(self, user_id):
        return self.db_session.session.query(Note).filter_by(user_id=user_id).order_by(Note.timestamp.desc()).all()

    def get_note_by_id_and_user(self, note_id, user_id):
        return self.db_session.session.query(Note).filter_by(id=note_id, user_id=user_id).first()

    def create_note(self, title, content, user_id):
        new_note = Note(title=title, content=content, user_id=user_id)
        self.db_session.session.add(new_note)
        self.db_session.session.commit()
        return new_note

    def update_note(self, note_id, user_id, title, content):
        note = self.get_note_by_id_and_user(note_id, user_id)
        if note:
            note.title = title
            note.content = content
            self.db_session.session.commit()
        return note

    def delete_note(self, note_id, user_id):
        note = self.get_note_by_id_and_user(note_id, user_id)
        if note:
            self.db_session.session.delete(note)
            self.db_session.session.commit()
            return True
        return False
