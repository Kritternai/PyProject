# Database Design - Smart Learning Hub

## 🎯 **หลักการออกแบบ**
1. **Normalization**: แยกข้อมูลให้เป็น tables ที่เหมาะสม
2. **Consistency**: ใช้ data type เดียวกันสำหรับ field เดียวกัน
3. **Scalability**: ออกแบบให้รองรับข้อมูลจำนวนมาก
4. **Maintainability**: เข้าใจง่าย ดูแลรักษาง่าย

## 📊 **Database Schema ใหม่**

### 1. **Users Table** (ผู้ใช้)
```sql
CREATE TABLE users (
    id VARCHAR(36) PRIMARY KEY,
    username VARCHAR(80) UNIQUE NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(128) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 2. **Lessons Table** (บทเรียน)
```sql
CREATE TABLE lessons (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    status VARCHAR(50) DEFAULT 'Not Started',
    tags TEXT, -- JSON array of tags
    author_name VARCHAR(100),
    color_theme INTEGER DEFAULT 1,
    is_favorite BOOLEAN DEFAULT FALSE,
    source_platform VARCHAR(50) DEFAULT 'manual',
    external_id VARCHAR(100), -- Google Classroom ID, MS Teams ID, etc.
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
    section_type VARCHAR(50) NOT NULL, -- 'text', 'file', 'assignment', 'note', 'material'
    order_index INTEGER DEFAULT 0,
    status VARCHAR(50) DEFAULT 'pending',
    tags TEXT, -- JSON array of tags
    due_date TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (lesson_id) REFERENCES lessons (id)
);
```

### 4. **Files Table** (ไฟล์แนบ)
```sql
CREATE TABLE files (
    id VARCHAR(36) PRIMARY KEY,
    section_id VARCHAR(36) NOT NULL,
    file_name VARCHAR(255) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    file_type VARCHAR(50), -- 'image', 'document', 'video', etc.
    file_size INTEGER,
    mime_type VARCHAR(100),
    external_url VARCHAR(500), -- For Google Drive, OneDrive links
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (section_id) REFERENCES lesson_sections (id)
);
```

### 5. **External Integrations Table** (การเชื่อมต่อภายนอก)
```sql
CREATE TABLE external_integrations (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    platform VARCHAR(50) NOT NULL, -- 'google_classroom', 'ms_teams', 'canvas'
    access_token TEXT,
    refresh_token TEXT,
    token_expires_at TIMESTAMP,
    platform_user_id VARCHAR(100),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id),
    UNIQUE (user_id, platform)
);
```

### 6. **External Data Table** (ข้อมูลจากภายนอก)
```sql
CREATE TABLE external_data (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    integration_id VARCHAR(36) NOT NULL,
    external_id VARCHAR(100) NOT NULL, -- Original ID from external platform
    data_type VARCHAR(50) NOT NULL, -- 'course', 'assignment', 'announcement', 'material'
    title VARCHAR(200),
    description TEXT,
    raw_data JSON, -- Complete data from external platform
    last_synced_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id),
    FOREIGN KEY (integration_id) REFERENCES external_integrations (id),
    UNIQUE (user_id, external_id, data_type)
);
```

### 7. **Tags Table** (แท็ก)
```sql
CREATE TABLE tags (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    name VARCHAR(100) NOT NULL,
    color VARCHAR(7) DEFAULT '#007bff', -- Hex color
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id),
    UNIQUE (user_id, name)
);
```

### 8. **Lesson Tags Table** (ความสัมพันธ์บทเรียน-แท็ก)
```sql
CREATE TABLE lesson_tags (
    lesson_id VARCHAR(36) NOT NULL,
    tag_id VARCHAR(36) NOT NULL,
    PRIMARY KEY (lesson_id, tag_id),
    FOREIGN KEY (lesson_id) REFERENCES lessons (id),
    FOREIGN KEY (tag_id) REFERENCES tags (id)
);
```

## 🔧 **Indexes สำหรับ Performance**
```sql
-- Users
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_username ON users(username);

-- Lessons
CREATE INDEX idx_lessons_user_id ON lessons(user_id);
CREATE INDEX idx_lessons_external_id ON lessons(external_id);
CREATE INDEX idx_lessons_source_platform ON lessons(source_platform);
CREATE INDEX idx_lessons_status ON lessons(status);
CREATE INDEX idx_lessons_created_at ON lessons(created_at);

-- Lesson Sections
CREATE INDEX idx_lesson_sections_lesson_id ON lesson_sections(lesson_id);
CREATE INDEX idx_lesson_sections_type ON lesson_sections(section_type);
CREATE INDEX idx_lesson_sections_order ON lesson_sections(lesson_id, order_index);

-- Files
CREATE INDEX idx_files_section_id ON files(section_id);
CREATE INDEX idx_files_type ON files(file_type);

-- External Integrations
CREATE INDEX idx_external_integrations_user_id ON external_integrations(user_id);
CREATE INDEX idx_external_integrations_platform ON external_integrations(platform);

-- External Data
CREATE INDEX idx_external_data_user_id ON external_data(user_id);
CREATE INDEX idx_external_data_integration_id ON external_data(integration_id);
CREATE INDEX idx_external_data_external_id ON external_data(external_id);
CREATE INDEX idx_external_data_type ON external_data(data_type);
```

## 📈 **ข้อดีของการออกแบบใหม่**

### 1. **Normalization ที่ดีขึ้น**
- แยกข้อมูลเป็น tables ที่เหมาะสม
- ลด data redundancy
- ง่ายต่อการ query และ update

### 2. **Scalability**
- รองรับข้อมูลจำนวนมาก
- Indexes ที่เหมาะสม
- Query performance ที่ดี

### 3. **Flexibility**
- รองรับหลาย platform (Google Classroom, MS Teams, Canvas)
- ง่ายต่อการเพิ่ม features ใหม่
- JSON field สำหรับข้อมูลที่ซับซ้อน

### 4. **Maintainability**
- โครงสร้างที่เข้าใจง่าย
- Consistent naming convention
- Clear relationships ระหว่าง tables

## 🔄 **Migration Plan**

### Phase 1: Create New Tables
1. สร้าง tables ใหม่ตาม schema
2. Migrate existing data
3. Test functionality

### Phase 2: Update Application Code
1. Update models
2. Update queries
3. Update API endpoints

### Phase 3: Cleanup
1. Remove old tables
2. Optimize indexes
3. Update documentation 