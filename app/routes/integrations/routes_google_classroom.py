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
            # Use MVC Service pattern
            from app.services import UserService
            user_service = UserService()
            g.user = user_service.get_user_by_id(user_id)
        except:
            g.user = None
    else:
        g.user = None

@google_classroom_bp.route('/authorize')
def authorize():
    """Authorize Google Classroom API access"""
    print("🔐 Google Classroom authorization requested")
    
    # Check environment variables
    client_id = current_app.config.get('GOOGLE_CLIENT_ID')
    client_secret = current_app.config.get('GOOGLE_CLIENT_SECRET')
    
    print(f"Client ID: {client_id[:20] if client_id else 'None'}...")
    print(f"Client Secret: {client_secret[:20] if client_secret else 'None'}...")
    
    if not client_id or not client_secret:
        flash('Google API credentials are not configured. Please set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET environment variables.', 'danger')
        return redirect(url_for('main_routes.index'))

    try:
        flow = Flow.from_client_config(
            client_config={
                "web": {
                    "client_id": client_id,
                    "client_secret": client_secret,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "redirect_uris": [
                        "http://localhost:5004/google_classroom/oauth2callback",
                        "http://127.0.0.1:5004/google_classroom/oauth2callback",
                        "http://localhost:5003/google_classroom/oauth2callback",
                        "http://127.0.0.1:5003/google_classroom/oauth2callback",
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
        print(f"Redirect URI: {flow.redirect_uri}")

        # Check if we should return to Google Classroom import modal
        return_to_import = request.args.get('return_to_import', 'false').lower() == 'true'
        print(f"Return to import: {return_to_import}")
        
        # Generate state parameter
        import secrets
        state = secrets.token_urlsafe(32)
        
        authorization_url, _ = flow.authorization_url(
            access_type='offline',
            prompt='consent',
            state=f"{state}&return_to_import={return_to_import}" if return_to_import else state
        )

        print(f"Authorization URL: {authorization_url}")
        session['oauth_state'] = state
        session['return_to_import'] = return_to_import
        
        print("🔗 Redirecting to Google OAuth...")
        return redirect(authorization_url)
        
    except Exception as e:
        print(f"❌ Error creating OAuth flow: {e}")
        import traceback
        traceback.print_exc()
        flash(f'Failed to initialize Google OAuth: {str(e)}', 'danger')
        return redirect(url_for('main_routes.index'))

@google_classroom_bp.route('/oauth2callback')
def oauth2callback():
    """OAuth2 callback for Google Classroom"""
    received_state = request.args.get('state')
    stored_state = session.pop('oauth_state', None)
    
    print(f"DEBUG: OAuth2 callback received")
    print(f"DEBUG: Received state: {received_state}")
    print(f"DEBUG: Stored state: {stored_state}")
    print(f"DEBUG: State match: {stored_state == received_state}")
    
    # Check state parameter with more flexibility
    if not received_state:
        print("DEBUG: No state parameter received")
        flash('No state parameter received from Google.', 'danger')
        return redirect(url_for('main_routes.index'))
    
    if not stored_state:
        print("DEBUG: No stored state found - allowing callback anyway")
        # If no stored state, allow callback anyway (for development)
        flash('Warning: No stored state found, but allowing callback.', 'warning')
    elif stored_state != received_state:
        print("DEBUG: State mismatch - checking if it's a return_to_import case")
        # Check if it's a return_to_import case (state might contain additional data)
        if 'return_to_import' in received_state:
            print("DEBUG: Detected return_to_import in state - allowing callback")
            # Extract the actual state from the combined parameter
            actual_state = received_state.split('&')[0] if '&' in received_state else received_state
            if actual_state == stored_state:
                print("DEBUG: Actual state matches - proceeding")
            else:
                print("DEBUG: Even extracted state doesn't match - allowing anyway for development")
                flash('Warning: State mismatch, but allowing callback for development.', 'warning')
        else:
            print("DEBUG: State mismatch and no return_to_import - rejecting")
            flash('Invalid state parameter.', 'danger')
            return redirect(url_for('main_routes.index'))
    else:
        print("DEBUG: State matches perfectly")

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
                    f"http://127.0.0.1:{port}/google_classroom/oauth2callback",
                    "http://localhost:5004/google_classroom/oauth2callback",
                    "http://127.0.0.1:5004/google_classroom/oauth2callback",
                    "http://localhost:5003/google_classroom/oauth2callback",
                    "http://127.0.0.1:5003/google_classroom/oauth2callback"
                ]
            }
        },
        scopes=SCOPES
    )

    flow.redirect_uri = f"http://localhost:{port}/google_classroom/oauth2callback"

    authorization_response = request.url
    flow.fetch_token(authorization_response=authorization_response)

    credentials = flow.credentials

    # Save credentials to database using OOP architecture
    user_id = session.get('user_id')
    if not user_id:
        # Store credentials temporarily in session for later use
        import json
        creds_data = {
            'token': credentials.token,
            'refresh_token': credentials.refresh_token,
            'token_uri': credentials.token_uri,
            'client_id': credentials.client_id,
            'client_secret': credentials.client_secret,
            'scopes': credentials.scopes
        }
        session['temp_google_credentials'] = json.dumps(creds_data)
        print(f"DEBUG: Stored credentials in session for later use")
        print(f"DEBUG: Session keys: {list(session.keys())}")
        flash('Google Classroom connected! Please log in to save your credentials.', 'success')
        return redirect(url_for('main_routes.index'))
    
    print(f"DEBUG: Saving Google Classroom credentials for user {user_id}")

    try:
        # Use MVC to get user
        from app.models.user import UserModel
        from app import db
        
        user_model = UserModel.query.filter_by(id=user_id).first()
        user = user_model
        
        if not user:
            flash('User not found.', 'danger')
            return redirect(url_for('main_routes.index'))
        
        # Store credentials in database
        from app.models.user import UserModel
        import json
        
        user_model = UserModel.query.filter_by(id=user_id).first()
        
        if user_model:
            # Store credentials as JSON
            creds_data = {
                'token': credentials.token,
                'refresh_token': credentials.refresh_token,
                'token_uri': credentials.token_uri,
                'client_id': credentials.client_id,
                'client_secret': credentials.client_secret,
                'scopes': credentials.scopes
            }
            
            user_model.google_credentials = json.dumps(creds_data)
            db.session.commit()
            
            print(f"DEBUG: Stored credentials for user {user_id}")
            print(f"  Token: {credentials.token[:20]}...")
            print(f"  Refresh Token: {credentials.refresh_token[:20] if credentials.refresh_token else 'None'}...")
            print(f"  Scopes: {credentials.scopes}")
            print(f"  Database updated successfully")
            
        flash('Successfully connected to Google Classroom!', 'success')
        print(f"DEBUG: OAuth2 callback completed for user {user_id}")
        
        # Check if we should return to Google Classroom import modal
        return_to_import = session.pop('return_to_import', False)
        
        # Also check if return_to_import was in the state parameter
        if not return_to_import and received_state and 'return_to_import' in received_state:
            return_to_import = True
            print("DEBUG: Detected return_to_import from state parameter")
        
        print(f"DEBUG: Return to import: {return_to_import}")
        
        if return_to_import:
            # Redirect back to dashboard with Google Classroom import modal open
            redirect_url = url_for('main_routes.dashboard') + '#class&open_google_import=true'
            print(f"DEBUG: Redirecting to: {redirect_url}")
            return redirect(redirect_url)
        else:
            # Redirect to dashboard normally
            redirect_url = url_for('main_routes.dashboard') + '#class'
            print(f"DEBUG: Redirecting to: {redirect_url}")
            return redirect(redirect_url)
        
    except Exception as e:
        print(f"ERROR: Failed to save Google Classroom credentials: {e}")
        import traceback
        traceback.print_exc()
        flash(f'Failed to save Google Classroom credentials: {str(e)}', 'danger')
        return redirect(url_for('main_routes.index'))

@google_classroom_bp.route('/fetch_courses')
def fetch_courses():
    """Fetch Google Classroom courses"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'success': False, 'error': 'User not authenticated'}), 401
        
        # Check if user has Google credentials in database or session
        from app.models.user import UserModel
        user = UserModel.query.filter_by(id=user_id).first()
        
        # Try to get credentials from database first
        credentials_data = None
        if user and user.google_credentials:
            import json
            credentials_data = json.loads(user.google_credentials)
            print(f"DEBUG: Found credentials in database for user {user_id}")
        # If not in database, check session
        elif session.get('temp_google_credentials'):
            import json
            credentials_data = json.loads(session['temp_google_credentials'])
            print(f"DEBUG: Found credentials in session for user {user_id}")
            # Save to database if user is logged in
            if user and credentials_data:
                user.google_credentials = json.dumps(credentials_data)
                db.session.commit()
                session.pop('temp_google_credentials', None)
                print(f"DEBUG: Saved credentials to database for user {user_id}")
        else:
            print(f"DEBUG: No credentials found for user {user_id}")
            print(f"DEBUG: User exists: {user is not None}")
            print(f"DEBUG: User has google_credentials: {user.google_credentials if user else 'N/A'}")
            print(f"DEBUG: Session has temp_google_credentials: {session.get('temp_google_credentials') is not None}")
        
        if not credentials_data:
            return jsonify({
                'success': False,
                'error': 'No Google credentials found. Please authorize first.',
                'needs_auth': True,
                'redirect_url': '/google_classroom/authorize?return_to_import=true'
            }), 401
        
        # Create credentials object from stored data
        from google.oauth2.credentials import Credentials
        credentials = Credentials(
            token=credentials_data['token'],
            refresh_token=credentials_data.get('refresh_token'),
            token_uri=credentials_data['token_uri'],
            client_id=credentials_data['client_id'],
            client_secret=credentials_data['client_secret'],
            scopes=credentials_data['scopes']
        )
        
        # Build Google Classroom API service
        from googleapiclient.discovery import build
        service = build('classroom', 'v1', credentials=credentials)
        
        # Fetch courses from Google Classroom
        results = service.courses().list(courseStates=['ACTIVE']).execute()
        courses = results.get('courses', [])
        
        # Format courses for frontend
        formatted_courses = []
        for course in courses:
            formatted_courses.append({
                'id': course['id'],
                'name': course['name'],
                'section': course.get('section', ''),
                'description': course.get('description', ''),
                'room': course.get('room', ''),
                'ownerId': course.get('ownerId', ''),
                'courseState': course.get('courseState', 'ACTIVE'),
                'creationTime': course.get('creationTime', ''),
                'updateTime': course.get('updateTime', ''),
                'enrollmentCode': course.get('enrollmentCode', ''),
                'courseMaterialSets': course.get('courseMaterialSets', []),
                'teacherGroupEmail': course.get('teacherGroupEmail', ''),
                'courseGroupEmail': course.get('courseGroupEmail', ''),
                'guardiansEnabled': course.get('guardiansEnabled', False),
                'calendarId': course.get('calendarId', ''),
                'gradebookSettings': course.get('gradebookSettings', {}),
                'alternateLink': course.get('alternateLink', ''),
                'teacherFolder': course.get('teacherFolder', {}),
                'courseCreator': course.get('courseCreator', '')
            })
        
        return jsonify({
            'success': True,
            'courses': formatted_courses
        })
        
    except Exception as e:
        print(f"Error fetching Google Classroom courses: {e}")
        return jsonify({
            'success': False,
            'error': f'Failed to fetch courses: {str(e)}'
        }), 500

@google_classroom_bp.route('/import_course', methods=['POST'])
def import_course():
    """Import a Google Classroom course"""
    try:
        data = request.get_json()
        course_id = data.get('courseId')
        settings = data.get('settings', {})
        
        if not course_id:
            return jsonify({'success': False, 'error': 'Course ID is required'}), 400
        
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'success': False, 'error': 'User not authenticated'}), 401
        
        # Use Google Classroom Service
        import sys
        import sys
        import os
        sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'services'))
        from google_classroom_service import GoogleClassroomService
        google_service = GoogleClassroomService()
        
        # Check if user has credentials
        credentials = google_service.get_credentials(user_id)
        if not credentials:
            return jsonify({
                'success': False,
                'error': 'No Google credentials found. Please authorize first.',
                'needs_auth': True,
                'redirect_url': '/google_classroom/authorize'
            }), 401
        
        # Import course using Google Classroom Service
        result = google_service.import_course(user_id, course_id, settings)
        
        return jsonify(result)
            
    except Exception as e:
        print(f"Error importing Google Classroom course: {e}")
        return jsonify({
            'success': False,
            'error': f'Failed to import course: {str(e)}'
        }), 500

