"""
Data Synchronization Service
Handles synchronization between Google Classroom and local database
"""

from app import db
from app.core.lesson import Lesson
from app.core.imported_data import ImportedData
from datetime import datetime
import json

class DataSyncService:
    @staticmethod
    def sync_google_classroom_data(user_id, google_data):
        """
        Synchronize Google Classroom data with local database
        """
        try:
            # Update imported data
            imported_data = ImportedData.query.filter_by(
                user_id=user_id, 
                platform='google_classroom_api'
            ).first()
            
            if not imported_data:
                imported_data = ImportedData(
                    user_id=user_id,
                    platform='google_classroom_api',
                    data=google_data
                )
                db.session.add(imported_data)
            else:
                imported_data.data = google_data
                imported_data.imported_at = datetime.utcnow()
            
            # Sync lessons
            if 'courses' in google_data:
                for course in google_data['courses']:
                    DataSyncService._sync_course_to_lesson(user_id, course)
            
            db.session.commit()
            return True
            
        except Exception as e:
            db.session.rollback()
            print(f"Error syncing Google Classroom data: {e}")
            return False
    
    @staticmethod
    def _sync_course_to_lesson(user_id, course):
        """
        Sync a single Google Classroom course to lesson
        """
        course_id = str(course.get('id'))
        
        # Check if lesson already exists
        lesson = Lesson.query.filter_by(
            user_id=user_id,
            google_classroom_id=course_id
        ).first()
        
        if not lesson:
            # Create new lesson
            lesson = Lesson(
                title=course.get('name', 'Untitled Course'),
                description=course.get('description', ''),
                author_name='Google Classroom Teacher',
                user_id=user_id,
                source_platform='google_classroom',
                google_classroom_id=course_id,
                tags='Google Classroom',
                status='Not Started'
            )
            db.session.add(lesson)
        
        # Update lesson data
        lesson.title = course.get('name', lesson.title)
        lesson.description = course.get('description', lesson.description)
        
        # Set teacher name
        if 'teachers' in course and course['teachers']:
            first_teacher = course['teachers'][0]
            if 'profile' in first_teacher and 'name' in first_teacher['profile']:
                lesson.author_name = first_teacher['profile']['name'].get('fullName', 'Google Classroom Teacher')
        
        # Update tags
        current_tags = lesson.tags.split(',') if lesson.tags else []
        if 'Google Classroom' not in current_tags:
            current_tags.append('Google Classroom')
        if course.get('section'):
            section_tag = f"Section {course['section']}"
            if section_tag not in current_tags:
                current_tags.append(section_tag)
        lesson.tags = ', '.join(current_tags)
        
        # Update assignment count
        if 'courseWork' in course:
            lesson.classroom_assignments_count = len(course['courseWork'])
        
        # Store additional data as JSON
        lesson.announcements_data = json.dumps(course.get('announcements', []))
        lesson.topics_data = json.dumps(course.get('topics', []))
        lesson.roster_data = json.dumps(course.get('students', []))
        lesson.attachments_data = json.dumps(course.get('all_attachments', []))
    
    @staticmethod
    def cleanup_orphaned_lessons(user_id):
        """
        Remove lessons that no longer exist in Google Classroom
        """
        try:
            # Get current Google Classroom courses
            imported_data = ImportedData.query.filter_by(
                user_id=user_id,
                platform='google_classroom_api'
            ).first()
            
            if not imported_data or 'courses' not in imported_data.data:
                return
            
            current_course_ids = {str(course.get('id')) for course in imported_data.data['courses']}
            
            # Find orphaned lessons (Google Classroom lessons that no longer exist)
            orphaned_lessons = Lesson.query.filter(
                Lesson.user_id == user_id,
                Lesson.source_platform == 'google_classroom',
                ~Lesson.google_classroom_id.in_(current_course_ids)
            ).all()
            
            for lesson in orphaned_lessons:
                db.session.delete(lesson)
            
            db.session.commit()
            return len(orphaned_lessons)
            
        except Exception as e:
            db.session.rollback()
            print(f"Error cleaning up orphaned lessons: {e}")
            return 0 