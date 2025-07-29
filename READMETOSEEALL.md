# 📚 Smart Learning Hub (Google Classroom-like LMS)

---

## 🇹🇭 สารบัญ (ภาษาไทย)
- [ภาพรวมโปรเจกต์](#ภาพรวมโปรเจกต์)
- [เทคโนโลยีที่ใช้ (Tech Stack)](#เทคโนโลยีที่ใช้-tech-stack)
- [โครงสร้างโปรเจกต์โดยละเอียด](#โครงสร้างโปรเจกต์โดยละเอียด)
- [โมเดลฐานข้อมูลและโค้ด Backend](#โมเดลฐานข้อมูลและโค้ด-backend)
- [ระบบ SPA และ JavaScript](#ระบบ-spa-และ-javascript)
- [โครงสร้าง Template และ UI/UX](#โครงสร้าง-template-และ-uiux)
- [Google Classroom Integration](#google-classroom-integration)
- [CSS และการปรับแต่ง UI](#css-และการปรับแต่ง-ui)
- [วิธีติดตั้งและใช้งาน](#วิธีติดตั้งและใช้งาน)
- [License](#license)

---

## Project Overview (English)
- [Project Overview](#project-overview)
- [Tech Stack](#tech-stack)
- [Detailed Project Structure](#detailed-project-structure)
- [Database Models & Backend Code](#database-models--backend-code)
- [SPA System & JavaScript](#spa-system--javascript)
- [Template Structure & UI/UX](#template-structure--uiux)
- [Google Classroom Integration](#google-classroom-integration-1)
- [CSS & UI Customization](#css--ui-customization)
- [How to Run](#how-to-run)
- [License](#license-1)

---

# 🇹🇭 ภาพรวมโปรเจกต์

**Smart Learning Hub** คือเว็บแอปพลิเคชัน LMS ที่จำลองประสบการณ์ Google Classroom อย่างครบถ้วน รองรับการจัดการบทเรียน (Class/Lesson) และเนื้อหาย่อย (Section/Content) แบบ SPA (Single Page Application) ที่ลื่นไหล UI/UX สวยงาม Responsive ด้วย Bootstrap 5 และ

**จุดเด่น:**
- SPA: ทุก action (add/edit/delete/view) ทำผ่าน AJAX/Fetch API, ไม่รีเฟรชหน้า
- Sidebar Navigation แบบ Google Classroom
- ระบบล็อกอิน/สมัคร/โปรไฟล์/เปลี่ยนรหัสผ่าน (local)
- CRUD บทเรียน (Class/Lesson) และเนื้อหา (Section) หลายประเภท (Text, File, Assignment, Note)
- อัปโหลดไฟล์ (หลายไฟล์), แสดง preview รูป/ PDF ใน card
- ฟิลเตอร์เนื้อหาแบบเรียลไทม์ (ประเภท, คำค้น, วันครบกำหนด)
- เชื่อมต่อและแสดงข้อมูล Google Classroom API

---

## เทคโนโลยีที่ใช้ (Tech Stack)
- **Backend:** Python 3, Flask, Flask-SQLAlchemy, SQLite
- **Frontend:** Bootstrap 5, Tailwind CSS, Vanilla JS (Fetch API), SPA logic
- **3rd-party:** Google Classroom API, Google Drive API
- **Dev Tools:** npm, PostCSS

---

## โครงสร้างโปรเจกต์โดยละเอียด

- `/` (Root):
    - `run.py`, `start_flask.sh`, `requirements.txt`, `package.json`, `LICENSE`, `README.md`
- `app/` (Flask App):
    - `__init__.py`: กำหนด config, สร้าง Flask app, SQLAlchemy, import models, load routes
    - `routes.py`: รวมทุก route (SPA partial, auth, CRUD, Google Classroom, integration)
    - `core/`: Business logic (user, lesson, section, Google API, ...)
        - `user.py`, `user_manager.py`, `authenticator.py`: User model, CRUD, Auth
        - `lesson.py`, `lesson_manager.py`: Lesson, LessonSection model, CRUD, import Google Classroom
        - `imported_data.py`: เก็บข้อมูลที่ import จาก Google Classroom/MS Teams
        - `google_credentials.py`: เก็บ OAuth token Google
        - `course_linkage.py`, `course_linkage_manager.py`: Mapping วิชา KMITL กับ Google Classroom
    - `static/`: CSS, JS, uploads
        - `js/main.js`: SPA logic, form handler, modal, filter, partial loader
        - `css/custom.css`, `css/tailwind.css`: ปรับแต่ง UI, สี, Responsive
        - `uploads/`: ไฟล์ที่อัปโหลดโดยผู้ใช้
    - `templates/`: HTML (Jinja2) templates (base, lessons, auth, ...)
        - `base.html`: Layout หลัก, sidebar, SPA loader
        - `class_fragment.html`, `dashboard_fragment.html`, ...: SPA partials
        - `lessons/`: ฟอร์ม/หน้ารายละเอียด/section CRUD
        - `google_classroom/`, `integrations/`, `external_data/`: Integration templates

---

## โมเดลฐานข้อมูลและโค้ด Backend

### User (app/core/user.py)
- `id`, `username`, `email`, `password_hash`
- Method: `set_password`, `check_password`

### UserManager (app/core/user_manager.py)
- CRUD user, ตรวจสอบซ้ำ, อัปเดต username/email/password

### Authenticator (app/core/authenticator.py)
- `login(username, password)`: ตรวจสอบรหัสผ่าน
- `register(username, email, password)`: สมัครใหม่

### Lesson (app/core/lesson.py)
- `id`, `title`, `description`, `status`, `tags`, `user_id`, ...
- Google Classroom fields: `google_classroom_id`, `source_platform`, `announcements_data`, `topics_data`, `roster_data`, `attachments_data`
- Relationship: `sections` (LessonSection)

### LessonSection (app/core/lesson.py)
- `id`, `lesson_id`, `title`, `content`, `type`, `file_urls` (JSON), `assignment_due`, ...
- รองรับหลายประเภท: text, file, assignment, note

### LessonManager (app/core/lesson_manager.py)
- CRUD Lesson/Section, import Google Classroom, update fields, multi-file upload
- Method: `add_lesson`, `get_lesson_by_id`, `get_lessons_by_user`, `update_lesson`, `delete_lesson`, `add_section`, `get_sections`, `get_section_by_id`, `update_section`, `delete_section`

### ImportedData (app/core/imported_data.py)
- เก็บ JSON data ที่ import จาก Google Classroom/MS Teams

### GoogleCredentials (app/core/google_credentials.py)
- เก็บ OAuth token, refresh_token, client_id, client_secret, scopes

### CourseLinkage (app/core/course_linkage.py)
- Mapping วิชา KMITL กับ Google Classroom

### CourseLinkageManager (app/core/course_linkage_manager.py)
- CRUD linkage, ลบ/เพิ่ม/อัปเดต mapping

### routes.py (app/routes.py)
- SPA partial routes: `/partial/class`, `/partial/class/<lesson_id>`, `/partial/class/<lesson_id>/sections`, ...
- Auth: `/partial/login`, `/partial/register`, `/partial/profile`, `/partial/change_password`, `/logout`
- Google Classroom: `/google_classroom/authorize`, `/google_classroom/oauth2callback`, `/google_classroom/fetch_data`, ...
- Integration: `/integrations/kmitl_classroom_link`, ...
- Jinja2 filter: `@app.template_filter('loads')` สำหรับ parse JSON ใน template

---

## ระบบ SPA และ JavaScript

### main.js (app/static/js/main.js)
- `loadPage(page)`: โหลด partial fragment ด้วย fetch, inject HTML, re-bind event
- `updateSidebarAuth()`: อัปเดต sidebar auth section หลัง login/logout
- `setupAuthForms()`: จัดการฟอร์ม login/register/change password (AJAX)
- `setupLessonForms()`, `setupLessonEditForm()`: ฟอร์มเพิ่ม/แก้ไข lesson (AJAX)
- `setupSectionForms()`: Modal + ฟอร์มเพิ่ม section, toggle field ตาม type, multi-file upload, client-side validation
- `setupSectionFilter()`: ฟิลเตอร์ section ตาม type, keyword, due date (real-time)
- `window.editSection`, `window.deleteSection`: SPA CRUD section (inline edit, AJAX delete)
- SPA navigation: ทุก action ไม่ reload หน้า, ใช้ JSON response/HTML fragment

---

## โครงสร้าง Template และ UI/UX

### base.html
- Layout หลัก, sidebar ซ้ายมือ, responsive, SPA loader, dynamic sidebar-auth

### class_fragment.html
- Card-based lesson list, ปุ่ม + เพิ่มวิชา, responsive grid

### lessons/_detail.html
- Tabs: Overview, Content, Google Classroom
- Content tab: Add Content (Modal), section list (card), filter UI
- Google Classroom tab: แสดงข้อมูลที่ import (announcements, topics, roster, attachments)

### lessons/section_list.html
- Card-based section list, icon/type, in-card preview (image, PDF, download), Edit/Delete (SPA)

### lessons/section_add.html, section_edit.html
- ฟอร์มเพิ่ม/แก้ไข section (fragment, inject ด้วย JS)

### sidebar_auth_fragment.html
- SPA partial สำหรับ auth section ใน sidebar (login/register/logout/profile)

---

## Google Classroom Integration
- OAuth2 flow (`google_classroom/authorize`, `oauth2callback`)
- ดึงข้อมูล course, assignment, material, roster, attachment จาก Google Classroom API
- Import เป็น Lesson/Section, mapping กับ user
- เก็บ token ใน GoogleCredentials, ข้อมูลใน ImportedData
- UI: Google Classroom tab ใน lesson, แสดงข้อมูลแบบ card/tab/accordion

---

## CSS และการปรับแต่ง UI
- Bootstrap 5: ใช้ทุก component หลัก (card, modal, tab, form, grid)

---

## วิธีติดตั้งและใช้งาน
1. **Clone repo:**
   ```bash
   git clone ...
   cd PyProject-3
   ```
2. **ติดตั้ง Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
3. **ติดตั้ง Frontend dependencies (optional):**
   ```bash
   npm install
   npm run tailwind:watch # ถ้าใช้ Tailwind
   ```
4. **ตั้งค่า env:**
   - สร้างไฟล์ `.env` หรือ export ตัวแปร env (ดูใน `app/__init__.py`)
5. **รันแอป:**
   ```bash
   python run.py
   # หรือ
   ./start_flask.sh
   ```
6. **เข้าใช้งาน:**
   - เปิด browser ไปที่ `http://localhost:5000`

---

## License
MIT License

---

# 🇬🇧 Project Overview

**Smart Learning Hub** is a modern, Google Classroom-inspired LMS web application. It features a beautiful, responsive UI, SPA navigation, robust local authentication, dynamic lesson/class and section/content management, file uploads with preview, real-time filtering, and seamless Google Classroom API integration.

---

## Tech Stack
- **Backend:** Python 3, Flask, Flask-SQLAlchemy, SQLite
- **Frontend:** Bootstrap 5, Tailwind CSS, Vanilla JS (Fetch API), SPA logic
- **3rd-party:** Google Classroom API, Google Drive API
- **Dev Tools:** npm, PostCSS

---

## Detailed Project Structure

- `/` (Root):
    - `run.py`, `start_flask.sh`, `requirements.txt`, `package.json`, `LICENSE`, `README.md`
- `app/` (Flask App):
    - `__init__.py`: App config, Flask/SQLAlchemy setup, model import, route loading
    - `routes.py`: All routes (SPA partials, auth, CRUD, Google Classroom, integration)
    - `core/`: Business logic (user, lesson, section, Google API, ...)
        - `user.py`, `user_manager.py`, `authenticator.py`: User model, CRUD, Auth
        - `lesson.py`, `lesson_manager.py`: Lesson, LessonSection model, CRUD, Google Classroom import
        - `imported_data.py`: Stores imported Google Classroom/MS Teams data
        - `google_credentials.py`: Stores Google OAuth tokens
        - `course_linkage.py`, `course_linkage_manager.py`: KMITL <-> Google Classroom mapping
    - `static/`: CSS, JS, uploads
        - `js/main.js`: SPA logic, form handler, modal, filter, partial loader
        - `css/custom.css`, `css/tailwind.css`: UI customization, color, responsive
        - `uploads/`: User-uploaded files
    - `templates/`: HTML (Jinja2) templates (base, lessons, auth, ...)
        - `base.html`: Main layout, sidebar, SPA loader
        - `class_fragment.html`, `dashboard_fragment.html`, ...: SPA partials
        - `lessons/`: Forms/detail/section CRUD
        - `google_classroom/`, `integrations/`, `external_data/`: Integration templates

---

## Database Models & Backend Code

### User (app/core/user.py)
- `id`, `username`, `email`, `password_hash`
- Methods: `set_password`, `check_password`

### UserManager (app/core/user_manager.py)
- CRUD user, duplicate check, update username/email/password

### Authenticator (app/core/authenticator.py)
- `login(username, password)`: Password check
- `register(username, email, password)`: Register new user

### Lesson (app/core/lesson.py)
- `id`, `title`, `description`, `status`, `tags`, `user_id`, ...
- Google Classroom fields: `google_classroom_id`, `source_platform`, `announcements_data`, `topics_data`, `roster_data`, `attachments_data`
- Relationship: `sections` (LessonSection)

### LessonSection (app/core/lesson.py)
- `id`, `lesson_id`, `title`, `content`, `type`, `file_urls` (JSON), `assignment_due`, ...
- Supports: text, file, assignment, note

### LessonManager (app/core/lesson_manager.py)
- CRUD Lesson/Section, import Google Classroom, update fields, multi-file upload
- Methods: `add_lesson`, `get_lesson_by_id`, `get_lessons_by_user`, `update_lesson`, `delete_lesson`, `add_section`, `get_sections`, `get_section_by_id`, `update_section`, `delete_section`

### ImportedData (app/core/imported_data.py)
- Stores imported JSON data from Google Classroom/MS Teams

### GoogleCredentials (app/core/google_credentials.py)
- Stores OAuth token, refresh_token, client_id, client_secret, scopes

### CourseLinkage (app/core/course_linkage.py)
- Mapping KMITL course to Google Classroom

### CourseLinkageManager (app/core/course_linkage_manager.py)
- CRUD linkage, add/update/delete mapping

### routes.py (app/routes.py)
- SPA partial routes: `/partial/class`, `/partial/class/<lesson_id>`, `/partial/class/<lesson_id>/sections`, ...
- Auth: `/partial/login`, `/partial/register`, `/partial/profile`, `/partial/change_password`, `/logout`
- Google Classroom: `/google_classroom/authorize`, `/google_classroom/oauth2callback`, `/google_classroom/fetch_data`, ...
- Integration: `/integrations/kmitl_classroom_link`, ...
- Jinja2 filter: `@app.template_filter('loads')` for JSON parsing in templates

---

## SPA System & JavaScript

### main.js (app/static/js/main.js)
- `loadPage(page)`: Loads partial fragment via fetch, injects HTML, re-binds events
- `updateSidebarAuth()`: Updates sidebar auth section after login/logout
- `setupAuthForms()`: Handles login/register/change password forms (AJAX)
- `setupLessonForms()`, `setupLessonEditForm()`: Add/edit lesson forms (AJAX)
- `setupSectionForms()`: Modal + add section form, dynamic field toggle, multi-file upload, client-side validation
- `setupSectionFilter()`: Filter section by type, keyword, due date (real-time)
- `window.editSection`, `window.deleteSection`: SPA CRUD section (inline edit, AJAX delete)
- SPA navigation: All actions without page reload, using JSON response/HTML fragment

---

## Template Structure & UI/UX

### base.html
- Main layout, left sidebar, responsive, SPA loader, dynamic sidebar-auth

### class_fragment.html
- Card-based lesson list, + add lesson button, responsive grid

### lessons/_detail.html
- Tabs: Overview, Content, Google Classroom
- Content tab: Add Content (Modal), section list (card), filter UI
- Google Classroom tab: Shows imported data (announcements, topics, roster, attachments)

### lessons/section_list.html
- Card-based section list, icon/type, in-card preview (image, PDF, download), Edit/Delete (SPA)

### lessons/section_add.html, section_edit.html
- Add/edit section forms (fragment, injected by JS)

### sidebar_auth_fragment.html
- SPA partial for sidebar auth section (login/register/logout/profile)

---

## Google Classroom Integration
- OAuth2 flow (`google_classroom/authorize`, `oauth2callback`)
- Fetches course, assignment, material, roster, attachment from Google Classroom API
- Import as Lesson/Section, mapping to user
- Stores token in GoogleCredentials, data in ImportedData
- UI: Google Classroom tab in lesson, data shown as card/tab/accordion

---

## CSS & UI Customization
- `custom.css`: Main color (blue), sidebar, card, button, responsive
- `tailwind.css`: Utility classes for layout, spacing, responsive (optional)
- Bootstrap 5: Used for all main components (card, modal, tab, form, grid)

---

## How to Run
1. **Clone repo:**
   ```bash
   git clone ...
   cd PyProject-3
   ```
2. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
3. **Install Frontend dependencies (optional):**
   ```bash
   npm install
   npm run tailwind:watch # if using Tailwind
   ```
4. **Set up env:**
   - Create `.env` or export env variables (see `app/__init__.py`)
5. **Run app:**
   ```bash
   python run.py
   # or
   ./start_flask.sh
   ```
6. **Access:**
   - Open browser at `http://localhost:5000`

---

## License
MIT License 