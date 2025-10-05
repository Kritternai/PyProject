# 🍅 Pomodoro Timer - Debug Guide

## ✅ **ระบบที่สร้างแล้ว:**

### **📁 Files Structure (2 ไฟล์)**
- `app/static/js/pomodoro.js` - JavaScript class (267 lines)
- `app/templates/pomodoro_fragment.html` - HTML template (173 lines)

### **🔧 การแก้ไขที่ทำ:**

#### **1. JavaScript Initialization**
- ✅ **เพิ่ม `initializePomodoro()` function**
- ✅ **รองรับ fragment loading**
- ✅ **Fallback initialization**
- ✅ **Multiple initialization methods**

#### **2. Fragment Integration**
- ✅ **เพิ่ม script ใน fragment**
- ✅ **Immediate initialization**
- ✅ **DOM ready fallback**
- ✅ **Console logging**

## 🚀 **การใช้งาน:**

### **1. เข้าใช้งาน**
- กด "Pomodoro" ใน navbar
- ใช้ fragment system

### **2. Debug Steps**
1. **เปิด Developer Tools** (F12)
2. **ดู Console** สำหรับ error messages
3. **ตรวจสอบ** `window.pomodoro` object
4. **ทดสอบ** button clicks

### **3. Expected Console Output**
```
🍅 Simple Pomodoro Timer loaded!
```
หรือ
```
🍅 Simple Pomodoro Timer loaded via fragment!
```

## 🔍 **Troubleshooting:**

### **ถ้ากดปุ่มแล้วไม่มีอะไรเกิดขึ้น:**

#### **1. ตรวจสอบ Console**
- เปิด Developer Tools (F12)
- ดู Console tab
- หา error messages

#### **2. ตรวจสอบ JavaScript Loading**
```javascript
// ใน Console พิมพ์:
console.log(window.pomodoro);
// ควรเห็น SimplePomodoro object
```

#### **3. ตรวจสอบ Button Events**
```javascript
// ใน Console พิมพ์:
document.getElementById('start-btn');
// ควรเห็น button element
```

#### **4. Manual Test**
```javascript
// ใน Console พิมพ์:
window.pomodoro.start();
// ควรเริ่ม timer
```

## 🎯 **Features ที่ควรทำงาน:**

### **✅ Controls**
- **Start**: เริ่ม 25-minute focus session
- **Pause**: หยุดชั่วคราว
- **Resume**: เริ่มต่อ
- **Reset**: รีเซ็ตเป็น 25:00

### **✅ Quick Actions**
- **Focus (25min)**: ตั้งเป็น focus mode
- **Short Break (5min)**: ตั้งเป็น short break
- **Long Break (15min)**: ตั้งเป็น long break

### **✅ Automatic Features**
- **Auto-break**: เริ่ม break อัตโนมัติหลัง focus
- **Session counter**: นับ sessions (0/4)
- **Long break**: ทุก 4 sessions = 15-minute break
- **Notifications**: แจ้งเตือนด้วยเสียงและภาพ

## 🚀 **Ready to Test!**

**ลองกด "Pomodoro" ใน navbar แล้วดู Console ว่ามี error หรือไม่!** 🍅✨
