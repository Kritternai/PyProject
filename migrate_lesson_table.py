#!/usr/bin/env python3
"""
Migration Script for Lesson Table
This script updates the existing lesson table to match the new schema
"""

import sys
import os
import sqlite3
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def migrate_lesson_table():
    """Migrate existing lesson table to new schema"""
    
    db_path = Path("instance/site.db")
    if not db_path.exists():
        print("❌ Database file not found at instance/site.db")
        return False
    
    print("🔄 Starting lesson table migration...")
    
    try:
        # Connect to existing database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check current lesson table schema
        cursor.execute("PRAGMA table_info(lesson)")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]
        
        print(f"📊 Current lesson table columns: {column_names}")
        
        # Add missing columns if they don't exist
        missing_columns = []
        
        # Define required columns and their types
        required_columns = {
            'progress_percentage': 'INTEGER DEFAULT 0',
            'difficulty_level': 'VARCHAR(20) DEFAULT "beginner"',
            'estimated_duration': 'INTEGER',
            'color_theme': 'INTEGER DEFAULT 1',
            'external_id': 'VARCHAR(100)',
            'external_url': 'VARCHAR(500)',
            'subject': 'VARCHAR(100)',
            'grade_level': 'VARCHAR(20)',
            'total_sections': 'INTEGER DEFAULT 0',
            'completed_sections': 'INTEGER DEFAULT 0',
            'total_time_spent': 'INTEGER DEFAULT 0',
            'created_at': 'DATETIME DEFAULT CURRENT_TIMESTAMP',
            'updated_at': 'DATETIME DEFAULT CURRENT_TIMESTAMP'
        }
        
        for col_name, col_type in required_columns.items():
            if col_name not in column_names:
                missing_columns.append((col_name, col_type))
        
        if missing_columns:
            print(f"🔧 Adding {len(missing_columns)} missing columns...")
            
            for col_name, col_type in missing_columns:
                try:
                    cursor.execute(f"ALTER TABLE lesson ADD COLUMN {col_name} {col_type}")
                    print(f"  ✅ Added column: {col_name}")
                except sqlite3.OperationalError as e:
                    if "duplicate column name" in str(e):
                        print(f"  ⚠️  Column {col_name} already exists")
                    else:
                        print(f"  ❌ Error adding column {col_name}: {e}")
        else:
            print("✅ All required columns already exist")
        
        # Check lesson_section table
        cursor.execute("PRAGMA table_info(lesson_section)")
        section_columns = cursor.fetchall()
        section_column_names = [col[1] for col in section_columns]
        
        print(f"📊 Current lesson_section table columns: {section_column_names}")
        
        # Add missing columns to lesson_section
        section_required_columns = {
            'section_type': 'VARCHAR(50) DEFAULT "text"',
            'order_index': 'INTEGER DEFAULT 0',
            'due_date': 'DATETIME',
            'estimated_duration': 'INTEGER',
            'points': 'INTEGER DEFAULT 0',
            'time_spent': 'INTEGER DEFAULT 0',
            'completion_percentage': 'INTEGER DEFAULT 0',
            'external_id': 'VARCHAR(100)',
            'created_at': 'DATETIME DEFAULT CURRENT_TIMESTAMP',
            'updated_at': 'DATETIME DEFAULT CURRENT_TIMESTAMP'
        }
        
        section_missing_columns = []
        for col_name, col_type in section_required_columns.items():
            if col_name not in section_column_names:
                section_missing_columns.append((col_name, col_type))
        
        if section_missing_columns:
            print(f"🔧 Adding {len(section_missing_columns)} missing columns to lesson_section...")
            
            for col_name, col_type in section_missing_columns:
                try:
                    cursor.execute(f"ALTER TABLE lesson_section ADD COLUMN {col_name} {col_type}")
                    print(f"  ✅ Added column: {col_name}")
                except sqlite3.OperationalError as e:
                    if "duplicate column name" in str(e):
                        print(f"  ⚠️  Column {col_name} already exists")
                    else:
                        print(f"  ❌ Error adding column {col_name}: {e}")
        else:
            print("✅ All required lesson_section columns already exist")
        
        # Update existing data for backward compatibility
        print("🔄 Updating existing data for backward compatibility...")
        
        # Copy order to order_index if order_index is NULL
        cursor.execute("UPDATE lesson_section SET order_index = \"order\" WHERE order_index IS NULL AND \"order\" IS NOT NULL")
        updated_rows = cursor.rowcount
        print(f"  ✅ Updated {updated_rows} rows: copied order to order_index")
        
        # Copy type to section_type if section_type is NULL
        cursor.execute("UPDATE lesson_section SET section_type = type WHERE section_type IS NULL AND type IS NOT NULL")
        updated_rows = cursor.rowcount
        print(f"  ✅ Updated {updated_rows} rows: copied type to section_type")
        
        # Update lesson status values to match new schema
        cursor.execute("UPDATE lesson SET status = 'not_started' WHERE status = 'Not Started'")
        updated_rows = cursor.rowcount
        print(f"  ✅ Updated {updated_rows} rows: status 'Not Started' → 'not_started'")
        
        cursor.execute("UPDATE lesson SET status = 'in_progress' WHERE status = 'In Progress'")
        updated_rows = cursor.rowcount
        print(f"  ✅ Updated {updated_rows} rows: status 'In Progress' → 'in_progress'")
        
        cursor.execute("UPDATE lesson SET status = 'completed' WHERE status = 'Completed'")
        updated_rows = cursor.rowcount
        print(f"  ✅ Updated {updated_rows} rows: status 'Completed' → 'completed'")
        
        # Copy selected_color to color_theme if color_theme is NULL (only if selected_color column exists)
        try:
            cursor.execute("SELECT COUNT(*) FROM pragma_table_info('lesson') WHERE name='selected_color'")
            has_selected_color = cursor.fetchone()[0] > 0
            
            if has_selected_color:
                cursor.execute("UPDATE lesson SET color_theme = selected_color WHERE color_theme IS NULL AND selected_color IS NOT NULL")
                updated_rows = cursor.rowcount
                print(f"  ✅ Updated {updated_rows} rows: copied selected_color to color_theme")
            else:
                print("  ℹ️  selected_color column does not exist, skipping copy")
        except Exception as e:
            print(f"  ℹ️  Could not check for selected_color column: {e}")
        
        # Create indexes for better performance
        print("🔧 Creating indexes...")
        
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_lesson_user_id ON lesson(user_id)",
            "CREATE INDEX IF NOT EXISTS idx_lesson_status ON lesson(status)",
            "CREATE INDEX IF NOT EXISTS idx_lesson_is_favorite ON lesson(is_favorite)",
            "CREATE INDEX IF NOT EXISTS idx_lesson_source_platform ON lesson(source_platform)",
            "CREATE INDEX IF NOT EXISTS idx_lesson_section_lesson_id ON lesson_section(lesson_id)",
            "CREATE INDEX IF NOT EXISTS idx_lesson_section_type ON lesson_section(section_type)",
            "CREATE INDEX IF NOT EXISTS idx_lesson_section_status ON lesson_section(status)"
        ]
        
        for index_sql in indexes:
            try:
                cursor.execute(index_sql)
                print(f"  ✅ Created index")
            except Exception as e:
                print(f"  ⚠️  Index creation warning: {e}")
        
        # Commit changes
        conn.commit()
        print("✅ Lesson table migration completed successfully")
        
        # Show final schema
        cursor.execute("PRAGMA table_info(lesson)")
        final_columns = cursor.fetchall()
        print(f"📊 Final lesson table columns: {[col[1] for col in final_columns]}")
        
        cursor.execute("PRAGMA table_info(lesson_section)")
        final_section_columns = cursor.fetchall()
        print(f"📊 Final lesson_section table columns: {[col[1] for col in final_section_columns]}")
        
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False
        
    finally:
        if 'conn' in locals():
            conn.close()

def main():
    """Main migration function"""
    print("🚀 Smart Learning Hub - Lesson Table Migration")
    print("=" * 50)
    
    if migrate_lesson_table():
        print("\n🎉 Migration completed successfully!")
        print("You can now use the updated lesson models.")
    else:
        print("\n💥 Migration failed!")
        print("Please check the error messages above.")
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
