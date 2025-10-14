# 📊 Grade System Documentation

## 🎯 Overview

ระบบ Grades สำหรับ Smart Learning Hub ที่ช่วยให้นักเรียนสามารถ:
- ติดตามคะแนนและเกรดของตัวเอง
- คำนวณว่าต้องทำคะแนนเท่าไหร่เพื่อได้เกรดที่ต้องการ
- ตั้งค่าเกณฑ์การตัดเกรดตาม Syllabus
- วิเคราะห์ผลการเรียนแต่ละหมวดหมู่

---

## 🏗️ Architecture (MVC Pattern)

### **Model** - Database Layer
```
database/models/grade.py
├── GradeConfig      - การตั้งค่าเกรดของวิชา
├── GradeCategory    - หมวดหมู่งาน (Assignments, Quizzes)
├── GradeItem        - รายการงานแต่ละอัน
├── GradeEntry       - คะแนนที่นักเรียนได้
└── GradeSummary     - สรุปคะแนนรวม (cached)
```

### **Controller** - Business Logic
```
app/controllers/grade_views.py
└── GradeController
    ├── create_grade_config()
    ├── create_category()
    ├── create_grade_item()
    ├── submit_grade()
    ├── calculate_grade_summary()    # คำนวณคะแนนรวม
    ├── calculate_goal()             # Goal Calculator
    └── calculate_what_if()          # What-If Calculator
```

### **View** - Presentation Layer
```
app/templates/class_detail/_grades.html
├── Grade Summary Card
├── Grade Goals Display
├── Category Breakdown
├── Detailed Grades Table
└── Goal Calculator Modal
```

### **Routes** - HTTP Endpoints
```
app/routes/grade_routes.py
├── GET  /grades/lessons/<id>/config
├── POST /grades/lessons/<id>/config
├── GET  /grades/lessons/<id>/categories
├── POST /grades/lessons/<id>/categories
├── GET  /grades/lessons/<id>/items
├── POST /grades/lessons/<id>/items
├── GET  /grades/lessons/<id>/my-grades
├── GET  /grades/lessons/<id>/summary
├── POST /grades/items/<id>/submit
├── POST /grades/lessons/<id>/goal-calculator
└── GET  /grades/partial/class/<id>/grades
```

---

## 📊 Database Schema

### **1. grade_config** - การตั้งค่าเกรด
```sql
CREATE TABLE grade_config (
    id TEXT PRIMARY KEY,
    lesson_id TEXT UNIQUE NOT NULL,
    grading_scale TEXT NOT NULL,        -- JSON: {"A": {"min": 80, ...}}
    grading_type TEXT DEFAULT 'percentage',
    total_points REAL DEFAULT 100,
    passing_grade TEXT DEFAULT 'D',
    passing_percentage REAL DEFAULT 50.0,
    show_total_grade BOOLEAN DEFAULT 1,
    allow_what_if BOOLEAN DEFAULT 1,
    show_class_average BOOLEAN DEFAULT 0,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    FOREIGN KEY (lesson_id) REFERENCES lesson(id)
);
```

### **2. grade_category** - หมวดหมู่งาน
```sql
CREATE TABLE grade_category (
    id TEXT PRIMARY KEY,
    lesson_id TEXT NOT NULL,
    name TEXT NOT NULL,                 -- "Assignments", "Midterm"
    description TEXT,
    weight REAL NOT NULL,               -- น้ำหนัก % (0-100)
    total_points REAL,
    drop_lowest INTEGER DEFAULT 0,      -- ตัดคะแนนต่ำสุดกี่ตัว
    drop_highest INTEGER DEFAULT 0,
    color TEXT DEFAULT '#3B82F6',
    icon TEXT DEFAULT 'bi-clipboard',
    order_index INTEGER DEFAULT 0,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    FOREIGN KEY (lesson_id) REFERENCES lesson(id)
);
```

### **3. grade_item** - รายการงาน
```sql
CREATE TABLE grade_item (
    id TEXT PRIMARY KEY,
    lesson_id TEXT NOT NULL,
    category_id TEXT NOT NULL,
    name TEXT NOT NULL,                 -- "Homework 1"
    description TEXT,
    points_possible REAL NOT NULL,      -- คะแนนเต็ม
    due_date TIMESTAMP,
    published_date TIMESTAMP,
    is_published BOOLEAN DEFAULT 0,
    is_extra_credit BOOLEAN DEFAULT 0,
    is_muted BOOLEAN DEFAULT 0,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    FOREIGN KEY (lesson_id) REFERENCES lesson(id),
    FOREIGN KEY (category_id) REFERENCES grade_category(id)
);
```

### **4. grade_entry** - คะแนนนักเรียน
```sql
CREATE TABLE grade_entry (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    lesson_id TEXT NOT NULL,
    grade_item_id TEXT NOT NULL,
    score REAL,                         -- คะแนนที่ได้
    points_possible REAL,               -- คะแนนเต็ม (snapshot)
    status TEXT DEFAULT 'pending',      -- pending, graded, excused
    is_excused BOOLEAN DEFAULT 0,
    comments TEXT,                      -- ความเห็นจากครู
    graded_by TEXT,
    graded_at TIMESTAMP,
    is_late BOOLEAN DEFAULT 0,
    late_penalty REAL DEFAULT 0,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES user(id),
    FOREIGN KEY (lesson_id) REFERENCES lesson(id),
    FOREIGN KEY (grade_item_id) REFERENCES grade_item(id)
);
```

### **5. grade_summary** - สรุปคะแนน (Cached)
```sql
CREATE TABLE grade_summary (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    lesson_id TEXT NOT NULL,
    current_score REAL,
    total_possible REAL,
    percentage REAL,
    letter_grade TEXT,
    gpa REAL,
    is_passing BOOLEAN DEFAULT 1,
    points_to_pass REAL,
    points_to_next_grade TEXT,          -- JSON
    last_calculated TIMESTAMP,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES user(id),
    FOREIGN KEY (lesson_id) REFERENCES lesson(id),
    UNIQUE(user_id, lesson_id)
);
```

---

## 🎯 Key Features

### **1. Flexible Grading Scale**
- กำหนดเกณฑ์การตัดเกรดได้เอง (A = 80+, B+ = 75-79, etc.)
- รองรับ percentage-based และ points-based grading
- กำหนด passing grade ได้

### **2. Category-Based Grading**
- แบ่งคะแนนเป็นหมวดหมู่ตาม Syllabus
- กำหนดน้ำหนักแต่ละหมวด (รวม 100%)
- คำนวณคะแนนถ่วงน้ำหนักอัตโนมัติ

### **3. Goal Calculator** 🎯
- คำนวณว่าต้องได้คะแนนเท่าไหร่เพื่อได้เกรดที่ต้องการ
- แสดงข้อความแบบ "Need 8 more points to get A"
- แสดงว่าต้องทำคะแนน % เท่าไหร่ในงานที่เหลือ

### **4. Real-time Grade Display**
- แสดงเกรดปัจจุบัน (Letter Grade + GPA + Percentage)
- แสดงคะแนนแต่ละ category
- Progress bar แสดงความก้าวหน้า

### **5. What-If Calculator**
- ลองคำนวณว่าถ้าได้คะแนนนี้ จะเกิดอะไรขึ้น
- Compare กับคะแนนจริง

---

## 💡 How to Use

### **Step 1: Setup Grading System**
1. เข้าหน้า Class Detail
2. คลิก "Grades" tab
3. คลิก "Setup Grading System"
4. กำหนด Categories และ Weight ตาม Syllabus
5. Save Configuration

### **Step 2: Add Assignments**
1. เพิ่มรายการงาน (Homework, Quiz, Exam)
2. กำหนดคะแนนเต็มและ due date
3. Publish เมื่อพร้อม

### **Step 3: Submit Grades**
1. กรอกคะแนนที่ได้
2. ระบบจะคำนวณเกรดรวมอัตโนมัติ

### **Step 4: Use Goal Calculator**
1. คลิก "Goal Calculator"
2. เลือกเกรดที่ต้องการ (A, B+, B, etc.)
3. ดูว่าต้องทำคะแนนเท่าไหร่

---

## 🎨 UI Components

### **Grade Summary Card**
```
┌─────────────────────────────────────┐
│  Current Grade                      │
│  ┌──────┐  ┌─────────────────────┐│
│  │      │  │  85.5%              ││
│  │  A   │  │  ████████████░░     ││
│  │ 4.0  │  │  342 / 400 points   ││
│  └──────┘  └─────────────────────┘│
└─────────────────────────────────────┘
```

### **Grade Goals Display**
```
┌─────────────────────────────────────┐
│  🎯 Grade Goals                     │
│                                     │
│  ✅ You already have an A!          │
│  ⬆️  Need 8 points to maintain A    │
│  ⚠️  5 points from dropping to B+   │
└─────────────────────────────────────┘
```

### **Category Breakdown**
```
┌─────────────────────────────────────┐
│  📈 Category Breakdown              │
│                                     │
│  Assignments    40%    88% ████████ │
│  Quizzes        20%    75% ██████   │
│  Midterm        20%    85% ███████  │
│  Final          20%    --  ░░░░░░   │
└─────────────────────────────────────┘
```

---

## 🧪 Testing

### **Run Test Data Script**
```bash
# สร้างข้อมูลทดสอบ
python scripts/tests/test_grade_system.py
```

### **Expected Output**
```
🧪 Creating test data for Grade System...
✅ Found test user: 1
✅ Created lesson: Test Course: Database Systems
✅ Created grade configuration
✅ Created category: Assignments (40.0%)
✅ Created category: Quizzes (20.0%)
✅ Created category: Midterm Exam (20.0%)
✅ Created category: Final Exam (20.0%)
...
📊 GRADE SUMMARY
Current Grade: A (85.20%)
GPA: 4.0
Status: ✅ Passing
```

### **Manual Testing Checklist**
- [ ] เปิด Class Detail page
- [ ] คลิก Grades tab
- [ ] ตรวจสอบ Grade Summary Card แสดงผลถูกต้อง
- [ ] ตรวจสอบ Grade Goals แสดงผล
- [ ] ตรวจสอบ Category Breakdown
- [ ] ตรวจสอบ Grades Table
- [ ] ทดสอบ Goal Calculator
- [ ] ทดสอบ Setup Grading Modal

---

## 📚 API Examples

### **1. Get Grade Summary**
```bash
GET /grades/lessons/{lesson_id}/summary
```

**Response:**
```json
{
  "success": true,
  "data": {
    "percentage": 85.5,
    "letter_grade": "A",
    "gpa": 4.0,
    "is_passing": true,
    "category_breakdown": {
      "cat-id-1": {
        "name": "Assignments",
        "weight": 40.0,
        "percentage": 88.0,
        "weighted_score": 35.2
      }
    },
    "goals": {
      "A": {
        "achievable": true,
        "already_achieved": true,
        "message": "You already have an A!"
      },
      "B+": {...}
    }
  }
}
```

### **2. Goal Calculator**
```bash
POST /grades/lessons/{lesson_id}/goal-calculator
Content-Type: application/json

{
  "target_grade": "A"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "target_grade": "A",
    "current_grade": "B+",
    "current_percentage": 77.5,
    "goal_info": {
      "achievable": true,
      "points_needed": 8.0,
      "percentage_needed": 92.0,
      "message": "Need 8.0 more points to get A (92% on remaining work)"
    }
  }
}
```

### **3. Create Category**
```bash
POST /grades/lessons/{lesson_id}/categories
Content-Type: application/json

{
  "name": "Assignments",
  "weight": 40.0,
  "color": "#3B82F6",
  "description": "Homework assignments"
}
```

---

## 🎓 Grading Scale (Default - Thai University System)

| Grade | Percentage | GPA | Description |
|-------|------------|-----|-------------|
| A     | 80-100%    | 4.0 | Excellent |
| B+    | 75-79%     | 3.5 | Very Good |
| B     | 70-74%     | 3.0 | Good |
| C+    | 65-69%     | 2.5 | Fairly Good |
| C     | 60-64%     | 2.0 | Fair |
| D+    | 55-59%     | 1.5 | Poor |
| D     | 50-54%     | 1.0 | Very Poor |
| F     | 0-49%      | 0.0 | Fail |

---

## 🚀 Quick Start

### **1. สร้าง Database Tables**
```bash
python database/setup_database.py
```

### **2. สร้าง Test Data**
```bash
python scripts/tests/test_grade_system.py
```

### **3. เปิดเว็บ**
```bash
python start_server.py
```

### **4. ทดสอบระบบ**
1. Login: email=`1`, password=`1`
2. ไปที่ Class Detail page
3. คลิก "Grades" tab
4. ทดสอบ Goal Calculator

---

## 🎯 Core Calculation Logic

### **การคำนวณคะแนนรวม**
```python
# 1. ดึงคะแนนแต่ละ category
for category in categories:
    category_percentage = (earned / possible) * 100
    weighted_score = category_percentage * (weight / 100)
    total_weighted_score += weighted_score

# 2. หาเกรด
letter_grade = get_letter_grade(total_weighted_score, grading_scale)

# 3. คำนวณ GPA
gpa = grading_scale[letter_grade]['gpa']
```

### **Goal Calculator Logic**
```python
# คำนวณคะแนนที่ต้องได้เพิ่ม
points_needed = target_percentage - current_percentage

# คำนวณ % ที่ต้องทำในงานที่เหลือ
percentage_needed = (points_needed / total_remaining_points) * 100

# ตรวจสอบว่าเป็นไปได้หรือไม่
if points_needed > total_remaining_points:
    achievable = False
else:
    achievable = True
```

---

## 📈 Example Scenario

### **Syllabus Configuration:**
```
Assignments:    40% (5 homeworks @ 20 pts each = 100 pts)
Quizzes:        20% (3 quizzes @ 10 pts each = 30 pts)
Midterm Exam:   20% (100 pts)
Final Exam:     20% (100 pts)
```

### **Current Grades:**
```
✅ Homework 1: 18/20 (90%)
✅ Homework 2: 17/20 (85%)
✅ Homework 3: 19/20 (95%)
✅ Homework 4: 16/20 (80%)
⏳ Homework 5: --/20 (pending)

✅ Quiz 1: 8/10 (80%)
✅ Quiz 2: 7/10 (70%)
⏳ Quiz 3: --/10 (pending)

✅ Midterm: 85/100 (85%)
⏳ Final: --/100 (pending)
```

### **Calculated Grade:**
```
Assignments:  87.5% × 40% = 35.0%
Quizzes:      75.0% × 20% = 15.0%
Midterm:      85.0% × 20% = 17.0%
Final:         0.0% × 20% =  0.0%
                           ------
Current Grade:              67.0% (C+)

With remaining work (HW5, Quiz3, Final):
Need 13 more points to get A (87% on remaining work)
```

---

## 🛠️ Configuration Options

### **Grade Config Settings**
- `grading_type`: 'percentage' หรือ 'points'
- `passing_percentage`: เปอร์เซ็นต์ขั้นต่ำที่ผ่าน (default: 50%)
- `allow_what_if`: เปิด/ปิด What-If Calculator
- `show_class_average`: แสดงคะแนนเฉลี่ยของชั้นเรียน

### **Category Settings**
- `weight`: น้ำหนัก % (รวมต้อง = 100%)
- `drop_lowest`: ตัดคะแนนต่ำสุดกี่ตัว
- `drop_highest`: ตัดคะแนนสูงสุดกี่ตัว

---

## 🔮 Future Enhancements

### **Phase 2 (Nice to Have)**
- [ ] Grade Analytics Dashboard
- [ ] Grade Trends Chart
- [ ] Performance Predictions (AI)
- [ ] Export to PDF/CSV
- [ ] Grade Notifications
- [ ] Class Comparison
- [ ] Achievement Badges

---

## 📞 Support

หากพบปัญหาหรือต้องการความช่วยเหลือ:
- ดูเอกสาร API: `/docs/API_DOCUMENTATION.md`
- ตรวจสอบ logs: `instance/` folder
- รัน tests: `scripts/tests/test_grade_system.py`

---

**Created:** October 10, 2025  
**Version:** 1.0  
**Status:** ✅ Production Ready

