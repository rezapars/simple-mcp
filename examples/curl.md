# Curl Examples

Start both services first.

```bash
curl http://localhost:8000/health
curl http://localhost:8000/api/v1/tools
curl -X POST http://localhost:8000/api/v1/authenticate \
  -H "Content-Type: application/json" \
  -H "x-mcp-session-id: demo-session" \
  -d '{"client_id":"123","otp":"9632"}'
curl http://localhost:8000/api/v1/client/onboarding-status -H "x-mcp-session-id: demo-session"
curl http://localhost:8000/api/v1/client/basic-info/name -H "x-mcp-session-id: demo-session"
curl http://localhost:8000/api/v1/client/facility -H "x-mcp-session-id: demo-session"
curl http://localhost:8000/api/v1/client/outreach-summary -H "x-mcp-session-id: demo-session"
curl http://localhost:8000/api/v1/clients/123/onboarding-status
curl http://localhost:8000/api/v1/clients/123/basic-info/name
curl http://localhost:8000/api/v1/clients/123/basic-info/family
curl http://localhost:8000/api/v1/clients/123/facility
curl http://localhost:8000/api/v1/clients/123/outreach-summary
```

MCP JSON-RPC:

```bash
curl -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -H "x-mcp-session-id: demo-session" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/list"}'
```

```bash
curl -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -H "x-mcp-session-id: demo-session" \
  -d '{"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"authenticate_client","arguments":{"client_id":"123","otp":"9632"}}}'
```

```bash
curl -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -H "x-mcp-session-id: demo-session" \
  -d '{"jsonrpc":"2.0","id":3,"method":"tools/call","params":{"name":"get_client_onboarding_status","arguments":{}}}'
```

```bash
curl -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -H "x-mcp-session-id: demo-session" \
  -d '{"jsonrpc":"2.0","id":4,"method":"tools/call","params":{"name":"get_client_facility_limit","arguments":{}}}'
```

```bash
curl -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -H "x-mcp-session-id: demo-session" \
  -d '{"jsonrpc":"2.0","id":5,"method":"tools/call","params":{"name":"summarize_client_outreach","arguments":{}}}'
```

With auth enabled:

```bash
curl http://localhost:8000/api/v1/clients/123/onboarding-status \
  -H "x-api-key: local-dev-key"
```
