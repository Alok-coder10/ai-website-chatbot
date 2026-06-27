import pytest
from pydantic import ValidationError
from app.schemas.chat import ChatRequest

def test_chat_request():

    data = ChatRequest(message="Hello")

    assert data.message == "Hello"


def test_empty_message():

    with pytest.raises(ValidationError):

        ChatRequest(message="")