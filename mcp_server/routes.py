from fastapi import APIRouter, Depends, Path, Request

from mcp_server.backend_client import BackendClient
from mcp_server.errors import ToolExecutionError
from mcp_server.models import (
    BasicInfoField,
    BasicInfoResponse,
    OnboardingStatusResponse,
    ToolListResponse,
)
from mcp_server.tool_registry import list_tools

router = APIRouter(prefix="/api/v1")


def get_backend_client(request: Request) -> BackendClient:
    return request.app.state.backend_client


@router.get(
    "/tools",
    response_model=ToolListResponse,
    tags=["metadata"],
    operation_id="list_client_tools",
)
async def get_tool_metadata() -> dict:
    return {"tools": list_tools()}


@router.get(
    "/clients/{client_id}/onboarding-status",
    response_model=OnboardingStatusResponse,
    tags=["client-tools"],
    operation_id="get_client_onboarding_status",
    summary="Get client onboarding status",
)
async def get_client_onboarding_status(
    client_id: str = Path(..., min_length=1, description="Client identifier."),
    backend_client: BackendClient = Depends(get_backend_client),
) -> OnboardingStatusResponse:
    try:
        return await backend_client.get_status(client_id)
    except Exception as exc:
        raise ToolExecutionError(
            code=getattr(exc, "code", "backend_error"),
            message=getattr(exc, "message", "Failed to get client onboarding status."),
            status_code=getattr(exc, "status_code", 502),
            details=getattr(exc, "details", None),
        ) from exc


@router.get(
    "/clients/{client_id}/basic-info/{field}",
    response_model=BasicInfoResponse,
    tags=["client-tools"],
    operation_id="get_client_basic_info",
    summary="Get client basic info",
)
async def get_client_basic_info(
    client_id: str = Path(..., min_length=1, description="Client identifier."),
    field: BasicInfoField = Path(..., description="Allowed values are name or family."),
    backend_client: BackendClient = Depends(get_backend_client),
) -> BasicInfoResponse:
    try:
        return await backend_client.get_basic_info(client_id, field)
    except Exception as exc:
        raise ToolExecutionError(
            code=getattr(exc, "code", "backend_error"),
            message=getattr(exc, "message", "Failed to get client basic info."),
            status_code=getattr(exc, "status_code", 502),
            details=getattr(exc, "details", None),
        ) from exc
