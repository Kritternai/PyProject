"""
Note Web Routes
Web routes for note fragments and pages (non-API)
"""
# app/routes/note_web_routes.py
from flask import Blueprint, render_template, request, redirect, url_for, session, g, jsonify, current_app
from functools import wraps
from ..services import NoteService
from werkzeug.utils import secure_filename
from app import db
import os
import time

# Create blueprint
note_web_bp = Blueprint('note_web', __name__)


@note_web_bp.before_request
def load_logged_in_user():
    """Load logged in user for note web routes"""
    from ..services import UserService
    user_id = session.get('user_id')
    if user_id:
        try:
            user_service = UserService()
            g.user = user_service.get_user_by_id(user_id)
        except:
            g.user = None
    else:
        g.user = None


def login_required_web(f):
    """Decorator to require login for web routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function


def _register_routes(note_web_bp):
    """Register all note web routes to the blueprint."""
    # ============================================
    # NOTE FRAGMENTS & PAGES
    # ============================================

    @note_web_bp.route('/notes')
    def notes_page():
        """Full page Notes view with CSS/JS via base layout"""
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        
        # Render base and let SPA load note partial by default
        return render_template('base.html', user=g.user, initial_page='note')


    @note_web_bp.route('/partial/note')
    def partial_note():
        """Note fragment with backend-calculated statistics"""
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        
        try:
            note_service = NoteService()
            notes = note_service.get_user_notes(g.user.id)
            notes = _enrich_notes_with_status_and_files(notes)
            
            # Calculate statistics in Python (backend)
            stats = {
                'total': len(notes),
                'completed': 0,
                'images': 0,
                'docs': 0
            }
            
            # Count statistics
            for note in notes:
                # Count completed notes
                if hasattr(note, 'status') and note.status == 'completed':
                    stats['completed'] += 1
                
                # Count images and documents
                if hasattr(note, 'files') and note.files:
                    for file in note.files:
                        if file and hasattr(file, 'file_type'):
                            if file.file_type == 'image':
                                stats['images'] += 1
                            elif file.file_type in ['document', 'pdf']:
                                stats['docs'] += 1
            
            return render_template('note_fragment.html', notes=notes, stats=stats, user=g.user)
        except Exception as e:
            return render_template('note_fragment.html', notes=[], stats={'total': 0, 'completed': 0, 'images': 0, 'docs': 0}, user=g.user)


    # ============================================
    # NOTE CRUD OPERATIONS (Web)
    # ============================================

    @note_web_bp.route('/partial/note/add', methods=['GET'])
    def partial_note_add_form():
        """Show add note form"""
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        
        return render_template('notes/note_add_fragment.html', user=g.user)


    @note_web_bp.route('/partial/note/editor', methods=['GET'])
    @note_web_bp.route('/partial/note/editor/<note_id>', methods=['GET'])
    def partial_note_editor(note_id=None):
        """Show note editor page (split view with list + editor)"""
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        
        try:
            note_service = NoteService()
            notes = note_service.get_user_notes(g.user.id)
            notes = _enrich_notes_with_status_and_files(notes)
            
            return render_template('notes/note_editor_fragment.html', 
                                 notes=notes, 
                                 user=g.user,
                                 selected_note_id=note_id)
        except Exception as e:
            return render_template('notes/note_editor_fragment.html', 
                                 notes=[], 
                                 user=g.user,
                                 selected_note_id=note_id)


    @note_web_bp.route('/partial/note/add', methods=['POST'])
    def partial_note_add():
        """Create a new note from the partial UI"""
        if 'user_id' not in session:
            return jsonify({'error': 'Not authenticated'}), 401
        
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
                title=title,
                content=content,
                lesson_id=None,  # Standalone note (not linked to any lesson/class)
                status=status,
                tags=tags,
                note_type=note_type,
                is_public=is_public,
                external_link=external_link
            )

            # Handle file uploads (multiple files from new UI)
            try:
                # Handle new file upload format (files[0], files[1], etc.)
                uploaded_files = []
                for key in request.files:
                    if key.startswith('files['):
                        uploaded_files.append(request.files[key])
                
                # Fallback to old format (image, file)
                if not uploaded_files:
                    uploaded_image = request.files.get('image')
                    uploaded_file = request.files.get('file')
                    if uploaded_image:
                        uploaded_files.append(uploaded_image)
                    if uploaded_file:
                        uploaded_files.append(uploaded_file)
                
                # Save all uploaded files
                for file in uploaded_files:
                    _save_single_file(note.id, file, g.user.id)
                    
            except Exception as e:
                print(f"File upload error: {e}")
                db.session.rollback()

            # If AJAX request, return JSON
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                # Return updated HTML
                notes = note_service.get_user_notes(g.user.id)
                notes = _enrich_notes_with_status_and_files(notes)
                
                # Calculate statistics for the returned HTML
                stats = {
                    'total': len(notes),
                    'completed': 0,
                    'images': 0,
                    'docs': 0
                }
                
                # Count statistics
                for note in notes:
                    if hasattr(note, 'status') and note.status == 'completed':
                        stats['completed'] += 1
                    if hasattr(note, 'files') and note.files:
                        for file in note.files:
                            if file and hasattr(file, 'file_type'):
                                if file.file_type == 'image':
                                    stats['images'] += 1
                                elif file.file_type in ['document', 'pdf']:
                                    stats['docs'] += 1
                
                html = render_template('note_fragment.html', notes=notes, stats=stats, user=g.user)
                return jsonify(success=True, html=html)

            # Non-AJAX fallback: redirect
            return redirect(url_for('note_web.notes_page'))
        except Exception as e:
            return jsonify(success=False, message=str(e)), 500


    @note_web_bp.route('/partial/note/<note_id>/delete', methods=['POST'])
    def partial_note_delete(note_id):
        """Delete a note and return updated fragment"""
        if 'user_id' not in session:
            return jsonify({'error': 'Not authenticated'}), 401
        
        try:
            note_service = NoteService()
            deleted = note_service.delete_note(note_id, g.user.id)
            if not deleted:
                return jsonify(success=False, message='Note not found or permission denied'), 404
            
            # Return updated fragment for AJAX
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                notes = note_service.get_user_notes(g.user.id)
                notes = _enrich_notes_with_status_and_files(notes)
                
                # Calculate statistics for the returned HTML
                stats = {
                    'total': len(notes),
                    'completed': 0,
                    'images': 0,
                    'docs': 0
                }
                
                # Count statistics
                for note in notes:
                    if hasattr(note, 'status') and note.status == 'completed':
                        stats['completed'] += 1
                    if hasattr(note, 'files') and note.files:
                        for file in note.files:
                            if file and hasattr(file, 'file_type'):
                                if file.file_type == 'image':
                                    stats['images'] += 1
                                elif file.file_type in ['document', 'pdf']:
                                    stats['docs'] += 1
                
                return render_template('note_fragment.html', notes=notes, stats=stats, user=g.user)
            return redirect(url_for('note_web.notes_page'))
        except Exception as e:
            return jsonify(success=False, message=str(e)), 500


    @note_web_bp.route('/partial/note/<note_id>/edit', methods=['POST'])
    def partial_note_edit(note_id):
        """Update a note and return JSON for SPA"""
        if 'user_id' not in session:
            return jsonify({'error': 'Not authenticated'}), 401
        
        try:
            title = request.form.get('title')
            content = request.form.get('content')
            tags_str = request.form.get('tags')
            status = request.form.get('status')
            note_type_str = request.form.get('note_type')
            is_public_raw = request.form.get('is_public')
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

            # If AJAX request, return JSON
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                # Handle file uploads/removals here if needed
                try:
                    # Handle new file upload format (files[0], files[1], etc.)
                    uploaded_files = []
                    for key in request.files:
                        if key.startswith('files['):
                            uploaded_files.append(request.files[key])
                    
                    # Fallback to old format (image, file)
                    if not uploaded_files:
                        uploaded_image = request.files.get('image')
                        uploaded_file = request.files.get('file')
                        if uploaded_image:
                            uploaded_files.append(uploaded_image)
                        if uploaded_file:
                            uploaded_files.append(uploaded_file)
                    
                    # Save all uploaded files
                    for file in uploaded_files:
                        _save_single_file(note_id, file, g.user.id)
                        
                except Exception as e:
                    print(f"File upload error in edit: {e}")
                    db.session.rollback()

                return jsonify(success=True)

            # Non-AJAX fallback
            return redirect(url_for('note_web.notes_page'))
        except Exception as e:
            return jsonify(success=False, message=str(e)), 500


    @note_web_bp.route('/partial/note/<note_id>/data', methods=['GET'])
    def partial_note_data(note_id):
        """Fetch latest note data from DB for editing"""
        if 'user_id' not in session:
            return jsonify({'error': 'Not authenticated'}), 401
        
        try:
            note_service = NoteService()
            note = note_service.get_note_by_id(note_id)
            if not note:
                return jsonify(success=False, message='Note not found or permission denied'), 404

            # Parse tags from JSON
            tags = []
            if note.tags:
                try:
                    import json
                    tags = json.loads(note.tags) if isinstance(note.tags, str) else note.tags
                except (json.JSONDecodeError, TypeError):
                    tags = []

            # Get files from file system
            note_files = _get_note_files_from_fs(note.id)
            
            data = {
                'id': note.id,
                'title': note.title,
                'content': note.content,
                'created_at': note.created_at.isoformat() if note.created_at else None,
                'status': note.status or 'pending',
                'external_link': note.external_link or '',
                'tags': ', '.join(tags) if tags else '',
                'note_type': note.note_type or 'text',
                'is_public': note.is_public or False,
                'files': note_files
            }

            return jsonify(success=True, data=data)
        except Exception as e:
            return jsonify(success=False, message=str(e)), 500


# Register routes
_register_routes(note_web_bp)


# ============================================
# HELPER FUNCTIONS
# ============================================

def _enrich_notes_with_status_and_files(notes):
    """Attach legacy fields (status, external_link) and files to domain notes"""
    try:
        if not notes:
            return notes
        note_ids = [getattr(n, 'id', None) for n in notes]
        note_ids = [nid for nid in note_ids if nid]
        if not note_ids:
            return notes

        # Build parameterized IN clause
        from sqlalchemy import text
        params = {f'id{i}': nid for i, nid in enumerate(note_ids)}
        placeholders = ", ".join([f":id{i}" for i in range(len(note_ids))])

        rows = db.session.execute(
            text(f"SELECT id, status, external_link FROM note WHERE id IN ({placeholders})")
            , params
        ).fetchall()
        meta_by_id = {row[0]: {'status': row[1], 'external_link': row[2]} for row in rows}

        # Get files for each note from file system
        for n in notes:
            meta = meta_by_id.get(getattr(n, 'id', None))
            if meta is not None:
                setattr(n, 'status', meta.get('status'))
                setattr(n, 'external_link', meta.get('external_link'))
            
            # Parse tags from JSON string to list
            if hasattr(n, 'tags') and n.tags:
                try:
                    import json
                    if isinstance(n.tags, str):
                        parsed_tags = json.loads(n.tags)
                        if isinstance(parsed_tags, list):
                            setattr(n, 'tags', parsed_tags)
                        else:
                            setattr(n, 'tags', [])
                    else:
                        setattr(n, 'tags', n.tags if isinstance(n.tags, list) else [])
                except (json.JSONDecodeError, TypeError):
                    # Fallback: try to split by comma if it's a string
                    if isinstance(n.tags, str):
                        setattr(n, 'tags', [tag.strip() for tag in n.tags.split(',') if tag.strip()])
                    else:
                        setattr(n, 'tags', [])
            else:
                setattr(n, 'tags', [])
            
            # Get files for this note from file system
            note_files = _get_note_files_from_fs(n.id)
            setattr(n, 'files', note_files)
        return notes
    except Exception:
        return notes


def _get_note_files_from_fs(note_id):
    """Get files for a note from file system"""
    try:
        files = []
        static_dir = current_app.static_folder
        uploads_dir = os.path.join(static_dir, 'uploads', 'notes')
        
        # Look for note-specific directory
        note_dir = os.path.join(uploads_dir, str(note_id))
        if os.path.exists(note_dir):
            for filename in os.listdir(note_dir):
                file_path = os.path.join(note_dir, filename)
                if os.path.isfile(file_path):
                    # Determine file type from extension
                    ext = os.path.splitext(filename)[1].lower()
                    file_type = 'document'
                    
                    if ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']:
                        file_type = 'image'
                    elif ext in ['.pdf']:
                        file_type = 'pdf'
                    elif ext in ['.doc', '.docx', '.txt', '.rtf']:
                        file_type = 'document'
                    
                    # Create file object
                    file_obj = type('File', (), {})()
                    file_obj.file_path = f"uploads/notes/{note_id}/{filename}"
                    file_obj.filename = filename
                    file_obj.file_type = file_type
                    file_obj.size = os.path.getsize(file_path)
                    
                    files.append(file_obj)
        
        return files
    except Exception as e:
        print(f"Error getting files for note {note_id}: {e}")
        return []


def _save_single_file(note_id, file, user_id):
    """Save a single uploaded file to static/uploads"""
    if not file or not getattr(file, 'filename', ''):
        return False
        
    static_dir = current_app.static_folder
    subdir = os.path.join('uploads', 'notes', str(user_id))
    target_dir = os.path.join(static_dir, subdir)
    os.makedirs(target_dir, exist_ok=True)

    filename = secure_filename(file.filename)
    name, ext = os.path.splitext(filename)
    unique_name = f"{int(time.time())}_{secure_filename(name)}{ext}"
    abs_path = os.path.join(target_dir, unique_name)
    file.save(abs_path)
    
    db.session.commit()
    return True


def _save_note_uploads(note_id, image_file, other_file, user_id):
    """Save uploaded files to static/uploads (legacy function)"""
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
        saved_any = True

    _save(image_file, 'image')
    _save(other_file, 'document')
    if saved_any:
        db.session.commit()

