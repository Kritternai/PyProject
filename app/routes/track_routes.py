# app/routes/track_routes.py (ไฟล์ใหม่)

from flask import Blueprint, jsonify, session, g
from app.middleware.auth_middleware import login_required
from app.services import NoteService, PomodoroService, LessonService, UserService

# สร้าง blueprint
track_bp = Blueprint('track_api', __name__, url_prefix='/api/track')

@track_bp.before_request
def load_user():
    """โหลด user object ก่อนทุก request ใน blueprint นี้"""
    if 'user_id' in session:
        user_service = UserService()
        try:
            # ใช้ g object ของ Flask เพื่อเก็บข้อมูล user ไว้ใช้ตลอด request
            g.user = user_service.get_user_by_id(session['user_id'])
        except Exception:
            g.user = None
    else:
        g.user = None


@track_bp.route('/statistics', methods=['GET'])
@login_required
def get_track_statistics():
    """
    API สำหรับดึงข้อมูลสถิติทั้งหมดในหน้า Track

    Returns:
        JSON object ที่มีข้อมูล today, total, และ weekly
    """
    try:
        if not g.user:
            return jsonify({"success": False, "error": "User not found"}), 404

        user_id = g.user.id
        
        # สร้าง service instances
        note_service = NoteService()
        pomodoro_service = PomodoroService()
        lesson_service = LessonService()
        
        # --- ดึงข้อมูลสำหรับ "Today's Progress" ---
        today_pomodoros = pomodoro_service.get_pomodoros_count_today(user_id)
        today_study_time = pomodoro_service.get_study_time_today(user_id)
        today_notes = note_service.get_notes_count_today(user_id)
        today_lessons = lesson_service.get_lessons_completed_today(user_id)
        
        # --- ดึงข้อมูลสำหรับ "Statistics Summary" (ข้อมูลรวม) ---
        total_pomodoros = pomodoro_service.get_total_pomodoros_count(user_id)
        total_lessons = lesson_service.get_lessons_count(user_id)
        total_notes = note_service.get_total_notes_count(user_id)
        total_study_time_minutes = total_pomodoros * 25 # สมมติว่า 1 pomodoro = 25 นาที

        # สร้างโครงสร้างข้อมูลที่จะส่งกลับไป
        data = {
            "success": True,
            "today": {
                "pomodoros": {"current": today_pomodoros, "goal": 8},
                "study_time": {"current": today_study_time, "goal": 240}, # 4 ชั่วโมง
                "lessons": {"current": today_lessons, "goal": 3},
                "notes": {"current": today_notes, "goal": 5}
            },
            "total": {
                "pomodoros": total_pomodoros,
                "study_time": total_study_time_minutes,
                "lessons": total_lessons,
                "notes": total_notes
            },
            "weekly": []  # ส่วนนี้จะทำในขั้นต่อไป (ตอนนี้ใส่เป็นค่าว่างไปก่อน)
        }
        
        return jsonify(data), 200
        
    except Exception as e:
        # ถ้ามีข้อผิดพลาด ให้ส่ง error message กลับไป
        return jsonify({"success": False, "error": str(e)}), 500