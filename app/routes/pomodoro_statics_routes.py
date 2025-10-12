"""
Pomodoro Statistics Routes
"""
from flask import Blueprint, request, jsonify
import sqlite3

# This would typically be in the same file or a shared module,
# so we redefine it here for clarity.
pomodoro_session_bp = Blueprint('pomodoro_statistics', __name__, url_prefix='/pomodoro')
DB_PATH = 'instance/site.db'

def get_db():
    """Get database connection"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# ============================================
# POMODORO STATISTICS ROUTES
# ============================================

@pomodoro_session_bp.route('/statistics/<user_id>/<date>', methods=['GET'])
def get_statistics(user_id, date):
    """ดึงสถิติ Pomodoro ของ user ตามวัน"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM pomodoro_statistics WHERE user_id = ? AND date = ?", (user_id, date))
    row = cursor.fetchone()
    conn.close()
    if row:
        return jsonify(dict(row))
    return jsonify({'error': 'Statistics not found'}), 404


@pomodoro_session_bp.route('/statistics', methods=['POST'])
def create_statistics():
    """สร้างสถิติใหม่"""
    data = request.json
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO pomodoro_statistics (
            id, user_id, date, total_sessions, total_focus_time, total_break_time,
            total_long_break_time, total_interrupted_sessions, total_completed_sessions,
            total_productivity_score, total_tasks_completed, total_tasks,
            total_focus_sessions, total_short_break_sessions, total_long_break_sessions,
            total_time_spent, total_effective_time, total_ineffective_time,
            total_abandoned_sessions, total_on_time_sessions, total_late_sessions,
            average_session_duration, productivity_score
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        data.get('id'), data.get('user_id'), data.get('date'), data.get('total_sessions', 0),
        data.get('total_focus_time', 0), data.get('total_break_time', 0), data.get('total_long_break_time', 0),
        data.get('total_interrupted_sessions', 0), data.get('total_completed_sessions', 0),
        data.get('total_productivity_score', 0), data.get('total_tasks_completed', 0), data.get('total_tasks', 0),
        data.get('total_focus_sessions', 0), data.get('total_short_break_sessions', 0), data.get('total_long_break_sessions', 0),
        data.get('total_time_spent', 0), data.get('total_effective_time', 0), data.get('total_ineffective_time', 0),
        data.get('total_abandoned_sessions', 0), data.get('total_on_time_sessions', 0), data.get('total_late_sessions', 0),
        data.get('average_session_duration', 0.0), data.get('productivity_score', 0.0)
    ))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Statistics created'}), 201


@pomodoro_session_bp.route('/statistics/<stat_id>', methods=['PUT'])
def update_statistics(stat_id):
    """อัปเดตสถิติ"""
    data = request.json
    conn = get_db()
    cursor = conn.cursor()
    fields = []
    values = []
    for key in [
        'total_sessions', 'total_focus_time', 'total_break_time', 'total_long_break_time',
        'total_interrupted_sessions', 'total_completed_sessions', 'total_productivity_score',
        'total_tasks_completed', 'total_tasks', 'total_focus_sessions', 'total_short_break_sessions',
        'total_long_break_sessions', 'total_time_spent', 'total_effective_time', 'total_ineffective_time',
        'total_abandoned_sessions', 'total_on_time_sessions', 'total_late_sessions',
        'average_session_duration', 'productivity_score'
    ]:
        if key in data:
            fields.append(f"{key} = ?")
            values.append(data[key])
    values.append(stat_id)
    cursor.execute(f"UPDATE pomodoro_statistics SET {', '.join(fields)}, updated_at = CURRENT_TIMESTAMP WHERE id = ?", values)
    conn.commit()
    conn.close()
    return jsonify({'message': 'Statistics updated'})


@pomodoro_session_bp.route('/statistics/<stat_id>', methods=['DELETE'])
def delete_statistics(stat_id):
    """ลบสถิติ"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM pomodoro_statistics WHERE id = ?", (stat_id,))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Statistics deleted'})