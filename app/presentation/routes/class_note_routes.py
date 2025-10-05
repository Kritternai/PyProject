"""
Class Note Routes - Integration with Note System
"""
from flask import Blueprint, request, jsonify, render_template, g
from sqlalchemy import text
from app import db
from app.infrastructure.di.container import get_service
from app.application.services.note_service import NoteService

class_note_bp = Blueprint('class_note', __name__, url_prefix='/class')

def login_required_web(f):
    """Decorator for web routes that require login"""
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not g.user:
            return jsonify({'error': 'Authentication required'}), 401
        return f(*args, **kwargs)
    return decorated_function

@class_note_bp.route('/<lesson_id>/notes-list', methods=['GET'])
@login_required_web
def get_notes_list(lesson_id):
    """Get notes list for iPhone-style interface"""
    try:
        print(f"🔧 Loading notes list for lesson: {lesson_id}")
        
        # Get notes that belong to this class ONLY
        notes_query = text("""
            SELECT n.id, n.title, n.content, n.status, n.created_at, n.updated_at
            FROM note n
            WHERE n.user_id = :user_id 
            AND n.lesson_id = :lesson_id
            ORDER BY n.updated_at DESC
        """)
        
        result = db.session.execute(notes_query, {
            'user_id': g.user.id,
            'lesson_id': lesson_id
        })
        
        notes = []
        for row in result:
            note = {
                'id': row.id,
                'title': row.title,
                'content': row.content,
                'status': row.status,
                'created_at': row.created_at,
                'updated_at': row.updated_at
            }
            notes.append(note)
        
        print(f"🔧 Found {len(notes)} notes for lesson {lesson_id}")
        return render_template('class_detail/_notes_list.html', notes=notes, lesson_id=lesson_id)
        
    except Exception as e:
        print(f"Error loading notes list: {e}")
        return jsonify({'error': str(e)}), 500

@class_note_bp.route('/<lesson_id>/notes', methods=['GET'])
@login_required_web
def get_class_notes(lesson_id):
    """Get notes for a specific class - shows both class notes and general notes"""
    try:
        print(f"🔧 Loading class notes for lesson: {lesson_id}")
        print(f"🔧 User: {g.user.id}")
        
        # Get notes that belong to this class ONLY (not general notes)
        notes_query = text("""
            SELECT n.*, 
                   COUNT(f.id) as file_count,
                   GROUP_CONCAT(f.file_path) as file_paths,
                   GROUP_CONCAT(f.file_type) as file_types
            FROM note n
            LEFT JOIN note_file f ON n.id = f.note_id
            WHERE n.user_id = :user_id 
            AND n.lesson_id = :lesson_id
            GROUP BY n.id
            ORDER BY n.created_at DESC
        """)
        
        result = db.session.execute(notes_query, {
            'user_id': g.user.id,
            'lesson_id': lesson_id
        })
        
        print(f"🔧 Query executed for lesson: {lesson_id}")
        
        notes = []
        for row in result:
            note = {
                'id': row.id,
                'title': row.title,
                'content': row.content,
                'status': row.status,
                'tags': row.tags,
                'created_at': row.created_at,
                'updated_at': row.updated_at,
                'file_count': row.file_count or 0,
                'files': [],
                'is_class_note': True  # All notes in this view are class notes
            }
            
            # Parse file information
            if row.file_paths and row.file_types:
                paths = row.file_paths.split(',')
                types = row.file_types.split(',')
                for i, (path, file_type) in enumerate(zip(paths, types)):
                    if path and file_type:
                        note['files'].append({
                            'file_path': path,
                            'file_type': file_type
                        })
            
            notes.append(note)
        
        print(f"🔧 Found {len(notes)} notes for lesson {lesson_id}")
        for note in notes:
            print(f"   - {note['title']} (ID: {note['id']})")
        
        return render_template('class_detail/_notes_grid.html', notes=notes, lesson_id=lesson_id)
        
    except Exception as e:
        print(f"Error loading class notes: {e}")
        return jsonify({'error': str(e)}), 500

@class_note_bp.route('/<lesson_id>/notes/create', methods=['POST'])
@login_required_web
def create_class_note(lesson_id):
    """Create a new note for a class and sync with main note system"""
    try:
        print(f"🔧 Creating class note for lesson: {lesson_id}")
        print(f"🔧 User: {g.user.id}")
        print(f"🔧 Form data: {dict(request.form)}")
        
        title = request.form.get('title', '').strip()
        content = request.form.get('content', '').strip()
        status = request.form.get('status', 'pending')
        tags = request.form.get('tags', '').strip()
        
        print(f"🔧 Parsed data: title='{title}', content='{content}', status='{status}', tags='{tags}'")
        
        if not title or not content:
            print("❌ Missing title or content")
            return jsonify({'error': 'Title and content are required'}), 400
        
        # Create note in database with lesson_id
        import uuid
        note_id = str(uuid.uuid4())
        note_query = text("""
            INSERT INTO note (id, user_id, lesson_id, title, content, status, tags, created_at, updated_at)
            VALUES (:note_id, :user_id, :lesson_id, :title, :content, :status, :tags, datetime('now'), datetime('now'))
        """)
        
        db.session.execute(note_query, {
            'note_id': note_id,
            'user_id': g.user.id,
            'lesson_id': lesson_id,
            'title': title,
            'content': content,
            'status': status,
            'tags': tags
        })
        
        # Handle file upload if present
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename:
                # Save file and create note_file record
                import os
                from werkzeug.utils import secure_filename
                
                filename = secure_filename(file.filename)
                file_path = f"uploads/notes/{filename}"
                
                # Create directory if not exists
                os.makedirs(os.path.dirname(f"app/static/{file_path}"), exist_ok=True)
                
                # Save file
                file.save(f"app/static/{file_path}")
                
                # Use the note_id we already created
                
                # Insert file record
                file_id = str(uuid.uuid4())
                file_query = text("""
                    INSERT INTO note_file (id, note_id, file_path, file_type, created_at)
                    VALUES (:file_id, :note_id, :file_path, 'image', datetime('now'))
                """)
                
                db.session.execute(file_query, {
                    'file_id': file_id,
                    'note_id': note_id,
                    'file_path': file_path
                })
        
        db.session.commit()
        
        # Also create a general note (without lesson_id) for main note system
        general_note_id = str(uuid.uuid4())
        general_note_query = text("""
            INSERT INTO note (id, user_id, lesson_id, title, content, status, tags, created_at, updated_at)
            VALUES (:note_id, :user_id, NULL, :title, :content, :status, :tags, datetime('now'), datetime('now'))
        """)
        
        db.session.execute(general_note_query, {
            'note_id': general_note_id,
            'user_id': g.user.id,
            'title': title,
            'content': content,
            'status': status,
            'tags': tags
        })
        
        print(f"✅ Created class note: {note_id}")
        print(f"✅ Created general note: {general_note_id}")
        
        # Handle file upload for general note if present
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename:
                import os
                from werkzeug.utils import secure_filename
                
                filename = secure_filename(file.filename)
                file_path = f"uploads/notes/{filename}"
                
                # Create directory if not exists
                os.makedirs(os.path.dirname(f"app/static/{file_path}"), exist_ok=True)
                
                # Save file
                file.save(f"app/static/{file_path}")
                
                # Insert file record for general note
                general_file_id = str(uuid.uuid4())
                general_file_query = text("""
                    INSERT INTO note_file (id, note_id, file_path, file_type, created_at)
                    VALUES (:file_id, :note_id, :file_path, 'image', datetime('now'))
                """)
                
                db.session.execute(general_file_query, {
                    'file_id': general_file_id,
                    'note_id': general_note_id,
                    'file_path': file_path
                })
        
        db.session.commit()
        
        # Return updated notes grid
        return get_class_notes(lesson_id)
        
    except Exception as e:
        print(f"Error creating class note: {e}")
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@class_note_bp.route('/<lesson_id>/notes/<note_id>', methods=['GET'])
@login_required_web
def get_single_note(lesson_id, note_id):
    """Get a single note for editing"""
    try:
        print(f"🔧 Loading single note: {note_id} for lesson: {lesson_id}")
        
        # Get the specific note
        note_query = text("""
            SELECT n.id, n.title, n.content, n.status, n.created_at, n.updated_at
            FROM note n
            WHERE n.id = :note_id 
            AND n.user_id = :user_id 
            AND n.lesson_id = :lesson_id
        """)
        
        result = db.session.execute(note_query, {
            'note_id': note_id,
            'user_id': g.user.id,
            'lesson_id': lesson_id
        }).fetchone()
        
        if result:
            note = {
                'id': result.id,
                'title': result.title,
                'content': result.content,
                'status': result.status,
                'created_at': result.created_at,
                'updated_at': result.updated_at
            }
            print(f"✅ Note loaded: {note['title']}")
            return jsonify(note)
        else:
            print(f"❌ Note not found: {note_id}")
            return jsonify({'error': 'Note not found'}), 404
            
    except Exception as e:
        print(f"Error loading single note: {e}")
        return jsonify({'error': str(e)}), 500

@class_note_bp.route('/<lesson_id>/notes/<note_id>/update', methods=['POST'])
@login_required_web
def update_class_note(lesson_id, note_id):
    """Update a class note"""
    try:
        title = request.form.get('title', '').strip()
        content = request.form.get('content', '').strip()
        status = request.form.get('status', 'pending')
        tags = request.form.get('tags', '').strip()
        
        if not title or not content:
            return jsonify({'error': 'Title and content are required'}), 400
        
        # Update note
        update_query = text("""
            UPDATE note 
            SET title = :title, content = :content, status = :status, tags = :tags, updated_at = datetime('now')
            WHERE id = :note_id AND user_id = :user_id AND lesson_id = :lesson_id
        """)
        
        result = db.session.execute(update_query, {
            'note_id': note_id,
            'user_id': g.user.id,
            'lesson_id': lesson_id,
            'title': title,
            'content': content,
            'status': status,
            'tags': tags
        })
        
        if result.rowcount == 0:
            return jsonify({'error': 'Note not found or unauthorized'}), 404
        
        db.session.commit()
        
        # Return updated notes grid
        return get_class_notes(lesson_id)
        
    except Exception as e:
        print(f"Error updating class note: {e}")
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@class_note_bp.route('/<lesson_id>/notes/<note_id>/delete', methods=['POST'])
@login_required_web
def delete_class_note(lesson_id, note_id):
    """Delete a class note"""
    try:
        # Delete note (cascade will handle files)
        delete_query = text("""
            DELETE FROM note 
            WHERE id = :note_id AND user_id = :user_id AND lesson_id = :lesson_id
        """)
        
        result = db.session.execute(delete_query, {
            'note_id': note_id,
            'user_id': g.user.id,
            'lesson_id': lesson_id
        })
        
        if result.rowcount == 0:
            return jsonify({'error': 'Note not found or unauthorized'}), 404
        
        db.session.commit()
        
        # Return updated notes grid
        return get_class_notes(lesson_id)
        
    except Exception as e:
        print(f"Error deleting class note: {e}")
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@class_note_bp.route('/<lesson_id>/notes/<note_id>/toggle-status', methods=['POST'])
@login_required_web
def toggle_note_status(lesson_id, note_id):
    """Toggle note status between pending/in-progress/completed"""
    try:
        # Get current status
        status_query = text("""
            SELECT status FROM note 
            WHERE id = :note_id AND user_id = :user_id AND lesson_id = :lesson_id
        """)
        
        result = db.session.execute(status_query, {
            'note_id': note_id,
            'user_id': g.user.id,
            'lesson_id': lesson_id
        })
        
        row = result.fetchone()
        if not row:
            return jsonify({'error': 'Note not found or unauthorized'}), 404
        
        current_status = row.status
        
        # Cycle through statuses
        status_cycle = ['pending', 'in-progress', 'completed']
        current_index = status_cycle.index(current_status) if current_status in status_cycle else 0
        new_status = status_cycle[(current_index + 1) % len(status_cycle)]
        
        # Update status
        update_query = text("""
            UPDATE note 
            SET status = :new_status, updated_at = datetime('now')
            WHERE id = :note_id AND user_id = :user_id AND lesson_id = :lesson_id
        """)
        
        db.session.execute(update_query, {
            'note_id': note_id,
            'user_id': g.user.id,
            'lesson_id': lesson_id,
            'new_status': new_status
        })
        
        db.session.commit()
        
        return jsonify({'success': True, 'new_status': new_status})
        
    except Exception as e:
        print(f"Error toggling note status: {e}")
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
