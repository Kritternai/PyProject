from app import app, db
from flask import render_template, request, flash, redirect, url_for, session, jsonify
from app.core.user_manager import UserManager
from app.core.authenticator import Authenticator
from app.core.lesson_manager import LessonManager
from app.core.lesson import Lesson # Import Lesson model for query
from app.core.note import Note # Import Note model for query
from app.core.imported_data import ImportedData # Import ImportedData model
from app.core.google_credentials import GoogleCredentials # Import GoogleCredentials model
from functools import wraps
from datetime import datetime

# For Google Classroom API
import os
import json
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

# Initialize Managers
user_manager = UserManager()
authenticator = Authenticator(user_manager)
lesson_manager = LessonManager()

# Google Classroom API Scopes - Simplified to only courses.readonly
SCOPES = [
    'https://www.googleapis.com/auth/classroom.courses.readonly',
    'https://www.googleapis.com/auth/userinfo.email',
    'https://www.googleapis.com/auth/userinfo.profile',
    'openid'
]

# Decorator for login required
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
@app.route('/index')
def index():
    if 'user_id' in session:
        user = user_manager.get_user_by_id(session['user_id'])
        if user:
            return render_template('dashboard.html', title='Dashboard', user=user)
    return render_template('index.html', title='Home')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')

        if not username or not email or not password:
            flash('Please fill out all fields.', 'danger')
            return redirect(url_for('register'))

        user = authenticator.register(username, email, password)
        if user:
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))
        else:
            flash('Username or email already exists.', 'danger')

    return render_template('register.html', title='Register')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = authenticator.login(username, password)
        if user:
            session['user_id'] = user.id
            flash('Logged in successfully!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password.', 'danger')

    return render_template('login.html', title='Login')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

# Lesson Management Routes
@app.route('/lessons')
@login_required
def list_lessons():
    user_id = session['user_id']
    lessons = lesson_manager.get_lessons_by_user(user_id)
    return render_template('lessons/list.html', title='My Lessons', lessons=lessons)

@app.route('/lessons/add', methods=['GET', 'POST'])
@login_required
def add_lesson():
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        status = request.form.get('status')
        tags = request.form.get('tags')
        user_id = session['user_id']

        if not title:
            flash('Title is required.', 'danger')
            return redirect(url_for('add_lesson'))
        
        lesson = lesson_manager.add_lesson(user_id, title, description, status, tags)
        if lesson:
            flash('Lesson added successfully!', 'success')
            return redirect(url_for('list_lessons'))
        else:
            flash('Error adding lesson.', 'danger')

    return render_template('lessons/add.html', title='Add New Lesson')

@app.route('/lessons/<lesson_id>')
@login_required
def lesson_detail(lesson_id):
    lesson = lesson_manager.get_lesson_by_id(lesson_id)
    if not lesson or lesson.user_id != session['user_id']:
        flash('Lesson not found or you do not have permission to view it.', 'danger')
        return redirect(url_for('list_lessons'))
    return render_template('lessons/detail.html', title=lesson.title, lesson=lesson)

@app.route('/lessons/<lesson_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_lesson(lesson_id):
    lesson = lesson_manager.get_lesson_by_id(lesson_id)
    if not lesson or lesson.user_id != session['user_id']:
        flash('Lesson not found or you do not have permission to edit it.', 'danger')
        return redirect(url_for('list_lessons'))

    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        status = request.form.get('status')
        tags = request.form.get('tags')

        if not title:
            flash('Title is required.', 'danger')
            return redirect(url_for('edit_lesson', lesson_id=lesson_id))

        if lesson_manager.update_lesson(lesson_id, title, description, status, tags):
            flash('Lesson updated successfully!', 'success')
            return redirect(url_for('lesson_detail', lesson_id=lesson_id))
        else:
            flash('Error updating lesson.', 'danger')

    return render_template('lessons/edit.html', title='Edit Lesson', lesson=lesson)

@app.route('/lessons/<lesson_id>/delete', methods=['POST'])
@login_required
def delete_lesson(lesson_id):
    lesson = lesson_manager.get_lesson_by_id(lesson_id)
    if not lesson or lesson.user_id != session['user_id']:
        flash('Lesson not found or you do not have permission to delete it.', 'danger')
        return redirect(url_for('list_lessons'))

    if lesson_manager.delete_lesson(lesson_id):
        flash('Lesson deleted successfully!', 'success')
    else:
        flash('Error deleting lesson.', 'danger')
    return redirect(url_for('list_lessons'))

# API Endpoint for Chrome Extension
@app.route('/api/import_data', methods=['POST'])
def import_data_from_extension():
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400

    data = request.get_json()
    platform = data.get('platform')
    imported_data_content = data.get('data')

    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"error": "User not authenticated"}), 401

    if not platform or not imported_data_content:
        return jsonify({"error": "Missing platform or data in request"}), 400

    try:
        new_imported_data = ImportedData(user_id=user_id, platform=platform, data=imported_data_content)
        db.session.add(new_imported_data)
        db.session.commit()
        return jsonify({"message": f"Data from {platform} received and saved successfully!"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to save data: {str(e)}"}), 500

@app.route('/external_data/view')
@login_required
def view_external_data():
    user_id = session['user_id']
    imported_data_list = ImportedData.query.filter_by(user_id=user_id).order_by(ImportedData.imported_at.desc()).all()

    google_classroom_data = []
    ms_teams_data = []

    for data_entry in imported_data_list:
        if data_entry.platform == 'google_classroom_api': # Changed platform name
            if 'courses' in data_entry.data:
                for course in data_entry.data['courses']:
                    google_classroom_data.append({
                        'name': course.get('name'),
                        'instructor': course.get('teacherDefinedByTeacher', course.get('ownerId')), # Adjusted for API
                        'section': course.get('section'),
                        'assignments': course.get('courseWork', []) # Use 'courseWork' from API
                    })
        elif data_entry.platform == 'ms_teams':
            if 'teams' in data_entry.data:
                for team in data_entry.data['teams']:
                    ms_teams_data.append({
                        'name': team.get('name'),
                        'channels': team.get('channels', [])
                    })

    return render_template('external_data/view.html', 
                           title='External Data', 
                           google_classroom_data=google_classroom_data,
                           ms_teams_data=ms_teams_data)

# Google Classroom API Integration Routes
@app.route('/google_classroom/authorize')
@login_required
def authorize_google_classroom():
    if not app.config.get('GOOGLE_CLIENT_ID') or not app.config.get('GOOGLE_CLIENT_SECRET'):
        flash('Google API credentials are not configured.', 'danger')
        return redirect(url_for('index'))

    flow = Flow.from_client_config(
        client_config={
            "web": {
                "client_id": app.config['GOOGLE_CLIENT_ID'],
                "client_secret": app.config['GOOGLE_CLIENT_SECRET'],
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": [url_for('oauth2callback', _external=True)] # Dynamic URL
            }
        },
        scopes=SCOPES
    )

    flow.redirect_uri = url_for('oauth2callback', _external=True)

    authorization_url, state = flow.authorization_url(
        access_type='offline',  # Request a refresh token
        include_granted_scopes='true',
        prompt='consent' # Added prompt=consent
    )

    session['oauth_state'] = state
    return redirect(authorization_url)

@app.route('/google_classroom/oauth2callback')
@login_required
def oauth2callback():
    state = session.pop('oauth_state', None)

    if not state or state != request.args.get('state'):
        flash('Invalid state parameter.', 'danger')
        return redirect(url_for('index'))

    flow = Flow.from_client_config(
        client_config={
            "web": {
                "client_id": app.config['GOOGLE_CLIENT_ID'],
                "client_secret": app.config['GOOGLE_CLIENT_SECRET'],
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": [url_for('oauth2callback', _external=True)] # Dynamic URL
            }
        },
        scopes=SCOPES,
        state=state
    )

    flow.redirect_uri = url_for('oauth2callback', _external=True)

    authorization_response = request.url
    flow.fetch_token(authorization_response=authorization_response)

    credentials = flow.credentials

    # Save credentials (especially refresh token) to the database for the current user
    user_id = session['user_id']
    print(f"DEBUG: User ID from session: {user_id}")

    google_creds = GoogleCredentials.query.filter_by(user_id=user_id).first()
    if not google_creds:
        google_creds = GoogleCredentials(user_id=user_id)
        db.session.add(google_creds)
        print(f"DEBUG: Created new GoogleCredentials entry for user {user_id}")
    
    google_creds.token = credentials.token
    # Only update refresh_token if a new one is provided
    google_creds.refresh_token = credentials.refresh_token if credentials.refresh_token else google_creds.refresh_token
    google_creds.token_uri = credentials.token_uri
    google_creds.client_id = credentials.client_id
    google_creds.client_secret = credentials.client_secret
    google_creds.scopes = ",".join(credentials.scopes)
    
    try:
        db.session.commit()
        print(f"DEBUG: GoogleCredentials saved/updated successfully for user {user_id}")
    except Exception as e:
        db.session.rollback()
        print(f"ERROR: Failed to save GoogleCredentials for user {user_id}: {e}")
        flash(f"Failed to save Google Classroom credentials: {e}", 'danger')
        return redirect(url_for('index'))

    flash('Successfully connected to Google Classroom!', 'success')
    return redirect(url_for('fetch_google_classroom_data'))

@app.route('/google_classroom/fetch_data')
@login_required
def fetch_google_classroom_data():
    user_id = session['user_id']
    google_creds = GoogleCredentials.query.filter_by(user_id=user_id).first()
    print(f"DEBUG: In fetch_google_classroom_data, google_creds is: {google_creds}")

    if not google_creds:
        flash('Please connect your Google Classroom account first.', 'danger')
        return redirect(url_for('authorize_google_classroom'))

    creds_data = {
        'token': google_creds.token,
        'refresh_token': google_creds.refresh_token,
        'token_uri': google_creds.token_uri,
        'client_id': google_creds.client_id,
        'client_secret': google_creds.client_secret,
        'scopes': google_creds.scopes.split(',')
    }
    credentials = Credentials.from_authorized_user_info(creds_data)

    # Refresh token if expired
    if not credentials.valid:
        print(f"DEBUG: Credentials not valid for user {user_id}. Attempting refresh.")
        if credentials.refresh_token:
            try:
                credentials.refresh(Request())
                # Update stored credentials in DB
                google_creds.token = credentials.token
                db.session.commit()
                print(f"DEBUG: Refreshed Google token for user {user_id}")
            except Exception as e:
                db.session.rollback()
                print(f"ERROR: Failed to refresh token for user {user_id}: {e}")
                flash('Failed to refresh Google Classroom token. Please re-authorize.', 'danger')
                return redirect(url_for('authorize_google_classroom'))
        else:
            print(f"DEBUG: No refresh token available for user {user_id}. Re-authorizing.")
            flash('Google Classroom credentials expired. Please re-authorize.', 'danger')
            return redirect(url_for('authorize_google_classroom'))

    try:
        print(f"DEBUG: Building Classroom service for user {user_id}.")
        service = build('classroom', 'v1', credentials=credentials)
        
        # Get courses
        print(f"DEBUG: Fetching courses for user {user_id}.")
        courses_results = service.courses().list(courseStates='ACTIVE').execute()
        courses = courses_results.get('courses', [])
        print(f"DEBUG: Found {len(courses)} active courses for user {user_id}.")

        # Get coursework for each course
        classroom_data = []
        for course in courses:
            course_info = {
                'id': course['id'],
                'name': course['name'],
                'section': course.get('section', ''),
                'courseWork': []
            }
            
            # Removed student submissions and coursework fetching for now
            # This part will be re-added once basic course fetching is confirmed working.

            classroom_data.append(course_info)

        # Save fetched data to ImportedData model
        print(f"DEBUG: Saving fetched data to ImportedData for user {user_id}.")
        new_imported_data = ImportedData(user_id=user_id, platform='google_classroom_api', data={'courses': classroom_data})
        db.session.add(new_imported_data)
        db.session.commit()
        print(f"DEBUG: Google Classroom data fetched and saved to ImportedData for user {user_id}.")

        flash('Google Classroom data fetched and saved successfully!', 'success')
        return redirect(url_for('view_external_data'))

    except Exception as e:
        flash(f'Error fetching Google Classroom data: {e}', 'danger')
        print(f"ERROR: Error fetching Google Classroom data for user {user_id}: {e}")
        return redirect(url_for('index'))

# Note Management Routes
from app.core.note_manager import NoteManager
note_manager = NoteManager()

@app.route('/notes')
@login_required
def list_notes():
    user_id = session['user_id']
    notes = note_manager.get_notes_by_user(user_id)
    return render_template('notes/list.html', title='My Notes', notes=notes)

@app.route('/notes/add', methods=['GET', 'POST'])
@login_required
def add_note():
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        note_date_str = request.form.get('note_date')
        user_id = session['user_id']

        if not title or not content:
            flash('Title and content are required.', 'danger')
            return redirect(url_for('add_note'))
        
        note_date = datetime.strptime(note_date_str, '%Y-%m-%d') if note_date_str else None

        note = note_manager.add_note(user_id, title, content, note_date)
        if note:
            flash('Note added successfully!', 'success')
            return redirect(url_for('list_notes'))
        else:
            flash('Error adding note.', 'danger')

    return render_template('notes/create.html', title='Create New Note')

@app.route('/notes/<note_id>')
@login_required
def view_note(note_id):
    note = note_manager.get_note_by_id(note_id)
    if not note or note.user_id != session['user_id']:
        flash('Note not found or you do not have permission to view it.', 'danger')
        return redirect(url_for('list_notes'))
    return render_template('notes/note.html', title=note.title, note=note)

@app.route('/notes/<note_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_note(note_id):
    note = note_manager.get_note_by_id(note_id)
    if not note or note.user_id != session['user_id']:
        flash('Note not found or you do not have permission to edit it.', 'danger')
        return redirect(url_for('list_notes'))

    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        note_date_str = request.form.get('note_date')
        note_date = datetime.strptime(note_date_str, '%Y-%m-%d') if note_date_str else None

        if not title or not content:
            flash('Title and content are required.', 'danger')
            return redirect(url_for('edit_note', note_id=note_id))

        if note_manager.update_note(note_id, title, content, note_date):
            flash('Note updated successfully!', 'success')
            return redirect(url_for('view_note', note_id=note_id))
        else:
            flash('Error updating note.', 'danger')

    return render_template('notes/edit.html', title='Edit Note', note=note)

@app.route('/notes/<note_id>/delete', methods=['POST'])
@login_required
def delete_note(note_id):
    note = note_manager.get_note_by_id(note_id)
    if not note or note.user_id != session['user_id']:
        flash('Note not found or you do not have permission to delete it.', 'danger')
        return redirect(url_for('list_notes'))

    if note_manager.delete_note(note_id):
        flash('Note deleted successfully!', 'success')
    else:
        flash('Error deleting note.', 'danger')
    return redirect(url_for('list_notes'))

