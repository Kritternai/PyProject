
<div align="center">

# 🎓 EduMatch

**ระบบค้นหาและจับคู่ Study Group อัจฉริยะ**

<p>
  <img alt="Python" src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" />
  <img alt="FastAPI" src="https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white" />
  <img alt="TailwindCSS" src="https://img.shields.io/badge/Tailwind_CSS-38B2AC?style=for-the-badge&logo=tailwind-css&logoColor=white" />
  <img alt="JavaScript" src="https://img.shields.io/badge/JavaScript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black" />
</p>

แพลตฟอร์มสำหรับนักศึกษาเพื่อค้นหาและสร้างกลุ่มติวหนังสือ แก้ปัญหาการหาเพื่อนติวและการนัดหมายที่ยุ่งยาก

_โปรเจคนี้เป็นส่วนหนึ่งของรายวิชา Software Design and Development 2_

</div>

---

## ✨ **คุณสมบัติหลัก (Core Features)**

- **การจัดการโปรไฟล์:** สร้างโปรไฟล์และกำหนดตารางเวลาว่างของตนเอง
- **การจัดการกลุ่ม:** สร้างและบริหารจัดการกลุ่มติวของตนเอง
- **ค้นหากลุ่ม:** ค้นหากลุ่มติวจากรหัสวิชาหรือชื่อกลุ่ม
- **การจับคู่อัจฉริยะ:** รับคำแนะนำกลุ่มที่เหมาะสมโดยอิงจากตารางเวลาที่ตรงกัน

---

## 🚀 **เริ่มต้นใช้งาน (Getting Started)**

### **Prerequisites**
- [Python 3.10+](https://www.python.org/)
- [Node.js 18.0+](https://nodejs.org/)

### **Installation & Running**

1.  **Clone a โปรเจค**
    ```bash
    git clone https://github.com/[your-username]/EduMatch.git
    cd EduMatch
    ```

2.  **รัน Backend (ใน Terminal ที่ 1)**
    ```bash
    # เข้าไปที่โฟลเดอร์ backend และติดตั้ง dependencies
    cd backend
    pip install -r ../requirements.txt

    # รัน API server
    uvicorn main:app --reload
    ```
    > 🚀 Backend จะทำงานที่ `http://127.0.0.1:8000`

3.  **รัน Frontend (ใน Terminal ที่ 2)**
    ```bash
    # ติดตั้ง dependencies และ build CSS
    npm install
    npm run watch
    ```
    > 🌍 เปิดไฟล์ `frontend/index.html` บนเบราว์เซอร์เพื่อดูหน้าเว็บ

---

## 🛠️ **เทคโนโลยีที่ใช้ (Tech Stack)**

- **Backend:** Python, FastAPI, SQLAlchemy
- **Frontend:** HTML, Tailwind CSS, Vanilla JavaScript
- **Database:** SQLite
- **Deployment:** Render.com

<br>

<div align="center">
  * Made on Earth by humans *
</div>
