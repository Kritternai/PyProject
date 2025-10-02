#!/usr/bin/env python3
"""
Migration script to create classwork-related tables
"""

import sqlite3
import os
import sys

def create_classwork_tables():
    """Create classwork-related tables"""
    
    # Get database path
    db_path = os.path.join(os.path.dirname(__file__), '..', '..', 'instance', 'site.db')
    
    if not os.path.exists(os.path.dirname(db_path)):
        os.makedirs(os.path.dirname(db_path))
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        print("🔧 Creating classwork tables...")
        
        # 1. classwork_task table
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
        
        # 2. classwork_material table
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
        
        # 3. classwork_note table
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
        
        # 4. classwork_session table
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
        
        # 5. classwork_progress table
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
        
        # Create indexes
        print("🔧 Creating indexes...")
        
        # classwork_task indexes
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_classwork_task_user_id ON classwork_task(user_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_classwork_task_lesson_id ON classwork_task(lesson_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_classwork_task_status ON classwork_task(status)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_classwork_task_priority ON classwork_task(priority)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_classwork_task_due_date ON classwork_task(due_date)")
        
        # classwork_material indexes
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_classwork_material_user_id ON classwork_material(user_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_classwork_material_lesson_id ON classwork_material(lesson_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_classwork_material_task_id ON classwork_material(task_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_classwork_material_subject ON classwork_material(subject)")
        
        # classwork_note indexes
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_classwork_note_user_id ON classwork_note(user_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_classwork_note_lesson_id ON classwork_note(lesson_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_classwork_note_task_id ON classwork_note(task_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_classwork_note_subject ON classwork_note(subject)")
        
        # classwork_session indexes
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_classwork_session_user_id ON classwork_session(user_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_classwork_session_lesson_id ON classwork_session(lesson_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_classwork_session_task_id ON classwork_session(task_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_classwork_session_start_time ON classwork_session(start_time)")
        
        # classwork_progress indexes
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_classwork_progress_user_id ON classwork_progress(user_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_classwork_progress_lesson_id ON classwork_progress(lesson_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_classwork_progress_task_id ON classwork_progress(task_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_classwork_progress_completed_at ON classwork_progress(completed_at)")
        
        conn.commit()
        print("✅ Classwork tables created successfully!")
        
        # Show table info
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'classwork_%'")
        tables = cursor.fetchall()
        print(f"📋 Created {len(tables)} classwork tables:")
        for table in tables:
            print(f"   • {table[0]}")
            
    except Exception as e:
        print(f"❌ Error creating classwork tables: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    create_classwork_tables()
