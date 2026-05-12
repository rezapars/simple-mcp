# Client Onboarding MCP for Microsoft Copilot and Teams

Minimal Python 3.12 project with:

- MCP server with four tools
- Separate mock backend server
- REST/OpenAPI facade
- Microsoft 365 Copilot plugin package files
- Microsoft Teams app manifest
- Docker, tests, local setup, auth placeholders, and examples

Architecture:

```text
[Microsoft Teams]
        |
        v
[Microsoft Copilot]
        |
        v
[MCP Server]
        |
        v
[Mock Backend Server]
```

## Folder Tree

```text
.
|-- appPackage/
|   |-- adaptive-cards/
|   |   `-- client-result.json
|   |-- color.png
|   |-- declarativeAgent.json
|   |-- manifest.json
|   |-- mcp-tools.json
|   |-- openapi.yaml
|   |-- outline.png
|   |-- plugin.json
|   `-- plugin.openapi.json
|-- examples/
|   |-- curl.md
|   |-- json-rpc.md
|   |-- requests.http
|   `-- responses/
|       |-- basic_info_family.json
|       |-- basic_info_name.json
|       |-- error_invalid_field.json
|       |-- facility_limit.json
|       |-- onboarding_status.json
|       `-- outreach_summary.json
|-- mcp_server/
|   |-- __init__.py
|   |-- __main__.py
|   |-- app.py
|   |-- auth.py
|   |-- backend_client.py
|   |-- config.py
|   |-- errors.py
|   |-- jsonrpc.py
|   |-- logging_config.py
|   |-- mcp_app.py
|   |-- models.py
|   |-- routes.py
|   `-- tool_registry.py
|-- mock_backend/
|   |-- __init__.py
|   |-- __main__.py
|   |-- app.py
|   |-- config.py
|   |-- logging_config.py
|   |-- models.py
|   `-- routes.py
|-- tests/
|   |-- conftest.py
|   |-- test_backend.py
|   |-- test_mcp_http.py
|   `-- test_tool_registry.py
|-- .env.example
|-- .vscode/launch.json
|-- Dockerfile
|-- docker-compose.yml
|-- main.py
|-- openapi.yaml
|-- pytest.ini
|-- requirements.txt
`-- tools.json
```

## Tools

The MCP exposes these four tools.

### get_client_onboarding_status

Input:

```json
{
  "client_id": "123"
}
```

Output:

```json
{
  "client_id": "123",
  "status": "Completed",
  "message": "Client onboarding completed successfully"
}
```

### get_client_basic_info

Input:

```json
{
  "client_id": "123",
  "field": "name"
}
```

Allowed `field` values:

- `name`
- `family`

Output:

```json
{
  "client_id": "123",
  "field": "name",
  "value": "John"
}
```

```json
{
  "client_id": "123",
  "field": "family",
  "value": "Doe"
}
```

### get_client_facility_limit

Input:

```json
{
  "client_id": "123"
}
```

Output:

```json
{
  "client_id": "123",
  "client_name": "John Doe",
  "facility_limit_eur": 75000000,
  "currency": "EUR",
  "formatted_limit": "EUR 75,000,000"
}
```

### summarize_client_outreach

Input:

```json
{
  "client_id": "123"
}
```

Output includes the outreach reasons, highlights, and total questions to answer:

```json
{
  "client_id": "123",
  "client_name": "John Doe",
  "outreach_count": 2,
  "questions_to_answer_count": 5,
  "reasons": ["Annual facility review", "Updated cash-flow forecast"],
  "summary": "John Doe has 2 outreach items. Reasons: Annual facility review, Updated cash-flow forecast. You should answer 5 questions in total."
}
```

## Local Setup

Use Python 3.12.

```bash
python -m venv .venv312
.venv312\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```

Terminal 1:

```bash
uvicorn mock_backend.app:app --host 0.0.0.0 --port 8001 --reload
```

Terminal 2:

```bash
uvicorn mcp_server.app:app --host 0.0.0.0 --port 8000 --reload
```

Health checks:

```bash
curl http://localhost:8001/health
curl http://localhost:8000/health
```

## REST API

OpenAPI 3.1 schema:

- Static YAML: `openapi.yaml`
- Runtime JSON: `http://localhost:8000/openapi.json`
- Runtime YAML file endpoint: `http://localhost:8000/openapi.yaml`

Endpoints:

```bash
curl http://localhost:8000/api/v1/clients/123/onboarding-status
curl http://localhost:8000/api/v1/clients/123/basic-info/name
curl http://localhost:8000/api/v1/clients/123/basic-info/family
curl http://localhost:8000/api/v1/clients/123/facility
curl http://localhost:8000/api/v1/clients/123/outreach-summary
```

## MCP JSON-RPC

List tools:

```bash
curl -X POST http://localhost:8000/mcp ^
  -H "Content-Type: application/json" ^
  -d "{\"jsonrpc\":\"2.0\",\"id\":1,\"method\":\"tools/list\"}"
```

Call tool:

```bash
curl -X POST http://localhost:8000/mcp ^
  -H "Content-Type: application/json" ^
  -d "{\"jsonrpc\":\"2.0\",\"id\":2,\"method\":\"tools/call\",\"params\":{\"name\":\"get_client_onboarding_status\",\"arguments\":{\"client_id\":\"123\"}}}"
```

The MCP Python SDK registration is in `mcp_server/mcp_app.py`. For stdio-style MCP testing:

```bash
python -m mcp_server.mcp_app
```

## Mock Backend

The mock backend is a separate FastAPI service and returns hardcoded data only.

```bash
curl http://localhost:8001/status/123
curl http://localhost:8001/info/123/name
curl http://localhost:8001/info/123/family
curl http://localhost:8001/facility/123
curl http://localhost:8001/outreach/123/summary
```

## Authentication Placeholder

Authentication is intentionally disabled for local development.

Enable API key validation:

```env
MCP_AUTH_REQUIRED=true
MCP_API_KEY_HEADER=x-api-key
MCP_API_KEY=local-dev-key
```

Then call:

```bash
curl http://localhost:8000/api/v1/clients/123/onboarding-status -H "x-api-key: local-dev-key"
```

Production replacement points:

- Replace `APIKeyAuthMiddleware` with Microsoft Entra ID JWT validation.
- Register an app in Microsoft Entra ID.
- Configure Teams bot and Copilot plugin auth references with the production app registration.
- Store secrets in Azure Key Vault or a managed secret store.

## Docker

```bash
docker compose up --build
```

Services:

- MCP server: `http://localhost:8000`
- Mock backend: `http://localhost:8001`

## Copilot Package

Package files are in `appPackage/`.

- `manifest.json`: Microsoft 365/Teams app manifest
- `declarativeAgent.json`: declarative agent manifest
- `plugin.json`: Microsoft 365 Copilot plugin manifest using `RemoteMCPServer`
- `plugin.openapi.json`: OpenAPI fallback plugin manifest
- `mcp-tools.json`: MCP tool discovery metadata mirror of the inline plugin metadata
- `openapi.yaml`: OpenAPI schema for the REST facade
- `color.png` and `outline.png`: Teams package icons

Before packaging:

1. Replace the hosted domain in `appPackage/plugin.json`, `appPackage/openapi.yaml`, and `appPackage/manifest.json` if you move away from the current Railway URL.
2. Replace the GUIDs in `appPackage/manifest.json` with real Microsoft Entra app and bot registration IDs.
3. Zip the contents of `appPackage/`, not the folder itself.
4. Upload the zip in Teams Developer Portal or Microsoft 365 Agents Toolkit.

Example Copilot prompts:

- Get onboarding status for client 123
- What is the client's name?
- What is the client's family name?
- For client 123, get the family field
- What is the current limit on my company's facility for client 123?
- Summarize the outreach highlights for client 123

## Teams Local Testing

1. Start both local services.
2. Start an HTTPS tunnel:

```bash
ngrok http 8000
```

3. Copy the HTTPS ngrok domain, for example `https://abc123.ngrok-free.app`.
4. Replace the hosted domain in `appPackage/manifest.json`, `appPackage/plugin.json`, and `appPackage/openapi.yaml`.
5. In Microsoft Entra ID, create or reuse an app registration for the Teams bot placeholder.
6. In Azure Bot Service or Bot Framework registration, set the messaging endpoint to your bot endpoint if you add a real Teams bot implementation.
7. In Teams Developer Portal, import the app package zip.
8. Validate the manifest and test in a personal scope first.

This project includes bot manifest placeholders but does not implement a Bot Framework message handler. Copilot calls the MCP server/plugin action; the bot block is present for Teams app packaging and future Teams conversational extensions.

## Error Handling Examples

Invalid basic info field through REST:

```bash
curl http://localhost:8000/api/v1/clients/123/basic-info/age
```

Response shape:

```json
{
  "error": {
    "code": "validation_error",
    "message": "Request validation failed.",
    "details": []
  }
}
```

Invalid MCP tool call:

```json
{
  "jsonrpc": "2.0",
  "id": 3,
  "method": "tools/call",
  "params": {
    "name": "get_client_basic_info",
    "arguments": {
      "client_id": "123",
      "field": "age"
    }
  }
}
```

Response shape:

```json
{
  "jsonrpc": "2.0",
  "id": 3,
  "error": {
    "code": -32602,
    "message": "Tool arguments failed validation.",
    "data": {
      "code": "invalid_arguments",
      "details": []
    }
  }
}
```

## Logging

Both services log requests with method, path, status code, and elapsed time.

Log levels:

```env
MCP_LOG_LEVEL=INFO
BACKEND_LOG_LEVEL=INFO
```

## Tests

```bash
pytest -q
```

Tests cover:

- Mock backend responses
- REST facade responses
- MCP `tools/list`
- MCP `tools/call`
- Tool validation

## API Versioning Strategy

REST endpoints are versioned under `/api/v1`.

Recommended evolution:

- Keep `/api/v1` stable for existing Copilot plugins.
- Add `/api/v2` for breaking response or parameter changes.
- Keep MCP tool names stable where possible.
- Add new tool names for breaking tool contract changes.
- Keep `operationId` values aligned with Copilot plugin function names.

## References

- Microsoft 365 Copilot plugins support REST APIs and MCP servers through declarative agent actions.
- Current Microsoft plugin manifest schema version used here: `v2.4`.
- Current Microsoft 365 app manifest schema used here: `v1.27`.
