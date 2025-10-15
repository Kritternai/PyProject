def test_tag_parsing_invalid_string(session, user):
    from app.models.note import NoteModel

    note = NoteModel(
        user_id=user.id,
        title="T",
        content="C",
        tags="[invalid json"
    )
    session.add(note)
    session.commit()

    data = note.to_dict()
    assert data["tags"] == []


def test_tag_parsing_list_to_json_roundtrip(session, user):
    from app.services import NoteService

    svc = NoteService()
    note = svc.create_note(user_id=user.id, title="T2", content="C2", tags=["alpha", "beta"]) 
    assert note.to_dict()["tags"] == ["alpha", "beta"]

