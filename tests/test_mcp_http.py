async def test_rest_onboarding_status(mcp_client):
    response = await mcp_client.get("/api/v1/clients/123/onboarding-status")

    assert response.status_code == 200
    assert response.json() == {
        "client_id": "123",
        "status": "Completed",
        "message": "Client onboarding completed successfully",
    }


async def test_rest_basic_info_family(mcp_client):
    response = await mcp_client.get("/api/v1/clients/123/basic-info/family")

    assert response.status_code == 200
    assert response.json() == {"client_id": "123", "field": "family", "value": "Doe"}


async def test_mcp_tools_list(mcp_client):
    response = await mcp_client.post(
        "/mcp",
        json={"jsonrpc": "2.0", "id": 1, "method": "tools/list"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["jsonrpc"] == "2.0"
    assert body["result"]["tools"][0]["name"] == "get_client_onboarding_status"


async def test_mcp_tool_call(mcp_client):
    response = await mcp_client.post(
        "/mcp",
        json={
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {
                "name": "get_client_basic_info",
                "arguments": {"client_id": "123", "field": "name"},
            },
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["result"]["structuredContent"] == {
        "client_id": "123",
        "field": "name",
        "value": "John",
    }


async def test_mcp_tool_call_invalid_field(mcp_client):
    response = await mcp_client.post(
        "/mcp",
        json={
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "get_client_basic_info",
                "arguments": {"client_id": "123", "field": "age"},
            },
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["error"]["code"] == -32602
    assert body["error"]["data"]["code"] == "invalid_arguments"
