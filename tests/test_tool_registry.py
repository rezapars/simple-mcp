import pytest

from mcp_server.errors import ToolExecutionError
from mcp_server.models import (
    BasicInfoField,
    BasicInfoResponse,
    ClientFacilityResponse,
    OnboardingStatusResponse,
    OutreachItem,
    OutreachSummaryResponse,
)
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

    async def get_client_facility(self, client_id: str) -> ClientFacilityResponse:
        return ClientFacilityResponse(
            client_id=client_id,
            client_name="John Doe",
            facility_limit_eur=75_000_000,
            formatted_limit="EUR 75,000,000",
        )

    async def summarize_client_outreach(self, client_id: str) -> OutreachSummaryResponse:
        outreaches = [
            OutreachItem(
                outreach_id="out-123-001",
                date="2026-04-22",
                channel="Email",
                reason="Annual facility review",
                questions_to_answer=["Question one?", "Question two?"],
            )
        ]
        return OutreachSummaryResponse(
            client_id=client_id,
            client_name="John Doe",
            outreach_count=1,
            questions_to_answer_count=2,
            reasons=["Annual facility review"],
            highlights=["2026-04-22 via Email: Annual facility review; 2 questions to answer."],
            summary="John Doe has 1 outreach item. Reason: Annual facility review. You should answer 2 questions in total.",
            outreaches=outreaches,
        )


def test_list_tools_exposes_expected_tools():
    tools = list_tools()

    assert [tool["name"] for tool in tools] == [
        "get_client_onboarding_status",
        "get_client_basic_info",
        "get_client_facility_limit",
        "summarize_client_outreach",
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


async def test_call_facility_tool_returns_limit_and_name():
    result = await call_tool(
        "get_client_facility_limit",
        {"client_id": "123"},
        FakeBackendClient(),
    )

    assert result == {
        "client_id": "123",
        "client_name": "John Doe",
        "facility_limit_eur": 75_000_000,
        "currency": "EUR",
        "formatted_limit": "EUR 75,000,000",
    }


async def test_call_outreach_tool_returns_summary():
    result = await call_tool(
        "summarize_client_outreach",
        {"client_id": "123"},
        FakeBackendClient(),
    )

    assert result["client_name"] == "John Doe"
    assert result["questions_to_answer_count"] == 2
    assert "Annual facility review" in result["summary"]
