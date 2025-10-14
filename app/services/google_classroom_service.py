"""
Google Classroom Service
Handles Google Classroom API integration
"""

import json
import os
from typing import List, Dict, Optional
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app import db
from app.models.user import UserModel


class GoogleClassroomService:
    """Service for Google Classroom API operations"""
    
    def __init__(self):
        self.client_id = os.environ.get('GOOGLE_CLIENT_ID')
        self.client_secret = os.environ.get('GOOGLE_CLIENT_SECRET')
        self.scopes = [
            'https://www.googleapis.com/auth/classroom.courses.readonly',
            'https://www.googleapis.com/auth/classroom.rosters.readonly',
            'https://www.googleapis.com/auth/classroom.course-work.readonly',
            'https://www.googleapis.com/auth/classroom.announcements.readonly',
            'https://www.googleapis.com/auth/classroom.courseworkmaterials.readonly',
            'https://www.googleapis.com/auth/userinfo.profile',
            'https://www.googleapis.com/auth/userinfo.email',
            'https://www.googleapis.com/auth/drive.readonly'
        ]
    
    def get_credentials(self, user_id: str) -> Optional[Credentials]:
        """Get stored credentials for user"""
        try:
            user = UserModel.query.filter_by(id=user_id).first()
            if not user or not user.google_credentials:
                print(f"No Google credentials found for user {user_id}")
                return None
            
            creds_data = json.loads(user.google_credentials)
            print(f"Found credentials for user {user_id}: {creds_data.get('token', '')[:20]}...")
            
            credentials = Credentials(
                token=creds_data.get('token'),
                refresh_token=creds_data.get('refresh_token'),
                token_uri=creds_data.get('token_uri', 'https://oauth2.googleapis.com/token'),
                client_id=creds_data.get('client_id', self.client_id),
                client_secret=creds_data.get('client_secret', self.client_secret),
                scopes=creds_data.get('scopes', self.scopes)
            )
            
            # Refresh token if needed
            if credentials.expired and credentials.refresh_token:
                print(f"Token expired for user {user_id}, refreshing...")
                credentials.refresh(Request())
                self.save_credentials(user_id, credentials)
                print(f"Token refreshed for user {user_id}")
            
            return credentials
            
        except Exception as e:
            print(f"Error getting credentials for user {user_id}: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def save_credentials(self, user_id: str, credentials: Credentials) -> bool:
        """Save credentials for user"""
        try:
            user = UserModel.query.filter_by(id=user_id).first()
            if not user:
                return False
            
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
            
            return True
            
        except Exception as e:
            print(f"Error saving credentials for user {user_id}: {e}")
            return False
    
    def fetch_courses(self, user_id: str) -> List[Dict]:
        """Fetch Google Classroom courses for user"""
        try:
            print(f"Fetching courses for user {user_id}")
            credentials = self.get_credentials(user_id)
            if not credentials:
                raise Exception("No valid credentials found")
            
            print(f"Building Google Classroom service for user {user_id}")
            # Build Google Classroom service
            service = build('classroom', 'v1', credentials=credentials)
            
            print(f"Fetching courses from Google Classroom API...")
            # Fetch courses
            results = service.courses().list(
                courseStates=['ACTIVE'],
                pageSize=100
            ).execute()
            
            courses = results.get('courses', [])
            print(f"Found {len(courses)} courses from Google Classroom")
            
            # Process each course to get additional details
            processed_courses = []
            for course in courses:
                course_id = course.get('id')
                course_name = course.get('name', 'Untitled Course')
                print(f"Processing course: {course_name} (ID: {course_id})")
                
                # Get students count
                try:
                    students_result = service.courses().students().list(
                        courseId=course_id,
                        pageSize=1000
                    ).execute()
                    students_count = len(students_result.get('students', []))
                    print(f"  - Students: {students_count}")
                except Exception as e:
                    print(f"  - Error getting students: {e}")
                    students_count = 0
                
                # Get course work count
                try:
                    coursework_result = service.courses().courseWork().list(
                        courseId=course_id,
                        pageSize=1000
                    ).execute()
                    assignments_count = len(coursework_result.get('courseWork', []))
                    print(f"  - Assignments: {assignments_count}")
                except Exception as e:
                    print(f"  - Error getting assignments: {e}")
                    assignments_count = 0
                
                # Get announcements count
                try:
                    announcements_result = service.courses().announcements().list(
                        courseId=course_id,
                        pageSize=1000
                    ).execute()
                    announcements_count = len(announcements_result.get('announcements', []))
                    print(f"  - Announcements: {announcements_count}")
                except Exception as e:
                    print(f"  - Error getting announcements: {e}")
                    announcements_count = 0
                
                # Get course work materials count
                try:
                    materials_result = service.courses().courseWorkMaterials().list(
                        courseId=course_id,
                        pageSize=1000
                    ).execute()
                    materials_count = len(materials_result.get('courseWorkMaterial', []))
                    print(f"  - Materials: {materials_count}")
                except Exception as e:
                    print(f"  - Error getting materials: {e}")
                    materials_count = 0
                
                processed_course = {
                    'id': course_id,
                    'name': course_name,
                    'description': course.get('description', ''),
                    'section': course.get('section', ''),
                    'room': course.get('room', ''),
                    'ownerId': course.get('ownerId', ''),
                    'creationTime': course.get('creationTime', ''),
                    'updateTime': course.get('updateTime', ''),
                    'enrollmentCode': course.get('enrollmentCode', ''),
                    'courseState': course.get('courseState', ''),
                    'studentsCount': students_count,
                    'assignmentsCount': assignments_count,
                    'materialsCount': materials_count,
                    'announcementsCount': announcements_count
                }
                
                processed_courses.append(processed_course)
            
            print(f"Successfully processed {len(processed_courses)} courses")
            return processed_courses
            
        except Exception as e:
            print(f"Error fetching courses for user {user_id}: {e}")
            import traceback
            traceback.print_exc()
            raise e
    
    def import_course(self, user_id: str, course_id: str, settings: Dict) -> Dict:
        """Import a Google Classroom course"""
        try:
            credentials = self.get_credentials(user_id)
            if not credentials:
                raise Exception("No valid credentials found")
            
            # Build Google Classroom service
            service = build('classroom', 'v1', credentials=credentials)
            
            # Get course details
            course = service.courses().get(id=course_id).execute()
            
            # Create lesson in our system
            from app.services import LessonService
            lesson_service = LessonService()
            
            lesson_data = {
                'title': f"Imported: {course.get('name', 'Google Classroom Course')}",
                'description': course.get('description', '') or f'Imported from Google Classroom - {course_id}',
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
                try:
                    students_result = service.courses().students().list(
                        courseId=course_id,
                        pageSize=1000
                    ).execute()
                    
                    students = students_result.get('students', [])
                    print(f"Found {len(students)} students to import")
                    # TODO: Import students to lesson
                    
                except Exception as e:
                    print(f"Error importing students: {e}")
            
            # Import assignments if requested
            if settings.get('importAssignments', True):
                try:
                    coursework_result = service.courses().courseWork().list(
                        courseId=course_id,
                        pageSize=1000
                    ).execute()
                    
                    assignments = coursework_result.get('courseWork', [])
                    print(f"Found {len(assignments)} assignments to import")
                    # TODO: Import assignments to lesson
                    
                except Exception as e:
                    print(f"Error importing assignments: {e}")
            
            # Import materials if requested
            if settings.get('importMaterials', True):
                try:
                    materials_result = service.courses().courseWorkMaterials().list(
                        courseId=course_id,
                        pageSize=1000
                    ).execute()
                    
                    materials = materials_result.get('courseWorkMaterial', [])
                    print(f"Found {len(materials)} materials to import")
                    # TODO: Import materials to lesson
                    
                except Exception as e:
                    print(f"Error importing materials: {e}")
            
            # Import announcements if requested
            if settings.get('importAnnouncements', True):
                try:
                    announcements_result = service.courses().announcements().list(
                        courseId=course_id,
                        pageSize=1000
                    ).execute()
                    
                    announcements = announcements_result.get('announcements', [])
                    print(f"Found {len(announcements)} announcements to import")
                    # TODO: Import announcements to lesson
                    
                except Exception as e:
                    print(f"Error importing announcements: {e}")
            
            return {
                'success': True,
                'message': 'Course imported successfully',
                'lesson_id': lesson.id,
                'course_name': course.get('name', 'Unknown Course')
            }
            
        except Exception as e:
            print(f"Error importing course {course_id} for user {user_id}: {e}")
            return {
                'success': False,
                'error': f'Failed to import course: {str(e)}'
            }