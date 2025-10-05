# 📋 Smart Learning Hub - MVC Architecture

## 🏗️ **โครงสร้างหลัก (Root Level)**

```
PyProject-5/
├── start_server.py          # 🚀 ไฟล์เริ่มต้นหลัก
├── requirements.txt         # 📦 Dependencies
├── README.md               # 📖 เอกสาร
├── LICENSE                 # 📄 License
├── app/                    # 🎯 แอปพลิเคชันหลัก (MVC)
├── database/               # 🗄️ ฐานข้อมูล
├── scripts/                # 🔧 Scripts ที่ใช้งาน
├── docs/                   # 📚 เอกสาร
├── chrome_extension/       # 🌐 Chrome Extension
├── instance/               # 💾 ไฟล์ instance
├── uploads/                # 📁 ไฟล์อัปโหลด
├── venv/                   # 🐍 Virtual Environment
└── archive/                # 📦 ไฟล์เก่า (ย้ายไปเก็บ)
```

## 🎯 **โครงสร้าง MVC ใน app/**

### **📁 Models (ข้อมูล)**
```
app/models/
├── user.py                 # 👤 User Model
├── lesson.py               # 📚 Lesson Model  
├── note.py                 # 📝 Note Model
├── task.py                 # ✅ Task Model
└── lesson_section.py       # 📖 Lesson Section Model
```

### **🎮 Controllers (Views)**
```
app/views/
├── auth_views.py           # 🔐 Authentication Controller
├── user_views.py          # 👤 User Controller
├── lesson_views.py        # 📚 Lesson Controller
├── note_views.py          # 📝 Note Controller
└── task_views.py          # ✅ Task Controller
```

### **🛣️ Routes (HTTP Routes)**
```
app/routes/
├── auth_routes.py         # 🔐 Auth Routes
├── user_routes.py         # 👤 User Routes
├── lesson_routes.py       # 📚 Lesson Routes
├── note_routes.py         # 📝 Note Routes
└── task_routes.py         # ✅ Task Routes
```

### **⚙️ Services (Business Logic)**
```
app/services.py            # 🏢 Business Logic Layer
├── UserService            # 👤 User Business Logic
├── LessonService          # 📚 Lesson Business Logic
├── NoteService            # 📝 Note Business Logic
└── TaskService            # ✅ Task Business Logic
```

### **🔧 Middleware**
```
app/middleware/
└── auth_middleware.py     # 🔐 Authentication Middleware
```

### **⚙️ Configuration**
```
app/config/
├── settings.py            # ⚙️ App Settings
└── google_classroom_config.py  # 🔗 Google Classroom Config
```

### **🎨 Templates (Views)**
```
app/templates/
├── base.html              # 🏠 Base Template
├── login.html             # 🔐 Login Page
├── register.html          # 📝 Register Page
├── dashboard_fragment.html # 📊 Dashboard
├── class_detail/          # 📚 Class Detail Pages
├── lessons/               # 📖 Lesson Pages
├── notes/                 # 📝 Note Pages
└── auth/                  # 🔐 Auth Pages
```

### **🎨 Static Files**
```
app/static/
├── css/                   # 🎨 CSS Styles
├── js/                    # 📜 JavaScript
├── fontawesome/           # 🎯 FontAwesome Icons
└── uploads/               # 📁 Uploaded Files
```

## 🗄️ **โครงสร้างฐานข้อมูล**

```
database/
├── config.py              # ⚙️ Database Config
├── manager.py             # 🔧 Database Manager
├── setup_database.py      # 🚀 Database Setup
├── models/                # 📊 Database Models
├── migrations/            # 🔄 Database Migrations
├── seeds/                 # 🌱 Seed Data
└── backups/               # 💾 Database Backups
```

## 🔧 **Scripts ที่ใช้งาน**

```
scripts/
├── database_setup.sh      # 🗄️ Database Setup
├── migrations/            # 🔄 Migration Scripts
├── debug/                 # 🐛 Debug Scripts
└── tests/                 # 🧪 Test Scripts
```

## 📦 **Archive (ไฟล์เก่า)**

```
archive/
├── old_files/             # 📁 ไฟล์เก่า
├── test_files/            # 🧪 ไฟล์ test เก่า
├── scripts/               # 🔧 Scripts เก่า
└── docs/                  # 📚 เอกสารเก่า
```

## 🎯 **หลักการ MVC**

### **📊 Model (ข้อมูล)**
- **หน้าที่**: จัดการข้อมูลและฐานข้อมูล
- **ไฟล์**: `app/models/`
- **ตัวอย่าง**: `UserModel`, `LessonModel`, `NoteModel`

### **🎮 View (การแสดงผล)**
- **หน้าที่**: จัดการการแสดงผลและ UI
- **ไฟล์**: `app/templates/`, `app/static/`
- **ตัวอย่าง**: HTML templates, CSS, JavaScript

### **🎯 Controller (ควบคุม)**
- **หน้าที่**: จัดการ business logic และ HTTP requests
- **ไฟล์**: `app/views/`, `app/routes/`, `app/services.py`
- **ตัวอย่าง**: `AuthController`, `UserService`, `LessonService`

## ✅ **ข้อดีของโครงสร้างใหม่**

1. **🎯 ชัดเจน**: แยกแยะ Model, View, Controller ชัดเจน
2. **🔧 ง่ายต่อการดูแล**: โครงสร้างเป็นระเบียบ
3. **📈 ขยายได้**: เพิ่ม features ใหม่ได้ง่าย
4. **👥 ทีมเข้าใจ**: ทีมเข้าใจโครงสร้างได้ง่าย
5. **🧹 สะอาด**: Root directory สะอาด เป็นระเบียบ
6. **📦 จัดเก็บ**: ไฟล์เก่าถูกย้ายไป archive/

## 🚀 **การเริ่มต้นใช้งาน**

```bash
# เริ่มต้นเซิร์ฟเวอร์
python start_server.py

# เซิร์ฟเวอร์จะทำงานที่
# http://localhost:5004
```

## 📝 **การพัฒนา**

### **เพิ่ม Model ใหม่**
1. สร้างไฟล์ใน `app/models/`
2. เพิ่ม Service ใน `app/services.py`
3. เพิ่ม View ใน `app/views/`
4. เพิ่ม Route ใน `app/routes/`

### **เพิ่ม Template ใหม่**
1. สร้างไฟล์ HTML ใน `app/templates/`
2. เพิ่ม CSS ใน `app/static/css/`
3. เพิ่ม JavaScript ใน `app/static/js/`

### **เพิ่ม API Endpoint ใหม่**
1. เพิ่ม route ใน `app/routes/`
2. เพิ่ม controller logic ใน `app/views/`
3. เพิ่ม business logic ใน `app/services.py`

---

**Smart Learning Hub MVC Architecture** - โครงสร้างที่ชัดเจน ง่ายต่อการดูแล และขยายได้ 🎯
