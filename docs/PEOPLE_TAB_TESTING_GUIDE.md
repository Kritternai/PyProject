# 🧪 People Tab Testing Guide

## 📋 การทดสอบระบบ People Tab

### เตรียมการทดสอบ

1. **รัน Database Migration:**
```bash
cd /Users/kbbk/PyProject-5
python database/setup_database.py
```

2. **สร้าง Test Users (ถ้ายังไม่มี):**
```python
python scripts/database/run_fresh_db.py
```

3. **เริ่ม Server:**
```bash
python start_server.py
```

---

## ✅ **TODO 13: ทดสอบการเพิ่ม/ลบสมาชิก และ Permissions**

### Test Case 1: ทดสอบการเข้าถึง People Tab
**Steps:**
1. Login เข้าระบบ
2. สร้าง Class ใหม่หรือเลือก Class ที่มี
3. คลิก tab "People"
4. ✅ ควรเห็นหน้า People โหลดสำเร็จ
5. ✅ ควรเห็น Owner (ตัวคุณเอง) แสดงอยู่
6. ✅ Summary Stats แสดงถูกต้อง (1 Owner, 0 Viewers)

---

### Test Case 2: ทดสอบการค้นหา User
**Steps:**
1. อยู่ใน People tab
2. คลิกปุ่ม "Add Member"
3. พิมพ์ username ใน search box
4. ✅ ควรเห็น loading spinner ขณะค้นหา
5. ✅ ผลลัพธ์แสดงภายใน 1 วินาที
6. ✅ แสดงเฉพาะ users ที่ยังไม่ได้เป็นสมาชิก
7. ✅ ไม่แสดงตัวเอง (Owner)

---

### Test Case 3: ทดสอบการเพิ่มสมาชิก (Owner Permission)
**Prerequisites:** ต้องเป็น Owner ของ Class

**Steps:**
1. คลิก "Add Member"
2. ค้นหา user ที่ต้องการเพิ่ม
3. คลิกปุ่ม "Add" ข้าง user นั้น
4. ✅ แสดง success message
5. ✅ Modal ปิดอัตโนมัติ
6. ✅ รายชื่อสมาชิกอัพเดททันที
7. ✅ User ที่เพิ่มแสดงใน "Viewers" section
8. ✅ Stats อัพเดท (Viewers +1, Total +1)
9. ✅ Role badge แสดง "Viewer"

---

### Test Case 4: ทดสอบการลบสมาชิก (Owner Permission)
**Prerequisites:** ต้องเป็น Owner และมีอย่างน้อย 1 Viewer

**Steps:**
1. หา Viewer ใน list
2. คลิกปุ่มลบ (trash icon) สีแดง
3. ✅ แสดง confirmation dialog
4. คลิก Confirm
5. ✅ แสดง success message
6. ✅ User หายจาก list ทันที
7. ✅ Stats อัพเดท (Viewers -1, Total -1)

---

### Test Case 5: ทดสอบ Viewer Permission (Read-only)
**Prerequisites:** มี Class ที่ถูกเชิญเป็น Viewer

**Steps:**
1. Login ด้วย account ที่เป็น Viewer
2. เข้าไปดู Class ที่ถูกเชิญ
3. คลิก People tab
4. ✅ สามารถดู People tab ได้
5. ✅ เห็น Owner และ Viewers อื่นๆ
6. ✅ **ไม่มีปุ่ม "Add Member"** (ซ่อนอยู่)
7. ✅ **ไม่มีปุ่มลบสมาชิก** (ไม่มี trash icon)
8. ทดลองเรียก API โดยตรง: `POST /api/class/{id}/members`
9. ✅ ได้ Error 403 Forbidden

---

### Test Case 6: ทดสอบ Non-Member Permission
**Prerequisites:** มี Class ที่ไม่ใช่ของคุณและไม่ได้ถูกเชิญ

**Steps:**
1. Login ด้วย account อื่น
2. ลองเข้า URL: `/class/{lesson_id}` ของคนอื่น
3. คลิก People tab
4. ✅ แสดง error message "You do not have permission"
5. ทดลองเรียก API: `GET /api/class/{id}/members`
6. ✅ ได้ Error 403 Forbidden

---

### Test Case 7: ทดสอบ Duplicate Prevention
**Steps:**
1. เพิ่ม user A เป็น member
2. ลองเพิ่ม user A อีกครั้ง
3. ✅ แสดง error: "User is already a member"
4. ✅ ไม่มี duplicate ใน list

---

### Test Case 8: ทดสอบ Owner Protection
**Steps:**
1. ลองลบ Owner ออกจาก Class
2. ✅ ไม่มีปุ่มลบที่ Owner card
3. ถ้าเรียก API โดยตรง: `DELETE /api/class/{id}/members/{owner_id}`
4. ✅ ได้ Error 400: "Cannot remove owner"

---

## ✅ **TODO 14: ทดสอบ UI Responsive Design**

### Test Case 1: Desktop View (1920x1080)
**Steps:**
1. เปิด browser แบบ full screen (≥ 1024px)
2. เข้า People tab
3. ✅ Sidebar แสดงด้านซ้าย (sticky position)
4. ✅ Content area กว้างเต็มที่
5. ✅ Member cards แสดงแบบ full width
6. ✅ Stats grid แสดง 3 columns

---

### Test Case 2: Tablet View (768x1024)
**Steps:**
1. เปิด DevTools (F12)
2. เลือก device: iPad (768px)
3. ✅ Layout ปรับเป็น single column
4. ✅ Sidebar ปรากฏด้านบน
5. ✅ ปุ่ม hamburger menu ไม่แสดง (ยังไม่จำเป็น)
6. ✅ Member cards ย่อขนาดเล็กลง
7. ✅ Text ยังอ่านได้ชัดเจน

---

### Test Case 3: Mobile View (375x667 - iPhone)
**Steps:**
1. เลือก device: iPhone 12 (390px)
2. ✅ Sidebar ซ่อนโดย default
3. ✅ ปุ่ม hamburger (list icon) แสดงใน header
4. คลิกปุ่ม hamburger
5. ✅ Sidebar slide in จากซ้าย
6. ✅ Overlay (backdrop) แสดง
7. คลิก overlay
8. ✅ Sidebar ปิดกลับไป
9. ✅ Stats grid แสดงแบบ vertical (1 column)
10. ✅ Member cards compact (avatar + info stacked)
11. ✅ Action buttons ย้ายลง row ใหม่

---

### Test Case 4: Mobile - Add Member Modal
**Steps:**
1. อยู่ใน mobile view
2. คลิก "Add Member"
3. ✅ Modal เต็มจอ (responsive)
4. ✅ Search input ใช้งานได้สะดวก
5. ✅ Search results แสดงแบบ stack
6. ✅ ปุ่ม "Add" อยู่ใน position ที่กดง่าย
7. ✅ Keyboard ไม่บัง content (scroll ได้)

---

### Test Case 5: Small Mobile (320x568 - iPhone SE)
**Steps:**
1. เลือก device: iPhone SE (320px)
2. ✅ ทุกอย่างยัง functional
3. ✅ Text ไม่ overflow
4. ✅ Buttons ขนาดพอกด (min 44x44px)
5. ✅ Member cards ไม่บีบจนเกินไป

---

### Test Case 6: Landscape Mode (Mobile)
**Steps:**
1. หมุน device เป็น landscape
2. ✅ Layout ปรับตาม
3. ✅ Sidebar แสดงถ้าพื้นที่พอ
4. ✅ Content ใช้พื้นที่อย่างมีประสิทธิภาพ

---

### Test Case 7: Touch Gestures (Mobile/Tablet)
**Steps:**
1. ใช้ touch screen หรือ Chrome DevTools (touch mode)
2. ✅ Scroll ราบรื่น
3. ✅ Tap ปุ่มใช้งานได้ (ไม่ต้อง double-tap)
4. ✅ Hover effects ไม่ติดค้าง
5. ✅ Swipe sidebar ปิดได้ (ถ้า implement)

---

### Test Case 8: Cross-Browser Testing

**Browsers to test:**
- ✅ Chrome (latest)
- ✅ Firefox (latest)
- ✅ Safari (latest) - important for Mac/iOS
- ✅ Edge (latest)

**Check:**
1. ✅ CSS gradients แสดงถูกต้อง
2. ✅ Backdrop blur ทำงาน (หรือ fallback สวย)
3. ✅ Flexbox/Grid layout ถูกต้อง
4. ✅ Fonts โหลดครบ (Bootstrap Icons)
5. ✅ JavaScript ทำงานปกติ

---

## 🐛 **Common Issues & Fixes**

### Issue 1: Member list ไม่อัพเดท
**Fix:** เช็ค console errors, verify API endpoints

### Issue 2: Search ไม่ทำงาน
**Fix:** เช็ค network tab, verify `/api/users/search` endpoint

### Issue 3: Permission error 403
**Fix:** ตรวจสอบว่า user เป็น owner หรือ member จริง

### Issue 4: Sidebar ไม่ปิดใน mobile
**Fix:** เช็ค overlay event listener, verify CSS classes

### Issue 5: CSS ไม่โหลด
**Fix:** เช็ค path: `/static/css/people.css`

---

## ✅ **Pass Criteria**

### Functionality (TODO 13)
- [x] Owner สามารถเพิ่มสมาชิกได้
- [x] Owner สามารถลบสมาชิกได้
- [x] Viewer เห็นแค่รายชื่อ (read-only)
- [x] Non-member ไม่สามารถเข้าถึงได้
- [x] Search users ทำงานถูกต้อง
- [x] Real-time update หลังเพิ่ม/ลบ
- [x] Stats แสดงถูกต้อง

### UI/UX (TODO 14)
- [x] Desktop view สวยงาม
- [x] Tablet view ใช้งานได้
- [x] Mobile view responsive
- [x] Touch gestures ทำงาน
- [x] Cross-browser compatible
- [x] Colors สอดคล้องกับ design system
- [x] Loading states ชัดเจน
- [x] Error messages เข้าใจง่าย

---

## 📊 **Test Summary Template**

```
✅ TODO 13: Permissions & Functionality Testing
  - Test Case 1: People Tab Access [PASS/FAIL]
  - Test Case 2: Search Users [PASS/FAIL]
  - Test Case 3: Add Member (Owner) [PASS/FAIL]
  - Test Case 4: Remove Member (Owner) [PASS/FAIL]
  - Test Case 5: Viewer Permission [PASS/FAIL]
  - Test Case 6: Non-Member Permission [PASS/FAIL]
  - Test Case 7: Duplicate Prevention [PASS/FAIL]
  - Test Case 8: Owner Protection [PASS/FAIL]

✅ TODO 14: Responsive Design Testing
  - Test Case 1: Desktop (1920px) [PASS/FAIL]
  - Test Case 2: Tablet (768px) [PASS/FAIL]
  - Test Case 3: Mobile (375px) [PASS/FAIL]
  - Test Case 4: Add Member Modal (Mobile) [PASS/FAIL]
  - Test Case 5: Small Mobile (320px) [PASS/FAIL]
  - Test Case 6: Landscape Mode [PASS/FAIL]
  - Test Case 7: Touch Gestures [PASS/FAIL]
  - Test Case 8: Cross-Browser [PASS/FAIL]
```

---

**Ready to Test!** 🚀
เมื่อทดสอบเสร็จแล้ว กรุณารายงานผลตามTemplate ด้านบน

