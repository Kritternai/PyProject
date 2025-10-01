#!/usr/bin/env python3
"""
Migration Script for Existing Database
This script updates the existing database to match the new schema
"""

import sys
import os
import sqlite3
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def migrate_existing_database():
    """Migrate existing database to new schema"""
    
    db_path = Path("instance/site.db")
    if not db_path.exists():
        print("❌ Database file not found at instance/site.db")
        return False
    
    print("🔄 Starting database migration...")
    
    try:
        # Connect to existing database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check current schema
        cursor.execute("PRAGMA table_info(user)")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]
        
        print(f"📊 Current user table columns: {column_names}")
        
        # Add missing columns if they don't exist
        missing_columns = []
        
        # Define required columns and their types
        required_columns = {
            'role': 'VARCHAR(20) DEFAULT "student"',
            'first_name': 'VARCHAR(50)',
            'last_name': 'VARCHAR(50)',
            'profile_image': 'VARCHAR(255)',
            'bio': 'TEXT',
            'preferences': 'TEXT',
            'is_active': 'BOOLEAN DEFAULT 1',
            'email_verified': 'BOOLEAN DEFAULT 0',
            'last_login': 'DATETIME',
            'total_lessons': 'INTEGER DEFAULT 0',
            'total_notes': 'INTEGER DEFAULT 0',
            'total_tasks': 'INTEGER DEFAULT 0',
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
                    cursor.execute(f"ALTER TABLE user ADD COLUMN {col_name} {col_type}")
                    print(f"  ✅ Added column: {col_name}")
                except sqlite3.OperationalError as e:
                    if "duplicate column name" in str(e):
                        print(f"  ⚠️  Column {col_name} already exists")
                    else:
                        print(f"  ❌ Error adding column {col_name}: {e}")
        else:
            print("✅ All required columns already exist")
        
        # Update existing users to have default role
        cursor.execute("UPDATE user SET role = 'student' WHERE role IS NULL")
        updated_rows = cursor.rowcount
        print(f"✅ Updated {updated_rows} users with default role")
        
        # Create indexes for better performance
        print("🔧 Creating indexes...")
        
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_user_email ON user(email)",
            "CREATE INDEX IF NOT EXISTS idx_user_username ON user(username)",
            "CREATE INDEX IF NOT EXISTS idx_user_role ON user(role)",
            "CREATE INDEX IF NOT EXISTS idx_user_active ON user(is_active)"
        ]
        
        for index_sql in indexes:
            try:
                cursor.execute(index_sql)
                print(f"  ✅ Created index")
            except Exception as e:
                print(f"  ⚠️  Index creation warning: {e}")
        
        # Commit changes
        conn.commit()
        print("✅ Database migration completed successfully")
        
        # Show final schema
        cursor.execute("PRAGMA table_info(user)")
        final_columns = cursor.fetchall()
        print(f"📊 Final user table columns: {[col[1] for col in final_columns]}")
        
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False
        
    finally:
        if 'conn' in locals():
            conn.close()

def main():
    """Main migration function"""
    print("🚀 Smart Learning Hub - Database Migration")
    print("=" * 50)
    
    if migrate_existing_database():
        print("\n🎉 Migration completed successfully!")
        print("You can now run the application with the new schema.")
    else:
        print("\n💥 Migration failed!")
        print("Please check the error messages above.")
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
