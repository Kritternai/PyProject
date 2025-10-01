"""
Pomodoro Timer Routes
Simple routes for Pomodoro functionality
"""

from flask import Blueprint, render_template, request, jsonify, session, g
from functools import wraps

# Create blueprint
pomodoro_bp = Blueprint('pomodoro', __name__)

def login_required_web(f):
    """Decorator to require login for web routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Not authenticated'}), 401
        return f(*args, **kwargs)
    return decorated_function

@pomodoro_bp.route('/pomodoro')
@login_required_web
def pomodoro_page():
    """Pomodoro timer page"""
    if not g.user:
        return jsonify({'error': 'User not found'}), 404
    
    return render_template('pomodoro_fragment.html', user=g.user)

@pomodoro_bp.route('/partial/pomodoro')
@login_required_web
def partial_pomodoro():
    """Pomodoro partial for SPA"""
    if not g.user:
        return jsonify({'error': 'Not authenticated'}), 401
    
    return render_template('pomodoro_fragment.html', user=g.user)

@pomodoro_bp.route('/api/pomodoro/complete', methods=['POST'])
@login_required_web
def complete_pomodoro():
    """Complete a pomodoro session"""
    if not g.user:
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        data = request.get_json()
        session_type = data.get('session_type', 'focus')
        duration = data.get('duration', 25)
        
        # Here you would save to database
        # For now, just return success
        return jsonify({
            'success': True,
            'message': f'{session_type} session completed',
            'duration': duration
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@pomodoro_bp.route('/api/pomodoro/statistics')
@login_required_web
def get_pomodoro_statistics():
    """Get pomodoro statistics"""
    if not g.user:
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        # Mock data for now
        statistics = {
            'today': {
                'pomodoros': 5,
                'focus_time': 125,  # minutes
                'break_time': 25
            },
            'week': {
                'pomodoros': 25,
                'focus_time': 625,
                'break_time': 125
            },
            'month': {
                'pomodoros': 100,
                'focus_time': 2500,
                'break_time': 500
            }
        }
        
        return jsonify({
            'success': True,
            'data': statistics
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
