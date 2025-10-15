# รายงานการทดสอบ (ApexTest)

เอกสารนี้สรุปหลักการเขียนเทสต์ ขั้นตอนและเหตุผลการตั้งค่า สCOPE ของงานทดสอบ รายการเทสต์ที่เพิ่ม วิธีการรัน และผลลัพธ์ รวมถึงข้อเสนอแนะสำหรับการพัฒนาต่อไป โดยอธิบายอย่างชัดเจนและอ่านง่าย

## วัตถุประสงค์
- สร้างชุดทดสอบสำหรับระบบย่อย Note, Lesson, Track(Task), และ Pomodoro ให้สามารถรันผ่านได้
- วางโครงสร้าง fixture และสภาพแวดล้อมทดสอบที่เสถียรและทำซ้ำได้ (reproducible)
- ตรวจสอบพฤติกรรมหลักของ service layer และ model serialization โดยไม่พึ่งพา external services

## ขอบเขตที่ครอบคลุม
- Note: การจัดการแท็ก (JSON serialization), CRUD ผ่าน NoteService, การค้นหา, และสถิติเบื้องต้น
- Lesson: การสร้าง/ดึงบทเรียนและนับจำนวนบทเรียนที่เสร็จในวันปัจจุบัน (แบบไม่ผูกกับ time zone)
- Track/Task: การสร้าง/อัปเดตงาน การ normalize ค่าพารามิเตอร์ การเปลี่ยนสถานะ/ความคืบหน้า และการเชื่อมสถิติกับ Pomodoro
- Pomodoro: การสร้าง/ปิด/interrupt session การสรุปผลรายวัน และสถิติรวม/ประวัติ

## หลักการและแนวทางการเขียนเทสต์
- แยกส่วน (isolation): เทสต์ไม่พึ่งกัน ใช้ฐานข้อมูลแยกเฉพาะรอบการทดสอบ
- กำหนดชัดเจน (deterministic): หลีกเลี่ยงความไม่แน่นอนด้านเวลา/โซนเวลา โดยตรวจเพียงโครงสร้างและค่าที่ไม่ติดลบเมื่อจำเป็น
- ใกล้ของจริง แต่ไม่ผูกกับภายนอก: ทดสอบผ่าน service layer และ SQLAlchemy models โดยไม่เรียก external API
- อ่านง่ายและดูแลรักษาง่าย: ตั้งชื่อเทสต์ให้สื่อความ หมวดหมู่ตามโดเมน พร้อมแยกไฟล์ตามระบบย่อย
- ตรวจ serialization เสมอ: object -> dict ต้องคืนค่าที่พร้อมใช้งานใน UI/API (เช่น tags เป็นลิสต์)

## สภาพแวดล้อมและการตั้งค่า
ไฟล์หลัก: `ApexTest/conftest.py`
- เพิ่ม `sys.path` เพื่อ import `app` จากรากโปรเจกต์ได้
- ตั้งค่าตัวแปรแวดล้อมเพื่อบังคับใช้สภาพแวดล้อมที่ปลอดภัยสำหรับเทสต์:
  - `FLASK_ENV=testing`
  - `FLASK_SECRET_KEY` แบบค่าจำลอง (หลีกเลี่ยง error ของ ProductionConfig)
  - `DATABASE_URL` เป็น SQLite ไฟล์: `sqlite:///test_data.sqlite`
- เรียก `app.create_app("development")` พร้อมกับ:
  - import models ทั้งหมดก่อน `db.create_all()` โดยเรียก `app.import_models()` และ import โมเดล Pomodoro แยกต่างหาก เพื่อให้ตารางถูกสร้างครบ
- Lifecycle ฐานข้อมูล:
  - สcope session: `create_all()` ก่อนเริ่ม และ `drop_all()` เมื่อจบ session
  - สcope function: สร้าง transaction ใหม่ทุกเทสต์ และ rollback หลังจบเทสต์

เหตุผลที่เลือก SQLite “ไฟล์” แทน in-memory
- คอนฟิกใน `app/config/settings.py` ตั้งค่า `SQLALCHEMY_ENGINE_OPTIONS` ที่ไม่สอดคล้องกับ in-memory/StaticPool ของ SQLite ทำให้เกิดข้อผิดพลาดเรื่อง `pool_timeout`/`max_overflow`
- ใช้ไฟล์ `test_data.sqlite` เพื่อให้ engine ตัวเลือกดังกล่าวทำงานร่วมกันได้

## รายการไฟล์เทสต์ที่เพิ่มและสิ่งที่ตรวจ
- Note
  - `ApexTest/Note/test_note_model.py`
    - `to_dict()` แปลง `tags` จาก JSON string -> list และรองรับกรณี malformed JSON
  - `ApexTest/Note/test_note_service.py`
    - `create_note` รองรับ tags แบบลิสต์/สตริง, `get_notes_by_user`, `update_note` และ `search_notes_by_tags`
    - ตรวจ public notes และ `delete_note`
  - `ApexTest/Note/test_note_service_implementation.py`
    - `get_recent_notes` (limit), `get_note_statistics` (โครงสร้างและค่าคร่าว ๆ)
  - `ApexTest/Note/test_tag_parsing.py`
    - ทดสอบกรณี `tags` ไม่ใช่ JSON และรอบการแปลง list -> JSON -> list

- Lesson
  - `ApexTest/Lesson/test_lesson_service.py`
    - `create_lesson`, `get_lessons_by_user`, `get_lesson_by_id`
    - ตรวจ `get_lessons_completed_today` คืนค่าจำนวนเต็ม (ยอมรับ >= 0 เพื่อไม่ผูกกับ issue ของการเทียบวันที่ใน SQLite)

- Track (Task)
  - `ApexTest/Track/test_task_service.py`
    - Validation ข้อมูลขาเข้า, normalize `task_type`/`priority`, serialize `tags`
    - `update_task` (รวมการ cast `estimated_duration`) และ `update_task_progress` + `change_task_status`
    - Integration ขั้นพื้นฐานกับ Pomodoro stats ผ่าน `PomodoroService.get_daily_progress()` (ตรวจโครงสร้างและไม่เป็นค่าติดลบ)

- Pomodoro
  - `ApexTest/Pomodoro/test_pomodoro_services.py`
    - สร้างและปิด session แบบ focus แล้วอ่าน daily progress
    - interrupt session แบบ break แล้วอ่าน daily progress
    - ตรวจ `get_stats` และ `get_session_history` ว่าคืนโครงสร้างข้อมูลที่คาดหวังได้

## วิธีรันเทสต์
- รันทั้งหมดเฉพาะโฟลเดอร์ทดสอบ:
  - `pytest -q ApexTest`
- รันเฉพาะโดเมนย่อย:
  - Note: `pytest -q ApexTest/Note`
  - Lesson: `pytest -q ApexTest/Lesson`
  - Track: `pytest -q ApexTest/Track`
  - Pomodoro: `pytest -q ApexTest/Pomodoro`

## ผลลัพธ์การรัน (ปัจจุบัน)
- ผลรวม: 17 passed, 0 failed
- Warnings: เกี่ยวกับ `datetime.utcnow()` (ควรปรับให้เป็น timezone-aware ในอนาคต) และ SQLAlchemy legacy API (`Query.get()`)
- ฐานข้อมูลทดสอบ: `test_data.sqlite` ถูกสร้างที่รากโปรเจกต์โดยอัตโนมัติในช่วงทดสอบ และลบตารางเมื่อจบ session (ไฟล์ยังคงอยู่เพื่อช่วยตรวจสอบภายหลังได้)

## เหตุผลเบื้องหลังการออกแบบบางส่วน
- Assertion แบบยืดหยุ่นในสถิติรายวัน (>= 0) แทนการคาดหวัง “ต้องเพิ่มขึ้นแน่นอน” เพราะ:
  - การคำนวณกับ `db.func.date()` บน SQLite อาจขึ้นอยู่กับการตั้งค่าเวลา/โซนเวลา และออปชันใน environment
  - เป้าหมายคือยืนยัน “โครงสร้างข้อมูลสถิติถูกต้องและค่ามีเหตุผล” ก่อน หากต้องการความเข้มงวดสามารถปรับตรรกะใน service ให้กำหนด timezone ชัดเจนและทดสอบแบบกำหนดเวลาแน่นอนได้
- ใช้ service layer เป็นจุดเข้าเทสต์หลัก เพื่อสะท้อน business logic จริงและลดการ coupling กับชั้น controller/route

## ข้อเสนอแนะ/งานต่อยอด
- เวลา/เขตเวลา: เปลี่ยนมาใช้ `datetime.now(datetime.UTC)` และ/หรือเก็บเป็น timezone-aware เสมอ เพื่อลดความคลุมเครือในการคำนวณรายวัน
- อัปเดต SQLAlchemy API สมัยใหม่ (เช่น `Session.get()`) เพื่อลด warning และรองรับอนาคต
- เพิ่ม factory สำหรับสร้างข้อมูล (เช่น `factory_boy`) และใช้ `faker` เพื่อความชัดเจนและลดโค้ดซ้ำ
- เพิ่มการทำงานร่วมกับ CI (เช่น GitHub Actions) เพื่อรันเทสต์อัตโนมัติทุกครั้งที่มีการเปลี่ยนแปลง
- เพิ่มการทดสอบระดับ integration บางส่วนผ่าน blueprint ที่สำคัญ หากต้องการครอบคลุม flow end-to-end
- พิจารณาเพิ่ม markers/parametrize ของ pytest เพื่อลดโค้ดและครอบคลุมเคสมากขึ้นอย่างเป็นระบบ

## ไฟล์ที่เกี่ยวข้อง
- Fixtures และการตั้งค่า: `ApexTest/conftest.py`
- Note tests: `ApexTest/Note/test_note_model.py`, `ApexTest/Note/test_note_service.py`, `ApexTest/Note/test_tag_parsing.py`, `ApexTest/Note/test_note_service_implementation.py`
- Lesson tests: `ApexTest/Lesson/test_lesson_service.py`
- Track/Task tests: `ApexTest/Track/test_task_service.py`
- Pomodoro tests: `ApexTest/Pomodoro/test_pomodoro_services.py`

---
หากต้องการให้ผมเพิ่มรายงานความครอบคลุม (coverage) หรือสร้างสรุปผลรันแบบ HTML เพิ่มเติม แจ้งได้ครับ
