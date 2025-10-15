import pytest
import json
from unittest.mock import patch, MagicMock
from datetime import datetime, timezone
from app import create_app
from app.models.user import UserModel
from app.models.lesson import LessonModel

@pytest.fixture
def client():
    """Create and configure a new app instance for each test."""
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    with app.app_context():
        with app.test_client() as client:
            # db.create_all() might be needed here if you have a test DB
            yield client

@pytest.fixture
def mock_user():
    """Fixture for a mock user that is active."""
    user = UserModel(id='test_user_123', username='testuser', email='test@example.com', is_active=True)
    return user

@pytest.fixture
def mock_lesson(mock_user):
    """Fixture for a mock lesson."""
    lesson = LessonModel(
        id="1",
        user_id=mock_user.id,
        title="Test Lesson",
        description="A test lesson",
                    created_at=datetime.now(timezone.utc),
                    updated_at=datetime.now(timezone.utc)    )
    return lesson

def test_create_lesson_success(client, mock_user, mock_lesson):
    """
    Test case for successfully creating a new lesson.
    Simulates a logged-in user by setting a session variable and patching the service layer.
    """
    # Patch the method used by the auth middleware to get the user
    mock_lesson = MagicMock()
    mock_lesson.to_dict.return_value = {
        'id': 'mock_lesson_id',
        'title': 'Test Lesson',
        'description': 'A lesson for testing purposes.',
        'user_id': mock_user.id
    }
    with patch('app.services.UserService.get_user_by_id') as mock_get_user:
        mock_get_user.return_value = mock_user

        # Patch the LessonService for the controller logic
        with patch('app.services.LessonService.create_lesson') as mock_create_lesson:
            mock_create_lesson.return_value = mock_lesson

            # Simulate a logged-in session by setting the user_id
            with client.session_transaction() as sess:                sess['user_id'] = mock_user.id

            lesson_data = {
                'title': 'Test Lesson',
                'description': 'A lesson for testing purposes.'
            }
            # Make the request with the session and correct headers
            response = client.post('/api/lessons',
                                   data=json.dumps(lesson_data),
                                   content_type='application/json',
                                   headers={'Accept': 'application/json'})

            # Assertions
            print(f"Response Status Code: {response.status_code}")
            print(f"Response Data: {response.data}")
            assert response.status_code == 201
            response_data = response.get_json()
            assert response_data['success'] is True
            assert response_data['data']['title'] == 'Test Lesson'

def test_create_lesson_no_title(client, mock_user):
    """
    Test case for creating a lesson without a title, which should fail with a 400 error.
    """
    # Patch the method used by the auth middleware to get the user
    with patch('app.services.UserService.get_user_by_id') as mock_get_user:
        mock_get_user.return_value = mock_user

        with client.session_transaction() as sess:
            sess['user_id'] = mock_user.id

        lesson_data = {'description': 'A lesson without a title.'}

        response = client.post('/api/lessons',
                               data=json.dumps(lesson_data),
                               content_type='application/json',
                               headers={'Accept': 'application/json'})

        # Assertions
        assert response.status_code == 400
        response_data = response.get_json()
        assert response_data['success'] is False
        assert response_data['message'] == 'Title is required'

def test_create_lesson_not_authenticated(client):
    """
    Test case for creating a lesson when not authenticated.
    Should be caught by the @login_required decorator and return a 401 error.
    """
    lesson_data = {'title': 'Test Lesson'}

    # Make the request without a session
    response = client.post('/api/lessons',
                           data=json.dumps(lesson_data),
                           content_type='application/json',
                           headers={'Accept': 'application/json'})

    # The @login_required decorator should return a 401
    assert response.status_code == 401
    response_data = response.get_json()
    assert response_data['success'] is False
    assert response_data['message'] == 'Authentication required'