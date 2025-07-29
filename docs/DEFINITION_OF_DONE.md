# Definition of Done (DoD) (อัปเดตล่าสุด)

เอกสารนี้คือนิยามของคำว่า "เสร็จ" ที่ทีม Smart Learning Hub ตกลงร่วมกัน งาน (User Story, Task, Bug Fix) จะถูกย้ายไปที่คอลัมน์ "Done" บน Kanban Board ได้ ก็ต่อเมื่อผ่านเกณฑ์ทั้งหมดใน Checklist นี้

---

## Checklist for "Done"

### 1. Code Quality
- [ ] โค้ดเขียนตามมาตรฐาน (PEP 8, CONTRIBUTING.md)
- [ ] ไม่มีโค้ดซ้ำซ้อน (DRY Principle)
- [ ] โค้ดอ่านง่าย, มีคอมเมนต์ใน logic ที่ซับซ้อน
- [ ] โครงสร้าง OOP/Modular ตามแนวทางโปรเจกต์

### 2. Testing
- [ ] มี Unit Test ครอบคลุม logic หลักของฟีเจอร์
- [ ] Integration Test สำหรับฟีเจอร์ที่เชื่อมต่อภายนอก (Google API, Chrome Extension)
- [ ] Automated Tests (Unit, Integration) ผ่าน 100%

### 3. Review & Integration
- [ ] โค้ดได้รับการตรวจสอบ (Code Review) และ approve จากเพื่อนร่วมทีมอย่างน้อย 1 คน
- [ ] Branch ของงานถูก Merge เข้าสู่ main/dev branch เรียบร้อยแล้ว
- [ ] ไม่มี Merge Conflict เกิดขึ้น

### 4. Documentation
- [ ] เอกสารที่เกี่ยวข้อง (Proposal, Roadmap, Backlog, User Guide, API) ได้รับการอัปเดตให้สอดคล้องกับการเปลี่ยนแปลง
- [ ] มีคอมเมนต์ในโค้ดส่วนที่ logic ซับซ้อน (อธิบาย "ทำไม" ไม่ใช่แค่ "ทำอะไร")
- [ ] ตัวอย่างการใช้งาน/วิธีติดตั้ง/วิธีเชื่อมต่อ (Google API, Chrome Extension) ถูกอัปเดตใน README หรือ docs

### 5. UX/UI & Integration
- [ ] UI/UX ตรงตาม design, responsive, ใช้งานได้จริง
- [ ] การเชื่อมต่อกับ Google Classroom, Chrome Extension, หรือ API ภายนอก ทดสอบแล้วใช้งานได้จริง

---

*DoD นี้สามารถปรับปรุงได้ผ่านการพูดคุยและตกลงร่วมกันในทีม*