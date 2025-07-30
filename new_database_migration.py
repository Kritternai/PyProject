#!/usr/bin/env python3
"""
New Database Migration Script
Migrates to the new normalized database schema
"""

import sqlite3
import os
import json
import uuid
from datetime import datetime

def create_new_schema():
    """Create new database schema"""
    db_path = 'instance/site.db'
    
    if not os.path.exists(db_path):
        print("Database file not found!")
        return False
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("Creating new database schema...")
    
    try:
        # Create new tables
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users_new (
                id VARCHAR(36) PRIMARY KEY,
                username VARCHAR(80) UNIQUE NOT NULL,
                email VARCHAR(120) UNIQUE NOT NULL,
                password_hash VARCHAR(128) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS lessons_new (
                id VARCHAR(36) PRIMARY KEY,
                user_id VARCHAR(36) NOT NULL,
                title VARCHAR(200) NOT NULL,
                description TEXT,
                status VARCHAR(50) DEFAULT 'Not Started',
                tags TEXT,
                author_name VARCHAR(100),
                color_theme INTEGER DEFAULT 1,
                is_favorite BOOLEAN DEFAULT FALSE,
                source_platform VARCHAR(50) DEFAULT 'manual',
                external_id VARCHAR(100),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users_new (id)
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS lesson_sections_new (
                id VARCHAR(36) PRIMARY KEY,
                lesson_id VARCHAR(36) NOT NULL,
                title VARCHAR(200) NOT NULL,
                content TEXT,
                section_type VARCHAR(50) NOT NULL,
                order_index INTEGER DEFAULT 0,
                status VARCHAR(50) DEFAULT 'pending',
                tags TEXT,
                due_date TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (lesson_id) REFERENCES lessons_new (id)
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS files_new (
                id VARCHAR(36) PRIMARY KEY,
                section_id VARCHAR(36) NOT NULL,
                file_name VARCHAR(255) NOT NULL,
                file_path VARCHAR(500) NOT NULL,
                file_type VARCHAR(50),
                file_size INTEGER,
                mime_type VARCHAR(100),
                external_url VARCHAR(500),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (section_id) REFERENCES lesson_sections_new (id)
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS external_integrations_new (
                id VARCHAR(36) PRIMARY KEY,
                user_id VARCHAR(36) NOT NULL,
                platform VARCHAR(50) NOT NULL,
                access_token TEXT,
                refresh_token TEXT,
                token_expires_at TIMESTAMP,
                platform_user_id VARCHAR(100),
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users_new (id),
                UNIQUE (user_id, platform)
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS external_data_new (
                id VARCHAR(36) PRIMARY KEY,
                user_id VARCHAR(36) NOT NULL,
                integration_id VARCHAR(36) NOT NULL,
                external_id VARCHAR(100) NOT NULL,
                data_type VARCHAR(50) NOT NULL,
                title VARCHAR(200),
                description TEXT,
                raw_data JSON,
                last_synced_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users_new (id),
                FOREIGN KEY (integration_id) REFERENCES external_integrations_new (id),
                UNIQUE (user_id, external_id, data_type)
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tags_new (
                id VARCHAR(36) PRIMARY KEY,
                user_id VARCHAR(36) NOT NULL,
                name VARCHAR(100) NOT NULL,
                color VARCHAR(7) DEFAULT '#007bff',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users_new (id),
                UNIQUE (user_id, name)
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS lesson_tags_new (
                lesson_id VARCHAR(36) NOT NULL,
                tag_id VARCHAR(36) NOT NULL,
                PRIMARY KEY (lesson_id, tag_id),
                FOREIGN KEY (lesson_id) REFERENCES lessons_new (id),
                FOREIGN KEY (tag_id) REFERENCES tags_new (id)
            )
        """)
        
        # Create indexes
        print("Creating indexes...")
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_users_email ON users_new(email)",
            "CREATE INDEX IF NOT EXISTS idx_users_username ON users_new(username)",
            "CREATE INDEX IF NOT EXISTS idx_lessons_user_id ON lessons_new(user_id)",
            "CREATE INDEX IF NOT EXISTS idx_lessons_external_id ON lessons_new(external_id)",
            "CREATE INDEX IF NOT EXISTS idx_lessons_source_platform ON lessons_new(source_platform)",
            "CREATE INDEX IF NOT EXISTS idx_lessons_status ON lessons_new(status)",
            "CREATE INDEX IF NOT EXISTS idx_lessons_created_at ON lessons_new(created_at)",
            "CREATE INDEX IF NOT EXISTS idx_lesson_sections_lesson_id ON lesson_sections_new(lesson_id)",
            "CREATE INDEX IF NOT EXISTS idx_lesson_sections_type ON lesson_sections_new(section_type)",
            "CREATE INDEX IF NOT EXISTS idx_lesson_sections_order ON lesson_sections_new(lesson_id, order_index)",
            "CREATE INDEX IF NOT EXISTS idx_files_section_id ON files_new(section_id)",
            "CREATE INDEX IF NOT EXISTS idx_files_type ON files_new(file_type)",
            "CREATE INDEX IF NOT EXISTS idx_external_integrations_user_id ON external_integrations_new(user_id)",
            "CREATE INDEX IF NOT EXISTS idx_external_integrations_platform ON external_integrations_new(platform)",
            "CREATE INDEX IF NOT EXISTS idx_external_data_user_id ON external_data_new(user_id)",
            "CREATE INDEX IF NOT EXISTS idx_external_data_integration_id ON external_data_new(integration_id)",
            "CREATE INDEX IF NOT EXISTS idx_external_data_external_id ON external_data_new(external_id)",
            "CREATE INDEX IF NOT EXISTS idx_external_data_type ON external_data_new(data_type)"
        ]
        
        for index in indexes:
            cursor.execute(index)
        
        conn.commit()
        print("✓ New schema created successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error creating schema: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

def migrate_data():
    """Migrate data from old tables to new tables"""
    db_path = 'instance/site.db'
    
    if not os.path.exists(db_path):
        print("Database file not found!")
        return False
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("Migrating data...")
    
    try:
        # Migrate users
        print("Migrating users...")
        cursor.execute("SELECT * FROM user")
        users = cursor.fetchall()
        
        for user in users:
            cursor.execute("""
                INSERT INTO users_new (id, username, email, password_hash, created_at, updated_at)
                VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
            """, user)
        
        print(f"✓ Migrated {len(users)} users")
        
        # Migrate lessons
        print("Migrating lessons...")
        cursor.execute("SELECT * FROM lesson")
        lessons = cursor.fetchall()
        
        for lesson in lessons:
            # Parse tags from string to JSON array
            tags = lesson[4] if lesson[4] else ""
            tags_array = [tag.strip() for tag in tags.split(',') if tag.strip()]
            tags_json = json.dumps(tags_array)
            
            cursor.execute("""
                INSERT INTO lessons_new (
                    id, user_id, title, description, status, tags, author_name,
                    color_theme, is_favorite, source_platform, external_id,
                    created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
            """, (
                lesson[0], lesson[8], lesson[1], lesson[2], lesson[3], tags_json,
                lesson[5], lesson[6], lesson[7], lesson[10], lesson[9]
            ))
        
        print(f"✓ Migrated {len(lessons)} lessons")
        
        # Migrate lesson sections
        print("Migrating lesson sections...")
        cursor.execute("SELECT * FROM lesson_section")
        sections = cursor.fetchall()
        
        for section in sections:
            cursor.execute("""
                INSERT INTO lesson_sections_new (
                    id, lesson_id, title, content, section_type, order_index,
                    status, tags, due_date, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                section[0], section[1], section[2], section[3], section[4],
                section[7], section[13], section[12], section[6], section[8], section[9]
            ))
        
        print(f"✓ Migrated {len(sections)} lesson sections")
        
        # Migrate external integrations (Google credentials)
        print("Migrating external integrations...")
        cursor.execute("SELECT * FROM google_credentials")
        credentials = cursor.fetchall()
        
        for cred in credentials:
            cursor.execute("""
                INSERT INTO external_integrations_new (
                    id, user_id, platform, access_token, refresh_token,
                    platform_user_id, is_active, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
            """, (
                str(uuid.uuid4()), cred[1], 'google_classroom', cred[2], cred[3],
                None, True
            ))
        
        print(f"✓ Migrated {len(credentials)} external integrations")
        
        # Migrate external data
        print("Migrating external data...")
        cursor.execute("SELECT * FROM imported_data")
        imported_data = cursor.fetchall()
        
        for data in imported_data:
            if data[2] == 'google_classroom_api' and 'courses' in data[3]:
                courses = data[3]['courses']
                for course in courses:
                    cursor.execute("""
                        INSERT INTO external_data_new (
                            id, user_id, integration_id, external_id, data_type,
                            title, description, raw_data, last_synced_at
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        str(uuid.uuid4()), data[1], 
                        # Get integration_id for this user and platform
                        cursor.execute("SELECT id FROM external_integrations_new WHERE user_id = ? AND platform = 'google_classroom'", (data[1],)).fetchone()[0],
                        course['id'], 'course', course.get('name'), course.get('description'),
                        json.dumps(course), data[4]
                    ))
        
        print("✓ Migrated external data")
        
        conn.commit()
        print("✓ Data migration completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error migrating data: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

def switch_to_new_schema():
    """Switch to new schema by renaming tables"""
    db_path = 'instance/site.db'
    
    if not os.path.exists(db_path):
        print("Database file not found!")
        return False
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("Switching to new schema...")
    
    try:
        # Backup old tables
        cursor.execute("ALTER TABLE user RENAME TO user_old")
        cursor.execute("ALTER TABLE lesson RENAME TO lesson_old")
        cursor.execute("ALTER TABLE lesson_section RENAME TO lesson_section_old")
        cursor.execute("ALTER TABLE google_credentials RENAME TO google_credentials_old")
        cursor.execute("ALTER TABLE imported_data RENAME TO imported_data_old")
        
        # Rename new tables
        cursor.execute("ALTER TABLE users_new RENAME TO user")
        cursor.execute("ALTER TABLE lessons_new RENAME TO lesson")
        cursor.execute("ALTER TABLE lesson_sections_new RENAME TO lesson_section")
        cursor.execute("ALTER TABLE external_integrations_new RENAME TO external_integrations")
        cursor.execute("ALTER TABLE external_data_new RENAME TO external_data")
        cursor.execute("ALTER TABLE files_new RENAME TO files")
        cursor.execute("ALTER TABLE tags_new RENAME TO tags")
        cursor.execute("ALTER TABLE lesson_tags_new RENAME TO lesson_tags")
        
        conn.commit()
        print("✓ Schema switch completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error switching schema: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

def main():
    """Run the complete migration"""
    print("Starting new database migration...")
    
    # Step 1: Create new schema
    if not create_new_schema():
        print("❌ Failed to create new schema")
        return
    
    # Step 2: Migrate data
    if not migrate_data():
        print("❌ Failed to migrate data")
        return
    
    # Step 3: Switch to new schema
    if not switch_to_new_schema():
        print("❌ Failed to switch to new schema")
        return
    
    print("🎉 Migration completed successfully!")
    print("New database schema is now active.")

if __name__ == "__main__":
    main() 