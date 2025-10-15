# Smart Learning Hub - Project Information

## 📋 Project Overview

**Smart Learning Hub** is a comprehensive Flask-based learning management system that integrates with Google Classroom and Microsoft Teams to provide a unified learning experience.

## 🏗️ Architecture

- **Framework**: Flask 3.1.1 with MVC architecture
- **Database**: SQLite (development) / PostgreSQL (production)
- **Frontend**: Bootstrap 5.3.3, Vanilla JavaScript
- **Authentication**: Google OAuth 2.0
- **Design Pattern**: Object-Oriented Programming (4 Pillars)

## 📁 Project Structure

```
├── app/                    # Main Flask application
│   ├── config/            # Configuration files
│   ├── controllers/       # MVC Controllers
│   ├── models/           # SQLAlchemy models
│   ├── routes/           # Flask routes
│   ├── services/         # Business logic (OOP)
│   ├── static/           # CSS, JS, images
│   ├── templates/        # Jinja2 templates
│   └── utils/            # Utilities and exceptions
├── database/             # Database scripts and setup
├── docs/                # Documentation
│   ├── guides/          # Setup and deployment guides
│   ├── api/             # API documentation
│   └── architecture/    # Architecture documentation
├── scripts/             # Utility scripts
├── archive/             # Archived files
├── chrome_extension/    # Browser extension (if applicable)
└── uploads/             # User uploaded files
```

## 🚀 Deployment Files

### Production Deployment (Render)
- `Procfile`: `web: python start.py`
- `render.yaml`: Complete Render configuration
- `build.sh`: Build script for dependencies and database setup
- `requirements.txt`: Python dependencies
- `start.py`: Production entry point
- `env.example`: Environment variables template

### Development
- `.env`: Local environment variables
- `runtime.txt`: Python version specification

## 🔧 Key Features

### Core Functionality
- **User Management**: Registration, authentication, profiles
- **Lesson Management**: Create, edit, organize lessons
- **Note Taking**: Advanced note management with search
- **Pomodoro Timer**: Built-in productivity timer
- **Dashboard**: Analytics and progress tracking

### Integrations
- **Google Classroom**: Import courses and manage data
- **Microsoft Teams**: Import teams and lessons
- **OAuth 2.0**: Secure authentication

### UI/UX
- **Responsive Design**: Works on all devices
- **Modern UI**: Glassmorphism effects, smooth animations
- **Google Fonts**: Professional typography (Prompt)
- **Professional Theme**: Blue and white color scheme

## 📚 Documentation

- [README.md](README.md) - Main project documentation
- [docs/guides/DEPLOYMENT_GUIDE.md](docs/guides/DEPLOYMENT_GUIDE.md) - Deployment instructions
- [docs/CLASS_OOP_DOCUMENTATION.md](docs/CLASS_OOP_DOCUMENTATION.md) - OOP implementation
- [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) - Code of conduct
- [CONTRIBUTING.md](CONTRIBUTING.md) - Contribution guidelines

## 🛠️ Development Setup

1. **Clone and setup**
   ```bash
   git clone <repository>
   cd PyProject
   pip install -r requirements.txt
   ```

2. **Environment setup**
   ```bash
   cp env.example .env
   # Edit .env with your values
   ```

3. **Database setup**
   ```bash
   python database/setup_database.py
   ```

4. **Run application**
   ```bash
   python start.py
   ```

## 🌐 Production Deployment

### Render (Recommended)
1. Fork repository
2. Create Web Service on Render
3. Connect GitHub repository
4. Set environment variables
5. Create PostgreSQL database
6. Deploy

### Environment Variables
```bash
FLASK_ENV=production
FLASK_DEBUG=0
FLASK_SECRET_KEY=<secure_key>
DATABASE_URL=<postgresql_url>
GOOGLE_CLIENT_ID=<oauth_client_id>
GOOGLE_CLIENT_SECRET=<oauth_secret>
OAUTHLIB_INSECURE_TRANSPORT=0
```

## 📊 Version History

- **v1.0.0**: Initial release
- **v1.1.0**: Google Classroom integration
- **v1.2.0**: Microsoft Teams integration
- **v1.3.0**: OOP architecture refactoring
- **v1.4.0**: Enhanced UI/UX design

## 🤝 Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed contribution guidelines.

## 📄 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) for details.

---

**Smart Learning Hub** - Empowering education through technology 🎓
