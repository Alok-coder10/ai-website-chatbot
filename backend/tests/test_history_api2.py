

def test_get_conversation(client):

    response = client.get(
        "/api/v1/conversations/1"
    )

    assert response.status_code == 200