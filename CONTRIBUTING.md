# Contributing to Smart Learning Hub

ขอบคุณที่สนใจช่วยพัฒนาโปรเจกต์ของเรา! การมีส่วนร่วมของคุณมีความสำคัญอย่างยิ่ง

## Git Workflow

เราใช้ Git Flow แบบง่ายๆ:

1.  **Fork the repository:** เริ่มจากการคัดลอกโปรเจกต์ไปที่บัญชีของคุณ
2.  **Create a new branch:** แตก Branch ใหม่ออกจาก `main` สำหรับฟีเจอร์หรืองานที่คุณจะทำ
    - ตั้งชื่อ Branch ให้สื่อความหมาย เช่น `feature/user-login` หรือ `fix/lesson-display-bug`
    - `git checkout -b <branch-name>`
3.  **Commit your changes:** ทำการ commit งานของคุณ โดยเขียน commit message ที่ชัดเจนและสื่อความหมาย
4.  **Push to your branch:** `git push origin <branch-name>`
5.  **Create a Pull Request (PR):** เปิด PR จาก Branch ของคุณมายัง `main` ของโปรเจกต์หลัก
    - ในรายละเอียดของ PR ให้อธิบายว่าโค้ดของคุณทำอะไร และเกี่ยวข้องกับ Backlog item ไหน (ถ้ามี)

## Code Style

- เราใช้ **PEP 8** เป็นมาตรฐานหลักในการเขียนโค้ด Python
- เราใช้ Linter (เช่น Ruff หรือ Flake8) เพื่อช่วยตรวจสอบคุณภาพโค้ดโดยอัตโนมัติ กรุณารัน linter ก่อนทำการ commit

## Submitting a Pull Request

- Pull Request ของคุณจะต้องผ่านการตรวจสอบ CI (Continuous Integration) ทั้งหมด
- จะต้องมีผู้ตรวจสอบ (Reviewer) อย่างน้อย 1 คนทำการ approve ก่อนที่จะ merge ได้
