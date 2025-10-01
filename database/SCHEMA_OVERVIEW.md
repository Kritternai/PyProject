# Database Schema Overview - Smart Learning Hub

## 🎯 **ภาพรวมระบบฐานข้อมูล**

ระบบฐานข้อมูล Smart Learning Hub ออกแบบมาเพื่อรองรับการจัดการการเรียนรู้แบบครบวงจร ประกอบด้วยตารางหลัก 16 ตารางที่เชื่อมโยงกันอย่างเป็นระบบ

## 📊 **โครงสร้างตารางหลัก**

### **1. Users Table** (ผู้ใช้)
- **วัตถุประสงค์**: จัดการข้อมูลผู้ใช้และสิทธิ์การเข้าถึง
- **Fields หลัก**: username, email, password_hash, role, profile_image
- **Relationships**: One-to-Many กับ Lessons, Notes, Tasks, Files
- **Indexes**: email, username, role, is_active

### **2. Lessons Table** (บทเรียน)
- **วัตถุประสงค์**: จัดการบทเรียนและเนื้อหาการเรียนรู้
- **Fields หลัก**: title, description, status, difficulty_level, source_platform
- **Relationships**: Many-to-One กับ Users, One-to-Many กับ LessonSections
- **Indexes**: user_id, status, source_platform, external_id

### **3. Lesson Sections Table** (ส่วนของบทเรียน)
- **วัตถุประสงค์**: จัดระเบียบเนื้อหาภายในบทเรียน
- **Fields หลัก**: title, content, section_type, order_index, status
- **Relationships**: Many-to-One กับ Lessons, One-to-Many กับ Files
- **Indexes**: lesson_id, order_index, section_type, status

### **4. Notes Table** (บันทึก)
- **วัตถุประสงค์**: จัดการบันทึกและโน๊ตของผู้ใช้
- **Fields หลัก**: title, content, note_type, tags, status
- **Relationships**: Many-to-One กับ Users, Lessons, LessonSections
- **Indexes**: user_id, note_type, status, lesson_id

### **5. Tasks Table** (งาน)
- **วัตถุประสงค์**: จัดการงานและภารกิจที่ต้องทำ
- **Fields หลัก**: title, description, status, priority, due_date
- **Relationships**: Many-to-One กับ Users, Lessons, LessonSections
- **Indexes**: user_id, status, priority, due_date

### **6. Files Table** (ไฟล์)
- **วัตถุประสงค์**: จัดการไฟล์แนบและสื่อต่างๆ
- **Fields หลัก**: file_name, file_path, file_type, file_size, mime_type
- **Relationships**: Many-to-One กับ Users, Lessons, Notes, Tasks
- **Indexes**: user_id, file_type, lesson_id, category

### **7. Tags Table** (แท็ก)
- **วัตถุประสงค์**: จัดการแท็กสำหรับการจัดหมวดหมู่
- **Fields หลัก**: name, color, tag_type, category
- **Relationships**: Many-to-One กับ Users, Many-to-Many กับ Lessons
- **Indexes**: user_id, name, tag_type, category

### **8. External Integrations Table** (การเชื่อมต่อภายนอก)
- **วัตถุประสงค์**: จัดการการเชื่อมต่อกับแพลตฟอร์มภายนอก
- **Fields หลัก**: platform, access_token, refresh_token, is_active
- **Relationships**: Many-to-One กับ Users, One-to-Many กับ ExternalData
- **Indexes**: user_id, platform, is_active

### **9. External Data Table** (ข้อมูลจากภายนอก)
- **วัตถุประสงค์**: เก็บข้อมูลที่ดึงมาจากแพลตฟอร์มภายนอก
- **Fields หลัก**: data_type, title, description, raw_data
- **Relationships**: Many-to-One กับ Users, ExternalIntegrations
- **Indexes**: user_id, data_type, external_id

### **10. Progress Tracking Table** (ติดตามความก้าวหน้า)
- **วัตถุประสงค์**: ติดตามความก้าวหน้าในการเรียนรู้
- **Fields หลัก**: progress_type, value, max_value, percentage
- **Relationships**: Many-to-One กับ Users, Lessons, LessonSections
- **Indexes**: user_id, lesson_id, progress_type

### **11. Pomodoro Sessions Table** (เซสชัน Pomodoro)
- **วัตถุประสงค์**: จัดการเซสชันการเรียนแบบ Pomodoro
- **Fields หลัก**: session_type, duration, start_time, end_time
- **Relationships**: Many-to-One กับ Users, Lessons, LessonSections
- **Indexes**: user_id, session_type, start_time

### **12. Reminders Table** (การแจ้งเตือน)
- **วัตถุประสงค์**: จัดการการแจ้งเตือนและนัดหมาย
- **Fields หลัก**: title, due_date, reminder_type, priority
- **Relationships**: Many-to-One กับ Users, Lessons, Tasks
- **Indexes**: user_id, due_date, priority, is_completed

### **13. Reports Table** (รายงาน)
- **วัตถุประสงค์**: สร้างและจัดการรายงานต่างๆ
- **Fields หลัก**: title, report_type, parameters, report_data
- **Relationships**: Many-to-One กับ Users
- **Indexes**: user_id, report_type, generation_status

### **14. Activity Logs Table** (บันทึกกิจกรรม)
- **วัตถุประสงค์**: บันทึกกิจกรรมและเหตุการณ์ต่างๆ
- **Fields หลัก**: action, activity_type, severity, entity_type
- **Relationships**: Many-to-One กับ Users
- **Indexes**: user_id, action, activity_type, severity

## 🔗 **ความสัมพันธ์ระหว่างตาราง**

### **One-to-Many Relationships**
- **Users** → **Lessons, Notes, Tasks, Files, Tags**
- **Lessons** → **LessonSections, Notes, Tasks, Files**
- **LessonSections** → **Files, Notes, Tasks**

### **Many-to-Many Relationships**
- **Lessons** ↔ **Tags** (ผ่าน LessonTags)
- **Notes** ↔ **Tags** (ผ่าน TagRelationships)
- **Tasks** ↔ **Tags** (ผ่าน TagRelationships)

### **Junction Tables**
- **LessonTags**: เชื่อม Lessons กับ Tags
- **TagRelationships**: เชื่อม Tags กับ Notes, Tasks

## 📈 **Performance Features**

### **Indexes**
- **Primary Keys**: ทุกตารางใช้ UUID เป็น Primary Key
- **Foreign Keys**: Indexes บน Foreign Keys ทั้งหมด
- **Composite Indexes**: สำหรับ queries ที่ใช้บ่อย
- **Status Indexes**: สำหรับ filtering ตามสถานะ

### **Optimization**
- **SQLite WAL Mode**: สำหรับ performance ที่ดีขึ้น
- **Connection Pooling**: จัดการ database connections
- **Eager Loading**: ลด N+1 query problems

## 🔧 **การใช้งาน**

### **การเริ่มต้นฐานข้อมูล**
```python
from database import init_database

# สร้างตารางทั้งหมด
success = init_database()
```

### **การใช้งาน Database Manager**
```python
from database import get_db_manager

manager = get_db_manager()

# ตรวจสอบสถานะฐานข้อมูล
info = manager.get_database_info()

# สร้าง backup
backup_path = manager.backup_database()
```

### **การใช้งาน Models**
```python
from database.models import User, Lesson

# สร้าง user ใหม่
user = User(username="john_doe", email="john@example.com")
user.set_password("password123")

# สร้าง lesson ใหม่
lesson = Lesson(
    title="Introduction to Python",
    description="Learn Python basics",
    user_id=user.id
)
```

## 🚀 **ข้อดีของการออกแบบ**

### **1. Scalability**
- รองรับผู้ใช้จำนวนมาก
- Indexes ที่เหมาะสมสำหรับ queries
- Connection pooling สำหรับ performance

### **2. Maintainability**
- โครงสร้างที่เข้าใจง่าย
- Relationships ที่ชัดเจน
- Documentation ที่ครบถ้วน

### **3. Flexibility**
- รองรับการขยายในอนาคต
- JSON fields สำหรับข้อมูลที่ซับซ้อน
- External integrations ที่ยืดหยุ่น

### **4. Security**
- Password hashing
- Role-based access control
- Activity logging

## 📚 **การพัฒนาต่อ**

### **Phase 1: Basic Setup** ✅
- [x] สร้าง Models ทั้งหมด
- [x] สร้าง Database Manager
- [x] สร้าง Configuration

### **Phase 2: Advanced Features**
- [ ] Database migrations
- [ ] Data seeding
- [ ] Backup automation
- [ ] Performance monitoring

### **Phase 3: Production Ready**
- [ ] PostgreSQL support
- [ ] Connection pooling
- [ ] Query optimization
- [ ] Monitoring and alerting

## 🎯 **สรุป**

ฐานข้อมูล Smart Learning Hub ออกแบบมาเพื่อ:
- **รองรับการใช้งานจริง** - ครบถ้วนตาม SRS
- **Performance ที่ดี** - Indexes และ optimization
- **การขยายตัว** - รองรับ features ใหม่
- **การดูแลรักษา** - โครงสร้างที่เข้าใจง่าย

ระบบพร้อมสำหรับการใช้งานและพัฒนาต่อในอนาคต!
