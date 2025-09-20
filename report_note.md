## UI/UX Notes (Bootstrap 5 + Glass/Neo) — 2025-09-20

### เพิ่ม (Added)
- โมดอล Note แบบ Glassmorphism/Neumorphism (`modal-glass`, `btn-soft`, `glass-section`) พร้อมไอคอน Bootstrap Icons และสีแบรนด์ (`--slh-primary`, `--slh-primary-2`, `--slh-primary-3`).
- Header แบบ Hero (ไอคอน + ชื่อเรื่อง + subtitle) และจัด `modal-dialog-centered modal-dialog-scrollable` ให้ใช้งานง่ายบนหน้าจอเล็ก/ยาว.
- Toolbar ด้านบนหน้ารายการ: ช่องค้นหา (Search) และปุ่มเพิ่มโน้ตสไตล์ลิงก์.
- แถบชิป Filter สถานะ: `All`, `Pending`, `In Progress`, `Completed` (ทำงานร่วมกับช่องค้นหาได้ทันที ไม่ต้องรีเฟรช).
- ฟังก์ชัน UX เสริมใน `note_fragment.html`:
  - Autofocus ช่อง Title เมื่อเปิดโมดอล (Add/Edit).
  - คีย์ลัด `Ctrl/Cmd + Enter` เพื่อ Submit แบบรวดเร็ว.
  - ค้นหา/กรองสถานะแบบ client-side (อ่านค่าจาก `data-status` ของการ์ด).

### แก้ไข (Changed)
- ปรับสไตล์โมดอล Add/Edit ให้เป็นกราเดียนต์สีแบรนด์, ปุ่มเป็น pill + soft shadow, badge สถานะเป็น pill.
- ปรับฟอร์มภายในให้มีพื้นหลังโปร่งใสแบบ glass และกรอบมนใหญ่ เพื่อความอ่านง่าย.
- ปรับปุ่ม Edit/Delete และการ์ดโน้ตเป็น `neo-card` (soft elevation + hover lift).

### ลบ (Removed)
- ลบแท็บปุ่ม (Info/Notes/Media) ใต้หัวโมดอลเพื่อให้หน้าตาเรียบง่ายและโฟกัสที่การกรอกข้อมูล.

### ไฟล์ที่เปลี่ยนแปลง
- `app/templates/note_fragment.html` (เพิ่ม/แก้ไขโครงสร้างโมดอล, toolbar, ชิป filter, CSS และ JS ฝังหน้า)
- `app/templates/notes/list.html` (เพิ่มสไตล์ glass/neo สำหรับโมดอลอย่างย่อ)

### ผลลัพธ์
- ผู้ใช้สามารถค้นหา + กรองสถานะโน้ตได้ทันทีบนหน้าเดียว, โมดอลใช้งานง่ายขึ้น (โฟกัสอัตโนมัติ, คีย์ลัด), และภาพรวม UI เข้ากับ Bootstrap 5/สีประจำโปรเจกต์.

## รายงานการแก้ไขฟีเจอร์ Note: การลบแล้วโหลดหน้ารายการใหม่ทันที

### สรุปปัญหา
- เมื่อผู้ใช้กดลบโน้ตจากหน้า Note รายการโน้ตไม่ได้รีเฟรชทันทีในหน้าเดียวกัน เพราะฝั่งไคลเอนต์ไม่ได้ส่งหัวข้อ AJAX ทำให้เซิร์ฟเวอร์ไม่ส่ง HTML fragment ของรายการโน้ตกลับมา

### สาเหตุ
- ฟังก์ชันลบโน้ตบนไคลเอนต์ (`window.deleteNote`) เรียก `fetch` แบบ POST โดยไม่มี header `X-Requested-With: XMLHttpRequest`
- ที่ฝั่งเซิร์ฟเวอร์ (`/partial/note/<note_id>/delete`) จะส่ง fragment (`note_fragment.html`) กลับก็ต่อเมื่อเป็นคำขอแบบ AJAX เท่านั้น

### แนวทางแก้ไข
- เพิ่ม header `X-Requested-With: XMLHttpRequest` ในคำขอ `fetch` ของฟังก์ชัน `window.deleteNote`

### ไฟล์ที่แก้ไข
- `app/static/js/main.js`

การแก้ไขที่สำคัญ:
```diff
window.deleteNote = function(noteId) {
  if (confirm('Are you sure you want to delete this note?')) {
    fetch(`/partial/note/${noteId}/delete`, {
      method: 'POST',
 +    headers: {
 +      'X-Requested-With': 'XMLHttpRequest'
 +    }
    })
    .then(response => response.text())
    .then(html => {
      document.getElementById('note-list-container').outerHTML = html;
    })
  }
};
```

### ผลลัพธ์หลังแก้ไข
- เมื่อกดยืนยันการลบ โน้ตจะถูกลบ และรายการโน้ตในหน้าเดียวกันจะอัปเดตทันที โดยไม่ต้องรีเฟรชทั้งหน้า

### ขั้นตอนทดสอบ (Manual)
1. ล็อกอินเข้าสู่ระบบ
2. ไปที่เมนู Note (sidebar)
3. คลิกปุ่ม Delete บนการ์ดโน้ตใดๆ และยืนยัน
4. คาดหวัง: รายการโน้ตรีเฟรชทันที และโน้ตที่ถูกลบหายไปจากรายการ

### ความเสี่ยง/ผลกระทบ
- มีผลเฉพาะพฤติกรรมการลบโน้ตบนหน้า Note ไม่กระทบฟังก์ชันอื่น
- ต้องแน่ใจว่า endpoint ฝั่งเซิร์ฟเวอร์ยังส่ง fragment เมื่อมี header AJAX (ปัจจุบันรองรับแล้วใน `app/routes_new.py`)

### วิธี Rollback
- ย้อนการแก้ไขไฟล์ `app/static/js/main.js` ไปเวอร์ชันก่อนหน้า (นำ header `X-Requested-With` ออก)

### การเตรียมสำหรับ OOP / Clean Architecture
- ใช้ Service ชั้นธุรกิจสำหรับโน้ตแล้ว: `NoteService` ถูกเรียกใช้ใน `partial_note_add`, `partial_note_edit`, `partial_note_delete` เพื่อสร้าง/แก้ไข/ลบ (ครอบคลุมการตรวจสิทธิ์และกฎธุรกิจใน `NoteServiceImpl`).
- เส้นทาง API มาตรฐานพร้อมแล้ว: `presentation/routes/note_routes.py` ครอบคลุม CRUD และการค้นหาแบบ REST (`/api/notes/...`) สำหรับการใช้งานฝั่ง SPA/ไคลเอนต์อื่นในอนาคตได้ทันที
- ส่วนที่ยังเป็น Legacy และแผนจัดระเบียบ:
  - ฟิลด์เสริม (`status`, `external_link`) ยังอัปเดตผ่าน SQL ตรงใน `routes_new.py` เพราะไม่อยู่ใน Domain `Note`; ควรพิจารณา:
    1) เพิ่มใน Domain/Model อย่างเป็นทางการ หรือ 2) แยกเป็น `NoteMeta` repository/service เฉพาะเมตาดาตา แล้วเปลี่ยน partial routes ให้เรียก service แทน SQL ตรง
  - การแนบไฟล์ยังใช้ `app.core.files.Files` โดยตรงผ่าน `_save_note_uploads(...)`; ควรค่อยๆ ย้ายไป service/repository ฝั่ง infrastructure (เช่น `FileRepository`/`FileService`) เพื่อให้ทดสอบง่ายและลดการผูกกับ ORM ในชั้น presentation
- แนวทางปรับให้สอดคล้อง OOP เพิ่มเติม (ไม่ breaking):
  - คง partial routes ใน `routes_new.py` แต่ลดการเรียก DB ตรงให้เหลือเฉพาะผ่าน service ทีละกรณี
  - รวม view logic สำหรับ fragment ให้เรียก controller ใน `presentation/controllers/note_controller.py` (เพิ่มเมธอดสำหรับคืน fragment เมื่อจำเป็น) เพื่อรวมศูนย์กฎธุรกิจ/response shape
  - เพิ่ม unit test ระดับ service สำหรับ `delete_note` และเคสสิทธิ์ผู้ใช้ เพื่อการันตีพฤติกรรมเมื่อย้าย logic ออกไปจาก presentation

## แก้ไขปัญหา Database Initialization (NoReferencedTableError)

### อาการ
- ระหว่างรัน `create_all()` (เช่นจาก `run_new.py` หรือสคริปต์เริ่มระบบ) เกิดข้อผิดพลาด:
  - `sqlalchemy.exc.NoReferencedTableError: Foreign key associated with column 'files.section_id' could not find table 'lesson_section' ...`

### สาเหตุ
- ตาราง `lesson_section` ไม่ถูกประกาศ/โหลดในฝั่ง Infrastructure ตอนเริ่มแอป ทำให้ SQLAlchemy สร้างตาราง `files` ไม่ได้ (เพราะมี FK อ้างถึง `lesson_section`).
- ใน `app/__init__.py:import_models()` เดิมมีการ import เฉพาะ `UserModel`, `LessonModel`, `NoteModel`, `TaskModel` แต่ไม่มีตาราง `lesson_section` ให้สร้างก่อน

### แนวทางแก้ไข
- เพิ่มโมเดลสำหรับตาราง `lesson_section` ฝั่ง Infrastructure (minimal schema) และ import ระหว่าง startup:
  - เพิ่มไฟล์: `app/infrastructure/database/models/lesson_section_model.py`
  - แก้ `app/__init__.py` ให้ import โมเดลนี้ในฟังก์ชัน `import_models()`

สรุปการแก้ไขที่สำคัญ (diff โดยสรุป):
```diff
# app/__init__.py (ฟังก์ชัน import_models)
-    from .infrastructure.database.models.lesson_model import LessonModel
+    from .infrastructure.database.models.lesson_model import LessonModel
+    from .infrastructure.database.models.lesson_section_model import LessonSectionModel
     from .infrastructure.database.models.note_model import NoteModel
     from .infrastructure.database.models.task_model import TaskModel
```

ไฟล์ใหม่ (สรุป): `app/infrastructure/database/models/lesson_section_model.py`
- `__tablename__ = 'lesson_section'`
- ฟิลด์หลัก: `id`, `lesson_id (FK -> lesson.id)`, `title`, `content`, `section_type`, `order_index`, `created_at`, `updated_at`

### ผลลัพธ์หลังแก้ไข
- รัน `db.create_all()` สำเร็จ โดย FK ของ `files.section_id` ถูก resolve ได้แล้วเพราะมีตาราง `lesson_section` ถูกประกาศก่อน

### หมายเหตุสำหรับ Windows (start script)
- การใช้ `python -c` แบบหลายบรรทัดผ่าน `subprocess.run` บน Windows อาจล้มเหลว แนะนำใช้คำสั่ง one-liner หรือพิมพ์ `stdout/stderr` เมื่อเกิด `CalledProcessError` เพื่อช่วยวิเคราะห์ปัญหา

### วิธี Rollback (ส่วนนี้ของ DB)
- ลบไฟล์ `app/infrastructure/database/models/lesson_section_model.py`
- ลบบรรทัด import `LessonSectionModel` ใน `app/__init__.py`
