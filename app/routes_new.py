"""
Main routes for OOP architecture.
Clean routes that integrate with the new OOP system.
"""

from flask import Blueprint, render_template, request, redirect, url_for, session, g, jsonify, current_app
from functools import wraps
from .middleware.auth_middleware import login_required
from .services import UserService, LessonService, NoteService, TaskService
from app import db
# from app.core.files import Files  # Removed - not needed for simple MVC
from werkzeug.utils import secure_filename
from sqlalchemy import text
import os
import time

# Create main blueprint
main_bp = Blueprint('main', __name__)

# Import login_required from middleware
from app.middleware.auth_middleware import login_required

def login_required_web(f):
    """Decorator to require login for web routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

@main_bp.before_request
def load_logged_in_user():
    """Load logged in user for web routes"""
    user_id = session.get('user_id')
    if user_id:
        try:
            user_service = UserService()
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
        return redirect(url_for('main.dashboard'))
    
    # Check if user just connected Google Classroom
    google_connected = request.args.get('google_classroom_connected') == 'true'
    return render_template('base.html', google_connected=google_connected, user=None)

@main_bp.route('/dashboard')
def dashboard():
    """Dashboard page."""
    # Simple check - if no user_id in session, redirect to login
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    # Get user from session
    user_id = session.get('user_id')
    if user_id:
        try:
            user_service = UserService()
            user = user_service.get_user_by_id(user_id)
            return render_template('base.html', user=user)
        except Exception:
            return redirect(url_for('auth.login'))
    else:
        return redirect(url_for('auth.login'))

@main_bp.route('/partial/dashboard')
def partial_dashboard():
    """Dashboard partial for SPA."""
    # Simple check - if no user_id in session, return 401
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    return render_template('dashboard_fragment.html', user=g.user)

@main_bp.route('/partial/class')
def partial_class():
    """Class/Lessons partial"""
    # Simple check - if no user_id in session, return 401
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        print(f"🔍 partial_class: Loading lessons for user {g.user.id}")
        lesson_service = LessonService()
        lessons = lesson_service.get_lessons_by_user(g.user.id)
        print(f"✅ Found {len(lessons)} lessons")
        
        # Sort lessons: Favorites first (pinned), then by created_at desc
        # Key explanation: (is_favorite, created_at) with reverse=True
        # - True > False, so favorites come first
        # - Within each group, newer dates come first
        lessons = sorted(lessons, key=lambda x: (x.is_favorite, x.created_at), reverse=True)
        print(f"📌 Sorted: Favorites first, then newest")
        
        # Debug sorting
        if lessons:
            fav_count = sum(1 for l in lessons if l.is_favorite)
            print(f"   Favorites: {fav_count}, Regular: {len(lessons) - fav_count}")
        
        # Debug: print first lesson
        if lessons:
            first = lessons[0]
            print(f"📝 First lesson: id={first.id}, title={first.title}, status={first.status}, is_favorite={first.is_favorite}")
        else:
            print("⚠️ No lessons found!")
        
        # Check Microsoft Teams connection status
        microsoft_teams_connected = session.get('microsoft_teams_connected', False)
        microsoft_teams_data = session.get('microsoft_teams_data', None)
        
        return render_template('class_fragment.html', 
                             lessons=lessons, 
                             user=g.user,
                             google_classroom_connected=False,  # TODO: implement real check
                             microsoft_teams_connected=microsoft_teams_connected,
                             microsoft_teams_data=microsoft_teams_data)
    except Exception as e:
        print(f"❌ Error loading lessons: {e}")
        import traceback
        traceback.print_exc()
        return render_template('class_fragment.html', 
                             lessons=[], 
                             user=g.user,
                             google_classroom_connected=False,
                             microsoft_teams_connected=False,
                             microsoft_teams_data=None)

@main_bp.route('/debug/lessons')
def debug_lessons():
    """Debug route to check lessons data"""
    # Simple check - if no user_id in session, return 401
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        lesson_service = LessonService()
        lessons = lesson_service.get_lessons_by_user(g.user.id)
        
        lessons_data = []
        for lesson in lessons:
            lessons_data.append({
                'id': lesson.id,
                'title': lesson.title,
                'description': lesson.description,
                'status': str(lesson.status),
                'color_theme': lesson.color_theme,
                'author_name': lesson.author_name,
                'created_at': str(lesson.created_at) if lesson.created_at else None,
                'is_favorite': lesson.is_favorite
            })
        
        return jsonify({
            'success': True,
            'user_id': g.user.id,
            'lessons_count': len(lessons),
            'lessons': lessons_data
        })
    except Exception as e:
        import traceback
        return jsonify({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500

@main_bp.route('/partial/class/add', methods=['POST'])
def add_lesson():
    """Add new lesson"""
    # Simple check - if no user_id in session, return 401
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        # from app.domain.entities.lesson import LessonStatus, DifficultyLevel
        lesson_service = LessonService()
        
        # Get form data
        title = request.form.get('title')
        description = request.form.get('description')
        status = request.form.get('status', 'not_started')
        author_name = request.form.get('author_name')
        tags = request.form.get('tags', '')
        selected_color = request.form.get('selectedColor', '1')
        difficulty = request.form.get('difficulty_level', 'beginner')
        duration = request.form.get('estimated_duration')
        
        print(f"📝 Creating lesson: title={title}, status={status}, difficulty={difficulty}, duration={duration}")
        
        if not title:
            return jsonify({'success': False, 'message': 'Title is required'}), 400
        
        # Convert color to integer
        try:
            color_theme = int(selected_color)
        except:
            color_theme = 1
        
        # Convert difficulty to string
        difficulty_map = {
            'beginner': 'beginner',
            'intermediate': 'intermediate',
            'advanced': 'advanced'
        }
        difficulty_level = difficulty_map.get(difficulty, 'beginner')
        
        # Convert duration to int
        estimated_duration = None
        if duration:
            try:
                estimated_duration = int(duration)
            except:
                pass
        
        # Create lesson using OOP service
        lesson = lesson_service.create_lesson(
            user_id=g.user.id,
            title=title,
            description=description or ''
        )
        
        # Update status using direct SQL (since the model uses enums)
        from app import db
        from sqlalchemy import text
        
        # Map status string to enum value
        status_map = {
            'not_started': 'not_started',
            'in_progress': 'in_progress', 
            'completed': 'completed',
            'archived': 'archived',
            'active': 'not_started'  # fallback
        }
        status_value = status_map.get(status, 'not_started')
        
        # Update status and tags
        db.session.execute(
            text("UPDATE lesson SET status = :status WHERE id = :lesson_id"),
            {"status": status_value, "lesson_id": lesson.id}
        )
        db.session.commit()
        
        print(f"✅ Lesson created: id={lesson.id}, status={status_value}, tags={tags}")
        
        return jsonify({
            'success': True,
            'message': 'Lesson created successfully',
            'lesson_id': lesson.id
        })
        
    except Exception as e:
        print(f"❌ Error creating lesson: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': str(e)}), 500

@main_bp.route('/class/<lesson_id>')
def view_class_detail(lesson_id):
    """View class detail page with tabs"""
    # Simple check - if no user_id in session, return 401
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        lesson_service = LessonService()
        lesson = lesson_service.get_lesson_by_id(lesson_id)
        
        if not lesson:
            return jsonify({'error': 'Lesson not found'}), 404
        
        return render_template('class_detail.html', 
                             lesson=lesson, 
                             user=g.user)
        
    except Exception as e:
        print(f"Error loading class detail: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@main_bp.route('/class/<lesson_id>/stream-notes')
def stream_notes(lesson_id):
    """Load stream notes template"""
    # Simple check - if no user_id in session, return 401
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        lesson_service = LessonService()
        lesson = lesson_service.get_lesson_by_id(lesson_id)
        if not lesson:
            return jsonify({'error': 'Lesson not found'}), 404
        if lesson.user_id != g.user.id:
            return jsonify({'error': 'Unauthorized'}), 403
        return render_template('class_detail/_stream_notes.html', lesson=lesson, user=g.user)
    except Exception as e:
        print(f"Error loading stream notes: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@main_bp.route('/partial/class/<lesson_id>')
def view_lesson_detail(lesson_id):
    """View lesson detail page (legacy route)"""
    # Simple check - if no user_id in session, return 401
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        from app import db
        lesson_service = LessonService()
        
        # Get lesson by ID
        lesson = lesson_service.get_lesson_by_id(lesson_id)
        if not lesson:
            return '<div class="alert alert-danger">Lesson not found or no permission.</div>', 404
        
        # Get sections using direct SQL query to avoid model import conflicts
        sections = []
        try:
            # Query sections directly from database without importing the model
            section_query = db.session.execute(
                db.text("""
                    SELECT id, lesson_id, type, title, content, files, 
                           assignment_due, created_at, updated_at, sort_order
                    FROM lesson_section 
                    WHERE lesson_id = :lesson_id 
                    ORDER BY sort_order ASC, created_at ASC
                """),
                {'lesson_id': lesson_id}
            )
            
            # Convert to dict objects for template compatibility
            for row in section_query:
                sections.append({
                    'id': row[0],
                    'lesson_id': row[1],
                    'type': row[2],
                    'title': row[3],
                    'content': row[4],
                    'files': row[5],
                    'assignment_due': row[6],
                    'created_at': row[7],
                    'updated_at': row[8],
                    'sort_order': row[9]
                })
        except Exception as e:
            print(f"Warning: Could not load sections: {e}")
            sections = []
        
        # Get notes using direct SQL query
        notes = []
        try:
            note_query = db.session.execute(
                db.text("""
                    SELECT id, title, content, tags, created_at, updated_at
                    FROM note 
                    WHERE lesson_id = :lesson_id AND user_id = :user_id
                    ORDER BY created_at DESC
                """),
                {'lesson_id': lesson_id, 'user_id': g.user.id}
            )
            
            for row in note_query:
                notes.append({
                    'id': row[0],
                    'title': row[1],
                    'content': row[2],
                    'tags': row[3],
                    'created_at': row[4],
                    'updated_at': row[5]
                })
        except Exception as e:
            print(f"Warning: Could not load notes: {e}")
            notes = []
        
        # Prepare lesson_summary (for compatibility with template)
        lesson_summary = {
            'notes': notes,
            'sections': sections
        }
        
        # Handle Google Classroom data if needed
        if hasattr(lesson, 'source_platform') and lesson.source_platform == 'google_classroom':
            import json
            try:
                lesson.announcements = json.loads(lesson.announcements_data) if hasattr(lesson, 'announcements_data') and lesson.announcements_data else []
            except Exception:
                lesson.announcements = []
            try:
                lesson.grouped_by_topic = json.loads(lesson.topics_data) if hasattr(lesson, 'topics_data') and lesson.topics_data else []
            except Exception:
                lesson.grouped_by_topic = []
            try:
                lesson.roster = json.loads(lesson.roster_data) if hasattr(lesson, 'roster_data') and lesson.roster_data else {}
            except Exception:
                lesson.roster = {}
            try:
                lesson.all_attachments = json.loads(lesson.attachments_data) if hasattr(lesson, 'attachments_data') and lesson.attachments_data else []
            except Exception:
                lesson.all_attachments = []
        
        return render_template('lessons/_detail.html', 
                             lesson=lesson, 
                             sections=sections, 
                             lesson_summary=lesson_summary,
                             user=g.user)
    except Exception as e:
        print(f"Error viewing lesson detail: {e}")
        import traceback
        traceback.print_exc()
        return f'<div class="alert alert-danger">Error loading lesson: {str(e)}</div>', 500

@main_bp.route('/partial/class/<lesson_id>/favorite', methods=['POST'])
def toggle_lesson_favorite(lesson_id):
    """Toggle lesson favorite status"""
    # Simple check - if no user_id in session, return 401
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        lesson_service = LessonService()
        
        # Get current lesson
        lesson = lesson_service.get_lesson_by_id(lesson_id)
        if not lesson:
            return jsonify({'success': False, 'message': 'Lesson not found'}), 404
        
        # Toggle favorite
        new_favorite_status = not lesson.is_favorite
        
        # Update using direct SQL
        from app import db
        from sqlalchemy import text
        
        db.session.execute(
            text("UPDATE lesson SET is_favorite = :fav WHERE id = :lesson_id AND user_id = :user_id"),
            {"fav": new_favorite_status, "lesson_id": lesson_id, "user_id": g.user.id}
        )
        db.session.commit()
        
        print(f"✅ Toggled favorite for lesson {lesson_id}: {new_favorite_status}")
        
        return jsonify({
            'success': True,
            'message': 'Favorite toggled successfully',
            'is_favorite': new_favorite_status
        })
    except Exception as e:
        print(f"❌ Error toggling favorite: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': str(e)}), 500

@main_bp.route('/partial/class/<lesson_id>/delete', methods=['POST'])
def delete_lesson(lesson_id):
    """Delete a lesson"""
    # Simple check - if no user_id in session, return 401
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        lesson_service = LessonService()
        lesson_service.delete_lesson(lesson_id, g.user.id)
        
        return jsonify({
            'success': True,
            'message': 'Lesson deleted successfully'
        })
    except Exception as e:
        print(f"Error deleting lesson: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': str(e)}), 500

@main_bp.route('/partial/note')
def partial_note():
    """Note partial"""
    # Simple check - if no user_id in session, return 401
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        note_service = NoteService()
        notes = note_service.get_user_notes(g.user.id)
        notes = _enrich_notes_with_status_and_files(notes)
        return render_template('note_fragment.html', notes=notes, user=g.user)
    except Exception as e:
        return render_template('note_fragment.html', notes=[], user=g.user)


@main_bp.route('/partial/note/editor')
@main_bp.route('/partial/note/editor/<note_id>')
def partial_note_editor(note_id=None):
    """Full-page Note editor UX (list + editor pane) as a fragment.

    - When loaded without note_id, selects the first note (if exists)
    - Right pane will fetch content lazily via /partial/note/<id>/data
    """
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401

    try:
        note_service = NoteService()
        notes = note_service.get_user_notes(g.user.id)
        notes = _enrich_notes_with_status_and_files(notes)

        # Choose default selected note id if not provided
        selected_id = note_id
        if not selected_id and notes:
            first = notes[0]
            selected_id = getattr(first, 'id', None)

        return render_template('notes/note_editor_fragment.html', notes=notes, selected_note_id=selected_id, user=g.user)
    except Exception as e:
        return render_template('notes/note_editor_fragment.html', notes=[], selected_note_id=None, user=g.user)


@main_bp.route('/notes')
def notes_page():
    """Full page Notes view with CSS/JS via base layout."""
    # Simple check - if no user_id in session, return 401
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    # Render base and let SPA load note partial by default
    return render_template('base.html', user=g.user, initial_page='note')


@main_bp.route('/partial/note/add', methods=['GET', 'POST'])
def partial_note_add():
    """Create a new note from the partial UI."""
    # Simple check - if no user_id in session, return 401
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    # GET: Return the add note fragment
    if request.method == 'GET':
        return render_template('notes/note_add_fragment.html')
    
    # POST: Create the note
    try:
        title = request.form.get('title')
        content = request.form.get('content')
        tags_str = request.form.get('tags')
        status = request.form.get('status')
        note_type_str = request.form.get('note_type')
        is_public_raw = request.form.get('is_public')
        # Convert note_type and is_public
        note_type = note_type_str if note_type_str else 'general'
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

        note_service = NoteService()
        note = note_service.create_note(
            user_id=g.user.id,
            lesson_id=None,
            title=title,
            content=content
        )

        # Note created successfully - no need for additional DB operations

        # Handle file uploads (image/file)
        try:
            uploaded_image = request.files.get('image')
            uploaded_file = request.files.get('file')
            _save_note_uploads(note.id, uploaded_image, uploaded_file, g.user.id)
        except Exception:
            db.session.rollback()

        # If AJAX request, return JSON
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify(success=True, note_id=getattr(note, 'id', None), message='Note created successfully')

        # Non-AJAX fallback: redirect to full notes page (with CSS/JS)
        return redirect(url_for('main.notes_page'))
    except Exception as e:
        return jsonify(success=False, message=str(e)), 500


@main_bp.route('/partial/note/<note_id>/delete', methods=['POST'])
def partial_note_delete(note_id):
    """Delete a note and return updated fragment."""
    # Simple check - if no user_id in session, return 401
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        note_service = NoteService()
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
def partial_note_edit(note_id):
    """Update a note and return JSON for SPA."""
    # Simple check - if no user_id in session, return 401
    if 'user_id' not in session:
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
            kwargs['note_type'] = note_type_str
        if is_public_raw is not None:
            kwargs['is_public'] = str(is_public_raw).lower() in ['1', 'true', 'on', 'yes']

        note_service = NoteService()
        updated_note = note_service.update_note(
            note_id=note_id,
            **kwargs
        )

        # Note updated successfully

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
def partial_note_data(note_id):
    """Fetch latest note data from DB for editing (without incrementing views)."""
    # Simple check - if no user_id in session, return 401
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        note_service = NoteService()
        note = note_service.get_note_by_id(note_id)
        if not note:
            return jsonify(success=False, message='Note not found or permission denied'), 404

        data = {
            'id': note.id,
            'title': note.title,
            'content': note.content,
            'created_at': note.created_at.isoformat() if note.created_at else None,
            'status': 'pending',  # Default status
            'external_link': '',  # Default external link
            'tags': '',  # Default tags
            'note_type': 'text',  # Default note type
            'is_public': False,  # Default is_public
            'files': []  # Default files array
        }

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
def partial_track():
    """Track/Progress Tracking partial"""
    # Simple check - if no user_id in session, return 401
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        # For now, just return the tracking fragment
        # Later we can add task service integration
        return render_template('track_fragment.html', user=g.user)
    except Exception as e:
        return render_template('track_fragment.html', user=g.user)

@main_bp.route('/partial/pomodoro')
def partial_pomodoro():
    """Pomodoro timer partial"""
    # Simple check - if no user_id in session, return 401
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        # Return the pomodoro fragment
        return render_template('pomodoro_fragment.html', user=g.user)
    except Exception as e:
        return render_template('pomodoro_fragment.html', user=g.user)

@main_bp.route('/partial/dev')
def partial_dev():
    """Development partial"""
    # Simple check - if no user_id in session, return 401
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    return render_template('dev_fragment.html', user=g.user)

# API endpoints for AJAX calls
@main_bp.route('/api/lessons/data')
def lessons_data():
    """Get lessons data for AJAX"""
    # Simple check - if no user_id in session, return 401
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        lesson_service = LessonService()
        lessons = lesson_service.get_lessons_by_user(g.user.id)
        return jsonify({
            'success': True,
            'data': [{
                'id': lesson.id,
                'title': lesson.title,
                'description': lesson.description,
                'status': getattr(lesson, 'status', 'not_started'),
                'created_at': lesson.created_at.isoformat() if lesson.created_at else None
            } for lesson in lessons]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@main_bp.route('/api/notes/data')
def notes_data():
    """Get notes data for AJAX"""
    # Simple check - if no user_id in session, return 401
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        note_service = NoteService()
        notes = note_service.get_user_notes(g.user.id)
        return jsonify({
            'success': True,
            'data': [{
                'id': note.id,
                'title': note.title,
                'content': note.content,
                'created_at': note.created_at.isoformat() if note.created_at else None
            } for note in notes]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@main_bp.route('/api/tasks/data')
def tasks_data():
    """Get tasks data for AJAX"""
    # Simple check - if no user_id in session, return 401
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        task_service = TaskService()
        tasks = task_service.get_user_tasks(g.user.id)
        return jsonify({
            'success': True,
            'data': [task.to_dict() for task in tasks]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Additional API endpoints for lesson detail pages
@main_bp.route('/class/<lesson_id>/notes-list')
def lesson_notes_list(lesson_id):
    """Get notes list for a specific lesson."""
    # Simple check - if no user_id in session, return 401
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        note_service = NoteService()
        notes = note_service.get_notes_by_user(g.user.id)  # Get all notes for user
        
        # Return HTML fragment instead of JSON
        return render_template('notes/notes_list_fragment.html', notes=notes, user=g.user)
    except Exception as e:
        return render_template('notes/notes_list_fragment.html', notes=[], user=g.user)

@main_bp.route('/class/<lesson_id>/notes/create', methods=['POST'])
def lesson_notes_create(lesson_id):
    """Create a note for a specific lesson."""
    # Simple check - if no user_id in session, return 401
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        title = request.form.get('title', '')
        content = request.form.get('content', '')
        
        note_service = NoteService()
        note = note_service.create_note(
            user_id=g.user.id,
            lesson_id=lesson_id,
            title=title,
            content=content
        )
        
        return jsonify({
            'success': True,
            'message': 'Note created successfully',
            'data': {
                'id': note.id,
                'title': note.title,
                'content': note.content
            }
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@main_bp.route('/class/<lesson_id>/notes/<note_id>')
def lesson_note_detail(lesson_id, note_id):
    """Get a specific note for editing."""
    # Simple check - if no user_id in session, return 401
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        note_service = NoteService()
        note = note_service.get_note_by_id(note_id)
        
        return jsonify({
            'success': True,
            'data': {
                'id': note.id,
                'title': note.title,
                'content': note.content,
                'created_at': note.created_at.isoformat() if note.created_at else None
            }
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@main_bp.route('/class/<lesson_id>/notes/<note_id>/update', methods=['POST'])
def lesson_note_update(lesson_id, note_id):
    """Update a specific note."""
    # Simple check - if no user_id in session, return 401
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        title = request.form.get('title', '')
        content = request.form.get('content', '')
        
        note_service = NoteService()
        note = note_service.update_note(note_id, title=title, content=content)
        
        return jsonify({
            'success': True,
            'message': 'Note updated successfully',
            'data': {
                'id': note.id,
                'title': note.title,
                'content': note.content
            }
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@main_bp.route('/class/<lesson_id>/classwork')
def lesson_classwork(lesson_id):
    """Get classwork content for a lesson."""
    # Simple check - if no user_id in session, return 401
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        lesson_service = LessonService()
        lesson = lesson_service.get_lesson_by_id(lesson_id)
        
        return jsonify({
            'success': True,
            'data': {
                'id': lesson.id,
                'title': lesson.title,
                'description': lesson.description,
                'classwork': []  # Empty for now
            }
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@main_bp.route('/classwork/lessons/<lesson_id>/dashboard')
def classwork_dashboard(lesson_id):
    """Get classwork dashboard for a lesson."""
    # Simple check - if no user_id in session, return 401
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        return jsonify({
            'success': True,
            'data': {
                'lesson_id': lesson_id,
                'total_tasks': 0,
                'completed_tasks': 0,
                'progress': 0
            }
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@main_bp.route('/classwork/lessons/<lesson_id>/materials')
def classwork_materials(lesson_id):
    """Get classwork materials for a lesson."""
    # Simple check - if no user_id in session, return 401
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        return jsonify({
            'success': True,
            'data': []
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@main_bp.route('/classwork/lessons/<lesson_id>/tasks')
def classwork_tasks(lesson_id):
    """Get classwork tasks for a lesson."""
    # Simple check - if no user_id in session, return 401
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        return jsonify({
            'success': True,
            'data': []
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
