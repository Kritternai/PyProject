# โครงสร้างโปรเจกต์

นี่คือโครงสร้างไฟล์และโฟลเดอร์ของโปรเจกต์ พร้อมคำอธิบายหน้าที่ของแต่ละส่วน

-   **`/` (Root Directory)**: ไดเรกทอรีหลักของโปรเจกต์
    -   `run.py`: ไฟล์หลักสำหรับเริ่มต้นการทำงานของเว็บแอปพลิเคชัน Flask
    -   `start_flask.sh`: สคริปต์ Shell สำหรับช่วยให้การรัน `run.py` ง่ายขึ้น
    -   `requirements.txt`: เก็บรายชื่อ Python libraries ที่โปรเจกต์นี้ต้องใช้ (สำหรับฝั่ง Backend)
    -   `package.json`: เก็บรายชื่อ JavaScript libraries ที่โปรเจกต์นี้ต้องใช้ (สำหรับฝั่ง Frontend, ในที่นี้คือ Tailwind CSS)
    -   `tailwind.config.js`: ไฟล์ตั้งค่าสำหรับ Tailwind CSS
    -   `LICENSE`, `README.md`, `CONTRIBUTING.md`: ไฟล์เอกสารมาตรฐานของโปรเจกต์

-   **`app/`**: โฟลเดอร์หลักของ Flask Application
    -   `__init__.py`: ไฟล์เริ่มต้นของ Python package นี้ ใช้สร้างและตั้งค่า Flask app instance
    -   `routes.py`: กำหนด URL endpoints ทั้งหมดของเว็บไซต์ และเชื่อมโยงไปยังฟังก์ชัน Python ที่จะทำงาน
    -   **`core/`**: เก็บโค้ดที่เป็นหัวใจหลัก (Business Logic) ของโปรเจกต์
        -   `user.py`, `user_manager.py`: จัดการข้อมูลและตรรกะของผู้ใช้
        -   `lesson.py`, `lesson_manager.py`: จัดการข้อมูลและตรรกะของบทเรียน
        -   `authenticator.py`: จัดการเกี่ยวกับการยืนยันตัวตน (Login/Logout)
        -   `google_credentials.py`: จัดการการเชื่อมต่อกับ Google API
    -   **`static/`**: เก็บไฟล์ที่ไม่ต้องประมวลผลบนเซิร์ฟเวอร์
        -   `css/`: เก็บไฟล์ CSS
            -   `input.css`: ไฟล์ CSS ที่เราเขียนเองก่อนที่จะให้ Tailwind ประมวลผล
            -   `tailwind.css`: ไฟล์ CSS ผลลัพธ์ที่ได้จาก Tailwind
    -   **`templates/`**: เก็บไฟล์ HTML ที่เป็นโครงหน้าเว็บต่างๆ
        -   `index.html`, `login.html`, `dashboard.html`: หน้าเว็บหลักๆ
        -   `lessons/`: โฟลเดอร์ย่อยสำหรับจัดกลุ่มหน้าเว็บที่เกี่ยวกับบทเรียน

-   **`chrome_extension/`**: โฟลเดอร์สำหรับส่วนขยายของเบราว์เซอร์ Google Chrome
    -   `manifest.json`: ไฟล์สำคัญที่สุดของ Extension บอกข้อมูลพื้นฐานและไฟล์ที่ต้องใช้
    -   `background.js`: สคริปต์ที่ทำงานเบื้องหลัง
    -   `popup.html`, `popup.js`: โค้ดสำหรับสร้างหน้าต่าง Popup ของ Extension
    -   `content_scripts/`: เก็บสคริปต์ที่จะถูกฝังเข้าไปในหน้าเว็บอื่น
    -   `icons/`: เก็บไฟล์รูปภาพไอคอนของ Extension

-   **`docs/`**: โฟลเดอร์สำหรับเก็บเอกสารทั้งหมดที่เกี่ยวกับโปรเจกต์
    -   `PRODUCT_ROADMAP.md`, `PROJECT_PROPOSAL.md`: เอกสารวางแผนและข้อเสนอโครงการ
    -   `adr/`: เก็บเอกสารการตัดสินใจทางสถาปัตยกรรม (Architecture Decision Records)

-   **`instance/`**: โฟลเดอร์ที่ Flask ใช้เก็บไฟล์เฉพาะของ instance นี้ (ไม่ถูก commit ขึ้น Git)
    -   `site.db`: ไฟล์ฐานข้อมูลของโปรเจกต์ (SQLite)

-   **`venv/`**: โฟลเดอร์ของ Python Virtual Environment

-   **`node_modules/`**: โฟลเดอร์ที่เก็บ JavaScript libraries ที่ติดตั้งผ่าน npm/yarn
