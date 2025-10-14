"""
Google Classroom Service
Handles Google Classroom API integration
"""

import os
import json
from typing import List, Dict, Optional, Any
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from app import db
from app.models.user import UserModel


class GoogleClassroomService:
    """Service for Google Classroom API operations"""
    
    # Required scopes for Google Classroom
    SCOPES = [
        'https://www.googleapis.com/auth/classroom.courses.readonly',
        'https://www.googleapis.com/auth/classroom.announcements.readonly',
        'https://www.googleapis.com/auth/classroom.courseworkmaterials.readonly',
        'https://www.googleapis.com/auth/classroom.course-work.readonly',
        'https://www.googleapis.com/auth/classroom.student-submissions.me.readonly',
        'https://www.googleapis.com/auth/classroom.topics.readonly',
        'https://www.googleapis.com/auth/classroom.rosters.readonly',
        'https://www.googleapis.com/auth/userinfo.profile',
        'openid',
        'https://www.googleapis.com/auth/userinfo.email',
        'https://www.googleapis.com/auth/drive.readonly'
    ]
    
    def __init__(self):
        self.classroom_service = None
        self.drive_service = None
    
    def get_credentials(self, user_id: str) -> Optional[Credentials]:
        """Get stored credentials for user"""
        try:
            user = UserModel.query.filter_by(id=user_id).first()
            if not user or not user.google_credentials:
                return None
            
            # Parse stored credentials
            creds_data = json.loads(user.google_credentials)
            credentials = Credentials.from_authorized_user_info(creds_data, self.SCOPES)
            
            # Refresh if needed
            if credentials.expired and credentials.refresh_token:
                credentials.refresh(Request())
                # Save refreshed credentials
                self.save_credentials(user_id, credentials)
            
            return credentials
            
        except Exception as e:
            print(f"Error getting credentials for user {user_id}: {e}")
            return None
    
    def save_credentials(self, user_id: str, credentials: Credentials):
        """Save credentials to database"""
        try:
            user = UserModel.query.filter_by(id=user_id).first()
            if user:
                creds_data = {
                    'token': credentials.token,
                    'refresh_token': credentials.refresh_token,
                    'token_uri': credentials.token_uri,
                    'client_id': credentials.client_id,
                    'client_secret': credentials.client_secret,
                    'scopes': credentials.scopes
                }
                user.google_credentials = json.dumps(creds_data)
                db.session.commit()
                
        except Exception as e:
            print(f"Error saving credentials for user {user_id}: {e}")
            db.session.rollback()
    
    def get_classroom_service(self, user_id: str):
        """Get authenticated Google Classroom service"""
        credentials = self.get_credentials(user_id)
        if not credentials:
            raise Exception("No valid credentials found")
        
        if not self.classroom_service:
            self.classroom_service = build('classroom', 'v1', credentials=credentials)
        
        return self.classroom_service
    
    def get_drive_service(self, user_id: str):
        """Get authenticated Google Drive service"""
        credentials = self.get_credentials(user_id)
        if not credentials:
            raise Exception("No valid credentials found")
        
        if not self.drive_service:
            self.drive_service = build('drive', 'v3', credentials=credentials)
        
        return self.drive_service
    
    def fetch_courses(self, user_id: str) -> List[Dict[str, Any]]:
        """Fetch all Google Classroom courses for user"""
        try:
            service = self.get_classroom_service(user_id)
            
            # Get courses
            results = service.courses().list(
                courseStates=['ACTIVE', 'ARCHIVED'],
                pageSize=100
            ).execute()
            
            courses = results.get('courses', [])
            
            # Enrich course data
            enriched_courses = []
            for course in courses:
                enriched_course = self._enrich_course_data(service, course)
                enriched_courses.append(enriched_course)
            
            return enriched_courses
            
        except HttpError as e:
            print(f"Google Classroom API error: {e}")
            raise Exception(f"Failed to fetch courses: {e}")
        except Exception as e:
            print(f"Error fetching courses: {e}")
            raise Exception(f"Failed to fetch courses: {e}")
    
    def _enrich_course_data(self, service, course: Dict[str, Any]) -> Dict[str, Any]:
        """Enrich course data with additional information"""
        course_id = course.get('id')
        
        try:
            # Get students count
            students_result = service.courses().students().list(courseId=course_id).execute()
            students_count = len(students_result.get('students', []))
            
            # Get course work count
            coursework_result = service.courses().courseWork().list(courseId=course_id).execute()
            coursework_count = len(coursework_result.get('courseWork', []))
            
            # Get course work materials count
            materials_result = service.courses().courseWorkMaterials().list(courseId=course_id).execute()
            materials_count = len(materials_result.get('courseWorkMaterial', []))
            
            # Get announcements count
            announcements_result = service.courses().announcements().list(courseId=course_id).execute()
            announcements_count = len(announcements_result.get('announcements', []))
            
            return {
                'id': course_id,
                'name': course.get('name', 'Untitled Course'),
                'description': course.get('description', ''),
                'section': course.get('section', ''),
                'room': course.get('room', ''),
                'courseState': course.get('courseState', 'ACTIVE'),
                'studentsCount': students_count,
                'assignmentsCount': coursework_count,
                'materialsCount': materials_count,
                'announcementsCount': announcements_count,
                'creationTime': course.get('creationTime', ''),
                'updateTime': course.get('updateTime', '')
            }
            
        except Exception as e:
            print(f"Error enriching course data for {course_id}: {e}")
            # Return basic course data if enrichment fails
            return {
                'id': course_id,
                'name': course.get('name', 'Untitled Course'),
                'description': course.get('description', ''),
                'section': course.get('section', ''),
                'room': course.get('room', ''),
                'courseState': course.get('courseState', 'ACTIVE'),
                'studentsCount': 0,
                'assignmentsCount': 0,
                'materialsCount': 0,
                'announcementsCount': 0,
                'creationTime': course.get('creationTime', ''),
                'updateTime': course.get('updateTime', '')
            }
    
    def get_course_details(self, user_id: str, course_id: str) -> Dict[str, Any]:
        """Get detailed information about a specific course"""
        try:
            service = self.get_classroom_service(user_id)
            
            # Get course details
            course = service.courses().get(id=course_id).execute()
            
            # Get students
            students_result = service.courses().students().list(courseId=course_id).execute()
            students = students_result.get('students', [])
            
            # Get course work
            coursework_result = service.courses().courseWork().list(courseId=course_id).execute()
            coursework = coursework_result.get('courseWork', [])
            
            # Get course work materials
            materials_result = service.courses().courseWorkMaterials().list(courseId=course_id).execute()
            materials = materials_result.get('courseWorkMaterial', [])
            
            # Get announcements
            announcements_result = service.courses().announcements().list(courseId=course_id).execute()
            announcements = announcements_result.get('announcements', [])
            
            return {
                'course': course,
                'students': students,
                'coursework': coursework,
                'materials': materials,
                'announcements': announcements
            }
            
        except HttpError as e:
            print(f"Google Classroom API error: {e}")
            raise Exception(f"Failed to get course details: {e}")
        except Exception as e:
            print(f"Error getting course details: {e}")
            raise Exception(f"Failed to get course details: {e}")
    
    def import_course(self, user_id: str, course_id: str, settings: Dict[str, bool]) -> Dict[str, Any]:
        """Import a Google Classroom course"""
        try:
            # Get course details
            course_data = self.get_course_details(user_id, course_id)
            course = course_data['course']
            
            # Create lesson
            from app.services import LessonService
            lesson_service = LessonService()
            
            lesson_data = {
                'title': course.get('name', 'Imported Course'),
                'description': course.get('description', ''),
                'status': 'in_progress',
                'color_theme': 1,
                'difficulty_level': 'intermediate',
                'author_name': 'Google Classroom Import'
            }
            
            lesson = lesson_service.create_lesson(user_id, lesson_data)
            
            if not lesson:
                raise Exception("Failed to create lesson")
            
            # Import students if requested
            if settings.get('importStudents', True):
                self._import_students(lesson.id, course_data['students'])
            
            # Import assignments if requested
            if settings.get('importAssignments', True):
                self._import_assignments(lesson.id, course_data['coursework'])
            
            # Import materials if requested
            if settings.get('importMaterials', True):
                self._import_materials(lesson.id, course_data['materials'])
            
            # Import announcements if requested
            if settings.get('importAnnouncements', True):
                self._import_announcements(lesson.id, course_data['announcements'])
            
            return {
                'success': True,
                'lesson_id': lesson.id,
                'message': 'Course imported successfully'
            }
            
        except Exception as e:
            print(f"Error importing course: {e}")
            raise Exception(f"Failed to import course: {e}")
    
    def _import_students(self, lesson_id: str, students: List[Dict[str, Any]]):
        """Import students from Google Classroom"""
        try:
            from app.models.member import MemberModel
            from app.models.user import UserModel
            
            for student in students:
                profile = student.get('profile', {})
                email = profile.get('emailAddress', '')
                name = profile.get('name', {})
                
                # Check if user exists
                user = UserModel.query.filter_by(email=email).first()
                if not user:
                    # Create new user
                    user = UserModel(
                        id=str(uuid.uuid4()),
                        username=email.split('@')[0],
                        email=email,
                        first_name=name.get('givenName', ''),
                        last_name=name.get('familyName', ''),
                        role='student',
                        is_active=True
                    )
                    db.session.add(user)
                    db.session.flush()
                
                # Add as member
                member = MemberModel(
                    id=str(uuid.uuid4()),
                    user_id=user.id,
                    lesson_id=lesson_id,
                    role='student'
                )
                db.session.add(member)
            
            db.session.commit()
            
        except Exception as e:
            print(f"Error importing students: {e}")
            db.session.rollback()
    
    def _import_assignments(self, lesson_id: str, coursework: List[Dict[str, Any]]):
        """Import assignments from Google Classroom"""
        try:
            from app.models.task import TaskModel
            
            for work in coursework:
                task = TaskModel(
                    id=str(uuid.uuid4()),
                    user_id=lesson_id,  # Will be updated with actual user_id
                    lesson_id=lesson_id,
                    title=work.get('title', 'Untitled Assignment'),
                    description=work.get('description', ''),
                    status='pending',
                    due_date=work.get('dueDate', {}).get('date', None),
                    points=work.get('maxPoints', 100)
                )
                db.session.add(task)
            
            db.session.commit()
            
        except Exception as e:
            print(f"Error importing assignments: {e}")
            db.session.rollback()
    
    def _import_materials(self, lesson_id: str, materials: List[Dict[str, Any]]):
        """Import materials from Google Classroom"""
        try:
            from app.models.note import NoteModel
            
            for material in materials:
                note = NoteModel(
                    id=str(uuid.uuid4()),
                    user_id=lesson_id,  # Will be updated with actual user_id
                    lesson_id=lesson_id,
                    title=material.get('title', 'Untitled Material'),
                    content=material.get('description', ''),
                    note_type='material'
                )
                db.session.add(note)
            
            db.session.commit()
            
        except Exception as e:
            print(f"Error importing materials: {e}")
            db.session.rollback()
    
    def _import_announcements(self, lesson_id: str, announcements: List[Dict[str, Any]]):
        """Import announcements from Google Classroom"""
        try:
            from app.models.announcement import AnnouncementModel
            
            for announcement in announcements:
                ann = AnnouncementModel(
                    id=str(uuid.uuid4()),
                    lesson_id=lesson_id,
                    user_id=lesson_id,  # Will be updated with actual user_id
                    title=announcement.get('text', 'Announcement'),
                    content=announcement.get('text', ''),
                    created_at=announcement.get('creationTime', datetime.now())
                )
                db.session.add(ann)
            
            db.session.commit()
            
        except Exception as e:
            print(f"Error importing announcements: {e}")
            db.session.rollback()
