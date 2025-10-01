# **Tech Stack: Smart Learning Hub**

**เอกสารเทคโนโลยีที่ใช้**  
**ฉบับที่:** 1.0  
**วันที่:** 17 กรกฎาคม 2568  
**จัดทำโดย:** ทีมพัฒนา Smart Learning Hub  
**รหัสเอกสาร:** SLH-TECH-2025-001-TH

---

## **บทสรุปเทคโนโลยี**

Smart Learning Hub ใช้เทคโนโลยีที่ทันสมัยและเหมาะสมสำหรับการพัฒนาเว็บแอปพลิเคชันที่รองรับการเชื่อมต่อกับบริการภายนอก การจัดการข้อมูลที่ซับซ้อน และการขยายฟีเจอร์ในอนาคต

### **สถาปัตยกรรมโดยรวม**
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend       │    │   External      │
│                 │    │                 │    │   Services      │
│ • Tailwind CSS  │◄──►│ • Flask         │◄──►│ • Google API    │
│ • Jinja2        │    │ • SQLAlchemy    │    │ • Chrome Ext.   │
│ • JavaScript    │    │ • SQLite        │    │ • MS Teams      │
│ • FontAwesome   │    │ • OAuth         │    │ • KMITL         │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

---

## **1. Backend Technologies**

### **1.1 ภาษาโปรแกรม: Python 3.x**

#### **เหตุผลในการเลือกใช้**
- **ความยืดหยุ่นสูง:** รองรับการพัฒนาได้หลากหลายรูปแบบ
- **ชุมชนที่แข็งแกร่ง:** มีไลบรารีและเครื่องมือมากมาย
- **การเรียนรู้ง่าย:** ไวยากรณ์ที่อ่านง่าย เหมาะสำหรับทีมที่หลากหลาย
- **การรองรับ AI/ML:** เตรียมพร้อมสำหรับการขยายฟีเจอร์ในอนาคต

#### **เวอร์ชันที่ใช้**
- **Python:** 3.9+ (ใช้ features ใหม่ๆ เช่น type hints, dataclasses)
- **Package Manager:** pip และ requirements.txt

### **1.2 Web Framework: Flask**

#### **เหตุผลในการเลือกใช้**
- **เบาและยืดหยุ่น:** ไม่มี overhead มาก เหมาะสำหรับโปรเจกต์ขนาดกลาง
- **การเรียนรู้ง่าย:** มีความซับซ้อนน้อยกว่า Django
- **Customizable:** สามารถปรับแต่งได้ตามต้องการ
- **RESTful API:** รองรับการสร้าง API ได้ดี

#### **การใช้งานหลัก**
```python
# app/__init__.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db = SQLAlchemy(app)
```

### **1.3 ฐานข้อมูล: SQLite (Development) / PostgreSQL (Production)**

#### **SQLite (Development)**
- **เหตุผล:** ง่ายต่อการพัฒนา ไม่ต้องติดตั้งเซิร์ฟเวอร์
- **ข้อดี:** ไฟล์เดียว, ไม่ต้องตั้งค่า, เหมาะสำหรับการทดสอบ
- **ข้อจำกัด:** ไม่เหมาะสำหรับ concurrent users จำนวนมาก

#### **PostgreSQL (Production)**
- **เหตุผล:** รองรับ concurrent users, ACID compliance
- **ข้อดี:** ประสิทธิภาพสูง, รองรับ JSON, Full-text search
- **การใช้งาน:** ใช้ใน production environment

### **1.4 ORM: SQLAlchemy**

#### **เหตุผลในการเลือกใช้**
- **Database Agnostic:** สามารถเปลี่ยนฐานข้อมูลได้ง่าย
- **Type Safety:** รองรับ type hints และ validation
- **Migration Support:** Alembic สำหรับจัดการ schema changes
- **Query Optimization:** มีเครื่องมือสำหรับ optimize queries

#### **ตัวอย่างการใช้งาน**
```python
# app/core/user.py
from app import db
from datetime import datetime

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    lessons = db.relationship('Lesson', backref='user', lazy=True)
    notes = db.relationship('Note', backref='user', lazy=True)
```

### **1.5 Authentication: Flask-Login + Google OAuth**

#### **Flask-Login**
- **เหตุผล:** ง่ายต่อการใช้งาน, รองรับ session management
- **ฟีเจอร์:** User session, Remember me, Login required decorator

#### **Google OAuth 2.0**
- **เหตุผล:** ปลอดภัย, ไม่ต้องจัดการ password, เชื่อมต่อกับ Google Classroom
- **การใช้งาน:** ใช้ google-auth-library สำหรับ OAuth flow

---

## **2. Frontend Technologies**

### **2.1 Template Engine: Jinja2**

#### **เหตุผลในการเลือกใช้**
- **Native Flask Integration:** มาพร้อมกับ Flask
- **Powerful:** รองรับ inheritance, macros, filters
- **Security:** Auto-escaping ป้องกัน XSS
- **Performance:** Compiled templates, caching

#### **ตัวอย่างการใช้งาน**
```html
<!-- templates/base.html -->
<!DOCTYPE html>
<html>
<head>
    <title>{% block title %}{% endblock %} - Smart Learning Hub</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='css/tailwind.css') }}">
</head>
<body>
    {% include 'sidebar_auth_fragment.html' %}
    <main class="ml-64 p-6">
        {% block content %}{% endblock %}
    </main>
</body>
</html>
```

### **2.2 CSS Framework: Tailwind CSS**

#### **เหตุผลในการเลือกใช้**
- **Utility-First:** เขียน CSS ได้เร็ว, ไม่ต้องคิดชื่อ class
- **Responsive:** มี responsive utilities ในตัว
- **Customizable:** สามารถปรับแต่ง theme ได้
- **Small Bundle Size:** PurgeCSS ลบ CSS ที่ไม่ได้ใช้

#### **การตั้งค่า**
```javascript
// tailwind.config.js
module.exports = {
  content: [
    "./app/templates/**/*.html",
    "./app/static/js/**/*.js"
  ],
  theme: {
    extend: {
      colors: {
        primary: '#3B82F6',
        secondary: '#10B981'
      }
    }
  },
  plugins: []
}
```

### **2.3 JavaScript: Vanilla JS**

#### **เหตุผลในการเลือกใช้**
- **No Dependencies:** ไม่ต้องโหลด library เพิ่ม
- **Performance:** ขนาดไฟล์เล็ก, โหลดเร็ว
- **Modern Features:** ES6+ features, async/await
- **Maintainability:** ง่ายต่อการดูแลรักษา

#### **ตัวอย่างการใช้งาน**
```javascript
// app/static/js/main.js
document.addEventListener('DOMContentLoaded', function() {
    // Pomodoro Timer
    const startTimer = () => {
        const timer = document.getElementById('pomodoro-timer');
        let timeLeft = 25 * 60; // 25 minutes
        
        const countdown = setInterval(() => {
            const minutes = Math.floor(timeLeft / 60);
            const seconds = timeLeft % 60;
            
            timer.textContent = `${minutes}:${seconds.toString().padStart(2, '0')}`;
            
            if (timeLeft <= 0) {
                clearInterval(countdown);
                alert('Pomodoro session completed!');
            }
            timeLeft--;
        }, 1000);
    };
    
    // Event listeners
    document.getElementById('start-timer')?.addEventListener('click', startTimer);
});
```

### **2.4 Icons: FontAwesome + Bootstrap Icons**

#### **FontAwesome**
- **เหตุผล:** มีไอคอนมากมาย, ใช้งานง่าย
- **การใช้งาน:** CDN หรือ local files

#### **Bootstrap Icons**
- **เหตุผล:** ฟรี, ใช้งานง่าย, มาพร้อมกับ Bootstrap
- **การใช้งาน:** สำหรับไอคอนพื้นฐาน

---

## **3. External Integrations**

### **3.1 Google Classroom API**

#### **เทคโนโลยีที่ใช้**
- **Library:** google-auth-library, google-api-python-client
- **Authentication:** OAuth 2.0 Service Account
- **API Version:** Classroom API v1

#### **การใช้งาน**
```python
# app/core/google_credentials.py
from google.oauth2 import service_account
from googleapiclient.discovery import build

class GoogleClassroomManager:
    def __init__(self, credentials_file):
        credentials = service_account.Credentials.from_service_account_file(
            credentials_file,
            scopes=['https://www.googleapis.com/auth/classroom.courses.readonly']
        )
        self.service = build('classroom', 'v1', credentials=credentials)
    
    def list_courses(self):
        """ดึงรายการห้องเรียนจาก Google Classroom"""
        courses = self.service.courses().list().execute()
        return courses.get('courses', [])
    
    def sync_course(self, course_id):
        """ซิงค์ข้อมูลห้องเรียนเข้าระบบ"""
        course = self.service.courses().get(id=course_id).execute()
        # Save to database logic here
        return course
```

### **3.2 Chrome Extension**

#### **เทคโนโลยีที่ใช้**
- **Manifest Version:** 3
- **Content Scripts:** สำหรับดึงข้อมูลจากหน้าเว็บ
- **Background Scripts:** สำหรับจัดการ extension lifecycle

#### **การใช้งาน**
```javascript
// chrome_extension/content_scripts/kmitl_studytable.js
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === 'extractData') {
        const data = extractPageData();
        sendToFlaskBackend(data);
    }
});

function extractPageData() {
    return {
        title: document.title,
        content: document.body.innerText,
        url: window.location.href,
        timestamp: new Date().toISOString()
    };
}

function sendToFlaskBackend(data) {
    fetch('http://localhost:5000/api/import-data', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data)
    });
}
```

---

## **4. Development Tools**

### **4.1 Version Control: Git + GitHub**

#### **เหตุผลในการเลือกใช้**
- **Industry Standard:** ใช้กันแพร่หลาย
- **Collaboration:** รองรับการทำงานเป็นทีม
- **Branching:** Feature branches, pull requests
- **CI/CD Integration:** เชื่อมต่อกับ GitHub Actions

#### **Workflow**
```bash
# Feature branch workflow
git checkout -b feature/new-feature
git add .
git commit -m "feat: add new feature"
git push origin feature/new-feature
# Create pull request
```

### **4.2 Package Management**

#### **Python: pip + requirements.txt**
```txt
# requirements.txt
Flask==2.3.3
Flask-SQLAlchemy==3.0.5
Flask-Login==0.6.3
google-auth==2.23.4
google-api-python-client==2.108.0
Werkzeug==2.3.7
```

#### **Node.js: npm + package.json**
```json
{
  "name": "smart-learning-hub",
  "version": "1.0.0",
  "scripts": {
    "build:css": "tailwindcss -i ./app/static/css/input.css -o ./app/static/css/tailwind.css --watch"
  },
  "devDependencies": {
    "tailwindcss": "^3.3.0",
    "postcss": "^8.4.31",
    "autoprefixer": "^10.4.16"
  }
}
```

### **4.3 Build Tools**

#### **PostCSS + Tailwind CSS**
```javascript
// postcss.config.js
module.exports = {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  }
}
```

---

## **5. Testing Technologies**

### **5.1 Unit Testing: pytest**

#### **เหตุผลในการเลือกใช้**
- **Python Native:** เขียนด้วย Python, ใช้งานง่าย
- **Fixtures:** รองรับ test data และ setup
- **Parametrized Tests:** ทดสอบหลายกรณีได้ง่าย
- **Coverage:** รองรับ code coverage

#### **ตัวอย่างการใช้งาน**
```python
# tests/test_user.py
import pytest
from app import create_app, db
from app.core.user import User

@pytest.fixture
def app():
    app = create_app('testing')
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

def test_user_registration(app, client):
    """ทดสอบการสมัครสมาชิก"""
    response = client.post('/auth/register', data={
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'password123'
    })
    assert response.status_code == 200
    assert User.query.filter_by(username='testuser').first() is not None
```

### **5.2 Integration Testing: Flask-Testing**

#### **เหตุผลในการเลือกใช้**
- **Flask Integration:** ออกแบบมาเฉพาะสำหรับ Flask
- **Database Testing:** รองรับการทดสอบฐานข้อมูล
- **Client Testing:** รองรับการทดสอบ HTTP requests

---

## **6. Deployment Technologies**

### **6.1 Development Environment**

#### **Virtual Environment**
```bash
# สร้าง virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# หรือ venv\Scripts\activate  # Windows

# ติดตั้ง dependencies
pip install -r requirements.txt
npm install

# รัน development server
python run.py
```

### **6.2 Production Environment**

#### **Web Server: Gunicorn + Nginx**
- **Gunicorn:** WSGI server สำหรับ Python
- **Nginx:** Reverse proxy, static file serving, SSL termination

#### **Configuration**
```python
# gunicorn.conf.py
bind = "0.0.0.0:8000"
workers = 4
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 2
```

```nginx
# nginx.conf
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    location /static/ {
        alias /path/to/your/static/files/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

---

## **7. Security Technologies**

### **7.1 Authentication & Authorization**

#### **Flask-Login**
- **Session Management:** จัดการ user sessions
- **Login Required:** Decorator สำหรับป้องกัน unauthorized access
- **Remember Me:** Long-term sessions

#### **OAuth 2.0**
- **Google OAuth:** ปลอดภัย, ไม่ต้องจัดการ password
- **JWT Tokens:** สำหรับ API authentication

### **7.2 Data Protection**

#### **Password Hashing: bcrypt**
```python
from werkzeug.security import generate_password_hash, check_password_hash

# เข้ารหัส password
password_hash = generate_password_hash('user_password')

# ตรวจสอบ password
is_valid = check_password_hash(password_hash, 'user_password')
```

#### **CSRF Protection: Flask-WTF**
```python
from flask_wtf.csrf import CSRFProtect

csrf = CSRFProtect(app)
```

### **7.3 API Security**

#### **Rate Limiting: Flask-Limiter**
```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)
```

---

## **8. Monitoring & Logging**

### **8.1 Logging: Python logging**

#### **การตั้งค่า**
```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
```

### **8.2 Error Tracking: Sentry (Future)**

#### **เหตุผลในการเลือกใช้**
- **Real-time Monitoring:** ติดตาม errors แบบ real-time
- **Performance Monitoring:** ติดตาม performance
- **Release Tracking:** ติดตาม deployment

---

## **9. Future Technology Considerations**

### **9.1 Database Scaling**
- **Redis:** สำหรับ caching และ session storage
- **PostgreSQL:** สำหรับ production database
- **Database Sharding:** สำหรับ scaling

### **9.2 API Development**
- **Flask-RESTful:** สำหรับ REST API
- **GraphQL:** สำหรับ flexible data fetching
- **API Documentation:** Swagger/OpenAPI

### **9.3 Frontend Enhancement**
- **Vue.js/React:** สำหรับ SPA features
- **WebSocket:** สำหรับ real-time features
- **PWA:** สำหรับ mobile experience

### **9.4 AI/ML Integration**
- **TensorFlow/PyTorch:** สำหรับ ML models
- **scikit-learn:** สำหรับ basic ML
- **NLP Libraries:** สำหรับ text processing

---

## **10. Technology Stack Summary**

### **Backend Stack**
- **Language:** Python 3.9+
- **Framework:** Flask 2.3+
- **Database:** SQLite (dev) / PostgreSQL (prod)
- **ORM:** SQLAlchemy
- **Authentication:** Flask-Login + Google OAuth

### **Frontend Stack**
- **Template Engine:** Jinja2
- **CSS Framework:** Bootstap + Tailwind CSS
- **JavaScript:** Vanilla JS (ES6+)
- **Icons:** FontAwesome + Bootstrap Icons

### **External Integrations**
- **Google APIs:** Classroom API, OAuth 2.0
- **Chrome Extension:** Manifest V3, Content Scripts

### **Development Tools**
- **Version Control:** Git + GitHub
- **Package Managers:** pip (Python) + npm (Node.js)
- **Build Tools:** PostCSS + Tailwind CSS

### **Testing & Quality**
- **Unit Testing:** pytest
- **Integration Testing:** Flask-Testing
- **Code Quality:** PEP 8, ESLint

### **Deployment & Operations**
- **Web Server:** Gunicorn + Nginx
- **SSL:** Let's Encrypt
- **Monitoring:** Python logging + Sentry (future)

---