from app import db
from app.core.note import Note

class NoteManager:
    # Method to create a new note
    def add_note(self, user_id, title, content, note_date=None, due_date=None, tags=None, status=None, image=None):
        try:
            new_note = Note(
                user_id=user_id,
                title=title,
                content=content,
                note_date=note_date,
                due_date=due_date,
                tags=tags,
                status=status,
                image=image
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
        return Note.query.filter_by(user_id=user_id).order_by(Note.note_date.desc()).all()

    # Method to update notes
    def update_note(self, note_id, title, content, note_date=None, due_date=None, tags=None, status=None, image=None):
        note = self.get_note_by_id(note_id)
        if note:
            note.title = title
            note.content = content
            note.note_date = note_date
            note.due_date = due_date
            note.tags = tags
            note.status = status
            if image is not None:
                note.image = image
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
    
# === สิ่งที่เกี่ยวข้องกับ note ===
# note.py, note_manager.py, routes.py, note.html, create.html, edit.html, list.html, static/uploads/

# การทำ static/uploads/images/ เพื่อเก็บไฟล์รูปภาพที่แนบมากับ note, static/uploads/files/ เพื่อเก็บไฟล์เอกสารที่แนบมากับ note date:
# สิ่งที่จะทำเพิ่ม การเก็บ file แบบ all file
# สิ่งที่จะทำเพิ่ม การเก็บไฟล์แนบ เช่น รูปภาพ, ไฟล์เอกสาร แบบ Hash
# สิ่งที่จะทำเพิ่ม การเก็บ link เช่น https://www.example.com
# สิ่งที่จะทำเพิ่ม การทำ search note คือการทำ search note โดยการใช้ library เช่น elasticsearch หรือ lunr.js
# สิ่งที่จะทำเพิ่ม การทำ note เป็นแบบ markdown คือการทำ note เป็นแบบ markdown editor โดยการใช้ library เช่น markdown-it หรือ showdown.js
# สิ่งที่จะทำเพิ่ม การทำ note เป็นแบบ checklist คือการทำ note เป็นแบบ checklist โดยการใช้ library เช่น react-checklist หรือ vue-checklist
# สิ่งที่จะทำเพิ่ม ถ้ามันดี เพราะเหมาะกับผู้ใช้ทั่วไป การทำ note เป็นแบบ rich text editor คือการทำ note เป็นแบบ rich text editor โดยการใช้ library เช่น quill.js หรือ tinymce
