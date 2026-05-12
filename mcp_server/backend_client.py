import logging
from typing import TypeVar

import httpx
from pydantic import BaseModel

from mcp_server.errors import BackendClientError
from mcp_server.models import BasicInfoField, BasicInfoResponse, OnboardingStatusResponse

ModelT = TypeVar("ModelT", bound=BaseModel)

logger = logging.getLogger(__name__)


class BackendClient:
    def __init__(self, base_url: str, timeout_seconds: float = 10.0) -> None:
        self.base_url = base_url.rstrip("/")
        self._client = httpx.AsyncClient(base_url=self.base_url, timeout=timeout_seconds)

    async def close(self) -> None:
        await self._client.aclose()

    async def __aenter__(self) -> "BackendClient":
        return self

    async def __aexit__(self, exc_type, exc, traceback) -> None:
        await self.close()

    async def get_status(self, client_id: str) -> OnboardingStatusResponse:
        response = await self._get(f"/status/{client_id}")
        return self._parse_response(response, OnboardingStatusResponse)

    async def get_basic_info(self, client_id: str, field: BasicInfoField) -> BasicInfoResponse:
        response = await self._get(f"/info/{client_id}/{field.value}")
        return self._parse_response(response, BasicInfoResponse)

    async def health(self) -> dict[str, str]:
        response = await self._get("/health")
        return response.json()

    async def _get(self, path: str) -> httpx.Response:
        try:
            response = await self._client.get(path)
        except httpx.HTTPError as exc:
            logger.warning("backend_request_failed path=%s error=%s", path, exc)
            raise BackendClientError(
                code="backend_unavailable",
                message="Mock backend server is not reachable.",
                status_code=503,
                details=str(exc),
            ) from exc

        if response.status_code >= 400:
            raise BackendClientError(
                code="backend_error",
                message="Mock backend returned an error.",
                status_code=response.status_code,
                details=_safe_response_body(response),
            )
        return response

    @staticmethod
    def _parse_response(response: httpx.Response, model: type[ModelT]) -> ModelT:
        try:
            return model.model_validate(response.json())
        except ValueError as exc:
            raise BackendClientError(
                code="invalid_backend_response",
                message="Mock backend returned invalid JSON.",
                status_code=502,
                details=response.text,
            ) from exc


def _safe_response_body(response: httpx.Response) -> dict | str:
    try:
        return response.json()
    except ValueError:
        return response.text
