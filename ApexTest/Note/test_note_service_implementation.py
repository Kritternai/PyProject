def test_get_recent_and_stats(session, user):
    from app.services import NoteService

    svc = NoteService()
    # Create different statuses and visibility
    n1 = svc.create_note(user_id=user.id, title="A", content="C", status="pending", is_public=True)
    n2 = svc.create_note(user_id=user.id, title="B", content="C", status="in-progress", is_public=False)
    n3 = svc.create_note(user_id=user.id, title="C", content="C", status="completed", is_public=True)

    # Recent notes limited
    recents = svc.get_recent_notes(user_id=user.id, limit=2)
    assert len(recents) == 2

    # Stats reflect counts
    stats = svc.get_note_statistics(user_id=user.id)
    assert stats["total"] >= 3
    assert stats["pending"] >= 1
    assert stats["in_progress"] >= 1
    assert stats["completed"] >= 1
    assert stats["public"] >= 2
    assert stats["private"] >= 1

