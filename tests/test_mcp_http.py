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


async def test_rest_facility_limit(mcp_client):
    response = await mcp_client.get("/api/v1/clients/123/facility")

    assert response.status_code == 200
    assert response.json() == {
        "client_id": "123",
        "client_name": "John Doe",
        "facility_limit_eur": 75_000_000,
        "currency": "EUR",
        "formatted_limit": "EUR 75,000,000",
    }


async def test_rest_outreach_summary(mcp_client):
    response = await mcp_client.get("/api/v1/clients/123/outreach-summary")

    assert response.status_code == 200
    body = response.json()
    assert body["outreach_count"] == 2
    assert body["questions_to_answer_count"] == 3
    assert "You should answer 3 questions" in body["summary"]


async def test_rest_session_authentication_flow(mcp_client):
    unauthenticated = await mcp_client.get(
        "/api/v1/client/onboarding-status",
        headers={"x-mcp-session-id": "rest-session"},
    )
    assert unauthenticated.status_code == 401
    assert unauthenticated.json() == {
        "error": "AUTH_REQUIRED",
        "message": "Please authenticate first using client_id and OTP",
    }

    failed_auth = await mcp_client.post(
        "/api/v1/authenticate",
        headers={"x-mcp-session-id": "rest-session"},
        json={"client_id": "123", "otp": "0000"},
    )
    assert failed_auth.status_code == 200
    assert failed_auth.json() == {"authenticated": False, "message": "Invalid OTP"}

    authenticated = await mcp_client.post(
        "/api/v1/authenticate",
        headers={"x-mcp-session-id": "rest-session"},
        json={"client_id": "123", "otp": "9632"},
    )
    assert authenticated.status_code == 200
    assert authenticated.json() == {
        "authenticated": True,
        "client_id": "123",
        "message": "Authentication successful",
    }

    status = await mcp_client.get(
        "/api/v1/client/onboarding-status",
        headers={"x-mcp-session-id": "rest-session"},
    )
    assert status.status_code == 200
    assert status.json()["client_id"] == "123"


async def test_mcp_tools_list(mcp_client):
    response = await mcp_client.post(
        "/mcp",
        json={"jsonrpc": "2.0", "id": 1, "method": "tools/list"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["jsonrpc"] == "2.0"
    assert [tool["name"] for tool in body["result"]["tools"]] == [
        "authenticate_client",
        "get_client_onboarding_status",
        "get_client_basic_info",
        "get_client_facility_limit",
        "summarize_client_outreach",
    ]


async def test_mcp_tool_call_requires_authentication(mcp_client):
    response = await mcp_client.post(
        "/mcp",
        headers={"x-mcp-session-id": "unauthenticated-session"},
        json={
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {
                "name": "get_client_onboarding_status",
                "arguments": {},
            },
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["result"]["structuredContent"] == {
        "error": "AUTH_REQUIRED",
        "message": "Please authenticate first using client_id and OTP",
    }


async def test_mcp_authenticate_client_invalid_otp(mcp_client):
    response = await mcp_client.post(
        "/mcp",
        headers={"x-mcp-session-id": "bad-otp-session"},
        json={
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {
                "name": "authenticate_client",
                "arguments": {"client_id": "123", "otp": "0000"},
            },
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["result"]["structuredContent"] == {
        "authenticated": False,
        "message": "Invalid OTP",
    }


async def test_mcp_authenticate_client_success(mcp_client):
    response = await mcp_client.post(
        "/mcp",
        headers={"x-mcp-session-id": "auth-session"},
        json={
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {
                "name": "authenticate_client",
                "arguments": {"client_id": "123", "otp": "9632"},
            },
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["result"]["structuredContent"] == {
        "authenticated": True,
        "client_id": "123",
        "message": "Authentication successful",
    }


async def test_mcp_tool_call(mcp_client):
    await mcp_client.post(
        "/mcp",
        headers={"x-mcp-session-id": "basic-info-session"},
        json={
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": "authenticate_client",
                "arguments": {"client_id": "123", "otp": "9632"},
            },
        },
    )
    response = await mcp_client.post(
        "/mcp",
        headers={"x-mcp-session-id": "basic-info-session"},
        json={
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {
                "name": "get_client_basic_info",
                "arguments": {"field": "name"},
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
    await mcp_client.post(
        "/mcp",
        headers={"x-mcp-session-id": "invalid-field-session"},
        json={
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": "authenticate_client",
                "arguments": {"client_id": "123", "otp": "9632"},
            },
        },
    )
    response = await mcp_client.post(
        "/mcp",
        headers={"x-mcp-session-id": "invalid-field-session"},
        json={
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "get_client_basic_info",
                "arguments": {"field": "age"},
            },
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["error"]["code"] == -32602
    assert body["error"]["data"]["code"] == "invalid_arguments"


async def test_mcp_facility_tool_call(mcp_client):
    await mcp_client.post(
        "/mcp",
        headers={"x-mcp-session-id": "facility-session"},
        json={
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": "authenticate_client",
                "arguments": {"client_id": "123", "otp": "9632"},
            },
        },
    )
    response = await mcp_client.post(
        "/mcp",
        headers={"x-mcp-session-id": "facility-session"},
        json={
            "jsonrpc": "2.0",
            "id": 4,
            "method": "tools/call",
            "params": {
                "name": "get_client_facility_limit",
                "arguments": {},
            },
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["result"]["structuredContent"]["client_name"] == "John Doe"
    assert body["result"]["structuredContent"]["facility_limit_eur"] == 75_000_000


async def test_mcp_outreach_tool_call(mcp_client):
    await mcp_client.post(
        "/mcp",
        headers={"x-mcp-session-id": "outreach-session"},
        json={
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": "authenticate_client",
                "arguments": {"client_id": "123", "otp": "9632"},
            },
        },
    )
    response = await mcp_client.post(
        "/mcp",
        headers={"x-mcp-session-id": "outreach-session"},
        json={
            "jsonrpc": "2.0",
            "id": 5,
            "method": "tools/call",
            "params": {
                "name": "summarize_client_outreach",
                "arguments": {},
            },
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["result"]["structuredContent"]["outreach_count"] == 2
    assert body["result"]["structuredContent"]["questions_to_answer_count"] == 3
