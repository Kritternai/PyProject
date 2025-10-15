import json


def test_note_model_to_dict_parses_tags(session, user):
    from app.models.note import NoteModel

    note = NoteModel(
        user_id=user.id,
        title="My Note",
        content="Some content",
        tags=json.dumps(["math", "study"])  # store JSON string
    )
    session.add(note)
    session.commit()

    data = note.to_dict()
    assert data["title"] == "My Note"
    assert data["content"] == "Some content"
    assert data["tags"] == ["math", "study"]
    assert isinstance(data["created_at"], str)


def test_note_model_to_dict_malformed_tags_returns_empty_list(session, user):
    from app.models.note import NoteModel

    note = NoteModel(
        user_id=user.id,
        title="Bad Tags",
        content="--",
        tags="not-json"
    )
    session.add(note)
    session.commit()

    data = note.to_dict()
    assert data["tags"] == []

