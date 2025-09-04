# สรุปการพัฒนาเบื้องต้น: Smart Learning Hub (Python Flask Web Application)

เอกสารนี้สรุปขั้นตอนและสถานะการพัฒนาโปรเจกต์ **Smart Learning Hub** ซึ่งเป็นเว็บแอปพลิเคชันที่พัฒนาด้วย **Python** และ **Flask** โดยมีเป้าหมายเพื่อเป็นระบบจัดการการเรียนรู้ส่วนบุคคลแบบครบวงจร รองรับการเชื่อมต่อกับ Google Classroom, การนำเข้าข้อมูลจาก MS Teams/KMITL ผ่าน Chrome Extension และมี UI ที่ทันสมัยด้วย Tailwind CSS

---

## 1. โครงสร้างโปรเจกต์และเทคโนโลยีที่ใช้

- **Backend:** Python 3.x, Flask, Flask-SQLAlchemy, SQLite, Google API Client
- **Frontend:** Jinja2 Template, Tailwind CSS, Bootstrap, Vanilla JS, FontAwesome
- **Dev Tools:** Git, GitHub, Node.js + npm (สำหรับ Tailwind), PostCSS, Chrome Extension
- **Integration:** Google Classroom API (OAuth2), Chrome Extension (MS Teams, KMITL)
- **แนวคิด:** Object-Oriented Programming (OOP), Modular, Kanban Workflow

### โครงสร้างโฟลเดอร์หลัก
- `app/` — โค้ด Flask, core modules, templates, static
- `chrome_extension/` — ส่วนขยายเบราว์เซอร์สำหรับดึงข้อมูลภายนอก
- `docs/` — เอกสารโครงการ (Proposal, Roadmap, Backlog, Retrospective ฯลฯ)
- `requirements.txt`, `package.json`, `tailwind.config.js` — ไฟล์ config และ dependencies

---

## 2. ฟีเจอร์หลักที่พัฒนาแล้ว/กำลังพัฒนา

- **User System:** สมัคร, ล็อกอิน, โปรไฟล์, Google OAuth
- **Lesson Manager:** สร้าง/แก้ไข/ลบบทเรียน, หมวดหมู่, สถานะ, เชื่อม Google Classroom
- **Note System:** จดบันทึก Markdown, ค้นหา, เชื่อมโยงกับบทเรียน
- **Task & To-Do:** (อยู่ระหว่างพัฒนา) สร้างงาน, Due Date, แจ้งเตือน
- **Pomodoro Timer:** (อยู่ระหว่างพัฒนา) ตัวจับเวลาโฟกัส
- **Progress Tracker:** Dashboard, สถิติ, รายงานความก้าวหน้า
- **Chrome Extension:** ดึงข้อมูลจาก MS Teams, KMITL, ส่งเข้า Flask Backend
- **Google Classroom Integration:** ดึงรายวิชา/งาน/ไฟล์/ประกาศ

---

## 3. การพัฒนา UI ด้วย Tailwind CSS

- ใช้ Tailwind CSS ผ่าน npm + watcher (`npm run tailwind:watch`)
- ปรับปรุง Jinja2 Template ให้รองรับ responsive, modern UI
- ใช้ Bootstrap/FontAwesome เสริมในบางส่วน

---

## 4. การเชื่อมต่อภายนอกและ Data Flow

- **Google Classroom:** OAuth2, ดึงข้อมูลรายวิชา/งาน/ไฟล์/ประกาศ, mapping กับ Lesson
- **Chrome Extension:** ดึงข้อมูลจาก MS Teams/KMITL, ส่งผ่าน API `/api/import_data` ไปยัง Flask
- **ฐานข้อมูล:** ใช้ SQLite (ผ่าน SQLAlchemy) สำหรับเก็บผู้ใช้, บทเรียน, บันทึก ฯลฯ

---

## 5. วิธีการรันโปรเจกต์ (อัปเดตล่าสุด)

1. ติดตั้ง Python, Node.js, npm
2. สร้าง Virtual Environment, ติดตั้ง dependencies (`requirements.txt`)
3. ติดตั้ง Tailwind CSS (`npm install`)
4. รัน Tailwind Watcher (`npm run tailwind:watch`)
5. รัน Flask (`flask run`)
6. เข้าถึงระบบที่ `http://127.0.0.1:5000/`

---

## 6. แนวทางการพัฒนาต่อ/สิ่งที่อยู่ใน Backlog

- พัฒนา Task Manager, Pomodoro Timer, Progress Tracker ให้สมบูรณ์
- เพิ่มระบบแจ้งเตือน, Export ข้อมูล, AI Assistant, Advanced Security
- ขยาย Chrome Extension ให้รองรับ platform เพิ่มเติม
- ปรับปรุงเอกสารและ Unit Test ให้ครอบคลุม

---

*หมายเหตุ: เอกสารนี้จะถูกอัปเดตเมื่อมีการเปลี่ยนแปลงโครงสร้างหรือฟีเจอร์สำคัญในโปรเจกต์*
