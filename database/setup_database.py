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
                google_credentials TEXT,
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
            "ALTER TABLE user ADD COLUMN last_login TIMESTAMP",
            "ALTER TABLE user ADD COLUMN google_credentials TEXT"
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
        
        # 9. Create member table (class_member)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS member (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                lesson_id TEXT NOT NULL,
                role TEXT DEFAULT 'viewer',
                invited_by TEXT,
                joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES user(id),
                FOREIGN KEY (lesson_id) REFERENCES lesson(id),
                FOREIGN KEY (invited_by) REFERENCES user(id),
                UNIQUE(user_id, lesson_id)
            )
        """)
        print("✅ Created member table")
        
        # Add invited_by column if not exists
        try:
            cursor.execute("ALTER TABLE member ADD COLUMN invited_by TEXT REFERENCES user(id)")
            print("✅ Added invited_by column to member table")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e):
                print("   invited_by column already exists, skipping...")
            else:
                print(f"   Warning: {e}")
        
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
        # ตารางเก็บ session การทำงาน Pomodoro แต่ละรอบ
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS pomodoro_session (
                id TEXT PRIMARY KEY,                  -- UUID ของ session
                user_id TEXT NOT NULL,                -- อ้างอิงผู้ใช้
                lesson_id TEXT,                       -- อ้างอิงบทเรียน (ถ้ามี)
                section_id TEXT,                      -- อ้างอิงส่วนของบทเรียน (ถ้ามี)
                task_id TEXT,                         -- อ้างอิงงาน (ถ้ามี)
                session_type TEXT NOT NULL,           -- ประเภท session: focus, short_break, long_break
                duration INTEGER NOT NULL,            -- ระยะเวลาที่ตั้งไว้ (นาที)
                actual_duration INTEGER,              -- ระยะเวลาที่ใช้จริง (นาที)
                start_time TIMESTAMP NOT NULL,        -- เวลาที่เริ่ม session
                end_time TIMESTAMP,                   -- เวลาที่จบ session
                status TEXT DEFAULT 'active',         -- สถานะ: active, completed, interrupted
                is_completed BOOLEAN DEFAULT FALSE,   -- สถานะเสร็จสมบูรณ์
                is_interrupted BOOLEAN DEFAULT FALSE, -- สถานะถูกขัดจังหวะ
                interruption_count INTEGER DEFAULT 0, -- จำนวนครั้งที่ถูกขัดจังหวะ
                interruption_reasons TEXT,            -- เหตุผลที่ถูกขัดจังหวะ
                productivity_score INTEGER,           -- คะแนนประสิทธิภาพของ session
                task TEXT,                           -- งานที่ทำใน session นี้
                auto_start_next BOOLEAN DEFAULT TRUE,  -- เริ่ม session ถัดไปอัตโนมัติ
                notification_enabled BOOLEAN DEFAULT TRUE, -- เปิดการแจ้งเตือน
                sound_enabled BOOLEAN DEFAULT TRUE,    -- เปิดเสียง
                notes TEXT,                           -- โน้ตเพิ่มเติม
                mood_before TEXT,                     -- อารมณ์ก่อนเริ่ม session
                mood_after TEXT,                      -- อารมณ์หลังจบ session
                focus_score INTEGER,                  -- คะแนนสมาธิ
                energy_level INTEGER,                 -- ระดับพลังงาน
                difficulty_level TEXT,                -- ระดับความยาก
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, -- เวลาที่สร้าง
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, -- เวลาที่อัพเดต
                FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE, -- ลบ user แล้ว session หายด้วย
                FOREIGN KEY (lesson_id) REFERENCES lesson(id) ON DELETE SET NULL, -- ลบบทเรียนแล้วให้เป็น NULL
                FOREIGN KEY (task_id) REFERENCES task(id) ON DELETE SET NULL  -- ลบงานแล้วให้เป็น NULL
            )
        """)

        # ตารางเก็บสถิติการใช้งาน Pomodoro ของแต่ละวัน
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS pomodoro_statistics (
                id TEXT PRIMARY KEY,                  -- UUID ของสถิติ
                user_id TEXT NOT NULL,                -- อ้างอิงผู้ใช้, ลบ user แล้วสถิติหายด้วย
                date DATE NOT NULL,                   -- วันที่เก็บสถิติ
                total_sessions INTEGER DEFAULT 0,     -- จำนวน session ทั้งหมดในวันนั้น
                total_focus_time INTEGER DEFAULT 0,   -- เวลาที่ใช้โฟกัส (นาที)
                total_break_time INTEGER DEFAULT 0,   -- เวลาที่ใช้พัก (นาที)
                total_long_break_time INTEGER DEFAULT 0, -- เวลาที่ใช้พักยาว (นาที)
                total_interrupted_sessions INTEGER DEFAULT 0, -- จำนวน session ที่ถูกขัดจังหวะ
                total_completed_sessions INTEGER DEFAULT 0,   -- จำนวน session ที่ทำเสร็จ
                total_productivity_score INTEGER DEFAULT 0,   -- คะแนนประสิทธิภาพรวม
                total_tasks_completed INTEGER DEFAULT 0,      -- จำนวนงานที่ทำเสร็จ
                total_tasks INTEGER DEFAULT 0,                -- จำนวนงานทั้งหมด
                total_focus_sessions INTEGER DEFAULT 0,       -- จำนวน session ที่โฟกัส
                total_short_break_sessions INTEGER DEFAULT 0, -- จำนวน session ที่พักสั้น
                total_long_break_sessions INTEGER DEFAULT 0,  -- จำนวน session ที่พักยาว
                total_time_spent INTEGER DEFAULT 0,           -- เวลาที่ใช้ทั้งหมด (นาที)
                total_effective_time INTEGER DEFAULT 0,       -- เวลาที่ใช้แบบมีประสิทธิภาพ (นาที)
                total_ineffective_time INTEGER DEFAULT 0,     -- เวลาที่ใช้แบบไม่มีประสิทธิภาพ (นาที)
                total_abandoned_sessions INTEGER DEFAULT 0,   -- จำนวน session ที่ถูกละทิ้ง
                total_on_time_sessions INTEGER DEFAULT 0,     -- จำนวน session ที่ทำตรงเวลา
                total_late_sessions INTEGER DEFAULT 0,        -- จำนวน session ที่ทำช้า
                average_session_duration REAL DEFAULT 0.0,    -- ระยะเวลาเฉลี่ยต่อ session
                productivity_score REAL DEFAULT 0.0,          -- คะแนนประสิทธิภาพเฉลี่ย
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, -- เวลาที่สร้าง
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, -- เวลาที่อัพเดต
                FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE -- ลบ user แล้วสถิติหายด้วย
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
        
        # ============================================
        # 16. Create Grade System Tables
        # ============================================
        print("🎓 Creating Grade System tables...")
        
        # 16.1 Grade Configuration Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS grade_config (
                id TEXT PRIMARY KEY,
                lesson_id TEXT UNIQUE NOT NULL,
                grading_scale TEXT NOT NULL,
                grading_type TEXT DEFAULT 'percentage',
                total_points REAL DEFAULT 100,
                passing_grade TEXT DEFAULT 'D',
                passing_percentage REAL DEFAULT 50.0,
                show_total_grade BOOLEAN DEFAULT 1,
                allow_what_if BOOLEAN DEFAULT 1,
                show_class_average BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (lesson_id) REFERENCES lesson(id) ON DELETE CASCADE
            )
        """)
        print("✅ Created grade_config table")
        
        # 16.2 Grade Category Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS grade_category (
                id TEXT PRIMARY KEY,
                lesson_id TEXT NOT NULL,
                name TEXT NOT NULL,
                description TEXT,
                weight REAL NOT NULL,
                total_points REAL,
                drop_lowest INTEGER DEFAULT 0,
                drop_highest INTEGER DEFAULT 0,
                color TEXT DEFAULT '#3B82F6',
                icon TEXT DEFAULT 'bi-clipboard',
                order_index INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (lesson_id) REFERENCES lesson(id) ON DELETE CASCADE
            )
        """)
        print("✅ Created grade_category table")
        
        # 16.3 Grade Item Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS grade_item (
                id TEXT PRIMARY KEY,
                lesson_id TEXT NOT NULL,
                category_id TEXT NOT NULL,
                name TEXT NOT NULL,
                description TEXT,
                points_possible REAL NOT NULL,
                due_date TIMESTAMP,
                published_date TIMESTAMP,
                is_published BOOLEAN DEFAULT 0,
                is_extra_credit BOOLEAN DEFAULT 0,
                is_muted BOOLEAN DEFAULT 0,
                classwork_task_id TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (lesson_id) REFERENCES lesson(id) ON DELETE CASCADE,
                FOREIGN KEY (category_id) REFERENCES grade_category(id) ON DELETE CASCADE,
                FOREIGN KEY (classwork_task_id) REFERENCES classwork_task(id) ON DELETE SET NULL
            )
        """)
        print("✅ Created grade_item table")
        
        # Add classwork_task_id column if table already exists
        try:
            cursor.execute("ALTER TABLE grade_item ADD COLUMN classwork_task_id TEXT")
            print("✅ Added classwork_task_id column to grade_item")
        except sqlite3.OperationalError as e:
            if "duplicate column name" not in str(e):
                print(f"   Note: {e}")
        
        # 16.4 Grade Entry Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS grade_entry (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                lesson_id TEXT NOT NULL,
                grade_item_id TEXT NOT NULL,
                score REAL,
                points_possible REAL,
                status TEXT DEFAULT 'pending',
                is_excused BOOLEAN DEFAULT 0,
                comments TEXT,
                graded_by TEXT,
                graded_at TIMESTAMP,
                is_late BOOLEAN DEFAULT 0,
                late_penalty REAL DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE,
                FOREIGN KEY (lesson_id) REFERENCES lesson(id) ON DELETE CASCADE,
                FOREIGN KEY (grade_item_id) REFERENCES grade_item(id) ON DELETE CASCADE,
                FOREIGN KEY (graded_by) REFERENCES user(id)
            )
        """)
        print("✅ Created grade_entry table")
        
        # 16.5 Grade Summary Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS grade_summary (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                lesson_id TEXT NOT NULL,
                current_score REAL,
                total_possible REAL,
                percentage REAL,
                letter_grade TEXT,
                gpa REAL,
                is_passing BOOLEAN DEFAULT 1,
                points_to_pass REAL,
                points_to_next_grade TEXT,
                last_calculated TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE,
                FOREIGN KEY (lesson_id) REFERENCES lesson(id) ON DELETE CASCADE,
                UNIQUE(user_id, lesson_id)
            )
        """)
        print("✅ Created grade_summary table")
        
        # 16.6 Create Grade System Indexes
        grade_indexes = [
            "CREATE INDEX IF NOT EXISTS idx_grade_config_lesson ON grade_config(lesson_id)",
            "CREATE INDEX IF NOT EXISTS idx_grade_category_lesson ON grade_category(lesson_id)",
            "CREATE INDEX IF NOT EXISTS idx_grade_item_lesson ON grade_item(lesson_id)",
            "CREATE INDEX IF NOT EXISTS idx_grade_item_category ON grade_item(category_id)",
            "CREATE INDEX IF NOT EXISTS idx_grade_entry_user ON grade_entry(user_id)",
            "CREATE INDEX IF NOT EXISTS idx_grade_entry_lesson ON grade_entry(lesson_id)",
            "CREATE INDEX IF NOT EXISTS idx_grade_entry_item ON grade_entry(grade_item_id)",
            "CREATE INDEX IF NOT EXISTS idx_grade_entry_status ON grade_entry(status)",
            "CREATE INDEX IF NOT EXISTS idx_grade_summary_user ON grade_summary(user_id)",
            "CREATE INDEX IF NOT EXISTS idx_grade_summary_lesson ON grade_summary(lesson_id)",
            "CREATE INDEX IF NOT EXISTS idx_grade_summary_user_lesson ON grade_summary(user_id, lesson_id)"
        ]
        
        for index_sql in grade_indexes:
            try:
                cursor.execute(index_sql)
            except sqlite3.OperationalError as e:
                print(f"   Warning: {e}")
        
        print("✅ Created grade system indexes")
        print("🎉 Grade System tables created successfully!")
        
        # ============================================
        # 17. Stream System (Q&A + Announcements + Activity Timeline)
        # ============================================
        print("\n📢 Creating Stream System tables...")
        
        # 17.1 Stream Posts Table (Q&A + Announcements + Activities)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS stream_post (
                id TEXT PRIMARY KEY,
                lesson_id TEXT NOT NULL,
                user_id INTEGER NOT NULL,
                type TEXT NOT NULL DEFAULT 'question',
                title TEXT,
                content TEXT NOT NULL,
                is_pinned BOOLEAN DEFAULT 0,
                allow_comments BOOLEAN DEFAULT 1,
                has_accepted_answer BOOLEAN DEFAULT 0,
                accepted_answer_id INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP,
                FOREIGN KEY (lesson_id) REFERENCES lesson(id) ON DELETE CASCADE,
                FOREIGN KEY (user_id) REFERENCES user(id)
            )
        """)
        print("✅ Created stream_post table")
        
        # 17.2 Stream Comments Table (Answers/Comments)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS stream_comment (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                post_id TEXT NOT NULL,
                user_id INTEGER NOT NULL,
                content TEXT NOT NULL,
                is_accepted BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP,
                FOREIGN KEY (post_id) REFERENCES stream_post(id) ON DELETE CASCADE,
                FOREIGN KEY (user_id) REFERENCES user(id)
            )
        """)
        print("✅ Created stream_comment table")
        
        # 17.3 Stream Attachments Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS stream_attachment (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                post_id TEXT NOT NULL,
                type TEXT NOT NULL,
                name TEXT NOT NULL,
                url TEXT NOT NULL,
                size INTEGER,
                mime_type TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (post_id) REFERENCES stream_post(id) ON DELETE CASCADE
            )
        """)
        print("✅ Created stream_attachment table")
        
        # 17.4 Create Stream System Indexes
        stream_indexes = [
            "CREATE INDEX IF NOT EXISTS idx_stream_post_lesson ON stream_post(lesson_id)",
            "CREATE INDEX IF NOT EXISTS idx_stream_post_type ON stream_post(lesson_id, type)",
            "CREATE INDEX IF NOT EXISTS idx_stream_post_pinned ON stream_post(lesson_id, is_pinned)",
            "CREATE INDEX IF NOT EXISTS idx_stream_post_created ON stream_post(lesson_id, created_at DESC)",
            "CREATE INDEX IF NOT EXISTS idx_stream_comment_post ON stream_comment(post_id)",
            "CREATE INDEX IF NOT EXISTS idx_stream_comment_accepted ON stream_comment(post_id, is_accepted)",
            "CREATE INDEX IF NOT EXISTS idx_stream_attachment_post ON stream_attachment(post_id)"
        ]
        
        for index_sql in stream_indexes:
            try:
                cursor.execute(index_sql)
            except sqlite3.OperationalError as e:
                print(f"   Warning: {e}")
        
        print("✅ Created stream system indexes")
        print("🎉 Stream System tables created successfully!")
        
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
