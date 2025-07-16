from app import db
from app.core.note import Note

class NoteManager:
    def add_note(self, user_id, title, content, note_date=None):
        try:
            new_note = Note(user_id=user_id, title=title, content=content, note_date=note_date)
            db.session.add(new_note)
            db.session.commit()
            return new_note
        except Exception as e:
            db.session.rollback()
            print(f"Error adding note: {e}")
            return None

    def get_note_by_id(self, note_id):
        return Note.query.get(note_id)

    def get_notes_by_user(self, user_id):
        return Note.query.filter_by(user_id=user_id).order_by(Note.note_date.desc()).all()

    def update_note(self, note_id, title, content, note_date=None):
        note = self.get_note_by_id(note_id)
        if note:
            note.title = title
            note.content = content
            note.note_date = note_date
            try:
                db.session.commit()
                return True
            except Exception as e:
                db.session.rollback()
                print(f"Error updating note: {e}")
                return False
        return False

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