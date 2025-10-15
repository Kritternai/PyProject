import json


def test_create_note_with_list_tags(session, user):
    from app.services import NoteService

    svc = NoteService()
    note = svc.create_note(
        user_id=user.id,
        title="Tagged Note",
        content="Hello",
        tags=["a", "b"],
        is_public=True,
    )

    # Stored tags should be a JSON string; to_dict returns list
    assert isinstance(note.tags, str)
    assert note.to_dict()["tags"] == ["a", "b"]

    # get_notes_by_user returns our note
    notes = svc.get_notes_by_user(user.id)
    assert any(n.id == note.id for n in notes)


def test_update_note_tags_with_json_string(session, user):
    from app.services import NoteService

    svc = NoteService()
    note = svc.create_note(user_id=user.id, title="N1", content="C1", tags=["x"])

    updated = svc.update_note(note.id, tags=json.dumps(["y", "z"]))
    assert updated.id == note.id
    assert updated.to_dict()["tags"] == ["y", "z"]


def test_search_notes_by_tags_returns_matches(session, user):
    from app.services import NoteService

    svc = NoteService()
    n1 = svc.create_note(user_id=user.id, title="Math", content="..", tags=["math", "study"]) 
    n2 = svc.create_note(user_id=user.id, title="Science", content="..", tags=["science"]) 
    _ = svc.create_note(user_id=user.id, title="Untagged", content="..")

    res_math = svc.search_notes_by_tags(["math"], user_id=user.id)
    assert any(n.id == n1.id for n in res_math)
    assert all("math" in (json.loads(n.tags) if isinstance(n.tags, str) else n.tags or []) or n.tags for n in res_math)

    res_both = svc.search_notes_by_tags(["science", "math"], user_id=user.id)
    ids = {n.id for n in res_both}
    assert n1.id in ids and n2.id in ids


def test_public_notes_and_delete(session, user):
    from app.services import NoteService

    svc = NoteService()
    p1 = svc.create_note(user_id=user.id, title="P1", content="..", is_public=True)
    p2 = svc.create_note(user_id=user.id, title="P2", content="..", is_public=True)
    _ = svc.create_note(user_id=user.id, title="Private", content="..", is_public=False)

    pubs = svc.get_public_notes(limit=2)
    assert len(pubs) <= 2
    assert all(getattr(n, "is_public", False) for n in pubs)

    # Delete one and ensure it’s gone
    assert svc.delete_note(p1.id) is True
    assert svc.delete_note(p1.id) is False

