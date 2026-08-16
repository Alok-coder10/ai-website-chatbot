from app.models.message import Message

def test_message():
    message = Message(
        role="user",
        content="Hello",
        conversation_id=1
    )

    assert message.role == "user"
    assert message.content == "Hello"