"""
Complete Database Migration Script
Creates all necessary tables for the Smart Learning Hub system
"""
import sqlite3
import os
from datetime import datetime

def create_complete_database():
    """Create complete database with all tables"""
    
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
                role TEXT DEFAULT 'student',
                is_active BOOLEAN DEFAULT 1,
                email_verified BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                total_lessons INTEGER DEFAULT 0,
                total_notes INTEGER DEFAULT 0,
                total_tasks INTEGER DEFAULT 0
            )
        """)
        print("✅ Created user table")
        
        # 2. Create lesson table with all columns
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
        
        # 3. Add missing columns to lesson table if they don't exist
        lesson_columns = [
            "ALTER TABLE lesson ADD COLUMN tags TEXT",
            "ALTER TABLE lesson ADD COLUMN status TEXT DEFAULT 'not_started'",
            "ALTER TABLE lesson ADD COLUMN color_theme INTEGER DEFAULT 1",
            "ALTER TABLE lesson ADD COLUMN is_favorite BOOLEAN DEFAULT 0",
            "ALTER TABLE lesson ADD COLUMN difficulty_level TEXT DEFAULT 'beginner'",
            "ALTER TABLE lesson ADD COLUMN estimated_duration INTEGER DEFAULT 0",
            "ALTER TABLE lesson ADD COLUMN author_name TEXT"
        ]
        
        for column_sql in lesson_columns:
            try:
                cursor.execute(column_sql)
            except sqlite3.OperationalError as e:
                if "duplicate column name" in str(e):
                    print(f"   Column already exists, skipping...")
                else:
                    print(f"   Warning: {e}")
        
        print("✅ Updated lesson table columns")
        
        # 4. Create note table
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
        
        # 5. Create note_file table
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
        
        # 6. Create task table
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
        
        # 7. Create announcement table
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
        
        # 8. Create announcement_comment table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS announcement_comment (
                id TEXT PRIMARY KEY,
                announcement_id TEXT NOT NULL,
                user_id TEXT NOT NULL,
                user_name TEXT,
                content TEXT NOT NULL,
                parent_comment_id TEXT,
                is_private BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (announcement_id) REFERENCES announcement(id) ON DELETE CASCADE,
                FOREIGN KEY (user_id) REFERENCES user(id),
                FOREIGN KEY (parent_comment_id) REFERENCES announcement_comment(id)
            )
        """)
        print("✅ Created announcement_comment table")
        
        # 9. Create assignment table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS assignment (
                id TEXT PRIMARY KEY,
                lesson_id TEXT NOT NULL,
                user_id TEXT NOT NULL,
                title TEXT NOT NULL,
                description TEXT,
                instructions TEXT,
                due_date TIMESTAMP,
                points INTEGER DEFAULT 100,
                status TEXT DEFAULT 'draft',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (lesson_id) REFERENCES lesson(id),
                FOREIGN KEY (user_id) REFERENCES user(id)
            )
        """)
        print("✅ Created assignment table")
        
        # 10. Create member table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS member (
                id TEXT PRIMARY KEY,
                lesson_id TEXT NOT NULL,
                user_id TEXT NOT NULL,
                role TEXT DEFAULT 'student',
                joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'active',
                FOREIGN KEY (lesson_id) REFERENCES lesson(id),
                FOREIGN KEY (user_id) REFERENCES user(id),
                UNIQUE(lesson_id, user_id)
            )
        """)
        print("✅ Created member table")
        
        # 11. Create indexes for better performance
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_user_email ON user(email)",
            "CREATE INDEX IF NOT EXISTS idx_user_username ON user(username)",
            "CREATE INDEX IF NOT EXISTS idx_lesson_user_id ON lesson(user_id)",
            "CREATE INDEX IF NOT EXISTS idx_lesson_status ON lesson(status)",
            "CREATE INDEX IF NOT EXISTS idx_lesson_is_favorite ON lesson(is_favorite)",
            "CREATE INDEX IF NOT EXISTS idx_note_user_id ON note(user_id)",
            "CREATE INDEX IF NOT EXISTS idx_note_lesson_id ON note(lesson_id)",
            "CREATE INDEX IF NOT EXISTS idx_note_status ON note(status)",
            "CREATE INDEX IF NOT EXISTS idx_note_created_at ON note(created_at)",
            "CREATE INDEX IF NOT EXISTS idx_note_file_note_id ON note_file(note_id)",
            "CREATE INDEX IF NOT EXISTS idx_task_user_id ON task(user_id)",
            "CREATE INDEX IF NOT EXISTS idx_task_status ON task(status)",
            "CREATE INDEX IF NOT EXISTS idx_announcement_lesson_id ON announcement(lesson_id)",
            "CREATE INDEX IF NOT EXISTS idx_announcement_user_id ON announcement(user_id)",
            "CREATE INDEX IF NOT EXISTS idx_announcement_is_pinned ON announcement(is_pinned)",
            "CREATE INDEX IF NOT EXISTS idx_announcement_created_at ON announcement(created_at)",
            "CREATE INDEX IF NOT EXISTS idx_announcement_comment_announcement_id ON announcement_comment(announcement_id)",
            "CREATE INDEX IF NOT EXISTS idx_announcement_comment_user_id ON announcement_comment(user_id)",
            "CREATE INDEX IF NOT EXISTS idx_announcement_comment_parent_id ON announcement_comment(parent_comment_id)",
            "CREATE INDEX IF NOT EXISTS idx_assignment_lesson_id ON assignment(lesson_id)",
            "CREATE INDEX IF NOT EXISTS idx_assignment_user_id ON assignment(user_id)",
            "CREATE INDEX IF NOT EXISTS idx_member_lesson_id ON member(lesson_id)",
            "CREATE INDEX IF NOT EXISTS idx_member_user_id ON member(user_id)"
        ]
        
        for index_sql in indexes:
            cursor.execute(index_sql)
        
        print("✅ Created database indexes")
        
        # 12. Create uploads directories
        uploads_dirs = [
            'app/static/uploads/notes',
            'app/static/uploads/lessons',
            'app/static/uploads/assignments'
        ]
        
        for upload_dir in uploads_dirs:
            os.makedirs(upload_dir, exist_ok=True)
        
        print("✅ Created uploads directories")
        
        # 12. Create classwork tables
        print("🔧 Creating classwork tables...")
        
        # classwork_task table
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
        
        # classwork_material table
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
        
        # classwork_note table
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
        
        # classwork_session table
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
        
        # classwork_progress table
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
        
        # Commit changes
        conn.commit()
        print("🎉 Complete database created successfully!")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating database: {e}")
        conn.rollback()
        return False
        
    finally:
        conn.close()

if __name__ == "__main__":
    create_complete_database()
