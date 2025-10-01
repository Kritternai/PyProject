"""
Main routes for backward compatibility.
Legacy routes that will be gradually migrated to new architecture.
"""

from flask import Blueprint, render_template, request, redirect, url_for, session, g
from functools import wraps
from .presentation.middleware.auth_middleware import login_required, get_current_user

# Create main blueprint
main_bp = Blueprint('main', __name__)


@main_bp.route('/')
@main_bp.route('/index')
def index():
    """Main index page."""
    # Check if user just connected Google Classroom
    google_connected = request.args.get('google_classroom_connected') == 'true'
    return render_template('base.html', google_connected=google_connected)


@main_bp.route('/dashboard')
@login_required
def dashboard():
    """Dashboard page."""
    return render_template('dashboard.html', user=g.user)


@main_bp.route('/partial/dashboard')
def partial_dashboard():
    """Dashboard partial for SPA."""
    return render_template('dashboard_fragment.html', user=g.user)


# Legacy routes for backward compatibility
# These will be gradually migrated to the new architecture

@main_bp.route('/login')
def login_page():
    """Login page."""
    return render_template('login.html')


@main_bp.route('/register')
def register_page():
    """Registration page."""
    return render_template('register.html')


# Import legacy routes for backward compatibility
# This ensures all existing functionality continues to work
try:
    # Note: Legacy models are commented out to avoid table name conflicts
    # from .core.lesson_manager import LessonManager
    # from .core.lesson import Lesson, LessonSection
    # from .core.imported_data import ImportedData
    # from .core.google_credentials import GoogleCredentials
    # from .core.course_linkage_manager import CourseLinkageManager
    # from .core.user_manager import UserManager
    # from .core.authenticator import Authenticator
    # from .core.note import Note
    # from .core.integration_service import IntegrationService

    # Initialize legacy managers
    # lesson_manager = LessonManager()
    # course_linkage_manager = CourseLinkageManager()
    # user_manager = UserManager()
    # authenticator = Authenticator(user_manager)

    # Import all legacy routes
    # from .legacy_routes import *

    print("Legacy routes temporarily disabled to avoid table conflicts")

except ImportError as e:
    print(f"Warning: Could not import legacy routes: {e}")
    # Continue without legacy routes if they don't exist yet

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
        if 'user_id' not in session or g.user is None:
            if request.accept_mimetypes['application/json']:
                return jsonify(success=False, message='Login required', redirect='login'), 401
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@main_bp.before_request
def load_logged_in_user():
    user_id = session.get('user_id')
    # g.user = user_manager.get_user_by_id(user_id) if user_id else None
    g.user = None  # Temporarily disabled

@main_bp.route('/')
def index():
    # Check if user just connected Google Classroom
    google_connected = request.args.get('google_classroom_connected') == 'true'
    return render_template('base.html', google_connected=google_connected)

@main_bp.route('/index')
def index_alt():
    # Check if user just connected Google Classroom
    google_connected = request.args.get('google_classroom_connected') == 'true'
    return render_template('base.html', google_connected=google_connected)

@main_bp.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', user=g.user)

@main_bp.route('/partial/dashboard')
def partial_dashboard():
    return render_template('dashboard_fragment.html', user=g.user)

@main_bp.route('/partial/note')
@login_required
def partial_note_list():
    from app.core.note import Note
    from app.core.integration_service import IntegrationService
    
    # Get all notes with lesson information
    notes = db.session.query(Note).filter(
        Note.user_id == g.user.id
    ).order_by(Note.created_at.desc()).all()
    
    # Get integrated data for summary
    user_data = IntegrationService.get_user_integrated_data(g.user.id)
    
    return render_template('note_fragment.html', 
                         notes=notes, 
                         user_data=user_data)

@main_bp.route('/partial/note/add', methods=['GET', 'POST'])
@login_required
def partial_note_add_standalone():
    if request.method == 'POST':
        from app.core.note import Note
        import uuid
        
        title = request.form.get('title')
        content = request.form.get('content')  # Changed from 'body' to 'content'
        tags = request.form.get('tags')
        status = request.form.get('status', 'active')
        external_link = request.form.get('external_link')

        if not title or not content:
            return jsonify(success=False, message='Title and content are required.')

        try:
            # Create new note using Note table
            new_note = Note(
                id=str(uuid.uuid4()),
                user_id=g.user.id,
                title=title,
                content=content,
                tags=tags,
                status=status,
                external_link=external_link
            )
            
            db.session.add(new_note)
            db.session.flush()  # Get the note ID
            
            # Handle file uploads
            from app.core.files import Files
            
            # Handle image upload
            image_file = request.files.get('image')
            if image_file and image_file.filename != '' and allowed_file(image_file.filename, 'image'):
                filename = secure_filename(image_file.filename)
                file_path = os.path.join('uploads', 'image', filename).replace('\\', '/')
                image_file.save(os.path.join(app.config['IMAGE_FOLDER'], filename))
                
                # Create file record
                image_file_record = Files(
                    id=str(uuid.uuid4()),
                    user_id=g.user.id,
                    note_id=new_note.id,
                    file_name=filename,
                    file_path=file_path,
                    file_type='image',
                    mime_type=image_file.content_type
                )
                db.session.add(image_file_record)
            
            # Handle file upload
            file_file = request.files.get('file')
            if file_file and file_file.filename != '' and allowed_file(file_file.filename, 'document'):
                filename = secure_filename(file_file.filename)
                file_path = os.path.join('uploads', 'files', filename).replace('\\', '/')
                file_file.save(os.path.join(app.config['FILE_FOLDER'], filename))
                
                # Create file record
                file_record = Files(
                    id=str(uuid.uuid4()),
                    user_id=g.user.id,
                    note_id=new_note.id,
                    file_name=filename,
                    file_path=file_path,
                    file_type='document',
                    mime_type=file_file.content_type
                )
                db.session.add(file_record)
            
            db.session.commit()
            
            # After adding, redirect to the main note list to see the new note
            notes = db.session.query(Note).filter(
                Note.user_id == g.user.id
            ).order_by(Note.created_at.desc()).all()
            html = render_template('note_fragment.html', notes=notes)
            return jsonify(success=True, html=html)
            
        except Exception as e:
            db.session.rollback()
            return jsonify(success=False, message=f'Error creating note: {str(e)}')

    return render_template('notes/create.html', lesson=None)


@main_bp.route('/partial/dev')
def partial_dev():
    user = g.user
    google_classroom_data = []
    if user:
        imported_data_gc = ImportedData.query.filter_by(user_id=user.id, platform='google_classroom_api').first()
        if imported_data_gc and 'courses' in imported_data_gc.data:
            google_classroom_data = imported_data_gc.data['courses']
    return render_template('dev_fragment.html', user=user, google_classroom_data=google_classroom_data)

# --- SPA CRUD for Class (Lesson) ---
@main_bp.route('/partial/class')
@login_required
def partial_class():
    print(f"DEBUG: partial_class called for user {g.user.id}")
    
    # Check if we should show Google Classroom courses
    show_google_courses = request.args.get('show_google_courses', 'false').lower() == 'true'
    google_classroom_connected = request.args.get('google_classroom_connected', 'false').lower() == 'true'
    
    lessons = lesson_manager.get_lessons_by_user(g.user.id)
    # Sort: favorite first, then by created order (id)
    lessons = sorted(lessons, key=lambda l: (not l.is_favorite, l.id))
    
    # Fetch imported Google Classroom data for the current user
    google_classroom_imported_data = ImportedData.query.filter_by(
        user_id=g.user.id, 
        platform='google_classroom_api'
    ).first()
    print(f"DEBUG: Found existing imported data: {google_classroom_imported_data is not None}")

    # Map Google Classroom courses to lessons
    classroom_courses_map = {}
    unimported_courses = []  # Courses that haven't been imported as lessons yet
    
    if google_classroom_imported_data and 'courses' in google_classroom_imported_data.data:
        courses = google_classroom_imported_data.data['courses']
        print(f"DEBUG: Found {len(courses)} Google Classroom courses")
        
        # Get existing Google Classroom lesson IDs
        existing_gc_lesson_ids = set()
        for lesson in lessons:
            if lesson.source_platform == 'google_classroom' and lesson.external_id:
                existing_gc_lesson_ids.add(str(lesson.external_id))
        
        for course_data in courses:
            course_id = str(course_data.get('id'))
            classroom_courses_map[course_id] = course_data
            
            # Check if this course hasn't been imported as a lesson yet
            if course_id not in existing_gc_lesson_ids:
                unimported_courses.append(course_data)

    # Process existing lessons
    for lesson in lessons:
        if lesson.source_platform == 'google_classroom' and lesson.external_id:
            course_id_str = str(lesson.external_id)
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
                
                # Add 'Google Classroom' tag to the first section if it exists
                if lesson.sections:
                    first_section = lesson.sections[0]
                    if first_section.tags:
                        try:
                            import json
                            current_tags = json.loads(first_section.tags)
                            if 'Google Classroom' not in current_tags:
                                current_tags.append('Google Classroom')
                                first_section.tags = json.dumps(current_tags)
                        except:
                            first_section.tags = json.dumps(['Google Classroom'])
                    else:
                        first_section.tags = json.dumps(['Google Classroom'])
            else:
                # If linked to GC but course data not found, set defaults
                lesson.author_name = 'Classroom Teacher (Data Missing)'
                lesson.classroom_assignments_count = 0
                # Add 'Google Classroom' tag to the first section if it exists
                if lesson.sections:
                    first_section = lesson.sections[0]
                    if first_section.tags:
                        try:
                            import json
                            current_tags = json.loads(first_section.tags)
                            if 'Google Classroom' not in current_tags:
                                current_tags.append('Google Classroom')
                                first_section.tags = json.dumps(current_tags)
                        except:
                            first_section.tags = json.dumps(['Google Classroom'])
                    else:
                        first_section.tags = json.dumps(['Google Classroom'])
        else:
            # For lessons not from Google Classroom
            lesson.classroom_assignments_count = 0 # Ensure it's 0 for non-GC lessons
            if not hasattr(lesson, 'author_name') or not lesson.author_name:
                lesson.author_name = 'Your Lesson' # Default author for non-GC lessons

    print(f"DEBUG: Rendering template with {len(lessons)} lessons and {len(unimported_courses)} unimported Google Classroom courses")
    return render_template('class_fragment.html', 
                         lessons=lessons, 
                         unimported_google_courses=unimported_courses,
                         google_classroom_connected=google_classroom_imported_data is not None,
                         show_google_courses=show_google_courses or len(unimported_courses) > 0)

@main_bp.route('/partial/class/add', methods=['GET', 'POST'])
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
        selected_color = request.form.get('selectedColor', 1) # Get selected color from form
        google_classroom_id = request.form.get('google_classroom_id') # Get Google Classroom ID
        source_platform = request.form.get('source_platform', 'manual') # Get source platform
        
        if not title:
            message = 'Title is required.'
        else:
            try:
                lesson = lesson_manager.add_lesson(
                    g.user.id, 
                    title, 
                    description, 
                    status, 
                    None,  # tags parameter not supported in new schema
                    source_platform=source_platform,
                    google_classroom_id=google_classroom_id,
                    author_name=author_name, 
                    selected_color=int(selected_color)
                )
                if lesson:
                    return jsonify(success=True, redirect='class')
                else:
                    message = 'Error adding lesson.'
            except Exception as e:
                print(f"Error adding lesson: {e}")
                message = f'Error adding lesson: {str(e)}'
        return jsonify(success=False, message=message)
    return render_template('lessons/_add.html')

@main_bp.route('/partial/class/<lesson_id>')
@login_required
def partial_class_detail(lesson_id):
    from app.core.integration_service import IntegrationService
    
    lesson = lesson_manager.get_lesson_by_id(lesson_id)
    if not lesson or lesson.user_id != g.user.id:
        return '<div class="alert alert-danger">Lesson not found or no permission.</div>'
    
    # Get integrated data
    lesson_summary = IntegrationService.get_lesson_summary(lesson_id, g.user.id)
    
    # Get notes for this lesson
    from app.core.note import Note
    notes = db.session.query(Note).filter(
        Note.lesson_id == lesson_id,
        Note.user_id == g.user.id
    ).order_by(Note.created_at.desc()).all()
    
    # Add notes to lesson_summary
    if lesson_summary:
        lesson_summary['notes'] = notes
    
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
    return render_template('lessons/_detail.html', 
                         lesson=lesson, 
                         sections=sections, 
                         lesson_summary=lesson_summary)

@main_bp.route('/partial/class/<lesson_id>/edit', methods=['GET', 'POST'])
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

@main_bp.route('/partial/class/<lesson_id>/delete', methods=['POST'])
@login_required
def partial_class_delete(lesson_id):
    lesson = lesson_manager.get_lesson_by_id(lesson_id)
    if not lesson or lesson.user_id != g.user.id:
        return jsonify(success=False, message='Lesson not found or no permission.')
    lesson_manager.delete_lesson(lesson_id)
    return jsonify(success=True, redirect='class')

# --- SPA CRUD for LessonSection (Section/Content) ---
@main_bp.route('/partial/class/<lesson_id>/sections')
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

@main_bp.route('/partial/class/<lesson_id>/sections/add', methods=['GET', 'POST'])
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
        import json
        if not title:
            return jsonify(success=False, message='Title is required.')
        
        # If type is 'note', create both note and section
        if type_ == 'note':
            # Create note in Note table
            from app.core.note import Note
            from app.core.files import Files
            
            new_note = Note(
                id=str(uuid.uuid4()),
                user_id=g.user.id,
                lesson_id=lesson_id,
                title=title,
                content=content,
                status='active',
                external_link=None
            )
            
            db.session.add(new_note)
            db.session.flush()  # Get the note ID
            
            # Handle file uploads for note
            if file_urls:
                try:
                    file_urls_list = json.loads(file_urls) if isinstance(file_urls, str) else file_urls
                    for file_url in file_urls_list:
                        filename = os.path.basename(file_url)
                        file_record = Files(
                            id=str(uuid.uuid4()),
                            user_id=g.user.id,
                            note_id=new_note.id,
                            lesson_id=lesson_id,
                            file_name=filename,
                            file_path=file_url.replace('/static/', ''),
                            file_type='document',
                            mime_type='application/octet-stream'
                        )
                        db.session.add(file_record)
                except Exception as e:
                    print(f"Error creating file records: {e}")
            
            # Also create a section for the note (so it shows in lesson)
            section = lesson_manager.add_section(lesson_id, title, content, 'note', None, file_urls=json.dumps(file_urls) if file_urls else None)
            
            db.session.commit()
            
            # Return updated sections list for class (with the new note section)
            sections = lesson_manager.get_sections(lesson_id)
            class_html = render_template('lessons/section_list.html', lesson=lesson, sections=sections)
            
            # Also return updated notes list for notes page
            from app.core.integration_service import IntegrationService
            user_data = IntegrationService.get_user_integrated_data(g.user.id)
            notes = db.session.query(Note).filter(
                Note.user_id == g.user.id
            ).order_by(Note.created_at.desc()).all()
            notes_html = render_template('note_fragment.html', notes=notes, user_data=user_data)
            

            
            return jsonify(
                success=True, 
                html=class_html,
                notes_html=notes_html,
                message='Note added successfully!',
                redirect_to='note'
            )
        else:
            # For other types, just create section
            section = lesson_manager.add_section(lesson_id, title, content, type_, assignment_due, file_urls=json.dumps(file_urls) if file_urls else None)
            # Return updated section list as HTML fragment
            sections = lesson_manager.get_sections(lesson_id)
            html = render_template('lessons/section_list.html', lesson=lesson, sections=sections)
            return jsonify(success=True, html=html)
    return render_template('lessons/section_add.html', lesson=lesson)

@main_bp.route('/partial/class/<lesson_id>/sections/<section_id>/edit', methods=['GET', 'POST'])
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
        lesson_manager.update_section(section_id, title, content, type_, assignment_due, file_urls=json.dumps(file_urls) if file_urls else None)
        # Return updated section list as HTML fragment
        sections = lesson_manager.get_sections(lesson_id)
        html = render_template('lessons/section_list.html', lesson=lesson, sections=sections)
        return jsonify(success=True, html=html)
    return render_template('lessons/section_edit.html', lesson=lesson, section=section)

@main_bp.route('/partial/class/<lesson_id>/sections/<section_id>/delete', methods=['POST'])
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
# app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER  # Temporarily disabled
# app.config['IMAGE_FOLDER'] = IMAGE_FOLDER  # Temporarily disabled
# app.config['FILE_FOLDER'] = FILE_FOLDER  # Temporarily disabled

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
@main_bp.route('/partial/class/<lesson_id>/notes/add', methods=['GET', 'POST'])
@login_required
def partial_note_add(lesson_id):
    from app.core.integration_service import IntegrationService
    
    lesson = lesson_manager.get_lesson_by_id(lesson_id)
    if not lesson or lesson.user_id != g.user.id:
        return '<div class="alert alert-danger">Lesson not found or no permission.</div>'
    
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        tags = request.form.get('tags')
        status = request.form.get('status', 'active')
        external_link = request.form.get('external_link')

        if not title or not content:
            return jsonify(success=False, message='Title and content are required.')

        try:
            # Create note using Note table
            from app.core.note import Note
            new_note = Note(
                id=str(uuid.uuid4()),
                user_id=g.user.id,
                lesson_id=lesson_id,
                title=title,
                content=content,
                tags=tags,
                status=status,
                external_link=external_link
            )
            
            db.session.add(new_note)
            db.session.flush()  # Get the note ID
            
            # Handle file uploads
            from app.core.files import Files
            
            # Handle image upload
            image_file = request.files.get('image')
            if image_file and image_file.filename != '' and allowed_file(image_file.filename, 'image'):
                filename = secure_filename(image_file.filename)
                file_path = os.path.join('uploads', 'image', filename).replace('\\', '/')
                image_file.save(os.path.join(app.config['IMAGE_FOLDER'], filename))
                
                # Create file record
                image_file_record = Files(
                    id=str(uuid.uuid4()),
                    user_id=g.user.id,
                    note_id=new_note.id,
                    lesson_id=lesson_id,
                    file_name=filename,
                    file_path=file_path,
                    file_type='image',
                    mime_type=image_file.content_type
                )
                db.session.add(image_file_record)
            
            # Handle file upload
            file_file = request.files.get('file')
            if file_file and file_file.filename != '' and allowed_file(file_file.filename, 'document'):
                filename = secure_filename(file_file.filename)
                file_path = os.path.join('uploads', 'files', filename).replace('\\', '/')
                file_file.save(os.path.join(app.config['FILE_FOLDER'], filename))
                
                # Create file record
                file_record = Files(
                    id=str(uuid.uuid4()),
                    user_id=g.user.id,
                    note_id=new_note.id,
                    lesson_id=lesson_id,
                    file_name=filename,
                    file_path=file_path,
                    file_type='document',
                    mime_type=file_file.content_type
                )
                db.session.add(file_record)
            
            db.session.commit()
            
            # Return updated sections list for class
            sections = lesson_manager.get_sections(lesson_id)
            class_html = render_template('lessons/section_list.html', lesson=lesson, sections=sections)
            
            # Also return updated notes list for notes page
            from app.core.integration_service import IntegrationService
            user_data = IntegrationService.get_user_integrated_data(g.user.id)
            notes = db.session.query(Note).filter(
                Note.user_id == g.user.id
            ).order_by(Note.created_at.desc()).all()
            notes_html = render_template('note_fragment.html', notes=notes, user_data=user_data)
            
            return jsonify(
                success=True, 
                html=class_html,
                notes_html=notes_html,
                message='Note added successfully and synced to notes page!'
            )
            
        except Exception as e:
            db.session.rollback()
            return jsonify(success=False, message=f'Error creating note: {str(e)}')

    return render_template('notes/create.html', lesson=lesson)

@main_bp.route('/partial/class/<lesson_id>/notes/<section_id>/edit', methods=['GET', 'POST'])
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
                image_path = os.path.join('uploads', 'image', filename).replace('\\', '/')
                image_file.save(os.path.join(app.config['IMAGE_FOLDER'], filename))

        file_path = None
        if request.form.get('remove_file'):
            if section.file_urls:
                try:
                    old_file_urls = json.loads(section.file_urls)
                    for old_file_url in old_file_urls:
                        old_file_filename = os.path.basename(old_file_url)
                        old_file_path = os.path.join(app.config['FILE_FOLDER'], old_file_filename)
                        if os.path.exists(old_file_path):
                            os.remove(old_file_path)
                except:
                    pass
                file_path = None
        elif 'file' in request.files and request.files['file'].filename != '':
            file_file = request.files['file']
            if allowed_file(file_file.filename, 'document'):
                if section.file_urls:
                    try:
                        old_file_urls = json.loads(section.file_urls)
                        for old_file_url in old_file_urls:
                            old_file_filename = os.path.basename(old_file_url)
                            old_file_path = os.path.join(app.config['FILE_FOLDER'], old_file_filename)
                            if os.path.exists(old_file_path):
                                os.remove(old_file_path)
                    except:
                        pass
                filename = secure_filename(file_file.filename)
                file_path = os.path.join('uploads', 'files', filename).replace('\\', '/')
                file_file.save(os.path.join(app.config['FILE_FOLDER'], filename))
        
        # Keep existing files if no new file uploaded and no removal requested
        if not file_path and not request.form.get('remove_file') and section.file_urls:
            file_path = section.file_urls

        lesson_manager.update_section(
            section_id=section_id,
            title=title,
            body=body,
            tags=tags,
            status=status,
            image_path=image_path,
            file_urls=json.dumps([file_path]) if file_path else None,
            external_link=external_link
        )
        sections = lesson_manager.get_sections(lesson_id)
        html = render_template('lessons/section_list.html', lesson=lesson, sections=sections)
        return jsonify(success=True, html=html)
    return render_template('notes/edit.html', lesson=lesson, note=section)



@main_bp.route('/partial/note/<note_id>/delete', methods=['POST'])
@login_required
def partial_note_delete_standalone(note_id):
    from app.core.note import Note
    
    note = db.session.query(Note).filter(
        Note.id == note_id,
        Note.user_id == g.user.id
    ).first()
    
    if not note:
        return jsonify(success=False, message='Note not found or permission denied'), 404

    try:
        db.session.delete(note)
        db.session.commit()
        
        # Return the updated list of all notes
        notes = db.session.query(Note).filter(
            Note.user_id == g.user.id
        ).order_by(Note.created_at.desc()).all()
        return render_template('note_fragment.html', notes=notes)
    except Exception as e:
        db.session.rollback()
        return jsonify(success=False, message=f'Error deleting note: {str(e)}')

@main_bp.route('/partial/note/<note_id>/edit', methods=['GET', 'POST'])
@login_required
def partial_note_edit_standalone(note_id):
    from app.core.note import Note
    
    note = db.session.query(Note).filter(
        Note.id == note_id,
        Note.user_id == g.user.id
    ).first()
    
    if not note:
        return jsonify(success=False, message='Note not found.')
    
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')  # Changed from 'body' to 'content'
        tags = request.form.get('tags')
        status = request.form.get('status', 'active')
        external_link = request.form.get('external_link')
        
        if not title:
            return jsonify(success=False, message='Title is required.')
        
        try:
            note.title = title
            note.content = content
            note.tags = tags
            note.status = status
            note.external_link = external_link
            note.updated_at = datetime.utcnow()
            
            # Handle file uploads
            from app.core.files import Files
            
            # Handle image upload
            image_file = request.files.get('image')
            if image_file and image_file.filename != '' and allowed_file(image_file.filename, 'image'):
                filename = secure_filename(image_file.filename)
                file_path = os.path.join('uploads', 'image', filename).replace('\\', '/')
                image_file.save(os.path.join(app.config['IMAGE_FOLDER'], filename))
                
                # Create file record
                image_file_record = Files(
                    id=str(uuid.uuid4()),
                    user_id=g.user.id,
                    note_id=note.id,
                    file_name=filename,
                    file_path=file_path,
                    file_type='image',
                    mime_type=image_file.content_type
                )
                db.session.add(image_file_record)
            
            # Handle file upload
            file_file = request.files.get('file')
            if file_file and file_file.filename != '' and allowed_file(file_file.filename, 'document'):
                filename = secure_filename(file_file.filename)
                file_path = os.path.join('uploads', 'files', filename).replace('\\', '/')
                file_file.save(os.path.join(app.config['FILE_FOLDER'], filename))
                
                # Create file record
                file_record = Files(
                    id=str(uuid.uuid4()),
                    user_id=g.user.id,
                    note_id=note.id,
                    file_name=filename,
                    file_path=file_path,
                    file_type='document',
                    mime_type=file_file.content_type
                )
                db.session.add(file_record)
            
            # Handle file removal
            if request.form.get('remove_image'):
                # Delete image files
                for file_record in note.files:
                    if file_record.file_type == 'image':
                        # Remove physical file
                        file_path = os.path.join(app.config['IMAGE_FOLDER'], file_record.file_name)
                        if os.path.exists(file_path):
                            os.remove(file_path)
                        # Remove from database
                        db.session.delete(file_record)
            
            if request.form.get('remove_file'):
                # Delete document files
                for file_record in note.files:
                    if file_record.file_type == 'document':
                        # Remove physical file
                        file_path = os.path.join(app.config['FILE_FOLDER'], file_record.file_name)
                        if os.path.exists(file_path):
                            os.remove(file_path)
                        # Remove from database
                        db.session.delete(file_record)
            
            db.session.commit()
            return jsonify(success=True, redirect='note')
        except Exception as e:
            db.session.rollback()
            return jsonify(success=False, message=f'Error updating note: {str(e)}')
    
        # For GET requests, return the edit form template
    return render_template('notes/_edit.html', note=note)

# Integration Routes
@main_bp.route('/api/integration/sync-note-to-lesson/<note_id>/<lesson_id>', methods=['POST'])
@login_required
def sync_note_to_lesson(note_id, lesson_id):
    """Sync a note to a lesson"""
    from app.core.integration_service import IntegrationService
    
    try:
        section = IntegrationService.create_lesson_section_from_note(note_id, lesson_id, g.user.id)
        if section:
            return jsonify(success=True, message='Note synced to lesson successfully!')
        else:
            return jsonify(success=False, message='Failed to sync note to lesson.')
    except Exception as e:
        return jsonify(success=False, message=f'Error syncing note: {str(e)}')

@main_bp.route('/api/integration/sync-lesson-to-note/<lesson_id>/<section_id>', methods=['POST'])
@login_required
def sync_lesson_to_note(lesson_id, section_id):
    """Sync a lesson section to a note"""
    from app.core.integration_service import IntegrationService
    
    try:
        note = IntegrationService.create_note_from_lesson_section(lesson_id, section_id, g.user.id)
        if note:
            return jsonify(success=True, message='Lesson section synced to note successfully!')
        else:
            return jsonify(success=False, message='Failed to sync lesson section to note.')
    except Exception as e:
        return jsonify(success=False, message=f'Error syncing lesson: {str(e)}')

@main_bp.route('/api/integration/sync-files/<source_type>/<source_id>/<target_type>/<target_id>', methods=['POST'])
@login_required
def sync_files_between_entities(source_type, source_id, target_type, target_id):
    """Sync files between different entities"""
    from app.core.integration_service import IntegrationService
    
    try:
        file_count = IntegrationService.sync_files_between_entities(
            source_type, source_id, target_type, target_id, g.user.id
        )
        return jsonify(success=True, message=f'{file_count} files synced successfully!')
    except Exception as e:
        return jsonify(success=False, message=f'Error syncing files: {str(e)}')


# === End of note management routes ===

@main_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = authenticator.login(email, password)
        if user:
            session['user_id'] = user.id
            return redirect(url_for('dashboard'))
        else:
            return render_template('login_fragment.html', success=False, message='Invalid email or password.')
    return render_template('login_fragment.html')

@main_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        if not email or not password:
            return render_template('register_fragment.html', success=False, message='Please fill out all fields.')
        user = authenticator.register(email, password)
        if user:
            return render_template('register_fragment.html', success=True, message='Registration successful! Please log in.')
        else:
            return render_template('register_fragment.html', success=False, message='Email already exists.')
    return render_template('register_fragment.html')

@main_bp.route('/partial/login', methods=['GET', 'POST'])
def partial_login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = authenticator.login(email, password)
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.accept_mimetypes['application/json']
        if user:
            session['user_id'] = user.id
            if is_ajax:
                return jsonify(success=True, message='Logged in successfully!', redirect='dashboard')
            else:
                return render_template('login_fragment.html', success=True, message='Logged in successfully!')
        else:
            if is_ajax:
                return jsonify(success=False, message='Invalid email or password.')
            else:
                return render_template('login_fragment.html', success=False, message='Invalid email or password.')
    return render_template('login_fragment.html')

@main_bp.route('/partial/register', methods=['GET', 'POST'])
def partial_register():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.accept_mimetypes['application/json']
        if not email or not password:
            if is_ajax:
                return jsonify(success=False, message='Please fill out all fields.')
            else:
                return render_template('register_fragment.html', success=False, message='Please fill out all fields.')
        
        user = authenticator.register(
            email=email, 
            password=password
        )
        if user:
            if is_ajax:
                return jsonify(success=True, message='Registration successful! Please log in.', redirect='login')
            else:
                return render_template('register_fragment.html', success=True, message='Registration successful! Please log in.')
        else:
            if is_ajax:
                return jsonify(success=False, message='Email already exists.')
            else:
                return render_template('register_fragment.html', success=False, message='Email already exists.')
    return render_template('register_fragment.html')

@main_bp.route('/partial/sidebar-auth')
def partial_sidebar_auth():
    return render_template('sidebar_auth_fragment.html')

@main_bp.route('/partial/profile')
@login_required
def partial_profile():
    return render_template('profile_fragment.html', user=g.user)

@main_bp.route('/partial/change_password', methods=['GET', 'POST'])
@login_required
def partial_change_password():
    if request.method == 'POST':
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')

        user = g.user
        if not user.check_password(current_password):
            return jsonify(success=False, message='Incorrect current password.')

        if new_password != confirm_password:
            return jsonify(success=False, message='New passwords do not match.')

        if user_manager.update_user(user.id, new_password=new_password):
            return jsonify(success=True, message='Password updated successfully!', redirect='profile')
        else:
            return jsonify(success=False, message='Error updating password.')
    return render_template('change_password_fragment.html', user=g.user)

@main_bp.route('/integrations/kmitl_classroom_link', methods=['GET', 'POST'])
@login_required
def kmitl_classroom_link():
    user_id = g.user.id
    kmitl_courses = []
    linkage_map = {}

    # Fetch KMITL Study Table data
    kmitl_imported_data = ImportedData.query.filter_by(user_id=user_id, platform='kmitl_studytable').first()
    if kmitl_imported_data and kmitl_imported_data.data:
        # Assuming kmitl_studytable data is a list of course dictionaries
        kmitl_courses = kmitl_imported_data.data.get('courses', []) 
        # Ensure each course has an 'identifier' for linking
        for course in kmitl_courses:
            if 'course_code' in course and 'semester' in course and 'academic_year' in course and 'section' in course:
                course['identifier'] = f"{course['course_code']}_{course['academic_year']}_{course['semester']}_{course['section']}"
            else:
                course['identifier'] = None # Or handle error/missing data

    # Fetch existing linkages
    linkages = CourseLinkage.query.filter_by(user_id=user_id).all()
    for linkage in linkages:
        linkage_map[linkage.kmitl_course_identifier] = linkage.google_classroom_id

    if request.method == 'POST':
        kmitl_course_identifier = request.form.get('kmitl_course_identifier')
        google_classroom_id = request.form.get('google_classroom_id')

        if kmitl_course_identifier and google_classroom_id:
            # Check if linkage already exists
            existing_linkage = CourseLinkage.query.filter_by(
                user_id=user_id, 
                kmitl_course_identifier=kmitl_course_identifier
            ).first()

            if existing_linkage:
                flash('This KMITL course is already linked.', 'warning')
            else:
                course_linkage_manager.add_linkage(user_id, kmitl_course_identifier, google_classroom_id)
                flash('Course linked successfully!', 'success')
            return redirect(url_for('kmitl_classroom_link'))
        else:
            flash('Missing KMITL course identifier or Google Classroom ID.', 'danger')

    return render_template(
        'integrations/kmitl_classroom_link.html',
        kmitl_courses=kmitl_courses,
        linkage_map=linkage_map
    )

@main_bp.route('/delete_course_linkage/<kmitl_course_identifier>', methods=['POST'])
@login_required
def delete_course_linkage(kmitl_course_identifier):
    user_id = g.user.id
    if course_linkage_manager.delete_linkage_by_kmitl_identifier(user_id, kmitl_course_identifier):
        flash('Course unlinked successfully!', 'success')
    else:
        flash('Error unlinking course.', 'danger')
    return redirect(url_for('kmitl_classroom_link'))

@main_bp.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

# Lesson Management Routes
@main_bp.route('/lessons')
def list_lessons():
    user_id = session['user_id']
    lessons = lesson_manager.get_lessons_by_user(user_id)
    return render_template('lessons/list.html', title='My Lessons', lessons=lessons)

@main_bp.route('/lessons/add', methods=['GET', 'POST'])
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
                        'lesson_tags': json.loads(lesson.sections[0].tags) if lesson.sections and lesson.sections[0].tags else []
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

@main_bp.route('/lessons/<lesson_id>')
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

@main_bp.route('/lessons/<lesson_id>/edit', methods=['GET', 'POST'])
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
                        'lesson_tags': json.loads(updated_lesson.sections[0].tags) if updated_lesson.sections and updated_lesson.sections[0].tags else []
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

@main_bp.route('/lessons/<lesson_id>/delete', methods=['POST'])
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

@main_bp.route('/partial/class/<lesson_id>/favorite', methods=['POST'])
@login_required
def partial_class_toggle_favorite(lesson_id):
    lesson = lesson_manager.get_lesson_by_id(lesson_id)
    if not lesson or lesson.user_id != g.user.id:
        return jsonify(success=False, message='Lesson not found or no permission.'), 404
    new_state = lesson_manager.toggle_favorite(lesson_id)
    return jsonify(success=True, is_favorite=new_state)

# API Endpoint for Chrome Extension
@main_bp.route('/api/import_data', methods=['POST'])
def import_data_from_extension():
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400

    data = request.get_json()
    platform = data.get('platform')
    imported_data_body = data.get('data')

    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"error": "User not authenticated"}), 401

    if not platform or not imported_data_body:
        return jsonify({"error": "Missing platform or data in request"}), 400

    try:
        new_imported_data = ImportedData(user_id=user_id, platform=platform, data=imported_data_body)
        db.session.add(new_imported_data)
        db.session.commit()
        return jsonify({"message": f"Data from {platform} received and saved successfully!"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to save data: {str(e)}"}), 500

@main_bp.route('/external_data/view')
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
@main_bp.route('/google_classroom/authorize')
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
                "redirect_uris": [
                    "http://localhost:8000/google_classroom/oauth2callback",
                    "http://localhost:8001/google_classroom/oauth2callback",
                    "http://127.0.0.1:8000/google_classroom/oauth2callback",
                    "http://127.0.0.1:8001/google_classroom/oauth2callback"
                ]
            }
        },
        scopes=SCOPES
    )

    # Use specific redirect URI instead of dynamic one
    flow.redirect_uri = "http://localhost:8000/google_classroom/oauth2callback"

    authorization_url, state = flow.authorization_url(
        access_type='offline',
        prompt='consent'
    )

    session['oauth_state'] = state
    return redirect(authorization_url)

@main_bp.route('/google_classroom/oauth2callback')
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
                "redirect_uris": [
                    "http://localhost:8000/google_classroom/oauth2callback",
                    "http://localhost:8001/google_classroom/oauth2callback",
                    "http://127.0.0.1:8000/google_classroom/oauth2callback",
                    "http://127.0.0.1:8001/google_classroom/oauth2callback"
                ]
            }
        },
        scopes=SCOPES,
        state=state
    )

    # Use specific redirect URI instead of dynamic one
    flow.redirect_uri = "http://localhost:8000/google_classroom/oauth2callback"

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
    print(f"DEBUG: OAuth2 callback completed for user {user_id}, redirecting to lessons page")
    
    # Fetch Google Classroom data immediately after successful connection
    try:
        print(f"DEBUG: Fetching Google Classroom data for user {user_id}")
        # Call the function directly instead of the route
        # GoogleCredentials is already imported at the top of the file
        from google.oauth2.credentials import Credentials
        from google.auth.transport.requests import Request
        from googleapiclient.discovery import build
        
        google_creds = GoogleCredentials.query.filter_by(user_id=user_id).first()
        if google_creds:
            creds_data = {
                'token': google_creds.token,
                'refresh_token': google_creds.refresh_token,
                'token_uri': google_creds.token_uri,
                'client_id': google_creds.client_id,
                'client_secret': google_creds.client_secret,
                'scopes': google_creds.scopes.split(',')
            }
            credentials = Credentials.from_authorized_user_info(creds_data)
            
            # Build service and fetch data
            service = build('classroom', 'v1', credentials=credentials)
            courses_results = service.courses().list(courseStates='ACTIVE').execute()
            fetched_courses = courses_results.get('courses', [])
            print(f"DEBUG: Found {len(fetched_courses)} active courses for user {user_id}")
            
            # Fetch detailed data for each course
            for course in fetched_courses:
                try:
                    course_id = course['id']
                    print(f"DEBUG: Fetching detailed data for course: {course.get('name', 'Unknown')}")
                    
                    # Fetch announcements
                    try:
                        announcements_results = service.courses().announcements().list(courseId=course_id).execute()
                        course['announcements'] = announcements_results.get('announcements', [])
                        print(f"DEBUG: Found {len(course['announcements'])} announcements")
                    except Exception as e:
                        print(f"DEBUG: Could not fetch announcements: {e}")
                        course['announcements'] = []
                    
                    # Fetch coursework
                    try:
                        coursework_results = service.courses().courseWork().list(courseId=course_id).execute()
                        course['courseWork'] = coursework_results.get('courseWork', [])
                        print(f"DEBUG: Found {len(course['courseWork'])} coursework items")
                    except Exception as e:
                        print(f"DEBUG: Could not fetch coursework: {e}")
                        course['courseWork'] = []
                    
                    # Fetch materials
                    try:
                        materials_results = service.courses().courseWorkMaterials().list(courseId=course_id).execute()
                        course['materials'] = materials_results.get('courseWorkMaterial', [])
                        print(f"DEBUG: Found {len(course['materials'])} materials")
                    except Exception as e:
                        print(f"DEBUG: Could not fetch materials: {e}")
                        course['materials'] = []
                    
                    # Fetch topics
                    try:
                        topics_results = service.courses().topics().list(courseId=course_id).execute()
                        course['topics'] = topics_results.get('topic', [])
                        print(f"DEBUG: Found {len(course['topics'])} topics")
                    except Exception as e:
                        print(f"DEBUG: Could not fetch topics: {e}")
                        course['topics'] = []
                    
                    # Fetch roster
                    try:
                        roster_results = service.courses().students().list(courseId=course_id).execute()
                        course['students'] = roster_results.get('students', [])
                        print(f"DEBUG: Found {len(course['students'])} students")
                    except Exception as e:
                        print(f"DEBUG: Could not fetch roster: {e}")
                        course['students'] = []
                    
                    # Fetch teachers
                    try:
                        teachers_results = service.courses().teachers().list(courseId=course_id).execute()
                        course['teachers'] = teachers_results.get('teachers', [])
                        print(f"DEBUG: Found {len(course['teachers'])} teachers")
                    except Exception as e:
                        print(f"DEBUG: Could not fetch teachers: {e}")
                        course['teachers'] = []
                        
                except Exception as e:
                    print(f"ERROR: Failed to fetch detailed data for course {course.get('name', 'Unknown')}: {e}")
                    continue
            
            # Store courses data
            imported_data = ImportedData.query.filter_by(
                user_id=user_id, 
                platform='google_classroom_api'
            ).first()
            
            if not imported_data:
                imported_data = ImportedData(
                    user_id=user_id, 
                    platform='google_classroom_api', 
                    data={'courses': fetched_courses}
                )
                db.session.add(imported_data)
            else:
                imported_data.data = {'courses': fetched_courses}
            
            db.session.commit()
            print(f"DEBUG: Google Classroom data fetched and stored successfully for user {user_id}")
        else:
            print(f"DEBUG: No Google credentials found for user {user_id}")
            flash('Connected successfully but failed to fetch data', 'warning')
            return redirect(url_for('index') + '#class?google_classroom_connected=true&show_google_courses=false')
        
        # Auto-import all courses immediately
        if fetched_courses:
            courses_count = len(fetched_courses)
            print(f"DEBUG: Found {courses_count} Google Classroom courses to auto-import")
            
            # Auto-import all courses with default settings
            lessons_created = 0
            total_sections = 0
            
            for course in fetched_courses:
                try:
                    print(f"DEBUG: Auto-importing course: {course.get('name', 'Unknown')}")
                    
                    # Create lesson with default settings
                    lesson = lesson_manager.add_lesson(
                        user_id=user_id,
                        title=course.get('name', 'Untitled Lesson'),
                        description=course.get('description', course.get('section', '')),
                        status='active',
                        tags='Google Classroom',
                        source_platform='google_classroom',
                        google_classroom_id=course.get('id'),
                        author_name='Classroom Teacher',
                        selected_color=1
                    )
                    
                    if lesson:
                        print(f"DEBUG: Successfully created lesson: {lesson.title}")
                        
                        # Update lesson with additional Google Classroom data
                        lesson.external_url = course.get('alternateLink', '')
                        
                        # Update lesson fields directly
                        lesson.difficulty_level = 'beginner'
                        lesson.is_favorite = False
                        lesson.total_sections = 0
                        lesson.completed_sections = 0
                        lesson.total_time_spent = 0
                        
                        # Add Google Classroom specific metadata
                        lesson.metadata = {
                            'google_classroom_course_id': course.get('id'),
                            'section': course.get('section', ''),
                            'announcements_count': len(course.get('announcements', [])),
                            'coursework_count': len(course.get('courseWork', [])),
                            'materials_count': len(course.get('materials', [])),
                            'topics_count': len(course.get('topics', [])),
                            'students_count': len(course.get('students', [])),
                            'teachers_count': len(course.get('teachers', [])),
                            'imported_at': datetime.utcnow().isoformat(),
                            'auto_imported': True
                        }
                        
                        # Import all content automatically
                        sections_created = 0
                        
                        # Import announcements
                        if course.get('announcements'):
                            for announcement in course['announcements']:
                                section = lesson_manager.add_section(
                                    lesson.id,
                                    title=f"Announcement: {announcement.get('text', 'Announcement')[:50]}...",
                                    content=announcement.get('description', announcement.get('text', '')),
                                    type='announcement',
                                    order=sections_created + 1
                                )
                                if section:
                                    sections_created += 1
                        
                        # Import assignments
                        if course.get('courseWork'):
                            for assignment in course['courseWork']:
                                section = lesson_manager.add_section(
                                    lesson.id,
                                    title=f"Assignment: {assignment.get('title', 'Assignment')}",
                                    content=assignment.get('description', ''),
                                    type='assignment',
                                    order=sections_created + 1
                                )
                                if section:
                                    sections_created += 1
                        
                        # Import materials
                        if course.get('materials'):
                            for material in course['materials']:
                                section = lesson_manager.add_section(
                                    lesson.id,
                                    title=f"Material: {material.get('title', 'Material')}",
                                    content=material.get('description', ''),
                                    type='material',
                                    order=sections_created + 1
                                )
                                if section:
                                    sections_created += 1
                        
                        # Import topics
                        if course.get('topics'):
                            for topic in course['topics']:
                                section = lesson_manager.add_section(
                                    lesson.id,
                                    title=f"Topic: {topic.get('name', 'Topic')}",
                                    content=topic.get('description', ''),
                                    type='topic',
                                    order=sections_created + 1
                                )
                                if section:
                                    sections_created += 1
                        
                        lessons_created += 1
                        total_sections += sections_created
                        print(f"DEBUG: Course '{course.get('name')}' imported with {sections_created} sections")
                        
                except Exception as e:
                    print(f"ERROR: Failed to auto-import course {course.get('name', 'Unknown')}: {e}")
                    import traceback
                    traceback.print_exc()
                    continue
            
            # Commit all changes
            db.session.commit()
            
            if lessons_created > 0:
                print(f"DEBUG: Successfully auto-imported {lessons_created} courses with {total_sections} total sections")
                flash(f'Successfully auto-imported {lessons_created} Google Classroom courses with {total_sections} sections!', 'success')
            else:
                print(f"DEBUG: No courses were auto-imported")
                flash('Connected successfully but no courses were imported', 'warning')
                
        else:
            print(f"DEBUG: No courses found to auto-import")
            flash('Connected successfully but no courses found to import', 'info')
            
    except Exception as e:
        print(f"ERROR: Failed to fetch or auto-import Google Classroom data: {e}")
        flash(f'Connected successfully but failed to auto-import data: {e}', 'warning')
    
    # Redirect to SPA main page with class tab active and Google Classroom connected
    return redirect(url_for('index') + '#class?google_classroom_connected=true&show_google_courses=false')

@main_bp.route('/google_classroom/fetch_data')
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
        existing_imported_data.imported_at = datetime.utcnow() # Update timestamp
        db.session.commit()
        print(f"DEBUG: Google Classroom data fetched and saved/updated successfully for user {user_id}.")

        flash('Google Classroom data fetched and saved successfully!', 'success')
        return redirect(url_for('partial_class') + '?google_classroom_connected=true')

    except Exception as e:
        db.session.rollback()
        flash(f'Error fetching Google Classroom data: {e}', 'danger')
        print(f"ERROR: Error fetching Google Classroom data for user {user_id}: {e}")
        return redirect(url_for('index'))

@main_bp.route('/google_classroom/check_status')
@login_required
def check_google_classroom_status():
    """Check if user has valid Google Classroom credentials"""
    user_id = session['user_id']
    google_creds = GoogleCredentials.query.filter_by(user_id=user_id).first()
    
    # Check if we're in demo mode
    if request.args.get('demo') == 'true':
        return jsonify({'connected': True, 'message': 'Demo Mode', 'demo': True})
    
    if not google_creds:
        return jsonify({'connected': False, 'message': 'Not connected'})
    
    # Check if credentials are valid
    creds_data = {
        'token': google_creds.token,
        'refresh_token': google_creds.refresh_token,
        'token_uri': google_creds.token_uri,
        'client_id': google_creds.client_id,
        'client_secret': google_creds.client_secret,
        'scopes': google_creds.scopes.split(',')
    }
    credentials = Credentials.from_authorized_user_info(creds_data)
    
    if not credentials.valid:
        if credentials.refresh_token:
            try:
                credentials.refresh(Request())
                # Update stored credentials
                google_creds.token = credentials.token
                db.session.commit()
                return jsonify({'connected': True, 'message': 'Connected'})
            except Exception as e:
                print(f"ERROR: Failed to refresh token: {e}")
                return jsonify({'connected': False, 'message': 'Token expired'})
        else:
            return jsonify({'connected': False, 'message': 'Token expired'})
    
    return jsonify({'connected': True, 'message': 'Connected'})

@main_bp.route('/google_classroom/fetch_courses')
@login_required
def fetch_google_classroom_courses():
    """Fetch courses from Google Classroom for the add lesson modal"""
    user_id = session['user_id']
    google_creds = GoogleCredentials.query.filter_by(user_id=user_id).first()
    
    # Check if we're in demo mode
    if request.args.get('demo') == 'true':
        # Return demo courses
        demo_courses = [
            {
                'id': 'demo_course_1',
                'name': 'Introduction to Computer Science',
                'description': 'Learn the fundamentals of computer science and programming',
                'section': 'CS101',
                'ownerId': 'demo@example.com',
                'creationTime': '2024-01-01T00:00:00Z',
                'updateTime': '2024-01-01T00:00:00Z'
            },
            {
                'id': 'demo_course_2',
                'name': 'Advanced Mathematics',
                'description': 'Advanced mathematical concepts and problem solving',
                'section': 'MATH201',
                'ownerId': 'demo@example.com',
                'creationTime': '2024-01-01T00:00:00Z',
                'updateTime': '2024-01-01T00:00:00Z'
            },
            {
                'id': 'demo_course_3',
                'name': 'Web Development Fundamentals',
                'description': 'Learn HTML, CSS, and JavaScript for web development',
                'section': 'WEB101',
                'ownerId': 'demo@example.com',
                'creationTime': '2024-01-01T00:00:00Z',
                'updateTime': '2024-01-01T00:00:00Z'
            }
        ]
        return jsonify({
            'success': True,
            'courses': demo_courses,
            'count': len(demo_courses),
            'demo': True
        })
    
    if not google_creds:
        return jsonify({'success': False, 'message': 'Not connected to Google Classroom'})
    
    # Check if credentials are valid
    creds_data = {
        'token': google_creds.token,
        'refresh_token': google_creds.refresh_token,
        'token_uri': google_creds.token_uri,
        'client_id': google_creds.client_id,
        'client_secret': google_creds.client_secret,
        'scopes': google_creds.scopes.split(',')
    }
    credentials = Credentials.from_authorized_user_info(creds_data)
    
    if not credentials.valid:
        if credentials.refresh_token:
            try:
                credentials.refresh(Request())
                google_creds.token = credentials.token
                db.session.commit()
            except Exception as e:
                print(f"ERROR: Failed to refresh token: {e}")
                return jsonify({'success': False, 'message': 'Token expired'})
        else:
            return jsonify({'success': False, 'message': 'Token expired'})
    
    try:
        service = build('classroom', 'v1', credentials=credentials)
        courses_results = service.courses().list(courseStates='ACTIVE').execute()
        courses = courses_results.get('courses', [])
        
        # Format courses for the UI
        formatted_courses = []
        for course in courses:
            formatted_courses.append({
                'id': course.get('id'),
                'name': course.get('name', 'Untitled Course'),
                'description': course.get('description', ''),
                'section': course.get('section', ''),
                'ownerId': course.get('ownerId', ''),
                'creationTime': course.get('creationTime', ''),
                'updateTime': course.get('updateTime', '')
            })
        
        return jsonify({
            'success': True,
            'courses': formatted_courses,
            'count': len(formatted_courses)
        })
        
    except Exception as e:
        print(f"ERROR: Failed to fetch courses: {e}")
        return jsonify({'success': False, 'message': f'Failed to fetch courses: {str(e)}'})

@main_bp.route('/google_classroom/import_course/<course_id>', methods=['POST'])
@login_required
def import_google_classroom_course_by_id(course_id):
    """Import a specific Google Classroom course as a lesson"""
    user_id = session['user_id']
    google_creds = GoogleCredentials.query.filter_by(user_id=user_id).first()
    
    if not google_creds:
        return jsonify({'success': False, 'message': 'Not connected to Google Classroom'})
    
    try:
        # Get course details from Google Classroom
        creds_data = {
            'token': google_creds.token,
            'refresh_token': google_creds.refresh_token,
            'token_uri': google_creds.token_uri,
            'client_id': google_creds.client_id,
            'client_secret': google_creds.client_secret,
            'scopes': google_creds.scopes.split(',')
        }
        credentials = Credentials.from_authorized_user_info(creds_data)
        
        if not credentials.valid:
            if credentials.refresh_token:
                credentials.refresh(Request())
                google_creds.token = credentials.token
                db.session.commit()
            else:
                return jsonify({'success': False, 'message': 'Token expired'})
        
        service = build('classroom', 'v1', credentials=credentials)
        course = service.courses().get(id=course_id).execute()
        
        # Create lesson from course data
        lesson_manager = LessonManager()
        lesson = lesson_manager.import_google_classroom_course_as_lesson(
            user_id=user_id,
            gc_course_data=course
        )
        
        return jsonify({
            'success': True,
            'message': 'Course imported successfully',
            'lesson_id': lesson.id,
            'lesson_title': lesson.title
        })
        
    except Exception as e:
        print(f"ERROR: Failed to import course: {e}")
        return jsonify({'success': False, 'message': f'Failed to import course: {str(e)}'})

@main_bp.route('/google_classroom/check_callback')
def check_google_classroom_callback():
    """Check if OAuth callback was successful"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'success': False, 'message': 'User not logged in'})
    
    google_creds = GoogleCredentials.query.filter_by(user_id=user_id).first()
    if google_creds:
        return jsonify({'success': True, 'message': 'Connected'})
    else:
        return jsonify({'success': False, 'message': 'Not connected'})

@main_bp.route('/api/google_classroom/lessons')
@login_required
def get_google_classroom_lessons():
    """Get Google Classroom courses as lessons for My Lessons page"""
    user_id = session['user_id']
    
    try:
        # Get imported Google Classroom data
        imported_data = ImportedData.query.filter_by(
            user_id=user_id, 
            platform='google_classroom_api'
        ).first()
        
        if not imported_data or 'courses' not in imported_data.data:
            return jsonify({'lessons': [], 'message': 'No Google Classroom data found'})
        
        courses = imported_data.data['courses']
        lessons = []
        
        for course in courses:
            # Create lesson object from Google Classroom course
            lesson = {
                'id': f"gc_{course['id']}",  # Prefix to avoid conflicts
                'title': course['name'],
                'description': course.get('section', ''),
                'external_id': course['id'],
                'external_url': course.get('alternateLink', ''),
                'source': 'google_classroom',
                'status': 'active',
                'color_theme': 1,  # Default color
                'created_at': datetime.utcnow().isoformat(),
                'updated_at': datetime.utcnow().isoformat(),
                
                # Google Classroom specific data
                'google_classroom_data': {
                    'course_id': course['id'],
                    'section': course.get('section', ''),
                    'alternate_link': course.get('alternateLink', ''),
                    'announcements_count': len(course.get('announcements', [])),
                    'coursework_count': len(course.get('courseWork', [])),
                    'materials_count': len(course.get('materials', [])),
                    'topics_count': len(course.get('topics', [])),
                    'students_count': len(course.get('students', [])),
                    'teachers_count': len(course.get('teachers', [])),
                    'attachments_count': len(course.get('all_attachments', [])),
                    'drive_files_count': len(course.get('drive_files', [])),
                    
                    # Grouped data by topics
                    'grouped_by_topic': course.get('grouped_by_topic', []),
                    
                    # Recent activity
                    'recent_announcements': course.get('announcements', [])[:5],  # Last 5
                    'recent_coursework': course.get('courseWork', [])[:5],  # Last 5
                    'recent_materials': course.get('materials', [])[:5],  # Last 5
                }
            }
            
            lessons.append(lesson)
        
        return jsonify({
            'lessons': lessons,
            'total_count': len(lessons),
            'message': f'Found {len(lessons)} Google Classroom courses'
        })
        
    except Exception as e:
        print(f"ERROR: Failed to get Google Classroom lessons for user {user_id}: {e}")
        return jsonify({'lessons': [], 'error': str(e)}), 500

@main_bp.route('/api/google_classroom/lesson/<course_id>')
@login_required
def get_google_classroom_lesson_detail(course_id):
    """Get detailed information for a specific Google Classroom course"""
    user_id = session['user_id']
    
    try:
        # Remove prefix if present
        if course_id.startswith('gc_'):
            course_id = course_id[3:]
        
        # Get imported Google Classroom data
        imported_data = ImportedData.query.filter_by(
            user_id=user_id, 
            platform='google_classroom_api'
        ).first()
        
        if not imported_data or 'courses' not in imported_data.data:
            return jsonify({'error': 'No Google Classroom data found'}), 404
        
        # Find the specific course
        course = None
        for c in imported_data.data['courses']:
            if c['id'] == course_id:
                course = c
                break
        
        if not course:
            return jsonify({'error': 'Course not found'}), 404
        
        # Return detailed course information
        return jsonify({
            'course': course,
            'message': 'Course details retrieved successfully'
        })
        
    except Exception as e:
        print(f"ERROR: Failed to get Google Classroom lesson detail for user {user_id}, course {course_id}: {e}")
        return jsonify({'error': str(e)}), 500

@main_bp.route('/api/google_classroom/sync')
@login_required
def sync_google_classroom_data():
    """Sync Google Classroom data and return updated lessons"""
    user_id = session['user_id']
    
    try:
        # Fetch fresh data from Google Classroom
        fetch_google_classroom_data()
        
        # Return updated lessons
        return get_google_classroom_lessons()
        
    except Exception as e:
        print(f"ERROR: Failed to sync Google Classroom data for user {user_id}: {e}")
        return jsonify({'error': str(e)}), 500

@main_bp.route('/api/google_classroom/import_course', methods=['POST'])
@login_required
def import_google_classroom_course_from_data():
    """Import a Google Classroom course as a lesson"""
    user_id = session['user_id']
    
    try:
        data = request.get_json()
        course_id = data.get('course_id')
        
        if not course_id:
            return jsonify({'success': False, 'message': 'Course ID is required'}), 400
        
        # Get imported Google Classroom data
        imported_data = ImportedData.query.filter_by(
            user_id=user_id, 
            platform='google_classroom_api'
        ).first()
        
        if not imported_data or 'courses' not in imported_data.data:
            return jsonify({'success': False, 'message': 'No Google Classroom data found'}), 404
        
        # Find the specific course
        course = None
        for c in imported_data.data['courses']:
            if str(c['id']) == str(course_id):
                course = c
                break
        
        if not course:
            return jsonify({'success': False, 'message': 'Course not found'}), 404
        
        # Check if course already imported
        existing_lesson = Lesson.query.filter_by(
            user_id=user_id,
            google_classroom_id=course_id
        ).first()
        
        if existing_lesson:
            return jsonify({'success': False, 'message': 'Course already imported as lesson'}), 400
        
        # Create new lesson from Google Classroom course
        lesson = lesson_manager.add_lesson(
            user_id=user_id,
            title=course['name'],
            description=course.get('section', ''),
            status='active',
            tags='Google Classroom',
            source_platform='google_classroom',
            google_classroom_id=course_id,
            author_name='Classroom Teacher',
            selected_color=1  # Default color
        )
        
        if lesson:
            # Update lesson with additional Google Classroom data
            lesson.external_url = course.get('alternateLink', '')
            lesson.external_id = course_id
            
            # Add Google Classroom specific metadata
            lesson.metadata = {
                'google_classroom_course_id': course_id,
                'section': course.get('section', ''),
                'announcements_count': len(course.get('announcements', [])),
                'coursework_count': len(course.get('courseWork', [])),
                'materials_count': len(course.get('materials', [])),
                'topics_count': len(course.get('topics', [])),
                'students_count': len(course.get('students', [])),
                'teachers_count': len(course.get('teachers', [])),
                'imported_at': datetime.utcnow().isoformat()
            }
            
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': f'Successfully imported "{course["name"]}" as lesson',
                'lesson_id': lesson.id
            })
        else:
            return jsonify({'success': False, 'message': 'Failed to create lesson'}), 500
            
    except Exception as e:
        db.session.rollback()
        print(f"ERROR: Failed to import Google Classroom course for user {user_id}: {e}")
        return jsonify({'success': False, 'message': f'Error importing course: {str(e)}'}), 500

@main_bp.route('/api/google_classroom/import_course_customized', methods=['POST'])
@login_required
def import_google_classroom_course_customized():
    """Import a Google Classroom course with custom settings"""
    user_id = session['user_id']
    
    try:
        data = request.get_json()
        course_id = data.get('course_id')
        course_data = data.get('course_data')
        
        if not course_id or not course_data:
            return jsonify({'success': False, 'message': 'Course ID and course data are required'}), 400
        
        # Get user preferences from form
        title = data.get('title', course_data.get('name', 'Untitled Lesson'))
        description = data.get('description', course_data.get('description', ''))
        status = data.get('status', 'active')
        color_theme = data.get('color_theme', 'blue')
        difficulty_level = data.get('difficulty_level', 'beginner')
        
        # Import options
        import_announcements = data.get('import_announcements', True)
        import_assignments = data.get('import_assignments', True)
        import_materials = data.get('import_materials', True)
        import_topics = data.get('import_topics', True)
        
        # Check if course already imported
        existing_lesson = Lesson.query.filter_by(
            user_id=user_id,
            external_id=course_id
        ).first()
        
        if existing_lesson:
            return jsonify({'success': False, 'message': 'Course already imported as lesson'}), 400
        
        # Create new lesson with custom settings
        lesson = lesson_manager.add_lesson(
            user_id=user_id,
            title=title,
            description=description,
            status=status,
            tags='Google Classroom',
            source_platform='google_classroom',
            google_classroom_id=course_id,
            author_name='Classroom Teacher',
            selected_color=1
        )
        
        if lesson:
            # Update lesson with additional Google Classroom data
            lesson.external_url = course_data.get('alternateLink', '')
            
            # Add Google Classroom specific metadata
            lesson.metadata = {
                'google_classroom_course_id': course_id,
                'section': course_data.get('section', ''),
                'announcements_count': len(course_data.get('announcements', [])),
                'coursework_count': len(course_data.get('courseWork', [])),
                'materials_count': len(course_data.get('materials', [])),
                'topics_count': len(course_data.get('topics', [])),
                'students_count': len(course_data.get('students', [])),
                'teachers_count': len(course_data.get('teachers', [])),
                'imported_at': datetime.utcnow().isoformat(),
                'import_options': {
                    'announcements': import_announcements,
                    'assignments': import_assignments,
                    'materials': import_materials,
                    'topics': import_topics
                }
            }
            
            # Import course content based on user preferences
            sections_created = 0
            
            if import_announcements and course_data.get('announcements'):
                for announcement in course_data['announcements']:
                    section = lesson_manager.add_section(
                        lesson.id,
                        title=f"Announcement: {announcement.get('text', 'Announcement')[:50]}...",
                        content=announcement.get('description', announcement.get('text', '')),
                        section_type='announcement',
                        order_index=sections_created + 1
                    )
                    if section:
                        sections_created += 1
            
            if import_assignments and course_data.get('courseWork'):
                for assignment in course_data['courseWork']:
                    section = lesson_manager.add_section(
                        lesson.id,
                        title=f"Assignment: {assignment.get('title', 'Assignment')}",
                        content=assignment.get('description', ''),
                        section_type='assignment',
                        order_index=sections_created + 1
                    )
                    if section:
                        sections_created += 1
            
            if import_materials and course_data.get('materials'):
                for material in course_data['materials']:
                    section = lesson_manager.add_section(
                        lesson.id,
                        title=f"Material: {material.get('title', 'Material')}",
                        content=material.get('description', ''),
                        section_type='material',
                        order_index=sections_created + 1
                    )
                    if section:
                        sections_created += 1
            
            if import_topics and course_data.get('topics'):
                for topic in course_data['topics']:
                    section = lesson_manager.add_section(
                        lesson.id,
                        title=f"Topic: {topic.get('name', 'Topic')}",
                        content=topic.get('description', ''),
                        section_type='topic',
                        order_index=sections_created + 1
                    )
                    if section:
                        sections_created += 1
            
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': f'Successfully imported "{title}" as lesson with {sections_created} sections',
                'lesson_id': lesson.id,
                'sections_count': sections_created
            })
        else:
            return jsonify({'success': False, 'message': 'Failed to create lesson'}), 500
            
    except Exception as e:
        db.session.rollback()
        print(f"ERROR: Failed to import customized Google Classroom course for user {user_id}: {e}")
        return jsonify({'success': False, 'message': f'Error importing course: {str(e)}'}), 500

@main_bp.route('/api/google_classroom/auto_import_all', methods=['POST'])
@login_required
def auto_import_all_google_classroom_courses():
    """Automatically import all Google Classroom courses with default settings"""
    user_id = session['user_id']
    
    try:
        # Get imported Google Classroom data
        imported_data = ImportedData.query.filter_by(
            user_id=user_id, 
            platform='google_classroom_api'
        ).first()
        
        if not imported_data or 'courses' not in imported_data.data:
            return jsonify({'success': False, 'message': 'No Google Classroom data found'}), 404
        
        courses = imported_data.data['courses']
        if not courses:
            return jsonify({'success': False, 'message': 'No courses to import'}), 404
        
        # Filter out already imported courses
        unimported_courses = []
        for course in courses:
            existing_lesson = Lesson.query.filter_by(
                user_id=user_id,
                external_id=course.get('id')
            ).first()
            if not existing_lesson:
                unimported_courses.append(course)
        
        if not unimported_courses:
            return jsonify({'success': False, 'message': 'All courses already imported'}), 400
        
        lessons_created = 0
        total_sections = 0
        
        for course in unimported_courses:
            try:
                # Create lesson with default settings
                lesson = lesson_manager.add_lesson(
                    user_id=user_id,
                    title=course.get('name', 'Untitled Lesson'),
                    description=course.get('description', course.get('section', '')),
                    status='active',
                    tags='Google Classroom',
                    source_platform='google_classroom',
                    google_classroom_id=course.get('id'),
                    author_name='Classroom Teacher',
                    selected_color=1
                )
                
                if lesson:
                    # Update lesson with additional Google Classroom data
                    lesson.external_url = course.get('alternateLink', '')
                    
                    # Add Google Classroom specific metadata
                    lesson.metadata = {
                        'google_classroom_course_id': course.get('id'),
                        'section': course.get('section', ''),
                        'announcements_count': len(course.get('announcements', [])),
                        'coursework_count': len(course.get('courseWork', [])),
                        'materials_count': len(course.get('materials', [])),
                        'topics_count': len(course.get('topics', [])),
                        'students_count': len(course.get('students', [])),
                        'teachers_count': len(course.get('teachers', [])),
                        'imported_at': datetime.utcnow().isoformat(),
                        'auto_imported': True
                    }
                    
                    # Import all content automatically
                    sections_created = 0
                    
                    # Import announcements
                    if course.get('announcements'):
                        for announcement in course['announcements']:
                            section = lesson_manager.add_section(
                                lesson.id,
                                title=f"Announcement: {announcement.get('text', 'Announcement')[:50]}...",
                                content=announcement.get('description', announcement.get('text', '')),
                                type='announcement',
                                order=sections_created + 1
                            )
                            if section:
                                sections_created += 1
                    
                    # Import assignments
                    if course.get('courseWork'):
                        for assignment in course['courseWork']:
                            section = lesson_manager.add_section(
                                lesson.id,
                                title=f"Assignment: {assignment.get('title', 'Assignment')}",
                                content=assignment.get('description', ''),
                                type='assignment',
                                order=sections_created + 1
                            )
                            if section:
                                sections_created += 1
                    
                    # Import materials
                    if course.get('materials'):
                        for material in course['materials']:
                            section = lesson_manager.add_section(
                                lesson.id,
                                title=f"Material: {material.get('title', 'Material')}",
                                content=material.get('description', ''),
                                type='material',
                                order=sections_created + 1
                            )
                            if section:
                                sections_created += 1
                    
                    # Import topics
                    if course.get('topics'):
                        for topic in course['topics']:
                            section = lesson_manager.add_section(
                                lesson.id,
                                title=f"Topic: {topic.get('name', 'Topic')}",
                                content=topic.get('description', ''),
                                type='topic',
                                order=sections_created + 1
                            )
                            if section:
                                sections_created += 1
                    
                    lessons_created += 1
                    total_sections += sections_created
                    
            except Exception as e:
                print(f"ERROR: Failed to import course {course.get('name', 'Unknown')}: {e}")
                continue
        
        db.session.commit()
        
        if lessons_created > 0:
            return jsonify({
                'success': True,
                'message': f'Successfully auto-imported {lessons_created} courses with {total_sections} total sections',
                'lessons_created': lessons_created,
                'sections_created': total_sections
            })
        else:
            return jsonify({'success': False, 'message': 'No courses were imported'}), 500
            
    except Exception as e:
        db.session.rollback()
        print(f"ERROR: Failed to auto-import Google Classroom courses for user {user_id}: {e}")
        return jsonify({'success': False, 'message': f'Error auto-importing courses: {str(e)}'}), 500

@main_bp.route('/api/google_classroom/bulk_import', methods=['POST'])
@login_required
def bulk_import_google_classroom_courses_from_data():
    """Import all Google Classroom courses as lessons"""
    user_id = session['user_id']
    
    try:
        # Get imported Google Classroom data
        imported_data = ImportedData.query.filter_by(
            user_id=user_id, 
            platform='google_classroom_api'
        ).first()
        
        if not imported_data or 'courses' not in imported_data.data:
            return jsonify({'success': False, 'message': 'No Google Classroom data found'}), 404
        
        courses = imported_data.data['courses']
        imported_count = 0
        errors = []
        
        # Get existing Google Classroom lesson IDs
        existing_gc_lesson_ids = set()
        existing_lessons = Lesson.query.filter_by(user_id=user_id).all()
        for lesson in existing_lessons:
            if lesson.google_classroom_id:
                existing_gc_lesson_ids.add(str(lesson.google_classroom_id))
        
        for course in courses:
            course_id = str(course['id'])
            
            # Skip if already imported
            if course_id in existing_gc_lesson_ids:
                continue
            
            try:
                # Create new lesson
                lesson = lesson_manager.add_lesson(
                    user_id=user_id,
                    title=course['name'],
                    description=course.get('section', ''),
                    status='active',
                    tags='Google Classroom',
                    source_platform='google_classroom',
                    google_classroom_id=course_id,
                    author_name='Classroom Teacher',
                    selected_color=1
                )
                
                if lesson:
                    # Update lesson with additional data
                    lesson.external_url = course.get('alternateLink', '')
                    lesson.external_id = course_id
                    
                    # Add metadata
                    lesson.metadata = {
                        'google_classroom_course_id': course_id,
                        'section': course.get('section', ''),
                        'announcements_count': len(course.get('announcements', [])),
                        'coursework_count': len(course.get('courseWork', [])),
                        'materials_count': len(course.get('materials', [])),
                        'topics_count': len(course.get('topics', [])),
                        'students_count': len(course.get('students', [])),
                        'teachers_count': len(course.get('teachers', [])),
                        'imported_at': datetime.utcnow().isoformat()
                    }
                    
                    imported_count += 1
                else:
                    errors.append(f"Failed to create lesson for {course['name']}")
                    
            except Exception as e:
                errors.append(f"Error importing {course['name']}: {str(e)}")
                continue
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Successfully imported {imported_count} courses as lessons',
            'imported_count': imported_count,
            'errors': errors
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"ERROR: Failed to bulk import Google Classroom courses for user {user_id}: {e}")
        return jsonify({'success': False, 'message': f'Error bulk importing: {str(e)}'}), 500