#from app.schemas import response
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_chat():
    response = client.post(
        "/api/v1/chat", 
        json = {
            "message":"Hello"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "response" in data