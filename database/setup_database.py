"""
Database Setup Script
Creates all necessary tables and columns for the Smart Learning Hub system
"""

import sqlite3
import os
from datetime import datetime

def create_complete_database_schema():
    """Create complete database schema with all tables and columns"""
    
    # Database path
    db_path = 'instance/site.db'
    
    # Create instance directory if not exists
    os.makedirs('instance', exist_ok=True)
    
    # Connect to database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        print("🔧 Creating complete database schema...")
        
        # 1. Create user table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user (
                id TEXT PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                first_name TEXT,
                last_name TEXT,
                profile_image TEXT,
                bio TEXT,
                role TEXT DEFAULT 'student',
                preferences TEXT,
                is_active BOOLEAN DEFAULT 1,
                email_verified BOOLEAN DEFAULT 0,
                last_login TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                total_lessons INTEGER DEFAULT 0,
                total_notes INTEGER DEFAULT 0,
                total_tasks INTEGER DEFAULT 0
            )
        """)
        print("✅ Created user table")
        
        # Add missing columns to user table if they don't exist
        user_columns = [
            "ALTER TABLE user ADD COLUMN first_name TEXT",
            "ALTER TABLE user ADD COLUMN last_name TEXT",
            "ALTER TABLE user ADD COLUMN profile_image TEXT",
            "ALTER TABLE user ADD COLUMN bio TEXT",
            "ALTER TABLE user ADD COLUMN preferences TEXT",
            "ALTER TABLE user ADD COLUMN last_login TIMESTAMP"
        ]
        
        for column_sql in user_columns:
            try:
                cursor.execute(column_sql)
            except sqlite3.OperationalError as e:
                if "duplicate column name" in str(e):
                    print(f"   User column already exists, skipping...")
                else:
                    print(f"   Warning: {e}")
        
        print("✅ Updated user table columns")
        
        # 2. Create lesson table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS lesson (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                title TEXT NOT NULL,
                description TEXT,
                content TEXT,
                status TEXT DEFAULT 'not_started',
                color_theme INTEGER DEFAULT 1,
                is_favorite BOOLEAN DEFAULT 0,
                difficulty_level TEXT DEFAULT 'beginner',
                estimated_duration INTEGER DEFAULT 0,
                author_name TEXT,
                tags TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES user(id)
            )
        """)
        print("✅ Created lesson table")
        
        # Add missing columns to lesson table if they don't exist
        lesson_columns = [
            "ALTER TABLE lesson ADD COLUMN tags TEXT",
            "ALTER TABLE lesson ADD COLUMN status TEXT DEFAULT 'not_started'",
            "ALTER TABLE lesson ADD COLUMN color_theme INTEGER DEFAULT 1",
            "ALTER TABLE lesson ADD COLUMN is_favorite BOOLEAN DEFAULT 0",
            "ALTER TABLE lesson ADD COLUMN difficulty_level TEXT DEFAULT 'beginner'",
            "ALTER TABLE lesson ADD COLUMN estimated_duration INTEGER DEFAULT 0",
            "ALTER TABLE lesson ADD COLUMN author_name TEXT",
            "ALTER TABLE lesson ADD COLUMN progress_percentage INTEGER DEFAULT 0",
            "ALTER TABLE lesson ADD COLUMN total_sections INTEGER DEFAULT 0",
            "ALTER TABLE lesson ADD COLUMN completed_sections INTEGER DEFAULT 0",
            "ALTER TABLE lesson ADD COLUMN total_time_spent INTEGER DEFAULT 0",
            "ALTER TABLE lesson ADD COLUMN source_platform TEXT DEFAULT 'manual'",
            "ALTER TABLE lesson ADD COLUMN external_id TEXT",
            "ALTER TABLE lesson ADD COLUMN external_url TEXT",
            "ALTER TABLE lesson ADD COLUMN subject TEXT",
            "ALTER TABLE lesson ADD COLUMN grade_level TEXT"
        ]
        
        for column_sql in lesson_columns:
            try:
                cursor.execute(column_sql)
            except sqlite3.OperationalError as e:
                if "duplicate column name" in str(e):
                    print(f"   Lesson column already exists, skipping...")
                else:
                    print(f"   Warning: {e}")
        
        print("✅ Updated lesson table columns")
        
        # 3. Create note table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS note (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                lesson_id TEXT,
                title TEXT NOT NULL,
                content TEXT,
                status TEXT DEFAULT 'pending',
                tags TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES user(id),
                FOREIGN KEY (lesson_id) REFERENCES lesson(id)
            )
        """)
        print("✅ Created note table")
        
        # Add missing columns to note table if they don't exist
        note_columns = [
            "ALTER TABLE note ADD COLUMN note_type TEXT DEFAULT 'text'",
            "ALTER TABLE note ADD COLUMN section_id TEXT",
            "ALTER TABLE note ADD COLUMN is_public BOOLEAN DEFAULT 0",
            "ALTER TABLE note ADD COLUMN view_count INTEGER DEFAULT 0",
            "ALTER TABLE note ADD COLUMN word_count INTEGER DEFAULT 0",
            "ALTER TABLE note ADD COLUMN status TEXT DEFAULT 'pending'",
            "ALTER TABLE note ADD COLUMN external_link TEXT"
        ]
        
        for column_sql in note_columns:
            try:
                cursor.execute(column_sql)
            except sqlite3.OperationalError as e:
                if "duplicate column name" in str(e):
                    print(f"   Note column already exists, skipping...")
                else:
                    print(f"   Warning: {e}")
        
        print("✅ Updated note table columns")
        
        # 4. Create note_file table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS note_file (
                id TEXT PRIMARY KEY,
                note_id TEXT NOT NULL,
                file_path TEXT NOT NULL,
                file_type TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (note_id) REFERENCES note(id) ON DELETE CASCADE
            )
        """)
        print("✅ Created note_file table")
        
        # 5. Create task table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS task (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                title TEXT NOT NULL,
                description TEXT,
                status TEXT DEFAULT 'pending',
                priority TEXT DEFAULT 'medium',
                due_date TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES user(id)
            )
        """)
        print("✅ Created task table")
        
        # 6. Create announcement table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS announcement (
                id TEXT PRIMARY KEY,
                lesson_id TEXT NOT NULL,
                user_id TEXT NOT NULL,
                title TEXT NOT NULL,
                content TEXT,
                status TEXT DEFAULT 'active',
                is_pinned BOOLEAN DEFAULT 0,
                allow_comments BOOLEAN DEFAULT 1,
                scheduled_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (lesson_id) REFERENCES lesson(id),
                FOREIGN KEY (user_id) REFERENCES user(id)
            )
        """)
        print("✅ Created announcement table")
        
        # 7. Create announcement_comment table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS announcement_comment (
                id TEXT PRIMARY KEY,
                announcement_id TEXT NOT NULL,
                user_id TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (announcement_id) REFERENCES announcement(id) ON DELETE CASCADE,
                FOREIGN KEY (user_id) REFERENCES user(id)
            )
        """)
        print("✅ Created announcement_comment table")
        
        # 8. Create assignment table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS assignment (
                id TEXT PRIMARY KEY,
                lesson_id TEXT NOT NULL,
                user_id TEXT NOT NULL,
                title TEXT NOT NULL,
                description TEXT,
                due_date TIMESTAMP,
                points INTEGER DEFAULT 0,
                status TEXT DEFAULT 'active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (lesson_id) REFERENCES lesson(id),
                FOREIGN KEY (user_id) REFERENCES user(id)
            )
        """)
        print("✅ Created assignment table")
        
        # 9. Create member table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS member (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                lesson_id TEXT NOT NULL,
                role TEXT DEFAULT 'student',
                joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES user(id),
                FOREIGN KEY (lesson_id) REFERENCES lesson(id)
            )
        """)
        print("✅ Created member table")
        
        # 10. Create database indexes
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_user_email ON user(email)",
            "CREATE INDEX IF NOT EXISTS idx_user_username ON user(username)",
            "CREATE INDEX IF NOT EXISTS idx_lesson_user_id ON lesson(user_id)",
            "CREATE INDEX IF NOT EXISTS idx_lesson_status ON lesson(status)",
            "CREATE INDEX IF NOT EXISTS idx_note_user_id ON note(user_id)",
            "CREATE INDEX IF NOT EXISTS idx_note_lesson_id ON note(lesson_id)",
            "CREATE INDEX IF NOT EXISTS idx_task_user_id ON task(user_id)",
            "CREATE INDEX IF NOT EXISTS idx_task_status ON task(status)",
            "CREATE INDEX IF NOT EXISTS idx_announcement_lesson_id ON announcement(lesson_id)",
            "CREATE INDEX IF NOT EXISTS idx_announcement_user_id ON announcement(user_id)",
            "CREATE INDEX IF NOT EXISTS idx_assignment_lesson_id ON assignment(lesson_id)",
            "CREATE INDEX IF NOT EXISTS idx_member_user_id ON member(user_id)",
            "CREATE INDEX IF NOT EXISTS idx_member_lesson_id ON member(lesson_id)"
        ]
        
        for index_sql in indexes:
            try:
                cursor.execute(index_sql)
            except sqlite3.OperationalError as e:
                print(f"   Warning: {e}")
        
        print("✅ Created database indexes")
        
        # 11. Create uploads directories
        upload_dirs = [
            'uploads',
            'uploads/notes',
            'uploads/lessons',
            'uploads/assignments',
            'uploads/announcements'
        ]
        
        for dir_path in upload_dirs:
            os.makedirs(dir_path, exist_ok=True)
        
        print("✅ Created uploads directories")
        
        # 12. Create pomodoro tables
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS pomodoro_session (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                session_type TEXT NOT NULL,
                duration INTEGER NOT NULL,
                actual_duration INTEGER,
                start_time TIMESTAMP NOT NULL,
                end_time TIMESTAMP,
                status TEXT DEFAULT 'active',
                productivity_score INTEGER,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES user(id)
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS pomodoro_statistics (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                date DATE NOT NULL,
                total_sessions INTEGER DEFAULT 0,
                total_focus_time INTEGER DEFAULT 0,
                total_break_time INTEGER DEFAULT 0,
                productivity_score REAL DEFAULT 0.0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES user(id)
            )
        """)
        
        print("✅ Created pomodoro tables")
        
        # 13. Create classwork tables
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS classwork_task (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                lesson_id TEXT NOT NULL,
                title TEXT NOT NULL,
                description TEXT,
                subject TEXT,
                category TEXT,
                priority TEXT DEFAULT 'medium',
                status TEXT DEFAULT 'todo',
                due_date TIMESTAMP,
                estimated_time INTEGER DEFAULT 0,
                actual_time INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES user(id),
                FOREIGN KEY (lesson_id) REFERENCES lesson(id)
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS classwork_material (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                lesson_id TEXT NOT NULL,
                task_id TEXT,
                title TEXT NOT NULL,
                description TEXT,
                file_path TEXT,
                file_type TEXT,
                file_size INTEGER,
                subject TEXT,
                category TEXT,
                tags TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES user(id),
                FOREIGN KEY (lesson_id) REFERENCES lesson(id),
                FOREIGN KEY (task_id) REFERENCES classwork_task(id)
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS classwork_note (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                lesson_id TEXT NOT NULL,
                task_id TEXT,
                title TEXT NOT NULL,
                content TEXT,
                subject TEXT,
                category TEXT,
                tags TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES user(id),
                FOREIGN KEY (lesson_id) REFERENCES lesson(id),
                FOREIGN KEY (task_id) REFERENCES classwork_task(id)
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS classwork_session (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                lesson_id TEXT NOT NULL,
                task_id TEXT,
                session_name TEXT,
                start_time TIMESTAMP,
                end_time TIMESTAMP,
                duration INTEGER DEFAULT 0,
                break_duration INTEGER DEFAULT 0,
                productivity_score INTEGER DEFAULT 0,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES user(id),
                FOREIGN KEY (lesson_id) REFERENCES lesson(id),
                FOREIGN KEY (task_id) REFERENCES classwork_task(id)
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS classwork_progress (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                lesson_id TEXT NOT NULL,
                task_id TEXT,
                progress_percentage INTEGER DEFAULT 0,
                completed_at TIMESTAMP,
                time_spent INTEGER DEFAULT 0,
                achievement_badges TEXT,
                streak_count INTEGER DEFAULT 0,
                last_activity TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES user(id),
                FOREIGN KEY (lesson_id) REFERENCES lesson(id),
                FOREIGN KEY (task_id) REFERENCES classwork_task(id)
            )
        """)
        
        print("✅ Created classwork tables")
        
        # 14. Create classwork indexes
        classwork_indexes = [
            "CREATE INDEX IF NOT EXISTS idx_classwork_task_user_id ON classwork_task(user_id)",
            "CREATE INDEX IF NOT EXISTS idx_classwork_task_lesson_id ON classwork_task(lesson_id)",
            "CREATE INDEX IF NOT EXISTS idx_classwork_task_status ON classwork_task(status)",
            "CREATE INDEX IF NOT EXISTS idx_classwork_task_priority ON classwork_task(priority)",
            "CREATE INDEX IF NOT EXISTS idx_classwork_task_due_date ON classwork_task(due_date)",
            "CREATE INDEX IF NOT EXISTS idx_classwork_material_user_id ON classwork_material(user_id)",
            "CREATE INDEX IF NOT EXISTS idx_classwork_material_lesson_id ON classwork_material(lesson_id)",
            "CREATE INDEX IF NOT EXISTS idx_classwork_material_task_id ON classwork_material(task_id)",
            "CREATE INDEX IF NOT EXISTS idx_classwork_material_subject ON classwork_material(subject)",
            "CREATE INDEX IF NOT EXISTS idx_classwork_note_user_id ON classwork_note(user_id)",
            "CREATE INDEX IF NOT EXISTS idx_classwork_note_lesson_id ON classwork_note(lesson_id)",
            "CREATE INDEX IF NOT EXISTS idx_classwork_note_task_id ON classwork_note(task_id)",
            "CREATE INDEX IF NOT EXISTS idx_classwork_session_user_id ON classwork_session(user_id)",
            "CREATE INDEX IF NOT EXISTS idx_classwork_session_lesson_id ON classwork_session(lesson_id)",
            "CREATE INDEX IF NOT EXISTS idx_classwork_session_task_id ON classwork_session(task_id)",
            "CREATE INDEX IF NOT EXISTS idx_classwork_progress_user_id ON classwork_progress(user_id)",
            "CREATE INDEX IF NOT EXISTS idx_classwork_progress_lesson_id ON classwork_progress(lesson_id)",
            "CREATE INDEX IF NOT EXISTS idx_classwork_progress_task_id ON classwork_progress(task_id)"
        ]
        
        for index_sql in classwork_indexes:
            try:
                cursor.execute(index_sql)
            except sqlite3.OperationalError as e:
                print(f"   Warning: {e}")
        
        print("✅ Created classwork indexes")
        
        # 15. Create classwork uploads directory
        classwork_upload_dir = 'uploads/classwork'
        os.makedirs(classwork_upload_dir, exist_ok=True)
        print("✅ Created classwork uploads directory")
        
        # Commit all changes
        conn.commit()
        print("🎉 Complete database schema created successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error creating database schema: {e}")
        conn.rollback()
        return False
        
    finally:
        conn.close()

if __name__ == "__main__":
    create_complete_database_schema()
