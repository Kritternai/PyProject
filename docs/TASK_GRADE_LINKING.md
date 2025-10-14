# 🔗 Task-Grade Linking System

## 🎯 **ระบบนี้ทำอะไร?**

เชื่อมโยง **Classwork Tasks** กับ **Grade Items** เข้าด้วยกัน เพื่อ:
- ✅ ไม่ต้องสร้างซ้ำซ้อน (Task 1 ชิ้น = Grade Item 1 ชิ้น)
- ✅ ติดตามได้ว่า task ไหนมีผลต่อเกรด
- ✅ เห็นความสัมพันธ์ระหว่างงานที่ทำกับคะแนนที่ได้
- ✅ จัดการง่ายขึ้น

---

## 📊 **ตัวอย่างการใช้งาน**

### **ก่อนมี Task Linking:**
```
Classwork Tab:
  📋 Homework Chapter 1 (To Do)
  📋 Quiz Preparation (In Progress)
  📋 Midterm Study (Done)

Grades Tab:
  📝 Homework 1 (20 pts) - No score
  📝 Quiz 1 (10 pts) - No score
  📝 Midterm (100 pts) - No score

❌ ปัญหา:
   - ซ้ำซ้อน! ทำ 2 ที่
   - ไม่รู้ว่า Task ไหนเกี่ยวกับ Grade ไหน
   - ต้องจำว่าอันไหนคืออันไหน
```

### **หลังมี Task Linking:**
```
Classwork Tab:
  ✅ Homework Chapter 1 (Done) 
     🔗 Linked to: Homework 1 (18/20 pts - 90%)

Grades Tab:
  📝 Homework 1 (20 pts) - 18 pts (90%)
     🔗 Linked to: Homework Chapter 1 (Done)

✅ ข้อดี:
   - เชื่อมโยงกัน! เห็นความสัมพันธ์ชัดเจน
   - คลิกจาก Task ไป Grade หรือกลับกันได้
   - รู้ว่างานที่ทำมีผลต่อคะแนนอย่างไร
```

---

## 🏗️ **Technical Implementation**

### **Database Schema**
```sql
-- เพิ่ม column ใน grade_item
ALTER TABLE grade_item 
ADD COLUMN classwork_task_id TEXT;

-- Foreign key constraint
FOREIGN KEY (classwork_task_id) 
    REFERENCES classwork_task(id) 
    ON DELETE SET NULL
```

### **Model Update**
```python
# app/models/grade.py
class GradeItem(db.Model):
    # ... existing fields ...
    
    # Link to Classwork Task
    classwork_task_id = db.Column(db.String(36), nullable=True)
```

### **Controller Method**
```python
# app/controllers/grade_views.py
@staticmethod
def get_available_tasks(lesson_id: str):
    """Get tasks that haven't been linked yet"""
    # Query tasks NOT IN (linked grade items)
    return available_tasks
```

### **API Endpoint**
```http
GET /grades/lessons/<lesson_id>/available-tasks
```

---

## 🎨 **UI Features**

### **1. Create Grade Item Modal**
```
┌──────────────────────────────────────┐
│  📝 Add Assignment/Exam              │
├──────────────────────────────────────┤
│                                      │
│  Assignment Name: [_______________]  │
│  Points: [____]                      │
│  Category: [Assignments ▼]           │
│                                      │
│  🔗 Link to Classwork Task:          │
│  [-- Select Task ▼]                  │
│    - 📋 Homework Chapter 1           │
│    - 🔄 Quiz Preparation             │
│    - ✅ Midterm Study                │
│                                      │
│  [Cancel] [Create Assignment]        │
└──────────────────────────────────────┘
```

### **2. Grades Table with Link**
```
┌────────────────────────────────────────────────┐
│  Assignment         Category    Score  Status  │
├────────────────────────────────────────────────┤
│  Homework 1         Assign      18/20  Graded  │
│  🔗 Homework Ch.1                               │
│                                                 │
│  Quiz 1             Quiz         8/10  Graded  │
│  🔗 Quiz Prep                                   │
└────────────────────────────────────────────────┘
```

---

## 🚀 **How to Use**

### **Scenario 1: สร้าง Grade Item ใหม่ พร้อม Link Task**

1. ไปที่ **Grades tab**
2. คลิก **"Add Assignment"**
3. กรอกข้อมูล:
   - Assignment Name: "Homework 1"
   - Points: 20
   - Category: "Assignments"
   - **🔗 Link to Task**: เลือก "Homework Chapter 1"
4. คลิก **"Create Assignment"**

**ผลลัพธ์:**
- ✅ สร้าง Grade Item "Homework 1" 
- ✅ Link กับ Task "Homework Chapter 1"
- ✅ Task จะไม่ปรากฏใน dropdown อีก (ถูก link แล้ว)

---

### **Scenario 2: สร้าง Grade Item โดยไม่ Link**

1. ไปที่ **Grades tab**
2. คลิก **"Add Assignment"**
3. กรอกข้อมูล
4. **ไม่เลือก Task** (เว้นว่างไว้)
5. คลิก **"Create Assignment"**

**ผลลัพธ์:**
- ✅ สร้าง Grade Item ได้ตามปกติ
- ✅ ไม่มี link ไปหา task

---

### **Scenario 3: ดู Linked Task ใน Grades Table**

```
Table แสดง:
┌─────────────────────────────────┐
│  Homework 1                     │
│  🔗 Homework Chapter 1          │ ← แสดง task ที่ link
│                                 │
│  Score: 18/20 (90%)             │
│  Status: Graded                 │
└─────────────────────────────────┘
```

---

## 🔄 **Data Flow**

```
User Creates Grade Item
        ↓
Select Task from Dropdown
        ↓
Save with classwork_task_id
        ↓
Database Links:
  grade_item.classwork_task_id → classwork_task.id
        ↓
Display in Grades Table:
  "Homework 1 🔗 Homework Chapter 1"
```

---

## 💡 **Smart Features**

### **1. Auto-populate from Task**
เมื่อเลือก Task จาก dropdown:
- ✅ ชื่อ assignment จะเติมอัตโนมัติ (ถ้าว่าง)
- ✅ Due date จะเติมจาก task (ถ้าว่าง)
- ✅ Description จะเติมจาก task (ถ้าว่าง)

### **2. Available Tasks Only**
Dropdown แสดงเฉพาะ tasks ที่:
- ✅ ยังไม่ถูก link กับ grade item อื่น
- ✅ อยู่ในวิชาเดียวกัน
- ✅ เรียงตามวันที่สร้าง (ล่าสุดก่อน)

### **3. Visual Indicators**
```
✅ Homework Chapter 1    ← Task done
🔄 Quiz Preparation      ← Task in progress
📋 Midterm Study         ← Task todo
```

---

## 📊 **Benefits**

| ข้อดี | คำอธิบาย |
|-------|----------|
| **ไม่ซ้ำซ้อน** | สร้าง task ครั้งเดียว link กับ grade |
| **เห็นความสัมพันธ์** | รู้ว่า task ไหนมีผลต่อคะแนน |
| **ติดตามง่าย** | เห็นสถานะทั้ง task และ grade |
| **จัดการง่าย** | แก้ไขที่เดียว ส่งผลทั้ง 2 ที่ |
| **UX ดีขึ้น** | ไม่ต้องจำว่าอันไหนคืออันไหน |

---

## 🎯 **Use Cases**

### **Use Case 1: Track Assignment Progress**
```
Task Status: In Progress (50%)
Grade: Not submitted yet

→ นักเรียนเห็นว่ายังต้องทำงานให้เสร็จก่อนส่งให้คะแนน
```

### **Use Case 2: Understand Grade Impact**
```
Task: Homework 1 (Done ✅)
Grade: 18/20 pts (90%)
Category: Assignments (40% weight)
Contribution: 36% to final grade

→ นักเรียนเห็นว่างานที่ทำมีผลต่อเกรดมากแค่ไหน
```

### **Use Case 3: Prioritize Work**
```
Available Tasks:
  - 📋 Homework 5 (Not linked)    → ควรทำ
  - 📋 Extra Credit (Not linked)  → ทำถ้ามีเวลา
  
Linked Tasks:
  - ✅ Homework 1-4 (All done)    → เสร็จแล้ว

→ นักเรียนรู้ว่าควรทำอะไรต่อ
```

---

## 🧪 **Testing Guide**

### **Test 1: Create Linked Grade Item**
```bash
# 1. สร้าง task ใน Classwork tab
# 2. ไป Grades tab
# 3. คลิก "Add Assignment"
# 4. เลือก task จาก dropdown
# 5. Save

Expected:
✅ Grade item created
✅ Linked to task
✅ Task ไม่แสดงใน dropdown อีก
✅ แสดง link icon ใน grades table
```

### **Test 2: View Linked Task**
```bash
# 1. ดู Grades table
# 2. หา assignment ที่ link แล้ว

Expected:
✅ แสดงชื่อ assignment
✅ แสดง 🔗 + task title ข้างล่าง
✅ แสดง category badge
```

### **Test 3: Multiple Links**
```bash
# 1. สร้าง 5 tasks ใน Classwork
# 2. Link ทีละตัวกับ grade items

Expected:
✅ Task แต่ละตัว link ได้ครั้งเดียว
✅ หลัง link แล้วหายจาก dropdown
✅ แสดงใน grades table ครบถ้วน
```

---

## 🎊 **สรุป**

### **ก่อนมี Linking:**
- ❌ ต้องสร้าง 2 ครั้ง (task + grade item)
- ❌ ไม่เห็นความเชื่อมโยง
- ❌ จัดการยาก

### **หลังมี Linking:**
- ✅ สร้างครั้งเดียว link เข้าด้วยกัน
- ✅ เห็นความเชื่อมโยงชัดเจน
- ✅ จัดการง่าย ไม่สับสน

---

**พร้อมใช้งานแล้วครับ! 🚀**

รัน server แล้วทดสอบได้เลย:
```bash
python start_server.py
```

---

**Created:** October 10, 2025  
**Version:** 1.0 - Task-Grade Linking  
**Status:** ✅ Production Ready

