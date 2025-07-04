
# แผนการพัฒนาซอฟต์แวร์ (Software Development Plan)

---

**ชื่อโปรเจค:** EduMatch: ระบบค้นหาและจับคู่ Study Group อัจฉริยะ

**เวอร์ชันเอกสาร:** 1.0

**วันที่จัดทำ:** 4 กรกฎาคม 2568

---

## สารบัญ

1. [บทนำ](#1-บทนำ-introduction)
2. [ระเบียบวิธีและเทคโนโลยี](#2-ระเบียบวิธีและเทคโนโลยี-methodology--technology)
3. [การออกแบบเชิงวัตถุและสถาปัตยกรรม](#3-การออกแบบเชิงวัตถุและสถาปัตยกรรม-oop-design--architecture)
4. [แผนการดำเนินงานตาม Waterfall Model](#4-แผนการดำเนินงานตาม-waterfall-model)
5. [ภาคผนวก](#5-ภาคผนวก-appendix)

---

## 1. บทนำ (Introduction)

### 1.1 วัตถุประสงค์ของเอกสาร

เอกสารฉบับนี้จัดทำขึ้นเพื่อเป็นแผนแม่บทในการพัฒนาซอฟต์แวร์โปรเจค "EduMatch" โดยจะระบุถึงความต้องการของระบบ, การออกแบบสถาปัตยกรรม, แผนการดำเนินงาน, และเทคโนโลยีที่ใช้ เพื่อให้ทีมพัฒนาและผู้มีส่วนได้ส่วนเสียทุกฝ่ายมีความเข้าใจตรงกันตลอดระยะเวลาของโปรเจค

### 1.2 ภาพรวมของโปรเจค

EduMatch คือแพลตฟอร์มสำหรับนักศึกษาที่ต้องการค้นหาหรือสร้างกลุ่มติวหนังสือ (Study Group) โดยมีเป้าหมายเพื่อแก้ปัญหาการหาเพื่อนติวและการนัดหมายที่ยุ่งยาก ระบบจะใช้ข้อมูลรายวิชาและตารางเวลาว่างของผู้ใช้ในการจับคู่และแนะนำกลุ่มที่เหมาะสมที่สุด เพื่อส่งเสริมการเรียนรู้ร่วมกันภายในมหาวิทยาลัย

### 1.3 ขอบเขต (Scope)

- **In-Scope:** การพัฒนาระบบ Backend API และ Frontend Web Application ที่ทำงานบนเบราว์เซอร์ โดยมีฟังก์ชันหลักคือการจัดการผู้ใช้, การจัดการกลุ่ม, การค้นหา, และการจับคู่อัตโนมัติ
- **Out-of-Scope:** การพัฒนาแอปพลิเคชันบนมือถือ (Native Mobile App), ระบบแชทแบบ Real-time, และการเชื่อมต่อกับระบบทะเบียนของมหาวิทยาลัย

---

## 2. ระเบียบวิธีและเทคโนโลยี (Methodology & Technology)

### 2.1 ระเบียบวิธีที่ใช้ (Methodology)

โปรเจคนี้จะดำเนินงานตามระเบียบวิธี **Waterfall Model** ซึ่งมีการทำงานเป็นลำดับขั้นที่ชัดเจน ได้แก่: Requirements Analysis -> System Design -> Implementation -> Testing -> Deployment -> Maintenance

### 2.2 เทคโนโลยีที่ใช้ (Technology Stack)

| Layer      | Technology                                    | Rationale                                                                 |
| :--------- | :-------------------------------------------- | :------------------------------------------------------------------------ |
| **Backend**  | Python, FastAPI, SQLAlchemy, Pydantic         | ประสิทธิภาพสูง, เหมาะกับการสร้าง API, และส่งเสริมการเขียนโค้ดแบบ OOP ได้ดีเยี่ยม |
| **Frontend** | HTML, Tailwind CSS, Vanilla JavaScript        | เรียบง่าย, ยืดหยุ่น, และเพียงพอสำหรับโปรเจค โดยไม่ต้องพึ่งพา Framework ที่ซับซ้อน |
| **Database** | SQLite                                        | ง่ายต่อการติดตั้งและจัดการ, เหมาะสำหรับโปรเจคระดับนี้ ไม่ต้องตั้งค่าเซิร์ฟเวอร์ |
| **Deployment**| Render.com (Web Service + Static Site)        | เป็นมิตรกับนักพัฒนา, มี Free Tier, และรองรับ Persistent Disk สำหรับ SQLite ได้ |

---

## 3. การออกแบบเชิงวัตถุและสถาปัตยกรรม (OOP Design & Architecture)

### 3.1 หลักการออกแบบเชิงวัตถุ (OOP Principles)

โปรเจคจะยึดตามหลักการออกแบบเชิงวัตถุ 5 ประการ (SOLID) และหลักการพื้นฐานของ OOP เพื่อให้ได้ซอฟต์แวร์ที่มีคุณภาพ, ยืดหยุ่น, และง่ายต่อการบำรุงรักษา:

- **Single Responsibility Principle (SRP):** แต่ละคลาสจะมีหน้าที่รับผิดชอบเพียงอย่างเดียว (เช่น `AuthService` จัดการเรื่องการยืนยันตัวตน, `GroupService` จัดการเรื่องกลุ่ม)
- **Open/Closed Principle (OCP):** ออกแบบให้สามารถเพิ่มฟังก์ชันใหม่ได้โดยไม่ต้องแก้ไขโค้ดเดิม
- **Liskov Substitution Principle (LSP):** คลาสลูกสามารถทำงานแทนที่คลาสแม่ได้เสมอ
- **Interface Segregation Principle (ISP):** แบ่ง Class การทำงานให้เล็กและเฉพาะเจาะจง
- **Dependency Inversion Principle (DIP):** ใช้ Dependency Injection ของ FastAPI เพื่อลดการพึ่งพากันโดยตรงระหว่างโมดูล ทำให้โค้ดทดสอบได้ง่าย
- **Encapsulation, Abstraction, Inheritance, Polymorphism:** จะถูกนำมาประยุกต์ใช้ในการออกแบบ Models, Services, และ Schemas ทั้งหมด

### 3.2 โครงสร้างโปรเจค (Project Structure)

โปรเจคจะถูกจัดเรียงตามโครงสร้างมาตรฐานของ FastAPI เพื่อความชัดเจนและง่ายต่อการพัฒนา:

```
EduMatch/
│
├── backend/                  # Backend Application (FastAPI)
│   ├── api/                  # API Routes (Controllers)
│   ├── core/                 # Core settings and configurations
│   ├── models/               # SQLAlchemy Models (Data Layer)
│   ├── schemas/              # Pydantic Schemas (Data Transfer Objects)
│   ├── services/             # Business Logic Services (OOP heart)
│   ├── database.py           # Database connection setup
│   └── main.py               # Main application entry point
│
├── frontend/                 # Frontend Application (Static Web)
│   ├── index.html
│   ├── dashboard.html
│   └── ... (other html files)
│
├── tests/                    # Test files
├── .gitignore
├── requirements.txt
└── README.md
```

---

## 4. แผนการดำเนินงานตาม Waterfall Model

### 4.1 Phase 1: การวิเคราะห์ความต้องการ (Requirements Analysis)
- **เป้าหมาย:** กำหนดขอบเขตและฟังก์ชันการทำงานของระบบให้ชัดเจน
- **ผลลัพธ์:** เอกสาร Software Requirements Specification (SRS) ที่ระบุถึง Functional และ Non-Functional Requirements ทั้งหมด

| ID   | Functional Requirement | Description                                                              |
| :--- | :--------------------- | :----------------------------------------------------------------------- |
| FR1  | User Management        | ผู้ใช้สามารถลงทะเบียน, เข้าสู่ระบบ, ออกจากระบบ, และแก้ไขโปรไฟล์ได้         |
| FR2  | Profile & Schedule     | ผู้ใช้สามารถกำหนดข้อมูลพื้นฐานและตารางเวลาที่ว่างของตนเองได้              |
| FR3  | Group Management       | ผู้ใช้สามารถสร้างกลุ่มติว, แก้ไขรายละเอียด, และจัดการสมาชิกได้             |
| FR4  | Search & Discovery     | ผู้ใช้สามารถค้นหากลุ่มติวจากรหัสวิชาหรือชื่อกลุ่มได้                      |
| FR5  | Joining Groups         | ผู้ใช้สามารถส่งคำขอเข้าร่วมกลุ่มและเจ้าของกลุ่มสามารถอนุมัติได้            |
| FR6  | Matching               | ระบบสามารถแนะนำกลุ่มที่เหมาะสมโดยพิจารณาจากตารางเวลาและวิชาที่สนใจ         |

### 4.2 Phase 2: การออกแบบระบบ (System Design)
- **เป้าหมาย:** ออกแบบสถาปัตยกรรมและโครงสร้างซอฟต์แวร์ทั้งหมด
- **ผลลัพธ์:** เอกสาร Software Design Document (SDD) ที่ประกอบด้วย:
    1.  **ER Diagram:** แผนภาพแสดงความสัมพันธ์ของตารางในฐานข้อมูล SQLite
    2.  **Class Diagram:** แผนภาพแสดงโครงสร้างและความสัมพันธ์ของคลาสในส่วน `services/` และ `models/`
    3.  **API Specification:** ตารางกำหนด Endpoint, HTTP Method, Request Body, และ Response ทั้งหมด

### 4.3 Phase 3: การพัฒนาโปรแกรม (Implementation)
- **เป้าหมาย:** เขียนโค้ดตามที่ออกแบบไว้ใน SDD
- **ผลลัพธ์:** ซอร์สโค้ดของโปรแกรม (Source Code) ที่สมบูรณ์

### 4.4 Phase 4: การทดสอบ (Testing)
- **เป้าหมาย:** ค้นหาและแก้ไขข้อผิดพลาดเพื่อให้มั่นใจว่าซอฟต์แวร์ทำงานได้ถูกต้อง
- **ผลลัพธ์:** เอกสาร Test Cases และรายงานผลการทดสอบ

### 4.5 Phase 5: การติดตั้งและใช้งาน (Deployment)
- **เป้าหมาย:** นำซอฟต์แวร์ขึ้นทำงานบนเซิร์ฟเวอร์จริงเพื่อให้ผู้ใช้เข้าถึงได้
- **ผลลัพธ์:** แอปพลิเคชัน EduMatch ที่ใช้งานได้จริงผ่าน URL
- **ขั้นตอนหลัก:**
    1.  Deploy Backend (FastAPI) บน Render.com เป็น "Web Service" พร้อมตั้งค่า "Persistent Disk" สำหรับไฟล์ฐานข้อมูล SQLite
    2.  Deploy Frontend (HTML/CSS/JS) บน Render.com เป็น "Static Site"

### 4.6 Phase 6: การบำรุงรักษา (Maintenance)
- **เป้าหมาย:** ดูแลรักษาระบบหลังจากเปิดใช้งานจริง
- **ผลลัพธ์:** ซอฟต์แวร์เวอร์ชันใหม่ที่มีการแก้ไขข้อผิดพลาดหรือเพิ่มฟีเจอร์ตาม Feedback

---

## 5. ภาคผนวก (Appendix)

### 5.1 คำย่อและคำจำกัดความ
- **API:** Application Programming Interface
- **OOP:** Object-Oriented Programming
- **SOLID:** หลักการออกแบบซอฟต์แวร์ 5 ประการ (Single Responsibility, Open/Closed, Liskov Substitution, Interface Segregation, Dependency Inversion)
- **UI:** User Interface
- **SRS:** Software Requirements Specification
- **SDD:** Software Design Document
