"""Pomodoro statistics API routes."""

from flask import Blueprint
from app.controllers.pomodoro_statistics_views import PomodoroStatisticsViews
from app.middleware.auth_middleware import login_required
pomodoro_stats_bp = Blueprint('pomodoro_statistics', __name__, url_prefix='/api/pomodoro/statistics')

stats_views = PomodoroStatisticsViews()


@pomodoro_stats_bp.route('/daily', methods=['POST'])
@login_required
def update_daily_statistics():
    """Recalculate daily statistics for the authenticated user."""
    return stats_views.update_daily_statistics()


@pomodoro_stats_bp.route('/timer', methods=['GET'])
@login_required
def get_timer_stats():
    """Return aggregate timer statistics for the authenticated user."""
    return stats_views.get_timer_stats()


@pomodoro_stats_bp.route('/daily-progress', methods=['GET'])
@login_required
def get_daily_progress():
    """Return today's progress metrics for the authenticated user."""
    return stats_views.get_daily_progress()


@pomodoro_stats_bp.route('/productivity', methods=['POST'])
@login_required
def get_productivity_report():
    """Return productivity report for the requested date range."""
    return stats_views.get_productivity_report()


@pomodoro_stats_bp.route('/history', methods=['GET'])
@login_required
def get_session_history():
    """Return Pomodoro session history for the authenticated user."""
    return stats_views.get_session_history()


@pomodoro_stats_bp.route('/export', methods=['GET'])
@login_required
def export_data():
    """Export Pomodoro statistics for the authenticated user."""
    return stats_views.export_data()