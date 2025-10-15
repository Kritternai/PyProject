# Smart Learning Hub

A comprehensive Flask-based learning management system with Google Classroom and Microsoft Teams integration.

## 🚀 Features

- **User Management**: Registration, authentication, and profile management
- **Lesson Management**: Create, edit, and organize lessons with OOP architecture
- **Google Classroom Integration**: Import courses and manage classroom data
- **Microsoft Teams Integration**: Import teams and lessons
- **Note Taking**: Advanced note management with search and filtering
- **Pomodoro Timer**: Built-in productivity timer
- **Dashboard**: Comprehensive analytics and progress tracking
- **Modern UI**: Responsive design with Google Fonts (Prompt)

## 🏗️ Architecture

- **Framework**: Flask 3.1.1
- **Database**: SQLite (development) / PostgreSQL (production)
- **Frontend**: Bootstrap 5.3.3, Vanilla JavaScript
- **Authentication**: Google OAuth 2.0
- **Design Pattern**: MVC with OOP principles (4 Pillars)

## 📦 Installation

### Prerequisites
- Python 3.11+
- Git

### Local Development

1. **Clone the repository**
   ```bash
   git clone https://github.com/Kritternai/PyProject.git
   cd PyProject
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   cp env.example .env
   # Edit .env with your actual values
   ```

4. **Initialize database**
   ```bash
   python database/setup_database.py
   ```

5. **Run the application**
   ```bash
   python start.py
   ```

6. **Access the application**
   - URL: http://localhost:8000
   - Default user: admin@admin.admin / admin

## 🌐 Deployment

### Render (Recommended)

1. **Fork this repository**
2. **Create a new Web Service on Render**
3. **Connect your GitHub repository**
4. **Configure environment variables** (see `env.example`)
5. **Create a PostgreSQL database service**
6. **Deploy**

The application will be automatically deployed with:
- `Procfile`: `web: python start.py`
- `render.yaml`: Complete Render configuration
- `build.sh`: Build script for dependencies and database setup

### Environment Variables for Production

```bash
FLASK_ENV=production
FLASK_DEBUG=0
FLASK_SECRET_KEY=<secure_random_key>
DATABASE_URL=<render_postgresql_url>
GOOGLE_CLIENT_ID=<your_google_client_id>
GOOGLE_CLIENT_SECRET=<your_google_client_secret>
OAUTHLIB_INSECURE_TRANSPORT=0
```

## 🔧 Configuration

### Google OAuth Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable Google Classroom API
4. Create OAuth 2.0 credentials
5. Add authorized redirect URIs:
   - `http://localhost:8000/auth/google/callback` (development)
   - `https://your-app.onrender.com/auth/google/callback` (production)

### Microsoft Teams Integration

1. Register application in [Azure Portal](https://portal.azure.com/)
2. Configure API permissions for Microsoft Graph
3. Set up OAuth 2.0 credentials
4. Update configuration in `app/config/`

## 📁 Project Structure

```
├── app/                    # Main application
│   ├── config/            # Configuration files
│   ├── controllers/       # MVC Controllers
│   ├── models/           # SQLAlchemy models
│   ├── routes/           # Flask routes
│   ├── services/         # Business logic (OOP)
│   ├── static/           # CSS, JS, images
│   ├── templates/        # Jinja2 templates
│   └── utils/            # Utilities and exceptions
├── database/             # Database scripts
├── docs/                # Documentation
├── scripts/             # Utility scripts
├── Procfile             # Render deployment
├── render.yaml          # Render configuration
├── requirements.txt     # Python dependencies
└── start.py             # Application entry point
```

## 🎯 Key Features

### OOP Architecture
- **Encapsulation**: Private methods and data hiding
- **Inheritance**: Base services with specialized implementations
- **Polymorphism**: Multiple service types for different platforms
- **Abstraction**: Abstract base classes with concrete implementations

### Modern UI/UX
- Responsive design for all devices
- Google Fonts (Prompt) integration
- Glassmorphism effects
- Smooth animations and transitions
- Professional color schemes

### Integration Capabilities
- Google Classroom API integration
- Microsoft Teams API integration
- OAuth 2.0 authentication
- RESTful API endpoints

## 🧪 Testing

```bash
# Test application import
python -c "from app import create_app; app = create_app('development'); print('✅ Application ready')"

# Test database connection
python database/setup_database.py

# Run specific tests (if available)
python -m pytest tests/
```

## 📚 Documentation

- [Class System OOP Documentation](docs/CLASS_OOP_DOCUMENTATION.md)
- [Database Schema](docs/database/)
- [API Documentation](docs/api/)
- [Setup Guides](docs/setup/)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

For support and questions:
- Create an issue on GitHub
- Check the documentation in the `docs/` folder
- Review the setup guides for common issues

## 🔄 Version History

- **v1.0.0**: Initial release with basic features
- **v1.1.0**: Added Google Classroom integration
- **v1.2.0**: Added Microsoft Teams integration
- **v1.3.0**: Implemented OOP architecture refactoring
- **v1.4.0**: Enhanced UI/UX with modern design

---

**Smart Learning Hub** - Empowering education through technology 🎓