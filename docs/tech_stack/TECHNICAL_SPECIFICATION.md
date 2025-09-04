# Technical Specification: Smart Learning Hub

**ฉบับเอกสาร:** 1.0  
**วันที่:** 17 กรกฎาคม 2568  
**ผู้พัฒนา:** Smart Learning Hub Team

---

## 1. สถาปัตยกรรมระบบ (System Architecture)

### 1.1 โครงสร้างโดยรวม
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend       │    │   External      │
│                 │    │                 │    │   Services      │
│ • HTML/Jinja2   │◄──►│ • Flask         │◄──►│ • Google API    │
│ • Tailwind CSS  │    │ • SQLAlchemy    │    │ • Chrome Ext.   │
│ • JavaScript    │    │ • SQLite        │    │ • MS Teams      │
│ • FontAwesome   │    │ • OAuth         │    │ • KMITL         │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### 1.2 แนวทางการออกแบบ
- **Modular Architecture:** แยกโมดูลตามหน้าที่ (User, Lesson, Note, Task)
- **Object-Oriented Design:** ใช้ OOP principles สำหรับ data models
- **RESTful API:** API endpoints สำหรับการเชื่อมต่อภายนอก
- **Separation of Concerns:** แยก business logic, data access, presentation

---

## 2. ฐานข้อมูล (Database Design)

### 2.1 Entity Relationship Diagram
```
User (1) ─── (N) Lesson
User (1) ─── (N) Note  
User (1) ─── (N) Task
User (1) ─── (N) Progress
Lesson (1) ─── (N) Note
Lesson (1) ─── (N) Task
```

### 2.2 ตารางหลัก (Core Tables)

#### Users Table
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(80) UNIQUE NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    google_id VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### Lessons Table
```sql
CREATE TABLE lessons (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    category VARCHAR(100),
    status VARCHAR(50) DEFAULT 'active',
    google_classroom_id VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id)
);
```

#### Notes Table
```sql
CREATE TABLE notes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    lesson_id INTEGER,
    title VARCHAR(255) NOT NULL,
    content TEXT,
    tags TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id),
    FOREIGN KEY (lesson_id) REFERENCES lessons (id)
);
```

#### Tasks Table
```sql
CREATE TABLE tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    lesson_id INTEGER,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    status VARCHAR(50) DEFAULT 'pending',
    priority VARCHAR(20) DEFAULT 'medium',
    due_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id),
    FOREIGN KEY (lesson_id) REFERENCES lessons (id)
);
```

---

## 3. API Endpoints

### 3.1 Authentication Endpoints
```
POST /auth/register     - สมัครสมาชิกใหม่
POST /auth/login        - เข้าสู่ระบบ
POST /auth/logout       - ออกจากระบบ
GET  /auth/google       - Google OAuth
GET  /auth/callback     - OAuth Callback
```

### 3.2 Lesson Management
```
GET    /lessons/                    - รายการบทเรียน
POST   /lessons/                    - สร้างบทเรียนใหม่
GET    /lessons/<id>                - ดูรายละเอียดบทเรียน
PUT    /lessons/<id>                - แก้ไขบทเรียน
DELETE /lessons/<id>                - ลบบทเรียน
GET    /lessons/<id>/notes          - ดูบันทึกในบทเรียน
GET    /lessons/<id>/tasks          - ดูงานในบทเรียน
```

### 3.3 Note Management
```
GET    /notes/                      - รายการบันทึก
POST   /notes/                      - สร้างบันทึกใหม่
GET    /notes/<id>                  - ดูรายละเอียดบันทึก
PUT    /notes/<id>                  - แก้ไขบันทึก
DELETE /notes/<id>                  - ลบบันทึก
GET    /notes/search?q=<query>      - ค้นหาบันทึก
```

### 3.4 Task Management
```
GET    /tasks/                      - รายการงาน
POST   /tasks/                      - สร้างงานใหม่
GET    /tasks/<id>                  - ดูรายละเอียดงาน
PUT    /tasks/<id>                  - แก้ไขงาน
DELETE /tasks/<id>                  - ลบงาน
PUT    /tasks/<id>/status           - อัปเดตสถานะงาน
```

### 3.5 Google Classroom Integration
```
GET    /google/classrooms           - รายการ Google Classroom
POST   /google/classrooms/sync      - ซิงค์ข้อมูลจาก Google Classroom
GET    /google/classrooms/<id>      - ดูรายละเอียดห้องเรียน
GET    /google/classrooms/<id>/assignments - ดูงานในห้องเรียน
```

---

## 4. การเชื่อมต่อภายนอก (External Integrations)

### 4.1 Google Classroom API
```python
# Google Classroom Integration
class GoogleClassroomManager:
    def __init__(self, credentials_file):
        self.service = build('classroom', 'v1', credentials=credentials)
    
    def list_courses(self):
        """ดึงรายการห้องเรียนจาก Google Classroom"""
        
    def sync_course(self, course_id):
        """ซิงค์ข้อมูลห้องเรียนเข้าระบบ"""
        
    def get_assignments(self, course_id):
        """ดึงรายการงานจากห้องเรียน"""
```

### 4.2 Chrome Extension Integration
```javascript
// Content Script for MS Teams/KMITL
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === 'extractData') {
        const data = extractPageData();
        sendToFlaskBackend(data);
    }
});

function extractPageData() {
    // ดึงข้อมูลจากหน้าเว็บ MS Teams/KMITL
    return {
        title: document.title,
        content: document.body.innerText,
        timestamp: new Date().toISOString()
    };
}
```

### 4.3 OAuth 2.0 Implementation
```python
# Google OAuth Configuration
GOOGLE_CLIENT_ID = 'your-client-id'
GOOGLE_CLIENT_SECRET = 'your-client-secret'
GOOGLE_REDIRECT_URI = 'http://localhost:5000/auth/callback'

@app.route('/auth/google')
def google_login():
    """เริ่มต้น Google OAuth flow"""
    
@app.route('/auth/callback')
def google_callback():
    """จัดการ OAuth callback และสร้าง session"""
```

---

## 5. มาตรฐานการพัฒนา (Development Standards)

### 5.1 โครงสร้างโปรเจกต์
```
PyProject-5/
├── app/                    # Flask Application
│   ├── __init__.py        # App Factory
│   ├── routes.py          # Route Definitions
│   ├── core/              # Business Logic
│   │   ├── user.py        # User Model
│   │   ├── lesson.py      # Lesson Model
│   │   ├── note.py        # Note Model
│   │   └── task.py        # Task Model
│   ├── static/            # Static Files
│   │   ├── css/           # Stylesheets
│   │   ├── js/            # JavaScript
│   │   └── uploads/       # File Uploads
│   └── templates/         # Jinja2 Templates
├── chrome_extension/      # Chrome Extension
├── docs/                  # Documentation
├── tests/                 # Test Files
├── requirements.txt       # Python Dependencies
├── package.json          # Node.js Dependencies
└── run.py               # Application Entry Point
```

### 5.2 Coding Standards
- **Python:** PEP 8, Type Hints, Docstrings
- **JavaScript:** ESLint, Prettier
- **CSS:** Tailwind CSS, BEM Methodology
- **Git:** Conventional Commits, Feature Branches

### 5.3 Testing Strategy
```python
# Unit Tests Example
def test_user_registration():
    """ทดสอบการสมัครสมาชิก"""
    response = client.post('/auth/register', data={
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'password123'
    })
    assert response.status_code == 200
    assert User.query.filter_by(username='testuser').first() is not None

# Integration Tests Example
def test_google_classroom_sync():
    """ทดสอบการซิงค์ข้อมูลจาก Google Classroom"""
    # Mock Google API response
    # Test data synchronization
    # Verify database updates
```

---

## 6. การจัดการความปลอดภัย (Security)

### 6.1 Authentication & Authorization
- **Password Hashing:** bcrypt สำหรับเข้ารหัสรหัสผ่าน
- **Session Management:** Flask-Session สำหรับจัดการ session
- **OAuth 2.0:** Google OAuth สำหรับ SSO
- **CSRF Protection:** Flask-WTF CSRF tokens

### 6.2 Data Protection
- **Input Validation:** Flask-WTF form validation
- **SQL Injection Prevention:** SQLAlchemy ORM
- **XSS Prevention:** Jinja2 auto-escaping
- **File Upload Security:** File type validation, size limits

### 6.3 API Security
- **Rate Limiting:** Flask-Limiter
- **CORS Configuration:** Flask-CORS
- **API Key Management:** สำหรับ external integrations

---

## 7. การปรับปรุงประสิทธิภาพ (Performance Optimization)

### 7.1 Database Optimization
- **Indexing:** สร้าง index สำหรับ fields ที่ใช้ค้นหาบ่อย
- **Query Optimization:** ใช้ eager loading สำหรับ relationships
- **Connection Pooling:** SQLAlchemy connection pooling

### 7.2 Caching Strategy
- **Redis Cache:** สำหรับ session และ temporary data
- **Static File Caching:** Browser caching สำหรับ CSS/JS
- **API Response Caching:** สำหรับข้อมูลที่ไม่เปลี่ยนแปลงบ่อย

### 7.3 Frontend Optimization
- **CSS/JS Minification:** ใช้ PostCSS และ Webpack
- **Image Optimization:** WebP format, lazy loading
- **CDN Integration:** สำหรับ static assets

---

## 8. การติดตั้งและ Deployment

### 8.1 Development Environment
```bash
# สร้าง Virtual Environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# หรือ venv\Scripts\activate  # Windows

# ติดตั้ง Dependencies
pip install -r requirements.txt
npm install

# รัน Development Server
python run.py
```

### 8.2 Production Deployment
- **Web Server:** Gunicorn + Nginx
- **Database:** PostgreSQL (สำหรับ production)
- **Environment Variables:** .env file สำหรับ configuration
- **SSL Certificate:** Let's Encrypt
- **Monitoring:** Sentry สำหรับ error tracking

---

## 9. การบำรุงรักษาและ Monitoring

### 9.1 Logging
```python
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
```

### 9.2 Error Handling
- **Global Exception Handler:** จัดการ error ทั่วทั้งแอป
- **Custom Error Pages:** 404, 500 error pages
- **Error Reporting:** ส่ง error reports ไปยัง monitoring service

### 9.3 Health Checks
- **Database Connectivity:** ตรวจสอบการเชื่อมต่อฐานข้อมูล
- **External API Status:** ตรวจสอบ Google API availability
- **System Resources:** ตรวจสอบ CPU, Memory usage

---

## 10. แผนการขยายในอนาคต (Future Expansion)

### 10.1 Microservices Architecture
- แยกโมดูลเป็น microservices แยกกัน
- ใช้ message queue (Redis/RabbitMQ) สำหรับการสื่อสาร
- Container orchestration ด้วย Docker + Kubernetes

### 10.2 Advanced Features
- **AI/ML Integration:** แนะนำบทเรียนตามพฤติกรรมผู้ใช้
- **Real-time Collaboration:** WebSocket สำหรับ real-time features
- **Mobile App:** React Native หรือ Flutter mobile app
- **Advanced Analytics:** Dashboard สำหรับวิเคราะห์พฤติกรรมผู้ใช้

### 10.3 Scalability Improvements
- **Load Balancing:** Nginx load balancer
- **Database Sharding:** แบ่งฐานข้อมูลตาม user groups
- **CDN Integration:** CloudFlare หรือ AWS CloudFront
- **Auto-scaling:** Kubernetes HPA หรือ AWS Auto Scaling

---

**หมายเหตุ:** เอกสารนี้จะได้รับการอัปเดตตามการพัฒนาของโปรเจกต์และความต้องการใหม่ที่เกิดขึ้น 