# 🚀 Smart Learning Hub - Render Deployment

## 📋 Quick Start

### 1. Deploy to Render
1. Fork this repository
2. Connect to [Render.com](https://render.com)
3. Create PostgreSQL database
4. Create Web Service
5. Set environment variables
6. Deploy!

### 2. Environment Variables Required

Copy from `env.render.example` to Render dashboard:

```
FLASK_ENV=production
FLASK_DEBUG=0
FLASK_SECRET_KEY=your-secure-secret-key
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
OAUTHLIB_INSECURE_TRANSPORT=0
```

### 3. Google OAuth Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create OAuth 2.0 credentials
3. Add redirect URI: `https://your-app-name.onrender.com/auth/google/callback`

### 4. Features

- ✅ User authentication
- ✅ Google Classroom integration
- ✅ Lesson management
- ✅ Note taking
- ✅ Task tracking
- ✅ Pomodoro timer
- ✅ Grade system
- ✅ Stream system (Q&A)

### 5. Tech Stack

- **Backend**: Flask, SQLAlchemy
- **Database**: PostgreSQL
- **Frontend**: HTML, CSS, JavaScript
- **Deployment**: Render.com
- **Authentication**: Google OAuth

## 📚 Documentation

See `RENDER_DEPLOYMENT_GUIDE.md` for detailed deployment instructions.

## 🔧 Development

```bash
# Local development
python start_server.py

# Production build
./build.sh
```

## 📞 Support

For issues with deployment, check:
1. Render logs
2. Environment variables
3. Google OAuth configuration
4. Database connection
