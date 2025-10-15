# Class System OOP Documentation

## Overview
This document describes the Object-Oriented Programming (OOP) implementation of the Class/Lesson system in the Smart Learning Hub application. The system follows the 4 Pillars of OOP: Encapsulation, Inheritance, Polymorphism, and Abstraction.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     Class System OOP                        │
├─────────────────────────────────────────────────────────────┤
│  BaseLessonService (Abstract Base Class)                   │
│  ├── LessonService (Main Implementation)                   │
│  ├── GoogleClassroomLessonService (Platform Specific)      │
│  └── MicrosoftTeamsLessonService (Platform Specific)       │
├─────────────────────────────────────────────────────────────┤
│  LessonServiceFactory (Factory Pattern)                    │
├─────────────────────────────────────────────────────────────┤
│  LessonController (MVC Controller)                         │
├─────────────────────────────────────────────────────────────┤
│  LessonModel (SQLAlchemy Model)                            │
└─────────────────────────────────────────────────────────────┘
```

## Core Classes

### 1. BaseLessonService (Abstraction)

**File:** `app/services.py`

**Purpose:** Abstract base class that defines the common interface for all lesson services.

**Key Features:**
- Defines validation methods for all subclasses
- Provides database session management
- Establishes common interface for lesson operations

```python
class BaseLessonService:
    def __init__(self):
        from app import db
        self._db = db
        self._model_class = None
    
    def _validate_user_id(self, user_id: str) -> bool:
        # Validates user ID format
    
    def _validate_lesson_id(self, lesson_id: str) -> bool:
        # Validates lesson ID format
    
    def _validate_title(self, title: str) -> bool:
        # Validates lesson title
```

**OOP Principle:** **Abstraction** - Hides implementation details and provides a common interface.

### 2. LessonService (Inheritance + Encapsulation)

**File:** `app/services.py`

**Purpose:** Main lesson service that handles all lesson-related business logic.

**Key Features:**
- Extends BaseLessonService (Inheritance)
- Implements comprehensive CRUD operations
- Uses private/protected methods (Encapsulation)
- Provides statistics and analytics

```python
class LessonService(BaseLessonService):
    def __init__(self):
        super().__init__()
        from app.models.lesson import LessonModel
        self._model_class = LessonModel
        self._max_title_length = 200
        self._max_description_length = 1000
    
    # Private methods (Encapsulation)
    def _create_lesson_model(self, user_id: str, title: str, **kwargs):
        # Creates lesson model instance
    
    def _validate_lesson_data(self, user_id: str, title: str, **kwargs):
        # Validates lesson data
    
    def _get_lesson_query(self, user_id: str = None, lesson_id: str = None, status: str = None):
        # Builds database queries
    
    def _commit_changes(self):
        # Commits database changes with error handling
    
    # Public interface methods
    def create_lesson(self, user_id: str, title: str, **kwargs):
        # Creates new lesson with validation
    
    def get_lessons_by_user(self, user_id: str):
        # Gets all lessons for a user
    
    def get_lesson_by_id(self, lesson_id: str):
        # Gets lesson by ID
    
    def update_lesson(self, lesson_id: str, user_id: str, **kwargs):
        # Updates lesson with authorization
    
    def delete_lesson(self, lesson_id: str, user_id: str):
        # Deletes lesson with authorization
    
    def toggle_favorite(self, lesson_id: str, user_id: str):
        # Toggles lesson favorite status
    
    # Statistics methods
    def get_lessons_count(self, user_id: str) -> int:
        # Gets total lesson count
    
    def get_completed_lessons_count(self, user_id: str) -> int:
        # Gets completed lesson count
    
    def get_lessons_completed_today(self, user_id: str) -> int:
        # Gets today's completed lessons
    
    def get_lesson_statistics(self, user_id: str) -> dict:
        # Gets comprehensive statistics
```

**OOP Principles:**
- **Inheritance:** Extends BaseLessonService
- **Encapsulation:** Private methods (`_create_lesson_model`, `_validate_lesson_data`, etc.)
- **Data Hiding:** Database session and model class are encapsulated

### 3. GoogleClassroomLessonService (Polymorphism)

**File:** `app/services.py`

**Purpose:** Specialized service for Google Classroom integration.

**Key Features:**
- Overrides base methods for Google Classroom specific logic
- Handles Google Classroom API integration
- Provides platform-specific validation

```python
class GoogleClassroomLessonService(LessonService):
    def __init__(self):
        super().__init__()
        self._source_platform = 'google_classroom'
        self._external_api_client = None
    
    def create_lesson(self, user_id: str, title: str, external_id: str = None, **kwargs):
        # Overrides base method for Google Classroom specific logic
        if not external_id:
            raise ValueError("Google Classroom course ID is required")
        
        kwargs.update({
            'source_platform': self._source_platform,
            'external_id': external_id,
            'external_url': f"https://classroom.google.com/c/{external_id}"
        })
        
        return super().create_lesson(user_id, title, **kwargs)
    
    def sync_with_google_classroom(self, lesson_id: str):
        # Google Classroom specific method
        lesson = self.get_lesson_by_id(lesson_id)
        
        if lesson.source_platform != self._source_platform:
            raise ValueError("Lesson is not a Google Classroom lesson")
        
        return lesson
```

**OOP Principle:** **Polymorphism** - Overrides base methods to provide different behavior for Google Classroom.

### 4. MicrosoftTeamsLessonService (Polymorphism)

**File:** `app/services.py`

**Purpose:** Specialized service for Microsoft Teams integration.

**Key Features:**
- Overrides base methods for Microsoft Teams specific logic
- Handles Microsoft Graph API integration
- Provides platform-specific validation

```python
class MicrosoftTeamsLessonService(LessonService):
    def __init__(self):
        super().__init__()
        self._source_platform = 'microsoft_teams'
        self._external_api_client = None
    
    def create_lesson(self, user_id: str, title: str, external_id: str = None, **kwargs):
        # Overrides base method for Microsoft Teams specific logic
        if not external_id:
            raise ValueError("Microsoft Teams team ID is required")
        
        kwargs.update({
            'source_platform': self._source_platform,
            'external_id': external_id,
            'external_url': f"https://teams.microsoft.com/l/team/{external_id}"
        })
        
        return super().create_lesson(user_id, title, **kwargs)
    
    def sync_with_microsoft_teams(self, lesson_id: str):
        # Microsoft Teams specific method
        lesson = self.get_lesson_by_id(lesson_id)
        
        if lesson.source_platform != self._source_platform:
            raise ValueError("Lesson is not a Microsoft Teams lesson")
        
        return lesson
```

**OOP Principle:** **Polymorphism** - Overrides base methods to provide different behavior for Microsoft Teams.

### 5. LessonServiceFactory (Factory Pattern)

**File:** `app/services.py`

**Purpose:** Factory class to create appropriate lesson service instances.

**Key Features:**
- Creates services based on platform type
- Provides dynamic service selection
- Supports extensibility for new platforms

```python
class LessonServiceFactory:
    @staticmethod
    def create_lesson_service(platform: str = 'manual') -> BaseLessonService:
        if platform == 'manual':
            return LessonService()
        elif platform == 'google_classroom':
            return GoogleClassroomLessonService()
        elif platform == 'microsoft_teams':
            return MicrosoftTeamsLessonService()
        else:
            raise ValueError(f"Unsupported platform: {platform}")
    
    @staticmethod
    def get_service_for_lesson(lesson_model) -> BaseLessonService:
        platform = getattr(lesson_model, 'source_platform', 'manual')
        return LessonServiceFactory.create_lesson_service(platform)
```

**OOP Principle:** **Factory Pattern** - Encapsulates object creation logic.

### 6. LessonController (MVC Controller)

**File:** `app/controllers/lesson_views.py`

**Purpose:** MVC Controller that handles HTTP requests and responses for lesson operations.

**Key Features:**
- Handles request/response logic
- Delegates business logic to services
- Manages authentication and authorization
- Provides comprehensive error handling

```python
class LessonController:
    def __init__(self):
        self._lesson_service = LessonService()
    
    def create_lesson(self) -> Dict[str, Any]:
        # Handles lesson creation requests
    
    def get_lesson(self, lesson_id: str) -> Dict[str, Any]:
        # Handles lesson retrieval requests
    
    def get_user_lessons(self) -> Dict[str, Any]:
        # Handles user lessons listing
    
    def update_lesson(self, lesson_id: str) -> Dict[str, Any]:
        # Handles lesson updates
    
    def delete_lesson(self, lesson_id: str) -> Dict[str, Any]:
        # Handles lesson deletion
    
    def change_lesson_status(self, lesson_id: str) -> Dict[str, Any]:
        # Handles status changes
    
    def update_lesson_progress(self, lesson_id: str) -> Dict[str, Any]:
        # Handles progress updates
    
    def toggle_favorite(self, lesson_id: str) -> Dict[str, Any]:
        # Handles favorite toggling
    
    def search_lessons(self) -> Dict[str, Any]:
        # Handles lesson search
    
    def get_lesson_statistics(self) -> Dict[str, Any]:
        # Handles statistics requests
```

**OOP Principle:** **Single Responsibility** - Handles only HTTP request/response logic.

### 7. LessonModel (Data Model)

**File:** `app/models/lesson.py`

**Purpose:** SQLAlchemy model that represents the lesson entity in the database.

**Key Features:**
- Maps to database table
- Provides data validation
- Includes relationships and constraints
- Offers serialization methods

```python
class LessonModel(db.Model):
    __tablename__ = 'lesson'
    
    # Basic lesson information
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('user.id'), nullable=False, index=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    
    # Lesson status and progress
    status = db.Column(db.String(50), default='not_started', nullable=False, index=True)
    progress_percentage = db.Column(db.Integer, default=0)
    
    # Lesson metadata
    difficulty_level = db.Column(db.String(20), default='beginner')
    estimated_duration = db.Column(db.Integer)
    color_theme = db.Column(db.Integer, default=1)
    is_favorite = db.Column(db.Boolean, default=False, index=True)
    
    # External platform integration
    source_platform = db.Column(db.String(50), default='manual', index=True)
    external_id = db.Column(db.String(100), index=True)
    external_url = db.Column(db.String(500))
    
    # Lesson content
    author_name = db.Column(db.String(100))
    subject = db.Column(db.String(100))
    grade_level = db.Column(db.String(20))
    
    # Statistics
    total_sections = db.Column(db.Integer, default=0)
    completed_sections = db.Column(db.Integer, default=0)
    total_time_spent = db.Column(db.Integer, default=0)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def to_dict(self):
        # Converts model to dictionary for API responses
```

**OOP Principle:** **Data Encapsulation** - Encapsulates lesson data and behavior.

### 8. LessonSectionModel (Related Model)

**File:** `app/models/lesson_section.py`

**Purpose:** SQLAlchemy model for lesson sections within a lesson.

**Key Features:**
- Represents lesson content sections
- Links to lesson via foreign key
- Supports ordering and categorization

```python
class LessonSectionModel(db.Model):
    __tablename__ = 'lesson_section'

    # Section identification
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    lesson_id = db.Column(db.String(36), db.ForeignKey('lesson.id'), nullable=False, index=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=True)

    # Basic classification and ordering
    section_type = db.Column(db.String(50), nullable=False, index=True, default='text')
    order_index = db.Column(db.Integer, default=0, nullable=False)

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
```

## Class Detail System

### Class Detail Page Structure

The class detail system consists of multiple tabs and components:

#### 1. Class Detail Route
**File:** `app/routes/class_routes.py`

```python
@class_bp.route('/class/<lesson_id>')
def view_detail(lesson_id):
    """View class detail page with tabs"""
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    try:
        lesson_service = LessonService()
        lesson = lesson_service.get_lesson_by_id(lesson_id)
        
        if not lesson:
            return jsonify({'error': 'Lesson not found'}), 404
        
        return render_template('class_detail.html', 
                             lesson=lesson, 
                             user=g.user)
    except Exception as e:
        print(f"Error loading class detail: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500
```

#### 2. Classwork Tab
**File:** `app/routes/class_routes.py`

```python
@class_bp.route('/partial/class/<lesson_id>/classwork')
def partial_classwork(lesson_id):
    """Classwork partial for specific class"""
    # Handles classwork data (tasks and materials)
    
@class_bp.route('/class/<lesson_id>/classwork')
def get_classwork_data(lesson_id):
    """Get classwork data (tasks and materials) for a lesson"""
    # Returns JSON data for classwork tasks and materials
```

#### 3. People Tab
**File:** `app/routes/class_routes.py`

```python
@class_bp.route('/partial/class/<lesson_id>/people')
def partial_people(lesson_id):
    """People partial for specific class"""
    # Handles people/members management

@class_bp.route('/api/class/<lesson_id>/members', methods=['GET'])
def get_members(lesson_id):
    """Get all members of a class"""
    # Returns JSON data for class members

@class_bp.route('/api/class/<lesson_id>/members', methods=['POST'])
def add_member(lesson_id):
    """Add a member to a class"""
    # Handles adding new members

@class_bp.route('/api/class/<lesson_id>/members/<user_id>', methods=['DELETE'])
def remove_member(lesson_id, user_id):
    """Remove a member from a class"""
    # Handles member removal
```

#### 4. Stream Tab
**File:** `app/routes/class_routes.py`

```python
@class_bp.route('/partial/class/<lesson_id>/stream')
def partial_stream(lesson_id):
    """Stream partial for specific class (Q&A + Announcements)"""
    # Handles stream/activity feed
```

#### 5. Settings Tab
**File:** `app/routes/class_routes.py`

```python
@class_bp.route('/partial/class/<lesson_id>/settings')
@login_required_web
def partial_settings(lesson_id):
    """Settings fragment for a specific class"""
    # Handles class settings

@class_bp.route('/api/class/<lesson_id>/settings', methods=['PUT'])
@login_required_web
def update_class_settings(lesson_id):
    """Update class settings"""
    # Handles settings updates
```

## OOP Principles Implementation

### 1. Encapsulation
- **Private Methods:** `_create_lesson_model()`, `_validate_lesson_data()`, `_get_lesson_query()`, `_commit_changes()`
- **Protected Methods:** `_validate_user_id()`, `_validate_lesson_id()`, `_validate_title()`
- **Data Hiding:** Database session and model class are encapsulated
- **Public Interface:** Only necessary methods are exposed

### 2. Inheritance
- **BaseLessonService:** Abstract base class with common functionality
- **LessonService:** Extends BaseLessonService with full implementation
- **GoogleClassroomLessonService:** Extends LessonService for Google Classroom
- **MicrosoftTeamsLessonService:** Extends LessonService for Microsoft Teams

### 3. Polymorphism
- **Method Overriding:** `create_lesson()` method overridden in specialized classes
- **Interface Consistency:** All services implement the same interface
- **Runtime Polymorphism:** Factory pattern creates appropriate service
- **Behavioral Polymorphism:** Each service has different behavior

### 4. Abstraction
- **Abstract Base Class:** BaseLessonService provides common interface
- **Complex Logic Hiding:** Database operations are hidden
- **Simplified Interface:** Public methods are easy to use
- **Implementation Details:** Hidden in private methods

## Usage Examples

### Basic Lesson Operations
```python
# Create lesson service
lesson_service = LessonService()

# Create a lesson
lesson = lesson_service.create_lesson(
    user_id="user123",
    title="Python Basics",
    description="Introduction to Python programming",
    difficulty_level="beginner",
    color_theme=1
)

# Get user lessons
lessons = lesson_service.get_lessons_by_user("user123")

# Update lesson
updated_lesson = lesson_service.update_lesson(
    lesson_id="lesson456",
    user_id="user123",
    title="Advanced Python",
    status="in_progress"
)

# Get statistics
stats = lesson_service.get_lesson_statistics("user123")
```

### Platform-Specific Operations
```python
# Google Classroom lesson
google_service = LessonServiceFactory.create_lesson_service('google_classroom')
google_lesson = google_service.create_lesson(
    user_id="user123",
    title="Math Course",
    external_id="course123"
)

# Microsoft Teams lesson
teams_service = LessonServiceFactory.create_lesson_service('microsoft_teams')
teams_lesson = teams_service.create_lesson(
    user_id="user123",
    title="Science Project",
    external_id="team456"
)
```

### Controller Usage
```python
# In route handlers
controller = LessonController()

# Create lesson via API
response = controller.create_lesson()

# Get lesson details
response = controller.get_lesson("lesson123")

# Update lesson
response = controller.update_lesson("lesson123")
```

## Benefits of OOP Implementation

1. **Maintainability:** Code is organized and easy to maintain
2. **Extensibility:** Easy to add new platforms or features
3. **Testability:** Each class can be tested independently
4. **Reusability:** Services can be reused across different contexts
5. **Type Safety:** Validation and error handling are built-in
6. **Platform Support:** Multiple platforms supported through polymorphism
7. **Clean Architecture:** Follows MVC and OOP principles

## File Structure

```
app/
├── services.py                    # Main service classes
├── controllers/
│   └── lesson_views.py           # Lesson controller
├── models/
│   ├── lesson.py                 # Lesson model
│   └── lesson_section.py         # Lesson section model
├── routes/
│   └── class_routes.py           # Class routes and handlers
└── templates/
    ├── class_fragment.html       # Class list fragment
    └── class_detail.html         # Class detail page
```

This OOP implementation provides a robust, scalable, and maintainable foundation for the class/lesson system while following established software engineering principles.
