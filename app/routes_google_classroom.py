"""
Google Classroom API Integration Routes
Separate blueprint for Google Classroom functionality
"""

from flask import Blueprint, render_template, request, redirect, url_for, session, g, flash, jsonify, current_app
from functools import wraps
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from app import db

# Create Google Classroom blueprint
google_classroom_bp = Blueprint('google_classroom', __name__, url_prefix='/google_classroom')

# Google Classroom API Scopes
SCOPES = [
    'https://www.googleapis.com/auth/classroom.courses.readonly',
    'https://www.googleapis.com/auth/classroom.announcements.readonly',
    'https://www.googleapis.com/auth/classroom.courseworkmaterials.readonly',
    'https://www.googleapis.com/auth/classroom.course-work.readonly',
    'https://www.googleapis.com/auth/classroom.student-submissions.me.readonly',
    'https://www.googleapis.com/auth/classroom.topics.readonly',
    'https://www.googleapis.com/auth/classroom.rosters.readonly',
    'https://www.googleapis.com/auth/userinfo.profile',
    'openid',
    'https://www.googleapis.com/auth/userinfo.email',
    'https://www.googleapis.com/auth/drive.readonly'
]

# Decorator for login required
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

@google_classroom_bp.before_request
def load_logged_in_user():
    """Load logged in user for Google Classroom routes"""
    user_id = session.get('user_id')
    if user_id:
        try:
            from app.infrastructure.di.container import get_service
            from app.domain.interfaces.services.user_service import UserService
            user_service = get_service(UserService)
            g.user = user_service.get_user_by_id(user_id)
        except:
            g.user = None
    else:
        g.user = None

@google_classroom_bp.route('/authorize')
@login_required
def authorize():
    """Authorize Google Classroom API access"""
    if not current_app.config.get('GOOGLE_CLIENT_ID') or not current_app.config.get('GOOGLE_CLIENT_SECRET'):
        flash('Google API credentials are not configured. Please set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET environment variables.', 'danger')
        return redirect(url_for('main.index'))

    flow = Flow.from_client_config(
        client_config={
            "web": {
                "client_id": current_app.config['GOOGLE_CLIENT_ID'],
                "client_secret": current_app.config['GOOGLE_CLIENT_SECRET'],
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": [
                    "http://localhost:5004/google_classroom/oauth2callback",
                    "http://127.0.0.1:5004/google_classroom/oauth2callback",
                    "http://localhost:8000/google_classroom/oauth2callback",
                    "http://localhost:8001/google_classroom/oauth2callback",
                    "http://127.0.0.1:8000/google_classroom/oauth2callback",
                    "http://127.0.0.1:8001/google_classroom/oauth2callback"
                ]
            }
        },
        scopes=SCOPES
    )

    # Use port from current app config
    port = current_app.config.get('PORT', 5004)
    flow.redirect_uri = f"http://localhost:{port}/google_classroom/oauth2callback"

    authorization_url, state = flow.authorization_url(
        access_type='offline',
        prompt='consent'
    )

    session['oauth_state'] = state
    return redirect(authorization_url)

@google_classroom_bp.route('/oauth2callback')
def oauth2callback():
    """OAuth2 callback for Google Classroom"""
    state = session.pop('oauth_state', None)

    if not state or state != request.args.get('state'):
        flash('Invalid state parameter.', 'danger')
        return redirect(url_for('main.index'))

    port = current_app.config.get('PORT', 5004)
    
    flow = Flow.from_client_config(
        client_config={
            "web": {
                "client_id": current_app.config['GOOGLE_CLIENT_ID'],
                "client_secret": current_app.config['GOOGLE_CLIENT_SECRET'],
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": [
                    f"http://localhost:{port}/google_classroom/oauth2callback",
                    f"http://127.0.0.1:{port}/google_classroom/oauth2callback"
                ]
            }
        },
        scopes=SCOPES,
        state=state
    )

    flow.redirect_uri = f"http://localhost:{port}/google_classroom/oauth2callback"

    authorization_response = request.url
    flow.fetch_token(authorization_response=authorization_response)

    credentials = flow.credentials

    # Save credentials to database using OOP architecture
    user_id = session['user_id']
    print(f"DEBUG: Saving Google Classroom credentials for user {user_id}")

    try:
        # Use OOP architecture to store credentials
        from app.infrastructure.di.container import get_service
        from app.domain.interfaces.repositories.user_repository import UserRepository
        
        user_repo = get_service(UserRepository)
        user = user_repo.get_by_id(user_id)
        
        if not user:
            flash('User not found.', 'danger')
            return redirect(url_for('main.index'))
        
        # Store credentials in user metadata (you may want to create a separate table for this)
        # For now, we'll use a simple approach
        from app.infrastructure.persistence.models.user_model import UserModel
        user_model = UserModel.query.filter_by(id=user_id).first()
        
        if user_model:
            # Store credentials as JSON in a metadata field (you'll need to add this field)
            # For now, we'll just print a message
            print(f"DEBUG: Would store credentials for user {user_id}")
            print(f"  Token: {credentials.token[:20]}...")
            print(f"  Refresh Token: {credentials.refresh_token[:20] if credentials.refresh_token else 'None'}...")
            
        flash('Successfully connected to Google Classroom!', 'success')
        print(f"DEBUG: OAuth2 callback completed for user {user_id}")
        
        # Redirect to class page
        return redirect(url_for('main.index') + '#class')
        
    except Exception as e:
        print(f"ERROR: Failed to save Google Classroom credentials: {e}")
        import traceback
        traceback.print_exc()
        flash(f'Failed to save Google Classroom credentials: {str(e)}', 'danger')
        return redirect(url_for('main.index'))

@google_classroom_bp.route('/fetch_courses')
@login_required
def fetch_courses():
    """Fetch Google Classroom courses (placeholder)"""
    flash('Google Classroom course fetching is under development.', 'info')
    return redirect(url_for('main.index') + '#class')

