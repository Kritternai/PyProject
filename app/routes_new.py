"""
Main routes for OOP architecture.
Clean routes that integrate with the new OOP system.
"""

from flask import Blueprint, render_template, request, redirect, url_for, session, g, jsonify, current_app
from functools import wraps
from .presentation.middleware.auth_middleware import login_required, get_current_user
from .infrastructure.di.container import get_service
from .domain.interfaces.services.user_service import UserService
from .domain.interfaces.services.lesson_service import LessonService
from .domain.interfaces.services.note_service import NoteService
from .domain.entities.note import NoteType
from .domain.interfaces.services.task_service import TaskService
from app import db
from app.core.files import Files
from werkzeug.utils import secure_filename
from sqlalchemy import text
import os
import time

# Create main blueprint
main_bp = Blueprint('main', __name__)

def login_required_web(f):
    """Decorator to require login for web routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('register.login'))
        return f(*args, **kwargs)
    return decorated_function

@main_bp.before_request
def load_logged_in_user():
    """Load logged in user for web routes"""
    user_id = session.get('user_id')
    if user_id:
        try:
            user_service = get_service(UserService)
            g.user = user_service.get_user_by_id(user_id)
        except:
            g.user = None
    else:
        g.user = None

@main_bp.route('/')
@main_bp.route('/index')
def index():
    """Main index page."""
    # Check if user is logged in
    if 'user_id' in session:
        return redirect(url_for('register.dashboard'))
    
    # Check if user just connected Google Classroom
    google_connected = request.args.get('google_classroom_connected') == 'true'
    return render_template('base.html', google_connected=google_connected)

@main_bp.route('/dashboard')
@login_required_web
def dashboard():
    """Dashboard page."""
    if not g.user:
        return redirect(url_for('register.login'))
    return render_template('base.html', user=g.user)

@main_bp.route('/partial/dashboard')
@login_required_web
def partial_dashboard():
    """Dashboard partial for SPA."""
    if not g.user:
        return jsonify({'error': 'Not authenticated'}), 401
    return render_template('dashboard_fragment.html', user=g.user)

@main_bp.route('/partial/class')
@login_required_web
def partial_class():
    """Class/Lessons partial"""
    if not g.user:
        return jsonify({'error': 'Not authenticated'}), 401
    try:
        lesson_service = get_service(LessonService)
        lessons = lesson_service.get_user_lessons(g.user.id)
        return render_template('class_fragment.html', lessons=lessons, user=g.user)
    except Exception as e:
        return render_template('class_fragment.html', lessons=[], user=g.user)

@main_bp.route('/partial/note')
@login_required_web
def partial_note():
    """Note partial"""
    if not g.user:
        return jsonify({'error': 'Not authenticated'}), 401
    try:
        note_service = get_service(NoteService)
        notes = note_service.get_user_notes(g.user.id)
        notes = _enrich_notes_with_status_and_files(notes)
        return render_template('note_fragment.html', notes=notes, user=g.user)
    except Exception as e:
        return render_template('note_fragment.html', notes=[], user=g.user)


@main_bp.route('/notes')
@login_required_web
def notes_page():
    """Full page Notes view with CSS/JS via base layout."""
    if not g.user:
        return redirect(url_for('register.login'))
    # Render base and let SPA load note partial by default
    return render_template('base.html', user=g.user, initial_page='note')


@main_bp.route('/partial/note/add', methods=['POST'])
@login_required_web
def partial_note_add():
    """Create a new note from the partial UI."""
    if not g.user:
        return jsonify({'error': 'Not authenticated'}), 401
    try:
        title = request.form.get('title')
        content = request.form.get('content')
        tags_str = request.form.get('tags')
        status = request.form.get('status')
        note_type_str = request.form.get('note_type')
        is_public_raw = request.form.get('is_public')
        # Convert note_type and is_public
        note_type = None
        if note_type_str:
            try:
                note_type = NoteType(note_type_str)
            except Exception:
                note_type = None
        is_public = False
        if is_public_raw is not None:
            is_public = str(is_public_raw).lower() in ['1', 'true', 'on', 'yes']
        external_link = request.form.get('external_link')

        if not title or not content:
            return jsonify(success=False, message='Title and content are required.'), 400

        # Parse comma-separated tags into list
        tags = None
        if tags_str:
            tags = [t.strip() for t in tags_str.split(',') if t.strip()]

        note_service = get_service(NoteService)
        note = note_service.create_note(
            user_id=g.user.id,
            title=title,
            content=content,
            note_type=note_type or NoteType.TEXT,
            tags=tags,
            is_public=is_public
        )

        # Persist additional fields (status, external_link) directly to DB (legacy columns)
        try:
            if status is not None or external_link is not None:
                db.session.execute(
                    text("""
                        UPDATE note
                        SET status = COALESCE(:status, status),
                            external_link = COALESCE(:external_link, external_link)
                        WHERE id = :note_id AND user_id = :user_id
                    """),
                    {
                        'status': status,
                        'external_link': external_link,
                        'note_id': note.id,
                        'user_id': g.user.id
                    }
                )
                db.session.commit()
        except Exception:
            db.session.rollback()

        # Handle file uploads (image/file)
        try:
            uploaded_image = request.files.get('image')
            uploaded_file = request.files.get('file')
            _save_note_uploads(note.id, uploaded_image, uploaded_file, g.user.id)
        except Exception:
            db.session.rollback()

        # If AJAX request, return JSON so client can refresh fragment
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            # Return updated HTML so SPA can swap content immediately
            notes = note_service.get_user_notes(g.user.id)
            notes = _enrich_notes_with_status_and_files(notes)
            html = render_template('note_fragment.html', notes=notes, user=g.user)
            return jsonify(success=True, html=html)

        # Non-AJAX fallback: redirect to full notes page (with CSS/JS)
        return redirect(url_for('main.notes_page'))
    except Exception as e:
        return jsonify(success=False, message=str(e)), 500


@main_bp.route('/partial/note/<note_id>/delete', methods=['POST'])
@login_required_web
def partial_note_delete(note_id):
    """Delete a note and return updated fragment."""
    if not g.user:
        return jsonify({'error': 'Not authenticated'}), 401
    try:
        note_service = get_service(NoteService)
        deleted = note_service.delete_note(note_id, g.user.id)
        if not deleted:
            return jsonify(success=False, message='Note not found or permission denied'), 404
        # Return updated fragment for AJAX; redirect for non-AJAX
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            notes = note_service.get_user_notes(g.user.id)
            notes = _enrich_notes_with_status_and_files(notes)
            return render_template('note_fragment.html', notes=notes, user=g.user)
        return redirect(url_for('main.notes_page'))
    except Exception as e:
        return jsonify(success=False, message=str(e)), 500


@main_bp.route('/partial/note/<note_id>/edit', methods=['POST'])
@login_required_web
def partial_note_edit(note_id):
    """Update a note and return JSON for SPA."""
    if not g.user:
        return jsonify({'error': 'Not authenticated'}), 401
    try:
        title = request.form.get('title')
        content = request.form.get('content')
        tags_str = request.form.get('tags')
        status = request.form.get('status')
        note_type_str = request.form.get('note_type')
        is_public_raw = request.form.get('is_public')
        # Removal lists for existing files/images
        remove_image_ids = request.form.getlist('remove_image_ids')
        remove_file_ids = request.form.getlist('remove_file_ids')
        external_link = request.form.get('external_link')

        # Only pass fields that are provided
        kwargs = {}
        if title is not None:
            kwargs['title'] = title
        if content is not None:
            kwargs['content'] = content
        if tags_str is not None:
            kwargs['tags'] = [t.strip() for t in tags_str.split(',') if t.strip()]
        if note_type_str is not None and note_type_str != '':
            try:
                kwargs['note_type'] = NoteType(note_type_str)
            except Exception:
                pass
        if is_public_raw is not None:
            kwargs['is_public'] = str(is_public_raw).lower() in ['1', 'true', 'on', 'yes']

        note_service = get_service(NoteService)
        updated_note = note_service.update_note(
            note_id=note_id,
            user_id=g.user.id,
            **kwargs
        )

        # Update additional fields (status, external_link) directly
        try:
            if status is not None or external_link is not None:
                db.session.execute(
                    text("""
                        UPDATE note
                        SET status = COALESCE(:status, status),
                            external_link = COALESCE(:external_link, external_link)
                        WHERE id = :note_id AND user_id = :user_id
                    """),
                    {
                        'status': status,
                        'external_link': external_link,
                        'note_id': note_id,
                        'user_id': g.user.id
                    }
                )
                db.session.commit()
        except Exception:
            db.session.rollback()

        # If AJAX request, return JSON for SPA handler
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            # Handle file removals
            try:
                ids_to_remove = list(filter(None, (remove_image_ids or []))) + list(filter(None, (remove_file_ids or [])))
                if ids_to_remove:
                    files = Files.query.filter(Files.id.in_(ids_to_remove), Files.user_id == str(g.user.id), Files.note_id == str(note_id)).all()
                    static_dir = current_app.static_folder
                    for f in files:
                        try:
                            abs_path = os.path.join(static_dir, f.file_path)
                            if os.path.exists(abs_path):
                                os.remove(abs_path)
                        except Exception:
                            pass
                        db.session.delete(f)
                    db.session.commit()
            except Exception:
                db.session.rollback()

            # Handle new uploads
            try:
                uploaded_image = request.files.get('image')
                uploaded_file = request.files.get('file')
                _save_note_uploads(note_id, uploaded_image, uploaded_file, g.user.id)
            except Exception:
                db.session.rollback()

            return jsonify(success=True)

        # Non-AJAX fallback: redirect to full notes page (with CSS/JS)
        return redirect(url_for('main.notes_page'))
    except Exception as e:
        return jsonify(success=False, message=str(e)), 500


@main_bp.route('/partial/note/<note_id>/data', methods=['GET'])
@login_required_web
def partial_note_data(note_id):
    """Fetch latest note data from DB for editing (without incrementing views)."""
    if not g.user:
        return jsonify({'error': 'Not authenticated'}), 401
    try:
        note_service = get_service(NoteService)
        note = note_service.get_note_by_id(note_id, g.user.id)
        if not note:
            return jsonify(success=False, message='Note not found or permission denied'), 404

        data = note.to_dict()

        # Attach legacy fields (status, external_link)
        try:
            row = db.session.execute(
                text("""
                    SELECT status, external_link
                    FROM note
                    WHERE id = :note_id AND user_id = :user_id
                """),
                { 'note_id': note_id, 'user_id': g.user.id }
            ).fetchone()
            if row:
                data['status'] = row[0]
                data['external_link'] = row[1]
        except Exception:
            pass

        # Attach files (filter by user_id for security)
        try:
            files = Files.query.filter(
                Files.note_id == note_id,
                Files.user_id == str(g.user.id)
            ).all()
            data['files'] = [
                {
                    'id': f.id,
                    'file_name': f.file_name,
                    'file_path': f.file_path,
                    'file_type': f.file_type,
                    'mime_type': f.mime_type,
                    'file_size': getattr(f, 'file_size', 0)
                } for f in files
            ]
        except Exception as e:
            print(f"Error fetching files for note {note_id}: {e}")
            data['files'] = []

        return jsonify(success=True, data=data)
    except Exception as e:
        return jsonify(success=False, message=str(e)), 500

@main_bp.route('/partial/track')
@login_required_web
def partial_track():
    """Track/Progress Tracking partial"""
    if not g.user:
        return jsonify({'error': 'Not authenticated'}), 401
    try:
        # For now, just return the tracking fragment
        # Later we can add task service integration
        return render_template('track_fragment.html', user=g.user)
    except Exception as e:
        return render_template('track_fragment.html', user=g.user)

@main_bp.route('/partial/pomodoro')
@login_required_web
def partial_pomodoro():
    """Pomodoro timer partial"""
    if not g.user:
        return jsonify({'error': 'Not authenticated'}), 401
    try:
        # Return the pomodoro fragment
        return render_template('pomodoro_fragment.html', user=g.user)
    except Exception as e:
        return render_template('pomodoro_fragment.html', user=g.user)

@main_bp.route('/partial/dev')
@login_required_web
def partial_dev():
    """Development partial"""
    if not g.user:
        return jsonify({'error': 'Not authenticated'}), 401
    return render_template('dev_fragment.html', user=g.user)

# API endpoints for AJAX calls
@main_bp.route('/api/lessons/data')
@login_required_web
def lessons_data():
    """Get lessons data for AJAX"""
    if not g.user:
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        lesson_service = get_service(LessonService)
        lessons = lesson_service.get_user_lessons(g.user.id)
        return jsonify({
            'success': True,
            'data': [lesson.to_dict() for lesson in lessons]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@main_bp.route('/api/notes/data')
@login_required_web
def notes_data():
    """Get notes data for AJAX"""
    if not g.user:
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        note_service = get_service(NoteService)
        notes = note_service.get_user_notes(g.user.id)
        return jsonify({
            'success': True,
            'data': [note.to_dict() for note in notes]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@main_bp.route('/api/tasks/data')
@login_required_web
def tasks_data():
    """Get tasks data for AJAX"""
    if not g.user:
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        task_service = get_service(TaskService)
        tasks = task_service.get_user_tasks(g.user.id)
        return jsonify({
            'success': True,
            'data': [task.to_dict() for task in tasks]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Legacy routes for backward compatibility - removed to prevent redirect loops
# All authentication routes are now handled by register_bp


def _enrich_notes_with_status_and_files(notes):
    """Attach legacy fields (status, external_link) and files to domain notes for rendering."""
    try:
        if not notes:
            return notes
        note_ids = [getattr(n, 'id', None) for n in notes]
        note_ids = [nid for nid in note_ids if nid]
        if not note_ids:
            return notes

        # Build parameterized IN clause
        params = {f'id{i}': nid for i, nid in enumerate(note_ids)}
        placeholders = ", ".join([f":id{i}" for i in range(len(note_ids))])

        rows = db.session.execute(
            text(f"SELECT id, status, external_link FROM note WHERE id IN ({placeholders})")
            , params
        ).fetchall()
        meta_by_id = {row[0]: {'status': row[1], 'external_link': row[2]} for row in rows}

        files = Files.query.filter(Files.note_id.in_(note_ids)).all()
        files_by_note = {}
        for f in files:
            files_by_note.setdefault(f.note_id, []).append(f)

        for n in notes:
            meta = meta_by_id.get(getattr(n, 'id', None))
            if meta is not None:
                setattr(n, 'status', meta.get('status'))
                setattr(n, 'external_link', meta.get('external_link'))
            setattr(n, 'files', files_by_note.get(getattr(n, 'id', None), []))
        return notes
    except Exception:
        return notes


def _save_note_uploads(note_id, image_file, other_file, user_id):
    """Save uploaded files to static/uploads and create Files records."""
    saved_any = False
    static_dir = current_app.static_folder
    subdir = os.path.join('uploads', 'notes', str(user_id))
    target_dir = os.path.join(static_dir, subdir)
    os.makedirs(target_dir, exist_ok=True)

    def _save(fs, file_type_hint):
        nonlocal saved_any
        if not fs or not getattr(fs, 'filename', ''):
            return
        filename = secure_filename(fs.filename)
        name, ext = os.path.splitext(filename)
        unique_name = f"{int(time.time())}_{secure_filename(name)}{ext}"
        abs_path = os.path.join(target_dir, unique_name)
        fs.save(abs_path)
        rel_path = os.path.join(subdir, unique_name).replace('\\', '/')
        file_type = 'image' if (file_type_hint == 'image' or (fs.mimetype or '').startswith('image/')) else 'document'
        size = os.path.getsize(abs_path)
        file_row = Files(
            user_id=str(user_id),
            note_id=str(note_id),
            file_name=filename,
            file_path=rel_path,
            file_type=file_type,
            file_size=size,
            mime_type=fs.mimetype
        )
        db.session.add(file_row)
        saved_any = True

    _save(image_file, 'image')
    _save(other_file, 'document')
    if saved_any:
        db.session.commit()
