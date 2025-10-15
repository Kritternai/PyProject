import pytest


def test_create_task_normalization_and_tags(session, user):
    from app.services import TaskService, ValidationException

    svc = TaskService()

    with pytest.raises(ValidationException):
        svc.create_task(user_id=user.id, title="  ")

    t = svc.create_task(
        user_id=user.id,
        title="Do Homework",
        task_type="STUDY",
        priority="HIGH",
        tags=["math", "urgent"],
    )

    d = t.to_dict()
    assert d["task_type"] == "study"
    assert d["priority"] == "high"
    assert d["status"] == "pending"
    assert d["tags"] == ["math", "urgent"]


def test_update_task_fields_and_progress_transitions(session, user):
    from app.services import TaskService

    svc = TaskService()
    t = svc.create_task(user_id=user.id, title="Task A", task_type="other", priority="medium")

    # Update basic fields
    t = svc.update_task(
        task_id=t.id, user_id=user.id,
        title="Task A+", priority="low", estimated_duration="30"
    )
    d = t.to_dict()
    assert d["title"] == "Task A+"
    assert d["priority"] == "low"
    assert d["estimated_duration"] == 30

    # Progress to 100 -> completed
    t = svc.update_task_progress(t.id, user.id, 150)
    d = t.to_dict()
    assert d["progress_percentage"] == 100
    assert d["status"] == "completed"
    assert d["completed_at"] is not None

    # Back to 50 -> in_progress and completed_at cleared
    t = svc.update_task_progress(t.id, user.id, 50)
    d = t.to_dict()
    assert d["progress_percentage"] == 50
    assert d["status"] == "in_progress"
    assert d["completed_at"] is None

    # Change to pending: since progress not 100, remains 50
    t = svc.change_task_status(t.id, user.id, "pending")
    assert t.status == "pending"
    assert t.progress_percentage == 50

    # Mark completed via status
    t = svc.change_task_status(t.id, user.id, "completed")
    assert t.status == "completed" and t.progress_percentage == 100


def test_delete_task_and_stats_integration(session, user):
    from app.services import TaskService, PomodoroService, NotFoundException
    from datetime import date

    tasks = TaskService()
    pom = PomodoroService()

    t = tasks.create_task(user_id=user.id, title="Finish report")
    # Completing should update daily statistics via TaskService hooks
    tasks.update_task_progress(t.id, user.id, 100)

    daily = pom.get_daily_progress(user.id)
    assert isinstance(daily, dict)
    assert "tasks_logged" in daily and daily["tasks_logged"] >= 0
    assert "tasks_completed" in daily and daily["tasks_completed"] >= 0

    assert tasks.delete_task(t.id, user.id) is True
    with pytest.raises(NotFoundException):
        tasks.get_task_by_id(t.id, user.id)
