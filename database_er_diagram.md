# Database ER Diagram - Smart Learning Hub

## 📊 **Entity Relationship Diagram**

```mermaid
erDiagram
    USERS ||--o{ LESSONS : "has"
    USERS ||--o{ EXTERNAL_INTEGRATIONS : "has"
    USERS ||--o{ TAGS : "has"
    USERS ||--o{ EXTERNAL_DATA : "has"
    
    LESSONS ||--o{ LESSON_SECTIONS : "contains"
    LESSONS ||--o{ LESSON_TAGS : "has"
    
    LESSON_SECTIONS ||--o{ FILES : "contains"
    
    EXTERNAL_INTEGRATIONS ||--o{ EXTERNAL_DATA : "provides"
    
    TAGS ||--o{ LESSON_TAGS : "used_in"
    
    USERS {
        varchar(36) id PK
        varchar(80) username UK
        varchar(120) email UK
        varchar(128) password_hash
        timestamp created_at
        timestamp updated_at
    }
    
    LESSONS {
        varchar(36) id PK
        varchar(36) user_id FK
        varchar(200) title
        text description
        varchar(50) status
        text tags
        varchar(100) author_name
        integer color_theme
        boolean is_favorite
        varchar(50) source_platform
        varchar(100) external_id
        timestamp created_at
        timestamp updated_at
    }
    
    LESSON_SECTIONS {
        varchar(36) id PK
        varchar(36) lesson_id FK
        varchar(200) title
        text content
        varchar(50) section_type
        integer order_index
        varchar(50) status
        text tags
        timestamp due_date
        timestamp created_at
        timestamp updated_at
    }
    
    FILES {
        varchar(36) id PK
        varchar(36) section_id FK
        varchar(255) file_name
        varchar(500) file_path
        varchar(50) file_type
        integer file_size
        varchar(100) mime_type
        varchar(500) external_url
        timestamp created_at
    }
    
 Wigrations {
        varchar(36) id PK
        varchar(36) user_id FK
        varchar(50) platform
        text access_token
        text refresh_token
        timestamp token_expires_at
        varchar(100) platform_user_id
        boolean is_active
        timestamp created_at
        timestamp updated_at
    }
    
    EXTERNAL_DATA {
        varchar(36) id PK
        varchar(36) user_id FK
        varchar(36) integration_id FK
        varchar(100) external_id
        varchar(50) data_type
        varchar(200) title
        text description
        json raw_data
        timestamp last_synced_at
    }
    
    TAGS {
        varchar(36) id PK
        varchar(36) user_id FK
        varchar(100) name
        varchar(7) color
        timestamp created_at
    }
    
    LESSON_TAGS {
        varchar(36) lesson_id FK
        varchar(36) tag_id FK
    }
```

## 🔗 **ความสัมพันธ์ระหว่าง Entities**

### 1. **Users (ผู้ใช้)**
- **One-to-Many** กับ Lessons (ผู้ใช้ 1 คน มีบทเรียนได้หลายบท)
- **One-to-Many** กับ External Integrations (ผู้ใช้ 1 คน เชื่อมต่อ platform ได้หลายตัว)
- **One-to-Many** กับ Tags (ผู้ใช้ 1 คน สร้างแท็กได้หลายแท็ก)
- **One-to-Many** กับ External Data (ผู้ใช้ 1 คน มีข้อมูลจากภายนอกได้หลายชุด)

### 2. **Lessons (บทเรียน)**
- **Many-to-One** กับ Users (บทเรียนหลายบท อยู่ในผู้ใช้ 1 คน)
- **One-to-Many** กับ Lesson Sections (บทเรียน 1 บท มีส่วนได้หลายส่วน)
- **Many-to-Many** กับ Tags ผ่าน Lesson Tags (บทเรียน 1 บท มีแท็กได้หลายแท็ก)

### 3. **Lesson Sections (ส่วนของบทเรียน)**
- **Many-to-One** กับ Lessons (ส่วนหลายส่วน อยู่ในบทเรียน 1 บท)
- **One-to-Many** กับ Files (ส่วน 1 ส่วน มีไฟล์ได้หลายไฟล์)

### 4. **Files (ไฟล์)**
- **Many-to-One** กับ Lesson Sections (ไฟล์หลายไฟล์ อยู่ในส่วน 1 ส่วน)

### 5. **External Integrations (การเชื่อมต่อภายนอก)**
- **Many-to-One** กับ Users (การเชื่อมต่อหลายตัว อยู่ในผู้ใช้ 1 คน)
- **One-to-Many** กับ External Data (การเชื่อมต่อ 1 ตัว ให้ข้อมูลได้หลายชุด)

### 6. **External Data (ข้อมูลจากภายนอก)**
- **Many-to-One** กับ Users (ข้อมูลหลายชุด อยู่ในผู้ใช้ 1 คน)
- **Many-to-One** กับ External Integrations (ข้อมูลหลายชุด มาจากการเชื่อมต่อ 1 ตัว)

### 7. **Tags (แท็ก)**
- **Many-to-One** กับ Users (แท็กหลายแท็ก อยู่ในผู้ใช้ 1 คน)
- **Many-to-Many** กับ Lessons ผ่าน Lesson Tags (แท็ก 1 แท็ก ใช้ในบทเรียนได้หลายบท)

## 📈 **ข้อดีของการออกแบบนี้**

### 1. **Normalization ที่ดี**
- แยกข้อมูลเป็น tables ที่เหมาะสม
- ลด data redundancy
- ง่ายต่อการ query และ update

### 2. **Scalability**
- รองรับข้อมูลจำนวนมาก
- Indexes ที่เหมาะสม
- Query performance ที่ดี

### 3. **Flexibility**
- รองรับหลาย platform
- ง่ายต่อการเพิ่ม features ใหม่
- JSON field สำหรับข้อมูลที่ซับซ้อน

### 4. **Maintainability**
- โครงสร้างที่เข้าใจง่าย
- Consistent naming convention
- Clear relationships ระหว่าง tables

## 🔧 **ตัวอย่าง Queries ที่ใช้บ่อย**

### 1. **ดึงบทเรียนทั้งหมดของผู้ใช้**
```sql
SELECT * FROM lessons WHERE user_id = ? ORDER BY created_at DESC;
```

### 2. **ดึงบทเรียนพร้อมแท็ก**
```sql
SELECT l.*, GROUP_CONCAT(t.name) as tag_names
FROM lessons l
LEFT JOIN lesson_tags lt ON l.id = lt.lesson_id
LEFT JOIN tags t ON lt.tag_id = t.id
WHERE l.user_id = ?
GROUP BY l.id;
```

### 3. **ดึงบทเรียนจาก Google Classroom**
```sql
SELECT * FROM lessons 
WHERE user_id = ? AND source_platform = 'google_classroom';
```

### 4. **ดึงไฟล์ทั้งหมดของบทเรียน**
```sql
SELECT f.* FROM files f
JOIN lesson_sections ls ON f.section_id = ls.id
WHERE ls.lesson_id = ?;
```

### 5. **ดึงข้อมูลจากภายนอก**
```sql
SELECT * FROM external_data 
WHERE user_id = ? AND data_type = 'course';
``` 