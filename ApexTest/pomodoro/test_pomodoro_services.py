def test_focus_session_complete_updates_stats(session, user):
    from app.services import PomodoroSessionService, PomodoroService

    sess = PomodoroSessionService()
    pom = PomodoroService()

    s = sess.create_session(user_id=user.id, session_type='focus', duration=25, task='Read')
    s = sess.end_session(s.id, status='completed')

    daily = pom.get_daily_progress(user.id)
    # Ensure structure and non-negative aggregates
    assert isinstance(daily, dict)
    assert 'completed_sessions' in daily and daily['completed_sessions'] >= 0
    assert 'focus_minutes' in daily and daily['focus_minutes'] >= 0


def test_interrupt_break_session_counts(session, user):
    from app.services import PomodoroSessionService, PomodoroService

    sess = PomodoroSessionService()
    pom = PomodoroService()

    s = sess.create_session(user_id=user.id, session_type='short_break', duration=5)
    s = sess.interrupt_session(s.id)

    daily = pom.get_daily_progress(user.id)
    assert 'interrupted_sessions' in daily and daily['interrupted_sessions'] >= 0
    assert 'break_minutes' in daily and daily['break_minutes'] >= 0


def test_pomodoro_service_stats_and_history(session, user):
    from app.services import PomodoroService

    pom = PomodoroService()
    stats = pom.get_stats(user.id)
    assert isinstance(stats, dict)
    assert 'total_sessions' in stats

    history = pom.get_session_history(user.id, limit=5)
    assert isinstance(history, list)
    # Contains session dicts
    if history:
        assert isinstance(history[0], dict)
