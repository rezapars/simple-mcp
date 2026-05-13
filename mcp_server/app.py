import json
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import FileResponse, JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from mcp_server.auth import APIKeyAuthMiddleware
from mcp_server.backend_client import BackendClient
from mcp_server.config import Settings, get_settings
from mcp_server.errors import ToolExecutionError
from mcp_server.jsonrpc import _error_response, handle_json_rpc_payload
from mcp_server.logging_config import RequestLoggingMiddleware, configure_logging
from mcp_server.routes import router
from mcp_server.session import SessionStore, resolve_session_id
from mcp_server.tool_registry import list_tools

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or get_settings()
    configure_logging(settings.log_level)

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        app.state.settings = settings
        app.state.backend_client = BackendClient(
            settings.backend_base_url,
            settings.request_timeout_seconds,
        )
        app.state.session_store = getattr(app.state, "session_store", SessionStore())
        yield
        await app.state.backend_client.close()

    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        openapi_version="3.1.0",
        description="Minimal MCP service for Microsoft Copilot and Microsoft Teams integration.",
        lifespan=lifespan,
    )
    app.add_middleware(RequestLoggingMiddleware)
    app.add_middleware(APIKeyAuthMiddleware, settings=settings)
    app.state.session_store = SessionStore()
    app.include_router(router)

    @app.exception_handler(ToolExecutionError)
    async def tool_error_handler(_: Request, exc: ToolExecutionError) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": {
                    "code": exc.code,
                    "message": exc.message,
                    "details": exc.details,
                }
            },
        )

    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(_: Request, exc: RequestValidationError) -> JSONResponse:
        return JSONResponse(
            status_code=422,
            content={
                "error": {
                    "code": "validation_error",
                    "message": "Request validation failed.",
                    "details": exc.errors(),
                }
            },
        )

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(_: Request, exc: StarletteHTTPException) -> JSONResponse:
        detail = exc.detail if isinstance(exc.detail, dict) else {"message": exc.detail}
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": {"code": "http_error", "message": detail.get("message", str(exc.detail))}},
        )

    @app.get("/health", tags=["health"])
    async def health(request: Request) -> dict:
        backend_status = "unknown"
        try:
            await request.app.state.backend_client.health()
            backend_status = "ok"
        except Exception:
            backend_status = "unavailable"
        return {
            "status": "ok",
            "service": "mcp-server",
            "version": settings.app_version,
            "api_version": settings.api_version,
            "backend": backend_status,
        }

    @app.get("/mcp/tools", tags=["mcp"], operation_id="mcp_list_tools")
    async def mcp_tools() -> dict:
        return {"tools": list_tools()}

    @app.post("/mcp", tags=["mcp"], operation_id="mcp_json_rpc")
    async def mcp_json_rpc(request: Request) -> JSONResponse:
        try:
            payload = await request.json()
        except json.JSONDecodeError:
            return JSONResponse(status_code=400, content=_error_response(None, -32700, "Parse error"))
        session_id = resolve_session_id(dict(request.headers))
        result = await handle_json_rpc_payload(
            payload,
            request.app.state.backend_client,
            request.app.state.session_store,
            session_id,
        )
        return JSONResponse(content=result)

    @app.get("/openapi.yaml", include_in_schema=False)
    async def openapi_yaml() -> FileResponse:
        return FileResponse(PROJECT_ROOT / "openapi.yaml", media_type="application/yaml")

    @app.get("/tools.json", include_in_schema=False)
    async def tools_json() -> FileResponse:
        return FileResponse(PROJECT_ROOT / "tools.json", media_type="application/json")

    @app.get("/copilot/plugin.json", include_in_schema=False)
    async def copilot_plugin_manifest() -> FileResponse:
        return FileResponse(PROJECT_ROOT / "appPackage" / "plugin.json", media_type="application/json")

    @app.get("/copilot/declarativeAgent.json", include_in_schema=False)
    async def copilot_declarative_agent() -> FileResponse:
        return FileResponse(PROJECT_ROOT / "appPackage" / "declarativeAgent.json", media_type="application/json")

    return app


app = create_app()
