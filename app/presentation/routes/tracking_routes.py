"""
Progress Tracking Routes
Simple routes for tracking functionality
"""

from flask import Blueprint, render_template, request, jsonify, session, g
from functools import wraps

# Create blueprint
tracking_bp = Blueprint('tracking', __name__)

def login_required_web(f):
    """Decorator to require login for web routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Not authenticated'}), 401
        return f(*args, **kwargs)
    return decorated_function

@tracking_bp.route('/track')
@login_required_web
def tracking_page():
    """Progress tracking page"""
    if not g.user:
        return jsonify({'error': 'User not found'}), 404
    
    return render_template('track_fragment.html', user=g.user)

@tracking_bp.route('/partial/track')
@login_required_web
def partial_tracking():
    """Tracking partial for SPA"""
    if not g.user:
        return jsonify({'error': 'Not authenticated'}), 401
    
    return render_template('track_fragment.html', user=g.user)

@tracking_bp.route('/api/tracking/update', methods=['POST'])
@login_required_web
def update_progress():
    """Update progress tracking"""
    if not g.user:
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        data = request.get_json()
        progress_type = data.get('type')  # pomodoros, studyTime, lessons, notes
        amount = data.get('amount', 1)
        
        # Here you would save to database
        # For now, just return success
        return jsonify({
            'success': True,
            'message': f'Updated {progress_type} by {amount}',
            'type': progress_type,
            'amount': amount
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@tracking_bp.route('/api/tracking/statistics')
@login_required_web
def get_tracking_statistics():
    """Get tracking statistics"""
    if not g.user:
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        # Mock data for now
        statistics = {
            'daily': {
                'pomodoros': 5,
                'studyTime': 150,
                'lessons': 2,
                'notes': 3,
                'goals': {
                    'pomodoros': 8,
                    'studyTime': 240,
                    'lessons': 3,
                    'notes': 5
                }
            },
            'weekly': {
                'pomodoros': [5, 7, 3, 8, 6, 4, 2],
                'studyTime': [150, 210, 90, 240, 180, 120, 60],
                'lessons': [2, 3, 1, 4, 2, 1, 1],
                'notes': [3, 5, 2, 6, 4, 2, 1]
            },
            'monthly': {
                'pomodoros': 100,
                'studyTime': 3000,
                'lessons': 50,
                'notes': 75
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

@tracking_bp.route('/api/tracking/goals', methods=['GET', 'POST'])
@login_required_web
def manage_goals():
    """Get or update goals"""
    if not g.user:
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        if request.method == 'GET':
            # Return current goals
            goals = {
                'daily': {
                    'pomodoros': 8,
                    'studyTime': 240,
                    'lessons': 3,
                    'notes': 5
                },
                'weekly': {
                    'pomodoros': 40,
                    'studyTime': 1200,
                    'lessons': 15,
                    'notes': 25
                }
            }
            
            return jsonify({
                'success': True,
                'data': goals
            })
        
        elif request.method == 'POST':
            # Update goals
            data = request.get_json()
            # Here you would save to database
            return jsonify({
                'success': True,
                'message': 'Goals updated successfully'
            })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
