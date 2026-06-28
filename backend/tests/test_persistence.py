from app.services.conversation_service import (
    ConversationService
)

service = ConversationService()

def test_conversation_service_loaded():
    assert service is not None