# 🍅 Pomodoro Code Architecture Deep Dive

## 📋 การวิเคราะห์โค้ดเชิงลึก

### 1. Frontend JavaScript Architecture

#### **ไฟล์: `app/static/js/pomodoro.js` (1,694 บรรทัด)**

##### **A. State Management Pattern**

```javascript
// Global State Object - Centralized State Management
let pomodoroState = {
  // Timer State
  mode: 'pomodoro',              // Current mode
  isRunning: false,              // Timer running status
  timeLeft: 25 * 60,             // Remaining time in seconds
  totalTime: 25 * 60,            // Total time for current mode
  cycle: 1,                      // Current cycle number
  
  // Session Management
  currentSessionId: null,        // Backend session ID
  completedPomodoros: 0,         // Completed pomodoros count
  
  // Task Management
  tasks: [],                     // Local tasks array
  
  // Settings
  settings: {
    pomodoro: 25,                // Focus time (minutes)
    shortBreak: 5,               // Short break (minutes)
    longBreak: 15,               // Long break (minutes)
    longBreakInterval: 4,        // Long break every N cycles
    autoStartBreaks: true,
    soundEnabled: true
  },
  
  // Statistics
  stats: {
    // Total Statistics
    totalPomodoros: 0,
    totalFocusTime: 0,
    totalTasks: 0,
    totalBreaks: 0,
    streak: 0,
    
    // Daily Statistics
    todayPomodoros: 0,
    todayFocusTime: 0,
    todayTasks: 0,
    todayBreaks: 0,
    goalCompletionPercent: 0,
    lastDate: new Date().toDateString()
  }
};
```

##### **B. Timer Core Functions**

```javascript
// Timer Control Functions
async function startTimer() {
  // 1. Validate current state
  if (pomodoroState.isRunning) {
    pauseTimer();
    return;
  }

  // 2. Ensure session exists in database
  const sessionReady = await ensureSessionForCurrentMode();
  if (!sessionReady) return;

  // 3. Start timer logic
  pomodoroState.isRunning = true;
  lastTick = Date.now();
  
  // 4. Start dual timer system
  startLocalInterval();   // For UI updates (100ms)
  startGlobalTimer();     // For time tracking (1000ms)
  
  updateButtons();
  saveState();
}

function pauseTimer() {
  pomodoroState.isRunning = false;
  stopAllTimers();
  updateButtons();
  saveState();
}

async function resetTimer() {
  // 1. Stop current timer
  pomodoroState.isRunning = false;
  stopAllTimers();
  
  // 2. Handle active session in database
  if (pomodoroState.currentSessionId) {
    await interruptSessionInDatabase();
    clearCurrentSession();
    await refreshServerStats();
  }
  
  // 3. Reset timer state
  pomodoroState.timeLeft = getModeTime();
  pomodoroState.totalTime = getModeTime();
  
  updateButtons();
  updateDisplay();
  saveState();
}
```

##### **C. Dual Timer System**

```javascript
// Local Timer - High Frequency UI Updates
function startLocalInterval() {
  if (interval) clearInterval(interval);
  
  interval = setInterval(() => {
    if (pomodoroState.isRunning) {
      updateDisplay(); // Update UI only
    }
  }, 100); // 100ms for smooth UI
}

// Global Timer - Actual Time Tracking
function startGlobalTimer() {
  if (globalTimer) clearInterval(globalTimer);
  
  globalTimer = setInterval(() => {
    if (pomodoroState.isRunning) {
      const now = Date.now();
      const delta = Math.floor((now - lastTick) / 1000);
      
      if (delta >= 1) {
        // Accurate time tracking
        pomodoroState.timeLeft = Math.max(0, pomodoroState.timeLeft - delta);
        lastTick = now;
        saveState();
        updateDisplay();
        
        // Timer completion check
        if (pomodoroState.timeLeft === 0) {
          timerComplete().catch(console.error);
        }
      }
    }
  }, 1000); // 1000ms for time accuracy
}
```

##### **D. Session Management with Backend**

```javascript
// Create Session on Server
async function createSessionOnServer(sessionType, duration, taskId = null) {
  try {
    const response = await fetch('/api/pomodoro/session', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify({
        session_type: sessionType,
        duration: duration,
        task_id: taskId
      })
    });

    if (!response.ok) {
      if (response.status === 401) {
        console.info('Session creation requires authentication');
        return null;
      }
      throw new Error(`HTTP ${response.status}`);
    }

    const result = await response.json();
    return result.success ? result.data : null;
  } catch (error) {
    console.error('Error creating session:', error);
    return null;
  }
}

// End Session on Server
async function endSessionOnServer(sessionId, status = 'completed') {
  try {
    const response = await fetch(`/api/pomodoro/session/${sessionId}/end`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify({ status })
    });

    if (response.ok) {
      const result = await response.json();
      return result.success ? result.data : null;
    }
  } catch (error) {
    console.error('Error ending session:', error);
  }
  return null;
}
```

##### **E. Task Integration System**

```javascript
// Task API Mapping
const TASKS_API_BASE = '/api/tasks';

function mapTaskFromApi(task) {
  if (!task) return null;

  return {
    id: task.id || null,
    text: task.title || task.text || '',
    completed: task.status === 'completed' || !!task.completed,
    createdAt: task.created_at || task.createdAt || new Date().toISOString(),
    completedAt: task.completed_at || task.completedAt || null
  };
}

// Create Task with Server Sync
async function createTaskOnServer(title) {
  try {
    const response = await fetch(TASKS_API_BASE, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify({
        title,
        task_type: 'focus',
        priority: 'medium'
      })
    });

    if (response.ok) {
      const result = await response.json();
      return result.success ? mapTaskFromApi(result.data) : null;
    }
    
    // Fallback for unauthenticated users
    if (response.status === 401) {
      console.info('Task creation requires authentication; storing locally.');
      return null;
    }
  } catch (error) {
    console.error('Error creating task:', error);
  }
  return null;
}
```

### 2. Backend Python Architecture

#### **A. Route Layer - API Endpoints**

```python
# File: app/routes/pomodoro_session_routes.py
from flask import Blueprint
from app.controllers.pomodoro_session_views import PomodoroSessionViews
from app.middleware.auth_middleware import login_required

pomodoro_session_bp = Blueprint('pomodoro_session', __name__, 
                               url_prefix='/api/pomodoro/session')
session_views = PomodoroSessionViews()

@pomodoro_session_bp.route('', methods=['POST'])
@login_required
def create_session():
    """Create new Pomodoro session"""
    return session_views.create_session()

@pomodoro_session_bp.route('/<session_id>/end', methods=['POST'])
@login_required  
def end_session(session_id):
    """End Pomodoro session"""
    return session_views.end_session(session_id)
```

#### **B. Controller Layer - Request Handling**

```python
# File: app/controllers/pomodoro_session_views.py
class PomodoroSessionViews:
    def __init__(self):
        self._session_service = PomodoroSessionService()

    def create_session(self) -> Dict[str, Any]:
        """Create a new Pomodoro session"""
        try:
            # 1. Extract user ID
            user_id = 'anonymous'
            if hasattr(g, 'user') and g.user and hasattr(g.user, 'id'):
                user_id = g.user.id

            # 2. Validate request data
            data = request.get_json()
            if not data:
                return jsonify({'error': 'Request data is required'}), 400

            required_fields = ['session_type', 'duration']
            missing_fields = [field for field in required_fields 
                            if field not in data]
            if missing_fields:
                return jsonify({
                    'error': f'Missing required fields: {", ".join(missing_fields)}'
                }), 400

            # 3. Create session via service
            session = self._session_service.create_session(
                user_id=user_id,
                session_type=data['session_type'],
                duration=data['duration'],
                task=data.get('task'),
                lesson_id=data.get('lesson_id'),
                task_id=data.get('task_id')
            )

            # 4. Return success response
            return jsonify({
                'success': True,
                'data': session.to_dict(),
                'message': 'Session created successfully'
            }), 201

        except ValidationException as e:
            return jsonify({'error': str(e)}), 400
        except Exception as e:
            return jsonify({'error': 'Internal server error'}), 500
```

#### **C. Service Layer - Business Logic**

```python
# File: app/services.py
class PomodoroSessionService:
    """Service layer for Pomodoro session management"""

    def create_session(self, user_id: str, session_type: str, duration: int, 
                      task: Optional[str] = None, lesson_id: Optional[str] = None,
                      task_id: Optional[str] = None, **kwargs):
        """Create a new Pomodoro session with validation and business logic."""
        from app.db_instance import db
        from app.models.pomodoro_session import PomodoroSessionModel

        # 1. Validate input parameters
        if not user_id:
            raise ValidationException("User ID is required")

        if session_type not in ['focus', 'short_break', 'long_break']:
            raise ValidationException("Invalid session type")

        if duration <= 0:
            raise ValidationException("Duration must be positive")

        # 2. Handle task linking
        task_title = task.strip() if isinstance(task, str) and task.strip() else None
        resolved_task_id: Optional[str] = None

        if task_id:
            task_service = TaskService()
            try:
                task_entity = task_service.get_task_by_id(task_id, user_id)
                resolved_task_id = task_entity.id
                task_title = task_title or task_entity.title
            except NotFoundException as exc:
                raise ValidationException("Invalid task_id provided") from exc

        # 3. Create session model
        session = PomodoroSessionModel(
            user_id=user_id,
            session_type=session_type,
            duration=duration,
            start_time=datetime.utcnow(),
            task=task_title,
            task_id=resolved_task_id,
            status='active',
            lesson_id=lesson_id,
            is_completed=False,
            is_interrupted=False,
            **kwargs
        )

        # 4. Save to database
        try:
            db.session.add(session)
            db.session.commit()

            # 5. Update statistics
            session_date = session.start_time.date()
            self._update_daily_statistics(user_id, session_date)

            return session
        except Exception as e:
            db.session.rollback()
            raise

    def end_session(self, session_id: str, status: str = 'completed'):
        """End a Pomodoro session with proper cleanup"""
        from app.db_instance import db
        
        # 1. Find session
        session = self.get_session(session_id)
        if not session:
            return None

        # 2. Update session data
        session.end_time = datetime.utcnow()
        session.status = status
        
        # 3. Set completion flags
        if status == 'completed':
            session.is_completed = True
            session.is_interrupted = False
        elif status == 'interrupted':
            session.is_interrupted = True
            session.is_completed = False

        # 4. Calculate actual duration
        if session.start_time:
            duration_seconds = (session.end_time - session.start_time).total_seconds()
            session.actual_duration = int(duration_seconds / 60)

        # 5. Save changes
        db.session.commit()

        # 6. Update statistics
        session_date = session.end_time.date()
        self._update_daily_statistics(session.user_id, session_date)

        return session
```

#### **D. Model Layer - Data Persistence**

```python
# File: app/models/pomodoro_session.py
class PomodoroSessionModel(db.Model):
    """SQLAlchemy model for Pomodoro sessions"""
    __tablename__ = 'pomodoro_session'

    # Primary identifiers
    id = db.Column(db.String(36), primary_key=True, 
                  default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), nullable=False, index=True)

    # Session configuration
    session_type = db.Column(db.String(20), nullable=False)  # focus, short_break, long_break
    duration = db.Column(db.Integer, nullable=False)         # Planned duration (minutes)
    
    # Timing data
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime)
    actual_duration = db.Column(db.Integer)                  # Actual duration (minutes)
    
    # Status tracking
    status = db.Column(db.String(20), default='active', nullable=False)
    is_completed = db.Column(db.Boolean, default=False)
    is_interrupted = db.Column(db.Boolean, default=False)
    interruption_count = db.Column(db.Integer, default=0)
    
    # Related entities
    lesson_id = db.Column(db.String(36))
    task_id = db.Column(db.String(36))
    task = db.Column(db.String(255))  # Task title for quick access
    
    # User preferences
    auto_start_next = db.Column(db.Boolean, default=True)
    notification_enabled = db.Column(db.Boolean, default=True)
    sound_enabled = db.Column(db.Boolean, default=True)
    
    # Session feedback
    productivity_score = db.Column(db.Integer)
    mood_before = db.Column(db.String(50))
    mood_after = db.Column(db.String(50))
    focus_score = db.Column(db.Integer)
    energy_level = db.Column(db.Integer)
    notes = db.Column(db.Text)

    def to_dict(self):
        """Convert model to dictionary for API responses"""
        # Handle task title resolution
        task_title = self.task
        if self.task_id and not task_title:
            from app.models.task import TaskModel
            task = TaskModel.query.get(self.task_id)
            if task:
                task_title = task.title
                
        return {
            'id': self.id,
            'user_id': self.user_id,
            'session_type': self.session_type,
            'duration': self.duration,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'actual_duration': self.actual_duration,
            'status': self.status,
            'is_completed': self.is_completed,
            'is_interrupted': self.is_interrupted,
            'task_id': self.task_id,
            'task': task_title,
            'lesson_id': self.lesson_id,
            'productivity_score': self.productivity_score,
            'mood_before': self.mood_before,
            'mood_after': self.mood_after,
            'focus_score': self.focus_score,
            'energy_level': self.energy_level,
            'notes': self.notes
        }
```

### 3. Database Design

#### **A. Schema Structure**

```sql
-- Main Pomodoro Session Table
CREATE TABLE pomodoro_session (
    -- Primary Key
    id TEXT PRIMARY KEY,
    
    -- User Association
    user_id TEXT NOT NULL,
    
    -- Session Configuration
    session_type TEXT NOT NULL CHECK (session_type IN ('focus', 'short_break', 'long_break')),
    duration INTEGER NOT NULL,  -- Planned duration in minutes
    
    -- Timing Information
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP,
    actual_duration INTEGER,    -- Actual duration in minutes
    
    -- Status Tracking
    status TEXT NOT NULL DEFAULT 'active',
    is_completed BOOLEAN DEFAULT FALSE,
    is_interrupted BOOLEAN DEFAULT FALSE,
    interruption_count INTEGER DEFAULT 0,
    interruption_reasons TEXT,
    
    -- Related Entities
    lesson_id TEXT,
    section_id TEXT,
    task_id TEXT,
    task TEXT,  -- Denormalized task name for performance
    
    -- User Preferences
    auto_start_next BOOLEAN DEFAULT TRUE,
    notification_enabled BOOLEAN DEFAULT TRUE,
    sound_enabled BOOLEAN DEFAULT TRUE,
    
    -- Session Quality Metrics
    notes TEXT,
    productivity_score INTEGER,
    mood_before TEXT,
    mood_after TEXT,
    focus_score INTEGER,
    energy_level INTEGER,
    difficulty_level INTEGER,
    
    -- Audit Fields
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Performance Indexes
CREATE INDEX idx_pomodoro_user ON pomodoro_session(user_id);
CREATE INDEX idx_pomodoro_type ON pomodoro_session(session_type);
CREATE INDEX idx_pomodoro_status ON pomodoro_session(status);
CREATE INDEX idx_pomodoro_start_time ON pomodoro_session(start_time);
CREATE INDEX idx_pomodoro_lesson ON pomodoro_session(lesson_id);
CREATE INDEX idx_pomodoro_completed ON pomodoro_session(is_completed);
```

### 4. Integration Points

#### **A. Authentication Integration**

```python
# Middleware: app/middleware/auth_middleware.py
@login_required
def protected_endpoint():
    # Access user via g.user
    user_id = g.user.id if g.user else 'anonymous'
```

#### **B. Task System Integration**

```javascript
// Frontend task synchronization
async function syncTasksFromServer() {
  const response = await fetch('/api/tasks?limit=100', {
    credentials: 'include'
  });
  
  if (response.ok) {
    const result = await response.json();
    if (result.success) {
      pomodoroState.tasks = result.data.map(mapTaskFromApi);
      updateTaskList();
    }
  }
}
```

#### **C. Statistics Integration**

```python
# Service: Automatic statistics update
def _update_daily_statistics(self, user_id: str, date: date):
    """Update daily statistics when session changes"""
    # Recalculate daily metrics
    sessions = PomodoroSessionModel.query.filter(
        PomodoroSessionModel.user_id == user_id,
        func.date(PomodoroSessionModel.start_time) == date
    ).all()
    
    # Calculate metrics
    completed_sessions = sum(1 for s in sessions if s.is_completed)
    focus_minutes = sum(
        s.actual_duration or s.duration 
        for s in sessions 
        if s.session_type == 'focus'
    )
    
    # Update statistics table
    # ... statistics update logic
```

## 🎯 สรุปจุดเด่นของ Architecture

### 1. **Separation of Concerns**
- Frontend: UI/UX และ State Management
- Backend: Business Logic และ Data Persistence  
- Database: Data Storage และ Integrity

### 2. **Scalability**
- Modular design ทำให้เพิ่มฟีเจอร์ได้ง่าย
- API-first approach รองรับ multiple clients
- Database indexing สำหรับ performance

### 3. **Reliability**
- Dual timer system สำหรับความแม่นยำ
- Error handling และ fallback mechanisms
- Transaction management สำหรับ data consistency

### 4. **User Experience**
- Real-time UI updates
- Offline capability (local storage)
- Seamless authentication handling

นี่คือสถาปัตยกรรมที่แข็งแกร่งและพร้อมสำหรับการพัฒนาต่อยอดในอนาคต!