from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from mock_backend.config import BackendSettings, get_backend_settings
from mock_backend.logging_config import RequestLoggingMiddleware, configure_logging
from mock_backend.routes import router


def create_app(settings: BackendSettings | None = None) -> FastAPI:
    settings = settings or get_backend_settings()
    configure_logging(settings.log_level)

    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        openapi_version="3.1.0",
        description="Hardcoded mock backend for the client onboarding MCP demo.",
    )
    app.add_middleware(RequestLoggingMiddleware)
    app.include_router(router)

    @app.get("/health", tags=["health"])
    async def health() -> dict[str, str]:
        return {"status": "ok", "service": "mock-backend", "version": settings.app_version}

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
        if isinstance(exc.detail, dict):
            message = exc.detail.get("message", "HTTP error")
            details = exc.detail
        else:
            message = str(exc.detail)
            details = None
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": {"code": "http_error", "message": message, "details": details}},
        )

    return app


app = create_app()
