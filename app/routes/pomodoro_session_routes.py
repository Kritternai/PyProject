"""
Pomodoro Session Routes
"""
from flask import Blueprint, request, jsonify
import sqlite3
from datetime import datetime

# Create blueprint
pomodoro_session_bp = Blueprint('pomodoro_session', __name__, url_prefix='/pomodoro')

DB_PATH = 'instance/site.db'

def get_db():
    """Get database connection"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# ============================================
# POMODORO SESSION ROUTES
# ============================================

@pomodoro_session_bp.route('/session', methods=['POST'])
def create_session():
    """สร้าง Pomodoro session ใหม่"""
    data = request.json
    conn = get_db()
    cursor = conn.cursor()
    session_id = data.get('id')
    user_id = data.get('user_id')
    session_type = data.get('session_type')
    duration = data.get('duration')
    actual_duration = data.get('actual_duration')
    start_time = data.get('start_time', datetime.now())
    end_time = data.get('end_time')
    status = data.get('status', 'active')
    productivity_score = data.get('productivity_score')
    task = data.get('task')

    cursor.execute("""
        INSERT INTO pomodoro_session (
            id, user_id, session_type, duration, actual_duration,
            start_time, end_time, status, productivity_score, task
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        session_id, user_id, session_type, duration, actual_duration,
        start_time, end_time, status, productivity_score, task
    ))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Pomodoro session created'}), 201


@pomodoro_session_bp.route('/session/<session_id>', methods=['GET'])
def get_session(session_id):
    """ดึงข้อมูล session ตาม id"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM pomodoro_session WHERE id = ?", (session_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return jsonify(dict(row))
    return jsonify({'error': 'Session not found'}), 404


@pomodoro_session_bp.route('/session/user/<user_id>', methods=['GET'])
def get_user_sessions(user_id):
    """ดึง session ทั้งหมดของ user"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM pomodoro_session WHERE user_id = ?", (user_id,))
    rows = cursor.fetchall()
    conn.close()
    return jsonify([dict(row) for row in rows])


@pomodoro_session_bp.route('/session/<session_id>', methods=['PUT'])
def update_session(session_id):
    """อัปเดต session"""
    data = request.json
    conn = get_db()
    cursor = conn.cursor()
    fields = []
    values = []
    for key in ['session_type', 'duration', 'actual_duration', 'start_time', 'end_time',
                'status', 'productivity_score', 'task']:
        if key in data:
            fields.append(f"{key} = ?")
            values.append(data[key])
    values.append(session_id)
    cursor.execute(f"UPDATE pomodoro_session SET {', '.join(fields)}, updated_at = CURRENT_TIMESTAMP WHERE id = ?", values)
    conn.commit()
    conn.close()
    return jsonify({'message': 'Session updated'})


@pomodoro_session_bp.route('/session/<session_id>', methods=['DELETE'])
def delete_session(session_id):
    """ลบ session"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM pomodoro_session WHERE id = ?", (session_id,))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Session deleted'})