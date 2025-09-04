#!/usr/bin/env python3
"""
Test Script for Lesson Creation
This script tests the lesson creation functionality
"""

import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_lesson_creation():
    """Test lesson creation functionality"""
    
    print("🔄 Testing lesson creation...")
    
    try:
        from app import app, db
        from app.core.lesson_manager import LessonManager
        from app.core.user_manager import UserManager
        from app.core.user import User
        from app.core.lesson import Lesson
        
        with app.app_context():
            # Create test user if not exists
            user_manager = UserManager()
            test_user = user_manager.get_user_by_username('test_user')
            
            if not test_user:
                print("📝 Creating test user...")
                test_user = user_manager.add_user(
                    username='test_user',
                    email='test@example.com',
                    password='password123',
                    first_name='Test',
                    last_name='User',
                    role='student'
                )
                print(f"✅ Test user created: {test_user.id}")
            else:
                print(f"✅ Test user exists: {test_user.id}")
            
            # Test lesson creation
            lesson_manager = LessonManager()
            
            print("📚 Testing lesson creation...")
            lesson = lesson_manager.add_lesson(
                user_id=test_user.id,
                title='Test Lesson from Script',
                description='This is a test lesson created from the test script',
                status='not_started',
                tags='test,python,learning',
                source_platform='manual',
                author_name='Test Script',
                selected_color=2
            )
            
            if lesson:
                print(f"✅ Lesson created successfully!")
                print(f"   ID: {lesson.id}")
                print(f"   Title: {lesson.title}")
                print(f"   Status: {lesson.status}")
                print(f"   Color Theme: {lesson.color_theme}")
                print(f"   Author: {lesson.author_name}")
                print(f"   Source Platform: {lesson.source_platform}")
                print(f"   Progress: {lesson.progress_percentage}%")
                print(f"   Is Favorite: {lesson.is_favorite}")
                
                # Test lesson retrieval
                retrieved_lesson = lesson_manager.get_lesson_by_id(lesson.id)
                if retrieved_lesson:
                    print(f"✅ Lesson retrieval successful: {retrieved_lesson.title}")
                else:
                    print("❌ Failed to retrieve lesson")
                
                # Test lessons by user
                user_lessons = lesson_manager.get_lessons_by_user(test_user.id)
                print(f"✅ User has {len(user_lessons)} lessons")
                
                # Test lesson update
                update_success = lesson_manager.update_lesson(
                    lesson.id,
                    status='in_progress',
                    selected_color=3
                )
                if update_success:
                    updated_lesson = lesson_manager.get_lesson_by_id(lesson.id)
                    print(f"✅ Lesson updated: status={updated_lesson.status}, color_theme={updated_lesson.color_theme}")
                else:
                    print("❌ Failed to update lesson")
                
                return True
            else:
                print("❌ Failed to create lesson")
                return False
                
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_lesson_forms():
    """Test lesson form data processing"""
    
    print("\n🔄 Testing lesson form data processing...")
    
    try:
        from app import app
        from app.core.lesson_manager import LessonManager
        from app.core.user_manager import UserManager
        
        with app.app_context():
            # Simulate form data
            form_data = {
                'title': 'Mathematics Basics',
                'description': 'Introduction to basic mathematical concepts',
                'status': 'Not Started',  # Old format
                'tags': 'math,basics,beginner',
                'author_name': 'John Doe',
                'selectedColor': '4',
                'source_platform': 'manual'
            }
            
            # Get test user
            user_manager = UserManager()
            test_user = user_manager.get_user_by_username('test_user')
            
            if not test_user:
                print("❌ Test user not found")
                return False
            
            # Create lesson with form data
            lesson_manager = LessonManager()
            lesson = lesson_manager.add_lesson(
                user_id=test_user.id,
                title=form_data['title'],
                description=form_data['description'],
                status=form_data['status'],
                tags=form_data['tags'],
                source_platform=form_data['source_platform'],
                author_name=form_data['author_name'],
                selected_color=int(form_data['selectedColor'])
            )
            
            if lesson:
                print(f"✅ Form data lesson created successfully!")
                print(f"   Title: {lesson.title}")
                print(f"   Status: {lesson.status} (converted from '{form_data['status']}')")
                print(f"   Color Theme: {lesson.color_theme}")
                print(f"   Author: {lesson.author_name}")
                return True
            else:
                print("❌ Failed to create lesson from form data")
                return False
                
    except Exception as e:
        print(f"❌ Form test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test function"""
    print("🚀 Smart Learning Hub - Lesson Creation Tests")
    print("=" * 50)
    
    success1 = test_lesson_creation()
    success2 = test_lesson_forms()
    
    if success1 and success2:
        print("\n🎉 All tests passed!")
        print("Lesson creation functionality is working correctly.")
        return 0
    else:
        print("\n💥 Some tests failed!")
        print("Please check the error messages above.")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
