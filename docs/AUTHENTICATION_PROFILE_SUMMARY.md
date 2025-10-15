# สรุปฟังก์ชัน Google Authentication, Profile และหน้า Login

## 📋 ภาพรวมระบบ

Smart Learning Hub มีระบบยืนยันตัวตนและการจัดการโปรไฟล์ที่ครอบคลุม ประกอบด้วย:
- **หน้า Login** สำหรับการเข้าสู่ระบบ
- **Google OAuth Authentication** สำหรับเข้าสู่ระบบผ่าน Google
- **Profile Management** สำหรับจัดการข้อมูลส่วนตัว
- **Password Management** สำหรับการเปลี่ยนรหัสผ่านและรีเซ็ตรหัสผ่าน

---

## 🔐 1. ระบบ Authentication

### 1.1 Web Authentication Routes (`app/routes_web_auth.py`)

**Blueprint:** `web_auth_bp` (ไม่มี url_prefix เพื่อให้ routes อยู่ที่ root level)

#### Routes:
- `GET/POST /login` - หน้าเข้าสู่ระบบ
- `GET/POST /register` - หน้าสมัครสมาชิก
- `GET /logout` - ออกจากระบบ
- `GET/POST /forgot-password` - หน้าลืมรหัสผ่าน
- `GET/POST /reset-password/<token>` - หน้ารีเซ็ตรหัสผ่าน
- `GET /test-reset-links` - หน้าทดสอบลิงก์รีเซ็ต (สำหรับ development)

#### Controller Integration:
```python
auth_controller = AuthController()

@web_auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    else:
        result = auth_controller.login()
        # Handle response based on success/failure
```

### 1.2 API Authentication Routes (`app/routes/auth_routes.py`)

**Blueprint:** `auth_bp` (url_prefix: `/api/auth`)

#### Routes:
- `POST /api/auth/login` - API endpoint สำหรับ login
- `POST /api/auth/register` - API endpoint สำหรับ register
- `GET /api/auth/logout` - API endpoint สำหรับ logout

---

## 🔑 2. Google OAuth Authentication

### 2.1 Google Auth Routes (`app/routes/integrations/routes_google_auth.py`)

**Blueprint:** `google_auth_bp` (url_prefix: `/auth/google`)

#### Configuration:
```python
SCOPES = [
    "openid",
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile"
]
```

#### Routes:
- `GET /auth/google/login` - เริ่มต้น Google OAuth flow
- `GET /auth/google/callback` - Callback URL สำหรับ Google OAuth

#### OAuth Flow Process:
1. **Authorization Request** (`/login`):
   ```python
   authorization_url, state = flow.authorization_url(
       access_type="offline",
       include_granted_scopes="true",
       prompt="select_account"
   )
   session['oauth_state'] = state
   ```

2. **Callback Handling** (`/callback`):
   ```python
   # Validate state parameter
   if not state or state != request.args.get('state'):
       flash("Invalid state or session expired", "warning")
   
   # Exchange code for token
   flow.fetch_token(authorization_response=request.url)
   
   # Get user info and create/update user
   user = UserModel.query.filter_by(email=email).first()
   if not user:
       user = UserModel(
           id=str(uuid.uuid4()),
           username=name or email.split("@")[0],
           email=email,
           password_hash="oauth_google",
           profile_image=picture,
           email_verified=True
       )
   ```

### 2.2 Google Classroom Integration

**Blueprint:** `google_classroom_bp` (url_prefix: `/google_classroom`)

#### Extended Scopes:
```python
SCOPES = [
    'https://www.googleapis.com/auth/classroom.courses.readonly',
    'https://www.googleapis.com/auth/classroom.announcements.readonly',
    'https://www.googleapis.com/auth/classroom.coursework.me',
    'https://www.googleapis.com/auth/userinfo.profile',
    'https://www.googleapis.com/auth/userinfo.email',
    'https://www.googleapis.com/auth/drive.readonly'
]
```

#### Key Routes:
- `GET /google_classroom/authorize` - เริ่ม Google Classroom OAuth
- `GET /google_classroom/oauth2callback` - Callback สำหรับ Google Classroom
- `GET /google_classroom/fetch_courses` - ดึงรายการ courses
- `POST /google_classroom/import_course` - Import course จาก Google Classroom

---

## 👤 3. Profile Management

### 3.1 Profile Routes (`app/routes/profile_routes.py`)

**Blueprint:** `profile_bp` (url_prefix: `/profile`)

#### Web Routes:
- `GET /profile/` - หน้าโปรไฟล์หลัก
- `GET /profile/edit` - หน้าแก้ไขโปรไฟล์
- `POST /profile/update` - อัปเดตโปรไฟล์ผ่าน web form
- `PUT /profile/api/update` - API endpoint สำหรับอัปเดตโปรไฟล์

#### File Upload Support:
```python
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
UPLOAD_FOLDER = 'uploads'

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
```

### 3.2 User API Routes (`app/routes/user_routes.py`)

**Blueprint:** `user_bp` (url_prefix: `/api/users`)

#### REST API Endpoints:
- `POST /api/users` - สร้างผู้ใช้ใหม่
- `GET /api/users/<user_id>` - ดึงข้อมูลผู้ใช้ตาม ID
- `GET /api/users/profile` - ดึงโปรไฟล์ผู้ใช้ปัจจุบัน
- `PUT /api/users/profile` - อัปเดตโปรไฟล์ผู้ใช้ปัจจุบัน
- `PUT /api/users/<user_id>/profile` - อัปเดตโปรไฟล์ผู้ใช้ตาม ID
- `PUT /api/users/<user_id>/password` - เปลี่ยนรหัสผ่าน

---

## 🎨 4. หน้า Login UI/UX

### 4.1 Template Structure (`app/templates/login.html`)

#### Layout Components:
```html
<div class="auth-page">
    <div class="auth-container">
        <!-- Sidebar with branding -->
        <aside class="auth-sidebar">
            <div class="auth-sidebar__brand">
                <h3>Smart Learning Hub</h3>
                <p>Learn better, faster — organized lessons, notes and practice</p>
            </div>
            
            <!-- Feature highlights -->
            <ul class="auth-features">
                <li>Personalized lessons</li>
                <li>Notes & progress tracking</li>
                <li>Google Classroom & Teams integration</li>
            </ul>
        </aside>
        
        <!-- Main login form -->
        <main class="auth-main">
            <div class="login-card">
                <!-- Login form content -->
            </div>
        </main>
    </div>
</div>
```

#### Form Features:
- **Flash Messages** - แสดงข้อความ error/success
- **Form Validation** - Client-side และ server-side validation
- **Password Toggle** - แสดง/ซ่อนรหัสผ่าน
- **Google OAuth Button** - เข้าสู่ระบบผ่าน Google
- **Forgot Password Link** - ลิงก์ไปยังหน้าลืมรหัสผ่าน

#### CSS Styling:
- **Blue Theme** - สีฟ้าเป็นหลัก (#2196F3, #1976D2)
- **Bootstrap Integration** - ใช้ Bootstrap 5.1.3
- **Bootstrap Icons** - ใช้แทนที่ emojis
- **Responsive Design** - รองรับทุกขนาดหน้าจอ
- **Custom Animations** - Hover effects และ transitions

### 4.2 Authentication Flow

#### 1. Login Process:
```
User Input → Form Validation → AuthController.login() 
→ UserService.authenticate_user() → Session Creation → Redirect to Dashboard
```

#### 2. Google OAuth Process:
```
Google Login Button → /auth/google/login → Google OAuth Consent 
→ /auth/google/callback → User Creation/Update → Session Creation → Redirect
```

#### 3. Registration Process:
```
Registration Form → Password Validation → AuthController.register() 
→ UserService.create_user() → Auto-login → Redirect to Dashboard
```

---

## 🔧 5. Controller Layer

### 5.1 AuthController (`app/controllers/auth_views.py`)

#### Key Methods:
```python
class AuthController:
    def login(self) -> Any:
        # Handle GET/POST for login
        # Validate credentials
        # Create session
        # Return JSON or redirect
    
    def register(self) -> Any:
        # Handle registration
        # Validate password strength
        # Create new user
        # Auto-login after registration
    
    def logout(self) -> Any:
        # Clear session
        # Redirect to login
```

### 5.2 UserController (`app/controllers/user_views.py`)

#### Key Methods:
```python
class UserController:
    def get_current_user_profile(self) -> Dict[str, Any]:
        # Get current user from session
        # Return profile data
    
    def update_user_profile(self, user_id: str) -> Dict[str, Any]:
        # Validate input data
        # Update user profile
        # Return success/error response
    
    def change_password(self, user_id: str) -> Dict[str, Any]:
        # Validate current password
        # Check new password strength
        # Update password hash
```

---

## 🛡️ 6. Security Features

### 6.1 Password Requirements
- **ความยาวขั้นต่ำ:** 8 ตัวอักษร
- **ตัวอักษรพิมพ์ใหญ่:** A-Z อย่างน้อย 1 ตัว
- **ตัวอักษรพิมพ์เล็ก:** a-z อย่างน้อย 1 ตัว
- **ตัวเลข:** 0-9 อย่างน้อย 1 ตัว
- **อักขระพิเศษ:** !@#$%^&* อย่างน้อย 1 ตัว

### 6.2 Session Management
```python
session['user_id'] = user.id
session.permanent = True
```

### 6.3 OAuth Security
- **State Parameter Validation** - ป้องกัน CSRF attacks
- **HTTPS Only** - สำหรับ production
- **Secure Token Storage** - เก็บ tokens ในฐานข้อมูล

---

## 📱 7. Profile Fragment UI

### 7.1 Profile Template (`app/templates/profile_fragment.html`)

#### Features:
- **Blue Theme Design** - สีฟ้าสวยงามสม่ำเสมอ
- **Bootstrap Icons** - ใช้ Bootstrap Icons แทน emojis
- **Responsive Cards** - แสดงข้อมูลในรูปแบบ cards
- **Edit Profile Modal** - Modal สำหรับแก้ไขโปรไฟล์
- **Change Password Section** - ส่วนเปลี่ยนรหัสผ่าน

#### Card Components:
1. **Profile Information Card** - ข้อมูลพื้นฐาน
2. **Account Settings Card** - การตั้งค่าบัญชี
3. **Security Settings Card** - การตั้งค่าความปลอดภัย
4. **Google Integration Card** - การเชื่อมต่อ Google services

---

## 🔄 8. Password Management

### 8.1 Change Password Feature
- **Current Password Verification** - ตรวจสอบรหัสผ่านปัจจุบัน
- **Password Strength Meter** - แสดงความแข็งแรงของรหัสผ่าน
- **Real-time Validation** - ตรวจสอบทันทีขณะพิมพ์
- **API Integration** - เชื่อมต่อกับ backend API

### 8.2 Forgot Password System
- **Email Submission** - ส่งอีเมลเพื่อรีเซ็ต
- **Token-based Reset** - ใช้ token สำหรับความปลอดภัย
- **Password Reset Form** - ฟอร์มตั้งรหัสผ่านใหม่
- **Comprehensive Validation** - ตรวจสอบครบถ้วน

---

## 📊 9. ข้อมูลเทคนิค

### 9.1 Dependencies
```
flask
google-auth-oauthlib
google-auth
google-api-python-client
bootstrap@5.1.3
bootstrap-icons@1.7.2
font-awesome@6.0.0
```

### 9.2 File Structure
```
app/
├── routes/
│   ├── auth_routes.py           # API auth endpoints
│   ├── user_routes.py           # API user endpoints
│   ├── profile_routes.py        # Web profile routes
│   └── integrations/
│       ├── routes_google_auth.py       # Google OAuth
│       └── routes_google_classroom.py  # Google Classroom
├── routes_web_auth.py           # Web auth pages
├── controllers/
│   ├── auth_views.py           # Auth controller
│   └── user_views.py           # User controller
├── templates/
│   ├── login.html              # Login page
│   ├── register.html           # Registration page
│   ├── profile_fragment.html   # Profile page
│   ├── forgot_password.html    # Forgot password page
│   └── reset_password.html     # Reset password page
└── static/
    └── css/
        └── custom.css          # Custom styling
```

### 9.3 Environment Variables
```
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
SECRET_KEY=your_flask_secret_key
```

---

## ✅ 10. Status และ Features

### ✅ Completed Features:
- ✅ Login/Register/Logout functionality
- ✅ Google OAuth integration
- ✅ Profile management with file upload
- ✅ Password change with strength validation
- ✅ Forgot password system
- ✅ Blue theme UI design
- ✅ Bootstrap Icons integration
- ✅ Responsive design
- ✅ Flash messaging system
- ✅ Session management
- ✅ Google Classroom integration

### 🚀 Ready for Use:
- Server: `http://localhost:8002`
- Login Page: `/login`
- Google Auth: `/auth/google/login`
- Profile: `/profile`
- API Endpoints: `/api/auth/*` และ `/api/users/*`

---

## 📝 Notes

1. **Architecture Pattern:** MVC (Model-View-Controller)
2. **Authentication:** Session-based + OAuth
3. **Database:** SQLAlchemy with SQLite
4. **UI Framework:** Bootstrap 5 + Custom CSS
5. **Language Support:** Thai และ English
6. **Security:** Password hashing, CSRF protection, OAuth validation

ระบบ Authentication และ Profile Management พร้อมใช้งานแล้วครับ! 🎉