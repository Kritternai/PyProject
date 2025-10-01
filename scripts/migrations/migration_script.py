#!/usr/bin/env python3
"""
Database Migration Script
Adds missing fields and optimizes database structure
"""

import sqlite3
import os
from datetime import datetime

def run_migration():
    db_path = 'instance/site.db'
    
    if not os.path.exists(db_path):
        print("Database file not found!")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("Starting database migration...")
    
    try:
        # Check if classroom_assignments_count column exists
        cursor.execute("PRAGMA table_info(lesson)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'classroom_assignments_count' not in columns:
            print("Adding classroom_assignments_count column...")
            cursor.execute("ALTER TABLE lesson ADD COLUMN classroom_assignments_count INTEGER DEFAULT 0")
            print("✓ Added classroom_assignments_count column")
        else:
            print("✓ classroom_assignments_count column already exists")
        
        # Add indexes for better performance
        print("Creating indexes...")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_lesson_user_id ON lesson(user_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_lesson_google_classroom_id ON lesson(google_classroom_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_lesson_source_platform ON lesson(source_platform)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_lesson_section_lesson_id ON lesson_section(lesson_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_imported_data_user_platform ON imported_data(user_id, platform)")
        print("✓ Created indexes")
        
        # Update existing Google Classroom lessons with assignment counts
        print("Updating Google Classroom assignment counts...")
        cursor.execute("""
            UPDATE lesson 
            SET classroom_assignments_count = (
                SELECT COUNT(*) 
                FROM json_each(
                    (SELECT data FROM imported_data 
                     WHERE user_id = lesson.user_id 
                     AND platform = 'google_classroom_api'
                     LIMIT 1)
                )
                WHERE json_extract(value, '$.courseWork') IS NOT NULL
            )
            WHERE source_platform = 'google_classroom'
        """)
        
        updated_rows = cursor.rowcount
        print(f"✓ Updated {updated_rows} lessons with assignment counts")
        
        # Commit changes
        conn.commit()
        print("✓ Migration completed successfully!")
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    run_migration() 