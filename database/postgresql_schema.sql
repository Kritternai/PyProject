-- PostgreSQL Schema for Smart Learning Hub
-- Complete database schema based on the project structure

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================
-- 1. CORE TABLES
-- ============================================

-- User table
CREATE TABLE IF NOT EXISTS "user" (
    id VARCHAR(36) PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    profile_image TEXT,
    bio TEXT,
    role VARCHAR(20) DEFAULT 'student',
    preferences TEXT,
    google_credentials TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    email_verified BOOLEAN DEFAULT FALSE,
    last_login TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    total_lessons INTEGER DEFAULT 0,
    total_notes INTEGER DEFAULT 0,
    total_tasks INTEGER DEFAULT 0
);

-- Lesson table
CREATE TABLE IF NOT EXISTS lesson (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    content TEXT,
    status VARCHAR(20) DEFAULT 'not_started',
    color_theme INTEGER DEFAULT 1,
    is_favorite BOOLEAN DEFAULT FALSE,
    difficulty_level VARCHAR(20) DEFAULT 'beginner',
    estimated_duration INTEGER DEFAULT 0,
    author_name VARCHAR(100),
    tags TEXT,
    progress_percentage INTEGER DEFAULT 0,
    total_sections INTEGER DEFAULT 0,
    completed_sections INTEGER DEFAULT 0,
    total_time_spent INTEGER DEFAULT 0,
    source_platform VARCHAR(50) DEFAULT 'manual',
    external_id VARCHAR(100),
    external_url TEXT,
    subject VARCHAR(100),
    grade_level VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES "user"(id) ON DELETE CASCADE
);

-- Lesson Section table
CREATE TABLE IF NOT EXISTS lesson_section (
    id VARCHAR(36) PRIMARY KEY,
    lesson_id VARCHAR(36) NOT NULL,
    title VARCHAR(200) NOT NULL,
    content TEXT,
    order_index INTEGER DEFAULT 0,
    is_completed BOOLEAN DEFAULT FALSE,
    time_spent INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (lesson_id) REFERENCES lesson(id) ON DELETE CASCADE
);

-- Note table
CREATE TABLE IF NOT EXISTS note (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    lesson_id VARCHAR(36),
    title VARCHAR(200) NOT NULL,
    content TEXT,
    status VARCHAR(20) DEFAULT 'pending',
    tags TEXT,
    note_type VARCHAR(20) DEFAULT 'text',
    section_id VARCHAR(36),
    is_public BOOLEAN DEFAULT FALSE,
    view_count INTEGER DEFAULT 0,
    word_count INTEGER DEFAULT 0,
    external_link TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES "user"(id) ON DELETE CASCADE,
    FOREIGN KEY (lesson_id) REFERENCES lesson(id) ON DELETE SET NULL,
    FOREIGN KEY (section_id) REFERENCES lesson_section(id) ON DELETE SET NULL
);

-- Note File table
CREATE TABLE IF NOT EXISTS note_file (
    id VARCHAR(36) PRIMARY KEY,
    note_id VARCHAR(36) NOT NULL,
    file_path TEXT NOT NULL,
    file_type VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (note_id) REFERENCES note(id) ON DELETE CASCADE
);

-- Task table
CREATE TABLE IF NOT EXISTS task (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    status VARCHAR(20) DEFAULT 'pending',
    priority VARCHAR(20) DEFAULT 'medium',
    due_date TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES "user"(id) ON DELETE CASCADE
);

-- ============================================
-- 2. CLASSROOM TABLES
-- ============================================

-- Announcement table
CREATE TABLE IF NOT EXISTS announcement (
    id VARCHAR(36) PRIMARY KEY,
    lesson_id VARCHAR(36) NOT NULL,
    user_id VARCHAR(36) NOT NULL,
    title VARCHAR(200) NOT NULL,
    content TEXT,
    status VARCHAR(20) DEFAULT 'active',
    is_pinned BOOLEAN DEFAULT FALSE,
    allow_comments BOOLEAN DEFAULT TRUE,
    scheduled_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (lesson_id) REFERENCES lesson(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES "user"(id) ON DELETE CASCADE
);

-- Announcement Comment table
CREATE TABLE IF NOT EXISTS announcement_comment (
    id VARCHAR(36) PRIMARY KEY,
    announcement_id VARCHAR(36) NOT NULL,
    user_id VARCHAR(36) NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (announcement_id) REFERENCES announcement(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES "user"(id) ON DELETE CASCADE
);

-- Assignment table
CREATE TABLE IF NOT EXISTS assignment (
    id VARCHAR(36) PRIMARY KEY,
    lesson_id VARCHAR(36) NOT NULL,
    user_id VARCHAR(36) NOT NULL,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    due_date TIMESTAMP,
    points INTEGER DEFAULT 0,
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (lesson_id) REFERENCES lesson(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES "user"(id) ON DELETE CASCADE
);

-- Member table (class members)
CREATE TABLE IF NOT EXISTS member (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    lesson_id VARCHAR(36) NOT NULL,
    role VARCHAR(20) DEFAULT 'viewer',
    invited_by VARCHAR(36),
    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES "user"(id) ON DELETE CASCADE,
    FOREIGN KEY (lesson_id) REFERENCES lesson(id) ON DELETE CASCADE,
    FOREIGN KEY (invited_by) REFERENCES "user"(id) ON DELETE SET NULL,
    UNIQUE(user_id, lesson_id)
);

-- ============================================
-- 3. POMODORO SYSTEM TABLES
-- ============================================

-- Pomodoro Session table
CREATE TABLE IF NOT EXISTS pomodoro_session (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    lesson_id VARCHAR(36),
    section_id VARCHAR(36),
    task_id VARCHAR(36),
    session_type VARCHAR(20) NOT NULL,
    duration INTEGER NOT NULL,
    actual_duration INTEGER,
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP,
    status VARCHAR(20) DEFAULT 'active',
    is_completed BOOLEAN DEFAULT FALSE,
    is_interrupted BOOLEAN DEFAULT FALSE,
    interruption_count INTEGER DEFAULT 0,
    interruption_reasons TEXT,
    productivity_score INTEGER,
    task TEXT,
    auto_start_next BOOLEAN DEFAULT TRUE,
    notification_enabled BOOLEAN DEFAULT TRUE,
    sound_enabled BOOLEAN DEFAULT TRUE,
    notes TEXT,
    mood_before VARCHAR(50),
    mood_after VARCHAR(50),
    focus_score INTEGER,
    energy_level INTEGER,
    difficulty_level VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES "user"(id) ON DELETE CASCADE,
    FOREIGN KEY (lesson_id) REFERENCES lesson(id) ON DELETE SET NULL,
    FOREIGN KEY (section_id) REFERENCES lesson_section(id) ON DELETE SET NULL,
    FOREIGN KEY (task_id) REFERENCES task(id) ON DELETE SET NULL
);

-- Pomodoro Statistics table
CREATE TABLE IF NOT EXISTS pomodoro_statistics (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    date DATE NOT NULL,
    total_sessions INTEGER DEFAULT 0,
    total_focus_time INTEGER DEFAULT 0,
    total_break_time INTEGER DEFAULT 0,
    total_long_break_time INTEGER DEFAULT 0,
    total_interrupted_sessions INTEGER DEFAULT 0,
    total_completed_sessions INTEGER DEFAULT 0,
    total_productivity_score INTEGER DEFAULT 0,
    total_tasks_completed INTEGER DEFAULT 0,
    total_tasks INTEGER DEFAULT 0,
    total_focus_sessions INTEGER DEFAULT 0,
    total_short_break_sessions INTEGER DEFAULT 0,
    total_long_break_sessions INTEGER DEFAULT 0,
    total_time_spent INTEGER DEFAULT 0,
    total_effective_time INTEGER DEFAULT 0,
    total_ineffective_time INTEGER DEFAULT 0,
    total_abandoned_sessions INTEGER DEFAULT 0,
    total_on_time_sessions INTEGER DEFAULT 0,
    total_late_sessions INTEGER DEFAULT 0,
    average_session_duration REAL DEFAULT 0.0,
    productivity_score REAL DEFAULT 0.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES "user"(id) ON DELETE CASCADE
);

-- ============================================
-- 4. CLASSWORK SYSTEM TABLES
-- ============================================

-- Classwork Task table
CREATE TABLE IF NOT EXISTS classwork_task (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    lesson_id VARCHAR(36) NOT NULL,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    subject VARCHAR(100),
    category VARCHAR(100),
    priority VARCHAR(20) DEFAULT 'medium',
    status VARCHAR(20) DEFAULT 'todo',
    due_date TIMESTAMP,
    estimated_time INTEGER DEFAULT 0,
    actual_time INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES "user"(id) ON DELETE CASCADE,
    FOREIGN KEY (lesson_id) REFERENCES lesson(id) ON DELETE CASCADE
);

-- Classwork Material table
CREATE TABLE IF NOT EXISTS classwork_material (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    lesson_id VARCHAR(36) NOT NULL,
    task_id VARCHAR(36),
    title VARCHAR(200) NOT NULL,
    description TEXT,
    file_path TEXT,
    file_type VARCHAR(50),
    file_size INTEGER,
    subject VARCHAR(100),
    category VARCHAR(100),
    tags TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES "user"(id) ON DELETE CASCADE,
    FOREIGN KEY (lesson_id) REFERENCES lesson(id) ON DELETE CASCADE,
    FOREIGN KEY (task_id) REFERENCES classwork_task(id) ON DELETE SET NULL
);

-- Classwork Note table
CREATE TABLE IF NOT EXISTS classwork_note (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    lesson_id VARCHAR(36) NOT NULL,
    task_id VARCHAR(36),
    title VARCHAR(200) NOT NULL,
    content TEXT,
    subject VARCHAR(100),
    category VARCHAR(100),
    tags TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES "user"(id) ON DELETE CASCADE,
    FOREIGN KEY (lesson_id) REFERENCES lesson(id) ON DELETE CASCADE,
    FOREIGN KEY (task_id) REFERENCES classwork_task(id) ON DELETE SET NULL
);

-- Classwork Session table
CREATE TABLE IF NOT EXISTS classwork_session (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    lesson_id VARCHAR(36) NOT NULL,
    task_id VARCHAR(36),
    session_name VARCHAR(200),
    start_time TIMESTAMP,
    end_time TIMESTAMP,
    duration INTEGER DEFAULT 0,
    break_duration INTEGER DEFAULT 0,
    productivity_score INTEGER DEFAULT 0,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES "user"(id) ON DELETE CASCADE,
    FOREIGN KEY (lesson_id) REFERENCES lesson(id) ON DELETE CASCADE,
    FOREIGN KEY (task_id) REFERENCES classwork_task(id) ON DELETE SET NULL
);

-- Classwork Progress table
CREATE TABLE IF NOT EXISTS classwork_progress (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    lesson_id VARCHAR(36) NOT NULL,
    task_id VARCHAR(36),
    progress_percentage INTEGER DEFAULT 0,
    completed_at TIMESTAMP,
    time_spent INTEGER DEFAULT 0,
    achievement_badges TEXT,
    streak_count INTEGER DEFAULT 0,
    last_activity TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES "user"(id) ON DELETE CASCADE,
    FOREIGN KEY (lesson_id) REFERENCES lesson(id) ON DELETE CASCADE,
    FOREIGN KEY (task_id) REFERENCES classwork_task(id) ON DELETE SET NULL
);

-- ============================================
-- 5. GRADE SYSTEM TABLES
-- ============================================

-- Grade Configuration table
CREATE TABLE IF NOT EXISTS grade_config (
    id VARCHAR(36) PRIMARY KEY,
    lesson_id VARCHAR(36) UNIQUE NOT NULL,
    grading_scale VARCHAR(50) NOT NULL,
    grading_type VARCHAR(20) DEFAULT 'percentage',
    total_points REAL DEFAULT 100,
    passing_grade VARCHAR(5) DEFAULT 'D',
    passing_percentage REAL DEFAULT 50.0,
    show_total_grade BOOLEAN DEFAULT TRUE,
    allow_what_if BOOLEAN DEFAULT TRUE,
    show_class_average BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (lesson_id) REFERENCES lesson(id) ON DELETE CASCADE
);

-- Grade Category table
CREATE TABLE IF NOT EXISTS grade_category (
    id VARCHAR(36) PRIMARY KEY,
    lesson_id VARCHAR(36) NOT NULL,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    weight REAL NOT NULL,
    total_points REAL,
    drop_lowest INTEGER DEFAULT 0,
    drop_highest INTEGER DEFAULT 0,
    color VARCHAR(7) DEFAULT '#3B82F6',
    icon VARCHAR(50) DEFAULT 'bi-clipboard',
    order_index INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (lesson_id) REFERENCES lesson(id) ON DELETE CASCADE
);

-- Grade Item table
CREATE TABLE IF NOT EXISTS grade_item (
    id VARCHAR(36) PRIMARY KEY,
    lesson_id VARCHAR(36) NOT NULL,
    category_id VARCHAR(36) NOT NULL,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    points_possible REAL NOT NULL,
    due_date TIMESTAMP,
    published_date TIMESTAMP,
    is_published BOOLEAN DEFAULT FALSE,
    is_extra_credit BOOLEAN DEFAULT FALSE,
    is_muted BOOLEAN DEFAULT FALSE,
    classwork_task_id VARCHAR(36),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (lesson_id) REFERENCES lesson(id) ON DELETE CASCADE,
    FOREIGN KEY (category_id) REFERENCES grade_category(id) ON DELETE CASCADE,
    FOREIGN KEY (classwork_task_id) REFERENCES classwork_task(id) ON DELETE SET NULL
);

-- Grade Entry table
CREATE TABLE IF NOT EXISTS grade_entry (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    lesson_id VARCHAR(36) NOT NULL,
    grade_item_id VARCHAR(36) NOT NULL,
    score REAL,
    points_possible REAL,
    status VARCHAR(20) DEFAULT 'pending',
    is_excused BOOLEAN DEFAULT FALSE,
    comments TEXT,
    graded_by VARCHAR(36),
    graded_at TIMESTAMP,
    is_late BOOLEAN DEFAULT FALSE,
    late_penalty REAL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES "user"(id) ON DELETE CASCADE,
    FOREIGN KEY (lesson_id) REFERENCES lesson(id) ON DELETE CASCADE,
    FOREIGN KEY (grade_item_id) REFERENCES grade_item(id) ON DELETE CASCADE,
    FOREIGN KEY (graded_by) REFERENCES "user"(id) ON DELETE SET NULL
);

-- Grade Summary table
CREATE TABLE IF NOT EXISTS grade_summary (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    lesson_id VARCHAR(36) NOT NULL,
    current_score REAL,
    total_possible REAL,
    percentage REAL,
    letter_grade VARCHAR(5),
    gpa REAL,
    is_passing BOOLEAN DEFAULT TRUE,
    points_to_pass REAL,
    points_to_next_grade VARCHAR(100),
    last_calculated TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES "user"(id) ON DELETE CASCADE,
    FOREIGN KEY (lesson_id) REFERENCES lesson(id) ON DELETE CASCADE,
    UNIQUE(user_id, lesson_id)
);

-- ============================================
-- 6. STREAM SYSTEM TABLES
-- ============================================

-- Stream Post table (Q&A + Announcements + Activities)
CREATE TABLE IF NOT EXISTS stream_post (
    id VARCHAR(36) PRIMARY KEY,
    lesson_id VARCHAR(36) NOT NULL,
    user_id VARCHAR(36) NOT NULL,
    type VARCHAR(20) NOT NULL DEFAULT 'question',
    title VARCHAR(200),
    content TEXT NOT NULL,
    is_pinned BOOLEAN DEFAULT FALSE,
    allow_comments BOOLEAN DEFAULT TRUE,
    has_accepted_answer BOOLEAN DEFAULT FALSE,
    accepted_answer_id VARCHAR(36),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP,
    FOREIGN KEY (lesson_id) REFERENCES lesson(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES "user"(id) ON DELETE CASCADE,
    FOREIGN KEY (accepted_answer_id) REFERENCES stream_comment(id) ON DELETE SET NULL
);

-- Stream Comment table (Answers/Comments)
CREATE TABLE IF NOT EXISTS stream_comment (
    id VARCHAR(36) PRIMARY KEY,
    post_id VARCHAR(36) NOT NULL,
    user_id VARCHAR(36) NOT NULL,
    content TEXT NOT NULL,
    is_accepted BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP,
    FOREIGN KEY (post_id) REFERENCES stream_post(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES "user"(id) ON DELETE CASCADE
);

-- Stream Attachment table
CREATE TABLE IF NOT EXISTS stream_attachment (
    id VARCHAR(36) PRIMARY KEY,
    post_id VARCHAR(36) NOT NULL,
    type VARCHAR(50) NOT NULL,
    name VARCHAR(200) NOT NULL,
    url TEXT NOT NULL,
    size INTEGER,
    mime_type VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (post_id) REFERENCES stream_post(id) ON DELETE CASCADE
);

-- ============================================
-- 7. INDEXES FOR PERFORMANCE
-- ============================================

-- User indexes
CREATE INDEX IF NOT EXISTS idx_user_email ON "user"(email);
CREATE INDEX IF NOT EXISTS idx_user_username ON "user"(username);
CREATE INDEX IF NOT EXISTS idx_user_role ON "user"(role);

-- Lesson indexes
CREATE INDEX IF NOT EXISTS idx_lesson_user_id ON lesson(user_id);
CREATE INDEX IF NOT EXISTS idx_lesson_status ON lesson(status);
CREATE INDEX IF NOT EXISTS idx_lesson_subject ON lesson(subject);

-- Note indexes
CREATE INDEX IF NOT EXISTS idx_note_user_id ON note(user_id);
CREATE INDEX IF NOT EXISTS idx_note_lesson_id ON note(lesson_id);
CREATE INDEX IF NOT EXISTS idx_note_section_id ON note(section_id);

-- Task indexes
CREATE INDEX IF NOT EXISTS idx_task_user_id ON task(user_id);
CREATE INDEX IF NOT EXISTS idx_task_status ON task(status);
CREATE INDEX IF NOT EXISTS idx_task_priority ON task(priority);

-- Announcement indexes
CREATE INDEX IF NOT EXISTS idx_announcement_lesson_id ON announcement(lesson_id);
CREATE INDEX IF NOT EXISTS idx_announcement_user_id ON announcement(user_id);
CREATE INDEX IF NOT EXISTS idx_announcement_pinned ON announcement(lesson_id, is_pinned);

-- Assignment indexes
CREATE INDEX IF NOT EXISTS idx_assignment_lesson_id ON assignment(lesson_id);
CREATE INDEX IF NOT EXISTS idx_assignment_user_id ON assignment(user_id);

-- Member indexes
CREATE INDEX IF NOT EXISTS idx_member_user_id ON member(user_id);
CREATE INDEX IF NOT EXISTS idx_member_lesson_id ON member(lesson_id);
CREATE INDEX IF NOT EXISTS idx_member_role ON member(role);

-- Pomodoro indexes
CREATE INDEX IF NOT EXISTS idx_pomodoro_session_user_id ON pomodoro_session(user_id);
CREATE INDEX IF NOT EXISTS idx_pomodoro_session_lesson_id ON pomodoro_session(lesson_id);
CREATE INDEX IF NOT EXISTS idx_pomodoro_session_date ON pomodoro_session(start_time);
CREATE INDEX IF NOT EXISTS idx_pomodoro_statistics_user_date ON pomodoro_statistics(user_id, date);

-- Classwork indexes
CREATE INDEX IF NOT EXISTS idx_classwork_task_user_id ON classwork_task(user_id);
CREATE INDEX IF NOT EXISTS idx_classwork_task_lesson_id ON classwork_task(lesson_id);
CREATE INDEX IF NOT EXISTS idx_classwork_task_status ON classwork_task(status);
CREATE INDEX IF NOT EXISTS idx_classwork_task_priority ON classwork_task(priority);

-- Grade indexes
CREATE INDEX IF NOT EXISTS idx_grade_config_lesson ON grade_config(lesson_id);
CREATE INDEX IF NOT EXISTS idx_grade_category_lesson ON grade_category(lesson_id);
CREATE INDEX IF NOT EXISTS idx_grade_item_lesson ON grade_item(lesson_id);
CREATE INDEX IF NOT EXISTS idx_grade_item_category ON grade_item(category_id);
CREATE INDEX IF NOT EXISTS idx_grade_entry_user ON grade_entry(user_id);
CREATE INDEX IF NOT EXISTS idx_grade_entry_lesson ON grade_entry(lesson_id);
CREATE INDEX IF NOT EXISTS idx_grade_entry_item ON grade_entry(grade_item_id);
CREATE INDEX IF NOT EXISTS idx_grade_summary_user_lesson ON grade_summary(user_id, lesson_id);

-- Stream indexes
CREATE INDEX IF NOT EXISTS idx_stream_post_lesson ON stream_post(lesson_id);
CREATE INDEX IF NOT EXISTS idx_stream_post_type ON stream_post(lesson_id, type);
CREATE INDEX IF NOT EXISTS idx_stream_post_pinned ON stream_post(lesson_id, is_pinned);
CREATE INDEX IF NOT EXISTS idx_stream_post_created ON stream_post(lesson_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_stream_comment_post ON stream_comment(post_id);
CREATE INDEX IF NOT EXISTS idx_stream_comment_accepted ON stream_comment(post_id, is_accepted);
CREATE INDEX IF NOT EXISTS idx_stream_attachment_post ON stream_attachment(post_id);

-- ============================================
-- 8. COMMENTS AND DOCUMENTATION
-- ============================================

COMMENT ON TABLE "user" IS 'Core user accounts and profiles';
COMMENT ON TABLE lesson IS 'Learning lessons and courses';
COMMENT ON TABLE lesson_section IS 'Individual sections within lessons';
COMMENT ON TABLE note IS 'User notes and annotations';
COMMENT ON TABLE task IS 'User tasks and assignments';
COMMENT ON TABLE announcement IS 'Class announcements';
COMMENT ON TABLE assignment IS 'Class assignments';
COMMENT ON TABLE member IS 'Class membership and roles';
COMMENT ON TABLE pomodoro_session IS 'Pomodoro timer sessions';
COMMENT ON TABLE pomodoro_statistics IS 'Daily Pomodoro statistics';
COMMENT ON TABLE classwork_task IS 'Classwork tasks and activities';
COMMENT ON TABLE classwork_material IS 'Classwork materials and files';
COMMENT ON TABLE grade_config IS 'Grade system configuration';
COMMENT ON TABLE grade_category IS 'Grade categories and weights';
COMMENT ON TABLE grade_item IS 'Individual grade items';
COMMENT ON TABLE grade_entry IS 'Student grade entries';
COMMENT ON TABLE grade_summary IS 'Student grade summaries';
COMMENT ON TABLE stream_post IS 'Stream posts (Q&A, announcements)';
COMMENT ON TABLE stream_comment IS 'Comments and answers on stream posts';
COMMENT ON TABLE stream_attachment IS 'File attachments for stream posts';
