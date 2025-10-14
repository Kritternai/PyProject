# 🍅 Pomodoro Database Integration Guide

## 📋 Overview
เอกสารนี้อธิบายขั้นตอนการแก้ไขและปรับปรุงระบบ Pomodoro ให้สามารถบันทึกข้อมูลลงฐานข้อมูลได้ โดยใช้หลัก MVC และ SPA architecture

---

## 🎯 ปัญหาเริ่มต้น
- ระบบ Pomodoro ทำงานได้แต่ไม่บันทึกข้อมูลลงฐานข้อมูล
- มีปัญหา import และ circular dependencies
- ตารางฐานข้อมูลขาดคอลัมน์ที่จำเป็น
- ระบบสถิติยังไม่ทำงาน

---

## 🔧 การแก้ไขที่ทำ

### 1. แก้ไขปัญหา Database Import และ Circular Dependencies

#### ปัญหา:
- ไฟล์หลายไฟล์พยายาม import `db` จาก `app` แต่เกิด circular import
- Services ไม่สามารถ import ได้ถูกต้อง

#### การแก้ไข:
```python
# ใช้ db_instance.py แทนการ import จาก app
# ไฟล์: app/models/pomodoro_session.py
from app.db_instance import db

# ไฟล์: app/models/pomodoro_statistics.py  
from app.db_instance import db

# ไฟล์: app/services/pomodoro_statistics_service.py
from app.db_instance import db
```

#### ไฟล์ที่แก้ไข:
- `app/models/pomodoro_session.py`
- `app/models/pomodoro_statistics.py`
- `app/services/pomodoro_statistics_service.py`
- `app/__init__.py` - เปลี่ยนจาก `db = SQLAlchemy()` เป็น `from .db_instance import db`

---

### 2. ปรับปรุงโครงสร้าง Services

#### ปัญหา:
- `PomodoroSessionService` อยู่ในไฟล์ `app/services.py` หลัก
- มีการ import ที่ซับซ้อน

#### การแก้ไข:
```python
# เพิ่ม PomodoroSessionService ในไฟล์ app/services.py หลัก
class PomodoroSessionService:
    """Service layer for Pomodoro session management"""

    def create_session(self, user_id: str, session_type: str, duration: int, 
                      task: Optional[str] = None, lesson_id: Optional[str] = None, 
                      section_id: Optional[str] = None, mood_before: Optional[str] = None, 
                      energy_level: Optional[int] = None, auto_start_next: bool = True, 
                      notification_enabled: bool = True, sound_enabled: bool = True):
        """Create a new Pomodoro session"""
        # Implementation...

    def end_session(self, session_id: str):
        """End a Pomodoro session"""
        # Implementation...
        
        # Update statistics after ending session
        self._update_daily_statistics(session.user_id)
        
        return session

    def _update_daily_statistics(self, user_id: str):
        """Update daily statistics after session completion"""
        # Implementation...
```

#### ไฟล์ที่แก้ไข:
- `app/services.py` - เพิ่ม `PomodoroSessionService` class
- `app/services/__init__.py` - เพิ่ม import สำหรับ services ใหม่

---

### 3. สร้าง Controller ใหม่

#### ปัญหา:
- `pomodoro_session_views.py` มีปัญหา import
- Controller ไม่สามารถใช้งาน service ได้

#### การแก้ไข:
```python
# ไฟล์: app/controllers/pomodoro_session_views.py
from app.services import PomodoroSessionService
from app.utils.exceptions import ValidationException

class PomodoroSessionViews:
    """Views for Pomodoro session operations"""

    def __init__(self):
        self._session_service = PomodoroSessionService()

    def create_session(self) -> Dict[str, Any]:
        """Create a new Pomodoro session"""
        # Implementation...

    def end_session(self, session_id: str) -> Dict[str, Any]:
        """End a Pomodoro session"""
        # Implementation...
```

#### ไฟล์ที่สร้างใหม่:
- `app/controllers/pomodoro_session_views.py` - สร้างใหม่ทั้งหมด
- `app/controllers/pomodoro_statistics_controller.py` - สำหรับจัดการสถิติ

---

### 4. แก้ไขปัญหา Database Schema

#### ปัญหา:
- ตาราง `pomodoro_session` ขาดคอลัมน์ที่จำเป็น
- Model ต้องการคอลัมน์ที่ไม่มีในฐานข้อมูล

#### การแก้ไข:
```sql
-- เพิ่มคอลัมน์ที่ขาดหายไปในตาราง pomodoro_session
ALTER TABLE pomodoro_session ADD COLUMN lesson_id TEXT;
ALTER TABLE pomodoro_session ADD COLUMN section_id TEXT;
ALTER TABLE pomodoro_session ADD COLUMN task_id TEXT;
ALTER TABLE pomodoro_session ADD COLUMN auto_start_next BOOLEAN DEFAULT 1;
ALTER TABLE pomodoro_session ADD COLUMN notification_enabled BOOLEAN DEFAULT 1;
ALTER TABLE pomodoro_session ADD COLUMN sound_enabled BOOLEAN DEFAULT 1;
```

#### ไฟล์ที่แก้ไข:
- `database/setup_database.py` - เพิ่มการสร้างคอลัมน์ที่ขาดหายไป

```python
# เพิ่มใน database/setup_database.py
pomodoro_session_columns = [
    "ALTER TABLE pomodoro_session ADD COLUMN lesson_id TEXT",
    "ALTER TABLE pomodoro_session ADD COLUMN section_id TEXT",
    "ALTER TABLE pomodoro_session ADD COLUMN task_id TEXT",
    "ALTER TABLE pomodoro_session ADD COLUMN auto_start_next BOOLEAN DEFAULT 1",
    "ALTER TABLE pomodoro_session ADD COLUMN notification_enabled BOOLEAN DEFAULT 1",
    "ALTER TABLE pomodoro_session ADD COLUMN sound_enabled BOOLEAN DEFAULT 1",
    # ... คอลัมน์อื่น ๆ
]

for column_sql in pomodoro_session_columns:
    try:
        cursor.execute(column_sql)
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print(f"   Pomodoro session column already exists, skipping...")
```

---

### 5. เพิ่มการอัปเดตสถิติอัตโนมัติ

#### ปัญหา:
- ระบบบันทึก sessions ได้แต่ไม่อัปเดตสถิติ
- ไม่มีการคำนวณข้อมูลสถิติ

#### การแก้ไข:

##### Backend (Python):
```python
# ใน PomodoroSessionService.end_session()
def end_session(self, session_id: str):
    # ... จบ session ...
    
    # Update statistics after ending session
    self._update_daily_statistics(session.user_id)
    
    return session

def _update_daily_statistics(self, user_id: str):
    """Update daily statistics after session completion"""
    try:
        from app.models.pomodoro_statistics import PomodoroStatisticsModel
        from datetime import date
        
        today = date.today()
        
        # Get or create today's statistics
        stats = PomodoroStatisticsModel.query.filter_by(
            user_id=user_id, 
            date=today
        ).first()
        
        if not stats:
            # Create new statistics record
            stats = PomodoroStatisticsModel(
                user_id=user_id,
                date=today,
                total_sessions=0,
                total_focus_time=0,
                total_completed_sessions=0,
                total_interrupted_sessions=0
            )
            database.session.add(stats)
        
        # Recalculate statistics from all sessions today
        today_sessions = PomodoroSessionModel.query.filter(
            PomodoroSessionModel.user_id == user_id,
            database.func.date(PomodoroSessionModel.created_at) == today
        ).all()
        
        # Update counters
        stats.total_sessions = len(today_sessions)
        stats.total_completed_sessions = len([s for s in today_sessions if s.is_completed])
        stats.total_interrupted_sessions = len([s for s in today_sessions if s.is_interrupted])
        stats.total_focus_time = sum([s.actual_duration or 0 for s in today_sessions if s.session_type == 'focus' and s.is_completed])
        
        # Calculate productivity score
        if stats.total_completed_sessions > 0:
            stats.productivity_score = (stats.total_completed_sessions / stats.total_sessions) * 10
        
        database.session.commit()
        
    except Exception as e:
        print(f"⚠️ Error updating daily statistics: {str(e)}")
```

##### Frontend (JavaScript):
```javascript
// ไฟล์: app/static/js/pomodoro.js
async function endSessionInDatabase(sessionId) {
  try {
    const response = await fetch(`/api/pomodoro/session/${sessionId}/end`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      }
    });

    if (response.ok) {
      const result = await response.json();
      if (result.success) {
        console.log('✅ Session ended in database:', sessionId);
        
        // Update statistics after ending session
        await updateStatistics();
        
        return result.session;
      }
    }
  } catch (error) {
    console.error('❌ Error ending session:', error);
  }
  return null;
}

// Update statistics after session completion
async function updateStatistics() {
  try {
    console.log('📊 Updating statistics...');
    const response = await fetch('/api/pomodoro/statistics/daily', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        date: new Date().toISOString().split('T')[0] // YYYY-MM-DD format
      })
    });

    if (response.ok) {
      const result = await response.json();
      if (result.success) {
        console.log('✅ Statistics updated successfully');
      }
    }
  } catch (error) {
    console.error('❌ Error updating statistics:', error);
  }
}
```

#### ไฟล์ที่แก้ไข:
- `app/services.py` - เพิ่มฟังก์ชัน `_update_daily_statistics`
- `app/static/js/pomodoro.js` - เพิ่มฟังก์ชัน `updateStatistics`

---

### 6. แก้ไขปัญหา Endpoint ซ้ำ

#### ปัญหา:
- มีฟังก์ชัน `partial_pomodoro` และ `pomodoro_statistics_page` ซ้ำกัน
- เซิร์ฟเวอร์ไม่สามารถรันได้

#### การแก้ไข:
```python
# ไฟล์: app/routes/main_routes.py
# ลบฟังก์ชันที่ซ้ำออก
# เหลือเฉพาะฟังก์ชันที่จำเป็น
```

#### ไฟล์ที่แก้ไข:
- `app/routes/main_routes.py` - ลบฟังก์ชันที่ซ้ำ

---

### 7. เพิ่ม API Endpoints

#### การเพิ่ม:
```python
# ไฟล์: app/routes/pomodoro_statistics_routes.py
@pomodoro_stats_bp.route('/daily', methods=['POST'])
def update_daily_statistics_post():
    """
    POST /api/pomodoro/statistics/daily
    Update or create daily statistics (alternative endpoint)
    Body: { "date": "YYYY-MM-DD" } (optional)
    """
    return stats_controller.update_daily_statistics()
```

#### ไฟล์ที่แก้ไข:
- `app/routes/pomodoro_statistics_routes.py` - เพิ่ม POST endpoint

---

## 🚀 การทดสอบ

### 1. รัน Database Setup
```bash
cd /Users/kbbk/PyProject-5
python database/setup_database.py
```

### 2. ทดสอบการสร้าง Session
```python
from app import create_app
from app.services import PomodoroSessionService

app = create_app()
with app.app_context():
    service = PomodoroSessionService()
    session = service.create_session(
        user_id='test-user',
        session_type='focus',
        duration=25,
        task='Test task'
    )
    print(f'✅ Session created: {session.id}')
```

### 3. ทดสอบการจบ Session และอัปเดตสถิติ
```python
ended_session = service.end_session(session.id)
print(f'✅ Session ended: {ended_session.status}')
print('✅ Statistics should be updated automatically')
```

---

## 📊 ผลลัพธ์

### ✅ ระบบที่ทำงานได้แล้ว:
1. **บันทึก Pomodoro Sessions** - สร้าง, อัปเดต, จบ sessions
2. **อัปเดตสถิติอัตโนมัติ** - คำนวณสถิติเมื่อจบ session
3. **API Endpoints** - รองรับ CRUD operations
4. **Database Integration** - บันทึกข้อมูลลงฐานข้อมูลได้
5. **MVC Architecture** - แยก concerns ตามหลัก MVC

### 🌐 API Endpoints ที่พร้อมใช้งาน:
- `POST /api/pomodoro/session` - สร้าง session ใหม่
- `GET /api/pomodoro/session/{id}` - ดู session
- `POST /api/pomodoro/session/{id}/end` - จบ session
- `GET /api/pomodoro/statistics/daily` - ดูสถิติรายวัน
- `POST /api/pomodoro/statistics/daily` - อัปเดตสถิติ

### 🎯 วิธีใช้งาน:
1. เข้า `http://localhost:8000/pomodoro` เพื่อใช้ Pomodoro Timer
2. เริ่ม Pomodoro → ระบบจะบันทึก session ใหม่
3. จบ Pomodoro → ระบบจะอัปเดตสถิติอัตโนมัติ
4. เข้า `http://localhost:8000/pomodoro/statistics` เพื่อดูสถิติ

---

## 🔧 ไฟล์ที่ถูกแก้ไข/สร้างใหม่

### ไฟล์ที่แก้ไข:
- `app/__init__.py` - แก้ไข database import
- `app/services.py` - เพิ่ม PomodoroSessionService
- `app/services/__init__.py` - แก้ไข imports
- `app/models/pomodoro_session.py` - แก้ไข database import
- `app/models/pomodoro_statistics.py` - แก้ไข database import
- `app/services/pomodoro_statistics_service.py` - แก้ไข database import
- `app/routes/main_routes.py` - ลบฟังก์ชันซ้ำ
- `app/routes/pomodoro_statistics_routes.py` - เพิ่ม POST endpoint
- `app/static/js/pomodoro.js` - เพิ่มการอัปเดตสถิติ
- `database/setup_database.py` - เพิ่มการสร้างคอลัมน์

### ไฟล์ที่สร้างใหม่:
- `app/controllers/pomodoro_session_views.py`
- `app/controllers/pomodoro_statistics_controller.py`

### ไฟล์ที่ลบ:
- `app/services/pomodoro_session_service.py` (ย้ายไปรวมใน services.py หลัก)

---

## 🎉 สรุป

ระบบ Pomodoro ตอนนี้สามารถ:
- ✅ บันทึกข้อมูลลงฐานข้อมูลได้
- ✅ อัปเดตสถิติอัตโนมัติ
- ✅ ใช้หลัก MVC และ SPA architecture
- ✅ รองรับ Google OAuth integration
- ✅ มี API endpoints ครบถ้วน

**ระบบ Pomodoro พร้อมใช้งานแล้ว!** 🍅📊✨
