from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from mcp_server.config import Settings


PUBLIC_PATH_PREFIXES = (
    "/health",
    "/docs",
    "/redoc",
    "/openapi.json",
    "/openapi.yaml",
    "/tools.json",
    "/copilot",
)


class APIKeyAuthMiddleware(BaseHTTPMiddleware):
    """Authentication placeholder for production API key or Entra token validation."""

    def __init__(self, app, settings: Settings) -> None:
        super().__init__(app)
        self.settings = settings

    async def dispatch(self, request: Request, call_next) -> Response:
        if not self.settings.auth_required:
            return await call_next(request)

        if request.url.path.startswith(PUBLIC_PATH_PREFIXES):
            return await call_next(request)

        supplied_key = request.headers.get(self.settings.api_key_header)
        if supplied_key != self.settings.api_key:
            return JSONResponse(
                status_code=401,
                content={
                    "error": {
                        "code": "unauthorized",
                        "message": f"Missing or invalid {self.settings.api_key_header} header.",
                    }
                },
            )

        return await call_next(request)
