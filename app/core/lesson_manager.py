from app import db
from app.core.lesson import Lesson
import json

class LessonManager:
    def add_lesson(self, user_id, title, description=None, status='Not Started', tags=None, source_platform='manual', google_classroom_id=None):
        lesson = Lesson(user_id=user_id, title=title, description=description, status=status, tags=tags, source_platform=source_platform, google_classroom_id=google_classroom_id)
        db.session.add(lesson)
        db.session.commit()
        return lesson

    def import_google_classroom_course_as_lesson(self, user_id, gc_course_data):
        # Check if this Google Classroom course has already been imported as a lesson
        existing_lesson = Lesson.query.filter_by(user_id=user_id, google_classroom_id=gc_course_data.get('id')).first()
        if existing_lesson:
            # If it exists, update it instead of creating a new one
            existing_lesson.title = gc_course_data.get('name', existing_lesson.title)
            existing_lesson.description = gc_course_data.get('description', existing_lesson.description)
            existing_lesson.announcements_data = json.dumps(gc_course_data.get('announcements', []))
            existing_lesson.topics_data = json.dumps(gc_course_data.get('grouped_by_topic', [])) # Use grouped_by_topic
            existing_lesson.roster_data = json.dumps({
                "teachers": gc_course_data.get('teachers', []),
                "students": gc_course_data.get('students', [])
            })
            existing_lesson.attachments_data = json.dumps(gc_course_data.get('all_attachments', []))
            db.session.commit()
            return existing_lesson
        else:
            # Create a new lesson from Google Classroom data
            lesson = Lesson(
                user_id=user_id,
                title=gc_course_data.get('name', 'Untitled Google Classroom Course'),
                description=gc_course_data.get('description', ''),
                status='Imported',
                tags='google-classroom',
                source_platform='google_classroom',
                google_classroom_id=gc_course_data.get('id'),
                announcements_data=json.dumps(gc_course_data.get('announcements', [])),
                topics_data=json.dumps(gc_course_data.get('grouped_by_topic', [])),
                roster_data=json.dumps({
                    "teachers": gc_course_data.get('teachers', []),
                    "students": gc_course_data.get('students', [])
                }),
                attachments_data=json.dumps(gc_course_data.get('all_attachments', []))
            )
            db.session.add(lesson)
            db.session.commit()
            return lesson

    def get_lesson_by_id(self, lesson_id):
        return Lesson.query.get(lesson_id)

    def get_lessons_by_user(self, user_id):
        return Lesson.query.filter_by(user_id=user_id).all()

    def update_lesson(self, lesson_id, title=None, description=None, status=None, tags=None, announcements_data=None, topics_data=None, roster_data=None, attachments_data=None):
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
        if announcements_data is not None:
            lesson.announcements_data = json.dumps(announcements_data)
        if topics_data is not None:
            lesson.topics_data = json.dumps(topics_data)
        if roster_data is not None:
            lesson.roster_data = json.dumps(roster_data)
        if attachments_data is not None:
            lesson.attachments_data = json.dumps(attachments_data)
        
        db.session.commit()
        return True

    def delete_lesson(self, lesson_id):
        lesson = self.get_lesson_by_id(lesson_id)
        if lesson:
            db.session.delete(lesson)
            db.session.commit()
            return True
        return False
