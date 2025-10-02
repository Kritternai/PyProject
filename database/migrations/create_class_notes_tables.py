"""
Create Class Notes Tables Migration
"""
import sqlite3
import os
from datetime import datetime

def create_class_notes_tables():
    """Create tables for class notes system"""
    
    # Database path
    db_path = 'instance/site.db'
    
    # Create instance directory if not exists
    os.makedirs('instance', exist_ok=True)
    
    # Connect to database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        print("🔧 Creating class notes tables...")
        
        # 1. Create note table (if not exists)
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
        
        # 2. Create note_file table (if not exists)
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
        
        # 3. Create announcement table (if not exists)
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
        
        # 4. Create announcement_comment table (if not exists)
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
        
        # 5. Create indexes for better performance
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_note_user_id ON note(user_id)",
            "CREATE INDEX IF NOT EXISTS idx_note_lesson_id ON note(lesson_id)",
            "CREATE INDEX IF NOT EXISTS idx_note_status ON note(status)",
            "CREATE INDEX IF NOT EXISTS idx_note_created_at ON note(created_at)",
            "CREATE INDEX IF NOT EXISTS idx_note_file_note_id ON note_file(note_id)",
            "CREATE INDEX IF NOT EXISTS idx_announcement_lesson_id ON announcement(lesson_id)",
            "CREATE INDEX IF NOT EXISTS idx_announcement_user_id ON announcement(user_id)",
            "CREATE INDEX IF NOT EXISTS idx_announcement_is_pinned ON announcement(is_pinned)",
            "CREATE INDEX IF NOT EXISTS idx_announcement_created_at ON announcement(created_at)",
            "CREATE INDEX IF NOT EXISTS idx_announcement_comment_announcement_id ON announcement_comment(announcement_id)",
            "CREATE INDEX IF NOT EXISTS idx_announcement_comment_user_id ON announcement_comment(user_id)",
            "CREATE INDEX IF NOT EXISTS idx_announcement_comment_parent_id ON announcement_comment(parent_comment_id)"
        ]
        
        for index_sql in indexes:
            cursor.execute(index_sql)
        
        print("✅ Created database indexes")
        
        # 6. Create uploads directory
        uploads_dir = 'app/static/uploads/notes'
        os.makedirs(uploads_dir, exist_ok=True)
        print("✅ Created uploads directory")
        
        # Commit changes
        conn.commit()
        print("🎉 Class notes tables created successfully!")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        conn.rollback()
        return False
        
    finally:
        conn.close()

if __name__ == "__main__":
    create_class_notes_tables()
