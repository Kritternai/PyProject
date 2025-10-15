import pytest
from datetime import datetime
from app import create_app, db
from app.models.lesson import LessonModel

import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


@pytest.fixture
def app_context():
    app = create_app('testing')
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()
def test_create_lesson_default_values(app_context):
    lesson = LessonModel(
        user_id="1234",
        title="Python Basics",
        description="Introduction to Python programming"
    )
    db.session.add(lesson)
    db.session.commit()

    # ตรวจสอบค่า default
    assert lesson.status == "not_started"
    assert lesson.difficulty_level == "beginner"
    assert lesson.progress_percentage == 0
    assert lesson.is_favorite is False
    assert lesson.created_at is not None
    assert isinstance(lesson.created_at, datetime)

# def test_lesson_to_domain_entity(app_context, mocker):
#     # Mock Domain Entities
#     mocker.patch("app.domain.entities.lesson.LessonStatus", lambda x: x)
#     mocker.patch("app.domain.entities.lesson.DifficultyLevel", lambda x: x)
#     mocker.patch("app.domain.entities.lesson.SourcePlatform", lambda x: x)
#     mock_lesson_class = mocker.patch("app.domain.entities.lesson.Lesson")
# 
#     lesson = LessonModel(
#         user_id="user-123",
#         title="Algebra Lesson",
#         status="in_progress",
#         difficulty_level="intermediate",
#         source_platform="khan_academy"
#     )
#     lesson.to_domain_entity()
# 
#     mock_lesson_class.assert_called_once()  # ตรวจว่าถูกสร้าง entity 1 ครั้ง

# def test_from_domain_entity(app_context):
#     class DummyLesson:
#         id = "abc"
#         user_id = "user-1"
#         title = "Math Lesson"
#         description = "Algebra basics"
#         status = type("obj", (), {"value": "completed"})
#         progress_percentage = 100
#         difficulty_level = type("obj", (), {"value": "beginner"})
#         estimated_duration = 30
#         color_theme = 2
#         is_favorite = True
#         source_platform = type("obj", (), {"value": "manual"})
#         external_id = "ext-001"
#         external_url = "http://example.com"
#         author_name = "Teacher A"
#         subject = "Math"
#         grade_level = "Grade 10"
#         total_sections = 10
#         completed_sections = 10
#         total_time_spent = 100
#         created_at = datetime.utcnow()
#         updated_at = datetime.utcnow()
# 
#     model = LessonModel.from_domain_entity(DummyLesson())
#     assert model.title == "Math Lesson"
#     assert model.is_favorite is True
#     assert model.progress_percentage == 100
#     assert model.source_platform == "manual"
