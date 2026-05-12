import pytest

from mcp_server.errors import ToolExecutionError
from mcp_server.models import BasicInfoField, BasicInfoResponse, OnboardingStatusResponse
from mcp_server.tool_registry import call_tool, list_tools


class FakeBackendClient:
    async def get_status(self, client_id: str) -> OnboardingStatusResponse:
        return OnboardingStatusResponse(
            client_id=client_id,
            status="Completed",
            message="Client onboarding completed successfully",
        )

    async def get_basic_info(self, client_id: str, field: BasicInfoField) -> BasicInfoResponse:
        return BasicInfoResponse(client_id=client_id, field=field, value="John")


def test_list_tools_exposes_only_two_tools():
    tools = list_tools()

    assert [tool["name"] for tool in tools] == [
        "get_client_onboarding_status",
        "get_client_basic_info",
    ]


async def test_call_tool_validates_arguments():
    with pytest.raises(ToolExecutionError) as error:
        await call_tool("get_client_basic_info", {"client_id": "123", "field": "age"}, FakeBackendClient())

    assert error.value.code == "invalid_arguments"


async def test_call_tool_returns_structured_json():
    result = await call_tool(
        "get_client_onboarding_status",
        {"client_id": "123"},
        FakeBackendClient(),
    )

    assert result == {
        "client_id": "123",
        "status": "Completed",
        "message": "Client onboarding completed successfully",
    }
