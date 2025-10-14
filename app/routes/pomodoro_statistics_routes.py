"""
Pomodoro Statistics API Routes
Defines REST API endpoints for statistics operations
"""

from flask import Blueprint
from app.controllers.pomodoro_statistics_controller import PomodoroStatisticsController

# Create Blueprint
pomodoro_stats_bp = Blueprint('pomodoro_statistics', __name__, url_prefix='/api/pomodoro/statistics')

# Initialize controller
stats_controller = PomodoroStatisticsController()

# === Daily Statistics Routes ===
@pomodoro_stats_bp.route('/daily', methods=['GET'])
def get_daily_statistics():
    """
    GET /api/pomodoro/statistics/daily?date=YYYY-MM-DD
    Get daily statistics for a specific date (default: today)
    """
    return stats_controller.get_daily_statistics()

@pomodoro_stats_bp.route('/daily', methods=['PUT'])
def update_daily_statistics():
    """
    PUT /api/pomodoro/statistics/daily
    Update or create daily statistics
    Body: { "date": "YYYY-MM-DD" } (optional)
    """
    return stats_controller.update_daily_statistics()

@pomodoro_stats_bp.route('/daily', methods=['DELETE'])
def delete_daily_statistics():
    """
    DELETE /api/pomodoro/statistics/daily?date=YYYY-MM-DD
    Delete daily statistics for a specific date
    """
    return stats_controller.delete_daily_statistics()

# === Utility Routes ===
@pomodoro_stats_bp.route('/recalculate', methods=['POST'])
def recalculate_all_statistics():
    """
    POST /api/pomodoro/statistics/recalculate
    Recalculate all statistics for the current user
    """
    return stats_controller.recalculate_all_statistics()

# === Health Check Route ===
@pomodoro_stats_bp.route('/health', methods=['GET'])
def health_check():
    """
    GET /api/pomodoro/statistics/health
    Check if the statistics API is working
    """
    return {
        'success': True,
        'message': 'Pomodoro Statistics API is running',
        'endpoints': {
            'daily': '/api/pomodoro/statistics/daily',
            'weekly': '/api/pomodoro/statistics/weekly',
            'monthly': '/api/pomodoro/statistics/monthly',
            'trends': '/api/pomodoro/statistics/trends',
            'summary': '/api/pomodoro/statistics/summary',
            'chart': '/api/pomodoro/statistics/chart',
            'recalculate': '/api/pomodoro/statistics/recalculate'
        }
    }

# Error handlers for the blueprint
@pomodoro_stats_bp.errorhandler(404)
def not_found(error):
    return {
        'success': False,
        'error': 'Endpoint not found',
        'message': 'The requested statistics endpoint does not exist'
    }, 404

@pomodoro_stats_bp.errorhandler(405)
def method_not_allowed(error):
    return {
        'success': False,
        'error': 'Method not allowed',
        'message': 'This HTTP method is not allowed for this endpoint'
    }, 405

@pomodoro_stats_bp.errorhandler(500)
def internal_error(error):
    return {
        'success': False,
        'error': 'Internal server error',
        'message': 'An unexpected error occurred in the statistics service'
    }, 500

# === Weekly Statistics Routes ===
@pomodoro_stats_bp.route('/weekly', methods=['GET'])
def get_weekly_statistics():
    """
    GET /api/pomodoro/statistics/weekly?start_date=YYYY-MM-DD
    Get weekly statistics (default: current week)
    """
    return stats_controller.get_weekly_statistics()

# === Monthly Statistics Routes ===
@pomodoro_stats_bp.route('/monthly', methods=['GET'])
def get_monthly_statistics():
    """
    GET /api/pomodoro/statistics/monthly?year=YYYY&month=MM
    Get monthly statistics (default: current month)
    """
    return stats_controller.get_monthly_statistics()

# === Trends and Analytics Routes ===
@pomodoro_stats_bp.route('/trends', methods=['GET'])
def get_productivity_trends():
    """
    GET /api/pomodoro/statistics/trends?days=7
    Get productivity trends over specified days
    """
    return stats_controller.get_productivity_trends()

@pomodoro_stats_bp.route('/summary', methods=['GET'])
def get_statistics_summary():
    """
    GET /api/pomodoro/statistics/summary
    Get overall statistics summary (today, week, trends)
    """
    return stats_controller.get_statistics_summary()

# === Chart Data Routes ===
@pomodoro_stats_bp.route('/chart', methods=['GET'])
def get_chart_data():
    """
    GET /api/pomodoro/statistics/chart?type=weekly&days=7
    Get data formatted for charts and visualizations
    Types: weekly, monthly, trends, daily
    """
    return stats_controller.get_statistics_chart_data()

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