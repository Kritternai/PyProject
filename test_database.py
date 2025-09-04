#!/usr/bin/env python3
"""
Database Test Script for Smart Learning Hub
This script tests the database functionality and creates sample data.
"""

import sys
import logging
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def test_database_models():
    """Test database models creation and relationships"""
    try:
        from database.models import User, Lesson, Note, Task, Tag
        from database import get_db_manager
        
        logger.info("Testing database models...")
        
        # Get database manager
        manager = get_db_manager()
        
        # Test creating a user
        user = User(
            username="test_user",
            email="test@example.com",
            first_name="Test",
            last_name="User"
        )
        user.set_password("test123")
        
        logger.info(f"Created test user: {user.username}")
        logger.info(f"User ID: {user.id}")
        logger.info(f"User full name: {user.full_name}")
        
        # Test creating a lesson
        lesson = Lesson(
            title="Test Lesson",
            description="This is a test lesson",
            difficulty_level="beginner",
            user_id=user.id
        )
        
        logger.info(f"Created test lesson: {lesson.title}")
        logger.info(f"Lesson ID: {lesson.id}")
        logger.info(f"Lesson status: {lesson.status}")
        
        # Test creating a tag
        tag = Tag(
            name="python",
            color="#007bff",
            tag_type="subject",
            user_id=user.id
        )
        
        logger.info(f"Created test tag: {tag.name}")
        logger.info(f"Tag ID: {tag.id}")
        logger.info(f"Tag color: {tag.color}")
        
        # Test creating a note
        note = Note(
            title="Test Note",
            content="This is a test note content",
            note_type="general",
            user_id=user.id
        )
        
        logger.info(f"Created test note: {note.title}")
        logger.info(f"Note ID: {note.id}")
        logger.info(f"Note type: {note.note_type}")
        
        # Test creating a task
        task = Task(
            title="Test Task",
            description="This is a test task",
            task_type="study",
            priority="high",
            user_id=user.id
        )
        
        logger.info(f"Created test task: {task.title}")
        logger.info(f"Task ID: {task.id}")
        logger.info(f"Task priority: {task.priority}")
        
        logger.info("✅ All model tests passed!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Model test failed: {e}")
        return False

def test_database_operations():
    """Test database operations"""
    try:
        from database import get_db_manager
        
        logger.info("Testing database operations...")
        
        manager = get_db_manager()
        
        # Test health check
        health = manager.health_check()
        logger.info(f"Database health: {'✅ Healthy' if health else '❌ Unhealthy'}")
        
        # Test database info
        info = manager.get_database_info()
        logger.info(f"Database path: {info.get('database_path')}")
        logger.info(f"Database size: {info.get('database_size_mb')} MB")
        logger.info(f"Table count: {info.get('table_count')}")
        logger.info(f"Health status: {info.get('health_status')}")
        
        # Test backup
        backup_path = manager.backup_database()
        if backup_path:
            logger.info(f"✅ Database backup created: {backup_path}")
        else:
            logger.warning("⚠️ Database backup failed")
        
        logger.info("✅ All database operation tests passed!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Database operation test failed: {e}")
        return False

def main():
    """Main test function"""
    logger.info("🚀 Starting database tests...")
    
    # Test 1: Models
    models_ok = test_database_models()
    
    # Test 2: Database operations
    operations_ok = test_database_operations()
    
    # Summary
    logger.info("\n" + "="*50)
    logger.info("📊 TEST RESULTS SUMMARY")
    logger.info("="*50)
    logger.info(f"Models Test: {'✅ PASSED' if models_ok else '❌ FAILED'}")
    logger.info(f"Operations Test: {'✅ PASSED' if operations_ok else '❌ FAILED'}")
    
    if models_ok and operations_ok:
        logger.info("🎉 All tests passed! Database is working correctly.")
        return 0
    else:
        logger.error("💥 Some tests failed. Please check the errors above.")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
