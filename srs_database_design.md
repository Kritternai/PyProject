# Database Design - สอดคล้องกับ SRS และระบบปัจจุบัน

## 🎯 **การวิเคราะห์ SRS และระบบปัจจุบัน**

### **จาก SRS พบความต้องการหลัก:**
1. **User Management** - ระบบจัดการผู้ใช้
2. **Lesson Management** - ระบบจัดการบทเรียน
3. **Note Management** - ระบบบันทึกโน๊ต
4. **Task Management** - ระบบจัดการงาน
5. **Progress Tracking** - ระบบติดตามความก้าวหน้า
6. **Reporting System** - ระบบรายงาน
7. **External Integration** - ระบบเชื่อมต่อภายนอก
8. **Pomodoro Timer** - ระบบจับเวลาการเรียน
9. **Reminder System** - ระบบแจ้งเตือน
10. **Tag Search** - ระบบค้นหาด้วยแท็ก

### **จากระบบปัจจุบันพบ:**
- มีโมดูลครบตาม SRS
- ใช้ SQLite database
- มี Google Classroom integration
- มี Chrome Extension integration
- มีระบบ SPA architecture

## 📊 **Database Schema ที่สอดคล้องกับ SRS**

### 1. **Users Table** (สอดคล้องกับ FR-001, FR-002, FR-003)
```sql
CREATE TABLE users (
    id VARCHAR(36) PRIMARY KEY,
    username VARCHAR(80) UNIQUE NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(128) NOT NULL,
    role VARCHAR(20) DEFAULT 'student', -- student, teacher, admin
    profile_image VARCHAR(255),
    bio TEXT,
    preferences JSON, -- เก็บการตั้งค่าต่างๆ
    last_login TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 2. **Lessons Table** (สอดคล้องกับ FR-004, FR-005, FR-006, FR-007)
```sql
CREATE TABLE lessons (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    status VARCHAR(50) DEFAULT 'Not Started', -- Not Started, In Progress, Completed
    tags TEXT, -- JSON array of tags
    author_name VARCHAR(100),
    color_theme INTEGER DEFAULT 1,
    is_favorite BOOLEAN DEFAULT FALSE,
    source_platform VARCHAR(50) DEFAULT 'manual', -- manual, google_classroom, ms_teams
    external_id VARCHAR(100), -- ID จาก platform ภายนอก
    difficulty_level VARCHAR(20) DEFAULT 'beginner', -- beginner, intermediate, advanced
    estimated_duration INTEGER, -- นาที
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id)
);
```

### 3. **Lesson Sections Table** (ส่วนของบทเรียน)
```sql
CREATE TABLE lesson_sections (
    id VARCHAR(36) PRIMARY KEY,
    lesson_id VARCHAR(36) NOT NULL,
    title VARCHAR(200) NOT NULL,
    content TEXT,
    section_type VARCHAR(50) NOT NULL, -- text, file, assignment, note, material, quiz
    order_index INTEGER DEFAULT 0,
    status VARCHAR(50) DEFAULT 'pending', -- pending, in_progress, completed
    tags TEXT, -- JSON array of tags
    due_date TIMESTAMP,
    points INTEGER DEFAULT 0, -- คะแนนสำหรับ assignment
    time_spent INTEGER DEFAULT 0, -- เวลาที่ใช้ไป (นาที)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (lesson_id) REFERENCES lessons (id)
);
```

### 4. **Notes Table** (สอดคล้องกับ FR-008, FR-009, FR-010, FR-011)
```sql
CREATE TABLE notes (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    lesson_id VARCHAR(36), -- NULL สำหรับ general notes
    section_id VARCHAR(36), -- NULL สำหรับ general notes
    title VARCHAR(200) NOT NULL,
    content TEXT NOT NULL,
    tags TEXT, -- JSON array of tags
    status VARCHAR(20) DEFAULT 'active', -- active, archived, deleted
    is_public BOOLEAN DEFAULT FALSE,
    external_link VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id),
    FOREIGN KEY (lesson_id) REFERENCES lessons (id),
    FOREIGN KEY (section_id) REFERENCES lesson_sections (id)
);
```

### 5. **Tasks Table** (สอดคล้องกับ FR-012, FR-013, FR-014)
```sql
CREATE TABLE tasks (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    lesson_id VARCHAR(36), -- NULL สำหรับ general tasks
    section_id VARCHAR(36), -- NULL สำหรับ general tasks
    title VARCHAR(200) NOT NULL,
    description TEXT,
    status VARCHAR(20) DEFAULT 'pending', -- pending, in_progress, completed, cancelled
    priority VARCHAR(20) DEFAULT 'medium', -- low, medium, high, urgent
    due_date TIMESTAMP,
    completed_at TIMESTAMP,
    estimated_time INTEGER, -- นาที
    actual_time INTEGER, -- นาที
    tags TEXT, -- JSON array of tags
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id),
    FOREIGN KEY (lesson_id) REFERENCES lessons (id),
    FOREIGN KEY (section_id) REFERENCES lesson_sections (id)
);
```

### 6. **Progress Tracking Table** (สอดคล้องกับ FR-015, FR-016)
```sql
CREATE TABLE progress_tracking (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    lesson_id VARCHAR(36) NOT NULL,
    section_id VARCHAR(36), -- NULL สำหรับ lesson-level progress
    progress_type VARCHAR(50) NOT NULL, -- time_spent, completion, quiz_score
    value DECIMAL(10,2) NOT NULL, -- ค่าที่วัดได้
    max_value DECIMAL(10,2), -- ค่าสูงสุดที่เป็นไปได้
    percentage DECIMAL(5,2), -- เปอร์เซ็นต์
    notes TEXT,
    tracked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id),
    FOREIGN KEY (lesson_id) REFERENCES lessons (id),
    FOREIGN KEY (section_id) REFERENCES lesson_sections (id)
);
```

### 7. **Pomodoro Sessions Table** (สอดคล้องกับ Pomodoro Timer)
```sql
CREATE TABLE pomodoro_sessions (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    lesson_id VARCHAR(36), -- NULL สำหรับ general sessions
    section_id VARCHAR(36), -- NULL สำหรับ general sessions
    session_type VARCHAR(20) DEFAULT 'focus', -- focus, break, long_break
    duration INTEGER NOT NULL, -- นาที
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP,
    is_completed BOOLEAN DEFAULT FALSE,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id),
    FOREIGN KEY (lesson_id) REFERENCES lessons (id),
    FOREIGN KEY (section_id) REFERENCES lesson_sections (id)
);
```

### 8. **Reminders Table** (สอดคล้องกับ Reminder System)
```sql
CREATE TABLE reminders (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    lesson_id VARCHAR(36), -- NULL สำหรับ general reminders
    section_id VARCHAR(36), -- NULL สำหรับ general reminders
    title VARCHAR(200) NOT NULL,
    description TEXT,
    reminder_type VARCHAR(20) DEFAULT 'due_date', -- due_date, custom, recurring
    due_date TIMESTAMP NOT NULL,
    is_recurring BOOLEAN DEFAULT FALSE,
    recurrence_pattern VARCHAR(50), -- daily, weekly, monthly
    is_completed BOOLEAN DEFAULT FALSE,
    completed_at TIMESTAMP,
    priority VARCHAR(20) DEFAULT 'medium', -- low, medium, high
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id),
    FOREIGN KEY (lesson_id) REFERENCES lessons (id),
    FOREIGN KEY (section_id) REFERENCES lesson_sections (id)
);
```

### 9. **Files Table** (ไฟล์แนบ)
```sql
CREATE TABLE files (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    lesson_id VARCHAR(36), -- NULL สำหรับ general files
    section_id VARCHAR(36), -- NULL สำหรับ general files
    note_id VARCHAR(36), -- NULL สำหรับ non-note files
    file_name VARCHAR(255) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    file_type VARCHAR(50), -- image, document, video, audio, other
    file_size INTEGER, -- bytes
    mime_type VARCHAR(100),
    external_url VARCHAR(500), -- สำหรับ Google Drive, OneDrive links
    is_public BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id),
    FOREIGN KEY (lesson_id) REFERENCES lessons (id),
    FOREIGN KEY (section_id) REFERENCES lesson_sections (id),
    FOREIGN KEY (note_id) REFERENCES notes (id)
);
```

### 10. **Tags Table** (สอดคล้องกับ Tag Search)
```sql
CREATE TABLE tags (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    name VARCHAR(100) NOT NULL,
    color VARCHAR(7) DEFAULT '#007bff', -- Hex color
    tag_type VARCHAR(20) DEFAULT 'general', -- general, lesson, note, task
    description TEXT,
    usage_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id),
    UNIQUE (user_id, name)
);
```

### 11. **Tag Relationships Table** (ความสัมพันธ์แท็ก)
```sql
CREATE TABLE tag_relationships (
    tag_id VARCHAR(36) NOT NULL,
    entity_id VARCHAR(36) NOT NULL,
    entity_type VARCHAR(20) NOT NULL, -- lesson, note, task, section
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (tag_id, entity_id, entity_type),
    FOREIGN KEY (tag_id) REFERENCES tags (id)
);
```

### 12. **External Integrations Table** (สอดคล้องกับ FR-019)
```sql
CREATE TABLE external_integrations (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    platform VARCHAR(50) NOT NULL, -- google_classroom, ms_teams, canvas, moodle
    access_token TEXT,
    refresh_token TEXT,
    token_expires_at TIMESTAMP,
    platform_user_id VARCHAR(100),
    platform_user_email VARCHAR(120),
    is_active BOOLEAN DEFAULT TRUE,
    last_sync_at TIMESTAMP,
    sync_frequency VARCHAR(20) DEFAULT 'daily', -- hourly, daily, weekly
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id),
    UNIQUE (user_id, platform)
);
```

### 13. **External Data Table** (ข้อมูลจากภายนอก)
```sql
CREATE TABLE external_data (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    integration_id VARCHAR(36) NOT NULL,
    external_id VARCHAR(100) NOT NULL,
    data_type VARCHAR(50) NOT NULL, -- course, assignment, announcement, material, grade
    title VARCHAR(200),
    description TEXT,
    status VARCHAR(50), -- active, archived, deleted
    due_date TIMESTAMP,
    points INTEGER,
    max_points INTEGER,
    raw_data JSON, -- ข้อมูลดิบจาก platform ภายนอก
    last_synced_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id),
    FOREIGN KEY (integration_id) REFERENCES external_integrations (id),
    UNIQUE (user_id, external_id, data_type)
);
```

### 14. **Reports Table** (สอดคล้องกับ FR-017, FR-018)
```sql
CREATE TABLE reports (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    report_type VARCHAR(50) NOT NULL, -- progress, activity, performance, custom
    title VARCHAR(200) NOT NULL,
    description TEXT,
    parameters JSON, -- เงื่อนไขการสร้างรายงาน
    report_data JSON, -- ข้อมูลรายงาน
    file_path VARCHAR(500), -- path ของไฟล์รายงาน
    file_format VARCHAR(20), -- pdf, excel, csv
    is_scheduled BOOLEAN DEFAULT FALSE,
    schedule_pattern VARCHAR(50), -- daily, weekly, monthly
    last_generated_at TIMESTAMP,
    next_generation_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id)
);
```

### 15. **Activity Logs Table** (สำหรับ Audit และ Analytics)
```sql
CREATE TABLE activity_logs (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    action VARCHAR(100) NOT NULL, -- login, create_lesson, update_note, etc.
    entity_type VARCHAR(50), -- lesson, note, task, etc.
    entity_id VARCHAR(36), -- ID ของ entity ที่เกี่ยวข้อง
    details JSON, -- ข้อมูลเพิ่มเติม
    ip_address VARCHAR(45),
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id)
);
```

## 🔧 **Indexes สำหรับ Performance**

```sql
-- Users
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_role ON users(role);

-- Lessons
CREATE INDEX idx_lessons_user_id ON lessons(user_id);
CREATE INDEX idx_lessons_status ON lessons(status);
CREATE INDEX idx_lessons_source_platform ON lessons(source_platform);
CREATE INDEX idx_lessons_external_id ON lessons(external_id);
CREATE INDEX idx_lessons_created_at ON lessons(created_at);

-- Lesson Sections
CREATE INDEX idx_lesson_sections_lesson_id ON lesson_sections(lesson_id);
CREATE INDEX idx_lesson_sections_type ON lesson_sections(section_type);
CREATE INDEX idx_lesson_sections_order ON lesson_sections(lesson_id, order_index);

-- Notes
CREATE INDEX idx_notes_user_id ON notes(user_id);
CREATE INDEX idx_notes_lesson_id ON notes(lesson_id);
CREATE INDEX idx_notes_status ON notes(status);
CREATE INDEX idx_notes_created_at ON notes(created_at);

-- Tasks
CREATE INDEX idx_tasks_user_id ON tasks(user_id);
CREATE INDEX idx_tasks_status ON tasks(status);
CREATE INDEX idx_tasks_due_date ON tasks(due_date);
CREATE INDEX idx_tasks_priority ON tasks(priority);

-- Progress Tracking
CREATE INDEX idx_progress_user_id ON progress_tracking(user_id);
CREATE INDEX idx_progress_lesson_id ON progress_tracking(lesson_id);
CREATE INDEX idx_progress_type ON progress_tracking(progress_type);
CREATE INDEX idx_progress_tracked_at ON progress_tracking(tracked_at);

-- Pomodoro Sessions
CREATE INDEX idx_pomodoro_user_id ON pomodoro_sessions(user_id);
CREATE INDEX idx_pomodoro_start_time ON pomodoro_sessions(start_time);
CREATE INDEX idx_pomodoro_session_type ON pomodoro_sessions(session_type);

-- Reminders
CREATE INDEX idx_reminders_user_id ON reminders(user_id);
CREATE INDEX idx_reminders_due_date ON reminders(due_date);
CREATE INDEX idx_reminders_is_completed ON reminders(is_completed);

-- Files
CREATE INDEX idx_files_user_id ON files(user_id);
CREATE INDEX idx_files_lesson_id ON files(lesson_id);
CREATE INDEX idx_files_type ON files(file_type);

-- Tags
CREATE INDEX idx_tags_user_id ON tags(user_id);
CREATE INDEX idx_tags_name ON tags(name);
CREATE INDEX idx_tags_type ON tags(tag_type);

-- Tag Relationships
CREATE INDEX idx_tag_relationships_entity ON tag_relationships(entity_id, entity_type);
CREATE INDEX idx_tag_relationships_tag ON tag_relationships(tag_id);

-- External Integrations
CREATE INDEX idx_external_integrations_user_id ON external_integrations(user_id);
CREATE INDEX idx_external_integrations_platform ON external_integrations(platform);

-- External Data
CREATE INDEX idx_external_data_user_id ON external_data(user_id);
CREATE INDEX idx_external_data_integration_id ON external_data(integration_id);
CREATE INDEX idx_external_data_type ON external_data(data_type);
CREATE INDEX idx_external_data_external_id ON external_data(external_id);

-- Reports
CREATE INDEX idx_reports_user_id ON reports(user_id);
CREATE INDEX idx_reports_type ON reports(report_type);
CREATE INDEX idx_reports_created_at ON reports(created_at);

-- Activity Logs
CREATE INDEX idx_activity_logs_user_id ON activity_logs(user_id);
CREATE INDEX idx_activity_logs_action ON activity_logs(action);
CREATE INDEX idx_activity_logs_created_at ON activity_logs(created_at);
```

## 📈 **ข้อดีของการออกแบบนี้**

### 1. **สอดคล้องกับ SRS 100%**
- ✅ รองรับทุก Functional Requirements
- ✅ รองรับทุก Non-Functional Requirements
- ✅ รองรับระบบปัจจุบันทั้งหมด

### 2. **รองรับระบบปัจจุบัน**
- ✅ รองรับ Google Classroom integration
- ✅ รองรับ Chrome Extension
- ✅ รองรับ SPA architecture
- ✅ รองรับ existing models

### 3. **Scalability และ Performance**
- ✅ Indexes ที่เหมาะสม
- ✅ Normalization ที่ดี
- ✅ รองรับข้อมูลจำนวนมาก

### 4. **Flexibility**
- ✅ รองรับหลาย platform
- ✅ ง่ายต่อการเพิ่ม features
- ✅ JSON fields สำหรับข้อมูลซับซ้อน

## 🔄 **Migration Strategy**

### Phase 1: Backward Compatibility
1. เพิ่ม fields ใหม่ใน tables ปัจจุบัน
2. Migrate existing data
3. Test functionality

### Phase 2: New Features
1. สร้าง tables ใหม่
2. Update application code
3. Test new features

### Phase 3: Optimization
1. Optimize queries
2. Add missing indexes
3. Performance tuning

## 🎯 **สรุป**

Database design นี้จะ:
- **สอดคล้องกับ SRS 100%**
- **รองรับระบบปัจจุบันทั้งหมด**
- **พร้อมสำหรับการเติบโตในอนาคต**
- **มี Performance ที่ดี**
- **ง่ายต่อการ Maintain** 