"""
Microsoft Teams API Integration Routes (Mockup)
Separate blueprint for Microsoft Teams functionality with mock data
"""

from flask import Blueprint, render_template, request, redirect, url_for, session, g, flash, jsonify, current_app
from functools import wraps
from datetime import datetime, timedelta
import uuid

# Create Microsoft Teams blueprint
microsoft_teams_bp = Blueprint('microsoft_teams', __name__, url_prefix='/microsoft_teams')

# Mock Microsoft Teams Data
MOCK_TEAMS_DATA = {
    'teams': [
        {
            'id': 'team-001',
            'displayName': 'Computer Science 101',
            'description': 'Introduction to Programming',
            'createdDateTime': '2024-09-01T08:00:00Z',
            'channels': [
                {
                    'id': 'channel-001',
                    'displayName': 'General',
                    'description': 'General discussion for CS101',
                    'messages': [
                        {
                            'id': 'msg-001',
                            'from': {'user': {'displayName': 'Prof. Smith'}},
                            'body': {'content': 'Welcome to Computer Science 101!'},
                            'createdDateTime': '2024-09-01T09:00:00Z'
                        },
                        {
                            'id': 'msg-002',
                            'from': {'user': {'displayName': 'Prof. Smith'}},
                            'body': {'content': 'Assignment 1 has been posted. Please check the Assignments tab.'},
                            'createdDateTime': '2024-09-05T10:30:00Z'
                        }
                    ]
                },
                {
                    'id': 'channel-002',
                    'displayName': 'Assignments',
                    'description': 'Course assignments and submissions',
                    'messages': []
                }
            ],
            'assignments': [
                {
                    'id': 'assign-001',
                    'displayName': 'Introduction to Python',
                    'instructions': 'Complete the Python basics tutorial and submit your code.',
                    'dueDateTime': '2024-09-15T23:59:00Z',
                    'status': 'assigned',
                    'points': 100
                },
                {
                    'id': 'assign-002',
                    'displayName': 'Data Structures Quiz',
                    'instructions': 'Complete the quiz on arrays, lists, and dictionaries.',
                    'dueDateTime': '2024-09-22T23:59:00Z',
                    'status': 'assigned',
                    'points': 50
                }
            ],
            'members': [
                {'displayName': 'Prof. Smith', 'email': 'smith@university.edu', 'role': 'owner'},
                {'displayName': 'John Doe', 'email': 'john@university.edu', 'role': 'member'},
                {'displayName': 'Jane Wilson', 'email': 'jane@university.edu', 'role': 'member'}
            ]
        },
        {
            'id': 'team-002',
            'displayName': 'Data Science Workshop',
            'description': 'Advanced data analysis and machine learning',
            'createdDateTime': '2024-09-10T08:00:00Z',
            'channels': [
                {
                    'id': 'channel-003',
                    'displayName': 'General',
                    'description': 'General discussion',
                    'messages': [
                        {
                            'id': 'msg-003',
                            'from': {'user': {'displayName': 'Dr. Johnson'}},
                            'body': {'content': 'Welcome to the Data Science Workshop!'},
                            'createdDateTime': '2024-09-10T09:00:00Z'
                        }
                    ]
                }
            ],
            'assignments': [
                {
                    'id': 'assign-003',
                    'displayName': 'Data Cleaning Project',
                    'instructions': 'Clean and prepare the provided dataset for analysis.',
                    'dueDateTime': '2024-09-28T23:59:00Z',
                    'status': 'assigned',
                    'points': 150
                }
            ],
            'members': [
                {'displayName': 'Dr. Johnson', 'email': 'johnson@university.edu', 'role': 'owner'},
                {'displayName': 'Alice Brown', 'email': 'alice@university.edu', 'role': 'member'}
            ]
        },
        {
            'id': 'team-003',
            'displayName': 'Web Development Team',
            'description': 'Full-stack web development course',
            'createdDateTime': '2024-08-25T08:00:00Z',
            'channels': [
                {
                    'id': 'channel-004',
                    'displayName': 'General',
                    'description': 'General discussion',
                    'messages': []
                },
                {
                    'id': 'channel-005',
                    'displayName': 'Code Reviews',
                    'description': 'Submit your code for peer review',
                    'messages': []
                }
            ],
            'assignments': [
                {
                    'id': 'assign-004',
                    'displayName': 'HTML/CSS Portfolio',
                    'instructions': 'Create a personal portfolio website using HTML and CSS.',
                    'dueDateTime': '2024-09-20T23:59:00Z',
                    'status': 'submitted',
                    'points': 100
                },
                {
                    'id': 'assign-005',
                    'displayName': 'JavaScript Calculator',
                    'instructions': 'Build a functional calculator using JavaScript.',
                    'dueDateTime': '2024-10-05T23:59:00Z',
                    'status': 'assigned',
                    'points': 120
                }
            ],
            'members': [
                {'displayName': 'Prof. Martinez', 'email': 'martinez@university.edu', 'role': 'owner'},
                {'displayName': 'Chris Lee', 'email': 'chris@university.edu', 'role': 'member'},
                {'displayName': 'Emily Chen', 'email': 'emily@university.edu', 'role': 'member'},
                {'displayName': 'David Kim', 'email': 'david@university.edu', 'role': 'member'}
            ]
        }
    ]
}

# Decorator for login required
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('register.login'))
        return f(*args, **kwargs)
    return decorated_function

@microsoft_teams_bp.before_request
def load_logged_in_user():
    """Load logged in user for Microsoft Teams routes"""
    user_id = session.get('user_id')
    if user_id:
        try:
            from app.infrastructure.di.container import get_service
            from app.domain.interfaces.services.user_service import UserService
            user_service = get_service(UserService)
            g.user = user_service.get_user_by_id(user_id)
        except:
            g.user = None
    else:
        g.user = None

@microsoft_teams_bp.route('/authorize')
@login_required
def authorize():
    """Mock Microsoft Teams OAuth authorization"""
    print(f"DEBUG: Mock Microsoft Teams authorization for user {session['user_id']}")
    
    # Simulate OAuth flow by redirecting to our own callback
    # In real implementation, this would redirect to Microsoft's OAuth page
    return redirect(url_for('microsoft_teams.oauth2callback', 
                          code='mock_auth_code_' + str(uuid.uuid4())[:8],
                          state='mock_state'))

@microsoft_teams_bp.route('/oauth2callback')
def oauth2callback():
    """Mock OAuth2 callback for Microsoft Teams"""
    user_id = session.get('user_id')
    
    if not user_id:
        flash('Please log in first.', 'warning')
        return redirect(url_for('register.login'))
    
    # Simulate successful OAuth
    auth_code = request.args.get('code')
    print(f"DEBUG: Mock Microsoft Teams OAuth callback for user {user_id}")
    print(f"  Auth Code: {auth_code}")
    
    # Store mock connection status in session
    session['microsoft_teams_connected'] = True
    session['microsoft_teams_access_token'] = f'mock_token_{uuid.uuid4()}'
    
    # Store mock data in session (in real app, this would be in database)
    session['microsoft_teams_data'] = MOCK_TEAMS_DATA
    
    flash('Successfully connected to Microsoft Teams! (Mockup)', 'success')
    print(f"DEBUG: Mock Microsoft Teams connection completed for user {user_id}")
    
    # Redirect to class page to show the teams
    return redirect(url_for('main.index') + '#class?microsoft_teams_connected=true')

@microsoft_teams_bp.route('/fetch_teams')
@login_required
def fetch_teams():
    """Fetch Microsoft Teams data (mock)"""
    if not session.get('microsoft_teams_connected'):
        flash('Please connect to Microsoft Teams first.', 'warning')
        return redirect(url_for('microsoft_teams.authorize'))
    
    # Return mock teams data
    teams_data = session.get('microsoft_teams_data', MOCK_TEAMS_DATA)
    
    return jsonify({
        'success': True,
        'teams': teams_data['teams'],
        'count': len(teams_data['teams'])
    })

@microsoft_teams_bp.route('/team/<team_id>')
@login_required
def get_team_details(team_id):
    """Get details for a specific team (mock)"""
    if not session.get('microsoft_teams_connected'):
        flash('Please connect to Microsoft Teams first.', 'warning')
        return redirect(url_for('microsoft_teams.authorize'))
    
    teams_data = session.get('microsoft_teams_data', MOCK_TEAMS_DATA)
    team = next((t for t in teams_data['teams'] if t['id'] == team_id), None)
    
    if not team:
        return jsonify({'success': False, 'error': 'Team not found'}), 404
    
    return jsonify({
        'success': True,
        'team': team
    })

@microsoft_teams_bp.route('/disconnect', methods=['POST'])
@login_required
def disconnect():
    """Disconnect Microsoft Teams (mock)"""
    session.pop('microsoft_teams_connected', None)
    session.pop('microsoft_teams_access_token', None)
    session.pop('microsoft_teams_data', None)
    
    flash('Successfully disconnected from Microsoft Teams.', 'info')
    return redirect(url_for('main.index') + '#class')

@microsoft_teams_bp.route('/status')
@login_required
def status():
    """Check Microsoft Teams connection status"""
    connected = session.get('microsoft_teams_connected', False)
    teams_count = 0
    
    if connected:
        teams_data = session.get('microsoft_teams_data', MOCK_TEAMS_DATA)
        teams_count = len(teams_data['teams'])
    
    return jsonify({
        'connected': connected,
        'teams_count': teams_count,
        'is_mock': True
    })

