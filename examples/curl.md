# Curl Examples

Start both services first.

```bash
curl http://localhost:8000/health
curl http://localhost:8000/api/v1/tools
curl http://localhost:8000/api/v1/clients/123/onboarding-status
curl http://localhost:8000/api/v1/clients/123/basic-info/name
curl http://localhost:8000/api/v1/clients/123/basic-info/family
```

MCP JSON-RPC:

```bash
curl -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/list"}'
```

```bash
curl -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"get_client_onboarding_status","arguments":{"client_id":"123"}}}'
```

With auth enabled:

```bash
curl http://localhost:8000/api/v1/clients/123/onboarding-status \
  -H "x-api-key: local-dev-key"
```
