#!/usr/bin/env python3
"""
Migration Script: Create Complete Class System Tables
Creates all tables needed for Google Classroom + LMS functionality
"""
import sqlite3
import sys
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

DB_PATH = Path(__file__).parent.parent.parent / 'instance' / 'site.db'

MIGRATIONS = [
    {
        'name': 'lesson_assignment',
        'sql': '''
        CREATE TABLE IF NOT EXISTS lesson_assignment (
            id TEXT PRIMARY KEY,
            lesson_id TEXT NOT NULL,
            title TEXT NOT NULL,
            description TEXT,
            instructions TEXT,
            
            -- Assignment type
            assignment_type TEXT DEFAULT 'assignment',
            
            -- Grading
            total_points INTEGER DEFAULT 100,
            grading_type TEXT DEFAULT 'points',
            
            -- Deadlines
            due_date DATETIME,
            due_time TEXT,
            allow_late_submission BOOLEAN DEFAULT 1,
            late_penalty_percent INTEGER DEFAULT 0,
            
            -- Settings
            allow_file_upload BOOLEAN DEFAULT 1,
            max_file_size INTEGER DEFAULT 10,
            allowed_file_types TEXT,
            submission_type TEXT DEFAULT 'individual',
            
            -- Visibility
            is_published BOOLEAN DEFAULT 0,
            publish_date DATETIME,
            
            -- Metadata
            order_index INTEGER DEFAULT 0,
            created_at DATETIME NOT NULL,
            updated_at DATETIME NOT NULL,
            created_by TEXT NOT NULL,
            
            FOREIGN KEY (lesson_id) REFERENCES lesson(id) ON DELETE CASCADE,
            FOREIGN KEY (created_by) REFERENCES user(id)
        )
        '''
    },
    {
        'name': 'assignment_submission',
        'sql': '''
        CREATE TABLE IF NOT EXISTS assignment_submission (
            id TEXT PRIMARY KEY,
            assignment_id TEXT NOT NULL,
            student_id TEXT NOT NULL,
            lesson_id TEXT NOT NULL,
            
            -- Submission content
            submission_text TEXT,
            submission_url TEXT,
            
            -- Status
            status TEXT DEFAULT 'draft',
            submission_date DATETIME,
            is_late BOOLEAN DEFAULT 0,
            
            -- Grading
            points_earned INTEGER,
            grade_percentage REAL,
            grade_letter TEXT,
            feedback TEXT,
            graded_by TEXT,
            graded_at DATETIME,
            
            -- Attempts
            attempt_number INTEGER DEFAULT 1,
            max_attempts INTEGER DEFAULT 1,
            
            -- Timestamps
            created_at DATETIME NOT NULL,
            updated_at DATETIME NOT NULL,
            returned_at DATETIME,
            
            FOREIGN KEY (assignment_id) REFERENCES lesson_assignment(id) ON DELETE CASCADE,
            FOREIGN KEY (student_id) REFERENCES user(id),
            FOREIGN KEY (lesson_id) REFERENCES lesson(id) ON DELETE CASCADE,
            FOREIGN KEY (graded_by) REFERENCES user(id)
        )
        '''
    },
    {
        'name': 'submission_file',
        'sql': '''
        CREATE TABLE IF NOT EXISTS submission_file (
            id TEXT PRIMARY KEY,
            submission_id TEXT NOT NULL,
            file_name TEXT NOT NULL,
            file_path TEXT NOT NULL,
            file_size INTEGER,
            file_type TEXT,
            uploaded_at DATETIME NOT NULL,
            
            FOREIGN KEY (submission_id) REFERENCES assignment_submission(id) ON DELETE CASCADE
        )
        '''
    },
    {
        'name': 'lesson_announcement',
        'sql': '''
        CREATE TABLE IF NOT EXISTS lesson_announcement (
            id TEXT PRIMARY KEY,
            lesson_id TEXT NOT NULL,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            
            -- Settings
            is_pinned BOOLEAN DEFAULT 0,
            allow_comments BOOLEAN DEFAULT 1,
            
            -- Schedule
            scheduled_date DATETIME,
            is_published BOOLEAN DEFAULT 1,
            
            -- Metadata
            created_by TEXT NOT NULL,
            created_at DATETIME NOT NULL,
            updated_at DATETIME NOT NULL,
            
            FOREIGN KEY (lesson_id) REFERENCES lesson(id) ON DELETE CASCADE,
            FOREIGN KEY (created_by) REFERENCES user(id)
        )
        '''
    },
    {
        'name': 'announcement_comment',
        'sql': '''
        CREATE TABLE IF NOT EXISTS announcement_comment (
            id TEXT PRIMARY KEY,
            announcement_id TEXT NOT NULL,
            user_id TEXT NOT NULL,
            content TEXT NOT NULL,
            parent_comment_id TEXT,
            
            is_private BOOLEAN DEFAULT 0,
            created_at DATETIME NOT NULL,
            updated_at DATETIME NOT NULL,
            
            FOREIGN KEY (announcement_id) REFERENCES lesson_announcement(id) ON DELETE CASCADE,
            FOREIGN KEY (user_id) REFERENCES user(id),
            FOREIGN KEY (parent_comment_id) REFERENCES announcement_comment(id) ON DELETE CASCADE
        )
        '''
    },
    {
        'name': 'lesson_member',
        'sql': '''
        CREATE TABLE IF NOT EXISTS lesson_member (
            id TEXT PRIMARY KEY,
            lesson_id TEXT NOT NULL,
            user_id TEXT NOT NULL,
            role TEXT NOT NULL,
            
            -- Enrollment
            joined_at DATETIME NOT NULL,
            invitation_status TEXT DEFAULT 'accepted',
            invited_by TEXT,
            
            -- Permissions
            can_post BOOLEAN DEFAULT 1,
            can_comment BOOLEAN DEFAULT 1,
            can_view_grades BOOLEAN DEFAULT 1,
            
            -- Status
            is_active BOOLEAN DEFAULT 1,
            
            FOREIGN KEY (lesson_id) REFERENCES lesson(id) ON DELETE CASCADE,
            FOREIGN KEY (user_id) REFERENCES user(id),
            FOREIGN KEY (invited_by) REFERENCES user(id),
            UNIQUE(lesson_id, user_id)
        )
        '''
    },
    {
        'name': 'lesson_grade',
        'sql': '''
        CREATE TABLE IF NOT EXISTS lesson_grade (
            id TEXT PRIMARY KEY,
            lesson_id TEXT NOT NULL,
            student_id TEXT NOT NULL,
            
            -- Overall grade
            total_points_earned REAL DEFAULT 0,
            total_points_possible REAL DEFAULT 0,
            grade_percentage REAL DEFAULT 0,
            letter_grade TEXT,
            
            -- Statistics
            assignments_completed INTEGER DEFAULT 0,
            assignments_total INTEGER DEFAULT 0,
            attendance_percentage REAL DEFAULT 0,
            
            -- Timestamps
            calculated_at DATETIME,
            updated_at DATETIME NOT NULL,
            
            FOREIGN KEY (lesson_id) REFERENCES lesson(id) ON DELETE CASCADE,
            FOREIGN KEY (student_id) REFERENCES user(id),
            UNIQUE(lesson_id, student_id)
        )
        '''
    },
    {
        'name': 'lesson_material',
        'sql': '''
        CREATE TABLE IF NOT EXISTS lesson_material (
            id TEXT PRIMARY KEY,
            lesson_id TEXT NOT NULL,
            title TEXT NOT NULL,
            description TEXT,
            
            -- Material type
            material_type TEXT NOT NULL,
            
            -- Content
            file_path TEXT,
            file_url TEXT,
            embed_code TEXT,
            
            -- Settings
            is_published BOOLEAN DEFAULT 1,
            download_allowed BOOLEAN DEFAULT 1,
            
            -- Organization
            folder TEXT,
            order_index INTEGER DEFAULT 0,
            
            -- Metadata
            file_size INTEGER,
            created_by TEXT NOT NULL,
            created_at DATETIME NOT NULL,
            updated_at DATETIME NOT NULL,
            
            FOREIGN KEY (lesson_id) REFERENCES lesson(id) ON DELETE CASCADE,
            FOREIGN KEY (created_by) REFERENCES user(id)
        )
        '''
    },
    {
        'name': 'lesson_quiz',
        'sql': '''
        CREATE TABLE IF NOT EXISTS lesson_quiz (
            id TEXT PRIMARY KEY,
            lesson_id TEXT NOT NULL,
            title TEXT NOT NULL,
            description TEXT,
            instructions TEXT,
            
            -- Settings
            total_points INTEGER DEFAULT 100,
            passing_score INTEGER DEFAULT 60,
            time_limit INTEGER,
            attempts_allowed INTEGER DEFAULT 1,
            
            -- Question settings
            shuffle_questions BOOLEAN DEFAULT 0,
            shuffle_answers BOOLEAN DEFAULT 0,
            show_correct_answers BOOLEAN DEFAULT 1,
            show_answers_after TEXT DEFAULT 'submission',
            
            -- Schedule
            available_from DATETIME,
            available_until DATETIME,
            due_date DATETIME,
            
            -- Status
            is_published BOOLEAN DEFAULT 0,
            
            -- Metadata
            created_by TEXT NOT NULL,
            created_at DATETIME NOT NULL,
            updated_at DATETIME NOT NULL,
            
            FOREIGN KEY (lesson_id) REFERENCES lesson(id) ON DELETE CASCADE,
            FOREIGN KEY (created_by) REFERENCES user(id)
        )
        '''
    },
    {
        'name': 'quiz_question',
        'sql': '''
        CREATE TABLE IF NOT EXISTS quiz_question (
            id TEXT PRIMARY KEY,
            quiz_id TEXT NOT NULL,
            question_text TEXT NOT NULL,
            question_type TEXT NOT NULL,
            
            -- Points
            points INTEGER DEFAULT 1,
            
            -- Options (JSON)
            options TEXT,
            correct_answer TEXT,
            
            -- Settings
            required BOOLEAN DEFAULT 1,
            order_index INTEGER DEFAULT 0,
            
            -- Explanation
            explanation TEXT,
            
            -- Metadata
            created_at DATETIME NOT NULL,
            updated_at DATETIME NOT NULL,
            
            FOREIGN KEY (quiz_id) REFERENCES lesson_quiz(id) ON DELETE CASCADE
        )
        '''
    },
    {
        'name': 'quiz_attempt',
        'sql': '''
        CREATE TABLE IF NOT EXISTS quiz_attempt (
            id TEXT PRIMARY KEY,
            quiz_id TEXT NOT NULL,
            student_id TEXT NOT NULL,
            lesson_id TEXT NOT NULL,
            
            -- Attempt info
            attempt_number INTEGER DEFAULT 1,
            status TEXT DEFAULT 'in_progress',
            
            -- Timing
            started_at DATETIME NOT NULL,
            submitted_at DATETIME,
            time_spent INTEGER DEFAULT 0,
            
            -- Grading
            points_earned REAL DEFAULT 0,
            points_possible REAL DEFAULT 0,
            percentage REAL DEFAULT 0,
            is_passed BOOLEAN DEFAULT 0,
            
            -- Answers (JSON)
            answers TEXT,
            
            -- Grading
            graded_at DATETIME,
            auto_graded BOOLEAN DEFAULT 1,
            
            FOREIGN KEY (quiz_id) REFERENCES lesson_quiz(id) ON DELETE CASCADE,
            FOREIGN KEY (student_id) REFERENCES user(id),
            FOREIGN KEY (lesson_id) REFERENCES lesson(id) ON DELETE CASCADE
        )
        '''
    },
    {
        'name': 'lesson_attendance',
        'sql': '''
        CREATE TABLE IF NOT EXISTS lesson_attendance (
            id TEXT PRIMARY KEY,
            lesson_id TEXT NOT NULL,
            student_id TEXT NOT NULL,
            date DATE NOT NULL,
            
            -- Status
            status TEXT DEFAULT 'present',
            
            -- Notes
            notes TEXT,
            recorded_by TEXT,
            recorded_at DATETIME NOT NULL,
            
            FOREIGN KEY (lesson_id) REFERENCES lesson(id) ON DELETE CASCADE,
            FOREIGN KEY (student_id) REFERENCES user(id),
            FOREIGN KEY (recorded_by) REFERENCES user(id),
            UNIQUE(lesson_id, student_id, date)
        )
        '''
    }
]

# Create indexes
INDEXES = [
    'CREATE INDEX IF NOT EXISTS idx_assignment_lesson ON lesson_assignment(lesson_id)',
    'CREATE INDEX IF NOT EXISTS idx_assignment_published ON lesson_assignment(is_published)',
    'CREATE INDEX IF NOT EXISTS idx_submission_assignment ON assignment_submission(assignment_id)',
    'CREATE INDEX IF NOT EXISTS idx_submission_student ON assignment_submission(student_id)',
    'CREATE INDEX IF NOT EXISTS idx_submission_status ON assignment_submission(status)',
    'CREATE INDEX IF NOT EXISTS idx_announcement_lesson ON lesson_announcement(lesson_id)',
    'CREATE INDEX IF NOT EXISTS idx_announcement_published ON lesson_announcement(is_published)',
    'CREATE INDEX IF NOT EXISTS idx_comment_announcement ON announcement_comment(announcement_id)',
    'CREATE INDEX IF NOT EXISTS idx_member_lesson ON lesson_member(lesson_id)',
    'CREATE INDEX IF NOT EXISTS idx_member_user ON lesson_member(user_id)',
    'CREATE INDEX IF NOT EXISTS idx_member_role ON lesson_member(role)',
    'CREATE INDEX IF NOT EXISTS idx_grade_lesson ON lesson_grade(lesson_id)',
    'CREATE INDEX IF NOT EXISTS idx_grade_student ON lesson_grade(student_id)',
    'CREATE INDEX IF NOT EXISTS idx_material_lesson ON lesson_material(lesson_id)',
    'CREATE INDEX IF NOT EXISTS idx_quiz_lesson ON lesson_quiz(lesson_id)',
    'CREATE INDEX IF NOT EXISTS idx_question_quiz ON quiz_question(quiz_id)',
    'CREATE INDEX IF NOT EXISTS idx_attempt_quiz ON quiz_attempt(quiz_id)',
    'CREATE INDEX IF NOT EXISTS idx_attempt_student ON quiz_attempt(student_id)',
    'CREATE INDEX IF NOT EXISTS idx_attendance_lesson ON lesson_attendance(lesson_id)',
    'CREATE INDEX IF NOT EXISTS idx_attendance_date ON lesson_attendance(date)',
]

def run_migration():
    """Run the migration"""
    print(f"\n{'='*60}")
    print("🚀 Class System Tables Migration")
    print(f"{'='*60}\n")
    
    if not DB_PATH.exists():
        print(f"❌ Database not found at: {DB_PATH}")
        return False
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        print(f"📊 Creating {len(MIGRATIONS)} tables...\n")
        
        # Create tables
        for migration in MIGRATIONS:
            try:
                cursor.execute(migration['sql'])
                print(f"  ✅ Created table: {migration['name']}")
            except Exception as e:
                print(f"  ⚠️  Table {migration['name']} already exists or error: {e}")
        
        print(f"\n📇 Creating {len(INDEXES)} indexes...\n")
        
        # Create indexes
        for index_sql in INDEXES:
            try:
                cursor.execute(index_sql)
                print(f"  ✅ Created index")
            except Exception as e:
                print(f"  ⚠️  Index error: {e}")
        
        conn.commit()
        
        # Verify tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        tables = cursor.fetchall()
        
        print(f"\n{'='*60}")
        print(f"📋 Total tables in database: {len(tables)}")
        print(f"{'='*60}\n")
        
        # Show new tables
        new_tables = [
            'lesson_assignment', 'assignment_submission', 'submission_file',
            'lesson_announcement', 'announcement_comment', 'lesson_member',
            'lesson_grade', 'lesson_material', 'lesson_quiz',
            'quiz_question', 'quiz_attempt', 'lesson_attendance'
        ]
        
        print("🆕 New Class System Tables:\n")
        for table in new_tables:
            exists = any(t[0] == table for t in tables)
            status = "✅" if exists else "❌"
            print(f"  {status} {table}")
        
        conn.close()
        
        print(f"\n{'='*60}")
        print("✅ Migration completed successfully!")
        print(f"{'='*60}\n")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = run_migration()
    sys.exit(0 if success else 1)

