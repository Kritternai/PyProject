#!/usr/bin/env python3
"""
SRS Database Migration Script
Migrates to database schema that supports SRS requirements and current system
"""

import sqlite3
import os
import json
import uuid
from datetime import datetime

def create_srs_schema():
    """Create SRS-compliant database schema"""
    db_path = 'instance/site.db'
    
    if not os.path.exists(db_path):
        print("Database file not found!")
        return False
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("Creating SRS-compliant database schema...")
    
    try:
        # Create new tables for SRS requirements
        
        # 1. Enhanced Users Table (FR-001, FR-002, FR-003)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users_enhanced (
                id VARCHAR(36) PRIMARY KEY,
                username VARCHAR(80) UNIQUE NOT NULL,
                email VARCHAR(120) UNIQUE NOT NULL,
                password_hash VARCHAR(128) NOT NULL,
                role VARCHAR(20) DEFAULT 'student',
                profile_image VARCHAR(255),
                bio TEXT,
                preferences JSON,
                last_login TIMESTAMP,
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 2. Enhanced Lessons Table (FR-004, FR-005, FR-006, FR-007)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS lessons_enhanced (
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
                difficulty_level VARCHAR(20) DEFAULT 'beginner',
                estimated_duration INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users_enhanced (id)
            )
        """)
        
        # 3. Enhanced Lesson Sections Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS lesson_sections_enhanced (
                id VARCHAR(36) PRIMARY KEY,
                lesson_id VARCHAR(36) NOT NULL,
                title VARCHAR(200) NOT NULL,
                content TEXT,
                section_type VARCHAR(50) NOT NULL,
                order_index INTEGER DEFAULT 0,
                status VARCHAR(50) DEFAULT 'pending',
                tags TEXT,
                due_date TIMESTAMP,
                points INTEGER DEFAULT 0,
                time_spent INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (lesson_id) REFERENCES lessons_enhanced (id)
            )
        """)
        
        # 4. Enhanced Notes Table (FR-008, FR-009, FR-010, FR-011)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS notes_enhanced (
                id VARCHAR(36) PRIMARY KEY,
                user_id VARCHAR(36) NOT NULL,
                lesson_id VARCHAR(36),
                section_id VARCHAR(36),
                title VARCHAR(200) NOT NULL,
                content TEXT NOT NULL,
                tags TEXT,
                status VARCHAR(20) DEFAULT 'active',
                is_public BOOLEAN DEFAULT FALSE,
                external_link VARCHAR(500),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users_enhanced (id),
                FOREIGN KEY (lesson_id) REFERENCES lessons_enhanced (id),
                FOREIGN KEY (section_id) REFERENCES lesson_sections_enhanced (id)
            )
        """)
        
        # 5. Tasks Table (FR-012, FR-013, FR-014)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id VARCHAR(36) PRIMARY KEY,
                user_id VARCHAR(36) NOT NULL,
                lesson_id VARCHAR(36),
                section_id VARCHAR(36),
                title VARCHAR(200) NOT NULL,
                description TEXT,
                status VARCHAR(20) DEFAULT 'pending',
                priority VARCHAR(20) DEFAULT 'medium',
                due_date TIMESTAMP,
                completed_at TIMESTAMP,
                estimated_time INTEGER,
                actual_time INTEGER,
                tags TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users_enhanced (id),
                FOREIGN KEY (lesson_id) REFERENCES lessons_enhanced (id),
                FOREIGN KEY (section_id) REFERENCES lesson_sections_enhanced (id)
            )
        """)
        
        # 6. Progress Tracking Table (FR-015, FR-016)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS progress_tracking (
                id VARCHAR(36) PRIMARY KEY,
                user_id VARCHAR(36) NOT NULL,
                lesson_id VARCHAR(36) NOT NULL,
                section_id VARCHAR(36),
                progress_type VARCHAR(50) NOT NULL,
                value DECIMAL(10,2) NOT NULL,
                max_value DECIMAL(10,2),
                percentage DECIMAL(5,2),
                notes TEXT,
                tracked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users_enhanced (id),
                FOREIGN KEY (lesson_id) REFERENCES lessons_enhanced (id),
                FOREIGN KEY (section_id) REFERENCES lesson_sections_enhanced (id)
            )
        """)
        
        # 7. Pomodoro Sessions Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS pomodoro_sessions (
                id VARCHAR(36) PRIMARY KEY,
                user_id VARCHAR(36) NOT NULL,
                lesson_id VARCHAR(36),
                section_id VARCHAR(36),
                session_type VARCHAR(20) DEFAULT 'focus',
                duration INTEGER NOT NULL,
                start_time TIMESTAMP NOT NULL,
                end_time TIMESTAMP,
                is_completed BOOLEAN DEFAULT FALSE,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users_enhanced (id),
                FOREIGN KEY (lesson_id) REFERENCES lessons_enhanced (id),
                FOREIGN KEY (section_id) REFERENCES lesson_sections_enhanced (id)
            )
        """)
        
        # 8. Reminders Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS reminders (
                id VARCHAR(36) PRIMARY KEY,
                user_id VARCHAR(36) NOT NULL,
                lesson_id VARCHAR(36),
                section_id VARCHAR(36),
                title VARCHAR(200) NOT NULL,
                description TEXT,
                reminder_type VARCHAR(20) DEFAULT 'due_date',
                due_date TIMESTAMP NOT NULL,
                is_recurring BOOLEAN DEFAULT FALSE,
                recurrence_pattern VARCHAR(50),
                is_completed BOOLEAN DEFAULT FALSE,
                completed_at TIMESTAMP,
                priority VARCHAR(20) DEFAULT 'medium',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users_enhanced (id),
                FOREIGN KEY (lesson_id) REFERENCES lessons_enhanced (id),
                FOREIGN KEY (section_id) REFERENCES lesson_sections_enhanced (id)
            )
        """)
        
        # 9. Enhanced Files Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS files_enhanced (
                id VARCHAR(36) PRIMARY KEY,
                user_id VARCHAR(36) NOT NULL,
                lesson_id VARCHAR(36),
                section_id VARCHAR(36),
                note_id VARCHAR(36),
                file_name VARCHAR(255) NOT NULL,
                file_path VARCHAR(500) NOT NULL,
                file_type VARCHAR(50),
                file_size INTEGER,
                mime_type VARCHAR(100),
                external_url VARCHAR(500),
                is_public BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users_enhanced (id),
                FOREIGN KEY (lesson_id) REFERENCES lessons_enhanced (id),
                FOREIGN KEY (section_id) REFERENCES lesson_sections_enhanced (id),
                FOREIGN KEY (note_id) REFERENCES notes_enhanced (id)
            )
        """)
        
        # 10. Tags Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tags (
                id VARCHAR(36) PRIMARY KEY,
                user_id VARCHAR(36) NOT NULL,
                name VARCHAR(100) NOT NULL,
                color VARCHAR(7) DEFAULT '#007bff',
                tag_type VARCHAR(20) DEFAULT 'general',
                description TEXT,
                usage_count INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users_enhanced (id),
                UNIQUE (user_id, name)
            )
        """)
        
        # 11. Tag Relationships Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tag_relationships (
                tag_id VARCHAR(36) NOT NULL,
                entity_id VARCHAR(36) NOT NULL,
                entity_type VARCHAR(20) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (tag_id, entity_id, entity_type),
                FOREIGN KEY (tag_id) REFERENCES tags (id)
            )
        """)
        
        # 12. Enhanced External Integrations Table (FR-019)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS external_integrations_enhanced (
                id VARCHAR(36) PRIMARY KEY,
                user_id VARCHAR(36) NOT NULL,
                platform VARCHAR(50) NOT NULL,
                access_token TEXT,
                refresh_token TEXT,
                token_expires_at TIMESTAMP,
                platform_user_id VARCHAR(100),
                platform_user_email VARCHAR(120),
                is_active BOOLEAN DEFAULT TRUE,
                last_sync_at TIMESTAMP,
                sync_frequency VARCHAR(20) DEFAULT 'daily',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users_enhanced (id),
                UNIQUE (user_id, platform)
            )
        """)
        
        # 13. Enhanced External Data Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS external_data_enhanced (
                id VARCHAR(36) PRIMARY KEY,
                user_id VARCHAR(36) NOT NULL,
                integration_id VARCHAR(36) NOT NULL,
                external_id VARCHAR(100) NOT NULL,
                data_type VARCHAR(50) NOT NULL,
                title VARCHAR(200),
                description TEXT,
                status VARCHAR(50),
                due_date TIMESTAMP,
                points INTEGER,
                max_points INTEGER,
                raw_data JSON,
                last_synced_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users_enhanced (id),
                FOREIGN KEY (integration_id) REFERENCES external_integrations_enhanced (id),
                UNIQUE (user_id, external_id, data_type)
            )
        """)
        
        # 14. Reports Table (FR-017, FR-018)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS reports (
                id VARCHAR(36) PRIMARY KEY,
                user_id VARCHAR(36) NOT NULL,
                report_type VARCHAR(50) NOT NULL,
                title VARCHAR(200) NOT NULL,
                description TEXT,
                parameters JSON,
                report_data JSON,
                file_path VARCHAR(500),
                file_format VARCHAR(20),
                is_scheduled BOOLEAN DEFAULT FALSE,
                schedule_pattern VARCHAR(50),
                last_generated_at TIMESTAMP,
                next_generation_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users_enhanced (id)
            )
        """)
        
        # 15. Activity Logs Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS activity_logs (
                id VARCHAR(36) PRIMARY KEY,
                user_id VARCHAR(36) NOT NULL,
                action VARCHAR(100) NOT NULL,
                entity_type VARCHAR(50),
                entity_id VARCHAR(36),
                details JSON,
                ip_address VARCHAR(45),
                user_agent TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users_enhanced (id)
            )
        """)
        
        # Create indexes for performance
        print("Creating indexes...")
        indexes = [
            # Users
            "CREATE INDEX IF NOT EXISTS idx_users_enhanced_email ON users_enhanced(email)",
            "CREATE INDEX IF NOT EXISTS idx_users_enhanced_username ON users_enhanced(username)",
            "CREATE INDEX IF NOT EXISTS idx_users_enhanced_role ON users_enhanced(role)",
            
            # Lessons
            "CREATE INDEX IF NOT EXISTS idx_lessons_enhanced_user_id ON lessons_enhanced(user_id)",
            "CREATE INDEX IF NOT EXISTS idx_lessons_enhanced_status ON lessons_enhanced(status)",
            "CREATE INDEX IF NOT EXISTS idx_lessons_enhanced_source_platform ON lessons_enhanced(source_platform)",
            "CREATE INDEX IF NOT EXISTS idx_lessons_enhanced_external_id ON lessons_enhanced(external_id)",
            "CREATE INDEX IF NOT EXISTS idx_lessons_enhanced_created_at ON lessons_enhanced(created_at)",
            
            # Lesson Sections
            "CREATE INDEX IF NOT EXISTS idx_lesson_sections_enhanced_lesson_id ON lesson_sections_enhanced(lesson_id)",
            "CREATE INDEX IF NOT EXISTS idx_lesson_sections_enhanced_type ON lesson_sections_enhanced(section_type)",
            "CREATE INDEX IF NOT EXISTS idx_lesson_sections_enhanced_order ON lesson_sections_enhanced(lesson_id, order_index)",
            
            # Notes
            "CREATE INDEX IF NOT EXISTS idx_notes_enhanced_user_id ON notes_enhanced(user_id)",
            "CREATE INDEX IF NOT EXISTS idx_notes_enhanced_lesson_id ON notes_enhanced(lesson_id)",
            "CREATE INDEX IF NOT EXISTS idx_notes_enhanced_status ON notes_enhanced(status)",
            "CREATE INDEX IF NOT EXISTS idx_notes_enhanced_created_at ON notes_enhanced(created_at)",
            
            # Tasks
            "CREATE INDEX IF NOT EXISTS idx_tasks_user_id ON tasks(user_id)",
            "CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status)",
            "CREATE INDEX IF NOT EXISTS idx_tasks_due_date ON tasks(due_date)",
            "CREATE INDEX IF NOT EXISTS idx_tasks_priority ON tasks(priority)",
            
            # Progress Tracking
            "CREATE INDEX IF NOT EXISTS idx_progress_tracking_user_id ON progress_tracking(user_id)",
            "CREATE INDEX IF NOT EXISTS idx_progress_tracking_lesson_id ON progress_tracking(lesson_id)",
            "CREATE INDEX IF NOT EXISTS idx_progress_tracking_type ON progress_tracking(progress_type)",
            "CREATE INDEX IF NOT EXISTS idx_progress_tracking_tracked_at ON progress_tracking(tracked_at)",
            
            # Pomodoro Sessions
            "CREATE INDEX IF NOT EXISTS idx_pomodoro_sessions_user_id ON pomodoro_sessions(user_id)",
            "CREATE INDEX IF NOT EXISTS idx_pomodoro_sessions_start_time ON pomodoro_sessions(start_time)",
            "CREATE INDEX IF NOT EXISTS idx_pomodoro_sessions_session_type ON pomodoro_sessions(session_type)",
            
            # Reminders
            "CREATE INDEX IF NOT EXISTS idx_reminders_user_id ON reminders(user_id)",
            "CREATE INDEX IF NOT EXISTS idx_reminders_due_date ON reminders(due_date)",
            "CREATE INDEX IF NOT EXISTS idx_reminders_is_completed ON reminders(is_completed)",
            
            # Files
            "CREATE INDEX IF NOT EXISTS idx_files_enhanced_user_id ON files_enhanced(user_id)",
            "CREATE INDEX IF NOT EXISTS idx_files_enhanced_lesson_id ON files_enhanced(lesson_id)",
            "CREATE INDEX IF NOT EXISTS idx_files_enhanced_type ON files_enhanced(file_type)",
            
            # Tags
            "CREATE INDEX IF NOT EXISTS idx_tags_user_id ON tags(user_id)",
            "CREATE INDEX IF NOT EXISTS idx_tags_name ON tags(name)",
            "CREATE INDEX IF NOT EXISTS idx_tags_type ON tags(tag_type)",
            
            # Tag Relationships
            "CREATE INDEX IF NOT EXISTS idx_tag_relationships_entity ON tag_relationships(entity_id, entity_type)",
            "CREATE INDEX IF NOT EXISTS idx_tag_relationships_tag ON tag_relationships(tag_id)",
            
            # External Integrations
            "CREATE INDEX IF NOT EXISTS idx_external_integrations_enhanced_user_id ON external_integrations_enhanced(user_id)",
            "CREATE INDEX IF NOT EXISTS idx_external_integrations_enhanced_platform ON external_integrations_enhanced(platform)",
            
            # External Data
            "CREATE INDEX IF NOT EXISTS idx_external_data_enhanced_user_id ON external_data_enhanced(user_id)",
            "CREATE INDEX IF NOT EXISTS idx_external_data_enhanced_integration_id ON external_data_enhanced(integration_id)",
            "CREATE INDEX IF NOT EXISTS idx_external_data_enhanced_type ON external_data_enhanced(data_type)",
            "CREATE INDEX IF NOT EXISTS idx_external_data_enhanced_external_id ON external_data_enhanced(external_id)",
            
            # Reports
            "CREATE INDEX IF NOT EXISTS idx_reports_user_id ON reports(user_id)",
            "CREATE INDEX IF NOT EXISTS idx_reports_type ON reports(report_type)",
            "CREATE INDEX IF NOT EXISTS idx_reports_created_at ON reports(created_at)",
            
            # Activity Logs
            "CREATE INDEX IF NOT EXISTS idx_activity_logs_user_id ON activity_logs(user_id)",
            "CREATE INDEX IF NOT EXISTS idx_activity_logs_action ON activity_logs(action)",
            "CREATE INDEX IF NOT EXISTS idx_activity_logs_created_at ON activity_logs(created_at)"
        ]
        
        for index in indexes:
            cursor.execute(index)
        
        conn.commit()
        print("✓ SRS-compliant schema created successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error creating schema: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

def migrate_existing_data():
    """Migrate existing data to new schema"""
    db_path = 'instance/site.db'
    
    if not os.path.exists(db_path):
        print("Database file not found!")
        return False
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("Migrating existing data...")
    
    try:
        # Migrate users
        print("Migrating users...")
        cursor.execute("SELECT * FROM user")
        users = cursor.fetchall()
        
        for user in users:
            cursor.execute("""
                INSERT INTO users_enhanced (
                    id, username, email, password_hash, role, is_active, 
                    created_at, updated_at
                ) VALUES (?, ?, ?, ?, 'student', TRUE, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
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
                INSERT INTO lessons_enhanced (
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
                INSERT INTO lesson_sections_enhanced (
                    id, lesson_id, title, content, section_type, order_index,
                    status, tags, due_date, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                section[0], section[1], section[2], section[3], section[4],
                section[7], section[13], section[12], section[6], section[8], section[9]
            ))
        
        print(f"✓ Migrated {len(sections)} lesson sections")
        
        # Migrate notes
        print("Migrating notes...")
        cursor.execute("SELECT * FROM note")
        notes = cursor.fetchall()
        
        for note in notes:
            cursor.execute("""
                INSERT INTO notes_enhanced (
                    id, user_id, title, content, tags, status, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                str(uuid.uuid4()), note[1], note[2], note[3], note[4], 'active',
                note[6] if note[6] else datetime.now(), datetime.now()
            ))
        
        print(f"✓ Migrated {len(notes)} notes")
        
        # Migrate external integrations (Google credentials)
        print("Migrating external integrations...")
        cursor.execute("SELECT * FROM google_credentials")
        credentials = cursor.fetchall()
        
        for cred in credentials:
            cursor.execute("""
                INSERT INTO external_integrations_enhanced (
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
            try:
                # Parse JSON data if it's a string
                if isinstance(data[3], str):
                    imported_json = json.loads(data[3])
                else:
                    imported_json = data[3]
                
                if data[2] == 'google_classroom_api' and isinstance(imported_json, dict) and 'courses' in imported_json:
                    courses = imported_json['courses']
                    for course in courses:
                        # Get integration_id for this user and platform
                        integration_result = cursor.execute(
                            "SELECT id FROM external_integrations_enhanced WHERE user_id = ? AND platform = 'google_classroom'", 
                            (data[1],)
                        ).fetchone()
                        
                        if integration_result:
                            integration_id = integration_result[0]
                            cursor.execute("""
                                INSERT INTO external_data_enhanced (
                                    id, user_id, integration_id, external_id, data_type,
                                    title, description, raw_data, last_synced_at
                                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                            """, (
                                str(uuid.uuid4()), data[1], integration_id,
                                course.get('id', ''), 'course', course.get('name', ''), course.get('description', ''),
                                json.dumps(course), data[4] if data[4] else datetime.now()
                            ))
            except Exception as e:
                print(f"Warning: Could not migrate external data for user {data[1]}: {e}")
                continue
        
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

def switch_to_srs_schema():
    """Switch to SRS schema by renaming tables"""
    db_path = 'instance/site.db'
    
    if not os.path.exists(db_path):
        print("Database file not found!")
        return False
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("Switching to SRS schema...")
    
    try:
        # Backup old tables
        cursor.execute("ALTER TABLE user RENAME TO user_old")
        cursor.execute("ALTER TABLE lesson RENAME TO lesson_old")
        cursor.execute("ALTER TABLE lesson_section RENAME TO lesson_section_old")
        cursor.execute("ALTER TABLE note RENAME TO note_old")
        cursor.execute("ALTER TABLE google_credentials RENAME TO google_credentials_old")
        cursor.execute("ALTER TABLE imported_data RENAME TO imported_data_old")
        
        # Rename new tables
        cursor.execute("ALTER TABLE users_enhanced RENAME TO user")
        cursor.execute("ALTER TABLE lessons_enhanced RENAME TO lesson")
        cursor.execute("ALTER TABLE lesson_sections_enhanced RENAME TO lesson_section")
        cursor.execute("ALTER TABLE notes_enhanced RENAME TO note")
        cursor.execute("ALTER TABLE external_integrations_enhanced RENAME TO external_integrations")
        cursor.execute("ALTER TABLE external_data_enhanced RENAME TO external_data")
        cursor.execute("ALTER TABLE files_enhanced RENAME TO files")
        
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
    """Run the complete SRS migration"""
    print("Starting SRS database migration...")
    
    # Step 1: Create SRS schema
    if not create_srs_schema():
        print("❌ Failed to create SRS schema")
        return
    
    # Step 2: Migrate data
    if not migrate_existing_data():
        print("❌ Failed to migrate data")
        return
    
    # Step 3: Switch to SRS schema
    if not switch_to_srs_schema():
        print("❌ Failed to switch to SRS schema")
        return
    
    print("🎉 SRS migration completed successfully!")
    print("Database now supports all SRS requirements and current system features.")

if __name__ == "__main__":
    main() 