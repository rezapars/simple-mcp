from mcp.server.fastmcp import FastMCP

from mcp_server.backend_client import BackendClient
from mcp_server.config import get_settings
from mcp_server.models import (
    AuthenticationArguments,
    BasicInfoArguments,
    ClientFacilityArguments,
    OnboardingStatusArguments,
    OutreachSummaryArguments,
)
from mcp_server.session import AUTH_REQUIRED_RESPONSE, DEFAULT_SESSION_ID, SessionStore

mcp = FastMCP("client-onboarding-mcp")
stdio_session_store = SessionStore()


def _stdio_client_id() -> str | None:
    return stdio_session_store.get_client_id(DEFAULT_SESSION_ID)


@mcp.tool()
async def authenticate_client(client_id: str, otp: str) -> dict:
    """Authenticate a client session using client ID and OTP."""
    args = AuthenticationArguments.model_validate({"client_id": client_id, "otp": otp})
    return stdio_session_store.authenticate(DEFAULT_SESSION_ID, args.client_id, args.otp)


@mcp.tool()
async def get_client_onboarding_status() -> dict:
    """Get the onboarding status for the authenticated client."""
    settings = get_settings()
    OnboardingStatusArguments.model_validate({})
    client_id = _stdio_client_id()
    if client_id is None:
        return AUTH_REQUIRED_RESPONSE
    async with BackendClient(settings.backend_base_url, settings.request_timeout_seconds) as client:
        result = await client.get_status(client_id)
        return result.model_dump(mode="json")


@mcp.tool()
async def get_client_basic_info(field: str) -> dict:
    """Get the authenticated client's basic name or family value."""
    settings = get_settings()
    args = BasicInfoArguments.model_validate({"field": field})
    client_id = _stdio_client_id()
    if client_id is None:
        return AUTH_REQUIRED_RESPONSE
    async with BackendClient(settings.backend_base_url, settings.request_timeout_seconds) as client:
        result = await client.get_basic_info(client_id, args.field)
        return result.model_dump(mode="json")


@mcp.tool()
async def get_client_facility_limit() -> dict:
    """Get the current facility limit in EUR and client name for the authenticated client."""
    settings = get_settings()
    ClientFacilityArguments.model_validate({})
    client_id = _stdio_client_id()
    if client_id is None:
        return AUTH_REQUIRED_RESPONSE
    async with BackendClient(settings.backend_base_url, settings.request_timeout_seconds) as client:
        result = await client.get_client_facility(client_id)
        return result.model_dump(mode="json")


@mcp.tool()
async def summarize_client_outreach() -> dict:
    """Summarize client outreach reasons, highlights, and questions to answer."""
    settings = get_settings()
    OutreachSummaryArguments.model_validate({})
    client_id = _stdio_client_id()
    if client_id is None:
        return AUTH_REQUIRED_RESPONSE
    async with BackendClient(settings.backend_base_url, settings.request_timeout_seconds) as client:
        result = await client.summarize_client_outreach(client_id)
        return result.model_dump(mode="json")


if __name__ == "__main__":
    mcp.run(transport="stdio")
