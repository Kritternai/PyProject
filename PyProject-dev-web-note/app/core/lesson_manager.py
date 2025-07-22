from app import db
from app.core.lesson import Lesson

class LessonManager:
    def add_lesson(self, user_id, title, description=None, status='Not Started', tags=None):
        lesson = Lesson(user_id=user_id, title=title, description=description, status=status, tags=tags)
        db.session.add(lesson)
        db.session.commit()
        return lesson

    def get_lesson_by_id(self, lesson_id):
        return Lesson.query.get(lesson_id)

    def get_lessons_by_user(self, user_id):
        return Lesson.query.filter_by(user_id=user_id).all()

    def update_lesson(self, lesson_id, title=None, description=None, status=None, tags=None):
        lesson = self.get_lesson_by_id(lesson_id)
        if not lesson:
            return False

        if title:
            lesson.title = title
        if description is not None:
            lesson.description = description
        if status:
            lesson.status = status
        if tags is not None:
            lesson.tags = tags
        
        db.session.commit()
        return True

    def delete_lesson(self, lesson_id):
        lesson = self.get_lesson_by_id(lesson_id)
        if lesson:
            db.session.delete(lesson)
            db.session.commit()
            return True
        return False
