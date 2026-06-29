from app.services.conversation_service import (
    ConversationService
)

service = ConversationService()

def test_service_has_create():
    assert hasattr(
        service,
        "create_conversation"
    )

def test_service_has_list():
    assert hasattr(
        service,
        "list_conversations"
    )

def test_service_has_delete():
    assert hasattr(
        service,
        "delete_conversation"
    )

def test_service_has_get():
    assert hasattr(
        service,
        "get_conversation"
    )