"""
Microsoft Teams API Integration Routes (Mockup)
Fake integration that simulates real Microsoft Teams API calls
"""

from flask import Blueprint, render_template, request, redirect, url_for, session, g, flash, jsonify, current_app
from functools import wraps
from datetime import datetime, timedelta
import random
import uuid
from sqlalchemy import text

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

def create_mockup_data_for_imported_team(lesson_id, team, settings, user_id):
    """Create mockup data for Stream, Classwork, People, and Grades after importing a team"""
    try:
        from app import db
        from app.models.task import TaskModel
        from app.models.note import NoteModel
        from app.models.grade import GradeItem
        
        print(f"🎯 Creating mockup data for lesson {lesson_id} from team {team['name']} for user {user_id}")
        
        # 1. Create Stream mockup data (Notes/Announcements)
        if settings.get('importChannels', True):
            create_stream_mockup(lesson_id, team, user_id)
        
        # 2. Create Classwork mockup data (Tasks)
        if settings.get('importAssignments', True):
            create_classwork_mockup(lesson_id, team, user_id)
        
        # 3. Create People mockup data (Notes for member management)
        if settings.get('importMembers', True):
            create_people_mockup(lesson_id, team, user_id)
        
        # 4. Create Grades mockup data (Grade items)
        if settings.get('importFiles', True):  # Using files setting for grades
            create_grades_mockup(lesson_id, team, user_id)
        
        print(f"✅ Mockup data created successfully for lesson {lesson_id}")
        
    except Exception as e:
        print(f"❌ Error creating mockup data: {e}")
        import traceback
        traceback.print_exc()

def create_stream_mockup(lesson_id, team, user_id):
    """Create Stream mockup data from team channels and messages"""
    try:
        from app.models.stream import StreamPost
        from app import db
        from datetime import datetime, timedelta
        
        print(f"🎯 Creating Stream mockup for lesson {lesson_id} with user {user_id}")
        
        # Create announcement posts
        stream_posts = []
        
        # Welcome announcement
        welcome_post = StreamPost(
            id=str(uuid.uuid4()),
            lesson_id=lesson_id,
            user_id=user_id,
            type='announcement',
            title=f"Welcome to {team['name']}!",
            content=f"""🎉 Welcome to {team['name']}!

This class has been imported from Microsoft Teams with {team.get('memberCount', 0)} members and {len(team.get('channels', []))} channels.

**Class Information:**
- 👥 {team.get('memberCount', 0)} members
- 💬 {len(team.get('channels', []))} channels  
- 📅 Created {team.get('created', 'recently')}
- 📝 {team.get('description', 'No description available')}

Feel free to explore the different channels and start collaborating!""",
            is_pinned=True,
            allow_comments=True,
            created_at=datetime.now()
        )
        stream_posts.append(welcome_post)
        
        # Channel updates
        channel_update_post = StreamPost(
            id=str(uuid.uuid4()),
            lesson_id=lesson_id,
            user_id=user_id,
            type='announcement',
            title='Channel Information',
            content=f"""📢 **Channel Updates**

Here's an overview of the channels that were imported:

**General Channel**
- 💬 Most active channel for class discussions
- 📊 Contains general announcements and updates
- 👥 All members have access

**Assignments Channel** 
- 📚 Assignment-related discussions
- 📝 Submission guidelines and deadlines
- 💡 Tips and clarifications

**Resources Channel**
- 📖 Study materials and resources
- 🔗 Important links and references
- 📁 Shared documents and files

**Q&A Channel**
- ❓ Questions and answers
- 🤝 Peer support and collaboration
- 💬 Quick discussions""",
            is_pinned=False,
            allow_comments=True,
            created_at=datetime.now() + timedelta(minutes=5)
        )
        stream_posts.append(channel_update_post)
        
        # Add to database
        for post in stream_posts:
            db.session.add(post)
        
        db.session.commit()
        print(f"📢 Created {len(stream_posts)} stream posts")
        print(f"📢 Stream posts: {[post.title for post in stream_posts]}")
        
    except Exception as e:
        print(f"❌ Error creating stream mockup: {e}")
        import traceback
        traceback.print_exc()

def create_classwork_mockup(lesson_id, team, user_id):
    """Create Classwork mockup data from team assignments"""
    try:
        from app import db
        from datetime import datetime, timedelta
        
        # Sample assignments based on team type
        if 'Computer Science' in team['name']:
            assignments = [
                {
                    'title': 'Programming Assignment 1: Basic Algorithms',
                    'description': 'Implement basic sorting algorithms and analyze their time complexity.',
                    'due_date': datetime.now() + timedelta(days=7),
                    'points': 100
                },
                {
                    'title': 'Data Structures Project',
                    'description': 'Create and implement a custom data structure with documentation.',
                    'due_date': datetime.now() + timedelta(days=14),
                    'points': 150
                },
                {
                    'title': 'Algorithm Analysis Quiz',
                    'description': 'Complete the online quiz covering algorithm analysis concepts.',
                    'due_date': datetime.now() + timedelta(days=3),
                    'points': 50
                }
            ]
        elif 'Web Development' in team['name']:
            assignments = [
                {
                    'title': 'HTML/CSS Portfolio',
                    'description': 'Create a responsive portfolio website using HTML and CSS.',
                    'due_date': datetime.now() + timedelta(days=10),
                    'points': 100
                },
                {
                    'title': 'JavaScript Interactive App',
                    'description': 'Build an interactive web application using vanilla JavaScript.',
                    'due_date': datetime.now() + timedelta(days=21),
                    'points': 200
                },
                {
                    'title': 'React Component Library',
                    'description': 'Create reusable React components with proper documentation.',
                    'due_date': datetime.now() + timedelta(days=28),
                    'points': 150
                }
            ]
        elif 'Data Science' in team['name']:
            assignments = [
                {
                    'title': 'Data Analysis Report',
                    'description': 'Analyze a dataset using Python and create a comprehensive report.',
                    'due_date': datetime.now() + timedelta(days=12),
                    'points': 150
                },
                {
                    'title': 'Machine Learning Model',
                    'description': 'Build and evaluate a machine learning model using scikit-learn.',
                    'due_date': datetime.now() + timedelta(days=21),
                    'points': 200
                },
                {
                    'title': 'Statistical Analysis Assignment',
                    'description': 'Perform statistical analysis on provided data using R or Python.',
                    'due_date': datetime.now() + timedelta(days=7),
                    'points': 100
                }
            ]
        else:
            # Generic assignments
            assignments = [
                {
                    'title': 'Research Assignment 1',
                    'description': 'Research and analyze current trends in the field.',
                    'due_date': datetime.now() + timedelta(days=10),
                    'points': 100
                },
                {
                    'title': 'Project Presentation',
                    'description': 'Present your findings to the class with visual aids.',
                    'due_date': datetime.now() + timedelta(days=21),
                    'points': 150
                },
                {
                    'title': 'Final Exam',
                    'description': 'Comprehensive exam covering all course material.',
                    'due_date': datetime.now() + timedelta(days=35),
                    'points': 200
                }
            ]
        
        # Create tasks using raw SQL to avoid model mismatch
        for assignment in assignments:
            task_id = str(uuid.uuid4())
            db.session.execute(
                text("""INSERT INTO task (id, user_id, title, description, status, priority, due_date, created_at, updated_at) 
                   VALUES (:task_id, :user_id, :title, :description, :status, :priority, :due_date, :created_at, :updated_at)"""),
                {
                    'task_id': task_id,
                    'user_id': user_id,
                    'title': assignment['title'],
                    'description': assignment['description'],
                    'status': 'active',
                    'priority': 'medium',
                    'due_date': assignment['due_date'],
                    'created_at': datetime.now(),
                    'updated_at': datetime.now()
                }
            )
            print(f"📚 Created task: {assignment['title']}")
        
        db.session.commit()
        print(f"📚 Created {len(assignments)} classwork assignments")
        
    except Exception as e:
        print(f"❌ Error creating classwork mockup: {e}")

def create_people_mockup(lesson_id, team, user_id):
    """Create People mockup data from team members"""
    try:
        from app.models.note import NoteModel
        from app import db
        from datetime import datetime
        
        # Create member management notes
        people_notes = []
        
        # Member list note
        member_count = team.get('memberCount', 0)
        member_note = NoteModel(
            user_id=user_id,
            lesson_id=lesson_id,
            title=f"Class Members ({member_count} total)",
            content=f"""
            <div class="members-overview">
                <h5>👥 Class Members</h5>
                <p>This class has {member_count} members imported from Microsoft Teams.</p>
                <div class="member-stats">
                    <div class="stat-card">
                        <span class="stat-number">{member_count}</span>
                        <span class="stat-label">Total Members</span>
                    </div>
                    <div class="stat-card">
                        <span class="stat-number">1</span>
                        <span class="stat-label">Instructors</span>
                    </div>
                    <div class="stat-card">
                        <span class="stat-number">{member_count - 1}</span>
                        <span class="stat-label">Students</span>
                    </div>
                </div>
                <div class="member-actions">
                    <button class="btn btn-primary btn-sm">View All Members</button>
                    <button class="btn btn-outline-primary btn-sm">Add Members</button>
                </div>
            </div>
            """,
            note_type='member_management',
            created_at=datetime.now()
        )
        people_notes.append(member_note)
        
        # Role management note
        role_note = NoteModel(
            user_id=user_id,
            lesson_id=lesson_id,
            title="Member Roles & Permissions",
            content=f"""
            <div class="roles-management">
                <h5>🔐 Member Roles</h5>
                <div class="role-list">
                    <div class="role-item">
                        <strong>Instructor:</strong> {team.get('owner', 'Team Owner')}
                        <span class="badge bg-warning">Full Access</span>
                    </div>
                    <div class="role-item">
                        <strong>Students:</strong> {member_count - 1} members
                        <span class="badge bg-info">Standard Access</span>
                    </div>
                </div>
                <p class="text-muted">Roles have been imported from Microsoft Teams and can be managed here.</p>
            </div>
            """,
            note_type='role_management',
            created_at=datetime.now()
        )
        people_notes.append(role_note)
        
        # Add to database
        for note in people_notes:
            db.session.add(note)
        
        db.session.commit()
        print(f"👥 Created {len(people_notes)} people management notes")
        
    except Exception as e:
        print(f"❌ Error creating people mockup: {e}")

def create_grades_mockup(lesson_id, team, user_id):
    """Create Grades mockup data from team assignments"""
    try:
        from app.models.grade import GradeCategory, GradeItem
        from app import db
        from datetime import datetime, timedelta
        
        # Create grade categories first
        categories = []
        category_data = [
            {'name': 'Assignments', 'weight': 40.0, 'color': '#1976D2', 'total_points': 300.0},
            {'name': 'Projects', 'weight': 30.0, 'color': '#48BB78', 'total_points': 200.0},
            {'name': 'Exams', 'weight': 20.0, 'color': '#F6AD55', 'total_points': 150.0},
            {'name': 'Participation', 'weight': 10.0, 'color': '#9F7AEA', 'total_points': 50.0}
        ]
        
        for i, cat_data in enumerate(category_data):
            category = GradeCategory(
                lesson_id=lesson_id,
                name=cat_data['name'],
                description=f"{cat_data['name']} component for {team['name']}",
                weight=cat_data['weight'],
                total_points=cat_data['total_points'],
                color=cat_data['color'],
                icon='bi-clipboard',
                order_index=i,
                created_at=datetime.now()
            )
            categories.append(category)
            db.session.add(category)
        
        db.session.flush()  # Get category IDs
        
        # Create grade items
        grade_items = []
        item_data = [
            {'name': 'Programming Assignment 1', 'points': 100.0, 'due_days': 7, 'category_idx': 0},
            {'name': 'Programming Assignment 2', 'points': 100.0, 'due_days': 14, 'category_idx': 0},
            {'name': 'Data Structures Project', 'points': 150.0, 'due_days': 21, 'category_idx': 1},
            {'name': 'Algorithm Analysis Quiz', 'points': 50.0, 'due_days': 3, 'category_idx': 2},
            {'name': 'Class Participation', 'points': 50.0, 'due_days': 30, 'category_idx': 3}
        ]
        
        for item_info in item_data:
            grade_item = GradeItem(
                lesson_id=lesson_id,
                category_id=categories[item_info['category_idx']].id,
                name=item_info['name'],
                description=f"{item_info['name']} for {team['name']}",
                points_possible=item_info['points'],
                due_date=datetime.now() + timedelta(days=item_info['due_days']),
                published_date=datetime.now(),
                is_published=True
            )
            grade_items.append(grade_item)
            db.session.add(grade_item)
        
        db.session.commit()
        print(f"📊 Created {len(categories)} grade categories and {len(grade_items)} grade items")
        
    except Exception as e:
        print(f"❌ Error creating grades mockup: {e}")
        import traceback
        traceback.print_exc()

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
        
        lesson = lesson_service.create_lesson(
            user_id=user_id, 
            title=title, 
            description=description,
            source_platform='microsoft_teams',
            external_id=team_id
        )
        
        # Create mockup data for Stream, Classwork, People, and Grades
        try:
            print(f"🎯 Starting mockup creation for lesson {lesson.id}")
            create_mockup_data_for_imported_team(lesson.id, team, settings, session['user_id'])
            print(f"✅ Mockup creation completed for lesson {lesson.id}")
        except Exception as e:
            print(f"❌ Error in mockup creation: {e}")
            import traceback
            traceback.print_exc()
        
        return jsonify({
            'success': True,
            'lesson': {
                'id': lesson.id,
                'title': lesson.title,
                'description': lesson.description
            },
            'message': f'Successfully imported team "{team["name"]}" with mockup data'
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

@microsoft_teams_bp.route('/create_mockup/<lesson_id>')
@login_required
def create_mockup_for_lesson(lesson_id):
    """Create mockup data for an existing lesson (for testing)"""
    try:
        # Get a sample team for testing
        sample_team = MOCK_TEAMS[0]  # Computer Science 101
        settings = {
            'importChannels': True,
            'importAssignments': True,
            'importMembers': True,
            'importFiles': True
        }
        
        print(f"🎯 Creating mockup for lesson {lesson_id}")
        create_mockup_data_for_imported_team(lesson_id, sample_team, settings, session['user_id'])
        
        return jsonify({
            'success': True,
            'message': f'Mockup data created for lesson {lesson_id}'
        })
        
    except Exception as e:
        print(f"❌ Error creating mockup: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@microsoft_teams_bp.route('/disconnect')
@login_required
def disconnect():
    """Disconnect from Microsoft Teams"""
    session.pop('microsoft_teams_connected', None)
    session.pop('microsoft_teams_user', None)
    
    flash('Disconnected from Microsoft Teams', 'info')
    return redirect(url_for('main_routes.dashboard'))