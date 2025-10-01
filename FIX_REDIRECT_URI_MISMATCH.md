# 🔧 แก้ไขปัญหา redirect_uri_mismatch

## 🚨 ปัญหาที่พบ

เมื่อพยายามเชื่อมต่อ Google Classroom API พบข้อผิดพลาด:
```
การเข้าถึงถูกบล็อก: คําขอของแอปนี้ไม่ถูกต้อง
ข้อผิดพลาด 400: redirect_uri_mismatch
```

## 🔍 สาเหตุ

**Error 400: redirect_uri_mismatch** เกิดขึ้นเมื่อ redirect URI ที่ตั้งค่าใน Google Cloud Console ไม่ตรงกับที่ application ใช้

### **รายละเอียดปัญหา**

1. **Application Route**: `/google_classroom/oauth2callback`
2. **Port ที่ใช้**: 8000 (หรือ 8001)
3. **Google Cloud Console**: อาจตั้งค่า redirect URI เป็น port อื่น (เช่น 5000)

## 🔧 วิธีแก้ไข

### **Option 1: แก้ไข Google Cloud Console (แนะนำ)**

#### **ขั้นตอนที่ 1: ไปที่ Google Cloud Console**
1. เปิด [Google Cloud Console](https://console.cloud.google.com/)
2. เลือก Project ที่สร้างไว้
3. ไปที่ **APIs & Services** > **Credentials**

#### **ขั้นตอนที่ 2: แก้ไข OAuth 2.0 Client ID**
1. คลิกที่ OAuth 2.0 Client ID ที่สร้างไว้
2. ในส่วน **Authorized redirect URIs** เพิ่ม URLs ต่อไปนี้:

```
http://localhost:8000/google_classroom/oauth2callback
http://127.0.0.1:8000/google_classroom/oauth2callback
http://localhost:8001/google_classroom/oauth2callback
http://127.0.0.1:8001/google_classroom/oauth2callback
```

#### **ขั้นตอนที่ 3: บันทึกการเปลี่ยนแปลง**
1. คลิก **Save**
2. รอสักครู่ให้การเปลี่ยนแปลงมีผล

### **Option 2: ตรวจสอบ Port ที่ใช้**

#### **ตรวจสอบ port ปัจจุบัน**
```bash
# ดู port ที่ application รันอยู่
lsof -i :8000
lsof -i :8001
lsof -i :5000

# หรือดู process ที่รันอยู่
ps aux | grep flask
```

#### **ตรวจสอบ start_flask.sh**
```bash
# ดู port ที่ตั้งค่าไว้
cat start_flask.sh | grep PORT
```

### **Option 3: แก้ไข Code (ถ้าจำเป็น)**

หากต้องการแก้ไข code ให้ใช้ port ที่แน่นอน:

```python
# ใน app/routes.py แก้ไขเป็น:
flow.redirect_uri = "http://localhost:8000/google_classroom/oauth2callback"
```

## 🧪 การทดสอบ

### **1. ทดสอบ Configuration**
```bash
python google_classroom_config.py
```

### **2. ทดสอบ Redirect URI**
```bash
python -c "
from app import app
with app.test_request_context():
    print('Redirect URI:', app.url_for('oauth2callback', _external=True))
"
```

### **3. ทดสอบ Web Interface**
1. รัน application: `./start_flask.sh`
2. ไปที่หน้า Create New Lesson
3. คลิก "Connect Google Classroom"
4. ตรวจสอบว่า redirect URI ตรงกับที่ตั้งค่าใน Google Cloud Console

## 🔍 การตรวจสอบ

### **ตรวจสอบ Redirect URI ใน Google Cloud Console**

1. **APIs & Services** > **Credentials**
2. คลิก OAuth 2.0 Client ID
3. ดู **Authorized redirect URIs**
4. ตรวจสอบว่า URLs ตรงกับที่ application ใช้

### **ตรวจสอบ Application Logs**

```bash
# ดู Flask logs
tail -f flask.log

# หรือดู console output เมื่อรัน application
```

### **ตรวจสอบ Network Requests**

1. เปิด Developer Tools (F12)
2. ไปที่ Network tab
3. คลิก "Connect Google Classroom"
4. ดู redirect URL ที่ส่งไป

## 📋 Redirect URIs ที่ต้องตั้งค่า

### **Development Environment**
```
http://localhost:8000/google_classroom/oauth2callback
http://127.0.0.1:8000/google_classroom/oauth2callback
http://localhost:8001/google_classroom/oauth2callback
http://127.0.0.1:8001/google_classroom/oauth2callback
```

### **Production Environment**
```
https://yourdomain.com/google_classroom/oauth2callback
```

## 🚀 ขั้นตอนการแก้ไข

### **1. ตรวจสอบ Port ปัจจุบัน**
```bash
# ดู port ที่ application รันอยู่
lsof -i :8000
```

### **2. ไปที่ Google Cloud Console**
- [Google Cloud Console](https://console.cloud.google.com/)
- APIs & Services > Credentials
- แก้ไข OAuth 2.0 Client ID

### **3. เพิ่ม Redirect URIs**
เพิ่ม URLs ที่ตรงกับ port ที่ใช้

### **4. บันทึกและทดสอบ**
- Save การเปลี่ยนแปลง
- รอสักครู่
- ทดสอบการเชื่อมต่อใหม่

## 🔒 ความปลอดภัย

### **ข้อควรระวัง**
1. **ไม่แชร์ Client Secret** - เก็บไว้เป็นความลับ
2. **ใช้ HTTPS ใน Production** - ไม่ใช้ HTTP
3. **จำกัด Redirect URIs** - เพิ่มเฉพาะที่จำเป็น
4. **ตรวจสอบ OAuth Consent Screen** - ตั้งค่าให้ถูกต้อง

### **การตรวจสอบ**
1. **Client ID**: ใช้ได้ใน public
2. **Client Secret**: เก็บเป็นความลับ
3. **Redirect URIs**: ต้องตรงกับที่ใช้จริง
4. **Scopes**: ต้องมี scopes ที่จำเป็น

## 🎯 สรุป

**ปัญหาหลัก**: redirect_uri_mismatch
**วิธีแก้**: เพิ่ม redirect URIs ที่ถูกต้องใน Google Cloud Console
**สิ่งที่ต้องทำ**: ไปที่ Google Cloud Console และเพิ่ม URLs ที่ตรงกับ port ที่ใช้

หลังจากแก้ไขแล้ว Google Classroom API จะเชื่อมต่อได้ปกติครับ! 🚀

**ทดสอบ**: ลองเชื่อมต่อ Google Classroom อีกครั้งหลังจากแก้ไข redirect URIs
