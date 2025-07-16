from app import app, db
from flask import render_template, request, flash, redirect, url_for, session, jsonify
from app.core.user_manager import UserManager
from app.core.authenticator import Authenticator
from app.core.lesson_manager import LessonManager
from app.core.lesson import Lesson # Import Lesson model for query
from app.core.imported_data import ImportedData # Import ImportedData model
from functools import wraps

# Initialize Managers
user_manager = UserManager()
authenticator = Authenticator(user_manager)
lesson_manager = LessonManager()

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

    # TODO: Implement actual user authentication for the API endpoint
    # For now, we'll assume a user is logged in via session for simplicity in development
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
        if data_entry.platform == 'google_classroom':
            # Assuming data_entry.data has a 'courses' key
            if 'courses' in data_entry.data:
                for course in data_entry.data['courses']:
                    google_classroom_data.append({
                        'name': course.get('name'),
                        'instructor': course.get('instructor'),
                        'section': course.get('section'),
                        'assignments': course.get('assignments', [])
                    })
        elif data_entry.platform == 'ms_teams':
            # Assuming data_entry.data has a 'teams' key
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