# 🚀 Smart Learning Hub - Render Deployment Guide

## 📋 Overview

This guide will help you deploy your Smart Learning Hub application to Render.com, a modern cloud platform that's perfect for Flask applications.

## 🎯 Why Render?

- ✅ **Free tier** available
- ✅ **PostgreSQL database** included
- ✅ **Auto-deploy** from GitHub
- ✅ **SSL certificates** provided
- ✅ **Easy environment variables** management
- ✅ **No server management** required

## 🚀 Step-by-Step Deployment

### Step 1: Prepare Your Repository

1. **Push your code to GitHub** (if not already done):
   ```bash
   git add .
   git commit -m "Prepare for Render deployment"
   git push origin main
   ```

2. **Verify these files exist**:
   - `requirements-production.txt`
   - `Procfile`
   - `runtime.txt`
   - `render.yaml`

### Step 2: Create Render Account

1. Go to [render.com](https://render.com)
2. Sign up with GitHub account
3. Connect your GitHub repository

### Step 3: Create Database

1. In Render dashboard, click **"New +"**
2. Select **"PostgreSQL"**
3. Configure:
   - **Name**: `smart-learning-hub-db`
   - **Plan**: Free (or higher for production)
   - **Region**: Choose closest to your users
4. Click **"Create Database"**

### Step 4: Create Web Service

1. In Render dashboard, click **"New +"**
2. Select **"Web Service"**
3. Connect your GitHub repository
4. Configure the service:

   **Basic Settings:**
   - **Name**: `smart-learning-hub`
   - **Environment**: `Python 3`
   - **Region**: Same as database
   - **Branch**: `main`
   - **Root Directory**: Leave empty
   - **Build Command**: `pip install -r requirements-production.txt`
   - **Start Command**: `gunicorn --bind 0.0.0.0:$PORT start_server:app`

   **Advanced Settings:**
   - **Plan**: Free (or higher for production)

### Step 5: Configure Environment Variables

In your web service settings, add these environment variables:

**Required Variables:**
```
FLASK_ENV=production
FLASK_DEBUG=0
OAUTHLIB_INSECURE_TRANSPORT=0
DATABASE_URL=<Copy from your PostgreSQL service>
```

**Google OAuth (Get these from Google Cloud Console):**
```
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
```

**Security:**
```
FLASK_SECRET_KEY=your-super-secure-secret-key-32-chars-minimum
```

### Step 6: Set Up Google OAuth

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create a new project or select existing
3. Enable Google+ API and Google Classroom API
4. Create OAuth 2.0 credentials:
   - **Application type**: Web application
   - **Authorized redirect URIs**: 
     - `https://your-app-name.onrender.com/auth/google/callback`
     - `https://your-app-name.onrender.com/oauth2callback`

### Step 7: Deploy

1. Click **"Create Web Service"**
2. Wait for build to complete (5-10 minutes)
3. Your app will be available at: `https://your-app-name.onrender.com`

## 🔧 Configuration Files

### render.yaml (Auto-deployment)
```yaml
services:
  - type: web
    name: smart-learning-hub
    env: python
    plan: free
    buildCommand: pip install -r requirements-production.txt
    startCommand: gunicorn --bind 0.0.0.0:$PORT start_server:app
    envVars:
      - key: FLASK_ENV
        value: production
      - key: FLASK_DEBUG
        value: 0
```

### Procfile
```
web: gunicorn --bind 0.0.0.0:$PORT start_server:app
```

### runtime.txt
```
python-3.11.9
```

## 🔒 Security Checklist

- ✅ Remove hardcoded secrets from code
- ✅ Use environment variables for all secrets
- ✅ Set `FLASK_DEBUG=0` in production
- ✅ Set `OAUTHLIB_INSECURE_TRANSPORT=0`
- ✅ Use strong `FLASK_SECRET_KEY` (32+ characters)

## 📊 Monitoring & Maintenance

### View Logs
- Go to your service dashboard
- Click **"Logs"** tab
- Monitor for errors and performance

### Database Management
- Use Render's built-in database dashboard
- Or connect with external tools using connection string

### Auto-deployments
- Render automatically deploys when you push to main branch
- You can disable auto-deploy in service settings

## 💰 Pricing

### Free Tier
- **Web Service**: 750 hours/month (sleeps after 15 min inactivity)
- **Database**: 1GB storage, 1GB RAM
- **Bandwidth**: 100GB/month

### Paid Plans
- **Starter**: $7/month (always-on web service)
- **Standard**: $25/month (better performance)
- **Pro**: $85/month (high availability)

## 🚨 Troubleshooting

### Common Issues

1. **Build Fails**
   - Check `requirements-production.txt` for correct dependencies
   - Verify `runtime.txt` has correct Python version
   - Check build logs for specific errors

2. **Database Connection Issues**
   - Verify `DATABASE_URL` is set correctly
   - Check database is running
   - Ensure `psycopg2-binary` is in requirements

3. **Google OAuth Issues**
   - Verify redirect URIs in Google Console
   - Check `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET`
   - Ensure `OAUTHLIB_INSECURE_TRANSPORT=0`

4. **App Crashes**
   - Check application logs
   - Verify all environment variables are set
   - Test locally first

### Performance Optimization

1. **Enable Redis** (for sessions):
   ```bash
   # Add to requirements-production.txt
   redis==5.0.1
   Flask-Session==0.5.0
   ```

2. **Database Optimization**:
   - Add indexes for frequently queried fields
   - Use connection pooling

3. **Static Files**:
   - Consider using CDN for static assets
   - Optimize images and CSS

## 🔄 Updates

To update your application:
1. Push changes to GitHub
2. Render will automatically rebuild and deploy
3. Monitor logs for any issues

## 📞 Support

- **Render Documentation**: [render.com/docs](https://render.com/docs)
- **Render Community**: [community.render.com](https://community.render.com)
- **Application Logs**: Check your service dashboard

---

**Your app will be live at**: `https://your-app-name.onrender.com`

**Database will be available at**: Render dashboard → Your database service
