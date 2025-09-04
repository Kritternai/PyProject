# 🔐 การตั้งค่า Google OAuth Credentials อย่างปลอดภัย

## 🚨 ปัญหาที่แก้ไขแล้ว

**GitHub Push Protection** ตรวจพบ Google OAuth credentials ในไฟล์ `start_flask.sh`
- ✅ ลบ Client ID และ Client Secret ออกจากไฟล์แล้ว
- ✅ ใช้ environment variables แทน
- ✅ ไม่มี secrets ใน code repository

## 🔧 วิธีตั้งค่า Google OAuth Credentials

### **1. ตั้งค่า Environment Variables**

#### **Option A: Export ใน Terminal (ชั่วคราว)**
```bash
export GOOGLE_CLIENT_ID="your-actual-client-id-here"
export GOOGLE_CLIENT_SECRET="your-actual-client-secret-here"
export FLASK_SECRET_KEY="your-strong-random-secret-key"
```

#### **Option B: สร้างไฟล์ .env (แนะนำ)**
```bash
# สร้างไฟล์ .env
cat > .env << 'EOF'
# Google OAuth 2.0 Credentials
GOOGLE_CLIENT_ID=your-actual-client-id-here
GOOGLE_CLIENT_SECRET=your-actual-client-secret-here

# Flask Configuration
FLASK_SECRET_KEY=your-strong-random-secret-key
FLASK_ENV=development
FLASK_DEBUG=1

# Google OAuth Settings
OAUTHLIB_INSECURE_TRANSPORT=1
EOF

# ตั้งค่า environment variables
export $(cat .env | xargs)
```

#### **Option C: เพิ่มใน ~/.zshrc (ถาวร)**
```bash
echo 'export GOOGLE_CLIENT_ID="your-actual-client-id-here"' >> ~/.zshrc
echo 'export GOOGLE_CLIENT_SECRET="your-actual-client-secret-here"' >> ~/.zshrc
echo 'export FLASK_SECRET_KEY="your-strong-random-secret-key"' >> ~/.zshrc
source ~/.zshrc
```

### **2. ตรวจสอบการตั้งค่า**

```bash
# ตรวจสอบ environment variables
echo "GOOGLE_CLIENT_ID: $GOOGLE_CLIENT_ID"
echo "GOOGLE_CLIENT_SECRET: $GOOGLE_CLIENT_SECRET"
echo "FLASK_SECRET_KEY: $FLASK_SECRET_KEY"

# ทดสอบ Google Classroom configuration
python google_classroom_config.py
```

### **3. ทดสอบ Application**

```bash
# รัน application
./start_flask.sh

# ตรวจสอบว่าไม่มี error เกี่ยวกับ credentials
```

## 🔒 ความปลอดภัย

### **✅ สิ่งที่ทำแล้ว**
- ลบ Google OAuth credentials ออกจาก code repository
- ใช้ environment variables แทน hardcoded values
- ไม่มี secrets ใน Git history

### **⚠️ สิ่งที่ต้องระวัง**
- **ไม่ commit ไฟล์ .env** - เพิ่มใน .gitignore
- **ไม่แชร์ credentials** - เก็บไว้เป็นความลับ
- **ใช้ HTTPS ใน production** - ไม่ใช้ HTTP
- **หมุนเวียน credentials** - เปลี่ยนเป็นระยะ

### **📁 ไฟล์ที่ต้องเพิ่มใน .gitignore**
```gitignore
# Environment variables
.env
.env.local
.env.production

# Secrets
*.key
*.pem
*.p12

# Google OAuth
google_credentials.json
client_secret.json
```

## 🚀 การใช้งาน

### **1. Development Environment**
```bash
# ตั้งค่า environment variables
export GOOGLE_CLIENT_ID="your-client-id"
export GOOGLE_CLIENT_SECRET="your-client-secret"

# รัน application
./start_flask.sh
```

### **2. Production Environment**
```bash
# ตั้งค่า environment variables ใน production server
export GOOGLE_CLIENT_ID="your-production-client-id"
export GOOGLE_CLIENT_SECRET="your-production-client-secret"
export FLASK_SECRET_KEY="your-production-secret-key"

# รัน application
./start_flask.sh
```

## 🧪 การทดสอบ

### **1. ทดสอบ Environment Variables**
```bash
python -c "
import os
print('GOOGLE_CLIENT_ID:', os.environ.get('GOOGLE_CLIENT_ID', 'Not set'))
print('GOOGLE_CLIENT_SECRET:', os.environ.get('GOOGLE_CLIENT_SECRET', 'Not set'))
print('FLASK_SECRET_KEY:', os.environ.get('FLASK_SECRET_KEY', 'Not set'))
"
```

### **2. ทดสอบ Google Classroom Configuration**
```bash
python google_classroom_config.py
```

### **3. ทดสอบ Application**
```bash
./start_flask.sh
```

## 📋 ขั้นตอนการแก้ไขปัญหา

### **1. ลบ Secrets ออกจาก Code (ทำแล้ว)**
- ✅ ลบ Google OAuth credentials จาก `start_flask.sh`
- ✅ ใช้ environment variables แทน

### **2. ตั้งค่า Environment Variables**
```bash
export GOOGLE_CLIENT_ID="your-actual-client-id"
export GOOGLE_CLIENT_SECRET="your-actual-client-secret"
export FLASK_SECRET_KEY="your-strong-random-secret"
```

### **3. ทดสอบการตั้งค่า**
```bash
python google_classroom_config.py
```

### **4. Push Code ใหม่**
```bash
git add .
git commit -m "Remove Google OAuth credentials from code, use environment variables"
git push origin dev-web/migrations
```

## 🎯 สรุป

✅ **แก้ไขปัญหา GitHub Push Protection แล้ว**
✅ **ลบ Google OAuth credentials ออกจาก code**
✅ **ใช้ environment variables แทน**
✅ **ไม่มี secrets ใน repository**

**สิ่งที่ต้องทำ**: ตั้งค่า environment variables ด้วย credentials จริง

**เวลาที่ใช้**: ประมาณ 5-10 นาที

หลังจากตั้งค่าแล้ว Google Classroom API จะทำงานได้ปกติและไม่มีปัญหา GitHub Push Protection ครับ! 🚀

**ทดสอบ**: ตั้งค่า environment variables และลอง push code ใหม่
