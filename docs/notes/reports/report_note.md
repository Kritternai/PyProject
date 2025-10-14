## UI/UX Notes (Bootstrap 5 + Glass/Neo) — 2025-09-21 (Updated)

### เพิ่ม (Added)
- โมดอล Note แบบ Glassmorphism/Neumorphism (`modal-glass`, `btn-soft`, `glass-section`) พร้อมไอคอน Bootstrap Icons และสีแบรนด์ (`--slh-primary`, `--slh-primary-2`, `--slh-primary-3`).
- Header แบบ Hero (ไอคอน + ชื่อเรื่อง + subtitle) และจัด `modal-dialog-centered modal-dialog-scrollable` ให้ใช้งานง่ายบนหน้าจอเล็ก/ยาว.
- Toolbar ด้านบนหน้ารายการ: ช่องค้นหา (Search) และปุ่มเพิ่มโน้ตสไตล์ลิงก์.
- แถบชิป Filter สถานะ: `All`, `Pending`, `In Progress`, `Completed` (ทำงานร่วมกับช่องค้นหาได้ทันที ไม่ต้องรีเฟรช).
- ฟังก์ชัน UX เสริมใน `note_fragment.html`:
  - Autofocus ช่อง Title เมื่อเปิดโมดอล (Add/Edit).
  - คีย์ลัด `Ctrl/Cmd + Enter` เพื่อ Submit แบบรวดเร็ว.
  - ค้นหา/กรองสถานะแบบ client-side (อ่านค่าจาก `data-status` ของการ์ด).
- แถบสถิติ (Statistics Row): แสดงจำนวน Total Notes, Completed, Images, Files แบบ card สไตล์ neo-morphism.
- ฟังก์ชัน `refreshNoteListPreserveFilters()` ใน `main.js`: รีโหลดรายการโน้ตหลัง Add/Edit โดยไม่สูญเสียค่าการค้นหาและกรอง.
- พื้นหลัง fallback สำหรับ note cards ที่ไม่มีรูปภาพ: ใช้ `note-cover` div พร้อมกราเดียนต์สีแบรนด์.

### แก้ไข (Changed)
- ปรับสไตล์โมดอล Add/Edit ให้เป็นกราเดียนต์สีแบรนด์, ปุ่มเป็น pill + soft shadow, badge สถานะเป็น pill.
- ปรับฟอร์มภายในให้มีพื้นหลังโปร่งใสแบบ glass และกรอบมนใหญ่ เพื่อความอ่านง่าย.
- ปรับปุ่ม Edit/Delete และการ์ดโน้ตเป็น `neo-card` (soft elevation + hover lift).
- ย้ายปุ่ม Edit/Delete ไปชิดขวาของการ์ด (`justify-content-end`).
- ปรับความสมดุลและความสดใสของ UI elements: stat cards, chips, note cards ให้ดูนุ่มนวลและใช้งานง่าย.
- แก้ไข URL รูปภาพใน Modal Edit: เปลี่ยนจาก hardcode `/static/` เป็น `{{ url_for('static', filename='') }}` เหมือน card note.
- เพิ่ม debug logging สำหรับการ parse JSON ของ images และ files ใน modal edit.

### ลบ (Removed)
- ลบแท็บปุ่ม (Info/Notes/Media) ใต้หัวโมดอลเพื่อให้หน้าตาเรียบง่ายและโฟกัสที่การกรอกข้อมูล.

### ไฟล์ที่เปลี่ยนแปลง
- `app/templates/note_fragment.html` (เพิ่ม/แก้ไขโครงสร้างโมดอล, toolbar, ชิป filter, statistics row, CSS และ JS ฝังหน้า)
- `app/templates/notes/list.html` (เพิ่มสไตล์ glass/neo สำหรับโมดอลอย่างย่อ)
- `app/static/js/main.js` (เพิ่มฟังก์ชัน search/filter และ preserve filters หลัง add/edit)

### ปัญหาที่แก้ไข
- **รูปภาพไม่แสดงใน Modal Edit**: แก้ไข URL path จาก hardcode `/static/` เป็น `{{ url_for('static', filename='') }}`
- **Search/Filter ไม่ทำงาน**: เพิ่ม event listeners และ filter logic ใน `setupNoteListFilters()`
- **สูญเสียค่า Search/Filter หลัง Add/Edit**: เพิ่มฟังก์ชัน `refreshNoteListPreserveFilters()` เพื่อรักษาสถานะ

### ผลลัพธ์
- ผู้ใช้สามารถค้นหา + กรองสถานะโน้ตได้ทันทีบนหน้าเดียว
- โมดอลใช้งานง่ายขึ้น (โฟกัสอัตโนมัติ, คีย์ลัด, รูปภาพแสดงถูกต้อง)
- UI มีความสมดุลและเข้ากับ Bootstrap 5/สีประจำโปรเจกต์
- การ Add/Edit โน้ตไม่ทำให้สูญเสียค่าการค้นหาและกรอง

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

## Verification — Note Search/Filter Feature (2025-10-01)

### ขอบเขตการตรวจสอบ
- ยืนยันการทำงานของการค้นหาและกรองรายการโน้ต (client-side) และตรวจสอบ API ฝั่งเซิร์ฟเวอร์ที่เกี่ยวข้อง
- อ้างอิงเฉพาะโค้ดที่มีในรีโพนี้เท่านั้น ทั้งชั้น presentation, service, repository, และโมเดล

### ภาพรวมการทำงานตามโค้ด
- Client-side filtering (ทันที ไม่เรียกเซิร์ฟเวอร์):
  - ฟังก์ชัน `setupNoteListFilters()` ใน `app/static/js/main.js` ค้นหาจากเนื้อหา card โดยอ่าน `.card-title` และ `.card-text` และกรองสถานะจาก `data-status` ของการ์ด
  - ฟังก์ชัน `refreshNoteListPreserveFilters()` รีโหลด fragment `/partial/note` แล้วคงค่า search term และ chip สถานะเดิมไว้ จากนั้น re-bind filter และ re-apply เงื่อนไขเดิม
- Partial routes สำหรับ SPA fragments:
  - `/partial/note`, `/partial/note/add`, `/partial/note/<id>/edit`, `/partial/note/<id>/delete`, `/partial/note/<id>/data` ถูกกำหนดใน `app/routes_new.py` (และมีฉบับ legacy ใน `app/routes.py`)
  - การลบโน้ตฝั่ง client (`window.deleteNote`) ส่ง header `X-Requested-With: XMLHttpRequest` เพื่อให้ฝั่งเซิร์ฟเวอร์ส่ง HTML fragment กลับมาแทนการ redirect ทั้งหน้า
- REST API สำหรับการค้นหา (พร้อมใช้งานหากต้องการ server-side search):
  - เส้นทางใน `app/presentation/routes/note_routes.py`: `GET /api/notes/search` และ `GET /api/notes/search/tags`
  - ตัวควบคุม `NoteController.search_notes` และ `NoteController.search_notes_by_tags` (
    เรียก `NoteService.search_notes` และ `NoteService.search_notes_by_tags`)
  - Service `NoteServiceImpl` มอบหมายไปยัง Repository (`NoteRepositoryImpl.search` และ `search_by_tags`)
  - Repository ใช้ SQLAlchemy `contains()` กับฟิลด์ `title`, `content` และ `tags` (แบบ simple JSON text contains) พร้อมสั่งเรียงตาม `created_at DESC`

### ประเด็นโค้ดสำคัญที่ยืนยันแล้ว
- UI search/filter:
  - `app/static/js/main.js`: `setupNoteListFilters()` และ `refreshNoteListPreserveFilters()` ทำงานร่วมกับ DOM โครงสร้าง card และ chip สถานะอย่างถูกต้อง
  - เหตุการณ์ input และ click ถูก bind และยกเลิก/ตั้งค่า class display card อย่างเหมาะสม ไม่พึ่งพา API ค้นหา
- API และ business layer:
  - `app/presentation/controllers/note_controller.py`: เมธอด `search_notes` ตรวจสอบสิทธิ์, รับพารามิเตอร์ `q`, `limit` และคืนค่า list ของ `note.to_dict()`
  - `app/application/services/note_service.py`: `search_notes()` และ `search_notes_by_tags()` เรียก repository โดยตรง (ไม่มี business rule พิเศษเพิ่มในการค้นหา)
  - `app/infrastructure/database/repositories/note_repository.py`: ค้นหาด้วย `NoteModel.title.contains(query) | NoteModel.content.contains(query)` และกรณี tags loop filter ต่อเนื่องด้วย `.tags.contains(tag)` แบบ simple matching
- โครงสร้างโมเดลที่เกี่ยวข้องกับฟีเจอร์:
  - `app/core/note.py` ใช้คอลัมน์ `content` (ยืนยันการเปลี่ยนชื่อจาก `body` เป็น `content` แล้ว)
  - มีการคงอยู่ของหลายเลเยอร์โมเดล (`app/core/note.py`, `app/infrastructure/database/models/note_model.py`, และ `database/models/note.py`) ซึ่งสะท้อนสภาพ migration/legacy ร่วมกับ clean architecture ที่กำลังย้ายเข้า

### ข้อสังเกต/ความเสี่ยง
- ขนาดข้อมูล: ปัจจุบันหน้า Note ใช้ client-side filtering; เมื่อจำนวนโน้ตมาก อาจเกิดปัญหาประสิทธิภาพฝั่งเบราว์เซอร์
  - แนวโน้มทางแก้: เชื่อม UI ให้เรียก `GET /api/notes/search` แทนการกรอง DOM ล้วน เมื่อเกิน threshold ที่กำหนด
- การค้นหา tags แบบ `.contains()` บน JSON string เป็น simple matching อาจเกิด false positive (เช่น คำที่เป็น prefix/substring)
  - ทางเลือก: แยกตาราง tags หรือเก็บเป็น JSON array จริงและใช้ฟังก์ชัน DB เฉพาะทาง (เช่น JSON operators)
- โมเดลซ้ำซ้อน: มีทั้ง `core` และ `infrastructure` + โฟลเดอร์ `database/` legacy อาจทำให้ schema drift ได้ถ้าแก้ไขไม่สอดคล้องกัน
  - แนะนำ: กำหนดแหล่งความจริงของ schema หนึ่งที่ชัดเจนและห่อชั้นอื่นด้วย mapping เท่านั้น
- ฟิลด์ legacy เช่น `status`, `external_link` ยังไม่ถูกรวมใน Domain Entity ตามที่ระบุไว้ในส่วนก่อนหน้า

### ผลการทดสอบเชิงพฤติกรรม (อ่านจากโค้ด + manual flow สั้น)
- Search box และ status chips ทำงานทันทีที่หน้าโน้ต (ไม่รีเฟรชหน้า)
- หลัง Add/Edit/Delete มีการรีเฟรช fragment ด้วย `refreshNoteListPreserveFilters()` ทำให้ค่าค้นหา/กรองเดิมยังคงอยู่
- API ค้นหา `/api/notes/search` พร้อมใช้งาน แต่ UI ปัจจุบันยังไม่เรียก API นี้โดยตรง

### ข้อเสนอแนะเชิงเทคนิค (ไม่ breaking)
- เพิ่ม switch ใน UI: หากจำนวนการ์ดเกิน N ให้เปลี่ยนเป็น server-side search (เรียก `/api/notes/search` พร้อม debounce)
- ปรับ tag storage/search ให้แม่นยำขึ้น (ตาราง tags หรือ JSON operator) เมื่อต้องรองรับการค้นหาที่ซับซ้อน
- ค่อยๆ ลดการพึ่งพา `core` model ตรงๆ ใน partial routes และใช้ service/repository เป็นหลัก เพื่อเลี่ยง schema drift

### สรุปสถานะ
- ฟีเจอร์ค้นหา/กรองโน้ตแบบ client-side ใช้งานได้ดีตามโค้ดปัจจุบัน และคงค่าการค้นหา/กรองหลังแก้ไขข้อมูลสำเร็จ
- โครง API สำหรับ server-side search พร้อมแล้ว เหมาะสำหรับ scale-up ในอนาคตเมื่อจำนวนโน้ตเพิ่มมาก
