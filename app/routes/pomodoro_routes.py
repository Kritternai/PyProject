from flask import Blueprint, render_template, jsonify
from app import db
from app.models.pomodoro import PomodoroSessionModel, PomodoroStatisticsModel
from datetime import date

pomodoro_bp = Blueprint('pomodoro', __name__)

@pomodoro_bp.route('/pomodoro')
def pomodoro():
    """
    Render the Pomodoro page showing recent sessions and today's statistics.
    """
    user_id = "demo-user-001"  # ใช้ mock id ชั่วคราว (รอเชื่อมระบบ login จริง)

    # ดึง session ล่าสุดของผู้ใช้
    sessions = (
        PomodoroSessionModel.query
        .filter_by(user_id=user_id)
        .order_by(PomodoroSessionModel.start_time.desc())
        .limit(5)
        .all()
    )

    # ดึงสถิติของวันนี้
    statistics = (
        PomodoroStatisticsModel.query
        .filter_by(user_id=user_id, date=date.today())
        .first()
    )

    return render_template(
        'pomodoro_fragment.html',
        sessions=[s.to_dict() for s in sessions],
        statistics=statistics.to_dict() if statistics else None
    )


@pomodoro_bp.route('/api/pomodoro/sessions')
def get_pomodoro_sessions():
    """
    Return JSON list of all Pomodoro sessions for the current user.
    """
    user_id = "demo-user-001"

    sessions = PomodoroSessionModel.query.filter_by(user_id=user_id).all()
    return jsonify([s.to_dict() for s in sessions])
