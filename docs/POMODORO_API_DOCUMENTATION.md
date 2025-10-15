# 🍅 Pomodoro API Documentation & Usage Examples

## 📚 API Reference

### 1. Pomodoro Session API

#### **Base URL:** `/api/pomodoro/session`

---

#### **POST /api/pomodoro/session**
สร้าง Pomodoro session ใหม่

**Headers:**
```
Content-Type: application/json
Cookie: session=<session_id>
```

**Request Body:**
```json
{
  "session_type": "focus",           // Required: "focus", "short_break", "long_break"
  "duration": 25,                    // Required: Duration in minutes
  "task": "Complete project docs",   // Optional: Task description
  "task_id": "task_123",            // Optional: Link to existing task
  "lesson_id": "lesson_456",        // Optional: Link to lesson
  "section_id": "section_789",      // Optional: Link to lesson section
  "mood_before": "focused",         // Optional: Mood before session
  "energy_level": 8,                // Optional: Energy level (1-10)
  "auto_start_next": true,          // Optional: Auto-start next session
  "notification_enabled": true,     // Optional: Enable notifications
  "sound_enabled": true             // Optional: Enable sound alerts
}
```

**Response (201 Created):**
```json
{
  "success": true,
  "data": {
    "id": "session_abc123",
    "user_id": "user_456",
    "session_type": "focus",
    "duration": 25,
    "start_time": "2025-10-15T10:30:00.000Z",
    "end_time": null,
    "actual_duration": null,
    "status": "active",
    "is_completed": false,
    "is_interrupted": false,
    "task": "Complete project docs",
    "task_id": "task_123",
    "lesson_id": "lesson_456"
  },
  "message": "Session created successfully"
}
```

**Error Responses:**
```json
// 400 Bad Request - Missing required fields
{
  "error": "Bad Request",
  "message": "Missing required fields: session_type, duration",
  "code": "MISSING_FIELDS"
}

// 401 Unauthorized
{
  "error": "Unauthorized", 
  "message": "Authentication required"
}

// 422 Validation Error
{
  "error": "Validation Error",
  "message": "Invalid session type"
}
```

---

#### **GET /api/pomodoro/session/<session_id>**
ดูข้อมูล session เฉพาะ

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "id": "session_abc123",
    "user_id": "user_456", 
    "session_type": "focus",
    "duration": 25,
    "start_time": "2025-10-15T10:30:00.000Z",
    "end_time": "2025-10-15T10:55:00.000Z",
    "actual_duration": 25,
    "status": "completed",
    "is_completed": true,
    "is_interrupted": false,
    "productivity_score": 8,
    "mood_after": "accomplished",
    "focus_score": 9,
    "notes": "Great focus session!"
  }
}
```

---

#### **POST /api/pomodoro/session/<session_id>/end**
จบ session

**Request Body:**
```json
{
  "status": "completed",           // "completed", "interrupted"
  "productivity_score": 8,         // Optional: 1-10
  "mood_after": "accomplished",    // Optional: Post-session mood
  "focus_score": 9,               // Optional: Focus quality 1-10
  "notes": "Great session!"       // Optional: Session notes
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "id": "session_abc123",
    "status": "completed",
    "end_time": "2025-10-15T10:55:00.000Z",
    "actual_duration": 25,
    "is_completed": true
  },
  "message": "Session ended successfully"
}
```

---

#### **GET /api/pomodoro/session/user**
ดู sessions ทั้งหมดของ user ปัจจุบัน

**Query Parameters:**
```
limit=50          // Optional: Limit results (default: 50)
offset=0          // Optional: Offset for pagination  
status=completed  // Optional: Filter by status
date=2025-10-15  // Optional: Filter by date
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": [
    {
      "id": "session_abc123",
      "session_type": "focus",
      "duration": 25,
      "start_time": "2025-10-15T10:30:00.000Z",
      "status": "completed"
    },
    {
      "id": "session_def456", 
      "session_type": "short_break",
      "duration": 5,
      "start_time": "2025-10-15T10:55:00.000Z",
      "status": "completed"
    }
  ],
  "pagination": {
    "total": 25,
    "limit": 50,
    "offset": 0,
    "has_more": false
  }
}
```

---

#### **GET /api/pomodoro/session/active**
ดู active session ของ user

**Response (200 OK) - มี active session:**
```json
{
  "success": true,
  "data": {
    "id": "session_xyz789",
    "session_type": "focus",
    "duration": 25,
    "start_time": "2025-10-15T11:00:00.000Z",
    "status": "active",
    "time_elapsed": 600,  // seconds since start
    "time_remaining": 900 // seconds remaining
  }
}
```

**Response (200 OK) - ไม่มี active session:**
```json
{
  "success": true,
  "data": null,
  "message": "No active session found"
}
```

---

### 2. Pomodoro Statistics API

#### **Base URL:** `/api/pomodoro/statistics`

---

#### **GET /api/pomodoro/statistics/timer**
ดูสถิติรวมของ timer

**Response (200 OK):**
```json
{
  "success": true,
  "stats": {
    "total_pomodoros": 127,
    "total_focus_minutes": 3175,    // Total focus time in minutes
    "total_tasks_completed": 45,
    "total_break_sessions": 98,
    "streak": 5,                    // Current daily streak
    "average_session_length": 24.8,
    "productivity_score_avg": 7.2,
    "total_interruptions": 12
  }
}
```

---

#### **GET /api/pomodoro/statistics/daily-progress**
ดูความก้าวหน้ารายวัน

**Query Parameters:**
```
date=2025-10-15  // Optional: Specific date (default: today)
```

**Response (200 OK):**
```json
{
  "success": true,
  "progress": {
    "date": "2025-10-15",
    "completed_sessions": 8,
    "focus_minutes": 200,
    "break_sessions": 6,
    "tasks_completed": 3,
    "goal_completion_percent": 80,
    "average_focus_score": 8.2,
    "productivity_trend": "increasing"
  }
}
```

---

#### **POST /api/pomodoro/statistics/daily**
อัปเดตสถิติรายวัน (Recalculate)

**Request Body:**
```json
{
  "date": "2025-10-15"  // Optional: Date to recalculate (default: today)
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Daily statistics updated successfully",
  "updated_date": "2025-10-15"
}
```

---

#### **POST /api/pomodoro/statistics/productivity**
ดูรายงานประสิทธิภาพ

**Request Body:**
```json
{
  "start_date": "2025-10-01",
  "end_date": "2025-10-15",
  "group_by": "day"  // "day", "week", "month"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "report": {
    "period": {
      "start_date": "2025-10-01",
      "end_date": "2025-10-15",
      "total_days": 15
    },
    "summary": {
      "total_sessions": 120,
      "total_focus_time": 3000,
      "average_daily_pomodoros": 8.0,
      "completion_rate": 85.5,
      "best_day": "2025-10-10",
      "most_productive_time": "09:00-11:00"
    },
    "daily_breakdown": [
      {
        "date": "2025-10-01",
        "sessions": 8,
        "focus_minutes": 200,
        "completion_rate": 87.5,
        "productivity_score": 8.1
      }
      // ... more days
    ]
  }
}
```

---

## 🛠 Usage Examples

### 1. JavaScript Frontend Integration

#### **A. เริ่ม Pomodoro Session**

```javascript
async function startPomodoroSession() {
  try {
    // สร้าง session ใหม่
    const response = await fetch('/api/pomodoro/session', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      credentials: 'include',
      body: JSON.stringify({
        session_type: 'focus',
        duration: 25,
        task: 'Complete feature development',
        auto_start_next: true,
        sound_enabled: true
      })
    });

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }

    const result = await response.json();
    
    if (result.success) {
      // เก็บ session ID สำหรับใช้ต่อ
      pomodoroState.currentSessionId = result.data.id;
      
      // เริ่มจับเวลา
      startTimer();
      
      console.log('Session started:', result.data);
    } else {
      console.error('Failed to create session:', result.message);
    }
  } catch (error) {
    console.error('Error starting session:', error);
    // Fallback: ทำงานแบบ offline
    startOfflineTimer();
  }
}
```

#### **B. จบ Session และบันทึกผลลัพธ์**

```javascript
async function completeSession(sessionId, feedback = {}) {
  try {
    const response = await fetch(`/api/pomodoro/session/${sessionId}/end`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      credentials: 'include',
      body: JSON.stringify({
        status: 'completed',
        productivity_score: feedback.productivity || 8,
        mood_after: feedback.mood || 'satisfied',
        focus_score: feedback.focus || 7,
        notes: feedback.notes || ''
      })
    });

    if (response.ok) {
      const result = await response.json();
      
      // อัปเดตสถิติใน UI
      await refreshServerStats();
      
      // เปลี่ยนไปโหมดถัดไป
      nextMode();
      
      console.log('Session completed:', result.data);
    }
  } catch (error) {
    console.error('Error completing session:', error);
  }
}
```

#### **C. ดึงสถิติและอัปเดต UI**

```javascript
async function refreshServerStats() {
  try {
    // ดึงสถิติทั้ง 2 ประเภท
    const [timerResponse, dailyResponse] = await Promise.all([
      fetch('/api/pomodoro/statistics/timer', { credentials: 'include' }),
      fetch('/api/pomodoro/statistics/daily-progress', { credentials: 'include' })
    ]);

    // ประมวลผลสถิติ timer
    if (timerResponse.ok) {
      const timerData = await timerResponse.json();
      if (timerData.success) {
        pomodoroState.stats.totalPomodoros = timerData.stats.total_pomodoros;
        pomodoroState.stats.totalFocusTime = timerData.stats.total_focus_minutes;
        pomodoroState.stats.streak = timerData.stats.streak;
      }
    }

    // ประมวลผลสถิติรายวัน
    if (dailyResponse.ok) {
      const dailyData = await dailyResponse.json();
      if (dailyData.success) {
        pomodoroState.stats.todayPomodoros = dailyData.progress.completed_sessions;
        pomodoroState.stats.todayFocusTime = dailyData.progress.focus_minutes;
        pomodoroState.stats.goalCompletionPercent = dailyData.progress.goal_completion_percent;
      }
    }

    // อัปเดต UI
    updateStatsDisplay();
    
  } catch (error) {
    console.error('Error fetching statistics:', error);
  }
}
```

### 2. Python Backend Usage

#### **A. การใช้งาน Service Layer**

```python
from app.services import PomodoroSessionService

# สร้าง service instance
session_service = PomodoroSessionService()

# สร้าง session ใหม่
session = session_service.create_session(
    user_id='user_123',
    session_type='focus',
    duration=25,
    task='Review code changes',
    task_id='task_456'
)

print(f"Created session: {session.id}")

# อัปเดต session
updated_session = session_service.update_session(session.id, {
    'productivity_score': 9,
    'mood_after': 'accomplished',
    'notes': 'Very productive session!'
})

# จบ session
completed_session = session_service.end_session(session.id, 'completed')
```

#### **B. การใช้งาน Statistics Service**

```python
from app.services import PomodoroStatisticsService
from datetime import date

stats_service = PomodoroStatisticsService()

# ดูสถิติรายวัน
daily_stats = stats_service.get_daily_progress('user_123', date.today())
print(f"Today's pomodoros: {daily_stats['completed_sessions']}")

# ดูสถิติรวม
timer_stats = stats_service.get_timer_stats('user_123')
print(f"Total focus time: {timer_stats['total_focus_minutes']} minutes")

# สร้างรายงานประสิทธิภาพ
report = stats_service.get_productivity_report(
    user_id='user_123',
    start_date=date(2025, 10, 1),
    end_date=date(2025, 10, 15)
)
```

### 3. Database Queries

#### **A. ดู Sessions ของ User**

```sql
-- ดู sessions ทั้งหมดของ user
SELECT id, session_type, duration, start_time, end_time, status
FROM pomodoro_session 
WHERE user_id = 'user_123'
ORDER BY start_time DESC
LIMIT 10;

-- ดู sessions ที่เสร็จสิ้นวันนี้
SELECT COUNT(*) as completed_today
FROM pomodoro_session 
WHERE user_id = 'user_123'
  AND DATE(start_time) = DATE('now')
  AND is_completed = 1;
```

#### **B. คำนวณสถิติ**

```sql
-- สถิติรายวัน
SELECT 
    DATE(start_time) as session_date,
    COUNT(*) as total_sessions,
    SUM(CASE WHEN is_completed = 1 THEN 1 ELSE 0 END) as completed_sessions,
    SUM(CASE WHEN session_type = 'focus' AND is_completed = 1 
             THEN COALESCE(actual_duration, duration) ELSE 0 END) as focus_minutes
FROM pomodoro_session 
WHERE user_id = 'user_123'
  AND start_time >= DATE('now', '-30 days')
GROUP BY DATE(start_time)
ORDER BY session_date DESC;

-- Top productive hours
SELECT 
    strftime('%H', start_time) as hour,
    COUNT(*) as sessions,
    AVG(productivity_score) as avg_productivity
FROM pomodoro_session
WHERE user_id = 'user_123'
  AND productivity_score IS NOT NULL
GROUP BY strftime('%H', start_time)
ORDER BY avg_productivity DESC;
```

### 4. Error Handling Patterns

#### **A. Frontend Error Handling**

```javascript
async function apiCall(url, options = {}) {
  try {
    const response = await fetch(url, {
      credentials: 'include',
      ...options
    });

    // Check HTTP status
    if (!response.ok) {
      if (response.status === 401) {
        console.warn('Authentication required');
        // Redirect to login or show auth modal
        return null;
      }
      
      if (response.status === 422) {
        const errorData = await response.json();
        throw new ValidationError(errorData.message);
      }
      
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }

    const data = await response.json();
    
    // Check API success flag
    if (!data.success) {
      throw new Error(data.message || 'API call failed');
    }

    return data;
    
  } catch (error) {
    console.error('API call failed:', error);
    
    // Show user-friendly error message
    showErrorNotification(error.message);
    
    return null;
  }
}
```

#### **B. Backend Error Handling**

```python
from app.utils.exceptions import ValidationException, NotFoundException

def create_session_endpoint():
    try:
        # Business logic
        session = session_service.create_session(...)
        
        return jsonify({
            'success': True,
            'data': session.to_dict()
        }), 201
        
    except ValidationException as e:
        return jsonify({
            'success': False,
            'error': 'Validation Error',
            'message': str(e)
        }), 422
        
    except NotFoundException as e:
        return jsonify({
            'success': False,
            'error': 'Not Found', 
            'message': str(e)
        }), 404
        
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return jsonify({
            'success': False,
            'error': 'Internal Server Error',
            'message': 'An unexpected error occurred'
        }), 500
```

## 🔍 Testing Examples

### 1. API Testing with curl

```bash
# Create session
curl -X POST http://localhost:5000/api/pomodoro/session \
  -H "Content-Type: application/json" \
  -d '{
    "session_type": "focus",
    "duration": 25,
    "task": "API testing"
  }'

# Get user sessions
curl -X GET http://localhost:5000/api/pomodoro/session/user

# End session
curl -X POST http://localhost:5000/api/pomodoro/session/abc123/end \
  -H "Content-Type: application/json" \
  -d '{
    "status": "completed",
    "productivity_score": 8
  }'
```

### 2. JavaScript Testing

```javascript
// Test session creation
async function testSessionCreation() {
  const sessionData = {
    session_type: 'focus',
    duration: 25,
    task: 'Test task'
  };
  
  const result = await apiCall('/api/pomodoro/session', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(sessionData)
  });
  
  console.assert(result.success, 'Session creation should succeed');
  console.assert(result.data.id, 'Session should have ID');
  console.assert(result.data.status === 'active', 'New session should be active');
}
```

นี่คือเอกสาร API ที่ครบถ้วนสำหรับระบบ Pomodoro พร้อมตัวอย่างการใช้งานในทุกระดับ!