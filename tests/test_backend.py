async def test_backend_status(backend_client):
    response = await backend_client.get("/status/123")

    assert response.status_code == 200
    assert response.json() == {
        "client_id": "123",
        "status": "Completed",
        "message": "Client onboarding completed successfully",
    }


async def test_backend_info_name(backend_client):
    response = await backend_client.get("/info/123/name")

    assert response.status_code == 200
    assert response.json() == {"client_id": "123", "field": "name", "value": "John"}


async def test_backend_rejects_unknown_field(backend_client):
    response = await backend_client.get("/info/123/age")

    assert response.status_code == 400
    assert response.json()["error"]["details"]["code"] == "invalid_field"
