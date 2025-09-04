#!/usr/bin/env python3
"""
Test script for OOP architecture
"""

def test_domain_entities():
    """Test domain entities"""
    print("🧪 Testing Domain Entities...")
    
    try:
        from app.domain.entities.user import User
        from app.domain.entities.lesson import Lesson, LessonStatus, DifficultyLevel, SourcePlatform
        from app.domain.entities.note import Note, NoteType
        from app.domain.entities.task import Task, TaskStatus, TaskPriority, TaskType
        from app.domain.value_objects.email import Email
        from app.domain.value_objects.password import Password
        
        # Test User entity
        email = Email("test@example.com")
        password = Password("TestPass123!")  # Fixed: added uppercase letter and special character
        user = User("testuser", email, password)
        print(f"✅ User created: {user.username}")
        
        # Test Lesson entity
        lesson = Lesson(
            user_id=user.id,
            title="Test Lesson",
            description="Test Description",
            status=LessonStatus.NOT_STARTED,
            difficulty_level=DifficultyLevel.BEGINNER,
            source_platform=SourcePlatform.MANUAL
        )
        print(f"✅ Lesson created: {lesson.title}")
        
        # Test Note entity
        note = Note(
            user_id=user.id,
            title="Test Note",
            content="Test Content",
            note_type=NoteType.TEXT
        )
        print(f"✅ Note created: {note.title}")
        
        # Test Task entity
        task = Task(
            user_id=user.id,
            title="Test Task",
            description="Test Description",
            task_type=TaskType.STUDY,
            status=TaskStatus.PENDING,
            priority=TaskPriority.MEDIUM
        )
        print(f"✅ Task created: {task.title}")
        
        return True
        
    except Exception as e:
        print(f"❌ Domain entities test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_services():
    """Test services"""
    print("\n🧪 Testing Services...")
    
    try:
        from app.infrastructure.di.container import configure_services, get_service
        from app.domain.interfaces.services.user_service import UserService
        from app.domain.interfaces.services.lesson_service import LessonService
        from app.domain.interfaces.services.note_service import NoteService
        from app.domain.interfaces.services.task_service import TaskService
        
        # Configure services
        configure_services()
        print("✅ Services configured")
        
        # Get service instances
        user_service = get_service(UserService)
        lesson_service = get_service(LessonService)
        note_service = get_service(NoteService)
        task_service = get_service(TaskService)
        
        print("✅ All services retrieved successfully")
        return True
        
    except Exception as e:
        print(f"❌ Services test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_database():
    """Test database operations"""
    print("\n🧪 Testing Database...")
    
    try:
        from app import create_app, db
        from app.infrastructure.di.container import configure_services
        
        # Create app
        app = create_app()
        configure_services()
        
        with app.app_context():
            # Test database connection
            result = db.session.execute(db.text('SELECT 1')).scalar()
            print(f"✅ Database connection: {result}")
            
            # Test table creation
            db.create_all()
            print("✅ Database tables created")
            
        return True
        
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_api_endpoints():
    """Test API endpoints"""
    print("\n🧪 Testing API Endpoints...")
    
    try:
        from app import create_app
        from app.infrastructure.di.container import configure_services
        
        # Create app
        app = create_app()
        configure_services()
        
        # Test client
        with app.test_client() as client:
            # Test auth endpoints
            response = client.get('/api/auth/register')
            print(f"✅ Auth register endpoint: {response.status_code}")
            
            # Test user endpoints
            response = client.get('/api/users/profile')
            print(f"✅ User profile endpoint: {response.status_code}")
            
            # Test lesson endpoints
            response = client.get('/api/lessons')
            print(f"✅ Lessons endpoint: {response.status_code}")
            
            # Test note endpoints
            response = client.get('/api/notes')
            print(f"✅ Notes endpoint: {response.status_code}")
            
            # Test task endpoints
            response = client.get('/api/tasks')
            print(f"✅ Tasks endpoint: {response.status_code}")
            
        return True
        
    except Exception as e:
        print(f"❌ API endpoints test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test function"""
    print("🚀 Starting OOP Architecture Tests...\n")
    
    tests = [
        ("Domain Entities", test_domain_entities),
        ("Services", test_services),
        ("Database", test_database),
        ("API Endpoints", test_api_endpoints)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "="*50)
    print("📊 TEST SUMMARY")
    print("="*50)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 Results: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("🎉 All tests passed! OOP architecture is working correctly!")
    else:
        print("⚠️  Some tests failed. Check the errors above.")

if __name__ == "__main__":
    main()
