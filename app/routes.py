from app import app, db
from flask import render_template, request, flash, redirect, url_for, session, jsonify, make_response, g
import json
from app.core.lesson_manager import LessonManager
from app.core.lesson import Lesson, LessonSection # Import Lesson model for query
from app.core.imported_data import ImportedData # Import ImportedData model
from app.core.google_credentials import GoogleCredentials # Import GoogleCredentials model
from app.core.course_linkage_manager import CourseLinkageManager # Import CourseLinkageManager
import datetime # Import datetime
from app.core.user_manager import UserManager
from app.core.authenticator import Authenticator
from functools import wraps

# For Google Classroom API
import os
import json
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

# Initialize Managers
lesson_manager = LessonManager()
course_linkage_manager = CourseLinkageManager() # Initialize CourseLinkageManager

user_manager = UserManager()
authenticator = Authenticator(user_manager)

# Google Classroom API Scopes - MATCHING EXACTLY WHAT GOOGLE RETURNS IN THE ERROR LOG
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
    'https://www.googleapis.com/auth/drive.readonly' # New scope for Google Drive access
]

# Decorator for login required
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or g.user is None: # Added g.user is None check
            if request.accept_mimetypes['application/json']:
                return jsonify(success=False, message='Login required', redirect='login'), 401
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.before_request
def load_logged_in_user():
    user_id = session.get('user_id')
    g.user = user_manager.get_user_by_id(user_id) if user_id else None

@app.route('/')
@app.route('/index')
def index():
    return render_template('base.html')

@app.route('/partial/dashboard')
def partial_dashboard():
    return render_template('dashboard_fragment.html', user=g.user)

@app.route('/partial/note')
@login_required
def partial_note_list():
    notes = db.session.query(LessonSection).join(Lesson).filter(
        Lesson.user_id == g.user.id,
        LessonSection.type == 'note'
    ).order_by(LessonSection.created_at.desc()).all()
    return render_template('note_fragment.html', notes=notes)

@app.route('/partial/note/add', methods=['GET', 'POST'])
@login_required
def partial_note_add_standalone():
    if request.method == 'POST':
        title = request.form.get('title')
        body = request.form.get('body')
        tags = request.form.get('tags')
        status = request.form.get('status')
        external_link = request.form.get('external_link')

        if not title or not body:
            return jsonify(success=False, message='Title and body are required.')

        image_file = request.files.get('image')
        image_path = None
        if image_file and image_file.filename != '' and allowed_file(image_file.filename, 'image'):
            filename = secure_filename(image_file.filename)
            image_path = os.path.join('static', 'uploads', 'image', filename).replace('\\', '/')
            image_file.save(os.path.join(app.config['IMAGE_FOLDER'], filename))

        file_file = request.files.get('file')
        file_path = None
        if file_file and file_file.filename != '' and allowed_file(file_file.filename, 'document'):
            filename = secure_filename(file_file.filename)
            file_path = os.path.join('static', 'uploads', 'files', filename).replace('\\', '/')
            file_file.save(os.path.join(app.config['FILE_FOLDER'], filename))

        # Find or create the "General Notes" lesson
        general_notes_lesson = Lesson.query.filter_by(user_id=g.user.id, title="General Notes").first()
        if not general_notes_lesson:
            general_notes_lesson = lesson_manager.add_lesson(g.user.id, "General Notes", "A place for your general notes.")

        lesson_manager.add_section(
            lesson_id=general_notes_lesson.id,
            title=title,
            body=body,
            type='note',
            tags=tags,
            status=status,
            image_path=image_path,
            file_url=file_path,
            external_link=external_link
        )
        # After adding, redirect to the main note list to see the new note
        notes = db.session.query(LessonSection).join(Lesson).filter(
            Lesson.user_id == g.user.id,
            LessonSection.type == 'note'
        ).order_by(LessonSection.created_at.desc()).all()
        html = render_template('note_fragment.html', notes=notes)
        return jsonify(success=True, html=html)

    return render_template('notes/create.html', lesson=None)


@app.route('/partial/dev')
def partial_dev():
    user = g.user
    google_classroom_data = []
    if user:
        imported_data_gc = ImportedData.query.filter_by(user_id=user.id, platform='google_classroom_api').first()
        if imported_data_gc and 'courses' in imported_data_gc.data:
            google_classroom_data = imported_data_gc.data['courses']
    return render_template('dev_fragment.html', user=user, google_classroom_data=google_classroom_data)

# --- SPA CRUD for Class (Lesson) ---
@app.route('/partial/class')
@login_required
def partial_class():
    lessons = lesson_manager.get_lessons_by_user(g.user.id)
    
    # Fetch imported Google Classroom data for the current user
    google_classroom_imported_data = ImportedData.query.filter_by(
        user_id=g.user.id, 
        platform='google_classroom_api'
    ).first()

    classroom_courses_map = {}
    if google_classroom_imported_data and 'courses' in google_classroom_imported_data.data:
        for course_data in google_classroom_imported_data.data['courses']:
            classroom_courses_map[str(course_data.get('id'))] = course_data

    for lesson in lessons:
        if lesson.source_platform == 'google_classroom' and lesson.google_classroom_id:
            course_id_str = str(lesson.google_classroom_id)
            if course_id_str in classroom_courses_map:
                classroom_course = classroom_courses_map[course_id_str]
                
                # Set author_name to Roster teacher
                if 'teachers' in classroom_course and classroom_course['teachers']:
                    # Assuming the first teacher in the roster is the primary one
                    first_teacher = classroom_course['teachers'][0]
                    if 'profile' in first_teacher and 'name' in first_teacher['profile']:
                        lesson.author_name = first_teacher['profile']['name'].get('fullName', 'Classroom Teacher')
                else:
                    lesson.author_name = 'Classroom Teacher' # Fallback if no teachers found

                # Set classroom_assignments_count
                if 'courseWork' in classroom_course:
                    lesson.classroom_assignments_count = len(classroom_course['courseWork'])
                else:
                    lesson.classroom_assignments_count = 0
                
                # Add 'Google Classroom' tag if not already present
                current_tags = lesson.tags.split(',') if lesson.tags else []
                if 'Google Classroom' not in current_tags:
                    current_tags.append('Google Classroom')
                lesson.tags = ', '.join(current_tags)
            else:
                # If linked to GC but course data not found, set defaults
                lesson.author_name = 'Classroom Teacher (Data Missing)'
                lesson.classroom_assignments_count = 0
                current_tags = lesson.tags.split(',') if lesson.tags else []
                if 'Google Classroom' not in current_tags:
                    current_tags.append('Google Classroom')
                lesson.tags = ', '.join(current_tags)
        else:
            # For lessons not from Google Classroom
            lesson.classroom_assignments_count = 0 # Ensure it's 0 for non-GC lessons
            if not hasattr(lesson, 'author_name') or not lesson.author_name:
                lesson.author_name = 'Your Lesson' # Default author for non-GC lessons

    return render_template('class_fragment.html', lessons=lessons)

@app.route('/partial/class/add', methods=['GET', 'POST'])
@login_required
def partial_class_add():
    message = None
    success = False
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        status = request.form.get('status')
        tags = request.form.get('tags')
        author_name = request.form.get('author_name') # Get author_name from form
        if not title:
            message = 'Title is required.'
        else:
            lesson = lesson_manager.add_lesson(g.user.id, title, description, status, tags, author_name=author_name) # Pass author_name
            if lesson:
                return jsonify(success=True, redirect='class')
            else:
                message = 'Error adding lesson.'
        return jsonify(success=False, message=message)
    return render_template('lessons/_add.html')

@app.route('/partial/class/<lesson_id>')
@login_required
def partial_class_detail(lesson_id):
    lesson = lesson_manager.get_lesson_by_id(lesson_id)
    if not lesson or lesson.user_id != g.user.id:
        return '<div class="alert alert-danger">Lesson not found or no permission.</div>'
    # แปลงข้อมูล Google Classroom
    if lesson.source_platform == 'google_classroom':
        import json
        try:
            lesson.announcements = json.loads(lesson.announcements_data) if lesson.announcements_data else []
        except Exception:
            lesson.announcements = []
        try:
            lesson.grouped_by_topic = json.loads(lesson.topics_data) if lesson.topics_data else []
        except Exception:
            lesson.grouped_by_topic = []
        try:
            lesson.roster = json.loads(lesson.roster_data) if lesson.roster_data else {}
        except Exception:
            lesson.roster = {}
        try:
            lesson.all_attachments = json.loads(lesson.attachments_data) if lesson.attachments_data else []
        except Exception:
            lesson.all_attachments = []
    # โหลด sections จาก db
    sections = lesson_manager.get_sections(lesson.id)
    return render_template('lessons/_detail.html', lesson=lesson, sections=sections)

@app.route('/partial/class/<lesson_id>/edit', methods=['GET', 'POST'])
@login_required
def partial_class_edit(lesson_id):
    lesson = lesson_manager.get_lesson_by_id(lesson_id)
    if not lesson or lesson.user_id != g.user.id:
        return '<div class="alert alert-danger">Lesson not found or no permission.</div>'
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        status = request.form.get('status')
        tags = request.form.get('tags')
        if not title:
            return jsonify(success=False, message='Title is required.')
        lesson_manager.update_lesson(lesson_id, title, description, status, tags)
        return jsonify(success=True, redirect=f'class/{lesson_id}')
    return render_template('lessons/_edit.html', lesson=lesson)

@app.route('/partial/class/<lesson_id>/delete', methods=['POST'])
@login_required
def partial_class_delete(lesson_id):
    lesson = lesson_manager.get_lesson_by_id(lesson_id)
    if not lesson or lesson.user_id != g.user.id:
        return jsonify(success=False, message='Lesson not found or no permission.')
    lesson_manager.delete_lesson(lesson_id)
    return jsonify(success=True, redirect='class')

# --- SPA CRUD for LessonSection (Section/Content) ---
@app.route('/partial/class/<lesson_id>/sections')
@login_required
def partial_section_list(lesson_id):
    lesson = lesson_manager.get_lesson_by_id(lesson_id)
    if not lesson or lesson.user_id != g.user.id:
        return '<div class="alert alert-danger">Lesson not found or no permission.</div>'
    sections = lesson_manager.get_sections(lesson_id)
    return render_template('lessons/section_list.html', lesson=lesson, sections=sections)

import os
from werkzeug.utils import secure_filename
UPLOAD_FOLDER = '/Users/kbbk/PyProject-3/app/static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/partial/class/<lesson_id>/sections/add', methods=['GET', 'POST'])
@login_required
def partial_section_add(lesson_id):
    lesson = lesson_manager.get_lesson_by_id(lesson_id)
    if not lesson or lesson.user_id != g.user.id:
        return '<div class="alert alert-danger">Lesson not found or no permission.</div>'
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        type_ = request.form.get('type')
        assignment_due = request.form.get('assignment_due')
        # Convert assignment_due to datetime or None
        if assignment_due:
            assignment_due = assignment_due.strip()
            if assignment_due == '':
                assignment_due = None
            else:
                try:
                    assignment_due = datetime.datetime.strptime(assignment_due, '%Y-%m-%dT%H:%M')
                except Exception:
                    assignment_due = None
        file_url = None
        file_urls = [] # Initialize file_urls list
        # handle multiple file upload
        if type_ == 'file' and 'files' in request.files:
            files = request.files.getlist('files')
            for file in files:
                print('DEBUG: file in request.files:', file, file.filename)
                if file and file.filename:
                    filename = secure_filename(file.filename)
                    save_path = os.path.join(UPLOAD_FOLDER, filename)
                    print('DEBUG: saving to', save_path)
                    file.save(save_path)
                    print('DEBUG: file saved?', os.path.exists(save_path))
                    url = '/static/uploads/' + filename
                    file_urls.append(url)
            if file_urls:
                file_url = file_urls[0] # legacy, for UI เดิม
        import json
        if not title:
            return jsonify(success=False, message='Title is required.')
        section = lesson_manager.add_section(lesson_id, title, content, type_, file_url, assignment_due, file_urls=json.dumps(file_urls) if file_urls else None)
        # Return updated section list as HTML fragment
        sections = lesson_manager.get_sections(lesson_id)
        html = render_template('lessons/section_list.html', lesson=lesson, sections=sections)
        return jsonify(success=True, html=html)
    return render_template('lessons/section_add.html', lesson=lesson)

@app.route('/partial/class/<lesson_id>/sections/<section_id>/edit', methods=['GET', 'POST'])
@login_required
def partial_section_edit(lesson_id, section_id):
    lesson = lesson_manager.get_lesson_by_id(lesson_id)
    section = lesson_manager.get_section_by_id(section_id)
    if not lesson or lesson.user_id != g.user.id or not section or section.lesson_id != lesson_id:
        return '<div class="alert alert-danger">Section not found or no permission.</div>'
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        type_ = request.form.get('type')
        assignment_due = request.form.get('assignment_due')
        file_url = section.file_url
        file_urls = [] # Initialize file_urls list
        # handle multiple file upload
        if type_ == 'file' and 'files' in request.files:
            files = request.files.getlist('files')
            for file in files:
                print('DEBUG: file in request.files:', file, file.filename)
                if file and file.filename:
                    filename = secure_filename(file.filename)
                    save_path = os.path.join(UPLOAD_FOLDER, filename)
                    print('DEBUG: saving to', save_path)
                    file.save(save_path)
                    print('DEBUG: file saved?', os.path.exists(save_path))
                    url = '/static/uploads/' + filename
                    file_urls.append(url)
            if file_urls:
                file_url = file_urls[0] # legacy, for UI เดิม
        # Convert assignment_due to datetime or None
        if assignment_due:
            assignment_due = assignment_due.strip()
            if assignment_due == '':
                assignment_due = None
            else:
                try:
                    assignment_due = datetime.datetime.strptime(assignment_due, '%Y-%m-%dT%H:%M')
                except Exception:
                    assignment_due = None
        import json
        lesson_manager.update_section(section_id, title, content, type_, file_url, assignment_due, file_urls=json.dumps(file_urls) if file_urls else None)
        # Return updated section list as HTML fragment
        sections = lesson_manager.get_sections(lesson_id)
        html = render_template('lessons/section_list.html', lesson=lesson, sections=sections)
        return jsonify(success=True, html=html)
    return render_template('lessons/section_edit.html', lesson=lesson, section=section)

@app.route('/partial/class/<lesson_id>/sections/<section_id>/delete', methods=['POST'])
@login_required
def partial_section_delete(lesson_id, section_id):
    lesson = lesson_manager.get_lesson_by_id(lesson_id)
    section = lesson_manager.get_section_by_id(section_id)
    if not lesson or lesson.user_id != g.user.id or not section or section.lesson_id != lesson_id:
        return jsonify(success=False, message='Section not found or no permission.')
    lesson_manager.delete_section(section_id)
    # Return updated section list as HTML fragment
    sections = lesson_manager.get_sections(lesson_id)
    html = render_template('lessons/section_list.html', lesson=lesson, sections=sections)
    return jsonify(success=True, html=html)

# === Start of note management routes ===

# กำหนดโฟลเดอร์สำหรับเก็บไฟล์ที่อัพโหลด
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'uploads')
IMAGE_FOLDER = os.path.join(UPLOAD_FOLDER, 'image')  # โฟลเดอร์สำหรับรูปภาพ
FILE_FOLDER = os.path.join(UPLOAD_FOLDER, 'files')   # โฟลเดอร์สำหรับไฟล์เอกสาร

# สร้างโฟลเดอร์ถ้ายังไม่มี
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# สร้างโฟลเดอร์ image ถ้ายังไม่มี
if not os.path.exists(IMAGE_FOLDER):
    os.makedirs(IMAGE_FOLDER)

# สร้างโฟลเดอร์ files ถ้ายังไม่มี
if not os.path.exists(FILE_FOLDER):
    os.makedirs(FILE_FOLDER)

# กำหนดค่า config ให้ app
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['IMAGE_FOLDER'] = IMAGE_FOLDER
app.config['FILE_FOLDER'] = FILE_FOLDER

# กำหนดประเภทไฟล์ที่อนุญาตให้อัพโหลด
ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
ALLOWED_FILE_EXTENSIONS = {'pdf', 'doc', 'docx', 'txt', 'xlsx', 'xlsm', 'xls', 'ppt', 'pptx', 'pptm'}
ALLOWED_EXTENSIONS = ALLOWED_IMAGE_EXTENSIONS | ALLOWED_FILE_EXTENSIONS

def allowed_file(filename, file_type='all'):
    """
    เช็คว่าไฟล์มี extension และอยู่ในรายการที่อนุญาตหรือเปล่า
    file_type: 'image', 'document', 'all'
    """
    if '.' not in filename:
        return False
    
    extension = filename.rsplit('.', 1)[1].lower()
    
    if file_type == 'image':
        return extension in ALLOWED_IMAGE_EXTENSIONS
    elif file_type == 'document':
        return extension in ALLOWED_FILE_EXTENSIONS
    else:  # 'all'
        return extension in ALLOWED_EXTENSIONS

# Note Management Routes is now part of LessonSection
@app.route('/partial/class/<lesson_id>/notes/add', methods=['GET', 'POST'])
@login_required
def partial_note_add(lesson_id):
    lesson = lesson_manager.get_lesson_by_id(lesson_id)
    if not lesson or lesson.user_id != g.user.id:
        return '<div class="alert alert-danger">Lesson not found or no permission.</div>'
    if request.method == 'POST':
        title = request.form.get('title')
        body = request.form.get('body')
        tags = request.form.get('tags')
        status = request.form.get('status')
        external_link = request.form.get('external_link')
        
        image_file = request.files.get('image')
        image_path = None
        if image_file and image_file.filename != '' and allowed_file(image_file.filename, 'image'):
            filename = secure_filename(image_file.filename)
            image_path = os.path.join('static', 'uploads', 'image', filename).replace('\\', '/')
            image_file.save(os.path.join(app.config['IMAGE_FOLDER'], filename))

        file_file = request.files.get('file')
        file_path = None
        if file_file and file_file.filename != '' and allowed_file(file_file.filename, 'document'):
            filename = secure_filename(file_file.filename)
            file_path = os.path.join('static', 'uploads', 'files', filename).replace('\\', '/')
            file_file.save(os.path.join(app.config['FILE_FOLDER'], filename))

        if not title or not body:
            return jsonify(success=False, message='Title and body are required.')

        section = lesson_manager.add_section(
            lesson_id=lesson_id,
            title=title,
            body=body,
            type='note',
            tags=tags,
            status=status,
            image_path=image_path,
            file_url=file_path,
            external_link=external_link
        )
        sections = lesson_manager.get_sections(lesson_id)
        html = render_template('lessons/section_list.html', lesson=lesson, sections=sections)
        return jsonify(success=True, html=html)
    return render_template('notes/create.html', lesson=lesson)

@app.route('/partial/class/<lesson_id>/notes/<section_id>/edit', methods=['GET', 'POST'])
@login_required
def partial_note_edit(lesson_id, section_id):
    lesson = lesson_manager.get_lesson_by_id(lesson_id)
    section = lesson_manager.get_section_by_id(section_id)
    if not lesson or lesson.user_id != g.user.id or not section or section.lesson_id != lesson_id:
        return '<div class="alert alert-danger">Note not found or no permission.</div>'

    if request.method == 'POST':
        title = request.form.get('title')
        body = request.form.get('body')
        tags = request.form.get('tags')
        status = request.form.get('status')
        external_link = request.form.get('external_link')

        image_path = section.image_path
        if request.form.get('remove_image'):
            if section.image_path:
                old_image_filename = os.path.basename(section.image_path)
                old_image_path = os.path.join(app.config['IMAGE_FOLDER'], old_image_filename)
                if os.path.exists(old_image_path):
                    os.remove(old_image_path)
                image_path = None
        elif 'image' in request.files and request.files['image'].filename != '':
            image_file = request.files['image']
            if allowed_file(image_file.filename, 'image'):
                if section.image_path:
                    old_image_filename = os.path.basename(section.image_path)
                    old_image_path = os.path.join(app.config['IMAGE_FOLDER'], old_image_filename)
                    if os.path.exists(old_image_path):
                        os.remove(old_image_path)
                filename = secure_filename(image_file.filename)
                image_path = os.path.join('static', 'uploads', 'image', filename).replace('\\', '/')
                image_file.save(os.path.join(app.config['IMAGE_FOLDER'], filename))

        file_path = section.file_url
        if request.form.get('remove_file'):
            if section.file_url:
                old_file_filename = os.path.basename(section.file_url)
                old_file_path = os.path.join(app.config['FILE_FOLDER'], old_file_filename)
                if os.path.exists(old_file_path):
                    os.remove(old_file_path)
                file_path = None
        elif 'file' in request.files and request.files['file'].filename != '':
            file_file = request.files['file']
            if allowed_file(file_file.filename, 'document'):
                if section.file_url:
                    old_file_filename = os.path.basename(section.file_url)
                    old_file_path = os.path.join(app.config['FILE_FOLDER'], old_file_filename)
                    if os.path.exists(old_file_path):
                        os.remove(old_file_path)
                filename = secure_filename(file_file.filename)
                file_path = os.path.join('static', 'uploads', 'files', filename).replace('\\', '/')
                file_file.save(os.path.join(app.config['FILE_FOLDER'], filename))

        lesson_manager.update_section(
            section_id=section_id,
            title=title,
            body=body,
            tags=tags,
            status=status,
            image_path=image_path,
            file_url=file_path,
            external_link=external_link
        )
        sections = lesson_manager.get_sections(lesson_id)
        html = render_template('lessons/section_list.html', lesson=lesson, sections=sections)
        return jsonify(success=True, html=html)
    return render_template('notes/edit.html', lesson=lesson, note=section)

# === End of note management routes ===

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = authenticator.login(username, password)
        if user:
            session['user_id'] = user.id
            return redirect(url_for('dashboard'))
        else:
            return render_template('login_fragment.html', success=False, message='Invalid username or password.')
    return render_template('login_fragment.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        if not username or not email or not password:
            return render_template('register_fragment.html', success=False, message='Please fill out all fields.')
        user = authenticator.register(username, email, password)
        if user:
            return render_template('register_fragment.html', success=True, message='Registration successful! Please log in.')
        else:
            return render_template('register_fragment.html', success=False, message='Username or email already exists.')
    return render_template('register_fragment.html')

@app.route('/partial/login', methods=['GET', 'POST'])
def partial_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = authenticator.login(username, password)
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.accept_mimetypes['application/json']
        if user:
            session['user_id'] = user.id
            if is_ajax:
                return jsonify(success=True, message='Logged in successfully!', redirect='dashboard')
            else:
                return render_template('login_fragment.html', success=True, message='Logged in successfully!')
        else:
            if is_ajax:
                return jsonify(success=False, message='Invalid username or password.')
            else:
                return render_template('login_fragment.html', success=False, message='Invalid username or password.')
    return render_template('login_fragment.html')

@app.route('/partial/register', methods=['GET', 'POST'])
def partial_register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.accept_mimetypes['application/json']
        if not username or not email or not password:
            if is_ajax:
                return jsonify(success=False, message='Please fill out all fields.')
            else:
                return render_template('register_fragment.html', success=False, message='Please fill out all fields.')
        user = authenticator.register(username, email, password)
        if user:
            if is_ajax:
                return jsonify(success=True, message='Registration successful! Please log in.', redirect='login')
            else:
                return render_template('register_fragment.html', success=True, message='Registration successful! Please log in.')
        else:
            if is_ajax:
                return jsonify(success=False, message='Username or email already exists.')
            else:
                return render_template('register_fragment.html', success=False, message='Username or email already exists.')
    return render_template('register_fragment.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

# Lesson Management Routes
@app.route('/lessons')
def list_lessons():
    user_id = session['user_id']
    lessons = lesson_manager.get_lessons_by_user(user_id)
    return render_template('lessons/list.html', title='My Lessons', lessons=lessons)

@app.route('/lessons/add', methods=['GET', 'POST'])
def add_lesson():
    is_htmx = 'HX-Request' in request.headers

    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        status = request.form.get('status')
        tags = request.form.get('tags')
        user_id = session['user_id']

        if not title:
            if is_htmx:
                response = make_response(render_template('lessons/_add.html', title='Add New Lesson'))
                response.headers['HX-Trigger'] = json.dumps({
                    'showMessage': {'message': 'Title is required.', 'category': 'danger'}
                })
                return response, 400 # Bad Request
            flash('Title is required.', 'danger')
            return redirect(url_for('add_lesson'))
        
        lesson = lesson_manager.add_lesson(user_id, title, description, status, tags)
        if lesson:
            if is_htmx:
                # Render the new lesson card and send it back
                response = make_response(render_template('lessons/_lesson_card.html', lesson=lesson))
                response.headers['HX-Trigger'] = json.dumps({
                    'showMessage': {'message': 'Lesson added successfully!', 'category': 'success'},
                    'lessonAdded': {
                        'lesson_id': lesson.id,
                        'lesson_title': lesson.title,
                        'lesson_status': lesson.status,
                        'lesson_tags': lesson.tags
                    }
                })
                return response
            flash('Lesson added successfully!', 'success')
            return redirect(url_for('list_lessons'))
        else:
            if is_htmx:
                response = make_response(render_template('lessons/_add.html', title='Add New Lesson'))
                response.headers['HX-Trigger'] = json.dumps({
                    'showMessage': {'message': 'Error adding lesson.', 'category': 'danger'}
                })
                return response, 500 # Internal Server Error
            flash('Error adding lesson.', 'danger')

    if is_htmx:
        return render_template('lessons/_add.html', title='Add New Lesson')
    return render_template('lessons/add.html', title='Add New Lesson')

@app.route('/lessons/<lesson_id>')
def lesson_detail(lesson_id):
    lesson = lesson_manager.get_lesson_by_id(lesson_id)
    is_htmx = 'HX-Request' in request.headers

    if not lesson or lesson.user_id != session['user_id']:
        if is_htmx:
            response = make_response('')
            response.headers['HX-Trigger'] = json.dumps({
                'showMessage': {'message': 'Lesson not found or you do not have permission to view it.', 'category': 'danger'}
            })
            return response, 404
        flash('Lesson not found or you do not have permission to view it.', 'danger')
        return redirect(url_for('list_lessons'))

    # If the lesson is from Google Classroom, parse the JSON data
    if lesson.source_platform == 'google_classroom':
        try:
            if lesson.announcements_data:
                lesson.announcements = json.loads(lesson.announcements_data)
            if lesson.topics_data:
                lesson.grouped_by_topic = json.loads(lesson.topics_data)
            if lesson.roster_data:
                lesson.roster = json.loads(lesson.roster_data)
            if lesson.attachments_data:
                lesson.all_attachments = json.loads(lesson.attachments_data)
            
            # Fetch drive_files from ImportedData if this is a Google Classroom lesson
            if lesson.google_classroom_id:
                imported_data_gc = ImportedData.query.filter_by(user_id=session['user_id'], platform='google_classroom_api').first()
                if imported_data_gc and 'courses' in imported_data_gc.data:
                    for course_data in imported_data_gc.data['courses']:
                        if str(course_data.get('id')) == str(lesson.google_classroom_id):
                            lesson.drive_files = course_data.get('drive_files', [])
                            break

        except json.JSONDecodeError as e:
            if is_htmx:
                response = make_response('')
                response.headers['HX-Trigger'] = json.dumps({
                    'showMessage': {'message': f"Error parsing Google Classroom data for this lesson: {e}", 'category': 'danger'}
                })
                return response, 500
            flash(f"Error parsing Google Classroom data for this lesson: {e}", 'danger')
            # Handle error, maybe set these fields to empty lists/dicts
            lesson.announcements = []
            lesson.grouped_by_topic = []
            lesson.roster = {}
            lesson.all_attachments = []
            lesson.drive_files = [] # Initialize drive_files as empty list on error

    if is_htmx:
        return render_template('lessons/_detail.html', title=lesson.title, lesson=lesson)
    return render_template('lessons/detail.html', title=lesson.title, lesson=lesson)

@app.route('/lessons/<lesson_id>/edit', methods=['GET', 'POST'])
def edit_lesson(lesson_id):
    lesson = lesson_manager.get_lesson_by_id(lesson_id)
    is_htmx = 'HX-Request' in request.headers

    if not lesson or lesson.user_id != session['user_id']:
        if is_htmx:
            response = make_response('')
            response.headers['HX-Trigger'] = json.dumps({
                'showMessage': {'message': 'Lesson not found or you do not have permission to edit it.', 'category': 'danger'}
            })
            return response, 404
        flash('Lesson not found or you do not have permission to edit it.', 'danger')
        return redirect(url_for('list_lessons'))

    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        status = request.form.get('status')
        tags = request.form.get('tags')

        if not title:
            if is_htmx:
                response = make_response(render_template('lessons/_edit.html', title='Edit Lesson', lesson=lesson))
                response.headers['HX-Trigger'] = json.dumps({
                    'showMessage': {'message': 'Title is required.', 'category': 'danger'}
                })
                return response, 400
            flash('Title is required.', 'danger')
            return redirect(url_for('edit_lesson', lesson_id=lesson_id))

        if lesson_manager.update_lesson(lesson_id, title, description, status, tags):
            if is_htmx:
                # Render the updated lesson card and send it back
                updated_lesson = lesson_manager.get_lesson_by_id(lesson_id) # Fetch updated lesson object
                response = make_response(render_template('lessons/_lesson_card.html', lesson=updated_lesson))
                response.headers['HX-Trigger'] = json.dumps({
                    'showMessage': {'message': 'Lesson updated successfully!', 'category': 'success'},
                    'lessonUpdated': {
                        'lesson_id': updated_lesson.id,
                        'lesson_title': updated_lesson.title,
                        'lesson_status': updated_lesson.status,
                        'lesson_tags': updated_lesson.tags
                    }
                })
                return response
            flash('Lesson updated successfully!', 'success')
            return redirect(url_for('lesson_detail', lesson_id=lesson_id))
        else:
            if is_htmx:
                response = make_response(render_template('lessons/_edit.html', title='Edit Lesson', lesson=lesson))
                response.headers['HX-Trigger'] = json.dumps({
                    'showMessage': {'message': 'Error updating lesson.', 'category': 'danger'}
                })
                return response, 500
            flash('Error updating lesson.', 'danger')

    if is_htmx:
        return render_template('lessons/_edit.html', title='Edit Lesson', lesson=lesson)
    return render_template('lessons/edit.html', title='Edit Lesson', lesson=lesson)

@app.route('/lessons/<lesson_id>/delete', methods=['POST'])
def delete_lesson(lesson_id):
    lesson = lesson_manager.get_lesson_by_id(lesson_id)
    is_htmx = 'HX-Request' in request.headers

    if not lesson or lesson.user_id != session['user_id']:
        if is_htmx:
            response = make_response('')
            response.headers['HX-Trigger'] = json.dumps({
                'showMessage': {'message': 'Lesson not found or you do not have permission to delete it.', 'category': 'danger'}
            })
            return response, 404
        flash('Lesson not found or you do not have permission to delete it.', 'danger')
        return redirect(url_for('list_lessons'))

    if lesson_manager.delete_lesson(lesson_id):
        if is_htmx:
            response = make_response('') # No content needed, HTMX will remove the element
            response.headers['HX-Trigger'] = json.dumps({
                'showMessage': {'message': 'Lesson deleted successfully!', 'category': 'success'}
            })
            return response
        flash('Lesson deleted successfully!', 'success')
    else:
        if is_htmx:
            response = make_response('')
            response.headers['HX-Trigger'] = json.dumps({
                'showMessage': {'message': 'Error deleting lesson.', 'category': 'danger'}
            })
            return response, 500
        flash('Error deleting lesson.', 'danger')
    
    if not is_htmx:
        return redirect(url_for('list_lessons'))
    return make_response('') # Fallback for HTMX if no specific error, though HX-Trigger should handle it

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
def view_external_data():
    user_id = session['user_id']
    imported_data_list = ImportedData.query.filter_by(user_id=user_id).order_by(ImportedData.imported_at.desc()).all()

    google_classroom_data = []
    ms_teams_data = []
    kmitl_studytable_data = []

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
        elif data_entry.platform == 'kmitl_studytable':
            kmitl_studytable_data.append(data_entry.data)

    return render_template('external_data/view.html', 
                           title='External Data', 
                           google_classroom_data=google_classroom_data,
                           ms_teams_data=ms_teams_data,
                           kmitl_studytable_data=kmitl_studytable_data)

# Google Classroom API Integration Routes
@app.route('/google_classroom/authorize')
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
        prompt='consent' # Force consent screen to ensure new scopes are requested
    )

    session['oauth_state'] = state
    return redirect(authorization_url)

@app.route('/google_classroom/oauth2callback')
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
        fetched_courses = courses_results.get('courses', [])
        print(f"DEBUG: Found {len(fetched_courses)} active courses for user {user_id}.")

        # Retrieve existing imported data for this user and platform
        existing_imported_data = ImportedData.query.filter_by(user_id=user_id, platform='google_classroom_api').first()
        if existing_imported_data:
            existing_courses_data = existing_imported_data.data.get('courses', [])
        else:
            existing_courses_data = []
            existing_imported_data = ImportedData(user_id=user_id, platform='google_classroom_api', data={'courses': []})
            db.session.add(existing_imported_data)

        # Create a map of existing courses by ID for efficient lookup
        existing_courses_map = {course['id']: course for course in existing_courses_data}
        updated_courses_list = []

        # Process fetched courses (upsert logic)
        for course in fetched_courses:
            course_id = course['id']
            course_info = existing_courses_map.get(course_id, {'id': course_id, 'name': course['name'], 'section': course.get('section', '')})
            
            # Update basic course info (name, section) in case it changed
            course_info['name'] = course['name']
            course_info['section'] = course.get('section', '')
            course_info['alternateLink'] = course.get('alternateLink', '') # Ensure alternateLink is stored
            course_info['all_attachments'] = [] # Initialize list for all attachments

            # Fetch announcements (Stream)
            try:
                print(f"DEBUG: Fetching announcements for course: {course['name']} ({course['id']})")
                announcements_results = service.courses().announcements().list(courseId=course['id']).execute()
                announcements = announcements_results.get('announcements', [])
                course_info['announcements'] = announcements
                print(f"DEBUG: Found {len(announcements)} announcements for this course.")
                for ann in announcements:
                    if 'materials' in ann:
                        for mat in ann['materials']:
                            course_info['all_attachments'].append({'source': 'announcement', 'item_id': ann['id'], 'material': mat})
            except Exception as e:
                print(f"ERROR: Could not fetch announcements for course {course['id']}: {e}")

            # Fetch coursework (ClassWork)
            try:
                print(f"DEBUG: Fetching coursework for course: {course['name']} ({course['id']})")
                coursework_results = service.courses().courseWork().list(courseId=course['id']).execute()
                coursework = coursework_results.get('courseWork', [])
                course_info['courseWork'] = coursework
                print(f"DEBUG: Found {len(coursework)} coursework items for this course.")
                for cw in coursework:
                    if 'materials' in cw:
                        for mat in cw['materials']:
                            course_info['all_attachments'].append({'source': 'coursework', 'item_id': cw['id'], 'material': mat})
            except Exception as e:
                print(f"ERROR: Could not fetch coursework for course {course['id']}: {e}")

            # Fetch courseWorkMaterials (Materials)
            try:
                print(f"DEBUG: Fetching materials for course: {course['name']} ({course['id']})")
                materials_results = service.courses().courseWorkMaterials().list(courseId=course['id']).execute()
                materials = materials_results.get('courseWorkMaterials', [])
                course_info['materials'] = materials
                print(f"DEBUG: Found {len(materials)} materials for this course.")
                for mat_item in materials:
                    if 'materials' in mat_item:
                        for mat in mat_item['materials']:
                            course_info['all_attachments'].append({'source': 'material', 'item_id': mat_item['id'], 'material': mat})
            except Exception as e:
                print(f"ERROR: Could not fetch materials for course {course['id']}: {e}")

            # Fetch topics
            try:
                print(f"DEBUG: Fetching topics for course: {course['name']} ({course['id']})")
                topics_results = service.courses().topics().list(courseId=course['id']).execute()
                course_info['topics'] = topics_results.get('topic', []) # Note: API returns 'topic' not 'topics'
                print(f"DEBUG: Found {len(course_info['topics'])} topics for this course.")
            except Exception as e:
                print(f"ERROR: Could not fetch topics for course {course['id']}: {e}")

            # Group coursework and materials by topic
            grouped_by_topic = {"untopiced": {"name": "Unthemed", "courseWork": [], "materials": []}}
            for topic in course_info['topics']:
                grouped_by_topic[topic['topicId']] = {"name": topic['name'], "courseWork": [], "materials": []}
            
            for work in course_info['courseWork']:
                topic_id = work.get('topicId', 'untopiced')
                if topic_id in grouped_by_topic:
                    grouped_by_topic[topic_id]['courseWork'].append(work)
                else:
                    # Fallback for any unexpected topicId
                    grouped_by_topic['untopiced']['courseWork'].append(work)

            for material in course_info['materials']:
                topic_id = material.get('topicId', 'untopiced')
                if topic_id in grouped_by_topic:
                    grouped_by_topic[topic_id]['materials'].append(material)
                else:
                    # Fallback for any unexpected topicId
                    grouped_by_topic['untopiced']['materials'].append(material)

            # Replace original lists with grouped data
            course_info['grouped_by_topic'] = list(grouped_by_topic.values())
            print(f"DEBUG: Grouped data for course {course['id']}: {course_info['grouped_by_topic']}") # Added debug print
            # Clear original lists as they are now grouped
            course_info['courseWork'] = []
            course_info['materials'] = []

            # Fetch students (roster)
            try:
                print(f"DEBUG: Fetching students for course: {course['name']} ({course['id']})")
                students_results = service.courses().students().list(courseId=course['id']).execute()
                course_info['students'] = students_results.get('students', [])
                print(f"DEBUG: Found {len(course_info['students'])} students for this course.")
            except Exception as e:
                print(f"ERROR: Could not fetch students for course {course['id']}: {e}")

            # Fetch teachers (roster)
            try:
                print(f"DEBUG: Fetching teachers for course: {course['name']} ({course['id']})")
                teachers_results = service.courses().teachers().list(courseId=course['id']).execute()
                course_info['teachers'] = teachers_results.get('teachers', [])
                print(f"DEBUG: Found {len(course_info['teachers'])} teachers for this course.")
            except Exception as e:
                print(f"ERROR: Could not fetch teachers for course {course['id']}: {e}")

            # Fetch files from user's Google Drive 'Classroom' folder and subfolders for each course
            course_info['drive_files'] = [] # Initialize list for drive files specific to this course
            try:
                print(f"DEBUG: Fetching files from Google Drive for course: {course['name']} ({course['id']})")
                drive_service = build('drive', 'v3', credentials=credentials)
                
                # Search for the main 'Classroom' folder
                classroom_folder_id = None
                results = drive_service.files().list(
                    q="name='Classroom' and mimeType='application/vnd.google-apps.folder' and trashed=false",
                    spaces='drive',
                    fields='files(id, name)'
                ).execute()
                items = results.get('files', [])
                if items:
                    classroom_folder_id = items[0]['id']
                    print(f"DEBUG: Found main 'Classroom' folder with ID: {classroom_folder_id}")

                    # Search for the course-specific subfolder within 'Classroom' folder
                    course_folder_id = None
                    course_folder_name = course['name'] # Use course name as folder name
                    subfolder_results = drive_service.files().list(
                        q=f"'{classroom_folder_id}' in parents and name contains '{course_folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false",
                        spaces='drive',
                        fields='files(id, name)'
                    ).execute()
                    subfolder_items = subfolder_results.get('files', [])
                    if subfolder_items:
                        course_folder_id = subfolder_items[0]['id']
                        print(f"DEBUG: Found course folder '{course_folder_name}' with ID: {course_folder_id}")

                        # List files within the course-specific folder
                        files_in_course_folder = []
                        page_token = None
                        while True:
                            response = drive_service.files().list(
                                q=f"'{course_folder_id}' in parents and trashed=false",
                                spaces='drive',
                                fields='nextPageToken, files(id, name, mimeType, webViewLink)',
                                pageToken=page_token
                            ).execute()
                            for file_item in response.get('files', []):
                                if file_item['mimeType'] != 'application/vnd.google-apps.folder':
                                    files_in_course_folder.append({
                                        'type': 'driveFile',
                                        'title': file_item['name'],
                                        'alternateLink': file_item['webViewLink'],
                                        'mimeType': file_item['mimeType']
                                    })
                            page_token = response.get('nextPageToken', None)
                            if not page_token:
                                break
                        
                        print(f"DEBUG: Found {len(files_in_course_folder)} files in course folder '{course_folder_name}'.")
                        course_info['drive_files'] = files_in_course_folder
                    else:
                        print(f"DEBUG: Course folder '{course_folder_name}' not found in main 'Classroom' folder.")
                else:
                    print(f"DEBUG: Main 'Classroom' folder not found in Google Drive for user {user_id}.")
            except Exception as e:
                print(f"ERROR: Could not fetch files from Google Drive for course {course['id']}: {e}")

            updated_courses_list.append(course_info)

        # Update the ImportedData entry with the new list of courses
        existing_imported_data.data['courses'] = updated_courses_list
        existing_imported_data.imported_at = datetime.datetime.utcnow() # Update timestamp
        db.session.commit()
        print(f"DEBUG: Google Classroom data fetched and saved/updated successfully for user {user_id}.")

        flash('Google Classroom data fetched and saved successfully!', 'success')
        return redirect(url_for('view_external_data'))

    except Exception as e:
        db.session.rollback()
        flash(f'Error fetching Google Classroom data: {e}', 'danger')
        print(f"ERROR: Error fetching Google Classroom data for user {user_id}: {e}")
        return redirect(url_for('index'))

# Google Classroom Course Details and Edit Routes
@app.route('/classroom/course/<course_id>')
def course_detail(course_id):
    user_id = session['user_id']
    imported_data = ImportedData.query.filter_by(user_id=user_id, platform='google_classroom_api').first()
    
    course_to_display = None
    if imported_data and 'courses' in imported_data.data:
        for course in imported_data.data['courses']:
            if str(course.get('id')) == str(course_id):
                course_to_display = course
                break

    if not course_to_display:
        flash('Course not found.', 'danger')
        return redirect(url_for('index'))

    return render_template('google_classroom/course_detail.html', title=course_to_display.get('name'), course=course_to_display)

@app.route('/classroom/course/<course_id>/edit', methods=['GET', 'POST'])
def edit_course(course_id):
    user_id = session['user_id']
    imported_data_entry = ImportedData.query.filter_by(user_id=user_id, platform='google_classroom_api').first()

    if not imported_data_entry:
        flash('No Google Classroom data found.', 'danger')
        return redirect(url_for('index'))

    course_to_edit = None
    course_index = -1
    if 'courses' in imported_data_entry.data:
        for i, course in enumerate(imported_data_entry.data['courses']):
            if str(course.get('id')) == str(course_id):
                course_to_edit = course
                course_index = i
                break

    if not course_to_edit:
        flash('Course not found.', 'danger')
        return redirect(url_for('index'))

    if request.method == 'POST':
        new_name = request.form.get('new_name')
        if not new_name:
            flash('New name cannot be empty.', 'danger')
        else:
            # Update the name in the JSON data
            imported_data_entry.data['courses'][course_index]['name'] = new_name
            
            # Mark the JSON field as modified to ensure SQLAlchemy detects the change
            db.session.flag_modified(imported_data_entry, 'data')
            
            try:
                db.session.commit()
                flash('Course name updated successfully!', 'success')
                return redirect(url_for('index'))
            except Exception as e:
                db.session.rollback()
                flash(f'Error updating course name: {str(e)}', 'danger')

    return render_template('google_classroom/edit_course.html', title='Edit Course Name', course=course_to_edit)

# Google Classroom CourseWork Item Detail
@app.route('/classroom/course/<course_id>/coursework/<item_id>')
def coursework_item_detail(course_id, item_id):
    user_id = session['user_id']
    imported_data = ImportedData.query.filter_by(user_id=user_id, platform='google_classroom_api').first()
    
    course_to_display = None
    coursework_item = None

    if imported_data and 'courses' in imported_data.data:
        for course in imported_data.data['courses']:
            if str(course.get('id')) == str(course_id):
                course_to_display = course
                if 'courseWork' in course:
                    for work in course['courseWork']:
                        if str(work.get('id')) == str(item_id):
                            coursework_item = work
                            break
                break

    if not course_to_display or not coursework_item:
        flash('CourseWork item not found.', 'danger')
        return redirect(url_for('index'))

    return render_template('google_classroom/coursework_detail.html', 
                           title=coursework_item.get('title'), 
                           course=course_to_display,
                           item=coursework_item)

# Google Classroom Material Item Detail
@app.route('/classroom/course/<course_id>/material/<item_id>')
def material_item_detail(course_id, item_id):
    user_id = session['user_id']
    imported_data = ImportedData.query.filter_by(user_id=user_id, platform='google_classroom_api').first()
    
    course_to_display = None
    material_item = None

    if imported_data and 'courses' in imported_data.data:
        for course in imported_data.data['courses']:
            if str(course.get('id')) == str(course_id):
                course_to_display = course
                if 'materials' in course:
                    for material in course['materials']:
                        if str(material.get('id')) == str(item_id):
                            material_item = material
                            break
                break

    if not course_to_display or not material_item:
        flash('Material item not found.', 'danger')
        return redirect(url_for('index'))

    print(f"DEBUG: Material item details: {material_item}") # Added debug print
    return render_template('google_classroom/material_detail.html', 
                           title=material_item.get('title'), 
                           course=course_to_display,
                           item=material_item)

@app.route('/google_classroom/add_to_lesson/<course_id>')
def add_google_classroom_course_to_lesson(course_id):
    user_id = session['user_id']
    imported_data = ImportedData.query.filter_by(user_id=user_id, platform='google_classroom_api').first()

    course_data_to_import = None
    if imported_data and 'courses' in imported_data.data:
        for course in imported_data.data['courses']:
            if str(course.get('id')) == str(course_id):
                course_data_to_import = course
                break

    if not course_data_to_import:
        flash('Google Classroom course not found in your imported data.', 'danger')
        return redirect(url_for('view_external_data')) # Or wherever you list GC courses

    try:
        lesson = lesson_manager.import_google_classroom_course_as_lesson(user_id, course_data_to_import)
        flash(f'Successfully added/updated "{lesson.title}" to your lessons!', 'success')
        return redirect(url_for('lesson_detail', lesson_id=lesson.id))
    except Exception as e:
        flash(f'Error adding Google Classroom course to lessons: {str(e)}', 'danger')
        return redirect(url_for('course_detail', course_id=course_id)) # Redirect back to GC course detail

@app.route('/integrations/kmitl_classroom_link', methods=['GET', 'POST'])
def kmitl_classroom_link():
    user_id = session['user_id']
    
    # Fetch KMITL Study Table data
    kmitl_data_entry = ImportedData.query.filter_by(user_id=user_id, platform='kmitl_studytable').order_by(ImportedData.imported_at.desc()).first()
    kmitl_courses = []
    if kmitl_data_entry and 'courses' in kmitl_data_entry.data:
        kmitl_courses = kmitl_data_entry.data['courses']
        # Add a unique identifier for each KMITL course for mapping
        for course in kmitl_courses:
            course['identifier'] = f"{kmitl_data_entry.data.get('student_id', '')}_{kmitl_data_entry.data.get('academic_year', '')}_{kmitl_data_entry.data.get('semester', '')}_{course.get('course_code', '')}"

    # Fetch Google Classroom data
    google_classroom_data_entry = ImportedData.query.filter_by(user_id=user_id, platform='google_classroom_api').order_by(ImportedData.imported_at.desc()).first()
    google_classroom_courses = []
    if google_classroom_data_entry and 'courses' in google_classroom_data_entry.data:
        google_classroom_courses = google_classroom_data_entry.data['courses']

    # Fetch existing linkages
    existing_linkages = course_linkage_manager.get_all_linkages_by_user(user_id)
    linkage_map = {link.kmitl_course_identifier: link.google_classroom_id for link in existing_linkages}

    if request.method == 'POST':
        kmitl_identifier = request.form.get('kmitl_course_identifier')
        google_course_id = request.form.get('google_classroom_course_id')

        if kmitl_identifier and google_course_id:
            linkage = course_linkage_manager.add_linkage(user_id, kmitl_identifier, google_course_id)
            if linkage:
                flash('Course linkage added/updated successfully!', 'success')
            else:
                flash('Error adding/updating course linkage.', 'danger')
        else:
            flash('Invalid linkage data.', 'danger')
        return redirect(url_for('kmitl_classroom_link'))

    return render_template('integrations/kmitl_classroom_link.html', 
                           title='Link KMITL & Google Classroom',
                           kmitl_courses=kmitl_courses,
                           google_classroom_courses=google_classroom_courses,
                           linkage_map=linkage_map)

@app.route('/integrations/delete_linkage/<kmitl_course_identifier>', methods=['POST'])
def delete_course_linkage(kmitl_course_identifier):
    user_id = session['user_id']
    if course_linkage_manager.delete_linkage_by_kmitl_identifier(user_id, kmitl_course_identifier):
        flash('Course linkage deleted successfully!', 'success')
    else:
        flash('Error deleting course linkage.', 'danger')
    return redirect(url_for('kmitl_classroom_link'))

@app.route('/partial/sidebar-auth')
def partial_sidebar_auth():
    return render_template('sidebar_auth_fragment.html')

@app.route('/partial/profile')
@login_required
def partial_profile():
    return render_template('profile_fragment.html', user=g.user)

@app.route('/partial/change_password', methods=['GET', 'POST'])
@login_required
def partial_change_password():
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.accept_mimetypes['application/json']
    message = None
    success = False
    if request.method == 'POST':
        old_password = request.form.get('old_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        if not old_password or not new_password or not confirm_password:
            message = 'Please fill out all fields.'
        elif not g.user.check_password(old_password):
            message = 'Old password is incorrect.'
        elif new_password != confirm_password:
            message = 'New passwords do not match.'
        elif old_password == new_password:
            message = 'New password must be different from old password.'
        elif len(new_password) < 6:
            message = 'New password must be at least 6 characters.'
        else:
            g.user.set_password(new_password)
            from app import db
            db.session.commit()
            message = 'Password changed successfully!'
            success = True
    if is_ajax and request.method == 'POST':
        return jsonify(success=success, message=message, redirect='profile' if success else None)
    return render_template('change_password_fragment.html', user=g.user, message=message, success=success)

# Register Jinja2 filter for json.loads
@app.template_filter('loads')
def jinja2_loads_filter(s):
    import json
    try:
        return json.loads(s)
    except Exception:
        return []
