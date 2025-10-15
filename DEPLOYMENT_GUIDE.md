# 🚀 Smart Learning Hub - Deployment Guide

## 📋 Overview

This guide will help you deploy the Smart Learning Hub application to production using Docker and best practices for security and performance.

## ⚠️ Pre-Deployment Checklist

### 1. Security Issues to Fix

**CRITICAL:** The following hardcoded secrets must be removed before production:

- `start_server.py` lines 120-122: Hardcoded Google OAuth credentials
- `scripts/start_flask_new.sh` lines 61-63: Hardcoded credentials
- `scripts/start_flask_simple.sh` lines 10-12: Hardcoded credentials

**Action Required:** Replace all hardcoded credentials with environment variables.

### 2. Environment Variables

Create `.env.production` file with your actual values:

```bash
# Copy the example file
cp env.production.example .env.production

# Edit with your actual values
nano .env.production
```

**Required Variables:**
- `FLASK_SECRET_KEY`: Generate a secure 32+ character random string
- `GOOGLE_CLIENT_ID`: Your production Google OAuth client ID
- `GOOGLE_CLIENT_SECRET`: Your production Google OAuth client secret
- `DATABASE_URL`: PostgreSQL connection string (recommended)

## 🐳 Docker Deployment (Recommended)

### Quick Start

```bash
# 1. Make deployment script executable
chmod +x deploy.sh

# 2. Run deployment script
./deploy.sh
```

### Manual Deployment

```bash
# 1. Build and start services
docker-compose up --build -d

# 2. Check status
docker-compose ps

# 3. View logs
docker-compose logs -f
```

### Services Included

- **Web App**: Flask application (port 8000)
- **Database**: PostgreSQL (port 5432)
- **Redis**: Session storage (port 6379)
- **Nginx**: Reverse proxy with SSL (ports 80, 443)

## 🔧 Alternative Deployment Methods

### 1. Traditional Server Deployment

#### Prerequisites
- Ubuntu 20.04+ or CentOS 8+
- Python 3.11+
- PostgreSQL 13+
- Nginx
- SSL certificate

#### Steps

```bash
# 1. Install dependencies
sudo apt update
sudo apt install python3.11 python3.11-venv postgresql nginx

# 2. Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# 3. Install requirements
pip install -r requirements-production.txt

# 4. Set up database
sudo -u postgres createdb smart_learning_hub
python database/setup_database.py

# 5. Configure environment
cp env.production.example .env.production
# Edit .env.production with your values

# 6. Run with Gunicorn
gunicorn --bind 0.0.0.0:8000 --workers 4 start_server:app

# 7. Configure Nginx (copy nginx.conf to /etc/nginx/sites-available/)
sudo cp nginx.conf /etc/nginx/sites-available/smart-learning-hub
sudo ln -s /etc/nginx/sites-available/smart-learning-hub /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### 2. Cloud Platform Deployment

#### Heroku
```bash
# 1. Install Heroku CLI
# 2. Login and create app
heroku login
heroku create your-app-name

# 3. Set environment variables
heroku config:set FLASK_ENV=production
heroku config:set FLASK_SECRET_KEY=your-secret-key
heroku config:set GOOGLE_CLIENT_ID=your-client-id
heroku config:set GOOGLE_CLIENT_SECRET=your-client-secret

# 4. Add PostgreSQL addon
heroku addons:create heroku-postgresql:hobby-dev

# 5. Deploy
git push heroku main
```

#### DigitalOcean App Platform
1. Connect your GitHub repository
2. Configure environment variables in the dashboard
3. Set build command: `pip install -r requirements-production.txt`
4. Set run command: `gunicorn --bind 0.0.0.0:8080 start_server:app`

#### AWS Elastic Beanstalk
1. Create `.ebextensions/01_packages.config`:
```yaml
packages:
  yum:
    postgresql-devel: []
    gcc: []
```
2. Deploy with EB CLI: `eb deploy`

## 🔒 Security Configuration

### 1. SSL/TLS Setup

#### Let's Encrypt (Recommended)
```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Get certificate
sudo certbot --nginx -d yourdomain.com

# Auto-renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

#### Self-signed (Development only)
```bash
# Already included in deploy.sh
mkdir ssl
openssl req -x509 -newkey rsa:4096 -keyout ssl/key.pem -out ssl/cert.pem -days 365 -nodes
```

### 2. Firewall Configuration

```bash
# UFW (Ubuntu)
sudo ufw allow 22/tcp   # SSH
sudo ufw allow 80/tcp   # HTTP
sudo ufw allow 443/tcp  # HTTPS
sudo ufw enable
```

### 3. Database Security

```sql
-- Create dedicated database user
CREATE USER smart_learning_user WITH PASSWORD 'secure_password';
CREATE DATABASE smart_learning_hub OWNER smart_learning_user;
GRANT ALL PRIVILEGES ON DATABASE smart_learning_hub TO smart_learning_user;
```

## 📊 Monitoring & Maintenance

### 1. Health Checks

```bash
# Check application health
curl -f http://localhost:8000/health

# Check database connection
docker-compose exec web python -c "from app import create_app, db; app = create_app(); print('DB OK' if db.engine.execute('SELECT 1').fetchone() else 'DB ERROR')"
```

### 2. Log Monitoring

```bash
# View application logs
docker-compose logs -f web

# View all logs
docker-compose logs -f

# Log rotation (add to crontab)
0 0 * * * docker-compose logs --no-color > logs/app-$(date +\%Y\%m\%d).log
```

### 3. Backup Strategy

```bash
# Database backup
docker-compose exec db pg_dump -U postgres smart_learning_hub > backup_$(date +%Y%m%d).sql

# File backup
tar -czf uploads_backup_$(date +%Y%m%d).tar.gz uploads/

# Automated backup script
cat > backup.sh << 'EOF'
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
docker-compose exec -T db pg_dump -U postgres smart_learning_hub > backups/db_$DATE.sql
tar -czf backups/uploads_$DATE.tar.gz uploads/
# Keep only last 30 days
find backups/ -name "*.sql" -mtime +30 -delete
find backups/ -name "*.tar.gz" -mtime +30 -delete
EOF
chmod +x backup.sh
```

## 🔄 Updates & Maintenance

### 1. Application Updates

```bash
# Pull latest code
git pull origin main

# Rebuild and restart
docker-compose down
docker-compose up --build -d

# Run migrations if needed
docker-compose exec web python -c "from app import create_app, db; app = create_app(); db.create_all()"
```

### 2. Dependency Updates

```bash
# Update requirements
pip-compile requirements-production.in

# Rebuild with new dependencies
docker-compose build --no-cache
docker-compose up -d
```

## 🚨 Troubleshooting

### Common Issues

1. **Port already in use**
   ```bash
   # Find process using port
   sudo lsof -i :8000
   # Kill process
   sudo kill -9 <PID>
   ```

2. **Database connection failed**
   ```bash
   # Check database status
   docker-compose ps db
   # Check logs
   docker-compose logs db
   ```

3. **SSL certificate issues**
   ```bash
   # Test SSL
   openssl s_client -connect localhost:443 -servername localhost
   ```

4. **Permission issues**
   ```bash
   # Fix uploads directory permissions
   sudo chown -R www-data:www-data uploads/
   sudo chmod -R 755 uploads/
   ```

### Performance Optimization

1. **Enable Gzip compression in Nginx**
2. **Set up Redis for session storage**
3. **Use CDN for static files**
4. **Implement database connection pooling**
5. **Add application monitoring (Sentry)**

## 📞 Support

For deployment issues:
1. Check logs: `docker-compose logs -f`
2. Verify environment variables: `docker-compose exec web env`
3. Test database connection: `docker-compose exec web python -c "from app import create_app, db; print('DB OK')"`
4. Check SSL: `openssl s_client -connect localhost:443`

---

**Remember:** Always test deployment in a staging environment before production!
