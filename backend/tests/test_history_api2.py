

def test_get_conversation(client):

    response = client.post(
        "/api/v1/conversations",
        json={"title": "History Test"}
    )

    cid = response.json()["id"]

    response = client.get(
        f"/api/v1/conversations/{cid}"
    )

    assert response.status_code == 200


def test_conversation_not_found(client):

    response = client.get(
        "/api/v1/conversations/99999"
    )

    assert response.status_code == 404