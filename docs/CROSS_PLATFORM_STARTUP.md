# 🚀 Cross-Platform Startup Guide

## 📋 **วิธีรันระบบ**

### **สำหรับ macOS/Linux:**
```bash
./start.sh
```

### **สำหรับ Windows:**
```bash
python start.py
```

### **สำหรับทุกระบบ (Cross-platform):**
```bash
python start.py
```

## 🎯 **สิ่งที่ Script จะทำ:**

### **1. Environment Setup**
- ตั้งค่า environment variables
- ตั้งค่า Google OAuth credentials
- ตั้งค่า Flask development mode

### **2. Virtual Environment**
- ตรวจสอบ virtual environment
- สร้าง virtual environment ใหม่ถ้าไม่มี
- เปิดใช้งาน virtual environment

### **3. Dependencies**
- ตรวจสอบ Python dependencies
- ติดตั้ง packages จาก requirements.txt
- ติดตั้ง dependency-injector

### **4. OOP Architecture Validation**
- ตรวจสอบไฟล์ OOP architecture
- ตรวจสอบ Domain, Application, Infrastructure, Presentation layers

### **5. Database Initialization**
- สร้าง instance directory
- รัน database migration
- ตรวจสอบ database health
- สร้าง database ใหม่ถ้าไม่มี

### **6. Default User**
- สร้าง test user (email: 1, password: 1)
- ตั้งค่า user permissions

### **7. OOP Architecture Test**
- ทดสอบ OOP architecture
- ตรวจสอบ dependency injection

### **8. Flask Application**
- เริ่ม Flask development server
- เปิดใช้งานที่ http://localhost:5004

## 🔧 **Requirements:**

### **System Requirements:**
- Python 3.8+
- pip
- Git

### **Python Packages:**
- Flask
- SQLAlchemy
- Werkzeug
- dependency-injector

## 📊 **Features ที่พร้อมใช้:**

### **✅ User Management**
- Login/Register
- User profiles
- Authentication

### **✅ Lesson Management**
- Create/Edit/Delete lessons
- Lesson categories
- Lesson status

### **✅ Note System**
- Markdown notes
- Note search
- Note categories

### **✅ Task Management**
- Create/Edit/Delete tasks
- Task priorities
- Due dates

### **✅ Pomodoro Timer**
- Focus sessions
- Break sessions
- Session statistics
- Productivity insights

### **✅ Progress Tracking**
- Dashboard
- Statistics
- Progress reports

## 🌐 **Access URLs:**

### **Web Interface:**
- **Main App**: http://localhost:5004
- **Dashboard**: http://localhost:5004/dashboard
- **Lessons**: http://localhost:5004/class
- **Notes**: http://localhost:5004/note
- **Tasks**: http://localhost:5004/track
- **Pomodoro**: http://localhost:5004/pomodoro

### **API Endpoints:**
- **Health Check**: http://localhost:5004/api/pomodoro/health
- **Start Session**: http://localhost:5004/api/pomodoro/start
- **User API**: http://localhost:5004/api/users
- **Lesson API**: http://localhost:5004/api/lessons

## 🎮 **Default Login:**
- **Email**: 1
- **Password**: 1

## 🛠️ **Troubleshooting:**

### **Port Already in Use:**
```bash
# Kill process on port 5004
lsof -ti:5004 | xargs kill -9
```

### **Database Issues:**
```bash
# Delete database and restart
rm -rf instance/site.db
python start.py
```

### **Dependencies Issues:**
```bash
# Reinstall dependencies
pip install -r requirements.txt
```

### **Virtual Environment Issues:**
```bash
# Recreate virtual environment
rm -rf venv
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## 📝 **Notes:**

- Script นี้ทำงานได้บน Windows, macOS, และ Linux
- ใช้ Python แทน bash script เพื่อความเข้ากันได้
- รองรับ cross-platform development
- มี error handling และ cleanup functions
- รองรับ signal handling สำหรับ graceful shutdown

## 🎉 **Ready to Go!**

เพียงรัน `python start.py` แล้วเข้าใช้งานได้เลย! 🚀
