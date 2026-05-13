import json
from typing import Any

from fastapi.encoders import jsonable_encoder

from mcp_server.backend_client import BackendClient
from mcp_server.errors import ToolExecutionError
from mcp_server.session import SessionStore
from mcp_server.tool_registry import call_tool, list_tools

JSONRPC_VERSION = "2.0"
MCP_PROTOCOL_VERSION = "2025-06-18"


async def handle_json_rpc_payload(
    payload: Any,
    backend_client: BackendClient,
    session_store: SessionStore,
    session_id: str,
) -> Any:
    if isinstance(payload, list):
        return [
            await _handle_single_request(item, backend_client, session_store, session_id)
            for item in payload
        ]
    return await _handle_single_request(payload, backend_client, session_store, session_id)


async def _handle_single_request(
    payload: Any,
    backend_client: BackendClient,
    session_store: SessionStore,
    session_id: str,
) -> dict[str, Any]:
    if not isinstance(payload, dict):
        return _error_response(None, -32600, "Invalid Request")

    request_id = payload.get("id")
    jsonrpc_mode = payload.get("jsonrpc") == JSONRPC_VERSION or "id" in payload
    method = payload.get("method")
    params = payload.get("params") or {}

    try:
        if method == "initialize":
            result = {
                "protocolVersion": MCP_PROTOCOL_VERSION,
                "capabilities": {"tools": {"listChanged": False}},
                "serverInfo": {"name": "client-onboarding-mcp", "version": "1.0.0"},
            }
        elif method == "tools/list":
            result = {"tools": list_tools()}
        elif method == "tools/call":
            result = await _handle_tool_call(params, backend_client, session_store, session_id)
        else:
            return _error_response(request_id, -32601, f"Method not found: {method}", jsonrpc_mode)
    except ToolExecutionError as exc:
        return _error_response(
            request_id,
            -32602 if exc.code in {"invalid_arguments", "tool_not_found"} else -32603,
            exc.message,
            jsonrpc_mode,
            {"code": exc.code, "details": jsonable_encoder(exc.details)},
        )
    except Exception as exc:
        return _error_response(
            request_id,
            -32603,
            "Internal error",
            jsonrpc_mode,
            {"code": "internal_error", "details": str(exc)},
        )

    if jsonrpc_mode:
        return {"jsonrpc": JSONRPC_VERSION, "id": request_id, "result": jsonable_encoder(result)}
    return jsonable_encoder(result)


async def _handle_tool_call(
    params: dict[str, Any],
    backend_client: BackendClient,
    session_store: SessionStore,
    session_id: str,
) -> dict[str, Any]:
    if not isinstance(params, dict):
        raise ToolExecutionError("invalid_arguments", "params must be an object.")

    name = params.get("name")
    arguments = params.get("arguments", {})
    if not isinstance(name, str) or not name:
        raise ToolExecutionError("invalid_arguments", "params.name is required.")
    if not isinstance(arguments, dict):
        raise ToolExecutionError("invalid_arguments", "params.arguments must be an object.")

    structured = await call_tool(name, arguments, backend_client, session_store, session_id)
    return {
        "content": [{"type": "text", "text": json.dumps(structured)}],
        "structuredContent": structured,
        "isError": False,
    }


def _error_response(
    request_id: Any,
    code: int,
    message: str,
    jsonrpc_mode: bool = True,
    data: Any | None = None,
) -> dict[str, Any]:
    error = {"code": code, "message": message}
    if data is not None:
        error["data"] = data
    if jsonrpc_mode:
        return {"jsonrpc": JSONRPC_VERSION, "id": request_id, "error": error}
    return {"error": error}
