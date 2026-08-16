from app.schemas.conversation import (
    ConversationCreate
)


def test_conversation_create():
    schema = ConversationCreate(
        title="My Chat"
    )
    assert schema.title == "My Chat"