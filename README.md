# 🎓 Smart Learning Hub

A comprehensive learning management system built with Flask, featuring lesson management, note-taking, task tracking, Pomodoro timer, and Google Classroom integration.

## ✨ Features

### 📚 Core Features
- **Lesson Management** - Create, organize, and track learning lessons
- **Note Taking** - Digital note-taking with rich text support
- **Task Management** - Track assignments and tasks with deadlines
- **Pomodoro Timer** - Built-in productivity timer with statistics
- **Stream System** - Q&A and discussion platform
- **Grade System** - Comprehensive grading and assessment tools

### 🔐 Authentication & Security
- **Google OAuth** - Secure login with Google accounts
- **User Management** - Role-based access control
- **Session Security** - Secure session management

### 🔗 Integrations
- **Google Classroom** - Import lessons and assignments
- **Google Drive** - File storage and sharing
- **Microsoft Teams** - Future integration support

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- SQLite (for development)
- PostgreSQL (for production)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-username/smart-learning-hub.git
   cd smart-learning-hub
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   export FLASK_SECRET_KEY='your-secret-key'
   export GOOGLE_CLIENT_ID='your-google-client-id'
   export GOOGLE_CLIENT_SECRET='your-google-client-secret'
   ```

5. **Initialize database**
   ```bash
   python database/setup_database.py
   ```

6. **Run the application**
   ```bash
   python start.py
   ```

7. **Access the application**
   - Open your browser to `http://localhost:8000`
   - Register or login with Google OAuth

## 🏗️ Project Structure

```
smart-learning-hub/
├── app/                    # Main application package
│   ├── config/            # Configuration files
│   ├── controllers/       # Business logic controllers
│   ├── middleware/        # Custom middleware
│   ├── models/           # Database models
│   ├── routes/           # API and web routes
│   ├── services/         # External service integrations
│   ├── static/           # Static assets (CSS, JS, images)
│   ├── templates/        # HTML templates
│   └── utils/            # Utility functions
├── database/             # Database setup and migrations
├── chrome_extension/     # Browser extension
├── docs/                # Documentation
├── scripts/             # Utility scripts
├── instance/            # SQLite database (development)
├── uploads/             # File uploads
├── requirements.txt     # Python dependencies
├── Procfile            # Deployment configuration
├── render.yaml         # Render.com deployment config
├── build.sh            # Build script
└── start.py            # Application entry point
```

## 🌐 Deployment

### Render.com (Recommended)

1. **Connect your GitHub repository** to Render
2. **Create a new Web Service**
3. **Configure environment variables:**
   ```
   FLASK_ENV=production
   FLASK_DEBUG=0
   FLASK_SECRET_KEY=your-secure-secret-key
   GOOGLE_CLIENT_ID=your-google-client-id
   GOOGLE_CLIENT_SECRET=your-google-client-secret
   OAUTHLIB_INSECURE_TRANSPORT=0
   ```
4. **Deploy** - Render will automatically build and deploy

### Manual Deployment

1. **Set up PostgreSQL database**
2. **Install dependencies:** `pip install -r requirements.txt`
3. **Run build script:** `./build.sh`
4. **Start application:** `python start.py`

## 🔧 Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `FLASK_SECRET_KEY` | Secret key for session security | Yes |
| `FLASK_ENV` | Environment (development/production) | No |
| `DATABASE_URL` | Database connection string | No (defaults to SQLite) |
| `GOOGLE_CLIENT_ID` | Google OAuth client ID | Yes |
| `GOOGLE_CLIENT_SECRET` | Google OAuth client secret | Yes |

### Google OAuth Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create a new project or select existing
3. Enable Google+ API and Google Classroom API
4. Create OAuth 2.0 credentials
5. Add authorized redirect URIs:
   - `http://localhost:8000/auth/google/callback` (development)
   - `https://your-domain.com/auth/google/callback` (production)

## 📱 Browser Extension

The project includes a Chrome extension for enhanced functionality:
- Quick access to lessons and notes
- Pomodoro timer integration
- Direct Google Classroom sync

## 🛠️ Development

### Running Tests
```bash
python -m pytest tests/
```

### Database Migrations
```bash
flask db migrate -m "Description of changes"
flask db upgrade
```

### Code Style
```bash
flake8 app/
black app/
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📞 Support

For support and questions:
- Create an issue on GitHub
- Check the documentation in `/docs`
- Review the troubleshooting guide

## 🎯 Roadmap

- [ ] Mobile app (React Native)
- [ ] Advanced analytics dashboard
- [ ] AI-powered study recommendations
- [ ] Multi-language support
- [ ] Offline mode support

---

**Built with ❤️ using Flask, SQLAlchemy, and modern web technologies.**
