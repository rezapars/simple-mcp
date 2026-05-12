from mcp.server.fastmcp import FastMCP

from mcp_server.backend_client import BackendClient
from mcp_server.config import get_settings
from mcp_server.models import (
    BasicInfoArguments,
    ClientFacilityArguments,
    OnboardingStatusArguments,
    OutreachSummaryArguments,
)

mcp = FastMCP("client-onboarding-mcp")


@mcp.tool()
async def get_client_onboarding_status(client_id: str) -> dict[str, str]:
    """Get the onboarding status for a client by client ID."""
    settings = get_settings()
    args = OnboardingStatusArguments.model_validate({"client_id": client_id})
    async with BackendClient(settings.backend_base_url, settings.request_timeout_seconds) as client:
        result = await client.get_status(args.client_id)
        return result.model_dump(mode="json")


@mcp.tool()
async def get_client_basic_info(client_id: str, field: str) -> dict[str, str]:
    """Get a client's basic name or family value by client ID."""
    settings = get_settings()
    args = BasicInfoArguments.model_validate({"client_id": client_id, "field": field})
    async with BackendClient(settings.backend_base_url, settings.request_timeout_seconds) as client:
        result = await client.get_basic_info(args.client_id, args.field)
        return result.model_dump(mode="json")


@mcp.tool()
async def get_client_facility_limit(client_id: str) -> dict:
    """Get the current facility limit in EUR and client name for a client ID."""
    settings = get_settings()
    args = ClientFacilityArguments.model_validate({"client_id": client_id})
    async with BackendClient(settings.backend_base_url, settings.request_timeout_seconds) as client:
        result = await client.get_client_facility(args.client_id)
        return result.model_dump(mode="json")


@mcp.tool()
async def summarize_client_outreach(client_id: str) -> dict:
    """Summarize client outreach reasons, highlights, and questions to answer."""
    settings = get_settings()
    args = OutreachSummaryArguments.model_validate({"client_id": client_id})
    async with BackendClient(settings.backend_base_url, settings.request_timeout_seconds) as client:
        result = await client.summarize_client_outreach(args.client_id)
        return result.model_dump(mode="json")


if __name__ == "__main__":
    mcp.run(transport="stdio")
