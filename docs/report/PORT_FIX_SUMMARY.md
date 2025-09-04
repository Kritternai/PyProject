# 🔧 แก้ไขปัญหาพอร์ตซ้ำ - Port 5000 Conflict

## 🚨 ปัญหาที่พบ

เมื่อรัน `./start_flask.sh` พบข้อผิดพลาด:
```
Address already in use
Port 5000 is in use by another program.
```

## 🔍 สาเหตุ

บน **macOS** พอร์ต 5000 มักจะถูกใช้โดย:
- **AirPlay Receiver** (System Preferences → General → AirDrop & Handoff)
- **AirPlay Receiver** service ที่เปิดใช้งานอยู่
- Process อื่นๆ ที่ใช้พอร์ต 5000

## ✅ วิธีแก้ไข

### **1. เปลี่ยนพอร์ตเป็น 8000 (แนะนำ)**

แก้ไขแล้วในไฟล์:
- `start_flask.sh` - ใช้พอร์ต 8000 เป็นหลัก
- `start_flask_simple.sh` - ใช้พอร์ต 8000 เป็นหลัก

### **2. การทำงานใหม่**

```bash
# รัน startup script
./start_flask.sh

# จะได้ผลลัพธ์:
[INFO] Starting Flask on port 8000 (avoiding macOS AirPlay port 5000)...
[INFO] Flask will be available at: http://localhost:8000
```

### **3. ถ้าพอร์ต 8000 ก็ไม่ว่าง**

Script จะเปลี่ยนไปใช้พอร์ต 8001 อัตโนมัติ:
```bash
[WARNING] Port 8000 is busy, trying port 8001...
[INFO] Flask will be available at: http://localhost:8001
```

## 🎯 พอร์ตที่แนะนำ

| พอร์ต | เหตุผล | สถานะ |
|-------|--------|--------|
| **8000** | ไม่มี conflict กับ macOS | ✅ แนะนำ |
| **8001** | Backup port | ✅ สำรอง |
| **5000** | มี conflict กับ AirPlay | ❌ ไม่แนะนำ |

## 🔧 การแก้ไขด้วยตนเอง

### **วิธีที่ 1: ปิด AirPlay Receiver**

1. ไปที่ **System Preferences** → **General**
2. เลือก **AirDrop & Handoff**
3. ปิด **AirPlay Receiver**

### **วิธีที่ 2: เปลี่ยนพอร์ตใน script**

แก้ไขใน `start_flask.sh`:
```bash
# เปลี่ยนจาก
PORT=8000

# เป็น
PORT=3000  # หรือพอร์ตอื่นที่ต้องการ
```

### **วิธีที่ 3: ระบุพอร์ตเอง**

```bash
# รัน Flask ด้วยพอร์ตที่ต้องการ
flask run --host=0.0.0.0 --port=3000
```

## 🚀 การใช้งาน

### **รันแบบปกติ**
```bash
./start_flask.sh
# จะใช้พอร์ต 8000 หรือ 8001
```

### **รันแบบง่าย**
```bash
./start_flask_simple.sh
# จะใช้พอร์ต 8000 หรือ 8001
```

### **ตรวจสอบพอร์ตที่ใช้**
```bash
# ดู process ที่รันอยู่
ps aux | grep flask

# ดูพอร์ตที่ใช้
netstat -an | grep LISTEN
```

## 📱 การเข้าถึงแอปพลิเคชัน

### **Local Access**
- **http://localhost:8000** (พอร์ตหลัก)
- **http://localhost:8001** (พอร์ตสำรอง)

### **Network Access**
- **http://YOUR_IP:8000** (จากอุปกรณ์อื่นในเครือข่าย)
- **http://YOUR_IP:8001** (จากอุปกรณ์อื่นในเครือข่าย)

## 🎉 สรุป

✅ **แก้ไขแล้ว** - เปลี่ยนจากพอร์ต 5000 เป็น 8000
✅ **Auto-fallback** - ถ้าพอร์ต 8000 ไม่ว่าง จะใช้ 8001
✅ **No more conflicts** - ไม่มีปัญหากับ macOS AirPlay
✅ **Easy to use** - รัน `./start_flask.sh` ได้เลย

ตอนนี้คุณสามารถรัน `./start_flask.sh` ได้โดยไม่มีปัญหาพอร์ตซ้ำแล้วครับ! 🚀
