from app.schemas.chat import ChatRequest

def test_chat_has_conversation_id():
    req = ChatRequest(
        message="hello"
    )
    assert req.conversation_id is None