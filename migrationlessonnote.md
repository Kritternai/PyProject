# 📝 บันทึกการรวมระบบโน้ต (Note Feature Migration)

เอกสารนี้สรุปขั้นตอนการรวมระบบจัดการโน้ตจากโปรเจกต์ย่อย (`PyProject-dev-web-note`) เข้ามาเป็นส่วนหนึ่งของโปรเจกต์หลัก (`PyProject-3`)

## 1. ภาพรวมและเป้าหมาย

เป้าหมายหลักคือการนำฟีเจอร์การสร้างและจัดการโน้ต (ซึ่งมีการเก็บข้อความ, รูปภาพ, ไฟล์แนบ, แท็ก, สถานะ) เข้ามารวมกับระบบจัดการบทเรียน (Lesson) ที่มีอยู่แล้ว โดยต้องการให้เป็นฟีเจอร์ที่แยกเป็นสัดส่วนและใช้งานง่ายผ่านแถบนำทางหลัก (Navbar)

## 2. การรวมโครงสร้างข้อมูล (Model Merging)

เพื่อรักษาโครงสร้างข้อมูลให้เป็นหนึ่งเดียว แทนที่จะสร้างตาราง `Note` ใหม่ เราได้ตัดสินใจขยายความสามารถของตาราง `LessonSection` ที่มีอยู่แล้ว

- **ไฟล์ที่แก้ไข:** `/Users/kbbk/PyProject-3/app/core/lesson.py`
- **การเปลี่ยนแปลง:** เพิ่มคอลัมน์ใหม่เข้าไปในคลาส `LessonSection` เพื่อให้สามารถเก็บข้อมูลเฉพาะของโน้ตได้ ดังนี้:
  - `body` (Text): เนื้อหาหลักของโน้ต
  - `image_path` (String): ที่อยู่ของไฟล์รูปภาพ
  - `external_link` (String): ลิงก์ภายนอก
  - `tags` (String): แท็กของโน้ต (เก็บในรูปแบบข้อความ)
  - `status` (String): สถานะของโน้ต (e.g., 'pending', 'completed')

## 3. การรวมตรรกะการจัดการ (Manager Logic)

เราได้ปรับปรุง `LessonManager` ให้สามารถจัดการข้อมูลใหม่ของโน้ตได้โดยตรง ทำให้ไม่จำเป็นต้องมี `NoteManager` แยกต่างหาก

- **ไฟล์ที่แก้ไข:** `/Users/kbbk/PyProject-3/app/core/lesson_manager.py`
- **การเปลี่ยนแปลง:**
  - อัปเดตเมธอด `add_section` และ `update_section` ให้รับพารามิเตอร์ใหม่ (`body`, `image_path`, `external_link`, `tags`, `status`) และบันทึกลงในอ็อบเจกต์ `LessonSection`

## 4. การรวมหน้าเว็บและเส้นทาง (Templates & Routes)

- **คัดลอก Templates:**
  - **ที่มา:** `/Users/kbbk/PyProject-3/PyProject-dev-web-note/app/templates/notes/`
  - **ปลายทาง:** `/Users/kbbk/PyProject-3/app/templates/notes/`
  - **เหตุผล:** นำไฟล์ HTML สำหรับฟอร์มการสร้างและแก้ไขโน้ตมาใช้ในโปรเจกต์หลัก

- **สร้างหน้า "All Notes" (Standalone Note Feature):**
  - **ไฟล์ที่สร้าง:** `/Users/kbbk/PyProject-3/app/templates/note_fragment.html`
  - **ไฟล์ที่แก้ไข:** `/Users/kbbk/PyProject-3/app/routes.py`
  - **การเปลี่ยนแปลง:**
    1.  เพิ่ม Route ใหม่ `/partial/note` เพื่อเป็นหน้าหลักสำหรับแสดงโน้ตทั้งหมดของผู้ใช้ โดยดึง `LessonSection` ทุกอันที่มี `type='note'`
    2.  สร้าง `note_fragment.html` เพื่อแสดงผลโน้ตทั้งหมดในรูปแบบ Card View

## 5. การสร้างระบบเพิ่มโน้ตแบบ Standalone ผ่าน Modal

เพื่อให้ผู้ใช้สามารถเพิ่มโน้ตจากหน้า "All Notes" ได้โดยตรงและมี UX ที่ดี เราได้สร้างระบบ Modal ขึ้นมา

- **ไฟล์ที่แก้ไข:**
  - `/Users/kbbk/PyProject-3/app/templates/note_fragment.html`: เพิ่มโครงสร้าง Bootstrap Modal และเปลี่ยนปุ่ม "Add New Note" ให้เรียกใช้ Modal
  - `/Users/kbbk/PyProject-3/app/static/js/main.js`:
    - เพิ่มฟังก์ชัน `setupNoteForms()` ที่ดัดแปลงมาจาก `setupSectionForms()` เพื่อจัดการการเปิด Modal และส่งข้อมูลฟอร์มผ่าน AJAX โดยเฉพาะ
    - เรียกใช้ `setupNoteForms()` เมื่อมีการโหลดหน้าใหม่
  - `/Users/kbbk/PyProject-3/app/routes.py`:
    - สร้าง Route `/partial/note/add` สำหรับจัดการการเพิ่มโน้ต
    - **Logic สำคัญ:** เมื่อผู้ใช้สร้างโน้ตจากหน้านี้ ระบบจะค้นหาหรือสร้าง "Lesson" พิเศษชื่อ **"General Notes"** ขึ้นมาโดยอัตโนมัติเพื่อใช้เก็บโน้ตเหล่านี้ ทำให้เข้ากับโครงสร้างข้อมูลเดิมได้
    - เมื่อบันทึกสำเร็จ Route จะส่งคืนเป็น JSON response ที่มี HTML fragment ของรายการโน้ตที่อัปเดตแล้วกลับไปให้ JavaScript แสดงผล

## 6. การแก้ไขข้อผิดพลาด (Troubleshooting)

- **`NameError: name 'LessonSection' is not defined`**:
  - **ไฟล์:** `app/routes.py`
  - **วิธีแก้:** เพิ่ม `LessonSection` เข้าไปในคำสั่ง import

- **`TypeError: object of type 'NoneType' has no len()`**:
  - **ไฟล์:** `app/templates/note_fragment.html`
  - **วิธีแก้:** แก้ไขการแสดงผล `note.body` เป็น `(note.body or '')` เพื่อป้องกัน error กรณีที่เนื้อหาเป็นค่าว่าง

- **`sqlite3.OperationalError: no such column: lesson_section.tags`**:
  - **สาเหตุ:** Schema ของ Model ในโค้ดไม่ตรงกับ Schema ของตารางในฐานข้อมูล `site.db`
  - **วิธีแก้:** เนื่องจากไม่มีระบบ Database Migration, จึงทำการลบไฟล์ฐานข้อมูลเดิม (`/Users/kbbk/PyProject-3/instance/site.db`) เพื่อให้ Flask-SQLAlchemy สร้างฐานข้อมูลขึ้นมาใหม่ตาม Schema ล่าสุดเมื่อรันแอปพลิเคชันอีกครั้ง
