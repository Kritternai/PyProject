import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from datetime import datetime
from app import create_app, db
from app.models.lesson import LessonModel
from app.models.lesson_section import LessonSectionModel

@pytest.fixture
def app_context():
    app = create_app('testing')
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()
def test_create_lesson_section(app_context):
    # สร้าง Lesson ก่อน (เพราะ lesson_section มี foreign key)
    lesson = LessonModel(user_id="user123", title="Python Basics")
    db.session.add(lesson)
    db.session.commit()

    # ทดสอบสร้าง Section
    section = LessonSectionModel(
        lesson_id=lesson.id,
        title="Introduction",
        content="This is the first section."
    )
    db.session.add(section)
    db.session.commit()

    assert section.id is not None
    assert section.section_type == "text"
    assert section.order_index == 0
    assert isinstance(section.created_at, datetime)
    assert isinstance(section.updated_at, datetime)
    assert f"{section.title}" in repr(section)
def test_foreign_key_constraint(app_context):
    # พยายามสร้างโดยไม่มี lesson_id → ต้อง error
    with pytest.raises(Exception):
        invalid_section = LessonSectionModel(
            title="No Lesson",
            content="This should fail."
        )
        db.session.add(invalid_section)
        db.session.commit()
def test_order_index_manual(app_context):
    lesson = LessonModel(user_id="user456", title="Flask App")
    db.session.add(lesson)
    db.session.commit()

    s1 = LessonSectionModel(lesson_id=lesson.id, title="Part 1", order_index=1)
    s2 = LessonSectionModel(lesson_id=lesson.id, title="Part 2", order_index=2)
    db.session.add_all([s1, s2])
    db.session.commit()

    assert s1.order_index == 1
    assert s2.order_index == 2
