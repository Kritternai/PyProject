# 🚀 Smart Learning Hub - Startup Scripts Guide

## 📋 ภาพรวม

โปรเจ็ค Smart Learning Hub มี startup scripts หลายตัวสำหรับการใช้งานที่แตกต่างกัน:

1. **`start_flask.sh`** - Full-featured startup script (แนะนำ)
2. **`start_flask_simple.sh`** - Simple startup script
3. **`database_setup.sh`** - Database setup script แยกต่างหาก

## 🎯 การใช้งาน

### **1. Full-Featured Startup (แนะนำ)**

```bash
# ให้สิทธิ์การรัน
chmod +x start_flask.sh

# รัน script
./start_flask.sh
```

**Features:**
- ✅ Environment setup อัตโนมัติ
- ✅ Virtual environment management
- ✅ Dependencies check & installation
- ✅ Database initialization & health check
- ✅ Automatic backup creation
- ✅ Comprehensive error handling
- ✅ Colored output และ status messages
- ✅ Cleanup on exit

### **2. Simple Startup**

```bash
# ให้สิทธิ์การรัน
chmod +x start_flask_simple.sh

# รัน script
./start_flask_simple.sh
```

**Features:**
- ✅ Basic environment setup
- ✅ Simple virtual environment handling
- ✅ Basic database initialization
- ✅ Minimal output

### **3. Database Setup แยกต่างหาก**

```bash
# ให้สิทธิ์การรัน
chmod +x database_setup.sh

# รัน script
./database_setup.sh
```

**Features:**
- ✅ Database initialization แยกต่างหาก
- ✅ Directory creation
- ✅ Backup management
- ✅ Health check
- ✅ Schema information display

## 🔧 การตั้งค่าเริ่มต้น

### **1. ให้สิทธิ์การรัน Scripts**

```bash
chmod +x start_flask.sh
chmod +x start_flask_simple.sh
chmod +x database_setup.sh
```

### **2. ตรวจสอบ Dependencies**

```bash
# ตรวจสอบ Python
python3 --version

# ตรวจสอบ pip
pip --version

# ตรวจสอบ virtual environment
which python
```

### **3. ตรวจสอบไฟล์ที่จำเป็น**

```
PyProject-5/
├── start_flask.sh          # Full startup script
├── start_flask_simple.sh   # Simple startup script
├── database_setup.sh       # Database setup script
├── init_database.py        # Database initialization
├── test_database.py        # Database testing
├── run.py                  # Flask application
├── requirements.txt        # Python dependencies
├── database/               # Database package
│   ├── __init__.py
│   ├── config.py
│   ├── manager.py
│   └── models/
└── app/                    # Flask application
    ├── __init__.py
    └── routes.py
```

## 🚀 ขั้นตอนการเริ่มต้น

### **ครั้งแรก (First Time Setup)**

```bash
# 1. Setup database
./database_setup.sh

# 2. Start application
./start_flask.sh
```

### **การใช้งานปกติ (Normal Usage)**

```bash
# Start application (database จะถูกตรวจสอบอัตโนมัติ)
./start_flask.sh
```

### **การใช้งานแบบง่าย (Quick Start)**

```bash
# Simple startup
./start_flask_simple.sh
```

## 📊 สิ่งที่ Scripts จะทำ

### **start_flask.sh (Full Version)**

1. **Environment Setup**
   - Set environment variables
   - Configure Flask settings

2. **Virtual Environment**
   - Check existing virtual environment
   - Create new one if needed
   - Activate virtual environment

3. **Dependencies**
   - Check Python packages
   - Install missing dependencies
   - Verify Flask installation

4. **Database**
   - Check database existence
   - Initialize if needed
   - Health check
   - Create backup

5. **Final Checks**
   - Verify required files
   - Final database health check
   - Start Flask application

6. **Cleanup**
   - Graceful shutdown
   - Deactivate virtual environment

### **start_flask_simple.sh**

1. Set environment variables
2. Handle virtual environment
3. Basic database check
4. Start Flask

### **database_setup.sh**

1. Create necessary directories
2. Initialize database
3. Health check
4. Create backup
5. Show schema information

## 🛠️ การแก้ไขปัญหา

### **ปัญหา: Permission Denied**

```bash
chmod +x start_flask.sh
```

### **ปัญหา: Virtual Environment ไม่พบ**

```bash
# Script จะสร้าง virtual environment ใหม่ให้อัตโนมัติ
# หรือสร้างเอง:
python3 -m venv venv
source venv/bin/activate
```

### **ปัญหา: Dependencies ไม่ครบ**

```bash
# Script จะติดตั้งให้อัตโนมัติ
# หรือติดตั้งเอง:
pip install -r requirements.txt
```

### **ปัญหา: Database Error**

```bash
# รัน database setup แยกต่างหาก:
./database_setup.sh
```

## 📝 การปรับแต่ง

### **1. เปลี่ยน Virtual Environment Path**

แก้ไขใน `start_flask.sh`:

```bash
# เปลี่ยนจาก
if [ -d "/Users/kbbk/PyProject-1/venv" ]; then
    source /Users/kbbk/PyProject-1/venv/bin/activate

# เป็น
if [ -d "./venv" ]; then
    source ./venv/bin/activate
```

### **2. เปลี่ยน Port**

แก้ไขใน script:

```bash
# เปลี่ยนจาก
flask run --host=0.0.0.0 --port=5000

# เป็น
flask run --host=0.0.0.0 --port=8000
```

### **3. เพิ่ม Environment Variables**

เพิ่มใน script:

```bash
export CUSTOM_VAR="value"
export ANOTHER_VAR="another_value"
```

## 🔍 การตรวจสอบสถานะ

### **1. ตรวจสอบ Database**

```bash
python test_database.py
```

### **2. ตรวจสอบ Flask App**

```bash
python -c "from app import app; print('Flask app loaded successfully')"
```

### **3. ตรวจสอบ Dependencies**

```bash
pip list | grep -E "(flask|sqlalchemy|werkzeug)"
```

## 📚 ตัวอย่างการใช้งาน

### **Development Mode**

```bash
./start_flask.sh
# จะเริ่มใน development mode พร้อม debug
```

### **Production Mode**

```bash
export FLASK_ENV="production"
export FLASK_DEBUG="0"
./start_flask.sh
```

### **Custom Port**

```bash
# แก้ไข script หรือรันเอง:
flask run --host=0.0.0.0 --port=8000
```

## 🎉 สรุป

Startup scripts เหล่านี้จะช่วยให้คุณ:

- **เริ่มต้นโปรเจ็คได้ง่าย** - ไม่ต้องจำคำสั่งยาวๆ
- **จัดการฐานข้อมูลอัตโนมัติ** - ไม่ต้องกังวลเรื่อง setup
- **ตรวจสอบระบบอัตโนมัติ** - รู้ปัญหาได้ทันที
- **จัดการ dependencies** - ติดตั้งให้อัตโนมัติ
- **สร้าง backup** - ข้อมูลปลอดภัย

**แนะนำให้ใช้ `start_flask.sh` เป็นหลัก** เพราะมี features ครบถ้วนและปลอดภัยที่สุด! 🚀
