from app.models.conversation import Conversation

def test_conversation():
    conversation = Conversation(
        title="Test"
    )

    assert conversation.title == "Test"