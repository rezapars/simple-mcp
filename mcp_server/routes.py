from fastapi import APIRouter, Depends, Path, Request
from fastapi.responses import JSONResponse

from mcp_server.backend_client import BackendClient
from mcp_server.errors import ToolExecutionError
from mcp_server.models import (
    AuthenticationArguments,
    AuthenticationResponse,
    BasicInfoField,
    BasicInfoResponse,
    ClientFacilityResponse,
    OnboardingStatusResponse,
    OutreachSummaryResponse,
    ToolListResponse,
)
from mcp_server.session import AUTH_REQUIRED_RESPONSE, SessionStore, resolve_session_id
from mcp_server.tool_registry import list_tools

router = APIRouter(prefix="/api/v1")


def get_backend_client(request: Request) -> BackendClient:
    return request.app.state.backend_client


def get_session_store(request: Request) -> SessionStore:
    return request.app.state.session_store


def get_session_id(request: Request) -> str:
    return resolve_session_id(dict(request.headers))


def get_authenticated_client_id(request: Request) -> str | None:
    return request.app.state.session_store.get_client_id(get_session_id(request))


@router.get(
    "/tools",
    response_model=ToolListResponse,
    tags=["metadata"],
    operation_id="list_client_tools",
)
async def get_tool_metadata() -> dict:
    return {"tools": list_tools()}


@router.post(
    "/authenticate",
    response_model=AuthenticationResponse,
    response_model_exclude_none=True,
    tags=["authentication"],
    operation_id="authenticate_client",
    summary="Authenticate client session",
)
async def authenticate_client(
    credentials: AuthenticationArguments,
    session_id: str = Depends(get_session_id),
    session_store: SessionStore = Depends(get_session_store),
) -> dict:
    return session_store.authenticate(session_id, credentials.client_id, credentials.otp)


@router.get(
    "/client/onboarding-status",
    response_model=None,
    tags=["client-tools"],
    operation_id="get_authenticated_client_onboarding_status",
    summary="Get authenticated client onboarding status",
)
async def get_authenticated_client_onboarding_status(
    client_id: str | None = Depends(get_authenticated_client_id),
    backend_client: BackendClient = Depends(get_backend_client),
) -> OnboardingStatusResponse | JSONResponse:
    if client_id is None:
        return JSONResponse(status_code=401, content=AUTH_REQUIRED_RESPONSE)
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
    "/client/basic-info/{field}",
    response_model=None,
    tags=["client-tools"],
    operation_id="get_authenticated_client_basic_info",
    summary="Get authenticated client basic info",
)
async def get_authenticated_client_basic_info(
    field: BasicInfoField = Path(..., description="Allowed values are name or family."),
    client_id: str | None = Depends(get_authenticated_client_id),
    backend_client: BackendClient = Depends(get_backend_client),
) -> BasicInfoResponse | JSONResponse:
    if client_id is None:
        return JSONResponse(status_code=401, content=AUTH_REQUIRED_RESPONSE)
    try:
        return await backend_client.get_basic_info(client_id, field)
    except Exception as exc:
        raise ToolExecutionError(
            code=getattr(exc, "code", "backend_error"),
            message=getattr(exc, "message", "Failed to get client basic info."),
            status_code=getattr(exc, "status_code", 502),
            details=getattr(exc, "details", None),
        ) from exc


@router.get(
    "/client/facility",
    response_model=None,
    tags=["client-tools"],
    operation_id="get_authenticated_client_facility_limit",
    summary="Get authenticated client facility limit",
)
async def get_authenticated_client_facility_limit(
    client_id: str | None = Depends(get_authenticated_client_id),
    backend_client: BackendClient = Depends(get_backend_client),
) -> ClientFacilityResponse | JSONResponse:
    if client_id is None:
        return JSONResponse(status_code=401, content=AUTH_REQUIRED_RESPONSE)
    try:
        return await backend_client.get_client_facility(client_id)
    except Exception as exc:
        raise ToolExecutionError(
            code=getattr(exc, "code", "backend_error"),
            message=getattr(exc, "message", "Failed to get client facility limit."),
            status_code=getattr(exc, "status_code", 502),
            details=getattr(exc, "details", None),
        ) from exc


@router.get(
    "/client/outreach-summary",
    response_model=None,
    tags=["client-tools"],
    operation_id="get_authenticated_client_outreach_summary",
    summary="Summarize authenticated client outreach",
)
async def get_authenticated_client_outreach_summary(
    client_id: str | None = Depends(get_authenticated_client_id),
    backend_client: BackendClient = Depends(get_backend_client),
) -> OutreachSummaryResponse | JSONResponse:
    if client_id is None:
        return JSONResponse(status_code=401, content=AUTH_REQUIRED_RESPONSE)
    try:
        return await backend_client.summarize_client_outreach(client_id)
    except Exception as exc:
        raise ToolExecutionError(
            code=getattr(exc, "code", "backend_error"),
            message=getattr(exc, "message", "Failed to summarize client outreach."),
            status_code=getattr(exc, "status_code", 502),
            details=getattr(exc, "details", None),
        ) from exc


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


@router.get(
    "/clients/{client_id}/facility",
    response_model=ClientFacilityResponse,
    tags=["client-tools"],
    operation_id="get_client_facility_limit",
    summary="Get client facility limit",
)
async def get_client_facility_limit(
    client_id: str = Path(..., min_length=1, description="Client identifier."),
    backend_client: BackendClient = Depends(get_backend_client),
) -> ClientFacilityResponse:
    try:
        return await backend_client.get_client_facility(client_id)
    except Exception as exc:
        raise ToolExecutionError(
            code=getattr(exc, "code", "backend_error"),
            message=getattr(exc, "message", "Failed to get client facility limit."),
            status_code=getattr(exc, "status_code", 502),
            details=getattr(exc, "details", None),
        ) from exc


@router.get(
    "/clients/{client_id}/outreach-summary",
    response_model=OutreachSummaryResponse,
    tags=["client-tools"],
    operation_id="summarize_client_outreach",
    summary="Summarize client outreach",
)
async def summarize_client_outreach(
    client_id: str = Path(..., min_length=1, description="Client identifier."),
    backend_client: BackendClient = Depends(get_backend_client),
) -> OutreachSummaryResponse:
    try:
        return await backend_client.summarize_client_outreach(client_id)
    except Exception as exc:
        raise ToolExecutionError(
            code=getattr(exc, "code", "backend_error"),
            message=getattr(exc, "message", "Failed to summarize client outreach."),
            status_code=getattr(exc, "status_code", 502),
            details=getattr(exc, "details", None),
        ) from exc
