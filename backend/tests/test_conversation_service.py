import pytest
from app.services.conversation_service import (
    ConversationService
)

service = ConversationService()

def test_service_exists():
    assert service is not None