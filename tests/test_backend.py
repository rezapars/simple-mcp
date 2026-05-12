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


async def test_backend_facility(backend_client):
    response = await backend_client.get("/facility/123")

    assert response.status_code == 200
    assert response.json() == {
        "client_id": "123",
        "client_name": "John Doe",
        "facility_limit_eur": 75_000_000,
        "currency": "EUR",
        "formatted_limit": "EUR 75,000,000",
    }


async def test_backend_outreach_summary(backend_client):
    response = await backend_client.get("/outreach/123/summary")

    assert response.status_code == 200
    body = response.json()
    assert body["client_id"] == "123"
    assert body["client_name"] == "John Doe"
    assert body["outreach_count"] == 2
    assert body["questions_to_answer_count"] == 5
    assert "Annual facility review" in body["reasons"]
    assert len(body["outreaches"]) == 2
