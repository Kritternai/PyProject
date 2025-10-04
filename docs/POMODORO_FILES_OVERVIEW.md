# 🍅 Pomodoro System - ไฟล์ทั้งหมดที่เกี่ยวข้อง

## 📁 **1. Domain Layer (Business Logic)**

### **`app/domain/entities/pomodoro_session.py`**
- **หน้าที่**: กำหนดโครงสร้างข้อมูล PomodoroSession
- **เนื้อหา**: Class ที่มี properties ต่างๆ เช่น id, user_id, session_type, duration, start_time, end_time, etc.
- **ใช้ทำ**: เป็น blueprint สำหรับข้อมูล session ในระบบ

### **`app/domain/interfaces/pomodoro_repository.py`**
- **หน้าที่**: กำหนด interface สำหรับ database operations
- **เนื้อหา**: Abstract methods เช่น create_session, get_session_by_id, update_session, delete_session
- **ใช้ทำ**: กำหนด contract ที่ repository implementation ต้องทำตาม

## 📁 **2. Application Layer (Business Logic)**

### **`app/application/services/pomodoro_service.py`**
- **หน้าที่**: ควบคุม business logic ของ Pomodoro
- **เนื้อหา**: Methods เช่น start_session, pause_session, resume_session, complete_session
- **ใช้ทำ**: จัดการ workflow ของ Pomodoro session

## 📁 **3. Infrastructure Layer (Database & External)**

### **`app/infrastructure/database/pomodoro_repository.py`**
- **หน้าที่**: ทำงานกับ database โดยตรง
- **เนื้อหา**: SQL queries, database operations
- **ใช้ทำ**: บันทึก/ดึงข้อมูลจาก database

### **`app/infrastructure/di/pomodoro_container.py`**
- **หน้าที่**: จัดการ dependency injection
- **เนื้อหา**: กำหนด dependencies ระหว่าง components
- **ใช้ทำ**: เชื่อมต่อ components เข้าด้วยกัน

## 📁 **4. Presentation Layer (HTTP & UI)**

### **`app/presentation/controllers/pomodoro_controller.py`**
- **หน้าที่**: รับ HTTP requests และส่ง response
- **เนื้อหา**: Methods ที่รับ request, เรียก service, ส่ง JSON response
- **ใช้ทำ**: เป็น bridge ระหว่าง HTTP และ business logic

### **`app/presentation/routes/pomodoro_routes_new.py`**
- **หน้าที่**: กำหนด URL routes และ HTTP methods
- **เนื้อหา**: Flask routes เช่น @pomodoro_bp_new.route('/start', methods=['POST'])
- **ใช้ทำ**: จัดการ routing และ authentication

## 📁 **5. Frontend Integration**

### **`app/static/js/pomodoro_oop.js`**
- **หน้าที่**: JavaScript class สำหรับเรียก API
- **เนื้อหา**: PomodoroOOP class, API calls, UI management
- **ใช้ทำ**: เชื่อมต่อ frontend กับ backend API

### **`app/templates/pomodoro_fragment.html`**
- **หน้าที่**: UI template สำหรับ Pomodoro
- **เนื้อหา**: HTML structure, CSS styling, JavaScript functions
- **ใช้ทำ**: แสดงหน้า Pomodoro timer

## 📁 **6. Application Integration**

### **`app/__init__.py`**
- **หน้าที่**: Flask application factory
- **เนื้อหา**: Blueprint registration, app configuration
- **ใช้ทำ**: เชื่อมต่อ Pomodoro routes เข้ากับ Flask app

### **`app/templates/base.html`**
- **หน้าที่**: Base template สำหรับทุกหน้า
- **เนื้อหา**: HTML structure, CSS/JS includes
- **ใช้ทำ**: รวม PomodoroOOP JavaScript เข้ากับทุกหน้า

## 📁 **7. Database Migration**

### **`database/migrations/create_complete_database.py`**
- **หน้าที่**: สร้าง database tables ทั้งหมด
- **เนื้อหา**: รวม pomodoro tables เข้ากับระบบหลัก
- **ใช้ทำ**: Database migration หลัก

## 📁 **8. Routes Integration**

### **`app/routes_new.py`**
- **หน้าที่**: กำหนด route สำหรับ Pomodoro page
- **เนื้อหา**: `@main_bp.route('/partial/pomodoro')` 
- **ใช้ทำ**: จัดการการแสดงหน้า Pomodoro

## 🔄 **การทำงานของระบบ:**

### **1. User Action Flow:**
```
User clicks "Start" → pomodoro_fragment.html → pomodoro_oop.js → API call → pomodoro_routes_new.py → pomodoro_controller.py → pomodoro_service.py → pomodoro_repository.py → Database
```

### **2. Data Flow:**
```
Database → pomodoro_repository.py → pomodoro_service.py → pomodoro_controller.py → JSON response → pomodoro_oop.js → UI update
```

### **3. File Dependencies:**
```
pomodoro_fragment.html → pomodoro_oop.js → API endpoints
pomodoro_routes_new.py → pomodoro_controller.py → pomodoro_service.py → pomodoro_repository.py
app/__init__.py → pomodoro_routes_new.py (Blueprint registration)
```

## 📊 **API Endpoints ที่พร้อมใช้:**

```bash
# Health Check
GET /api/pomodoro/health

# Session Management
POST /api/pomodoro/start
POST /api/pomodoro/{id}/pause
POST /api/pomodoro/{id}/resume
POST /api/pomodoro/{id}/complete
POST /api/pomodoro/{id}/cancel

# Session Queries
GET /api/pomodoro/active
GET /api/pomodoro/sessions
GET /api/pomodoro/lessons/{id}/sessions

# Statistics & Analytics
GET /api/pomodoro/statistics?period=week
GET /api/pomodoro/insights?days=30
```

## 🎯 **สรุป:**

**ระบบ Pomodoro OOP ทำงานแบบ Clean Architecture:**
- **Domain**: กำหนด business rules
- **Application**: จัดการ business logic
- **Infrastructure**: ทำงานกับ database
- **Presentation**: รับ HTTP requests และแสดง UI

**ทุกไฟล์ทำงานร่วมกันเพื่อสร้างระบบ Pomodoro ที่สมบูรณ์!** 🚀🍅
