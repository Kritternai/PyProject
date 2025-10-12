"""
Pomodoro Statistics Routes
Routes for managing Pomodoro statistics
"""

from flask import Blueprint
from app.controllers.pomodoro_statistics_control import PomodoroStatisticsController

# Create blueprint
pomodoro_stats_bp = Blueprint('pomodoro_statistics', __name__, url_prefix='/api/pomodoro/statistics')

# Create controller instance
stats_controller = PomodoroStatisticsController()

# Statistics routes
@pomodoro_stats_bp.route('/user/<user_id>/date/<date>', methods=['GET'])
def get_statistics(user_id, date):
    """Get statistics for user on specific date"""
    return stats_controller.get_statistics(user_id, date)

@pomodoro_stats_bp.route('', methods=['POST'])
def create_statistics():
    """Create new statistics entry"""
    return stats_controller.create_statistics()

@pomodoro_stats_bp.route('/<stat_id>', methods=['PUT'])
def update_statistics(stat_id):
    """Update statistics"""
    return stats_controller.update_statistics(stat_id)

@pomodoro_stats_bp.route('/<stat_id>', methods=['DELETE'])
def delete_statistics(stat_id):
    """Delete statistics"""
    return stats_controller.delete_statistics(stat_id)

@pomodoro_stats_bp.route('/user/<user_id>/summary', methods=['GET'])
def get_user_statistics_summary(user_id):
    """Get user's statistics summary"""
    return stats_controller.get_statistics_summary(user_id)