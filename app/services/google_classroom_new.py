"""
Google Classroom Service - New Complete Implementation
บริการสำหรับการจัดการ Google Classroom API
"""

import os
import json
from typing import Dict, List, Optional, Any
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import logging

logger = logging.getLogger(__name__)

class GoogleClassroomService:
    """Google Classroom Service สำหรับจัดการ API calls"""
    
    def __init__(self):
        self.client_id = os.environ.get('GOOGLE_CLIENT_ID')
        self.client_secret = os.environ.get('GOOGLE_CLIENT_SECRET')
        
    def create_credentials_from_dict(self, creds_data: Dict[str, Any]) -> Credentials:
        """สร้าง Credentials object จาก dictionary"""
        try:
            return Credentials(
                token=creds_data['token'],
                refresh_token=creds_data.get('refresh_token'),
                token_uri=creds_data.get('token_uri', 'https://oauth2.googleapis.com/token'),
                client_id=creds_data.get('client_id', self.client_id),
                client_secret=creds_data.get('client_secret', self.client_secret),
                scopes=creds_data.get('scopes', [])
            )
        except Exception as e:
            logger.error(f"Error creating credentials: {e}")
            raise
    
    def build_classroom_service(self, credentials: Credentials):
        """สร้าง Google Classroom API service"""
        try:
            # Refresh credentials if needed
            if credentials.expired:
                credentials.refresh(Request())
            
            return build('classroom', 'v1', credentials=credentials)
        except Exception as e:
            logger.error(f"Error building classroom service: {e}")
            raise
    
    def fetch_courses(self, credentials: Credentials) -> List[Dict[str, Any]]:
        """ดึงรายการ courses จาก Google Classroom"""
        try:
            service = self.build_classroom_service(credentials)
            
            # ดึง courses ที่ active
            results = service.courses().list(courseStates=['ACTIVE']).execute()
            courses = results.get('courses', [])
            
            # จัดรูปแบบข้อมูล courses
            formatted_courses = []
            for course in courses:
                formatted_course = {
                    'id': course['id'],
                    'name': course['name'],
                    'section': course.get('section', ''),
                    'description': course.get('description', ''),
                    'room': course.get('room', ''),
                    'ownerId': course.get('ownerId', ''),
                    'courseState': course.get('courseState', 'ACTIVE'),
                    'creationTime': course.get('creationTime', ''),
                    'updateTime': course.get('updateTime', ''),
                    'enrollmentCode': course.get('enrollmentCode', ''),
                    'teacherGroupEmail': course.get('teacherGroupEmail', ''),
                    'courseGroupEmail': course.get('courseGroupEmail', ''),
                    'guardiansEnabled': course.get('guardiansEnabled', False),
                    'calendarId': course.get('calendarId', ''),
                    'alternateLink': course.get('alternateLink', ''),
                    'courseCreator': course.get('courseCreator', '')
                }
                formatted_courses.append(formatted_course)
            
            logger.info(f"Fetched {len(formatted_courses)} courses from Google Classroom")
            return formatted_courses
            
        except HttpError as e:
            logger.error(f"Google Classroom API error: {e}")
            raise
        except Exception as e:
            logger.error(f"Error fetching courses: {e}")
            raise
    
    def fetch_course_details(self, credentials: Credentials, course_id: str) -> Dict[str, Any]:
        """ดึงรายละเอียด course จาก Google Classroom"""
        try:
            service = self.build_classroom_service(credentials)
            
            # ดึงข้อมูล course
            course = service.courses().get(id=course_id).execute()
            
            # ดึงข้อมูล students
            students = []
            try:
                students_result = service.courses().students().list(courseId=course_id).execute()
                students = students_result.get('students', [])
            except HttpError:
                logger.warning(f"Could not fetch students for course {course_id}")
            
            # ดึงข้อมูล teachers
            teachers = []
            try:
                teachers_result = service.courses().teachers().list(courseId=course_id).execute()
                teachers = teachers_result.get('teachers', [])
            except HttpError:
                logger.warning(f"Could not fetch teachers for course {course_id}")
            
            # ดึงข้อมูล course work
            course_work = []
            try:
                course_work_result = service.courses().courseWork().list(courseId=course_id).execute()
                course_work = course_work_result.get('courseWork', [])
            except HttpError:
                logger.warning(f"Could not fetch course work for course {course_id}")
            
            # ดึงข้อมูล course materials
            course_materials = []
            try:
                materials_result = service.courses().courseWorkMaterials().list(courseId=course_id).execute()
                course_materials = materials_result.get('courseWorkMaterial', [])
            except HttpError:
                logger.warning(f"Could not fetch course materials for course {course_id}")
            
            # ดึงข้อมูล announcements
            announcements = []
            try:
                announcements_result = service.courses().announcements().list(courseId=course_id).execute()
                announcements = announcements_result.get('announcements', [])
            except HttpError:
                logger.warning(f"Could not fetch announcements for course {course_id}")
            
            return {
                'course': course,
                'students': students,
                'teachers': teachers,
                'course_work': course_work,
                'course_materials': course_materials,
                'announcements': announcements,
                'stats': {
                    'student_count': len(students),
                    'teacher_count': len(teachers),
                    'course_work_count': len(course_work),
                    'materials_count': len(course_materials),
                    'announcements_count': len(announcements)
                }
            }
            
        except HttpError as e:
            logger.error(f"Google Classroom API error for course {course_id}: {e}")
            raise
        except Exception as e:
            logger.error(f"Error fetching course details for {course_id}: {e}")
            raise
    
    def test_connection(self, credentials: Credentials) -> Dict[str, Any]:
        """ทดสอบการเชื่อมต่อกับ Google Classroom API"""
        try:
            service = self.build_classroom_service(credentials)
            
            # ทดสอบการดึงข้อมูล profile
            profile = service.userProfiles().get(userId='me').execute()
            
            # ทดสอบการดึงข้อมูล courses
            courses_result = service.courses().list(courseStates=['ACTIVE']).execute()
            courses_count = len(courses_result.get('courses', []))
            
            return {
                'success': True,
                'profile': profile,
                'courses_count': courses_count,
                'message': f'Connected successfully. Found {courses_count} active courses.'
            }
            
        except HttpError as e:
            logger.error(f"Google Classroom API connection error: {e}")
            return {
                'success': False,
                'error': f'API Error: {str(e)}',
                'message': 'Failed to connect to Google Classroom API'
            }
        except Exception as e:
            logger.error(f"Google Classroom connection test error: {e}")
            return {
                'success': False,
                'error': f'Connection Error: {str(e)}',
                'message': 'Failed to connect to Google Classroom'
            }
