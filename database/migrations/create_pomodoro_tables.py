"""
Create Pomodoro Tables Migration
Creates pomodoro_session table for OOP architecture
"""
import sqlite3
import os

def create_pomodoro_tables():
    """Create pomodoro_session table"""
    try:
        # Get database path
        db_path = os.path.join(os.path.dirname(__file__), '..', '..', 'instance', 'site.db')
        
        # Connect to database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("🔧 Creating pomodoro_session table...")
        
        # Create pomodoro_session table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS pomodoro_session (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                session_type TEXT NOT NULL,
                duration INTEGER NOT NULL,
                start_time TIMESTAMP NOT NULL,
                end_time TIMESTAMP,
                actual_duration INTEGER,
                status TEXT NOT NULL DEFAULT 'active',
                is_completed BOOLEAN DEFAULT FALSE,
                is_interrupted BOOLEAN DEFAULT FALSE,
                interruption_count INTEGER DEFAULT 0,
                interruption_reasons TEXT,
                lesson_id TEXT,
                section_id TEXT,
                task_id TEXT,
                auto_start_next BOOLEAN DEFAULT TRUE,
                notification_enabled BOOLEAN DEFAULT TRUE,
                sound_enabled BOOLEAN DEFAULT TRUE,
                notes TEXT,
                productivity_score INTEGER,
                mood_before TEXT,
                mood_after TEXT,
                focus_score INTEGER,
                energy_level INTEGER,
                difficulty_level INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES user(id),
                FOREIGN KEY (lesson_id) REFERENCES lesson(id)
            )
        """)
        
        # Create indexes
        print("🔧 Creating indexes...")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_pomodoro_user ON pomodoro_session(user_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_pomodoro_type ON pomodoro_session(session_type)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_pomodoro_status ON pomodoro_session(status)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_pomodoro_start_time ON pomodoro_session(start_time)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_pomodoro_lesson ON pomodoro_session(lesson_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_pomodoro_completed ON pomodoro_session(is_completed)")
        
        # Commit changes
        conn.commit()
        print("✅ Pomodoro tables created successfully!")
        
        # Close connection
        conn.close()
        
    except Exception as e:
        print(f"❌ Error creating pomodoro tables: {e}")
        raise e

if __name__ == "__main__":
    create_pomodoro_tables()
