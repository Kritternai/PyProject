"""
Microsoft Teams API Integration Routes (Mockup)
Fake integration that simulates real Microsoft Teams API calls
"""

from flask import Blueprint, render_template, request, redirect, url_for, session, g, flash, jsonify, current_app
from functools import wraps
from datetime import datetime, timedelta
import random
import uuid

# Create Microsoft Teams blueprint
microsoft_teams_bp = Blueprint('microsoft_teams', __name__, url_prefix='/microsoft_teams')

# Mock Microsoft Teams Data - Enhanced with more realistic data
MOCK_TEAMS = [
    {
        'id': 'team_001',
        'name': 'Computer Science 101',
        'description': 'Introduction to Computer Science - Fundamentals of programming, algorithms, and data structures',
        'owner': 'Dr. Smith',
        'ownerEmail': 'dr.smith@university.edu',
        'memberCount': 45,
        'created': '2024-01-15',
        'lastActivity': '2024-10-15 14:30:00',
        'isArchived': False,
        'channels': [
            {'id': 'ch_001', 'name': 'General', 'type': 'Standard', 'messageCount': 156},
            {'id': 'ch_002', 'name': 'Assignments', 'type': 'Standard', 'messageCount': 89},
            {'id': 'ch_003', 'name': 'Discussions', 'type': 'Standard', 'messageCount': 234},
            {'id': 'ch_004', 'name': 'Office Hours', 'type': 'Standard', 'messageCount': 67}
        ],
        'assignments': 12,
        'files': 28,
        'tags': ['Computer Science', 'Programming', 'Algorithms']
    },
    {
        'id': 'team_002', 
        'name': 'Web Development Bootcamp',
        'description': 'Full-stack web development course covering HTML, CSS, JavaScript, React, and Node.js',
        'owner': 'Prof. Johnson',
        'ownerEmail': 'prof.johnson@tech.edu',
        'memberCount': 32,
        'created': '2024-02-01',
        'lastActivity': '2024-10-14 16:45:00',
        'isArchived': False,
        'channels': [
            {'id': 'ch_005', 'name': 'General', 'type': 'Standard', 'messageCount': 203},
            {'id': 'ch_006', 'name': 'HTML/CSS', 'type': 'Standard', 'messageCount': 145},
            {'id': 'ch_007', 'name': 'JavaScript', 'type': 'Standard', 'messageCount': 178},
            {'id': 'ch_008', 'name': 'React', 'type': 'Standard', 'messageCount': 92},
            {'id': 'ch_009', 'name': 'Projects', 'type': 'Standard', 'messageCount': 67}
        ],
        'assignments': 8,
        'files': 45,
        'tags': ['Web Development', 'JavaScript', 'React', 'Full-stack']
    },
    {
        'id': 'team_003',
        'name': 'Data Science Workshop',
        'description': 'Advanced data analysis and machine learning techniques using Python, R, and statistical methods',
        'owner': 'Dr. Chen',
        'ownerEmail': 'dr.chen@data.edu',
        'memberCount': 28,
        'created': '2024-02-15',
        'lastActivity': '2024-10-13 11:20:00',
        'isArchived': False,
        'channels': [
            {'id': 'ch_010', 'name': 'General', 'type': 'Standard', 'messageCount': 89},
            {'id': 'ch_011', 'name': 'Python', 'type': 'Standard', 'messageCount': 134},
            {'id': 'ch_012', 'name': 'Machine Learning', 'type': 'Standard', 'messageCount': 156},
            {'id': 'ch_013', 'name': 'Datasets', 'type': 'Standard', 'messageCount': 45}
        ],
        'assignments': 15,
        'files': 67,
        'tags': ['Data Science', 'Machine Learning', 'Python', 'Statistics']
    },
    {
        'id': 'team_004',
        'name': 'Digital Marketing Mastery',
        'description': 'Complete guide to digital marketing strategies, SEO, social media, and analytics',
        'owner': 'Ms. Rodriguez',
        'ownerEmail': 'ms.rodriguez@marketing.edu',
        'memberCount': 38,
        'created': '2024-03-01',
        'lastActivity': '2024-10-15 09:15:00',
        'isArchived': False,
        'channels': [
            {'id': 'ch_014', 'name': 'General', 'type': 'Standard', 'messageCount': 112},
            {'id': 'ch_015', 'name': 'SEO & Analytics', 'type': 'Standard', 'messageCount': 78},
            {'id': 'ch_016', 'name': 'Social Media', 'type': 'Standard', 'messageCount': 95},
            {'id': 'ch_017', 'name': 'Campaigns', 'type': 'Standard', 'messageCount': 56}
        ],
        'assignments': 10,
        'files': 34,
        'tags': ['Marketing', 'SEO', 'Social Media', 'Analytics']
    },
    {
        'id': 'team_005',
        'name': 'UX/UI Design Fundamentals',
        'description': 'User experience and interface design principles, prototyping, and user research methods',
        'owner': 'Mr. Kim',
        'ownerEmail': 'mr.kim@design.edu',
        'memberCount': 24,
        'created': '2024-03-15',
        'lastActivity': '2024-10-12 15:30:00',
        'isArchived': False,
        'channels': [
            {'id': 'ch_018', 'name': 'General', 'type': 'Standard', 'messageCount': 67},
            {'id': 'ch_019', 'name': 'Design Theory', 'type': 'Standard', 'messageCount': 89},
            {'id': 'ch_020', 'name': 'Prototyping', 'type': 'Standard', 'messageCount': 123},
            {'id': 'ch_021', 'name': 'User Research', 'type': 'Standard', 'messageCount': 45}
        ],
        'assignments': 6,
        'files': 52,
        'tags': ['UX/UI', 'Design', 'Prototyping', 'User Research']
    }
]

# Mock Channel Messages - Enhanced with more realistic conversations
MOCK_MESSAGES = {
    'ch_001': [
        {'id': 'msg_001', 'author': 'Dr. Smith', 'content': 'Welcome to Computer Science 101! This semester we\'ll cover fundamental programming concepts.', 'timestamp': '2024-10-15 09:00:00', 'avatar': '👨‍🏫'},
        {'id': 'msg_002', 'author': 'Alice Johnson', 'content': 'Thank you professor! Excited to learn!', 'timestamp': '2024-10-15 09:05:00', 'avatar': '👩‍🎓'},
        {'id': 'msg_003', 'author': 'Bob Wilson', 'content': 'Same here! Looking forward to the programming assignments.', 'timestamp': '2024-10-15 09:10:00', 'avatar': '👨‍💻'},
        {'id': 'msg_004', 'author': 'Dr. Smith', 'content': 'Great enthusiasm! First assignment will be posted tomorrow.', 'timestamp': '2024-10-15 09:15:00', 'avatar': '👨‍🏫'}
    ],
    'ch_002': [
        {'id': 'msg_005', 'author': 'Dr. Smith', 'content': 'Assignment 1: Basic Algorithms is now available in the Files tab', 'timestamp': '2024-10-15 10:00:00', 'avatar': '👨‍🏫'},
        {'id': 'msg_006', 'author': 'Dr. Smith', 'content': 'Due date: October 30th, 11:59 PM. Submit via Teams or email.', 'timestamp': '2024-10-15 10:01:00', 'avatar': '👨‍🏫'},
        {'id': 'msg_007', 'author': 'Alice Johnson', 'content': 'Professor, can we work in pairs for this assignment?', 'timestamp': '2024-10-15 10:30:00', 'avatar': '👩‍🎓'},
        {'id': 'msg_008', 'author': 'Dr. Smith', 'content': 'Yes, pairs are allowed but individual understanding is required.', 'timestamp': '2024-10-15 10:35:00', 'avatar': '👨‍🏫'}
    ],
    'ch_005': [
        {'id': 'msg_009', 'author': 'Prof. Johnson', 'content': 'Welcome to Web Development Bootcamp! Let\'s build amazing websites together! 🚀', 'timestamp': '2024-10-14 16:45:00', 'avatar': '👨‍💼'},
        {'id': 'msg_010', 'author': 'Sarah Chen', 'content': 'Can\'t wait to learn React!', 'timestamp': '2024-10-14 17:00:00', 'avatar': '👩‍💻'},
        {'id': 'msg_011', 'author': 'Mike Davis', 'content': 'Same here! HTML/CSS fundamentals first though 😄', 'timestamp': '2024-10-14 17:15:00', 'avatar': '👨‍🎨'}
    ],
    'ch_006': [
        {'id': 'msg_012', 'author': 'Prof. Johnson', 'content': 'HTML/CSS Module 1 is ready. Focus on semantic HTML and responsive design.', 'timestamp': '2024-10-14 14:00:00', 'avatar': '👨‍💼'},
        {'id': 'msg_013', 'author': 'Emma Wilson', 'content': 'The CSS Grid examples are really helpful!', 'timestamp': '2024-10-14 14:30:00', 'avatar': '👩‍🎨'},
        {'id': 'msg_014', 'author': 'Prof. Johnson', 'content': 'Great! Grid and Flexbox are essential for modern layouts.', 'timestamp': '2024-10-14 14:35:00', 'avatar': '👨‍💼'}
    ],
    'ch_010': [
        {'id': 'msg_015', 'author': 'Dr. Chen', 'content': 'Welcome to Data Science Workshop! Today we start with Python basics.', 'timestamp': '2024-10-13 11:20:00', 'avatar': '👨‍🔬'},
        {'id': 'msg_016', 'author': 'David Kim', 'content': 'Excited to dive into pandas and numpy!', 'timestamp': '2024-10-13 11:30:00', 'avatar': '👨‍💻'},
        {'id': 'msg_017', 'author': 'Lisa Zhang', 'content': 'Same! Machine learning here we come!', 'timestamp': '2024-10-13 11:35:00', 'avatar': '👩‍🔬'}
    ],
    'ch_011': [
        {'id': 'msg_018', 'author': 'Dr. Chen', 'content': 'Python Module 2: Data Manipulation with Pandas is now available.', 'timestamp': '2024-10-13 09:00:00', 'avatar': '👨‍🔬'},
        {'id': 'msg_019', 'author': 'Alex Brown', 'content': 'The Jupyter notebook examples are very detailed!', 'timestamp': '2024-10-13 09:15:00', 'avatar': '👨‍💻'},
        {'id': 'msg_020', 'author': 'Dr. Chen', 'content': 'Practice with the exercises to master data manipulation!', 'timestamp': '2024-10-13 09:20:00', 'avatar': '👨‍🔬'}
    ]
}

# Decorator for login required
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

@microsoft_teams_bp.before_request
def load_logged_in_user():
    """Load logged in user for Microsoft Teams routes"""
    user_id = session.get('user_id')
    if user_id:
        try:
            from app.services import UserService
            user_service = UserService()
            g.user = user_service.get_user_by_id(user_id)
        except:
            g.user = None
    else:
        g.user = None

@microsoft_teams_bp.route('/authorize')
@login_required
def authorize():
    """Mock Microsoft Teams authorization"""
    print("🔐 Microsoft Teams authorization requested (MOCK)")
    
    # Simulate OAuth flow delay
    import time
    time.sleep(1)
    
    # Store mock connection in session
    session['microsoft_teams_connected'] = True
    session['microsoft_teams_user'] = {
        'id': str(uuid.uuid4()),
        'name': g.user.username if g.user else 'Test User',
        'email': g.user.email if g.user else 'test@example.com'
    }
    
    flash('Successfully connected to Microsoft Teams!', 'success')
    return redirect(url_for('main_routes.dashboard') + '#class&open_teams_import=true')

@microsoft_teams_bp.route('/fetch_teams')
@login_required
def fetch_teams():
    """Fetch Microsoft Teams (Mock)"""
    try:
        # Check if user has Teams connection
        if not session.get('microsoft_teams_connected'):
            return jsonify({
                'success': False,
                'error': 'Not connected to Microsoft Teams',
                'needs_auth': True,
                'redirect_url': '/microsoft_teams/authorize'
            }), 401
        
        # Return mock teams data
        return jsonify({
            'success': True,
            'teams': MOCK_TEAMS
        })
        
    except Exception as e:
        print(f"Error fetching Microsoft Teams: {e}")
        return jsonify({
            'success': False,
            'error': f'Failed to fetch teams: {str(e)}'
        }), 500

@microsoft_teams_bp.route('/fetch_channels/<team_id>')
@login_required
def fetch_channels(team_id):
    """Fetch channels for a specific team (Mock)"""
    try:
        if not session.get('microsoft_teams_connected'):
            return jsonify({
                'success': False,
                'error': 'Not connected to Microsoft Teams'
            }), 401
        
        # Find team
        team = next((t for t in MOCK_TEAMS if t['id'] == team_id), None)
        if not team:
            return jsonify({
                'success': False,
                'error': 'Team not found'
            }), 404
        
        return jsonify({
            'success': True,
            'channels': team['channels']
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to fetch channels: {str(e)}'
        }), 500

@microsoft_teams_bp.route('/fetch_messages/<channel_id>')
@login_required
def fetch_messages(channel_id):
    """Fetch messages for a specific channel (Mock)"""
    try:
        if not session.get('microsoft_teams_connected'):
            return jsonify({
                'success': False,
                'error': 'Not connected to Microsoft Teams'
            }), 401
        
        messages = MOCK_MESSAGES.get(channel_id, [])
        
        return jsonify({
            'success': True,
            'messages': messages
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to fetch messages: {str(e)}'
        }), 500

@microsoft_teams_bp.route('/import_team', methods=['POST'])
@login_required
def import_team():
    """Import a Microsoft Teams team as a lesson"""
    try:
        data = request.get_json()
        team_id = data.get('teamId')
        settings = data.get('settings', {})
        
        if not team_id:
            return jsonify({'success': False, 'error': 'Team ID is required'}), 400
        
        if not session.get('microsoft_teams_connected'):
            return jsonify({
                'success': False,
                'error': 'Not connected to Microsoft Teams'
            }), 401
        
        # Find team
        team = next((t for t in MOCK_TEAMS if t['id'] == team_id), None)
        if not team:
            return jsonify({
                'success': False,
                'error': 'Team not found'
            }), 404
        
        # Create lesson from team data
        from app.services import LessonService
        lesson_service = LessonService()
        
        # Extract lesson data
        title = f"Imported: {team['name']}"
        description = team['description']
        user_id = session['user_id']
        
        lesson = lesson_service.create_lesson(user_id, title, description)
        
        return jsonify({
            'success': True,
            'lesson': {
                'id': lesson.id,
                'title': lesson.title,
                'description': lesson.description
            },
            'message': f'Successfully imported team "{team["name"]}"'
        })
        
    except Exception as e:
        print(f"Error importing Microsoft Teams team: {e}")
        return jsonify({
            'success': False,
            'error': f'Failed to import team: {str(e)}'
        }), 500

@microsoft_teams_bp.route('/team/<team_id>')
@login_required
def view_team(team_id):
    """View detailed information about a specific team"""
    try:
        if not session.get('microsoft_teams_connected'):
            return jsonify({
                'success': False,
                'error': 'Not connected to Microsoft Teams'
            }), 401
        
        # Find team
        team = next((t for t in MOCK_TEAMS if t['id'] == team_id), None)
        if not team:
            return jsonify({
                'success': False,
                'error': 'Team not found'
            }), 404
        
        return jsonify({
            'success': True,
            'team': team
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to fetch team details: {str(e)}'
        }), 500

@microsoft_teams_bp.route('/channel/<channel_id>')
@login_required
def view_channel(channel_id):
    """View detailed information about a specific channel"""
    try:
        if not session.get('microsoft_teams_connected'):
            return jsonify({
                'success': False,
                'error': 'Not connected to Microsoft Teams'
            }), 401
        
        # Find channel and its team
        channel = None
        team = None
        
        for t in MOCK_TEAMS:
            for ch in t['channels']:
                if ch['id'] == channel_id:
                    channel = ch
                    team = t
                    break
            if channel:
                break
        
        if not channel:
            return jsonify({
                'success': False,
                'error': 'Channel not found'
            }), 404
        
        # Get messages for this channel
        messages = MOCK_MESSAGES.get(channel_id, [])
        
        return jsonify({
            'success': True,
            'channel': channel,
            'team': team,
            'messages': messages
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to fetch channel details: {str(e)}'
        }), 500

@microsoft_teams_bp.route('/disconnect')
@login_required
def disconnect():
    """Disconnect from Microsoft Teams"""
    session.pop('microsoft_teams_connected', None)
    session.pop('microsoft_teams_user', None)
    
    flash('Disconnected from Microsoft Teams', 'info')
    return redirect(url_for('main_routes.dashboard'))