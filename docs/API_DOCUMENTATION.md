# **API Documentation: Smart Learning Hub**

**เอกสาร API**  
**ฉบับที่:** 1.0  
**วันที่:** 17 กรกฎาคม 2568  
**จัดทำโดย:** ทีมพัฒนา Smart Learning Hub  
**รหัสเอกสาร:** SLH-API-2025-001

---

## **บทสรุป**

Smart Learning Hub API เป็น RESTful API ที่พัฒนาด้วย Flask สำหรับการจัดการข้อมูลการเรียนรู้ การเชื่อมต่อกับ Google Classroom และการจัดการผู้ใช้

### **Base URL**
```
Development: http://localhost:5000/api
Production: https://your-domain.com/api
```

### **Authentication**
API ใช้ JWT tokens สำหรับการยืนยันตัวตน
```
Authorization: Bearer <your-jwt-token>
```

---

## **1. Authentication Endpoints**

### **1.1 User Registration**
```http
POST /api/auth/register
```

**Request Body:**
```json
{
  "username": "john_doe",
  "email": "john@example.com",
  "password": "secure_password123"
}
```

**Response (200):**
```json
{
  "success": true,
  "message": "User registered successfully",
  "user": {
    "id": 1,
    "username": "john_doe",
    "email": "john@example.com",
    "created_at": "2025-07-17T10:30:00Z"
  }
}
```

### **1.2 User Login**
```http
POST /api/auth/login
```

**Request Body:**
```json
{
  "email": "john@example.com",
  "password": "secure_password123"
}
```

**Response (200):**
```json
{
  "success": true,
  "message": "Login successful",
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": 1,
    "username": "john_doe",
    "email": "john@example.com"
  }
}
```

### **1.3 Google OAuth**
```http
GET /api/auth/google
```

**Response (302):**
Redirects to Google OAuth consent screen

### **1.4 OAuth Callback**
```http
GET /api/auth/callback
```

**Query Parameters:**
- `code`: Authorization code from Google
- `state`: CSRF protection token

**Response (200):**
```json
{
  "success": true,
  "message": "OAuth login successful",
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": 1,
    "username": "john_doe",
    "email": "john@example.com",
    "google_id": "123456789"
  }
}
```

### **1.5 Logout**
```http
POST /api/auth/logout
```

**Headers:**
```
Authorization: Bearer <your-jwt-token>
```

**Response (200):**
```json
{
  "success": true,
  "message": "Logout successful"
}
```

---

## **2. User Management Endpoints**

### **2.1 Get User Profile**
```http
GET /api/users/profile
```

**Headers:**
```
Authorization: Bearer <your-jwt-token>
```

**Response (200):**
```json
{
  "success": true,
  "user": {
    "id": 1,
    "username": "john_doe",
    "email": "john@example.com",
    "created_at": "2025-07-17T10:30:00Z",
    "updated_at": "2025-07-17T10:30:00Z",
    "stats": {
      "total_lessons": 15,
      "total_notes": 45,
      "total_tasks": 23,
      "completed_tasks": 18
    }
  }
}
```

### **2.2 Update User Profile**
```http
PUT /api/users/profile
```

**Headers:**
```
Authorization: Bearer <your-jwt-token>
```

**Request Body:**
```json
{
  "username": "john_doe_updated",
  "email": "john.updated@example.com"
}
```

**Response (200):**
```json
{
  "success": true,
  "message": "Profile updated successfully",
  "user": {
    "id": 1,
    "username": "john_doe_updated",
    "email": "john.updated@example.com",
    "updated_at": "2025-07-17T11:00:00Z"
  }
}
```

---

## **3. Lesson Management Endpoints**

### **3.1 Get All Lessons**
```http
GET /api/lessons
```

**Headers:**
```
Authorization: Bearer <your-jwt-token>
```

**Query Parameters:**
- `page`: Page number (default: 1)
- `per_page`: Items per page (default: 10)
- `category`: Filter by category
- `status`: Filter by status (active, archived)

**Response (200):**
```json
{
  "success": true,
  "lessons": [
    {
      "id": 1,
      "title": "Introduction to Python",
      "description": "Learn the basics of Python programming",
      "category": "Programming",
      "status": "active",
      "google_classroom_id": "123456789",
      "created_at": "2025-07-17T10:30:00Z",
      "updated_at": "2025-07-17T10:30:00Z",
      "note_count": 5,
      "task_count": 3
    }
  ],
  "pagination": {
    "page": 1,
    "per_page": 10,
    "total": 15,
    "pages": 2
  }
}
```

### **3.2 Create New Lesson**
```http
POST /api/lessons
```

**Headers:**
```
Authorization: Bearer <your-jwt-token>
```

**Request Body:**
```json
{
  "title": "Advanced JavaScript",
  "description": "Learn advanced JavaScript concepts",
  "category": "Programming",
  "status": "active",
  "google_classroom_id": "987654321"
}
```

**Response (201):**
```json
{
  "success": true,
  "message": "Lesson created successfully",
  "lesson": {
    "id": 2,
    "title": "Advanced JavaScript",
    "description": "Learn advanced JavaScript concepts",
    "category": "Programming",
    "status": "active",
    "google_classroom_id": "987654321",
    "created_at": "2025-07-17T11:00:00Z",
    "updated_at": "2025-07-17T11:00:00Z"
  }
}
```

### **3.3 Get Lesson by ID**
```http
GET /api/lessons/{lesson_id}
```

**Headers:**
```
Authorization: Bearer <your-jwt-token>
```

**Response (200):**
```json
{
  "success": true,
  "lesson": {
    "id": 1,
    "title": "Introduction to Python",
    "description": "Learn the basics of Python programming",
    "category": "Programming",
    "status": "active",
    "google_classroom_id": "123456789",
    "created_at": "2025-07-17T10:30:00Z",
    "updated_at": "2025-07-17T10:30:00Z",
    "notes": [
      {
        "id": 1,
        "title": "Variables and Data Types",
        "content": "Python has several data types...",
        "created_at": "2025-07-17T10:35:00Z"
      }
    ],
    "tasks": [
      {
        "id": 1,
        "title": "Complete Python Basics Quiz",
        "status": "pending",
        "due_date": "2025-07-20T23:59:59Z"
      }
    ]
  }
}
```

### **3.4 Update Lesson**
```http
PUT /api/lessons/{lesson_id}
```

**Headers:**
```
Authorization: Bearer <your-jwt-token>
```

**Request Body:**
```json
{
  "title": "Introduction to Python Programming",
  "description": "Updated description for Python basics",
  "category": "Programming",
  "status": "active"
}
```

**Response (200):**
```json
{
  "success": true,
  "message": "Lesson updated successfully",
  "lesson": {
    "id": 1,
    "title": "Introduction to Python Programming",
    "description": "Updated description for Python basics",
    "category": "Programming",
    "status": "active",
    "updated_at": "2025-07-17T11:30:00Z"
  }
}
```

### **3.5 Delete Lesson**
```http
DELETE /api/lessons/{lesson_id}
```

**Headers:**
```
Authorization: Bearer <your-jwt-token>
```

**Response (200):**
```json
{
  "success": true,
  "message": "Lesson deleted successfully"
}
```

---

## **4. Note Management Endpoints**

### **4.1 Get All Notes**
```http
GET /api/notes
```

**Headers:**
```
Authorization: Bearer <your-jwt-token>
```

**Query Parameters:**
- `page`: Page number (default: 1)
- `per_page`: Items per page (default: 10)
- `lesson_id`: Filter by lesson ID
- `search`: Search in title and content
- `tags`: Filter by tags

**Response (200):**
```json
{
  "success": true,
  "notes": [
    {
      "id": 1,
      "title": "Variables and Data Types",
      "content": "Python has several data types including...",
      "tags": "python, variables, data-types",
      "lesson_id": 1,
      "lesson_title": "Introduction to Python",
      "created_at": "2025-07-17T10:35:00Z",
      "updated_at": "2025-07-17T10:35:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "per_page": 10,
    "total": 45,
    "pages": 5
  }
}
```

### **4.2 Create New Note**
```http
POST /api/notes
```

**Headers:**
```
Authorization: Bearer <your-jwt-token>
```

**Request Body:**
```json
{
  "title": "Control Structures in Python",
  "content": "# Control Structures\n\n## If Statements\n\n```python\nif condition:\n    statement\n```",
  "tags": "python, control-structures, if-statements",
  "lesson_id": 1
}
```

**Response (201):**
```json
{
  "success": true,
  "message": "Note created successfully",
  "note": {
    "id": 2,
    "title": "Control Structures in Python",
    "content": "# Control Structures\n\n## If Statements\n\n```python\nif condition:\n    statement\n```",
    "tags": "python, control-structures, if-statements",
    "lesson_id": 1,
    "created_at": "2025-07-17T11:00:00Z",
    "updated_at": "2025-07-17T11:00:00Z"
  }
}
```

### **4.3 Get Note by ID**
```http
GET /api/notes/{note_id}
```

**Headers:**
```
Authorization: Bearer <your-jwt-token>
```

**Response (200):**
```json
{
  "success": true,
  "note": {
    "id": 1,
    "title": "Variables and Data Types",
    "content": "Python has several data types including integers, floats, strings, and booleans...",
    "tags": "python, variables, data-types",
    "lesson_id": 1,
    "lesson_title": "Introduction to Python",
    "created_at": "2025-07-17T10:35:00Z",
    "updated_at": "2025-07-17T10:35:00Z"
  }
}
```

### **4.4 Update Note**
```http
PUT /api/notes/{note_id}
```

**Headers:**
```
Authorization: Bearer <your-jwt-token>
```

**Request Body:**
```json
{
  "title": "Updated Variables and Data Types",
  "content": "Updated content about Python data types...",
  "tags": "python, variables, data-types, updated"
}
```

**Response (200):**
```json
{
  "success": true,
  "message": "Note updated successfully",
  "note": {
    "id": 1,
    "title": "Updated Variables and Data Types",
    "content": "Updated content about Python data types...",
    "tags": "python, variables, data-types, updated",
    "updated_at": "2025-07-17T11:30:00Z"
  }
}
```

### **4.5 Delete Note**
```http
DELETE /api/notes/{note_id}
```

**Headers:**
```
Authorization: Bearer <your-jwt-token>
```

**Response (200):**
```json
{
  "success": true,
  "message": "Note deleted successfully"
}
```

### **4.6 Search Notes**
```http
GET /api/notes/search
```

**Headers:**
```
Authorization: Bearer <your-jwt-token>
```

**Query Parameters:**
- `q`: Search query
- `page`: Page number (default: 1)
- `per_page`: Items per page (default: 10)

**Response (200):**
```json
{
  "success": true,
  "notes": [
    {
      "id": 1,
      "title": "Variables and Data Types",
      "content": "Python has several data types...",
      "tags": "python, variables, data-types",
      "lesson_title": "Introduction to Python",
      "created_at": "2025-07-17T10:35:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "per_page": 10,
    "total": 5,
    "pages": 1
  }
}
```

---

## **5. Task Management Endpoints**

### **5.1 Get All Tasks**
```http
GET /api/tasks
```

**Headers:**
```
Authorization: Bearer <your-jwt-token>
```

**Query Parameters:**
- `page`: Page number (default: 1)
- `per_page`: Items per page (default: 10)
- `lesson_id`: Filter by lesson ID
- `status`: Filter by status (pending, in_progress, completed)
- `priority`: Filter by priority (low, medium, high)

**Response (200):**
```json
{
  "success": true,
  "tasks": [
    {
      "id": 1,
      "title": "Complete Python Basics Quiz",
      "description": "Take the quiz on Python fundamentals",
      "status": "pending",
      "priority": "high",
      "due_date": "2025-07-20T23:59:59Z",
      "lesson_id": 1,
      "lesson_title": "Introduction to Python",
      "created_at": "2025-07-17T10:30:00Z",
      "updated_at": "2025-07-17T10:30:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "per_page": 10,
    "total": 23,
    "pages": 3
  }
}
```

### **5.2 Create New Task**
```http
POST /api/tasks
```

**Headers:**
```
Authorization: Bearer <your-jwt-token>
```

**Request Body:**
```json
{
  "title": "Practice JavaScript Functions",
  "description": "Complete exercises on JavaScript functions",
  "status": "pending",
  "priority": "medium",
  "due_date": "2025-07-25T23:59:59Z",
  "lesson_id": 2
}
```

**Response (201):**
```json
{
  "success": true,
  "message": "Task created successfully",
  "task": {
    "id": 2,
    "title": "Practice JavaScript Functions",
    "description": "Complete exercises on JavaScript functions",
    "status": "pending",
    "priority": "medium",
    "due_date": "2025-07-25T23:59:59Z",
    "lesson_id": 2,
    "created_at": "2025-07-17T11:00:00Z",
    "updated_at": "2025-07-17T11:00:00Z"
  }
}
```

### **5.3 Update Task Status**
```http
PUT /api/tasks/{task_id}/status
```

**Headers:**
```
Authorization: Bearer <your-jwt-token>
```

**Request Body:**
```json
{
  "status": "completed"
}
```

**Response (200):**
```json
{
  "success": true,
  "message": "Task status updated successfully",
  "task": {
    "id": 1,
    "status": "completed",
    "updated_at": "2025-07-17T11:30:00Z"
  }
}
```

---

## **6. Google Classroom Integration Endpoints**

### **6.1 Get Google Classrooms**
```http
GET /api/google/classrooms
```

**Headers:**
```
Authorization: Bearer <your-jwt-token>
```

**Response (200):**
```json
{
  "success": true,
  "classrooms": [
    {
      "id": "123456789",
      "name": "Introduction to Computer Science",
      "section": "CS101",
      "description": "Basic computer science concepts",
      "ownerId": "teacher@school.edu",
      "creationTime": "2025-01-15T08:00:00Z",
      "updateTime": "2025-07-17T10:00:00Z",
      "enrollmentCode": "abc123",
      "courseState": "ACTIVE"
    }
  ]
}
```

### **6.2 Sync Google Classroom**
```http
POST /api/google/classrooms/sync
```

**Headers:**
```
Authorization: Bearer <your-jwt-token>
```

**Request Body:**
```json
{
  "classroom_id": "123456789"
}
```

**Response (200):**
```json
{
  "success": true,
  "message": "Classroom synced successfully",
  "synced_data": {
    "course": {
      "id": "123456789",
      "name": "Introduction to Computer Science"
    },
    "assignments": 5,
    "materials": 12,
    "announcements": 3
  }
}
```

### **6.3 Get Classroom Assignments**
```http
GET /api/google/classrooms/{classroom_id}/assignments
```

**Headers:**
```
Authorization: Bearer <your-jwt-token>
```

**Response (200):**
```json
{
  "success": true,
  "assignments": [
    {
      "id": "assignment_123",
      "title": "Python Programming Assignment 1",
      "description": "Complete the basic Python exercises",
      "dueDate": "2025-07-25T23:59:59Z",
      "dueTime": "23:59:59",
      "maxPoints": 100,
      "state": "PUBLISHED",
      "creationTime": "2025-07-15T10:00:00Z",
      "updateTime": "2025-07-15T10:00:00Z"
    }
  ]
}
```

---

## **7. Chrome Extension API Endpoints**

### **7.1 Import Data from Extension**
```http
POST /api/import-data
```

**Request Body:**
```json
{
  "title": "MS Teams Meeting Notes",
  "content": "Discussion about project requirements...",
  "url": "https://teams.microsoft.com/meeting/123",
  "source": "ms_teams",
  "timestamp": "2025-07-17T10:30:00Z"
}
```

**Response (200):**
```json
{
  "success": true,
  "message": "Data imported successfully",
  "imported_data": {
    "id": 1,
    "title": "MS Teams Meeting Notes",
    "content": "Discussion about project requirements...",
    "source": "ms_teams",
    "created_at": "2025-07-17T10:30:00Z"
  }
}
```

---

## **8. Error Responses**

### **8.1 Authentication Error (401)**
```json
{
  "success": false,
  "error": "Unauthorized",
  "message": "Invalid or missing authentication token"
}
```

### **8.2 Validation Error (400)**
```json
{
  "success": false,
  "error": "Validation Error",
  "message": "Invalid input data",
  "details": {
    "username": ["Username is required"],
    "email": ["Invalid email format"]
  }
}
```

### **8.3 Not Found Error (404)**
```json
{
  "success": false,
  "error": "Not Found",
  "message": "Resource not found"
}
```

### **8.4 Server Error (500)**
```json
{
  "success": false,
  "error": "Internal Server Error",
  "message": "An unexpected error occurred"
}
```

---

## **9. Rate Limiting**

API มีการจำกัดอัตราการเรียกใช้:
- **Authentication endpoints:** 5 requests per minute
- **General endpoints:** 100 requests per hour
- **Search endpoints:** 50 requests per hour

เมื่อเกินขีดจำกัด จะได้รับ response:
```json
{
  "success": false,
  "error": "Rate Limit Exceeded",
  "message": "Too many requests. Please try again later.",
  "retry_after": 60
}
```

---

## **10. Testing the API**

### **10.1 Using curl**

#### **Register User:**
```bash
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "password123"
  }'
```

#### **Login:**
```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "password123"
  }'
```

#### **Get Lessons (with token):**
```bash
curl -X GET http://localhost:5000/api/lessons \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### **10.2 Using Postman**

1. **Import Collection:** ใช้ไฟล์ Smart_Learning_Hub_API.postman_collection.json
2. **Set Environment Variables:** 
   - `base_url`: http://localhost:5000/api
   - `token`: JWT token จาก login response
3. **Run Tests:** ทดสอบ endpoints ต่างๆ

---

**หมายเหตุ:** API นี้จะได้รับการอัปเดตตามการพัฒนาของโปรเจกต์และความต้องการใหม่ที่เกิดขึ้น 