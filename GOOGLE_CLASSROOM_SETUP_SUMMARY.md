# 🚀 การตั้งค่า Google Classroom API ให้เชื่อมต่อได้

## 🎯 สถานะปัจจุบัน

### **✅ สิ่งที่พร้อมแล้ว**

1. **Google API Libraries** - ติดตั้งครบถ้วนแล้ว
2. **GoogleCredentials Model** - พร้อมใช้งาน
3. **Google Classroom Routes** - 7 routes พร้อมใช้งาน
4. **Required Scopes** - 11 scopes ครบถ้วน
5. **Integration Components** - DataSyncService และ LessonManager พร้อม
6. **Database Schema** - รองรับ Google Classroom data

### **⚠️ สิ่งที่ต้องตั้งค่า**

1. **Google Cloud Console Project** - ต้องสร้างและตั้งค่า
2. **OAuth 2.0 Credentials** - ต้องสร้าง Client ID และ Client Secret
3. **Environment Variables** - ต้องตั้งค่า GOOGLE_CLIENT_ID และ GOOGLE_CLIENT_SECRET

## 🔧 ขั้นตอนการตั้งค่า

### **1. 🌐 สร้าง Google Cloud Console Project**

1. ไปที่ [Google Cloud Console](https://console.cloud.google.com/)
2. สร้าง Project ใหม่หรือเลือก Project ที่มีอยู่
3. เปิดใช้งาน Billing (ถ้าจำเป็น)

### **2. 🔧 เปิดใช้งาน Google Classroom API**

1. ไปที่ **APIs & Services** > **Library**
2. ค้นหา "Google Classroom API"
3. คลิก **Enable**

### **3. 🔑 สร้าง OAuth 2.0 Credentials**

1. ไปที่ **APIs & Services** > **Credentials**
2. คลิก **Create Credentials** > **OAuth 2.0 Client IDs**
3. เลือก **Web application**
4. ตั้งชื่อ: "Smart Learning Hub"

### **4. 📝 ตั้งค่า OAuth Consent Screen**

1. **App name**: Smart Learning Hub
2. **User support email**: your-email@domain.com
3. **Developer contact information**: your-email@domain.com
4. **Scopes**: เพิ่ม scopes ที่จำเป็น

### **5. 🔗 เพิ่ม Authorized Redirect URIs**

```
http://localhost:8000/google_classroom/oauth2callback
http://127.0.0.1:8000/google_classroom/oauth2callback
```

**สำหรับ Production:**
```
https://yourdomain.com/google_classroom/oauth2callback
```

### **6. 📋 คัดลอก Credentials**

1. **Client ID**: คัดลอกและเก็บไว้
2. **Client Secret**: คัดลอกและเก็บไว้
3. เก็บข้อมูลเหล่านี้อย่างปลอดภัย

### **7. ⚙️ ตั้งค่า Environment Variables**

#### **Option A: Export ใน Terminal**
```bash
export GOOGLE_CLIENT_ID='your-client-id-here'
export GOOGLE_CLIENT_SECRET='your-client-secret-here'
```

#### **Option B: สร้างไฟล์ .env**
```bash
# คัดลอกไฟล์ตัวอย่าง
cp env_example.txt .env

# แก้ไขไฟล์ .env
nano .env

# ตั้งค่าตัวแปร
export $(cat .env | xargs)
```

#### **Option C: เพิ่มใน ~/.zshrc หรือ ~/.bashrc**
```bash
echo 'export GOOGLE_CLIENT_ID="your-client-id-here"' >> ~/.zshrc
echo 'export GOOGLE_CLIENT_SECRET="your-client-secret-here"' >> ~/.zshrc
source ~/.zshrc
```

## 🧪 การทดสอบ

### **1. ทดสอบ Configuration**
```bash
python google_classroom_config.py
```

### **2. ทดสอบ Integration**
```bash
python test_google_classroom.py
```

### **3. ทดสอบ Web Interface**
1. รัน application: `./start_flask.sh`
2. ไปที่หน้า Create New Lesson
3. คลิก "Connect Google Classroom"
4. ทำ OAuth flow

## 🔍 Troubleshooting

### **ปัญหาที่พบบ่อย**

#### **1. "Google API credentials are not configured"**
**สาเหตุ**: ไม่ได้ตั้งค่า environment variables
**วิธีแก้**: ตั้งค่า GOOGLE_CLIENT_ID และ GOOGLE_CLIENT_SECRET

#### **2. "redirect_uri_mismatch"**
**สาเหตุ**: Redirect URI ไม่ตรงกับที่ตั้งค่าใน Google Cloud Console
**วิธีแก้**: ตรวจสอบ redirect URIs ใน OAuth 2.0 credentials

#### **3. "access_denied"**
**สาเหตุ**: User ไม่ได้ให้ permission
**วิธีแก้**: ตรวจสอบ OAuth consent screen และ scopes

#### **4. "invalid_client"**
**สาเหตุ**: Client ID หรือ Client Secret ไม่ถูกต้อง
**วิธีแก้**: ตรวจสอบ credentials และ environment variables

### **การตรวจสอบ Logs**

```bash
# ดู Flask logs
tail -f flask.log

# ดู application logs
python -c "from app import app; app.logger.info('Testing logger')"
```

## 📊 Google Classroom API Scopes

### **Required Scopes**
```
✅ classroom.courses.readonly - อ่านข้อมูล courses
✅ classroom.announcements.readonly - อ่าน announcements
✅ classroom.courseworkmaterials.readonly - อ่าน materials
✅ classroom.course-work.readonly - อ่าน coursework
✅ classroom.student-submissions.me.readonly - อ่าน submissions
✅ classroom.topics.readonly - อ่าน topics
✅ classroom.rosters.readonly - อ่าน rosters
✅ drive.readonly - อ่าน Google Drive files
✅ userinfo.profile - อ่าน profile information
✅ userinfo.email - อ่าน email address
✅ openid - OpenID Connect
```

## 🚀 Features ที่พร้อมใช้งาน

### **1. OAuth 2.0 Authentication**
- `/google_classroom/authorize` - เริ่ม OAuth flow
- `/google_classroom/oauth2callback` - OAuth callback

### **2. Data Fetching**
- `/google_classroom/fetch_data` - ดึงข้อมูล Google Classroom
- `/google_classroom/fetch_courses` - ดึงรายการ courses
- `/google_classroom/check_status` - ตรวจสอบสถานะการเชื่อมต่อ

### **3. Course Import**
- `/google_classroom/import_course/<course_id>` - นำเข้า course เป็น lesson

### **4. Integration Services**
- **DataSyncService** - ซิงค์ข้อมูล Google Classroom
- **LessonManager** - จัดการ lessons จาก Google Classroom
- **GoogleCredentials** - เก็บ OAuth credentials

## 📁 ไฟล์ที่เกี่ยวข้อง

### **Core Files**
- `app/routes.py` - Google Classroom routes
- `app/core/google_credentials.py` - GoogleCredentials model
- `app/core/data_sync.py` - DataSyncService
- `app/core/lesson_manager.py` - LessonManager

### **Configuration Files**
- `google_classroom_config.py` - Configuration checker
- `env_example.txt` - Environment variables template
- `test_google_classroom.py` - Integration tests

### **Templates**
- `app/templates/lessons/_add.html` - Connect Google Classroom button
- `app/templates/dev.html` - Google Classroom API link
- `app/templates/dashboard.html` - Google Classroom integration

## 🎉 สรุป

✅ **Google Classroom Integration** - พร้อมใช้งาน 100%
✅ **OAuth 2.0 Flow** - พร้อมใช้งาน
✅ **API Endpoints** - 7 routes พร้อมใช้งาน
✅ **Data Models** - รองรับ Google Classroom data
✅ **Integration Services** - DataSyncService และ LessonManager พร้อม

**สิ่งที่ต้องทำ**: ตั้งค่า Google Cloud Console และ environment variables

**เวลาที่ใช้**: ประมาณ 15-30 นาที

**ความยาก**: ง่าย (มี step-by-step instructions)

หลังจากตั้งค่าเสร็จ คุณจะสามารถ:
1. เชื่อมต่อ Google Classroom account
2. นำเข้า courses เป็น lessons
3. ซิงค์ข้อมูล announcements, coursework, materials
4. จัดการ Google Drive files
5. ดู rosters และ topics

🚀 **พร้อมใช้งาน Google Classroom API แล้วครับ!**
