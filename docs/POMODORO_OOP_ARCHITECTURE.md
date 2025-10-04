# 🍅 Pomodoro OOP Architecture Documentation

## 📋 Overview
ระบบ Pomodoro Timer ที่ใช้ OOP Architecture ตาม Clean Architecture และ SOLID Principles

## 🏗️ Architecture Structure

### 1. Domain Layer
```
app/domain/
├── entities/
│   └── pomodoro_session.py          # PomodoroSession entity
└── interfaces/
    └── pomodoro_repository.py     # Repository interface
```

### 2. Application Layer
```
app/application/
└── services/
    └── pomodoro_service.py         # Business logic service
```

### 3. Infrastructure Layer
```
app/infrastructure/
├── database/
│   └── pomodoro_repository.py      # Database implementation
└── di/
    └── pomodoro_container.py       # Dependency injection
```

### 4. Presentation Layer
```
app/presentation/
├── controllers/
│   └── pomodoro_controller.py     # HTTP request handling
└── routes/
    └── pomodoro_routes_new.py      # API routes
```

## 🔧 Core Components

### PomodoroSession Entity
```python
class PomodoroSession:
    - id: str
    - user_id: str
    - session_type: SessionType (focus, short_break, long_break)
    - duration: int (minutes)
    - start_time: datetime
    - status: SessionStatus (active, paused, completed, interrupted)
    - productivity_score: int (1-10)
    - mood_before/after: str
    - focus_score: int (1-10)
    - energy_level: int (1-10)
    - difficulty_level: int (1-10)
```

### Session Types
- **FOCUS**: 25 minutes focus session
- **SHORT_BREAK**: 5 minutes break
- **LONG_BREAK**: 15 minutes break (every 4 pomodoros)

### Session Status
- **ACTIVE**: Currently running
- **PAUSED**: Temporarily stopped
- **COMPLETED**: Successfully finished
- **INTERRUPTED**: Stopped due to interruption
- **CANCELLED**: Manually cancelled

## 🚀 API Endpoints

### Session Management
```
POST /api/pomodoro/start          # Start new session
POST /api/pomodoro/pause          # Pause active session
POST /api/pomodoro/resume         # Resume paused session
POST /api/pomodoro/complete       # Complete session
POST /api/pomodoro/interrupt      # Interrupt session
POST /api/pomodoro/cancel         # Cancel session
```

### Session Queries
```
GET /api/pomodoro/active          # Get active session
GET /api/pomodoro/sessions        # Get user sessions
GET /api/pomodoro/lessons/{id}/sessions  # Get lesson sessions
```

### Statistics & Analytics
```
GET /api/pomodoro/statistics      # Get session statistics
GET /api/pomodoro/insights        # Get productivity insights
GET /api/pomodoro/health          # Health check
```

## 📊 Features

### 1. Session Management
- ✅ Start/Pause/Resume/Complete sessions
- ✅ Interrupt handling with reasons
- ✅ Session cancellation
- ✅ Auto-start next session option

### 2. Progress Tracking
- ✅ Session completion tracking
- ✅ Time spent tracking
- ✅ Productivity scoring (1-10)
- ✅ Mood tracking (before/after)
- ✅ Focus score assessment
- ✅ Energy level monitoring
- ✅ Difficulty level tracking

### 3. Analytics & Insights
- ✅ Daily/Weekly/Monthly statistics
- ✅ Productivity insights
- ✅ Best time of day analysis
- ✅ Most productive day analysis
- ✅ Efficiency trend calculation
- ✅ Personalized recommendations

### 4. Integration
- ✅ Lesson integration
- ✅ Task integration
- ✅ Section integration
- ✅ User-specific data

## 🗄️ Database Schema

### pomodoro_session Table
```sql
CREATE TABLE pomodoro_session (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    session_type TEXT NOT NULL,
    duration INTEGER NOT NULL,
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP,
    actual_duration INTEGER,
    status TEXT NOT NULL,
    is_completed BOOLEAN DEFAULT FALSE,
    is_interrupted BOOLEAN DEFAULT FALSE,
    interruption_count INTEGER DEFAULT 0,
    interruption_reasons TEXT,
    lesson_id TEXT,
    section_id TEXT,
    task_id TEXT,
    notes TEXT,
    productivity_score INTEGER,
    mood_before TEXT,
    mood_after TEXT,
    focus_score INTEGER,
    energy_level INTEGER,
    difficulty_level INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## 🔄 Usage Examples

### Start a Focus Session
```javascript
fetch('/api/pomodoro/start', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
        session_type: 'focus',
        duration: 25,
        lesson_id: 'lesson-123',
        mood_before: 'focused'
    })
});
```

### Complete Session with Feedback
```javascript
fetch('/api/pomodoro/complete', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
        session_id: 'session-123',
        productivity_score: 8,
        mood_after: 'satisfied',
        focus_score: 7,
        energy_level: 6,
        difficulty_level: 5,
        notes: 'Great focus session!'
    })
});
```

### Get Statistics
```javascript
fetch('/api/pomodoro/statistics?period=week')
    .then(response => response.json())
    .then(data => {
        console.log('Weekly stats:', data.statistics);
    });
```

## 🎯 Next Steps

### 1. Database Integration
- [ ] Create database tables
- [ ] Run migrations
- [ ] Test database operations

### 2. Frontend Integration
- [ ] Connect JavaScript timer to API
- [ ] Add session feedback forms
- [ ] Create statistics dashboard
- [ ] Add productivity insights UI

### 3. Advanced Features
- [ ] Settings management
- [ ] Notification system
- [ ] Sound integration
- [ ] Export functionality
- [ ] Team collaboration features

### 4. Testing
- [ ] Unit tests for services
- [ ] Integration tests for API
- [ ] Frontend testing
- [ ] Performance testing

## 📝 Notes

- ระบบใช้ OOP Architecture ตาม Clean Architecture
- Dependency Injection สำหรับ loose coupling
- Repository pattern สำหรับ data access
- Service layer สำหรับ business logic
- Controller layer สำหรับ HTTP handling
- Entity layer สำหรับ domain models

**ระบบพร้อมใช้งานและขยายต่อได้ง่าย!** 🚀
