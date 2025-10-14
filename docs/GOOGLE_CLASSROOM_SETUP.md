# Google Classroom Integration Setup Guide

## 🎯 Overview
This guide will help you set up Google Classroom integration for importing courses, students, assignments, and materials.

## 📋 Prerequisites
- Google account with access to Google Classroom
- Google Cloud Console access
- Flask application running

## 🔧 Step-by-Step Setup

### 1. Google Cloud Console Setup

#### 1.1 Create a New Project
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click "Select a project" → "New Project"
3. Enter project name: `Smart Learning Hub`
4. Click "Create"

#### 1.2 Enable Required APIs
1. Go to "APIs & Services" → "Library"
2. Enable the following APIs:
   - **Google Classroom API**
   - **Google Drive API**
   - **Google People API**
   - **Google OAuth2 API**

#### 1.3 Configure OAuth Consent Screen
1. Go to "APIs & Services" → "OAuth consent screen"
2. Choose "External" user type
3. Fill in required information:
   - App name: `Smart Learning Hub`
   - User support email: `your-email@domain.com`
   - Developer contact: `your-email@domain.com`
4. Add scopes:
   - `https://www.googleapis.com/auth/classroom.courses.readonly`
   - `https://www.googleapis.com/auth/classroom.rosters.readonly`
   - `https://www.googleapis.com/auth/classroom.course-work.readonly`
   - `https://www.googleapis.com/auth/userinfo.profile`
   - `https://www.googleapis.com/auth/userinfo.email`

#### 1.4 Create OAuth 2.0 Credentials
1. Go to "APIs & Services" → "Credentials"
2. Click "Create Credentials" → "OAuth 2.0 Client IDs"
3. Choose "Web application"
4. Add authorized redirect URIs:
   - `http://localhost:5004/google_classroom/oauth2callback`
   - `http://127.0.0.1:5004/google_classroom/oauth2callback`
   - `https://yourdomain.com/google_classroom/oauth2callback` (for production)
5. Click "Create"
6. Copy the Client ID and Client Secret

### 2. Environment Configuration

#### 2.1 Set Environment Variables
```bash
# Development
export GOOGLE_CLIENT_ID="your-client-id.apps.googleusercontent.com"
export GOOGLE_CLIENT_SECRET="your-client-secret"
export FLASK_SECRET_KEY="your-secret-key"

# Production
export GOOGLE_CLIENT_ID="your-production-client-id"
export GOOGLE_CLIENT_SECRET="your-production-client-secret"
export FLASK_SECRET_KEY="your-production-secret-key"
```

#### 2.2 Create .env File
```bash
# .env
GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-client-secret
FLASK_SECRET_KEY=your-secret-key
FLASK_ENV=development
```

### 3. Database Migration

#### 3.1 Run Migration Script
```bash
python scripts/migrations/add_google_credentials.py
```

#### 3.2 Verify Migration
```bash
# Check if column was added
sqlite3 instance/site.db "PRAGMA table_info(user);"
```

### 4. Testing the Integration

#### 4.1 Start the Application
```bash
python start_server.py
```

#### 4.2 Test Google Classroom Connection
1. Go to `http://localhost:5004`
2. Click "Create New Class"
3. Click "Import from Google Classroom"
4. Complete OAuth flow
5. Select a course to import

## 🔍 Troubleshooting

### Common Issues

#### Issue 1: "No Google credentials found"
**Solution:**
- Make sure OAuth flow completed successfully
- Check if credentials are stored in database
- Verify environment variables are set

#### Issue 2: "Invalid redirect URI"
**Solution:**
- Add your domain to authorized redirect URIs in Google Cloud Console
- Check if the redirect URI matches exactly

#### Issue 3: "API not enabled"
**Solution:**
- Enable Google Classroom API in Google Cloud Console
- Wait a few minutes for changes to propagate

#### Issue 4: "Insufficient permissions"
**Solution:**
- Check OAuth consent screen configuration
- Verify required scopes are added
- Test with a different Google account

### Debug Mode

#### Enable Debug Logging
```python
# In your Flask app
import logging
logging.basicConfig(level=logging.DEBUG)
```

#### Check Database
```bash
# Check if credentials are stored
sqlite3 instance/site.db "SELECT id, username, google_credentials FROM user WHERE google_credentials IS NOT NULL;"
```

## 🚀 Production Deployment

### 1. Update Redirect URIs
Add your production domain to Google Cloud Console:
- `https://yourdomain.com/google_classroom/oauth2callback`

### 2. Environment Variables
Set production environment variables:
```bash
export GOOGLE_CLIENT_ID="production-client-id"
export GOOGLE_CLIENT_SECRET="production-client-secret"
export FLASK_SECRET_KEY="production-secret-key"
```

### 3. SSL Certificate
Ensure your production site has SSL certificate for OAuth to work properly.

## 📚 API Reference

### Available Endpoints
- `GET /google_classroom/authorize` - Start OAuth flow
- `GET /google_classroom/oauth2callback` - OAuth callback
- `GET /google_classroom/fetch_courses` - Get available courses
- `POST /google_classroom/import_course` - Import selected course

### Request/Response Examples

#### Fetch Courses
```javascript
fetch('/google_classroom/fetch_courses')
  .then(response => response.json())
  .then(data => {
    console.log(data.courses);
  });
```

#### Import Course
```javascript
fetch('/google_classroom/import_course', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    courseId: 'course_123',
    settings: {
      importStudents: true,
      importAssignments: true,
      importMaterials: true,
      importAnnouncements: true
    }
  })
});
```

## 🔒 Security Considerations

### 1. Credential Storage
- Google credentials are encrypted and stored in database
- Use environment variables for sensitive configuration
- Implement proper access controls

### 2. OAuth Security
- Use HTTPS in production
- Validate state parameter in OAuth flow
- Implement proper session management

### 3. Data Privacy
- Only import data that users explicitly authorize
- Provide clear data usage policies
- Implement data deletion capabilities

## 📞 Support

If you encounter issues:
1. Check the troubleshooting section above
2. Review Google Cloud Console configuration
3. Check application logs for error messages
4. Verify database migration completed successfully

## 🎉 Success!

Once setup is complete, you can:
- Import Google Classroom courses
- Sync students and assignments
- Maintain data consistency
- Provide seamless user experience
