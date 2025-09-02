# 🚨 แก้ไขปัญหา redirect_uri_mismatch ทันที

## 🔍 สาเหตุที่พบ

**Application ใช้**: `http://localhost/google_classroom/oauth2callback` (ไม่มี port)
**Port ที่ตั้งค่า**: 8000 หรือ 8001
**Google Cloud Console**: ต้องตั้งค่า redirect URIs ให้ตรงกัน

## 🚀 วิธีแก้ไขทันที

### **ขั้นตอนที่ 1: ไปที่ Google Cloud Console**

1. เปิด [Google Cloud Console](https://console.cloud.google.com/)
2. เลือก Project ที่สร้างไว้
3. ไปที่ **APIs & Services** > **Credentials**

### **ขั้นตอนที่ 2: แก้ไข OAuth 2.0 Client ID**

1. คลิกที่ OAuth 2.0 Client ID ที่สร้างไว้
2. ในส่วน **Authorized redirect URIs** เพิ่ม URLs ต่อไปนี้:

```
http://localhost/google_classroom/oauth2callback
http://localhost:8000/google_classroom/oauth2callback
http://localhost:8001/google_classroom/oauth2callback
http://127.0.0.1:8000/google_classroom/oauth2callback
http://127.0.0.1:8001/google_classroom/oauth2callback
```

### **ขั้นตอนที่ 3: บันทึกการเปลี่ยนแปลง**

1. คลิก **Save**
2. รอสักครู่ให้การเปลี่ยนแปลงมีผล (ประมาณ 1-2 นาที)

## 🔧 ทางเลือกอื่น (ถ้าต้องการแก้ไข Code)

### **Option 1: แก้ไข routes.py ให้ใช้ port ที่แน่นอน**

```python
# ใน app/routes.py แก้ไขบรรทัดที่ 1456 และ 1487:

# แทนที่:
"redirect_uris": [url_for('oauth2callback', _external=True)]

# เป็น:
"redirect_uris": ["http://localhost:8000/google_classroom/oauth2callback"]
```

### **Option 2: แก้ไข app/__init__.py ให้ใช้ port ที่แน่นอน**

```python
# เพิ่มใน app/__init__.py:
app.config['SERVER_NAME'] = 'localhost:8000'
```

## 🧪 การทดสอบหลังแก้ไข

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
4. ตรวจสอบว่าไม่มี error redirect_uri_mismatch

## 📋 Redirect URIs ที่ต้องมีใน Google Cloud Console

### **Development Environment (ต้องมีทั้งหมด)**
```
✅ http://localhost/google_classroom/oauth2callback
✅ http://localhost:8000/google_classroom/oauth2callback
✅ http://localhost:8001/google_classroom/oauth2callback
✅ http://127.0.0.1:8000/google_classroom/oauth2callback
✅ http://127.0.0.1:8001/google_classroom/oauth2callback
```

### **Production Environment**
```
✅ https://yourdomain.com/google_classroom/oauth2callback
```

## 🔍 การตรวจสอบ

### **ตรวจสอบใน Google Cloud Console**
1. **APIs & Services** > **Credentials**
2. คลิก OAuth 2.0 Client ID
3. ดู **Authorized redirect URIs**
4. ตรวจสอบว่า URLs ตรงกับที่ใช้จริง

### **ตรวจสอบ Application**
1. รัน application
2. ดู console output ว่าใช้ port อะไร
3. ตรวจสอบ redirect URI ที่ส่งไป

## 🎯 สรุป

**ปัญหาหลัก**: redirect_uri_mismatch
**วิธีแก้**: เพิ่ม redirect URIs ที่ถูกต้องใน Google Cloud Console
**เวลาที่ใช้**: ประมาณ 5-10 นาที

### **สิ่งที่ต้องทำทันที**
1. ไปที่ Google Cloud Console
2. เพิ่ม redirect URIs ที่ถูกต้อง
3. บันทึกการเปลี่ยนแปลง
4. ทดสอบการเชื่อมต่อใหม่

### **Redirect URIs ที่ต้องมี**
```
http://localhost/google_classroom/oauth2callback
http://localhost:8000/google_classroom/oauth2callback
http://localhost:8001/google_classroom/oauth2callback
```

หลังจากแก้ไขแล้ว Google Classroom API จะเชื่อมต่อได้ปกติครับ! 🚀

**ทดสอบ**: ลองเชื่อมต่อ Google Classroom อีกครั้งหลังจากแก้ไข redirect URIs
