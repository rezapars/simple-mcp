# MCP JSON-RPC Examples

Initialize:

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "initialize",
  "params": {
    "protocolVersion": "2025-06-18",
    "capabilities": {},
    "clientInfo": {
      "name": "local-test",
      "version": "1.0.0"
    }
  }
}
```

List tools:

```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "method": "tools/list"
}
```

Call `get_client_onboarding_status`:

```json
{
  "jsonrpc": "2.0",
  "id": 3,
  "method": "tools/call",
  "params": {
    "name": "get_client_onboarding_status",
    "arguments": {
      "client_id": "123"
    }
  }
}
```

Call `get_client_basic_info`:

```json
{
  "jsonrpc": "2.0",
  "id": 4,
  "method": "tools/call",
  "params": {
    "name": "get_client_basic_info",
    "arguments": {
      "client_id": "123",
      "field": "family"
    }
  }
}
```

Call `get_client_facility_limit`:

```json
{
  "jsonrpc": "2.0",
  "id": 5,
  "method": "tools/call",
  "params": {
    "name": "get_client_facility_limit",
    "arguments": {
      "client_id": "123"
    }
  }
}
```

Call `summarize_client_outreach`:

```json
{
  "jsonrpc": "2.0",
  "id": 6,
  "method": "tools/call",
  "params": {
    "name": "summarize_client_outreach",
    "arguments": {
      "client_id": "123"
    }
  }
}
```
