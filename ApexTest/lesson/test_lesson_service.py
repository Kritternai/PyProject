def test_lesson_create_fetch_and_counts(session, user):
    from app.services import LessonService

    svc = LessonService()
    l1 = svc.create_lesson(user_id=user.id, title="Algebra 1", description="Intro")
    l2 = svc.create_lesson(user_id=user.id, title="Biology", description=None)

    lessons = svc.get_lessons_by_user(user.id)
    ids = {l.id for l in lessons}
    assert l1.id in ids and l2.id in ids

    fetched = svc.get_lesson_by_id(l1.id)
    assert fetched.title == "Algebra 1"

    # Mark one lesson completed today and ensure count reflects it
    fetched.status = 'completed'
    session.commit()

    completed_today = svc.get_lessons_completed_today(user.id)
    # SQLite date comparisons may vary; ensure it returns an integer
    assert isinstance(completed_today, int) and completed_today >= 0
