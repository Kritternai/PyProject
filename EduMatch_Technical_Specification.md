
# เอกสารข้อกำหนดทางเทคนิค (Technical Specification)

---

**ชื่อโปรเจค:** EduMatch: ระบบค้นหาและจับคู่ Study Group อัจฉริยะ

**เวอร์ชันเอกสาร:** 1.0

**กลุ่มเป้าหมาย:** ทีมพัฒนา (Backend & Frontend Developers)

**วันที่จัดทำ:** 4 กรกฎาคม 2568

---

## 1. บทนำ (Introduction)

เอกสารฉบับนี้มีวัตถุประสงค์เพื่อเป็นแนวทางเชิงเทคนิคสำหรับทีมพัฒนาในการสร้างโปรเจค EduMatch โดยจะลงรายละเอียดเกี่ยวกับการตั้งค่าสภาพแวดล้อม, สถาปัตยกรรมของ Backend, โครงสร้างฐานข้อมูล, การออกแบบคลาสและ API, รวมถึงแนวทางการทดสอบและ Deployment

---

## 2. การตั้งค่าสภาพแวดล้อม (Project Setup & Environment)

### 2.1 เครื่องมือที่จำเป็น (Prerequisites)
- **Python:** 3.10+
- **Node.js & npm:** 18.0+ (สำหรับจัดการ Tailwind CSS)
- **Git:** สำหรับ Version Control

### 2.2 การตั้งค่า Backend (Python)
1.  สร้างและเปิดใช้งาน Virtual Environment:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```
2.  ติดตั้ง Dependencies ทั้งหมดจากไฟล์ `requirements.txt`:
    ```bash
    pip install -r requirements.txt
    ```
    **เนื้อหาไฟล์ `requirements.txt`:**
    ```
    fastapi
    uvicorn[standard]
    sqlalchemy
    pydantic
    passlib[bcrypt]
    python-jose[cryptography]
    ```

### 2.3 การตั้งค่า Frontend (Tailwind CSS)
1.  ติดตั้ง Dependencies ของ Node.js:
    ```bash
    npm install -D tailwindcss
    npx tailwindcss init
    ```
2.  สร้างไฟล์ CSS โดยใช้คำสั่ง Build ของ Tailwind:
    ```bash
    npx tailwindcss -i ./frontend/src/input.css -o ./frontend/css/style.css --watch
    ```

---

### 2.4 โครงสร้างไฟล์ของโปรเจค (Project File Structure)

เพื่อให้การพัฒนาเป็นไปอย่างมีระเบียบและง่ายต่อการบำรุงรักษา โปรเจคจะถูกจัดเรียงตามโครงสร้างมาตรฐานดังนี้:

```
EduMatch/
│
├── backend/                  # Backend Application (FastAPI)
│   ├── api/                  # API Routes (Controllers)
│   │   ├── __init__.py
│   │   ├── auth_routes.py
│   │   └── group_routes.py
│   │
│   ├── core/                 # Core settings and configurations
│   │   ├── __init__.py
│   │   └── config.py
│   │
│   ├── models/               # SQLAlchemy Models (Data Layer)
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── user_model.py
│   │   └── group_model.py
│   │
│   ├── schemas/              # Pydantic Schemas (Data Transfer Objects)
│   │   ├── __init__.py
│   │   ├── user_schema.py
│   │   └── group_schema.py
│   │
│   ├── services/             # Business Logic Services (OOP heart)
│   │   ├── __init__.py
│   │   ├── auth_service.py
│   │   ├── group_service.py
│   │   └── matching_service.py
│   │
│   ├── database.py           # Database connection setup
│   └── main.py               # Main application entry point
│
├── frontend/                 # Frontend Application (Static Web)
│   ├── src/                  # Source files for Tailwind
│   │   └── input.css
│   ├── css/                  # Compiled CSS
│   │   └── style.css
│   ├── js/                   # JavaScript files
│   │   └── app.js
│   └── index.html
│   └── ... (other html files)
│
├── tests/                    # Test files
│   ├── __init__.py
│   └── test_matching_service.py
│
├── .gitignore
├── requirements.txt
└── README.md
```

---

## 3. สถาปัตยกรรม Backend เชิงลึก (Backend Architecture Deep Dive)

### 3.1 โครงสร้างฐานข้อมูล (SQLite Database Schema)

ฐานข้อมูลจะประกอบด้วย 4 ตารางหลักที่มีความสัมพันธ์กันดังนี้:

- **`users`**
    - `id` (INTEGER, PRIMARY KEY, AUTOINCREMENT)
    - `email` (TEXT, UNIQUE, NOT NULL)
    - `hashed_password` (TEXT, NOT NULL)

- **`profiles`**
    - `id` (INTEGER, PRIMARY KEY, AUTOINCREMENT)
    - `user_id` (INTEGER, FOREIGN KEY -> `users.id`)
    - `full_name` (TEXT, NOT NULL)
    - `major` (TEXT)
    - `free_schedule` (TEXT) - *เก็บเป็น JSON String ของ Array ที่มี 168 ช่อง (24 ชม. x 7 วัน) โดย 1=ว่าง, 0=ไม่ว่าง*

- **`groups`**
    - `id` (INTEGER, PRIMARY KEY, AUTOINCREMENT)
    - `group_name` (TEXT, NOT NULL)
    - `course_code` (TEXT, NOT NULL)
    - `description` (TEXT)
    - `owner_id` (INTEGER, FOREIGN KEY -> `users.id`)

- **`memberships`**
    - `id` (INTEGER, PRIMARY KEY, AUTOINCREMENT)
    - `user_id` (INTEGER, FOREIGN KEY -> `users.id`)
    - `group_id` (INTEGER, FOREIGN KEY -> `groups.id`)
    - `status` (TEXT, NOT NULL) - *สถานะ: 'pending' หรือ 'approved'*

### 3.2 การออกแบบคลาส (Class Design)

#### 3.2.1 Models Layer (`backend/models/`)

ใช้ SQLAlchemy ORM ในการแปลงตารางในฐานข้อมูลให้เป็น Python Class

```python
# backend/models/user_model.py
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    profile = relationship("Profile", back_populates="user", uselist=False)

class Profile(Base):
    __tablename__ = "profiles"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    full_name = Column(String)
    # ... other fields
    user = relationship("User", back_populates="profile")
```

#### 3.2.2 Schemas Layer (`backend/schemas/`)

ใช้ Pydantic ในการกำหนด Data Shape และ Validation สำหรับ API

```python
# backend/schemas/user_schema.py
from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    email: EmailStr
    password: str

class UserRead(BaseModel):
    id: int
    email: EmailStr

    class Config:
        orm_mode = True
```

#### 3.2.3 Services Layer (`backend/services/`)

หัวใจของ Business Logic ที่ใช้หลักการ OOP อย่างเต็มที่

- **`AuthService`**: รับผิดชอบการลงทะเบียน, ตรวจสอบรหัสผ่าน (ใช้ `passlib`), และสร้าง/ตรวจสอบ JWT (ใช้ `python-jose`)
- **`GroupService`**: รับผิดชอบการสร้าง, ค้นหา, และจัดการสมาชิกกลุ่ม
- **`MatchingService`**: รับผิดชอบอัลกอริทึมการจับคู่
    - **อัลกอริทึมการจับคู่ (Matching Algorithm):**
        1.  **Input:** `user_id` ของผู้ใช้ที่ต้องการหาคู่
        2.  **Step 1:** ดึงข้อมูล `free_schedule` ของผู้ใช้คนนั้นจากตาราง `profiles`
        3.  **Step 2:** ค้นหากลุ่มทั้งหมด (`candidate_groups`) ที่ผู้ใช้ยังไม่ได้เป็นสมาชิก
        4.  **Step 3:** สำหรับแต่ละ `candidate_group`:
            a. ดึง `free_schedule` ของเจ้าของกลุ่ม (`owner`)
            b. **คำนวณคะแนนความเข้ากันได้ (Match Score):** คำนวณจำนวนชั่วโมงที่ตารางว่างทับซ้อนกันระหว่าง `user` และ `owner`
            c. เก็บค่า (group, match_score)
        5.  **Step 4:** เรียงลำดับกลุ่มทั้งหมดจาก `match_score` มากไปน้อย
        6.  **Output:** คืนค่าเป็น List ของกลุ่มที่เรียงลำดับแล้ว

### 3.3 ข้อกำหนดของ API (API Specification)

| Method | Endpoint                             | Description                                  |
| :----- | :----------------------------------- | :------------------------------------------- |
| `POST` | `/api/v1/auth/register`              | สร้างผู้ใช้ใหม่                               |
| `POST` | `/api/v1/auth/token`                 | เข้าระบบเพื่อรับ JWT Token                    |
| `GET`  | `/api/v1/users/me`                   | [Protected] ดูข้อมูลโปรไฟล์ส่วนตัว             |
| `PUT`  | `/api/v1/users/me/profile`           | [Protected] อัปเดตข้อมูลโปรไฟล์              |
| `GET`  | `/api/v1/groups`                     | ค้นหากลุ่มทั้งหมด (มี Query Params)           |
| `POST` | `/api/v1/groups`                     | [Protected] สร้างกลุ่มใหม่                    |
| `GET`  | `/api/v1/groups/{group_id}`          | ดูรายละเอียดของกลุ่มเดียว                      |
| `POST` | `/api/v1/groups/{group_id}/join`     | [Protected] ส่งคำขอเข้าร่วมกลุ่ม              |
| `GET`  | `/api/v1/users/me/matches`           | [Protected] ขอรายการกลุ่มที่ระบบแนะนำ         |

*`[Protected]` หมายถึง Endpoint ที่ต้องใช้ JWT Token ใน Authorization Header* 

---

## 4. สถาปัตยกรรม Frontend

- **การจัดการ State:** เนื่องจากเป็น Vanilla JS, State ของแอปพลิเคชัน (เช่น ข้อมูลผู้ใช้ที่ login อยู่, JWT Token) จะถูกเก็บไว้ใน `localStorage` ของเบราว์เซอร์
- **การเรียก API:** ใช้ `fetch()` API ของ JavaScript ในการสื่อสารกับ Backend

```javascript
// ตัวอย่างการเรียก Protected API
const token = localStorage.getItem('authToken');

fetch('/api/v1/users/me', {
    method: 'GET',
    headers: {
        'Authorization': `Bearer ${token}`
    }
})
.then(response => response.json())
.then(data => console.log(data));
```

---

## 5. กลยุทธ์การทดสอบ (Testing Strategy)

- **Unit Testing:** ใช้ `pytest` เพื่อทดสอบแต่ละฟังก์ชันใน Service Classes โดยเฉพาะ `MatchingService` โดยจะมีการจำลอง (Mock) การเชื่อมต่อฐานข้อมูลเพื่อทดสอบเฉพาะ Logic การคำนวณ
- **Integration Testing:** ใช้ `TestClient` ของ FastAPI เพื่อทดสอบ API Endpoints ทั้งหมด เพื่อให้มั่นใจว่าทุกส่วนทำงานร่วมกันได้อย่างถูกต้อง

---

## 6. แผนการติดตั้งและใช้งาน (Deployment Pipeline)

- **Backend (Render Web Service):**
    - **Build Command:** `pip install -r requirements.txt`
    - **Start Command:** `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`
    - **Persistent Disk:** สร้าง Disk และ Mount ที่ Path `/data` จากนั้นกำหนดให้ไฟล์ SQLite ถูกสร้างที่ `/data/edumatch.db`

- **Frontend (Render Static Site):**
    - **Build Command:** `npm install && npx tailwindcss -i ./frontend/src/input.css -o ./frontend/css/style.css`
    - **Publish Directory:** `frontend`
