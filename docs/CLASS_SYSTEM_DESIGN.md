# 📚 Complete Class System Design (Google Classroom + LMS)

## 🎯 Overview
สร้างระบบ Class/Lesson ที่ครบถ้วนแบบ Google Classroom รวมกับ LMS

## 📊 Database Schema Design

### ✅ Tables ที่มีอยู่แล้ว
1. **lesson** - Main class/course
2. **lesson_section** - Content sections (text, video, material, etc.)
3. **note** - Student notes
4. **files** - File uploads

### 🆕 Tables ที่ต้องสร้างใหม่

#### 1. **lesson_assignment** (งานที่มอบหมาย)
```sql
CREATE TABLE lesson_assignment (
    id TEXT PRIMARY KEY,
    lesson_id TEXT NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    instructions TEXT,
    
    -- Assignment type
    assignment_type TEXT DEFAULT 'assignment',  -- assignment, quiz, material, question
    
    -- Grading
    total_points INTEGER DEFAULT 100,
    grading_type TEXT DEFAULT 'points',  -- points, percentage, pass_fail
    
    -- Deadlines
    due_date DATETIME,
    due_time TEXT,
    allow_late_submission BOOLEAN DEFAULT 1,
    late_penalty_percent INTEGER DEFAULT 0,
    
    -- Settings
    allow_file_upload BOOLEAN DEFAULT 1,
    max_file_size INTEGER DEFAULT 10,  -- MB
    allowed_file_types TEXT,  -- JSON array
    submission_type TEXT DEFAULT 'individual',  -- individual, group
    
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
);
```

#### 2. **assignment_submission** (การส่งงาน)
```sql
CREATE TABLE assignment_submission (
    id TEXT PRIMARY KEY,
    assignment_id TEXT NOT NULL,
    student_id TEXT NOT NULL,
    lesson_id TEXT NOT NULL,
    
    -- Submission content
    submission_text TEXT,
    submission_url TEXT,
    
    -- Status
    status TEXT DEFAULT 'draft',  -- draft, submitted, returned, graded
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
);
```

#### 3. **submission_file** (ไฟล์ที่ส่ง)
```sql
CREATE TABLE submission_file (
    id TEXT PRIMARY KEY,
    submission_id TEXT NOT NULL,
    file_name TEXT NOT NULL,
    file_path TEXT NOT NULL,
    file_size INTEGER,
    file_type TEXT,
    uploaded_at DATETIME NOT NULL,
    
    FOREIGN KEY (submission_id) REFERENCES assignment_submission(id) ON DELETE CASCADE
);
```

#### 4. **lesson_announcement** (ประกาศ)
```sql
CREATE TABLE lesson_announcement (
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
);
```

#### 5. **announcement_comment** (ความคิดเห็น)
```sql
CREATE TABLE announcement_comment (
    id TEXT PRIMARY KEY,
    announcement_id TEXT NOT NULL,
    user_id TEXT NOT NULL,
    content TEXT NOT NULL,
    parent_comment_id TEXT,  -- For replies
    
    is_private BOOLEAN DEFAULT 0,
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL,
    
    FOREIGN KEY (announcement_id) REFERENCES lesson_announcement(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES user(id),
    FOREIGN KEY (parent_comment_id) REFERENCES announcement_comment(id) ON DELETE CASCADE
);
```

#### 6. **lesson_member** (สมาชิกในคลาส)
```sql
CREATE TABLE lesson_member (
    id TEXT PRIMARY KEY,
    lesson_id TEXT NOT NULL,
    user_id TEXT NOT NULL,
    role TEXT NOT NULL,  -- teacher, student, assistant
    
    -- Enrollment
    joined_at DATETIME NOT NULL,
    invitation_status TEXT DEFAULT 'accepted',  -- pending, accepted, declined
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
);
```

#### 7. **lesson_grade** (คะแนน)
```sql
CREATE TABLE lesson_grade (
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
);
```

#### 8. **lesson_material** (เอกสารประกอบ)
```sql
CREATE TABLE lesson_material (
    id TEXT PRIMARY KEY,
    lesson_id TEXT NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    
    -- Material type
    material_type TEXT NOT NULL,  -- pdf, video, link, document, presentation
    
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
);
```

#### 9. **lesson_quiz** (แบบทดสอบ)
```sql
CREATE TABLE lesson_quiz (
    id TEXT PRIMARY KEY,
    lesson_id TEXT NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    instructions TEXT,
    
    -- Settings
    total_points INTEGER DEFAULT 100,
    passing_score INTEGER DEFAULT 60,
    time_limit INTEGER,  -- minutes
    attempts_allowed INTEGER DEFAULT 1,
    
    -- Question settings
    shuffle_questions BOOLEAN DEFAULT 0,
    shuffle_answers BOOLEAN DEFAULT 0,
    show_correct_answers BOOLEAN DEFAULT 1,
    show_answers_after TEXT DEFAULT 'submission',  -- submission, grading, never
    
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
);
```

#### 10. **quiz_question** (คำถาม)
```sql
CREATE TABLE quiz_question (
    id TEXT PRIMARY KEY,
    quiz_id TEXT NOT NULL,
    question_text TEXT NOT NULL,
    question_type TEXT NOT NULL,  -- multiple_choice, true_false, short_answer, essay, fill_blank
    
    -- Points
    points INTEGER DEFAULT 1,
    
    -- Options (JSON for multiple choice)
    options TEXT,  -- JSON: [{"id": "a", "text": "...", "is_correct": true}]
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
);
```

#### 11. **quiz_attempt** (การทำแบบทดสอบ)
```sql
CREATE TABLE quiz_attempt (
    id TEXT PRIMARY KEY,
    quiz_id TEXT NOT NULL,
    student_id TEXT NOT NULL,
    lesson_id TEXT NOT NULL,
    
    -- Attempt info
    attempt_number INTEGER DEFAULT 1,
    status TEXT DEFAULT 'in_progress',  -- in_progress, completed, abandoned
    
    -- Timing
    started_at DATETIME NOT NULL,
    submitted_at DATETIME,
    time_spent INTEGER DEFAULT 0,  -- seconds
    
    -- Grading
    points_earned REAL DEFAULT 0,
    points_possible REAL DEFAULT 0,
    percentage REAL DEFAULT 0,
    is_passed BOOLEAN DEFAULT 0,
    
    -- Answers (JSON)
    answers TEXT,  -- JSON: {"question_id": "answer"}
    
    -- Grading
    graded_at DATETIME,
    auto_graded BOOLEAN DEFAULT 1,
    
    FOREIGN KEY (quiz_id) REFERENCES lesson_quiz(id) ON DELETE CASCADE,
    FOREIGN KEY (student_id) REFERENCES user(id),
    FOREIGN KEY (lesson_id) REFERENCES lesson(id) ON DELETE CASCADE
);
```

#### 12. **lesson_attendance** (เช็คชื่อ)
```sql
CREATE TABLE lesson_attendance (
    id TEXT PRIMARY KEY,
    lesson_id TEXT NOT NULL,
    student_id TEXT NOT NULL,
    date DATE NOT NULL,
    
    -- Status
    status TEXT DEFAULT 'present',  -- present, absent, late, excused
    
    -- Notes
    notes TEXT,
    recorded_by TEXT,
    recorded_at DATETIME NOT NULL,
    
    FOREIGN KEY (lesson_id) REFERENCES lesson(id) ON DELETE CASCADE,
    FOREIGN KEY (student_id) REFERENCES user(id),
    FOREIGN KEY (recorded_by) REFERENCES user(id),
    UNIQUE(lesson_id, student_id, date)
);
```

## 🎯 Features Breakdown

### 1. **Stream (ฟีด)**
- ✅ Announcements with comments
- ✅ Pinned posts
- ✅ File attachments
- ✅ @mentions
- ✅ Scheduled posts

### 2. **Classwork (งาน)**
- ✅ Assignments with due dates
- ✅ File submissions
- ✅ Grading rubrics
- ✅ Late submissions
- ✅ Multiple attempts
- ✅ Materials (PDFs, links, videos)
- ✅ Quizzes with auto-grading

### 3. **People (คน)**
- ✅ Teachers
- ✅ Students
- ✅ Assistants
- ✅ Invitation system
- ✅ Role permissions

### 4. **Grades (คะแนน)**
- ✅ Grade book
- ✅ Individual grades
- ✅ Class statistics
- ✅ Export grades
- ✅ Grade distribution

### 5. **Progress Tracking**
- ✅ Assignment completion
- ✅ Quiz scores
- ✅ Attendance
- ✅ Time spent
- ✅ Learning analytics

## 📱 UI Components Needed

### Class Detail Page Tabs:
1. **Stream** - News feed with announcements
2. **Classwork** - Assignments, materials, quizzes
3. **People** - Teachers and students
4. **Grades** - Grade book (students see their own)
5. **Analytics** - Progress tracking (teachers only)

## 🔄 Next Steps
1. ✅ Create migration script
2. Create domain entities (OOP)
3. Create repositories
4. Create services
5. Create controllers
6. Create UI templates
7. Testing & integration

